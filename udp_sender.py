import sys
import socket
import struct
import zlib
import time
import threading
from pathlib import Path
import random

HDR_FMT = "!I H I"
HDR_LEN = struct.calcsize(HDR_FMT)


def make_packet(seq: int, data: bytes):
    length = len(data)
    checksum = zlib.crc32(data) & 0xFFFFFFFF
    header = struct.pack(HDR_FMT, seq, length, checksum)
    return header + data


def parse_ack(data: bytes):
    if len(data) < 4:
        return None
    return struct.unpack("!I", data[:4])[0]


def sender(
    address, filename, window_size=5, packet_size=1024, timeout=0.5, loss_prob=0.0
):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.1)
    file_path = Path(filename)
    if not file_path.exists():
        print("Arquivo não existe:", filename)
        return

    chunks = []
    with file_path.open("rb") as f:
        while True:
            b = f.read(packet_size)
            if not b:
                break
            chunks.append(b)
    total_packets = len(chunks)
    print(f"sending {filename} -> {address}, {total_packets} packets")

    base = 0
    next_seq = 0
    lock = threading.Lock()
    timer = None
    timer_start = None

    def start_timer():
        nonlocal timer_start
        timer_start = time.time()

    def stop_timer():
        nonlocal timer_start
        timer_start = None

    def timer_expired():
        nonlocal timer_start
        if timer_start is None:
            return False
        return (time.time() - timer_start) > timeout

    sent_packets = {}

    while base < total_packets:
        while next_seq < total_packets and next_seq - base < window_size:
            pkt = make_packet(next_seq, chunks[next_seq])
            if random.random() >= loss_prob:
                sock.sendto(pkt, address)
            else:
                print(f"[SIMULADO] perda pacote seq {next_seq}")
            sent_packets[next_seq] = pkt
            if base == next_seq:
                start_timer()
            next_seq += 1

        try:
            data, _ = sock.recvfrom(1024)
            ack = parse_ack(data)
            if ack is None:
                continue
            with lock:
                if ack >= base:
                    base = ack + 1
                    if base == next_seq:
                        stop_timer()
                    else:
                        start_timer()
        except socket.timeout:
            if timer_expired():
                print(f"timeout, retransmit from {base} to {next_seq-1}")
                start_timer()
                for seq in range(base, next_seq):
                    pkt = sent_packets.get(seq)
                    if pkt is None:
                        continue
                    if random.random() >= loss_prob:
                        sock.sendto(pkt, address)
                    else:
                        print(f"[SIMULADO] perda retransmissão seq {seq}")

    eof_seq = 0xFFFFFFFF
    eof_pkt = struct.pack(HDR_FMT, eof_seq, 0, 0)
    for _ in range(5):
        sock.sendto(eof_pkt, address)
    print("transfer complete")
    sock.close()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    window_size = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    packet_size = int(sys.argv[5]) if len(sys.argv) > 5 else 1024
    timeout = float(sys.argv[6]) if len(sys.argv) > 6 else 0.6
    loss_prob = float(sys.argv[7]) if len(sys.argv) > 7 else 0.0
    sender((host, port), filename, window_size, packet_size, timeout, loss_prob)
