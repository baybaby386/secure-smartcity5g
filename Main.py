# File: main.py

import socket
import platform
import psutil
import json
import subprocess
import threading

def handler(request):
    def get_device_info():
        return {
            "Hostname": socket.gethostname(),
            "IP Address": socket.gethostbyname(socket.gethostname()),
            "OS": platform.system(),
            "OS Version": platform.version(),
            "CPU": platform.processor(),
            "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"
        }

    def check_open_ports():
        open_ports = []
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 3306, 3389, 8080, 8443]
        target_ip = socket.gethostbyname(socket.gethostname())

        def scan_port(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.02)
                    if sock.connect_ex((target_ip, port)) == 0:
                        open_ports.append(port)
            except:
                pass

        threads = []
        for port in common_ports:
            thread = threading.Thread(target=scan_port, args=(port,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return open_ports

    def scan_network():
        devices = set()
        try:
            output = subprocess.check_output("arp -a", shell=True).decode()
            for line in output.splitlines():
                if '-' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        ip = parts[0]
                        if ip != socket.gethostbyname(socket.gethostname()):
                            devices.add(ip)
        except Exception as e:
            return {"error": str(e)}
        return list(devices)

    # Process request
    action = request["query_params"].get("action", "info")

    if action == "info":
        return json.dumps(get_device_info())
    elif action == "ports":
        return json.dumps({"open_ports": check_open_ports()})
    elif action == "devices":
        return json.dumps({"devices": scan_network()})
    else:
        return json.dumps({"error": "Invalid action. Use 'info', 'ports', or 'devices'."})
