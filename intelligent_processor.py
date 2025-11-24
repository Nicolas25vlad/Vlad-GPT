import re
import json
from typing import Dict, Any, Tuple
from system_monitor import SystemMonitor
from command_executor import CommandExecutor
from genai_integration import GenAIIntegration

class IntelligentProcessor:
    def __init__(self):
        self.monitor = SystemMonitor()
        self.executor = CommandExecutor()
        self.genai = GenAIIntegration()
        self.context = self._get_current_context()
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Obtém contexto atual do sistema"""
        try:
            return {
                "system_info": self.monitor.get_system_info(),
                "cpu_usage": self.monitor.get_cpu_usage(),
                "memory_usage": self.monitor.get_memory_usage(),
                "disk_usage": self.monitor.get_disk_usage(),
                "network_info": self.monitor.get_network_info(),
                "top_processes": self.monitor.get_running_processes(5)
            }
        except Exception as e:
            return {"error": f"Erro ao obter contexto: {e}"}
    
    def process_natural_language(self, user_input: str) -> str:
        """
        Processa linguagem natural usando IA generativa
        """
        # Atualiza contexto
        self.context = self._get_current_context()
        
        # Primeiro: verifica se é um comando direto para executar
        direct_command = self._extract_direct_command(user_input)
        if direct_command:
            result = self.executor.safe_execution(direct_command)
            return f"🔧 **Comando executado:** `{direct_command}`\n\n**Resultado:**\n```\n{result}\n```"
        
        # Segundo: detecta intenções que requerem ação imediata
        action, confidence = self._detect_intent(user_input)
        
        if confidence > 0.8:
            result = self._execute_detected_action(action, user_input)
            if result:
                return result
        
        # Terceiro: usa IA generativa e depois executa comandos mencionados na resposta
        system_prompt = self._create_system_prompt(user_input)
        
        try:
            response = self.genai.call_genai_api(
                prompt=user_input,
                system_message=system_prompt,
                context=self.context
            )
            
            # QUARTO: Agora o mais importante - EXECUTA comandos que a IA mencionou
            final_response = self._execute_commands_in_response(response, user_input)
            
            return final_response
            
        except Exception as e:
            return f"Erro no processamento: {str(e)}. Tente reformular sua pergunta."
    
    def _extract_direct_command(self, text: str) -> str:
        """Extrai comandos diretos do usuário"""
        text_lower = text.lower()
        
        # Padrões para comandos diretos
        patterns = [
            r'executar\s+(.+)',
            r'rodar\s+(.+)', 
            r'run\s+(.+)',
            r'comando\s+(.+)',
            r'execute\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                command = match.group(1).strip()
                # Remove aspas se houver
                command = command.replace('"', '').replace("'", "")
                return command
        
        return None
    
    def _detect_intent(self, text: str) -> Tuple[str, float]:
        """
        Detecta intenções específicas com confiança
        """
        text_lower = text.lower()
        
        intents = {
            "system_status": {
                "keywords": ["sistema", "status", "como está", "cpu", "memória", "disco", "uso"],
                "confidence": 0.9
            },
            "process_list": {
                "keywords": ["processos", "programas", "aplicativos", "rodando", "top", "ps"],
                "confidence": 0.9
            },
            "file_operation": {
                "keywords": ["arquivo", "arquivos", "lista", "ls", "diretório", "pasta", "listar"],
                "confidence": 0.8
            },
            "network_info": {
                "keywords": ["rede", "internet", "conexão", "ip", "ifconfig"],
                "confidence": 0.8
            },
            "disk_usage": {
                "keywords": ["disco", "espaço", "hd", "armazenamento", "df"],
                "confidence": 0.8
            },
            "help": {
                "keywords": ["ajuda", "help", "como usar"],
                "confidence": 0.95
            }
        }
        
        for intent, data in intents.items():
            if any(keyword in text_lower for keyword in data["keywords"]):
                return intent, data["confidence"]
        
        return "general", 0.5
    
    def _execute_detected_action(self, action: str, user_input: str) -> str:
        """
        Executa ações detectadas com alta confiança
        """
        if action == "system_status":
            return self._execute_system_commands()
        
        elif action == "process_list":
            return self._execute_process_commands()
        
        elif action == "file_operation":
            return self._execute_file_commands()
        
        elif action == "network_info":
            return self._execute_network_commands()
        
        elif action == "disk_usage":
            return self._execute_disk_commands()
        
        elif action == "help":
            return self._get_help()

        return ""
    
    def _execute_system_commands(self) -> str:
        """Executa comandos de sistema"""
        try:
            results = []
            
            # Comando de uptime
            uptime = self.executor.safe_execution("uptime -p")
            results.append(f"**Tempo de atividade:** {uptime.strip()}")
            
            # Comando de memória
            memory = self.executor.safe_execution("free -h")
            results.append(f"**Memória:**\n```{memory}```")
            
            # Comando de sistema
            system_info = self.executor.safe_execution("uname -a")
            results.append(f"**Sistema:** {system_info.strip()}")
            
            return "📊 **Status do Sistema (Executado):**\n\n" + "\n\n".join(results)
            
        except Exception as e:
            return f"❌ Erro ao executar comandos de sistema: {e}"
    
    def _execute_process_commands(self) -> str:
        """Executa comandos de processos"""
        try:
            processes = self.executor.safe_execution("ps aux --sort=-%cpu | head -10")
            return f"🖥️ **Processos em Execução (Executado):**\n```{processes}```"
        except Exception as e:
            return f"❌ Erro ao executar comando de processos: {e}"
    
    def _execute_file_commands(self) -> str:
        """Executa comandos de arquivos"""
        try:
            files = self.executor.safe_execution("ls -la")
            return f"📁 **Arquivos do Diretório (Executado):**\n```{files}```"
        except Exception as e:
            return f"❌ Erro ao executar comando de arquivos: {e}"
    
    def _execute_network_commands(self) -> str:
        """Executa comandos de rede"""
        try:
            ip_info = self.executor.safe_execution("ip addr show")
            return f"🌐 **Informações de Rede (Executado):**\n```{ip_info}```"
        except Exception as e:
            return f"❌ Erro ao executar comando de rede: {e}"
    
    def _execute_disk_commands(self) -> str:
        """Executa comandos de disco"""
        try:
            disk_usage = self.executor.safe_execution("df -h")
            return f"💾 **Uso de Disco (Executado):**\n```{disk_usage}```"
        except Exception as e:
            return f"❌ Erro ao executar comando de disco: {e}"
    
    def _get_help(self):
        """Retorna texto de ajuda"""
        return """
🤖 **Vlad-GPT - Assistente ATIVO para Fedora**

💡 **AGORA EU EXECUTO COMANDOS!**

⚡ **COMANDOS QUE EXECUTO AUTOMATICAMENTE:**
- `sistema` → Executa: uptime, free, uname
- `processos` → Executa: ps aux (top 10 por CPU)  
- `arquivos` → Executa: ls -la
- `rede` → Executa: ip addr show
- `disco` → Executa: df -h

🎯 **EXEMPLOS FUNCIONAIS:**
- "Mostre os processos" → Executa `ps aux` e mostra resultado
- "Como está a memória?" → Executa `free -h` 
- "Liste os arquivos" → Executa `ls -la`
- "Quais processos usam mais CPU?" → Executa `ps aux --sort=-%cpu`

🔧 **COMANDOS DIRETOS:**
- "executar ls -la"
- "rodar df -h"
- "execute ps aux"

💬 **LINGUAGEM NATURAL:**
- "Bom dia Vlad-GPT, mostre o status do sistema"
- "Quais arquivos tem nesta pasta?"
- "Monitore a rede por favor"
"""
    
    def _create_system_prompt(self, user_input: str) -> str:
        """Cria prompt do sistema que ENCORAJA execução real"""
        context = self.context
        
        prompt = f"""Você é o Vlad-GPT, assistente ATIVO para Linux Fedora.

# SUA MISSÃO PRINCIPAL: EXECUTAR COMANDOS REAIS

Você TEM ACESSO DIRETO ao terminal e PODE executar comandos.

# FORMATO OBRIGATÓRIO:
Quando for útil, INCLUA comandos no formato: 
`executar [comando-real-aqui]`

# EXEMPLOS CORRETOS:

Usuário: "Quais processos estão rodando?"
Vlad-GPT: "Vou mostrar os processos em execução: `executar ps aux --sort=-%cpu | head -10`"

Usuário: "Como está o uso de memória?"
Vlad-GPT: "Vou verificar a memória: `executar free -h`"

Usuário: "Liste os arquivos"
Vlad-GPT: "Aqui estão os arquivos: `executar ls -la`"

# CONTEXTO ATUAL:
CPU: {context.get('cpu_usage', 'N/A')}%
Memória: {context.get('memory_usage', {}).get('percent', 'N/A')}%
Disco: {context.get('disk_usage', {}).get('percent', 'N/A')}%

# COMANDOS DISPONÍVEIS:
ls, ps, top, df, free, ip, uptime, uname, etc.

NÃO APENAS SUGIRA - EXECUTE COMANDOS quando for útil!

Usuário: {user_input}

Vlad-GPT:"""
        
        return prompt
    
    def _execute_commands_in_response(self, response: str, original_input: str) -> str:
        """
        A PARTE MAIS IMPORTANTE: Executa comandos que a IA mencionou na resposta
        """
        # Procura por padrões de comandos na resposta da IA
        command_patterns = [
            r'executar\s+`([^`]+)`',
            r'`executar\s+([^`]+)`',
            r'executar\s+([^\s`]+[^`]*)',  # Captura comandos sem backticks também
        ]
        
        executed_commands = []
        final_response = response
        
        for pattern in command_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for command in matches:
                command = command.strip()
                if command and not command.startswith('http'):  # Evita URLs
                    try:
                        print(f"🔧 Executando comando detectado: {command}")
                        result = self.executor.safe_execution(command)
                        executed_commands.append((command, result))
                    except Exception as e:
                        executed_commands.append((command, f"Erro: {e}"))
        
        # Adiciona os resultados dos comandos executados à resposta
        if executed_commands:
            final_response += "\n\n" + "🔧 **COMANDOS EXECUTADOS:**"
            for cmd, result in executed_commands:
                final_response += f"\n\n**Comando:** `{cmd}`"
                final_response += f"\n**Resultado:**\n```\n{result}\n```"
        
        return final_response
    
    def get_conversation_history(self):
        """Retorna o histórico de conversação"""
        return self.genai.get_history()
    
    def clear_history(self):
        """Limpa o histórico"""
        self.genai.clear_history()