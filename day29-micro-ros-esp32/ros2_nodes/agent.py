#!/usr/bin/env python3
"""Host agent: bridges a serial client onto the ROS 2 DDS graph.

Nothing on ROS 2 is created until the serial client sends CREATE_NODE,
CREATE_SUB, and CREATE_PUB frames over the UART/PTY link.
"""

from __future__ import annotations

import argparse
import errno
import os
import struct
import termios
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

from qos import command_qos, latched
from wire import (
    CLIENT_KEY,
    FrameParser,
    OP_CREATE_CLIENT,
    OP_CREATE_NODE,
    OP_CREATE_PUB,
    OP_CREATE_SUB,
    OP_STATUS_DATA,
    pack_ack,
    pack_cmd_vel,
    unpack_status,
)


def open_serial(path: str) -> int:
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    try:
        attrs = termios.tcgetattr(fd)
        attrs[0] = 0
        attrs[1] = 0
        attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        attrs[3] = 0
        attrs[4] = termios.B115200
        attrs[5] = termios.B115200
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
    except termios.error:
        pass
    return fd


class SerialAgent:
    def __init__(self, dev: str, mode: str) -> None:
        self._fd = open_serial(dev)
        self._mode = mode
        self._parser = FrameParser()
        self._session = False
        self._proxy_node: Node | None = None
        self._cmd_sub = None
        self._status_pub = None
        self._node_name = "-"
        self._sub_topic = "-"
        self._pub_topic = "-"
        self._cmd_forwarded = 0
        self._status_forwarded = 0
        self._last_state = "NONE"
        self._reported = False

    @property
    def proxy_node(self) -> Node | None:
        return self._proxy_node

    def _write_all(self, data: bytes) -> None:
        view = memoryview(data)
        sent = 0
        while sent < len(data):
            try:
                n = os.write(self._fd, view[sent:])
                sent += n
            except BlockingIOError:
                time.sleep(0.002)

    def _on_cmd_vel(self, msg: Twist) -> None:
        if not self._session:
            return
        self._cmd_forwarded += 1
        frame = pack_cmd_vel(self._cmd_forwarded, float(msg.linear.x), float(msg.angular.z))
        self._write_all(frame)

    def poll_serial(self) -> None:
        try:
            chunk = os.read(self._fd, 256)
        except OSError as exc:
            if exc.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return
            raise
        if not chunk:
            return

        for opcode, payload in self._parser.feed(chunk):
            if opcode == OP_CREATE_CLIENT and len(payload) == 4:
                (key,) = struct.unpack("<I", payload)
                ok = 1 if key == CLIENT_KEY else 0
                self._session = bool(ok)
                self._write_all(pack_ack(OP_CREATE_CLIENT, ok))
            elif opcode == OP_CREATE_NODE and self._session:
                name = payload.decode("ascii", errors="replace")
                if self._proxy_node is None:
                    self._proxy_node = Node(name)
                    self._node_name = name
                self._write_all(pack_ack(OP_CREATE_NODE, 1))
            elif opcode == OP_CREATE_SUB and self._session and self._proxy_node is not None:
                spec = payload.decode("ascii", errors="replace")
                _, topic = spec.split(":", 1)
                if self._cmd_sub is None:
                    self._cmd_sub = self._proxy_node.create_subscription(
                        Twist, topic, self._on_cmd_vel, command_qos()
                    )
                    self._sub_topic = topic
                self._write_all(pack_ack(OP_CREATE_SUB, 1))
            elif opcode == OP_CREATE_PUB and self._session and self._proxy_node is not None:
                spec = payload.decode("ascii", errors="replace")
                _, topic = spec.split(":", 1)
                if self._status_pub is None:
                    self._status_pub = self._proxy_node.create_publisher(String, topic, latched())
                    self._pub_topic = topic
                self._write_all(pack_ack(OP_CREATE_PUB, 1))
            elif opcode == OP_STATUS_DATA and self._status_pub is not None and len(payload) == 37:
                info = unpack_status(payload)
                self._status_forwarded += 1
                self._last_state = info["state"]
                out = String()
                out.data = (
                    f"state={info['state']} cmd_rx={info['cmd_rx']} "
                    f"vx={info['vx']:.3f} wz={info['wz']:.3f} "
                    f"left={info['left']:.3f} right={info['right']:.3f}"
                )
                self._status_pub.publish(out)
                self._maybe_report()

    def _maybe_report(self) -> None:
        if self._reported:
            return
        if self._mode == "bridged" and self._last_state == "DRIVING" and self._cmd_forwarded >= 5:
            self._emit_summary()
        elif self._mode == "watchdog" and self._last_state == "WATCHDOG_STOP":
            self._emit_summary()

    def _emit_summary(self) -> None:
        if self._reported:
            return
        self._reported = True
        print(
            "SUMMARY "
            f"node=agent mode={self._mode} session={int(self._session)} "
            f"ros_node={self._node_name} sub={self._sub_topic} pub={self._pub_topic} "
            f"cmd_forwarded={self._cmd_forwarded} status_forwarded={self._status_forwarded} "
            f"last_state={self._last_state} crc_err={self._parser.crc_errors}",
            flush=True,
        )
        print(f"READY node=agent mode={self._mode}", flush=True)

    def close(self) -> None:
        self._emit_summary()
        if self._proxy_node is not None:
            self._proxy_node.destroy_node()
            self._proxy_node = None
        os.close(self._fd)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", required=True)
    parser.add_argument("--mode", default="bridged", choices=("bridged", "watchdog"))
    args = parser.parse_args()

    rclpy.init()
    agent = SerialAgent(args.dev, args.mode)
    try:
        while rclpy.ok():
            agent.poll_serial()
            if agent.proxy_node is not None:
                rclpy.spin_once(agent.proxy_node, timeout_sec=0.01)
            else:
                time.sleep(0.01)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        agent.close()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
