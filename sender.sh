#!/bin/bash

IP_LOCAL=$(hostname -I | awk '{print $1}')
if [ -z "$IP_LOCAL" ]; then
    echo "Não foi possível obter o IP local."
    exit 1
fi

echo "IP local detectado: $IP_LOCAL"

# Parâmetros
PORTA=5001
ARQUIVO="arquivo_para_enviar.bin"

# Executa o sender
python3 udp_sender.py "$IP_LOCAL" "$PORTA" "$ARQUIVO" 8 1024 0.6 0.0
