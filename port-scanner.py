#!/usr/bin/env python3

import socket
from termcolor import colored
import threading
import ipaddress
import nmap
import time
import sys

def validate_ip(ip_str):
    """Validate the IP address"""
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def scan_port(host, port, open_ports, nm):
    """Scan a single port on the host"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)  # Set timeout for the socket
            result = sock.connect_ex((host, port))
            if result == 0:
                if port not in open_ports:
                    open_ports.add(port)
                    print(colored(f"[+] Port {port} open", "magenta"))

                    nm.scan(host, str(port), '-sV --version-intensity 9 --version-all')
                    if port in nm[host]['tcp']:
                        service = nm[host]['tcp'][port]['name']
                        version = nm[host]['tcp'][port]['version']
                        product = nm[host]['tcp'][port]['product']
                        extra_info = nm[host]['tcp'][port].get('extrainfo', '')

                        print(colored(f"    Port: {port}", "yellow"))
                        print(colored(f"    Service: {service}", "grey"))
                        print(colored(f"    Version: {version}", "grey"))
                        print(colored(f"    Product: {product}", "grey"))
                        if extra_info:
                            print(colored(f"    Extra Info: {extra_info}", "grey"))

                # Send an HTTP request to common web server ports
                if port in [80, 443, 8080, 5426]:
                    message = 'GET / HTTP/1.1\r\nHost: {}\r\nUser-Agent: port-scanner\r\nConnection: close\r\n\r\n'.format(host)
                    sock.sendall(message.encode())  

                    chunks = []
                    while True:
                        chunk = sock.recv(8192)  # Receive data in chunks
                        if not chunk:
                            break
                        chunks.append(chunk)
                    data = b''.join(chunks)  # Combine the chunks into a single response

                    print(colored(f"Received from port {port}: {data}", "grey"))

    except socket.timeout:
        sys.stdout.write("\n")
        print(colored(f"Socket timeout on port {port}", "yellow"))
    except socket.error as err:
        print(colored(f"Socket error on port {port}: {err}", "yellow"))
    except Exception as e:
        print(colored(f"Error scanning port {port} on {host}: {e}", "red"))
    finally:
        pass

def main():
    host = input(colored("[*] Enter the IP address to scan: ", "yellow"))

    if not validate_ip(host):
        print(colored("[!] Invalid IP address", "red"))
        return

    nm = nmap.PortScanner()
    open_ports = set()

    # List of common ports to scan
    common_ports = [21, 22, 23, 25, 53, 80, 101, 110, 111, 123, 135, 136, 137, 138, 139, 143, 161, 179, 194, 389, 443, 444, 445, 465, 513, 514, 548, 546, 547, 587, 591, 631, 636, 646, 787, 808, 853, 873, 902, 993, 990, 995, 1194, 1433, 1521, 1701, 1723, 1812, 1813, 2049, 2082, 2083, 2086, 2087, 2095, 2096, 2100, 3074, 3306, 3389, 4662, 4672, 5000, 5060, 5061, 5222, 5400, 5432, 5500, 5700, 5800, 5900, 5938, 6881, 6969, 8080, 8081, 8443, 10000, 32768, 49152, 49153, 49154, 49155, 49156, 49157, 49158, 49159, 49160, 49161, 49163, 49165, 49167, 49175, 49176, 49400, 51400, 6660, 6661, 6662, 6663, 6664, 6665, 6666, 6667, 6668, 6669]

    threads = [threading.Thread(target=scan_port, args=(host, port, open_ports, nm)) for port in common_ports]

    for thread in threads:
        thread.start()

    # Periodically print a progress message in the same line
    while any(thread.is_alive() for thread in threads):
        for i in range(4):
            sys.stdout.write(colored("\r[*] Still scanning" + "." * i, "blue"))
            sys.stdout.flush()
            time.sleep(1)  # Adjust the interval as needed


    for thread in threads:
        thread.join()

    print(colored("\r[*] Scan complete.", "blue"))  

main()









