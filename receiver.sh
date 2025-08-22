#!/bin/bash

# Parâmetros
PORTA=5001
ARQUIVO="./receiver/recebido.bin"

# Executa o receiver
python3 udp_receiver.py "$PORTA" "$ARQUIVO" 0.0
