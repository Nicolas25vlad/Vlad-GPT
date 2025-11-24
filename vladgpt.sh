#!/bin/bash

# Buscar o arquivo vladgpt.py recursivamente a partir do HOME
VLADGPT_PATH=$(find $HOME -name "vladgpt.py" -type f 2>/dev/null | head -n 1)

# Verificar se encontrou o arquivo
if [ -z "$VLADGPT_PATH" ]; then
    echo "Erro: Arquivo vladgpt.py não encontrado em $HOME"
    exit 1
fi

# Executar o arquivo
sudo python3 "$VLADGPT_PATH"