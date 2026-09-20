#!/usr/bin/env bash
# Investigation C — durability / late-join latch behavior
set -euo pipefail
cd "$(dirname "$0")"
source ./env.sh
ros2 daemon stop >/dev/null 2>&1 || true

echo "=== C1: VOLATILE both sides — late joiner gets NEW samples only ==="
echo "1) Start pub (transient_local:=false path = volatile):"
echo "   python3 qos_pub.py --ros-args -p reliability:=reliable -p durability:=volatile -p publish_hz:=2.0"
echo "2) Wait ~3 s, then start sub with same QoS."
echo "Expect: first last_seq is near 'live', not 1."
echo
echo "=== C2: TRANSIENT_LOCAL both sides — late joiner can get retained history ==="
echo "1) python3 qos_pub.py --ros-args -p reliability:=reliable -p durability:=transient_local -p depth:=10 -p publish_hz:=2.0"
echo "2) Wait ~3 s, then:"
echo "   python3 qos_sub.py --ros-args -p reliability:=reliable -p durability:=transient_local -p depth:=10"
echo "Expect: late sub may receive older retained seqs (within depth)."
echo
echo "=== C3: MISMATCH — VOLATILE pub + TRANSIENT_LOCAL sub (expect ZERO) ==="
echo "  pub:  durability:=volatile"
echo "  sub:  durability:=transient_local"
echo "Expect: endpoints visible, no data path."
