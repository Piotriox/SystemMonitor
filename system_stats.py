# system_stats.py

import psutil


class SystemStats:
    def __init__(self):
        self.cpu_history = []
        self.ram_history = []
        self.gpu_history = []
        self.net_up_history = []
        self.net_down_history = []
        self.last_net_io = None
        self.gpu_available = self._check_gpu_availability()

    def _check_gpu_availability(self):
        try:
            import GPUtil
            return True
        except ImportError:
            try:
                if psutil.virtual_memory():
                    pass
            except:
                pass
            return False

    def update(self, max_history=60):
        self._update_cpu(max_history)
        self._update_ram(max_history)
        self._update_gpu(max_history)
        self._update_network(max_history)

    def _update_cpu(self, max_history):
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_history.append(cpu_percent)
        if len(self.cpu_history) > max_history:
            self.cpu_history.pop(0)

    def _update_ram(self, max_history):
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        self.ram_history.append(ram_percent)
        if len(self.ram_history) > max_history:
            self.ram_history.pop(0)

    def _update_gpu(self, max_history):
        gpu_percent = self._get_gpu_usage()
        self.gpu_history.append(gpu_percent)
        if len(self.gpu_history) > max_history:
            self.gpu_history.pop(0)

    def _get_gpu_usage(self):
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].load * 100
        except:
            pass
        return 0

    def _update_network(self, max_history):
        net_io = psutil.net_io_counters()
        if self.last_net_io is None:
            self.last_net_io = net_io
            self.net_up_history.append(0)
            self.net_down_history.append(0)
        else:
            bytes_sent_delta = net_io.bytes_sent - self.last_net_io.bytes_sent
            bytes_recv_delta = net_io.bytes_recv - self.last_net_io.bytes_recv
            
            upload_kb = bytes_sent_delta / 1024
            download_kb = bytes_recv_delta / 1024
            
            self.net_up_history.append(upload_kb)
            self.net_down_history.append(download_kb)
            
            if len(self.net_up_history) > max_history:
                self.net_up_history.pop(0)
            if len(self.net_down_history) > max_history:
                self.net_down_history.pop(0)
            
            self.last_net_io = net_io

    def get_cpu_percent(self):
        cpu_percent = psutil.cpu_percent(interval=0.1)
        return cpu_percent

    def get_ram_info(self):
        ram = psutil.virtual_memory()
        used_gb = ram.used / (1024 ** 3)
        total_gb = ram.total / (1024 ** 3)
        percent = ram.percent
        return used_gb, total_gb, percent

    def get_gpu_info(self):
        if not self.gpu_available:
            return 0, "No GPU"
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return gpu.load * 100, gpu.name
        except:
            pass
        
        return 0, "No GPU"

    def get_disk_info(self):
        disk = psutil.disk_usage('/')
        percent = disk.percent
        return percent

    def get_network_speeds(self):
        if self.net_up_history:
            upload_kb = self.net_up_history[-1]
        else:
            upload_kb = 0
        
        if self.net_down_history:
            download_kb = self.net_down_history[-1]
        else:
            download_kb = 0
        
        return upload_kb, download_kb

    def format_network_speed(self, kb_s):
        if kb_s >= 1024:
            return f"{kb_s / 1024:.2f} MB/s"
        else:
            return f"{kb_s:.2f} KB/s"
