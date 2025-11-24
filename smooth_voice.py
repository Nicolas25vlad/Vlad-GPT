import os
import threading
import queue
import tempfile
import subprocess
from typing import Optional, Callable, List, Dict
import speech_recognition as sr
from config import VOICE_ENABLED

class SmoothVoice:
    os.environ['SDL_AUDIODRIVER'] = 'alsa'
    os.environ['AUDIODRIVER'] = 'alsa'
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.voice_thread = None
        self.recognition_callback = None
        self.current_voice_engine = "edge_tts"  # Melhor qualidade
        
        # Configurações de vozes disponíveis (eSpeak removido)
        self.voice_engines = {
            "edge_tts": {
                "name": "Edge TTS (Recomendado)",
                "command": "edge-tts",
                "args": ["--voice", "pt-BR-AntonioNeural", "--rate=+25%"],
                "available": self._check_edge_tts()
            },
            "google_tts_simple": {
                "name": "Google TTS Simples",
                "command": "python3",
                "args": [],
                "available": self._check_google_tts_simple(),
                "function": self._speak_google_tts_simple
            }
        }
        
        if VOICE_ENABLED:
            self._select_best_voice_engine()
            self._start_speech_thread()
            print(f"🎤 Voz inicializada: {self.voice_engines[self.current_voice_engine]['name']}")
    
    # eSpeak não é mais utilizado
    
    def _check_edge_tts(self) -> bool:
        """Verifica se Edge TTS está disponível"""
        try:
            result = subprocess.run(["which", "edge-tts"], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_google_tts_simple(self) -> bool:
        """Verifica se temos as dependências mínimas para Google TTS"""
        try:
            from gtts import gTTS
            return True
        except ImportError:
            return False
    
    def _select_best_voice_engine(self):
        """Seleciona o melhor mecanismo de voz disponível"""
        preferred_order = ["edge_tts", "google_tts_simple"]
        
        for engine in preferred_order:
            if self.voice_engines[engine]["available"]:
                self.current_voice_engine = engine
                return
        
        print("⚠️  Nenhum mecanismo de voz encontrado. Desativando síntese de voz.")
        global VOICE_ENABLED
        VOICE_ENABLED = False
    
    def _start_speech_thread(self):
        """Inicia thread para processamento de fala"""
        def speech_worker():
            while True:
                text, priority = self.speech_queue.get()
                if text is None:  # Sentinel value to stop
                    break
                self._speak_sync(text, priority)
                self.speech_queue.task_done()
        
        self.voice_thread = threading.Thread(target=speech_worker, daemon=True)
        self.voice_thread.start()
    
    def _speak_sync(self, text: str, priority: bool = False):
        """Fala o texto usando o mecanismo selecionado"""
        if not VOICE_ENABLED:
            return
        
        self.is_speaking = True
        # Limpa e prepara o texto
        text = self._clean_text(text)
        if len(text) > 250:
            text = text[:250] + "..."

        engine = self.voice_engines[self.current_voice_engine]
        success = False

        # Tenta função interna (gTTS) ou comando de sistema
        if "function" in engine:
            try:
                engine["function"](text)
                success = True
            except Exception:
                success = False
        else:
            try:
                success = self._speak_system_command(text, engine)
            except Exception:
                success = False

        # Se falhou, tenta fallback para Google TTS (silencioso)
        if not success:
            if (
                "google_tts_simple" in self.voice_engines
                and self.voice_engines["google_tts_simple"]["available"]
                and self.current_voice_engine != "google_tts_simple"
            ):
                try:
                    self.voice_engines["google_tts_simple"]["function"](text)
                    success = True
                except Exception:
                    success = False

        if not success:
            print("❌ Erro na síntese de voz: todos os mecanismos falharam.")

        self.is_speaking = False
    
    def _clean_text(self, text: str) -> str:
        """Limpa o texto para síntese de voz - mantém frases completas"""
        import re
        
        # Remove formatação markdown
        text = re.sub(r'[\*\#\_\`\-\=\|]', '', text)
        
        # Remove URLs e links
        text = re.sub(r'http\S+', '', text)
        
        # Remove conteúdo entre chaves (como JSON)
        text = re.sub(r'\{.*?\}', '', text)
        
        # Remove múltiplos espaços
        text = re.sub(r'\s+', ' ', text)
        
        # Mantém apenas frases completas
        sentences = re.split(r'[.!?]+', text)
        clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Junta frases até atingir ~250 caracteres (mantém frases completas)
        result = ""
        for sentence in clean_sentences[:5]:  # Máximo 5 frases
            if len(result) + len(sentence) + 2 <= 250:
                result += sentence + ". "
            else:
                break
        
        return result.strip()
    
    def _speak_system_command(self, text: str, engine: Dict):
        """Fala usando comandos de sistema"""
        # Retorna True em sucesso, False em falha (não lança exceção para permitir fallback silencioso)
        if engine["command"] == "edge-tts":
            # Edge TTS - melhor qualidade
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                temp_file = f.name

            try:
                # Gera áudio com Edge TTS
                tts_cmd = [engine["command"]] + engine["args"] + ["--text", text, "--write-media", temp_file]
                proc = subprocess.run(tts_cmd, capture_output=True, text=True)
                if proc.returncode != 0:
                    return False
                # Post-processa para timbre JARVIS se possível
                play_file = self._postprocess_audio(temp_file)

                # Reproduz com mpv (mais suave) ou ffplay
                players = ["mpv", "ffplay", "mplayer", "play"]
                played = False
                for player in players:
                    if subprocess.run(["which", player], capture_output=True).returncode == 0:
                        try:
                            if player == "mpv":
                                subprocess.run([player, "--no-video", "--really-quiet", play_file], check=True)
                            elif player == "ffplay":
                                subprocess.run([player, "-autoexit", "-nodisp", play_file], check=True, capture_output=True)
                            elif player == "mplayer":
                                subprocess.run([player, "-really-quiet", play_file], check=True, capture_output=True)
                            else:
                                subprocess.run([player, play_file], check=True, capture_output=True)
                            played = True
                        except Exception:
                            played = False
                        break

                # Remove arquivo pós-processado se foi gerado
                if play_file != temp_file and os.path.exists(play_file):
                    try:
                        os.unlink(play_file)
                    except:
                        pass

                return played
            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

        else:
            # Tenta executar comando genérico como fallback (se definido)
            cmd = [engine.get("command")] + engine.get("args", []) + [text]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            return proc.returncode == 0
    
    def _speak_google_tts_simple(self, text: str):
        """Google TTS simplificado - sem pygame"""
        try:
            from gtts import gTTS
            
            # Limita texto
            if len(text) > 200:
                text = text[:200] + "..."
            
            # Cria áudio temporário
            tts = gTTS(text=text, lang='pt', slow=False, lang_check=False)
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                temp_file = f.name
            
            try:
                tts.save(temp_file)

                # Post-processa para timbre JARVIS se possível
                play_file = self._postprocess_audio(temp_file)

                # Reproduz com player disponível
                players = ["mpv", "ffplay", "mplayer", "play"]
                for player in players:
                    if subprocess.run(["which", player], capture_output=True).returncode == 0:
                        if player == "mpv":
                            subprocess.run([player, "--no-video", "--really-quiet", play_file], check=True)
                        elif player == "ffplay":
                            subprocess.run([player, "-autoexit", "-nodisp", play_file], check=True, capture_output=True)
                        break

                # Remove arquivo pós-processado se foi gerado
                if play_file != temp_file and os.path.exists(play_file):
                    try:
                        os.unlink(play_file)
                    except:
                        pass
                        
            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except Exception as e:
            raise Exception(f"Erro no Google TTS: {e}")

    def _postprocess_audio(self, infile: str) -> str:
        """Aplica efeitos para timbre masculino/robótico (JARVIS-like) com ffmpeg.

        Retorna o caminho do arquivo a ser reproduzido (pode ser o mesmo `infile` se ffmpeg não disponível).
        """
        # Verifica se ffmpeg está disponível
        try:
            if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
                return infile
        except Exception:
            return infile

        # Cria arquivo processado
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            out_file = f.name

        # Ajustes para voz grave/robótica:
        # 1. lowpass=2000: Remove altas frequências (deixa mais grave/robótico)
        # 2. highpass=100: Remove muito grave (melhora clareza)
        # 3. aresample: Resampling para efeito robótico
        # 4. atempo=1.5: Acelera significativamente (50% mais rápido)
        # 5. volume=1.3: Aumenta volume para melhor projeção
        ff_cmd = [
            "ffmpeg", "-y", "-i", infile,
            "-filter_complex",
            "lowpass=2000,highpass=100,aresample=44100,atempo=1.5,volume=1.3",
            "-q:a", "4", out_file
        ]

        try:
            proc = subprocess.run(ff_cmd, capture_output=True)
            if proc.returncode == 0:
                return out_file
            else:
                try:
                    os.unlink(out_file)
                except:
                    pass
                return infile
        except Exception:
            try:
                os.unlink(out_file)
            except:
                pass
            return infile
    
    def speak(self, text: str, priority: bool = False):
        """Fala o texto de forma assíncrona"""
        if not VOICE_ENABLED:
            return
        
        if priority and self.is_speaking:
            self.stop_speaking()
            threading.Event().wait(0.3)
        
        self.speech_queue.put((text, priority))
    
    def stop_speaking(self):
        """Para a fala atual"""
        try:
            subprocess.run(["pkill", "mpv"], capture_output=True)
            subprocess.run(["pkill", "ffplay"], capture_output=True)
            subprocess.run(["pkill", "mplayer"], capture_output=True)
        except:
            pass
    
    def listen(self, timeout: int = 8, phrase_time_limit: int = 12) -> Optional[str]:
        """Ouve e reconhece comando de voz"""
        if not VOICE_ENABLED:
            return None
        
        try:
            with self.microphone as source:
                print("🎤 Ouvindo... (Ctrl+C para voltar)")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            print("🔍 Processando...")
            command = self.recognizer.recognize_google(audio, language='pt-BR')
            
            if len(command.strip()) > 2:
                print(f"📝 Comando: {command}")
                return command.lower()
            return None
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            self.speak("Não entendi, pode repetir?")
            return None
        except KeyboardInterrupt:
            print("\n🛑 Voltando ao modo texto")
            return "voltar"
        except Exception as e:
            print(f"❌ Erro no reconhecimento: {e}")
            return None
    
    def continuous_listen(self, callback: Callable[[str], None]):
        """Escuta contínua para modo voz ativo"""
        self.recognition_callback = callback
        print("🎤 Modo voz ativo. Fale naturalmente...")
        self.speak("Modo voz ativo. Pode falar.")
        
        while True:
            command = self.listen(timeout=10, phrase_time_limit=15)
            if command:
                if any(word in command for word in ['sair', 'parar', 'voltar', 'modo texto']):
                    self.speak("Retornando ao modo texto.")
                    break
                callback(command)
    
    def get_available_engines(self) -> List[Dict]:
        """Retorna mecanismos de voz disponíveis"""
        return [
            {"id": engine_id, "name": info["name"], "available": info["available"]}
            for engine_id, info in self.voice_engines.items()
        ]
    
    def set_voice_engine(self, engine_id: str) -> bool:
        """Altera o mecanismo de voz"""
        if engine_id in self.voice_engines and self.voice_engines[engine_id]["available"]:
            self.current_voice_engine = engine_id
            print(f"✅ Voz alterada para: {self.voice_engines[engine_id]['name']}")
            return True
        return False
    
    def test_voice(self, engine_id: str = None):
        """Testa uma voz específica"""
        test_text = "Olá, eu sou o JARVIS. Esta é uma demonstração da minha voz natural e suave."
        
        if engine_id:
            if engine_id in self.voice_engines and self.voice_engines[engine_id]["available"]:
                old_engine = self.current_voice_engine
                self.current_voice_engine = engine_id
                self._speak_sync(test_text)
                self.current_voice_engine = old_engine
            else:
                print(f"❌ Voz '{engine_id}' não disponível")
        else:
            print("🔊 Testando voz atual...")
            self._speak_sync(test_text)
