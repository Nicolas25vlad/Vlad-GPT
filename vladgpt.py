#!/usr/bin/env python3

import os
# Configura environment para áudio ANTES de qualquer import
os.environ['SDL_AUDIODRIVER'] = 'alsa'
os.environ['AUDIODRIVER'] = 'alsa'
os.environ['PULSE_RUNTIME_PATH'] = '/run/user/1000/pulse'  # Ajuste o ID do usuário se necessário

import sys
import time
from config import *
from system_monitor import SystemMonitor
from command_executor import CommandExecutor
from smooth_voice import SmoothVoice  # SUBSTITUA esta linha
from enhanced_output import EnhancedOutput  # NOVO
from intelligent_processor import IntelligentProcessor

class JARVIS:
    def __init__(self):
        self.monitor = SystemMonitor()
        self.executor = CommandExecutor()
        self.voice = SmoothVoice()  # ATUALIZADO
        self.output = EnhancedOutput()  # NOVO
        self.processor = IntelligentProcessor()
        self.running = True
        
        # Inicialização com output melhorado
        self.output.clear_screen()
        self.output.print_header()
        
        # Mensagem de boas-vindas com efeito
        welcome_msg = "Sistema Vlad-GPT inicializado. Digite 'ajuda' para ver os comandos disponíveis."
        self.output.print_jarvis_message(welcome_msg, "info")
        self.voice.speak("Olá! Eu sou o Vlad-GPT. Sistema inicializado e pronto para ajudá-lo.")
    
    def process_command(self, command):
        """Processa comandos usando IA generativa"""
        command = command.strip()
        
        # Comandos de controle do sistema
        if command in ['sair', 'exit', 'quit', 'parar']:
            self.voice.speak("Encerrando sistema Vlad-GPT. Até logo!", priority=True)
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
        
        elif command in ['voz', 'voice']:
            self.output.print_jarvis_message("Alternando para modo voz...", "info")
            self.run_voice_mode()
            return ""
        
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
Fale ou digite em {self.output.colorize('linguagem natural', 'bright_green')}! Exemplos:
• "{self.output.colorize('Como está o sistema?', 'white')}"
• "{self.output.colorize('Quais processos usam mais CPU?', 'white')}"  
• "{self.output.colorize('Execute o comando ls -la', 'white')}"
• "{self.output.colorize('Monitore a rede', 'white')}"

{self.output.colorize('⚡ COMANDOS RÁPIDOS:', 'bright_yellow')}
• {self.output.colorize('sistema', 'bright_green')}    - Status completo do sistema
• {self.output.colorize('processos', 'bright_green')}  - Lista de processos ativos
• {self.output.colorize('rede', 'bright_green')}      - Informações de rede
• {self.output.colorize('voz', 'bright_green')}       - Alterna para modo voz
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
    
    def run_voice_mode(self):
        """Modo de operação por voz com IA"""
        self.output.print_jarvis_message("Modo voz ativado. Fale seus comandos naturalmente.", "success")
        self.voice.speak("Modo de voz ativado. Pode falar seus comandos.")
        
        def voice_callback(command):
            self.output.print_user_message(command)
            result = self.process_command(command)
            if result and result != self.output.colorize("👋 Encerrando Vlad-GPT...", "bright_yellow"):
                self.output.print_jarvis_message(result)
                # Fala apenas o primeiro parágrafo para não ser muito longo
                lines = result.split('\n')
                first_line = lines[0].strip()
                if first_line and not first_line.startswith('#'):
                    speak_text = first_line[:100]  # Limita a 100 caracteres
                    self.voice.speak(speak_text)
        
        self.voice.continuous_listen(voice_callback)
        self.output.print_jarvis_message("Retornando ao modo texto.", "info")
    
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
                    try:
                        lines = result.split('\n')
                        first_line = next((l.strip() for l in lines if l.strip()), '')
                        if first_line and not first_line.startswith('#'):
                            speak_text = first_line[:150]
                            self.voice.speak(speak_text)
                    except Exception:
                        pass
                    
            except KeyboardInterrupt:
                self.output.print_jarvis_message("Interrupção detectada. Encerrando...", "warning")
                self.voice.speak("Encerrando sistema por interrupção do usuário", priority=True)
                break
            except Exception as e:
                self.output.print_jarvis_message(f"Erro: {e}", "error")
    
    def run(self, mode='text'):
        """Inicia o Vlad-GPT inteligente"""
        if mode == 'voice':
            self.run_voice_mode()
        else:
            self.run_text_mode()

if __name__ == "__main__":
    mode = 'text'
    if len(sys.argv) > 1 and sys.argv[1] in ['voice', 'voz']:
        mode = 'voice'
    
    try:
        jarvis = JARVIS()
        jarvis.run(mode)
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        print("💡 Tente reinstalar as dependências ou verificar a configuração")