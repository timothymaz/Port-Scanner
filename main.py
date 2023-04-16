import socket
import ipaddress
from contextlib import closing
import concurrent.futures
from tkinter import *
from tkinter import messagebox

def scan_port(ip, port, timeout=3):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout)
        result = sock.connect_ex((str(ip), port))
        return result == 0

def check_ip_ports(ip, ports):
    results = []
    for port in ports:
        is_port_open = scan_port(ip, port)
        if is_port_open:
            results.append(f"Port {port} is open on {ip}")
        else:
            results.append(f"Port {port} is closed on {ip}")
    return results

def start_scan():
    start_ip = start_ip_entry.get()
    end_ip = end_ip_entry.get()
    ports = list(map(int, ports_entry.get().split(',')))

    start_ip = ipaddress.IPv4Address(start_ip.strip())
    end_ip = ipaddress.IPv4Address(end_ip.strip())

    ips = [ipaddress.IPv4Address(ip_int) for ip_int in range(int(start_ip), int(end_ip) + 1)]
    max_workers = int(max_workers_entry.get())

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = []
        for ip in ips:
            ip_results = list(executor.map(lambda port: check_ip_ports(ip, [port]), ports))
            results.extend([result[0] for result in ip_results])

    output_text.delete(1.0, END)
    for result in results:
        output_text.insert(INSERT, result + "\n")

app = Tk()
app.title("Port Scanner")

Label(app, text="Start IP:").grid(row=0, column=0, sticky=W)
start_ip_entry = Entry(app, width=20)
start_ip_entry.grid(row=0, column=1)

Label(app, text="End IP:").grid(row=1, column=0, sticky=W)
end_ip_entry = Entry(app, width=20)
end_ip_entry.grid(row=1, column=1)

Label(app, text="Ports (comma separated):").grid(row=2, column=0, sticky=W)
ports_entry = Entry(app, width=20)
ports_entry.grid(row=2, column=1)

Label(app, text="Max Threads:").grid(row=3, column=0, sticky=W)
max_workers_entry = Entry(app, width=20)
max_workers_entry.grid(row=3, column=1)

Button(app, text="Start Scan", command=start_scan).grid(row=4, column=0, columnspan=2)

output_text = Text(app, wrap=WORD, width=40, height=20)
output_text.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

app.mainloop()
