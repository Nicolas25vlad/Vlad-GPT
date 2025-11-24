import os
import json


# Configurações da API GenAI
with open("config.json") as f:
    config_data = json.load(f)
GENAI_API_KEY = config_data.get("api_key", "")


# Configurações do Sistema
SYSTEM_NAME = "Fedora Vlad-GPT IA"
USER_NAME = os.getenv("USER", "usuário")

# Configurações de Voz
VOICE_ENABLED = True
SPEECH_RATE = 180  # Um pouco mais rápido
SPEECH_VOLUME = 0.9
VOICE_TIMEOUT = 8
VOICE_PHRASE_LIMIT = 12

# Comandos Permitidos
ALLOWED_COMMANDS = [
    "ls", "pwd", "whoami", "date", "cal", "uptime", "free", "df", 
    "ps", "top", "htop", "uname", "neofetch", "cowsay", "fortune",
    "lscpu", "lshw", "ip", "ifconfig", "netstat", "ss", "ping",
    "find", "grep", "cat", "head", "tail", "wc", "du", "tree",
    "touch", "mkdir", "rm", "rmdir", "mv", "cp", "chmod", "chown",
    "sudo"
]

# Configurações de IA
AI_MAX_HISTORY = 10
AI_TEMPERATURE = 0.7
AI_MAX_TOKENS = 1000

# Configurações de UI
ENABLE_COLORS = True
ENABLE_ANIMATIONS = True