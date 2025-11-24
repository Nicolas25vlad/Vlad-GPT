import os
import google.generativeai as genai
import logging
from typing import Dict, List, Any
from config import GENAI_API_KEY

class GenAIIntegration:
    def __init__(self):
        self.api_key = GENAI_API_KEY
        self.model = None
        self.chat_instance = None
        self.conversation_history = []
        self.max_history = 10
        self._initialize_model()
    
    def _initialize_model(self):
        """Inicializa o modelo Gemini"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
            self.chat_instance = self.model.start_chat(history=[])
            print("✅ Modelo Gemini 2.0 Flash inicializado com sucesso!")
        except Exception as e:
            logging.error(f"Erro ao inicializar modelo Gemini: {e}")
            raise
    
    def call_genai_api(self, prompt: str, system_message: str = None, context: Dict = None) -> str:
        """
        Faz chamada para API Gemini usando a biblioteca oficial
        """
        try:
            # Prepara o prompt completo
            full_prompt = self._build_prompt(prompt, system_message, context)
            
            # Envia mensagem para o modelo
            response = self.chat_instance.send_message(full_prompt)
            text_response = response.text
            
            # Atualiza histórico
            self._update_history(prompt, text_response)
            
            return text_response
            
        except Exception as e:
            logging.error(f"Erro na chamada da API Gemini: {e}")
            return self._fallback_response(prompt, context)
    
    def _build_prompt(self, prompt: str, system_message: str, context: Dict) -> str:
        """Constrói o prompt completo"""
        if not system_message:
            system_message = self._get_system_prompt()
        
        context_str = ""
        if context:
            context_str = f"\n\n--- CONTEXTO DO SISTEMA ---\n"
            context_str += f"CPU: {context.get('cpu_usage', 'N/A')}%\n"
            context_str += f"Memória: {context.get('memory_usage', {}).get('percent', 'N/A')}%\n"
            context_str += f"Disco: {context.get('disk_usage', {}).get('percent', 'N/A')}%\n"
            context_str += f"Processos ativos: {len(context.get('top_processes', []))}\n"
            context_str += f"Sistema: {context.get('system_info', {}).get('system', 'N/A')} {context.get('system_info', {}).get('release', 'N/A')}\n"
            context_str += "--- FIM DO CONTEXTO ---\n"
        
        history_str = self._get_conversation_history()
        
        return f"{system_message}{context_str}{history_str}\n\nUSUÁRIO: {prompt}\n\nVlad-GPT:"
    
    def _get_conversation_history(self) -> str:
        """Retorna o histórico como string"""
        if not self.conversation_history:
            return ""
        
        history_text = "\n\n--- HISTÓRICO DA CONVERSA ---"
        for msg in self.conversation_history[-self.max_history:]:
            role = "USUÁRIO" if msg["role"] == "user" else "Vlad-GPT"
            # Limita o tamanho de cada mensagem no histórico
            content = msg['content']
            if len(content) > 200:
                content = content[:200] + "..."
            history_text += f"\n{role}: {content}"
        history_text += "\n--- FIM DO HISTÓRICO ---"
        
        return history_text
    
    def _update_history(self, user_message: str, assistant_message: str):
        """Atualiza o histórico de conversação"""
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        # Mantém apenas o histórico mais recente
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-(self.max_history * 2):]
    
    def _get_system_prompt(self) -> str:
        """
        Retorna o prompt do sistema que define o comportamento do Vlad-GPT
        """
        return """Você é o Vlad-GPT (Just A Rather Very Intelligent System), um assistente pessoal INTEGRADO e ATIVO para Linux Fedora.

# SUA IDENTIDADE E CAPACIDADES:
- Você é um assistente INTELIGENTE e ATIVO que PODE executar comandos no sistema
- Você está INTEGRADO diretamente com o terminal Linux Fedora do usuário
- Você tem PERMISSÃO para executar comandos seguros através da função `executar [comando]`
- Você recebe informações em tempo real do sistema (CPU, memória, processos, etc.)

# SUAS CAPACIDADES DE EXECUÇÃO:
✅ **VOCÊ PODE EXECUTAR COMANDOS** usando o formato: `executar [comando]`
✅ **VOCÊ TEM ACESSO** aos comandos permitidos predefinidos
✅ **VOCÊ PODE** monitorar, analisar e interagir com o sistema
✅ **VOCÊ PODE** sugerir e executar comandos úteis

# COMANDOS QUE VOCÊ PODE EXECUTAR:
- Monitoramento: `ps`, `top`, `htop`, `free`, `df`, `uptime`, `neofetch`
- Sistema: `uname`, `lscpu`, `lshw`, `whoami`, `date`
- Arquivos: `ls`, `find`, `grep`, `cat`, `head`, `tail`, `tree`, `du`
- Rede: `ip`, `ifconfig`, `ping`, `netstat`, `ss`
- Utilitários: `cal`, `cowsay`, `fortune`

# FORMATO DE RESPOSTA ATIVA:
1. **SEJA PROATIVO**: Quando relevante, EXECUTE comandos para obter informações
2. **EXPLIQUE E EXECUTE**: Primeiro explique o que vai fazer, depois execute
3. **USE COMANDOS**: Para perguntas sobre o sistema, USE comandos para obter dados reais
4. **SEJA ÚTIL**: Não apenas sugira - EXECUTE quando for útil

# EXEMPLOS DE COMO AGIR:

❌ **ERRADO**: "Você pode executar o comando ls para ver os arquivos"
✅ **CORRETO**: "Vou listar os arquivos no diretório atual: `executar ls -la`"

❌ **ERRADO**: "O comando df mostra uso do disco"
✅ **CORRETO**: "Vou verificar o uso do disco: `executar df -h`"

❌ **ERRADO**: "Talvez você queira ver os processos"
✅ **CORRETO**: "Vou mostrar os processos em execução: `executar ps aux --sort=-%cpu | head -10`"

# SEGURANÇA:
- Apenas comandos da lista permitida serão executados
- Você NÃO precisa pedir permissão para comandos seguros
- Comandos complexos devem ser explicados brevemente antes
- Mantenha o usuário informado sobre o que está fazendo

# PERSONALIDADE:
- Formal mas amigável, como um mordomo eficiente
- Técnico mas acessível
- PROATIVO - tome iniciativa quando for útil
- ÚTIL - resolva problemas ativamente

Agora, responda de forma ATIVA e PRÁTICA, executando comandos quando necessário para fornecer informações precisas e úteis."""
    
    def _fallback_response(self, prompt: str, context: Dict = None) -> str:
        """
        Resposta de fallback quando a API não está disponível
        """
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['oi', 'olá', 'hello', 'ola', 'bom dia', 'boa tarde', 'boa noite']):
            return "Olá! Sou o Vlad-GPT, seu assistente pessoal para Linux Fedora. No momento estou operando com recursos locais. Posso ajudar com monitoramento do sistema e execução de comandos seguros. Digite 'ajuda' para ver todas as opções disponíveis."
        
        elif any(word in prompt_lower for word in ['sistema', 'cpu', 'memória', 'disco', 'status', 'desempenho']):
            if context:
                return f"📊 **Status do Sistema (Local):**\n• CPU: {context.get('cpu_usage', 'N/A')}%\n• Memória: {context.get('memory_usage', {}).get('percent', 'N/A')}%\n• Disco: {context.get('disk_usage', {}).get('percent', 'N/A')}%\n\n💡 Use 'sistema' para informações detalhadas."
            return "Posso verificar o status do sistema. Use 'sistema' para informações detalhadas."
        
        elif any(word in prompt_lower for word in ['executar', 'comando', 'rodar', 'run']):
            return "Para executar comandos, use: 'executar [comando]'. Exemplo: 'executar ls -la'"
        
        elif any(word in prompt_lower for word in ['processos', 'programas', 'aplicativos']):
            return "Posso mostrar os processos em execução. Use 'processos' para ver a lista."
        
        elif any(word in prompt_lower for word in ['ajuda', 'help', 'como usar']):
            return "**Comandos disponíveis:**\n- 'sistema': Status do sistema\n- 'processos': Lista de processos\n- 'executar [comando]': Executa comandos\n- 'ajuda': Mostra esta mensagem\n- 'sair': Encerra o Vlad-GPT"
        
        else:
            return "Desculpe, no momento estou com acesso limitado à minha IA principal. Posso ajudar com: monitoramento do sistema, execução de comandos seguros, e informações básicas. Digite 'ajuda' para ver todas as opções."

    def clear_history(self):
        """Limpa o histórico de conversação"""
        self.conversation_history.clear()
        # Reinicia o chat também
        try:
            self.chat_instance = self.model.start_chat(history=[])
        except:
            pass

    def get_history(self):
        """Retorna o histórico de conversação"""
        return self.conversation_history