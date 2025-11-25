#!/usr/bin/env python3

import os
import sys
import time
from config import *
from system_monitor import SystemMonitor
from command_executor import CommandExecutor
from enhanced_output import EnhancedOutput
from intelligent_processor import IntelligentProcessor

class JARVIS:
    def __init__(self):
        self.monitor = SystemMonitor()
        self.executor = CommandExecutor()
        self.output = EnhancedOutput()
        self.processor = IntelligentProcessor()
        self.running = True
        
        # Inicialização com output melhorado
        self.output.clear_screen()
        self.output.print_header()
        
        # Mensagem de boas-vindas
        welcome_msg = "Sistema Vlad-GPT inicializado. Digite 'ajuda' para ver os comandos disponíveis."
        self.output.print_jarvis_message(welcome_msg, "info")
        print("🔇 Modo sem voz ativado")
    
    def process_command(self, command):
        """Processa comandos usando IA generativa"""
        command = command.strip()
        
        # Comandos de controle do sistema
        if command in ['sair', 'exit', 'quit', 'parar']:
            self.running = False
            return self.output.colorize("👋 Encerrando Vlad-GPT...", "bright_yellow")
        
        elif command in ['ajuda', 'help', '?']:
            return self.show_help()
        
        elif command in ['limpar', 'clear', 'cls']:
            self.output.clear_screen()
            self.output.print_header()
            return ""
        
        elif command in ['histórico', 'history']:
            return self.show_conversation_history()
        
        elif command in ['sistema', 'system', 'status']:
            return self.show_system_info()
        
        elif command == '':
            return ""
        
        else:
            try:
                # Mostra spinner durante processamento
                self.output.start_spinner("Processando comando")
                result = self.processor.process_natural_language(command)
                self.output.stop_spinner()
                return result
            except Exception as e:
                self.output.stop_spinner()
                error_msg = f"Erro no processamento: {str(e)}"
                self.output.print_jarvis_message(error_msg, "error")
                return error_msg
    
    def show_help(self):
        """Exibe ajuda inteligente com formatação melhorada"""
        help_text = f"""
{self.output.colorize('🤖 Vlad-GPT - ASSISTENTE INTELIGENTE', 'bright_cyan', 'bold')}

{self.output.colorize('💡 COMO USAR:', 'bright_yellow')}
Digite em {self.output.colorize('linguagem natural', 'bright_green')}! Exemplos:
• "{self.output.colorize('Como está o sistema?', 'white')}"
• "{self.output.colorize('Quais processos usam mais CPU?', 'white')}"  
• "{self.output.colorize('Execute o comando ls -la', 'white')}"
• "{self.output.colorize('Monitore a rede', 'white')}"

{self.output.colorize('⚡ COMANDOS RÁPIDOS:', 'bright_yellow')}
• {self.output.colorize('sistema', 'bright_green')}    - Status completo do sistema
• {self.output.colorize('processos', 'bright_green')}  - Lista de processos ativos
• {self.output.colorize('rede', 'bright_green')}      - Informações de rede
• {self.output.colorize('limpar', 'bright_green')}    - Limpa a tela
• {self.output.colorize('sair', 'bright_red')}        - Encerra o Vlad-GPT

{self.output.colorize('🔧 FUNCIONALIDADES:', 'bright_yellow')}
• {self.output.colorize('Monitoramento em tempo real', 'white')}
• {self.output.colorize('Execução segura de comandos', 'white')}
• {self.output.colorize('Análise inteligente do sistema', 'white')}
• {self.output.colorize('Sugestões de otimização', 'white')}
• {self.output.colorize('Suporte a linguagem natural', 'white')}

{self.output.colorize('🎯 DICA:', 'bright_magenta')} Experimente comandos como:
"{self.output.colorize('Bom dia Vlad-GPT, como está o sistema?', 'bright_white')}"
"""
        return help_text
    
    def show_system_info(self):
        """Exibe informações do sistema formatadas"""
        context = self.processor.context
        self.output.print_system_info({
            'cpu_usage': context['cpu_usage'],
            'memory_usage': context['memory_usage'],
            'disk_usage': context['disk_usage'],
            'network_info': context['network_info']
        })
        return ""
    
    def show_conversation_history(self):
        """Mostra histórico da conversa"""
        history = self.processor.get_conversation_history()
        if not history:
            return self.output.colorize("📝 Nenhuma conversa no histórico.", "dim")
        
        history_text = f"\n{self.output.colorize('📝 HISTÓRICO DA CONVERSA:', 'bright_cyan', 'bold')}\n"
        for i, msg in enumerate(history[-6:], 1):  # Últimas 6 mensagens
            if msg["role"] == "user":
                prefix = self.output.colorize("👤 Você:", "bright_green")
                content = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
            else:
                prefix = self.output.colorize("🤖 Vlad-GPT:", "bright_cyan")
                content = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
            
            history_text += f"\n{self.output.colorize(f'{i:2d}.', 'dim')} {prefix} {content}"
        
        return history_text
    
    def run_text_mode(self):
        """Modo de operação por texto com output melhorado"""
        while self.running:
            try:
                # Prompt colorido
                prompt = f"{self.output.colorize('👤', 'bright_green')} {self.output.colorize('Você', 'bright_green', 'bold')}{self.output.colorize(':', 'bright_green')} "
                command = input(prompt).strip()
                
                result = self.process_command(command)
                if result and result != self.output.colorize("👋 Encerrando Vlad-GPT...", "bright_yellow"):
                    self.output.print_jarvis_message(result)
                    
            except KeyboardInterrupt:
                self.output.print_jarvis_message("Interrupção detectada. Encerrando...", "warning")
                break
            except Exception as e:
                self.output.print_jarvis_message(f"Erro: {e}", "error")
    
    def run(self):
        """Inicia o Vlad-GPT inteligente (apenas modo texto)"""
        self.run_text_mode()

if __name__ == "__main__":
    try:
        jarvis = JARVIS()
        jarvis.run()
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        print("💡 Tente reinstalar as dependências ou verificar a configuração")