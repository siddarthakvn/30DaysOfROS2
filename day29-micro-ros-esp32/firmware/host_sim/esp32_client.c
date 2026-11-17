/*
 * esp32_client.c — Standalone C serial client (zero ROS / DDS dependencies).
 *
 * Speaks compact 0x7E + CRC-16 binary frames over a POSIX UART/PTY device.
 * Models the exact split used by micro-ROS over DDS-XRCE:
 *   1. Open session with the host agent over serial.
 *   2. Ask the agent to create node "esp32_base", sub "/cmd_vel", pub "/esp32/status".
 *   3. Convert Twist (vx, wz) into differential wheel speeds (wheel_base = 0.30 m).
 *   4. Cut wheels to 0.000 if no command arrives within 250 ms (watchdog).
 *
 * For the physical ESP32 rclc / micro_ros_arduino firmware, see:
 *   firmware/esp32_base/esp32_base.ino
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>

#define SYNC_BYTE        0x7E
#define CLIENT_KEY       0xE5320029u

#define OP_CREATE_CLIENT 0x01
#define OP_CREATE_NODE   0x02
#define OP_CREATE_SUB    0x03
#define OP_CREATE_PUB    0x04
#define OP_CMD_VEL       0x05
#define OP_STATUS_DATA   0x06
#define OP_STATUS_ACK    0x81

#define STATE_IDLE          0
#define STATE_DRIVING       1
#define STATE_WATCHDOG_STOP 2

#define WHEEL_BASE_M   0.30
#define WATCHDOG_MS    250L

static volatile sig_atomic_t g_stop = 0;

static void on_signal(int sig) {
    (void)sig;
    g_stop = 1;
}

static int64_t now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000LL + (int64_t)(ts.tv_nsec / 1000000L);
}

static void sleep_ms(long ms) {
    struct timespec ts;
    ts.tv_sec = ms / 1000;
    ts.tv_nsec = (ms % 1000) * 1000000L;
    nanosleep(&ts, NULL);
}

static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x8000u) {
                crc = (uint16_t)((crc << 1) ^ 0x1021u);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

static int open_serial(const char *path) {
    int fd = open(path, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) {
        return -1;
    }
    struct termios tio;
    if (tcgetattr(fd, &tio) == 0) {
        tio.c_iflag = 0;
        tio.c_oflag = 0;
        tio.c_lflag = 0;
        tio.c_cflag = CS8 | CREAD | CLOCAL;
        cfsetispeed(&tio, B115200);
        cfsetospeed(&tio, B115200);
        tcsetattr(fd, TCSANOW, &tio);
    }
    return fd;
}

typedef struct {
    uint32_t tx_frames;
    uint32_t rx_frames;
    uint32_t tx_bytes;
    uint32_t rx_bytes;
    uint32_t crc_err;
} WireStats;

static int send_frame(int fd, uint8_t opcode, const void *payload, uint16_t len, WireStats *st) {
    uint8_t frame[256];
    if (len > 128) {
        return -1;
    }
    frame[0] = SYNC_BYTE;
    frame[1] = opcode;
    frame[2] = (uint8_t)(len & 0xFFu);
    frame[3] = (uint8_t)((len >> 8) & 0xFFu);
    if (len > 0 && payload != NULL) {
        memcpy(&frame[4], payload, len);
    }
    uint16_t crc = crc16_ccitt(&frame[1], (size_t)(3u + len));
    frame[4 + len] = (uint8_t)(crc & 0xFFu);
    frame[5 + len] = (uint8_t)((crc >> 8) & 0xFFu);

    size_t total = (size_t)(6u + len);
    size_t off = 0;
    while (off < total) {
        ssize_t n = write(fd, frame + off, total - off);
        if (n > 0) {
            off += (size_t)n;
        } else if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            sleep_ms(2);
        } else {
            return -1;
        }
    }
    st->tx_frames += 1;
    st->tx_bytes += (uint32_t)total;
    return 0;
}

typedef struct {
    uint8_t buf[512];
    size_t len;
} RxBuf;

static int poll_frame(int fd, RxBuf *rx, uint8_t *opcode_out, uint8_t *payload_out, uint16_t *len_out, WireStats *st) {
    uint8_t tmp[128];
    ssize_t n = read(fd, tmp, sizeof(tmp));
    if (n > 0) {
        if (rx->len + (size_t)n > sizeof(rx->buf)) {
            rx->len = 0;
        }
        memcpy(rx->buf + rx->len, tmp, (size_t)n);
        rx->len += (size_t)n;
        st->rx_bytes += (uint32_t)n;
    }
    while (rx->len > 0) {
        size_t sync = 0;
        while (sync < rx->len && rx->buf[sync] != SYNC_BYTE) {
            sync++;
        }
        if (sync > 0) {
            memmove(rx->buf, rx->buf + sync, rx->len - sync);
            rx->len -= sync;
        }
        if (rx->len < 6) {
            return 0;
        }
        uint8_t op = rx->buf[1];
        uint16_t plen = (uint16_t)rx->buf[2] | ((uint16_t)rx->buf[3] << 8);
        if (plen > 128) {
            memmove(rx->buf, rx->buf + 1, rx->len - 1);
            rx->len -= 1;
            continue;
        }
        size_t total = (size_t)(6u + plen);
        if (rx->len < total) {
            return 0;
        }
        uint16_t want = (uint16_t)rx->buf[4 + plen] | ((uint16_t)rx->buf[5 + plen] << 8);
        uint16_t got = crc16_ccitt(&rx->buf[1], (size_t)(3u + plen));
        if (want != got) {
            st->crc_err += 1;
            memmove(rx->buf, rx->buf + total, rx->len - total);
            rx->len -= total;
            continue;
        }
        *opcode_out = op;
        *len_out = plen;
        if (plen > 0) {
            memcpy(payload_out, &rx->buf[4], plen);
        }
        memmove(rx->buf, rx->buf + total, rx->len - total);
        rx->len -= total;
        st->rx_frames += 1;
        return 1;
    }
    return 0;
}

static int send_status(int fd, uint32_t cmd_rx, uint8_t state, double vx, double wz, double left, double right, WireStats *st) {
    uint8_t payload[37];
    memcpy(&payload[0], &cmd_rx, 4);
    payload[4] = state;
    memcpy(&payload[5], &vx, 8);
    memcpy(&payload[13], &wz, 8);
    memcpy(&payload[21], &left, 8);
    memcpy(&payload[29], &right, 8);
    return send_frame(fd, OP_STATUS_DATA, payload, sizeof(payload), st);
}

static const char *state_name(int session, uint8_t state) {
    if (!session) {
        return "NO_AGENT";
    }
    if (state == STATE_DRIVING) {
        return "DRIVING";
    }
    if (state == STATE_WATCHDOG_STOP) {
        return "WATCHDOG_STOP";
    }
    return "IDLE";
}

static int wait_ack(int fd, RxBuf *rx, uint8_t expected_op, long timeout_ms, WireStats *st) {
    int64_t deadline = now_ms() + timeout_ms;
    uint8_t op = 0;
    uint8_t payload[128];
    uint16_t plen = 0;
    while (!g_stop && now_ms() < deadline) {
        while (poll_frame(fd, rx, &op, payload, &plen, st) > 0) {
            if (op == OP_STATUS_ACK && plen >= 2 && payload[0] == expected_op && payload[1] == 1) {
                return 1;
            }
        }
        sleep_ms(10);
    }
    return 0;
}

int main(int argc, char **argv) {
    const char *dev = NULL;
    const char *mode = "bridged";
    long duration_ms = 0;

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--dev") == 0 && i + 1 < argc) {
            dev = argv[++i];
        } else if (strcmp(argv[i], "--mode") == 0 && i + 1 < argc) {
            mode = argv[++i];
        } else if (strcmp(argv[i], "--duration-ms") == 0 && i + 1 < argc) {
            duration_ms = strtol(argv[++i], NULL, 10);
        }
    }
    if (dev == NULL) {
        fprintf(stderr, "usage: %s --dev <serial_path> [--mode no_agent|bridged|watchdog] [--duration-ms N]\n", argv[0]);
        return 2;
    }

    signal(SIGINT, on_signal);
    signal(SIGTERM, on_signal);

    int fd = open_serial(dev);
    if (fd < 0) {
        perror("open_serial");
        return 1;
    }

    WireStats st = {0, 0, 0, 0, 0};
    RxBuf rx;
    memset(&rx, 0, sizeof(rx));

    int session = 0;
    int entities = 0;
    uint32_t cmd_rx = 0;
    uint8_t state = STATE_IDLE;
    double vx = 0.0, wz = 0.0, left = 0.0, right = 0.0;
    double peak_left = 0.0, peak_right = 0.0;
    int watchdog_trips = 0;
    int reported = 0;

    int64_t t_start = now_ms();
    int64_t last_ping = 0;
    int64_t last_cmd = 0;

    while (!g_stop) {
        int64_t now = now_ms();
        if (duration_ms > 0 && (now - t_start) >= duration_ms) {
            break;
        }

        if (!session) {
            if (now - last_ping >= 250) {
                uint32_t key = CLIENT_KEY;
                send_frame(fd, OP_CREATE_CLIENT, &key, sizeof(key), &st);
                last_ping = now;
            }
            if (wait_ack(fd, &rx, OP_CREATE_CLIENT, 50, &st)) {
                session = 1;
                const char *node_name = "esp32_base";
                const char *sub_spec = "geometry_msgs/msg/Twist:/cmd_vel";
                const char *pub_spec = "std_msgs/msg/String:/esp32/status";
                send_frame(fd, OP_CREATE_NODE, node_name, (uint16_t)strlen(node_name), &st);
                if (wait_ack(fd, &rx, OP_CREATE_NODE, 500, &st)) {
                    entities += 1;
                }
                send_frame(fd, OP_CREATE_SUB, sub_spec, (uint16_t)strlen(sub_spec), &st);
                if (wait_ack(fd, &rx, OP_CREATE_SUB, 500, &st)) {
                    entities += 1;
                }
                send_frame(fd, OP_CREATE_PUB, pub_spec, (uint16_t)strlen(pub_spec), &st);
                if (wait_ack(fd, &rx, OP_CREATE_PUB, 500, &st)) {
                    entities += 1;
                }
                send_status(fd, cmd_rx, state, vx, wz, left, right, &st);
            }
            continue;
        }

        uint8_t op = 0;
        uint8_t payload[128];
        uint16_t plen = 0;
        while (poll_frame(fd, &rx, &op, payload, &plen, &st) > 0) {
            if (op == OP_CMD_VEL && plen == 20) {
                double in_vx = 0.0, in_wz = 0.0;
                memcpy(&in_vx, &payload[4], 8);
                memcpy(&in_wz, &payload[12], 8);
                vx = in_vx;
                wz = in_wz;
                left = vx - 0.5 * wz * WHEEL_BASE_M;
                right = vx + 0.5 * wz * WHEEL_BASE_M;
                if (left > peak_left) peak_left = left;
                if (right > peak_right) peak_right = right;
                cmd_rx += 1;
                state = STATE_DRIVING;
                last_cmd = now_ms();
                send_status(fd, cmd_rx, state, vx, wz, left, right, &st);
            }
        }

        now = now_ms();
        if (state == STATE_DRIVING && last_cmd > 0 && (now - last_cmd) >= WATCHDOG_MS) {
            vx = 0.0;
            wz = 0.0;
            left = 0.0;
            right = 0.0;
            state = STATE_WATCHDOG_STOP;
            watchdog_trips += 1;
            send_status(fd, cmd_rx, state, vx, wz, left, right, &st);
        }

        if (!reported) {
            if (strcmp(mode, "bridged") == 0 && cmd_rx >= 5 && state == STATE_DRIVING) {
                printf(
                    "SUMMARY node=esp32_client mode=%s session=%d entities=%d cmd_rx=%u state=%s "
                    "vx=%.3f wz=%.3f left=%.3f right=%.3f peak_left=%.3f peak_right=%.3f "
                    "watchdog_trips=%d tx_frames=%u rx_frames=%u crc_err=%u\n",
                    mode, session, entities, cmd_rx, state_name(session, state),
                    vx, wz, left, right, peak_left, peak_right,
                    watchdog_trips, st.tx_frames, st.rx_frames, st.crc_err
                );
                printf("READY node=esp32_client mode=%s\n", mode);
                fflush(stdout);
                reported = 1;
            } else if (strcmp(mode, "watchdog") == 0 && watchdog_trips >= 1 && state == STATE_WATCHDOG_STOP) {
                printf(
                    "SUMMARY node=esp32_client mode=%s session=%d entities=%d cmd_rx=%u state=%s "
                    "vx=%.3f wz=%.3f left=%.3f right=%.3f peak_left=%.3f peak_right=%.3f "
                    "watchdog_trips=%d tx_frames=%u rx_frames=%u crc_err=%u\n",
                    mode, session, entities, cmd_rx, state_name(session, state),
                    vx, wz, left, right, peak_left, peak_right,
                    watchdog_trips, st.tx_frames, st.rx_frames, st.crc_err
                );
                printf("READY node=esp32_client mode=%s\n", mode);
                fflush(stdout);
                reported = 1;
            }
        }

        sleep_ms(10);
    }

    if (!reported) {
        printf(
            "SUMMARY node=esp32_client mode=%s session=%d entities=%d cmd_rx=%u state=%s "
            "vx=%.3f wz=%.3f left=%.3f right=%.3f peak_left=%.3f peak_right=%.3f "
            "watchdog_trips=%d tx_frames=%u rx_frames=%u crc_err=%u\n",
            mode, session, entities, cmd_rx, state_name(session, state),
            vx, wz, left, right, peak_left, peak_right,
            watchdog_trips, st.tx_frames, st.rx_frames, st.crc_err
        );
        printf("READY node=esp32_client mode=%s\n", mode);
        fflush(stdout);
    }

    close(fd);
    return 0;
}
