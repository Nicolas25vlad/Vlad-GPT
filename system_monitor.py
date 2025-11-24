import psutil
import platform
import subprocess
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.system_info = self.get_system_info()
    
    def get_system_info(self):
        """Coleta informações básicas do sistema"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "hostname": platform.node()
        }
    
    def get_cpu_usage(self):
        """Retorna uso da CPU"""
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self):
        """Retorna uso de memória"""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used
        }
    
    def get_disk_usage(self):
        """Retorna uso do disco"""
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
    
    def get_running_processes(self, limit=10):
        """Retorna processos em execução"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Ordena por uso de CPU e limita resultados
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        return processes[:limit]
    
    def get_system_uptime(self):
        """Retorna tempo de atividade do sistema"""
        return psutil.boot_time()
    
    def get_network_info(self):
        """Retorna informações de rede"""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }