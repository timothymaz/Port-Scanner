import socket
import ipaddress
from contextlib import closing
import concurrent.futures
import threading
from tkinter import *
from tkinter import ttk, messagebox


def scan_port(ip, port, timeout=3):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout)
        result = sock.connect_ex((str(ip), port))
        return result == 0


def check_ip_ports(ip, ports, resolve_hostname):
    results = []
    hostname = ""
    if resolve_hostname:
        try:
            hostname, _, _ = socket.gethostbyaddr(str(ip))
            hostname = f"{hostname} - "
        except socket.herror:
            hostname = ""
    for port in ports:
        is_port_open = scan_port(ip, port)
        status = "open" if is_port_open else "closed"
        log_message = f"Scanning {hostname}{ip}:{port} - {status}"
        add_live_log(log_message)
        result = f"Port {port} is open on {hostname}{ip}" if is_port_open else f"Port {port} is closed on {hostname}{ip}"
        results.append(result)
    return results


def add_live_log(message):
    live_log_text.insert(INSERT, message + "\n")
    live_log_text.see("end")


def update_progressbar(value):
    progress_bar["value"] = value
    app.update_idletasks()


def scan_ips():
    start_ip = ".".join([start_ip_entry1.get(), start_ip_entry2.get(), start_ip_entry3.get(), start_ip_entry4.get()])
    end_ip = ".".join([end_ip_entry1.get(), end_ip_entry2.get(), end_ip_entry3.get(), end_ip_entry4.get()])
    ports = list(map(int, ports_entry.get().split(',')))

    start_ip = ipaddress.IPv4Address(start_ip.strip())
    end_ip = ipaddress.IPv4Address(end_ip.strip())

    ips = [ipaddress.IPv4Address(ip_int) for ip_int in range(int(start_ip), int(end_ip) + 1)]
    max_workers = int(max_workers_entry.get())
    resolve_hostname = resolve_hostname_var.get()
    
    total_tasks = len(ips) * len(ports)
    progress_bar["maximum"] = total_tasks
    completed_tasks = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = []
        for ip in ips:
            ip_results = list(executor.map(lambda port: check_ip_ports(ip, [port], resolve_hostname), ports))
            results.extend([result[0] for result in ip_results])
            completed_tasks += len(ports)
            update_progressbar(completed_tasks)

    output_text.delete(1.0, END)
    for result in results:
        output_text.insert(INSERT, result + "\n")
    update_progressbar(0)  # Reset progress bar after scan
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = []
        for ip in ips:
            ip_results = list(executor.map(lambda port: check_ip_ports(ip, [port], resolve_hostname), ports))
            results.extend([result[0] for result in ip_results])


    output_text.delete(1.0, END)
    for result in results:
        output_text.insert(INSERT, result + "\n")


    
def is_valid_ip(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False
    
def is_valid_ports(ports):
    for port in ports:
        if not (0 <= port <= 65535):
            return False
    return True

def is_valid_threads(threads):
    return 0 < threads <= 100
def start_scan():
    start_ip = ".".join([start_ip_entry1.get(), start_ip_entry2.get(), start_ip_entry3.get(), start_ip_entry4.get()])
    end_ip = ".".join([end_ip_entry1.get(), end_ip_entry2.get(), end_ip_entry3.get(), end_ip_entry4.get()])

    if not is_valid_ip(start_ip) or not is_valid_ip(end_ip):
        messagebox.showerror("Error", "Invalid IP address.")
        return

    try:
        ports = list(map(int, ports_entry.get().split(',')))
    except ValueError:
        messagebox.showerror("Error", "Invalid ports. Please enter comma-separated integers.")
        return

    if not is_valid_ports(ports):
        messagebox.showerror("Error", "Invalid ports. Ports must be between 0 and 65535.")
        return

    try:
        max_workers = int(max_workers_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Invalid number of threads. Please enter an integer.")
        return

    if not is_valid_threads(max_workers):
        messagebox.showerror("Error", "Invalid number of threads. Threads must be between 1 and 100.")
        return

    scanning_thread = threading.Thread(target=scan_ips)
    scanning_thread.start()
    
app = Tk()
app.title("Port Scanner")

Label(app, text="Start IP:").grid(row=0, column=0, sticky=W)
start_ip_entry1 = Entry(app, width=4)
start_ip_entry1.grid(row=0, column=1)
Label(app, text=".").grid(row=0, column=2)
start_ip_entry2 = Entry(app, width=4)
start_ip_entry2.grid(row=0, column=3)
Label(app, text=".").grid(row=0, column=4)
start_ip_entry3 = Entry(app, width=4)
start_ip_entry3.grid(row=0, column=5)
Label(app, text=".").grid(row=0, column=6)
start_ip_entry4 = Entry(app, width=4)
start_ip_entry4.grid(row=0, column=7)

Label(app, text="End IP:").grid(row=1, column=0, sticky=W)
end_ip_entry1 = Entry(app, width=4)
end_ip_entry1.grid(row=1, column=1)
Label(app, text=".").grid(row=1, column=2)
end_ip_entry2 = Entry(app, width=4)
end_ip_entry2.grid(row=1, column=3)
Label(app, text=".").grid(row=1, column=4)
end_ip_entry3 = Entry(app, width=4)
end_ip_entry3.grid(row=1, column=5)
Label(app, text=".").grid(row=1, column=6)
end_ip_entry4 = Entry(app, width=4)
end_ip_entry4.grid(row=1, column=7)

Label(app, text="Ports (comma separated):").grid(row=2, column=0, sticky=W)
ports_entry = Entry(app, width=20)
ports_entry.grid(row=2, column=1, columnspan=7)

Label(app, text="Max Threads:").grid(row=3, column=0, sticky=W)
max_workers_entry = Entry(app, width=20)
max_workers_entry.grid(row=3, column=1, columnspan=7)

resolve_hostname_var = BooleanVar()
resolve_hostname_checkbutton = Checkbutton(app, text="Hostname Resolution", variable=resolve_hostname_var)
resolve_hostname_checkbutton.grid(row=4, column=1, columnspan=3, sticky=W)

Button(app, text="Start Scan", command=start_scan).grid(row=4, column=4, columnspan=4)

output_text = Text(app, wrap=WORD, width=60, height=20)
output_text.grid(row=5, column=0, columnspan=8, padx=10, pady=10)

# Add the progress bar and live log text box
progress_bar = ttk.Progressbar(app, orient=HORIZONTAL, length=300, mode="determinate")
progress_bar.grid(row=6, column=0, columnspan=8, pady=10)

Label(app, text="Live Logs:").grid(row=7, column=0, sticky=W)
live_log_text = Text(app, wrap=WORD, width=60, height=10)
live_log_text.grid(row=8, column=0, columnspan=8, padx=10, pady=10)


app.mainloop()
