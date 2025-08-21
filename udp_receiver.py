import sys
import socket
import struct
import zlib
from pathlib import Path
import random

HDR_FMT = "!I H I"
HDR_LEN = struct.calcsize(HDR_FMT)


def parse_packet(packet: bytes):
    if len(packet) < HDR_LEN:
        return None, None, None
    seq, length, checksum = struct.unpack(HDR_FMT, packet[:HDR_LEN])
    data = packet[HDR_LEN : HDR_LEN + length]
    return seq, data, checksum


def make_ack(seq: str | bytes):
    return struct.pack("!I", seq)


def receiver(listen_port, output_file, loss_prob=0.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", listen_port))
    print(f"listening on UDP port {listen_port}")
    expected = 0
    out_path = Path(output_file)
    f = out_path.open("wb")
    sender_addr = None

    while True:
        packet, addr = sock.recvfrom(65536)
        sender_addr = addr
        seq, data, checksum = parse_packet(packet)
        if seq is None:
            continue

        if seq == 0xFFFFFFFF:
            print("EOF received, finishing.")
            ack = make_ack(expected - 1 if expected > 0 else 0)
            sock.sendto(ack, sender_addr)
            break

        if random.random() < loss_prob:
            print(f"[SIMULADO] perda recepção seq {seq}")
            continue

        calc = zlib.crc32(data) & 0xFFFFFFFF
        if calc != checksum:
            print(
                f"checksum mismatch seq {seq}, expected {checksum}, got {calc}. dropping."
            )
            continue

        if seq == expected:
            f.write(data)
            expected += 1
            ack_pkt = make_ack(seq)
            sock.sendto(ack_pkt, sender_addr)
        else:
            ack_to_send = expected - 1 if expected > 0 else 0
            sock.sendto(make_ack(ack_to_send), sender_addr)

    f.close()
    sock.close()
    print("file saved to", output_file)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    listen_port = int(sys.argv[1])
    output_file = sys.argv[2]
    loss_prob = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    receiver(listen_port, output_file, loss_prob)
