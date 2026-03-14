# system_stats.py

import psutil
import platform
import sys
import subprocess
import os


class SystemStats:
    def __init__(self):
        self.cpu_history = []
        self.ram_history = []
        self.gpu_history = []
        self.net_up_history = []
        self.net_down_history = []
        self.last_net_io = None
        self.gpu_available = self._check_gpu_availability()
        self.platform = sys.platform

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
        except Exception:
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

    def get_cpu_model(self):
        """Return a human-readable CPU model name if possible."""
        try:
            if self.platform.startswith('linux'):
                cpuinfo_path = '/proc/cpuinfo'
                if os.path.exists(cpuinfo_path):
                    with open(cpuinfo_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if 'model name' in line:
                                return line.split(':', 1)[1].strip()
            elif self.platform.startswith('win'):
                # Use WMIC on Windows to get CPU name
                try:
                    output = subprocess.check_output(
                        ['wmic', 'cpu', 'get', 'Name'],
                        text=True,
                        stderr=subprocess.DEVNULL,
                    )
                    lines = [l.strip() for l in output.splitlines() if l.strip()]
                    if len(lines) >= 2:
                        # First line is the header "Name", rest are values
                        return lines[1]
                except Exception:
                    pass
            name = platform.processor()
            if not name:
                name = platform.uname().processor
            return name or "Unknown CPU"
        except Exception:
            return "Unknown CPU"

    def get_gpu_info(self):
        """Return load and primary GPU name (if available)."""
        if not self.gpu_available:
            return 0, "No GPU"

        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return gpu.load * 100, gpu.name
        except Exception:
            pass

        return 0, "No GPU"

    def get_dual_gpu_info(self):
        """
        Return (integrated_load, integrated_name, primary_load, primary_name).
        Best-effort classification based on GPU names.
        """
        if not self.gpu_available:
            return 0, "No GPU", 0, "No GPU"

        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if not gpus:
                return 0, "No GPU", 0, "No GPU"

            integrated_gpu = None
            primary_gpu = None

            for gpu in gpus:
                name_lower = gpu.name.lower() if gpu.name else ""
                if any(vendor in name_lower for vendor in ["intel", "apu", "vega"]) and integrated_gpu is None:
                    integrated_gpu = gpu
                elif any(vendor in name_lower for vendor in ["nvidia", "geforce", "rtx", "gtx", "amd", "radeon"]):
                    # Prefer this as primary GPU
                    if primary_gpu is None:
                        primary_gpu = gpu

            # Fallbacks if classification failed
            if primary_gpu is None and gpus:
                primary_gpu = gpus[0]
            if integrated_gpu is None and len(gpus) >= 2:
                # Use a second GPU as integrated if we have one, even if we couldn't classify
                candidate = gpus[1]
                if candidate is not primary_gpu:
                    integrated_gpu = candidate

            integrated_load = integrated_gpu.load * 100 if integrated_gpu else 0
            primary_load = primary_gpu.load * 100 if primary_gpu else 0

            integrated_name = integrated_gpu.name if integrated_gpu else "No integrated GPU"
            primary_name = primary_gpu.name if primary_gpu else "No primary GPU"

            return integrated_load, integrated_name, primary_load, primary_name
        except Exception:
            return 0, "No GPU", 0, "No GPU"

    def get_gpu_names(self):
        """Return a list of all detected GPU names."""
        if not self.gpu_available:
            return []

        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                return [gpu.name for gpu in gpus]
        except Exception:
            pass

        return []

    def get_disk_info(self):
        disk = psutil.disk_usage('/')
        percent = disk.percent
        return percent

    def get_ram_hardware_info(self):
        """
        Best-effort RAM hardware information.
        Returns (ram_type, ram_model).
        """
        if self.platform.startswith('linux'):
            try:
                output = subprocess.check_output(
                    ['dmidecode', '-t', 'memory'],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                ram_type = None
                ram_model = None
                for line in output.splitlines():
                    line = line.strip()
                    if line.startswith('Type:') and ram_type is None:
                        value = line.split(':', 1)[1].strip()
                        if value and value.lower() != 'unknown':
                            ram_type = value
                    elif (
                        (line.startswith('Part Number:') or line.startswith('Manufacturer:'))
                        and ram_model is None
                    ):
                        value = line.split(':', 1)[1].strip()
                        if value and value.lower() != 'unknown':
                            ram_model = value
                    if ram_type and ram_model:
                        break
                return ram_type or "Unknown RAM type", ram_model or "Unknown RAM model"
            except Exception:
                return "Unknown RAM type", "Unknown RAM model"

        if self.platform.startswith('win'):
            try:
                # Query physical memory modules via WMIC
                output = subprocess.check_output(
                    ['wmic', 'memorychip', 'get', 'MemoryType,Manufacturer,PartNumber'],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                lines = [l.strip() for l in output.splitlines() if l.strip()]
                if len(lines) <= 1:
                    return "Unknown RAM type", "Unknown RAM model"

                # Map numeric MemoryType to a friendly name (simplified)
                type_map = {
                    '20': 'DDR',
                    '21': 'DDR2',
                    '24': 'DDR3',
                    '26': 'DDR4',
                    '34': 'DDR5',
                }
                ram_type = None
                ram_model = None
                for line in lines[1:]:
                    parts = line.split()
                    if not parts:
                        continue
                    mem_type_code = parts[0]
                    ram_type = type_map.get(mem_type_code, "Unknown RAM type")
                    # Remaining parts may contain manufacturer and part number
                    if len(parts) > 1:
                        ram_model = " ".join(parts[1:]).strip()
                    if ram_model:
                        break

                return ram_type or "Unknown RAM type", ram_model or "Unknown RAM model"
            except Exception:
                return "Unknown RAM type", "Unknown RAM model"

        return "Unknown RAM type", "Unknown RAM model"

    def get_disk_hardware_info(self):
        """
        Best-effort disk hardware information for the root filesystem.
        Returns (disk_type, disk_model).
        """
        if self.platform.startswith('linux'):
            try:
                partitions = psutil.disk_partitions()
                if not partitions:
                    return "Unknown disk type", "Unknown disk model"

                root_device = partitions[0].device  # e.g. /dev/sda1 or /dev/nvme0n1p2
                base = os.path.basename(root_device)
                # Strip common partition suffixes to get the base device name
                base = base.rstrip('0123456789')
                if base.endswith('p'):
                    base = base[:-1]

                output = subprocess.check_output(
                    ['lsblk', '-d', '-o', 'NAME,ROTA,MODEL'],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                lines = output.splitlines()
                if len(lines) <= 1:
                    return "Unknown disk type", "Unknown disk model"

                disk_type = None
                disk_model = None
                for line in lines[1:]:
                    parts = line.split(None, 2)
                    if len(parts) < 2:
                        continue
                    name = parts[0]
                    rota = parts[1]
                    model = parts[2].strip() if len(parts) >= 3 else ""
                    if name == base:
                        disk_type = "HDD" if rota == "1" else "SSD"
                        disk_model = model or "Unknown disk model"
                        break

                return disk_type or "Unknown disk type", disk_model or "Unknown disk model"
            except Exception:
                return "Unknown disk type", "Unknown disk model"

        if self.platform.startswith('win'):
            try:
                output = subprocess.check_output(
                    ['wmic', 'diskdrive', 'get', 'Model,MediaType'],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                lines = [l.strip() for l in output.splitlines() if l.strip()]
                if len(lines) <= 1:
                    return "Unknown disk type", "Unknown disk model"

                # Skip header, take the first non-empty disk line
                for line in lines[1:]:
                    if not line:
                        continue
                    # WMIC output may have variable spacing; last token(s) are model
                    parts = line.split()
                    if not parts:
                        continue
                    media_info = line.lower()
                    if 'ssd' in media_info or 'solid state' in media_info:
                        disk_type = 'SSD'
                    elif 'hdd' in media_info or 'hard disk' in media_info:
                        disk_type = 'HDD'
                    else:
                        disk_type = 'Unknown disk type'

                    # Model string: everything after the first token
                    if len(parts) > 1:
                        disk_model = " ".join(parts[1:]).strip()
                    else:
                        disk_model = line.strip()

                    return disk_type, disk_model or "Unknown disk model"

                return "Unknown disk type", "Unknown disk model"
            except Exception:
                return "Unknown disk type", "Unknown disk model"

        return "Unknown disk type", "Unknown disk model"

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
