import subprocess
import os
from config import ALLOWED_COMMANDS

class CommandExecutor:
    def __init__(self):
        self.allowed_commands = ALLOWED_COMMANDS
    
    def execute_command(self, command):
        """Executa comandos do sistema de forma segura"""
        try:
            # Verifica se o comando é permitido
            base_command = command.split()[0] if command.split() else command
            if base_command not in self.allowed_commands:
                return f"Erro: Comando '{base_command}' não é permitido."
            
            # Executa o comando
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout if result.stdout else "Comando executado com sucesso."
            else:
                return f"Erro: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Erro: Comando expirou (timeout)."
        except Exception as e:
            return f"Erro ao executar comando: {str(e)}"
    
    def safe_execution(self, command):
        """Execução segura com validação adicional"""
        dangerous_keywords = ['rm -rf', 'format', 'dd', 'mkfs', 'fdisk']
        
        if any(keyword in command for keyword in dangerous_keywords):
            return "Erro: Comando potencialmente perigoso detectado."
        
        return self.execute_command(command)