import psutil
try:
    import pynvml
except (ImportError, Exception):
    pynvml = None
import time
import os


class HardwareDetector:
    """
    This class detects the hardware specifications of the computer and monitors them continuously.

    Contract and Specification:
    - Anchor: self.hardware_profile = {} (initialized empty in __init__, source line 18)
    - get_computer_specs() populates:
        - ram_total_gb (float, rounded to 2 decimal places): memory.total / 1024^3
        - ram_used_gb (float, rounded to 2 decimal places): memory.used / 1024^3
        - available_diskspace_gb (float, rounded to 2 decimal places): disk_usage('/').free / 1024^3
        - cpu_cores (int): psutil.cpu_count(logical=True)
        - cpu_usage_percent (float): psutil.cpu_percent()
    - Representative Example:
        Given a system with:
          RAM total = 17,179,869,184 bytes (16 GB)
          RAM used  = 8,589,934,592 bytes (8 GB)
          Disk free = 107,374,182,400 bytes (100 GB)
          CPU cores = 8
          CPU usage = 15.5%
        Resulting profile:
          {'ram_total_gb': 16.0, 'ram_used_gb': 8.0, 'available_diskspace_gb': 100.0,
           'cpu_cores': 8, 'cpu_usage_percent': 15.5}
    """

    def __init__(self):
        self.hardware_profile = {}

    def get_gpu_specs(self) -> None:
        """
        Detects the GPU specifications of the computer.
        :return: None
        """
        if pynvml is None:
            self.hardware_profile['gpu_name'] = "None available"
            self.hardware_profile['gpu_total_memory_gb'] = 0
            self.hardware_profile['gpu_used_memory_gb'] = 0
            return
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count == 0:
                self.hardware_profile['gpu_name'] = "None available"
                self.hardware_profile['gpu_total_memory_gb'] = 0
                self.hardware_profile['gpu_used_memory_gb'] = 0
                return
            gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            gpu_name = pynvml.nvmlDeviceGetName(gpu_handle)
            gpu_mem_info = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle)
            gpu_total_mem = gpu_mem_info.total / (1024 ** 3)
            gpu_used_mem = gpu_mem_info.used / (1024 ** 3)
            pynvml.nvmlShutdown()
            self.hardware_profile['gpu_name'] = gpu_name
            self.hardware_profile['gpu_total_memory_gb'] = round(gpu_total_mem, 2)
            self.hardware_profile['gpu_used_memory_gb'] = round(gpu_used_mem, 2)
        except Exception:
            self.hardware_profile['gpu_name'] = "None available"
            self.hardware_profile['gpu_total_memory_gb'] = 0
            self.hardware_profile['gpu_used_memory_gb'] = 0

    def get_computer_specs(self) -> None:
        """
        Detects the computer specifications including RAM, available disk space, and CPU cores.
        :return: None
        """
        memory = psutil.virtual_memory()
        ram_total = memory.total
        ram_used = memory.used
        available_diskspace = psutil.disk_usage('/').free / (1024 ** 3)
        cpu_cores = psutil.cpu_count(logical=True)
        cpu_usage = psutil.cpu_percent(interval=0.1)
        self.hardware_profile['ram_total_gb'] = round(ram_total / (1024 ** 3), 2)
        self.hardware_profile['ram_used_gb'] = round(ram_used / (1024 ** 3), 2)
        self.hardware_profile['available_diskspace_gb'] = round(available_diskspace, 2)
        self.hardware_profile['cpu_cores'] = cpu_cores
        self.hardware_profile['cpu_usage_percent'] = cpu_usage

    def monitor_resources(self, interval: int = 1) -> None:
        """
        Continuously monitors and displays hardware resources.
        :param interval: Time in seconds between updates.
        :return: None
        """
        try:
            while True:
                self.get_computer_specs()
                self.get_gpu_specs()
                os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console for a clean display
                print("Hardware Resource Monitor")
                print("==========================")
                for key, value in self.hardware_profile.items():
                    print(f"{key}: {value}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")


if __name__ == "__main__":
    # Run the continuous monitor
    hardware = HardwareDetector()
    hardware.monitor_resources(interval=0.5)
