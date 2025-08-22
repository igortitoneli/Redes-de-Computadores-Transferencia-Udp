#!/bin/bash

# Parâmetros
PORTA=5001
ARQUIVO="./receiver/small_file.txt"

# Executa o receiver
python3 udp_receiver.py "$PORTA" "$ARQUIVO" 0.0
