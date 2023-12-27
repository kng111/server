import psutil

cpu_info = psutil.cpu_info()
print(f"Processor: {cpu_info[0].model}")
