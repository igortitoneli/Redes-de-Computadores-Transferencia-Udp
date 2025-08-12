# Transferência de Arquivos via UDP com Controle de Fluxo (Go-Back-N)

Este projeto implementa uma transferência de arquivos usando **UDP** em Python, com **controle de fluxo** baseado no protocolo **Go-Back-N**.  
Ele permite enviar arquivos de uma máquina para outra usando janelas deslizantes, ACKs e retransmissão em caso de perda de pacotes.

---

## 📂 Estrutura do Projeto

udp_sender.py # Script para enviar arquivos

udp_receiver.py # Script para receber arquivos

---

## ⚙️ Requisitos

- Python 3.6+
- Conexão de rede (pode ser local ou entre máquinas diferentes)
- Permissão para abrir portas UDP

---

## 🚀 Como Usar

### 1️⃣ Passo 1 — Inicie o receptor
Na máquina que **vai receber** o arquivo:

```bash
python udp_receiver.py <porta> <arquivo_saida> [probabilidade_perda]

python udp_receiver.py 5001 recebido.bin
```

porta → Porta UDP para ouvir (ex.: 5001)

arquivo_saida → Caminho onde o arquivo recebido será salvo

probabilidade_perda (opcional) → Valor entre 0.0 e 1.0 para simular perda de pacotes (padrão: 0.0)


```bash
python udp_sender.py <ip_receptor> <porta_receptor> <arquivo_para_enviar> [janela] [tam_pacote] [timeout] [probabilidade_perda]

python udp_sender.py 192.168.96.1 5001 arquivo.txt 8 1024 0.6 0.0
```

ip_receptor → IP da máquina que está rodando o udp_receiver.py

porta_receptor → Porta onde o receptor está ouvindo

arquivo_para_enviar → Caminho do arquivo que será enviado

janela (opcional) → Tamanho da janela (padrão: 8)

tam_pacote (opcional) → Tamanho de cada pacote em bytes (padrão: 1024)

timeout (opcional) → Timeout para retransmissão, em segundos (padrão: 0.6)

probabilidade_perda (opcional) → Valor entre 0.0 e 1.0 para simular perda (padrão: 0.0)



