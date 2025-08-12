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
        # EOF packet
        if seq == 0xFFFFFFFF:
            print("EOF received, finishing.")
            # send final ACK for last received seq - 1
            ack = make_ack(expected - 1 if expected > 0 else 0)
            sock.sendto(ack, sender_addr)
            break

        # optional simulate loss of incoming packets
        if random.random() < loss_prob:
            print(f"[SIMULADO] perda recepção seq {seq}")
            continue

        # validate checksum
        calc = zlib.crc32(data) & 0xFFFFFFFF
        if calc != checksum:
            print(
                f"checksum mismatch seq {seq}, expected {checksum}, got {calc}. dropping."
            )
            continue

        # If seq == expected, accept and advance; if greater, it's out of order -> drop (GBN).
        if seq == expected:
            f.write(data)
            expected += 1
            # send cumulative ack (last in-order seq)
            ack_pkt = make_ack(seq)
            sock.sendto(ack_pkt, sender_addr)
        else:
            # duplicate or out-of-order; resend last ack (expected-1) to inform sender
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
