import os
import sys
import time
import threading
from typing import Dict, Any, List

class EnhancedOutput:
    def __init__(self):
        self.colors = self._init_colors()
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_running = False
        self.spinner_thread = None
    
    def _init_colors(self) -> Dict[str, str]:
        """Inicializa cores para terminal"""
        colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'italic': '\033[3m',
            
            # Cores básicas
            'black': '\033[30m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            
            # Cores brilhantes
            'bright_red': '\033[91m',
            'bright_green': '\033[92m',
            'bright_yellow': '\033[93m',
            'bright_blue': '\033[94m',
            'bright_magenta': '\033[95m',
            'bright_cyan': '\033[96m',
            'bright_white': '\033[97m',
            
            # Fundos
            'bg_blue': '\033[44m',
            'bg_green': '\033[42m',
            'bg_yellow': '\033[43m',
            'bg_red': '\033[41m',
        }
        return colors
    
    def colorize(self, text: str, color: str, style: str = '') -> str:
        """Aplica cor e estilo ao texto"""
        color_code = self.colors.get(color, '')
        style_code = self.colors.get(style, '')
        reset = self.colors['reset']
        return f"{style_code}{color_code}{text}{reset}"
    
    def clear_screen(self):
        """Limpa a tela"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Imprime cabeçalho do Vlad-GPT"""
        header = f"""
{self.colorize('╔══════════════════════════════════════════════════════════════╗', 'bright_blue')}
{self.colorize('║', 'bright_blue')}          {self.colorize('🤖 Vlad-GPT - Intelligent Assistant', 'bright_cyan', 'bold')}                 {self.colorize('║', 'bright_blue')}
{self.colorize('║', 'bright_blue')}    {self.colorize('Just A Rather Very Intelligent System', 'bright_white')}                     {self.colorize('║', 'bright_blue')}
{self.colorize('║', 'bright_blue')}         {self.colorize('for Linux Fedora', 'bright_yellow')}                                     {self.colorize('║', 'bright_blue')}
{self.colorize('╚══════════════════════════════════════════════════════════════╝', 'bright_blue')}
        """
        print(header)
    
    def print_user_message(self, message: str):
        """Formata mensagem do usuário"""
        formatted = f"\n{self.colorize('👤 Você:', 'bright_green', 'bold')} {message}"
        print(formatted)
    
    def print_jarvis_message(self, message: str, message_type: str = "normal"):
        """Formata mensagem do Vlad-GPT"""
        # Define cores baseadas no tipo de mensagem
        type_colors = {
            "normal": ("bright_cyan", "🤖"),
            "warning": ("bright_yellow", "⚠️"),
            "error": ("bright_red", "❌"),
            "success": ("bright_green", "✅"),
            "info": ("bright_blue", "ℹ️"),
            "system": ("bright_magenta", "💻")
        }
        
        color, emoji = type_colors.get(message_type, ("bright_cyan", "🤖"))
        
        # Divide mensagens longas
        lines = message.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            if i == 0:
                prefix = f"{emoji} {self.colorize('Vlad-GPT:', color, 'bold')}"
            else:
                prefix = " " * 10  # Alinhamento para linhas subsequentes
            
            formatted_lines.append(f"{prefix} {line}")
        
        print("\n" + "\n".join(formatted_lines))
    
    def print_system_info(self, system_data: Dict[str, Any]):
        """Formata informações do sistema de forma bonita"""
        info = f"""
{self.colorize('📊 STATUS DO SISTEMA', 'bright_cyan', 'bold')}
{self.colorize('┌────────────────────────────────────────────────────────────┐', 'bright_blue')}
{self.colorize('│', 'bright_blue')}    {self.colorize('💻 CPU:', 'bright_green')} {system_data['cpu_usage']:>5}% utilizado          {self.colorize('│', 'bright_blue')}
{self.colorize('│', 'bright_blue')}    {self.colorize('🧠 Memória:', 'bright_green')} {system_data['memory_usage']['percent']:>5}% ({system_data['memory_usage']['used']//1024//1024:>4}MB / {system_data['memory_usage']['total']//1024//1024:>4}MB) {self.colorize('│', 'bright_blue')}
{self.colorize('│', 'bright_blue')}    {self.colorize('💾 Disco:', 'bright_green')} {system_data['disk_usage']['percent']:>5}% usado             {self.colorize('│', 'bright_blue')}
{self.colorize('│', 'bright_blue')}    {self.colorize('🌐 Rede:', 'bright_green')} ↓{system_data['network_info']['bytes_recv']//1024:>5}KB ↑{system_data['network_info']['bytes_sent']//1024:>5}KB {self.colorize('│', 'bright_blue')}
{self.colorize('└────────────────────────────────────────────────────────────┘', 'bright_blue')}
        """
        print(info)
    
    def print_command_result(self, command: str, result: str):
        """Formata resultado de comandos"""
        border = self.colorize("═" * 60, "bright_blue")
        print(f"\n{border}")
        print(f"{self.colorize('🔧 COMANDO EXECUTADO:', 'bright_yellow', 'bold')} {self.colorize(command, 'bright_white')}")
        print(f"{border}")
        print(f"{self.colorize(result, 'white')}")
        print(f"{border}\n")
    
    def start_spinner(self, message: str = "Processando"):
        """Inicia spinner de loading"""
        self.spinner_running = True
        
        def spin():
            i = 0
            while self.spinner_running:
                char = self.spinner_chars[i % len(self.spinner_chars)]
                sys.stdout.write(f"\r{self.colorize(char, 'bright_cyan')} {message}... ")
                sys.stdout.flush()
                time.sleep(0.1)
                i += 1
            sys.stdout.write('\r' + ' ' * 50 + '\r')  # Limpa linha
        
        self.spinner_thread = threading.Thread(target=spin)
        self.spinner_thread.start()
    
    def stop_spinner(self):
        """Para o spinner"""
        self.spinner_running = False
        if self.spinner_thread:
            self.spinner_thread.join()
    
    def typewriter_effect(self, text: str, delay: float = 0.02):
        """Efeito máquina de escrever"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()  # Nova linha no final
    
    def progress_bar(self, current: int, total: int, length: int = 40):
        """Barra de progresso"""
        percent = current / total
        filled = int(length * percent)
        bar = self.colorize('█' * filled, 'bright_green') + self.colorize('░' * (length - filled), 'dim')
        print(f"\r[{bar}] {percent:.1%}", end='', flush=True)
        if current == total:
            print()  # Nova linha quando completar