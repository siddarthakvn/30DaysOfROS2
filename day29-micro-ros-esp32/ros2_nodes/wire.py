"""Compact 0x7E + CRC-16 serial framing shared with firmware/host_sim/esp32_client.c."""

from __future__ import annotations

import struct

SYNC = 0x7E
CLIENT_KEY = 0xE5320029

OP_CREATE_CLIENT = 0x01
OP_CREATE_NODE = 0x02
OP_CREATE_SUB = 0x03
OP_CREATE_PUB = 0x04
OP_CMD_VEL = 0x05
OP_STATUS_DATA = 0x06
OP_STATUS_ACK = 0x81

STATE_NAMES = {
    0: "IDLE",
    1: "DRIVING",
    2: "WATCHDOG_STOP",
}


def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def encode_frame(opcode: int, payload: bytes = b"") -> bytes:
    body = struct.pack("<BH", opcode, len(payload)) + payload
    crc = crc16_ccitt(body)
    return struct.pack("<B", SYNC) + body + struct.pack("<H", crc)


class FrameParser:
    """Incremental byte-stream parser for 0x7E-framed serial packets."""

    def __init__(self) -> None:
        self._buf = bytearray()
        self.crc_errors = 0

    def feed(self, chunk: bytes) -> list[tuple[int, bytes]]:
        self._buf.extend(chunk)
        out: list[tuple[int, bytes]] = []
        while True:
            idx = self._buf.find(SYNC)
            if idx < 0:
                self._buf.clear()
                break
            if idx > 0:
                del self._buf[:idx]
            if len(self._buf) < 6:
                break
            opcode, length = struct.unpack_from("<BH", self._buf, 1)
            if length > 128:
                del self._buf[0]
                continue
            total = 1 + 3 + length + 2
            if len(self._buf) < total:
                break
            body = bytes(self._buf[1 : 4 + length])
            (want_crc,) = struct.unpack_from("<H", self._buf, 4 + length)
            del self._buf[:total]
            if crc16_ccitt(body) != want_crc:
                self.crc_errors += 1
                continue
            out.append((opcode, body[3:]))
        return out


def pack_ack(acked_op: int, ok: int = 1) -> bytes:
    return encode_frame(OP_STATUS_ACK, struct.pack("<BB", acked_op, ok))


def pack_cmd_vel(seq: int, linear_x: float, angular_z: float) -> bytes:
    return encode_frame(OP_CMD_VEL, struct.pack("<Idd", seq, linear_x, angular_z))


def unpack_status(payload: bytes) -> dict:
    cmd_rx, state_code, vx, wz, left, right = struct.unpack("<IBdddd", payload)
    return {
        "cmd_rx": int(cmd_rx),
        "state": STATE_NAMES.get(int(state_code), f"UNKNOWN_{state_code}"),
        "vx": float(vx),
        "wz": float(wz),
        "left": float(left),
        "right": float(right),
    }
