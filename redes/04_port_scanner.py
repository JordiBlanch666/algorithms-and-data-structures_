"""
Port Scanner — discovering which services are running on a host.

A port is a numbered endpoint (0–65535) that lets one machine run
multiple network services simultaneously. Think of the IP address as
the building address and the port as the apartment number.

Well-known ports:
  21   → FTP (file transfer)
  22   → SSH (secure shell)
  25   → SMTP (email sending)
  53   → DNS (name resolution)
  80   → HTTP (web, unencrypted)
  443  → HTTPS (web, encrypted)
  3306 → MySQL
  5432 → PostgreSQL

A port scanner tries to connect to each port. If the connection succeeds,
the port is OPEN — a service is listening there. If it's refused or times
out, the port is CLOSED or filtered by a firewall.

IMPORTANT: Only scan hosts you own or have explicit permission to test.
Scanning someone else's server without authorization is illegal in most
countries. This script defaults to localhost (127.0.0.1) for that reason.
"""

import socket
import concurrent.futures
from datetime import datetime


# Well-known ports and the services they're associated with.
# This is our local lookup table — no external library needed.
KNOWN_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
    443: "HTTPS", 445: "SMB", 3306: "MySQL",
    5432: "PostgreSQL", 6379: "Redis", 8080: "HTTP-alt",
    8443: "HTTPS-alt", 27017: "MongoDB",
}


def scan_port(host: str, port: int, timeout: float = 0.5) -> bool:
    """
    Try to open a TCP connection to host:port.
    Returns True if the port is open, False otherwise.

    We use a short timeout (0.5s) so closed/filtered ports fail fast
    instead of making us wait the OS default (which can be 20+ seconds).
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        # connect_ex returns 0 on success, an error code otherwise.
        # Unlike connect(), it doesn't raise an exception on failure —
        # which is exactly what we want when probing many ports.
        result = s.connect_ex((host, port))
        return result == 0


def scan_range(host: str, start: int, end: int,
               max_workers: int = 100) -> list[int]:
    """
    Scan a range of ports concurrently using a thread pool.

    Sequential scanning is simple but slow — if each port takes 0.5s to
    time out, scanning 1000 ports would take ~8 minutes. With 100 threads
    running in parallel, that drops to under 5 seconds.

    ThreadPoolExecutor manages the thread lifecycle for us — we just hand
    it tasks and collect results.
    """
    open_ports: list[int] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all scan tasks at once. Each returns a Future.
        futures = {
            executor.submit(scan_port, host, port): port
            for port in range(start, end + 1)
        }

        for future in concurrent.futures.as_completed(futures):
            port = futures[future]
            if future.result():
                open_ports.append(port)

    return sorted(open_ports)


def print_report(host: str, open_ports: list[int], elapsed: float) -> None:
    if not open_ports:
        print(f"  No open ports found on {host}.")
        return

    print(f"  {'Port':<8} {'Service':<15} Status")
    print("  " + "-" * 35)
    for port in open_ports:
        service = KNOWN_SERVICES.get(port, "unknown")
        print(f"  {port:<8} {service:<15} OPEN")

    print(f"\n  {len(open_ports)} open port(s) found in {elapsed:.2f}s")


if __name__ == "__main__":
    TARGET = "127.0.0.1"   # localhost only — safe to scan your own machine
    START_PORT = 1
    END_PORT = 1024        # well-known ports range

    print("══ Port Scanner ════════════════════════════════════")
    print(f"  Target: {TARGET}  |  Range: {START_PORT}–{END_PORT}\n")

    start_time = datetime.now()
    open_ports = scan_range(TARGET, START_PORT, END_PORT)
    elapsed = (datetime.now() - start_time).total_seconds()

    print_report(TARGET, open_ports, elapsed)
