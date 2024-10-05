import platform

import GPUtil
import psutil


def get_platform_info():
    return {
        "system": platform.system(),
        "node_name": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def get_cpu_info():
    return {
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "cpu_frequency": psutil.cpu_freq().current,
        "cpu_usage": psutil.cpu_percent(interval=1),
    }


def get_memory_info():
    virtual_memory = psutil.virtual_memory()
    return {
        "total_memory_gb": virtual_memory.total / (1024 ** 3),
        "available_memory_gb": virtual_memory.available / (1024 ** 3),
        "memory_usage_percentage": virtual_memory.percent
    }


def get_disk_info():
    disk_info = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "file_system_type": partition.fstype,
                "total_size_gb": usage.total / (1024 ** 3),
                "used_gb": usage.used / (1024 ** 3),
                "free_gb": usage.free / (1024 ** 3),
                "usage_percentage": usage.percent
            })
        except PermissionError:
            # Skip inaccessible partitions
            pass
    return disk_info


def get_network_info():
    net_io = psutil.net_io_counters()
    return {
        "bytes_sent_mb": net_io.bytes_sent / (1024 ** 2),
        "bytes_received_mb": net_io.bytes_recv / (1024 ** 2),
    }


def get_gpu_info():
    gpus = GPUtil.getGPUs()
    gpu_info = []
    for gpu in gpus:
        gpu_info.append({
            "gpu_id": gpu.id,
            "name": gpu.name,
            "load_percentage": gpu.load * 100,
            "free_memory_mb": gpu.memoryFree,
            "used_memory_mb": gpu.memoryUsed,
            "total_memory_mb": gpu.memoryTotal,
            "temperature_in_c": gpu.temperature,
        })
    return gpu_info


def log_system_info():
    system_info = {
        "platform_information": get_platform_info(),
        "cpu_information": get_cpu_info(),
        "memory_information": get_memory_info(),
        "disk_information": get_disk_info(),
        "network_information": get_network_info(),
        "gpu_information": get_gpu_info(),
    }

    # Print the system info in JSON format to the pod logs
    # print(json.dumps(system_info, indent=4))
    # print(system_info)
    return system_info
