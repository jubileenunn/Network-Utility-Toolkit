#!/usr/bin/env python3
"""
Network Utility Toolkit (single file)

Tools included:
- Ping sweep (CIDR)
- Port scan
- DNS lookup
- Traceroute

Examples:
    python netutil.py ping-sweep 192.168.1.0/24
    python netutil.py port-scan 192.168.1.10 --ports 1-1024
    python netutil.py dns example.com -t A
    python netutil.py traceroute 8.8.8.8
"""

import argparse
import ipaddress
import platform
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# Optional dependency: dnspython
try:
    import dns.resolver
    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False


# ------------------------------------------------------------
# Ping Sweep
# ------------------------------------------------------------

def _ping_host(host: str, timeout: int = 1000) -> bool:
    """Send a single ping to a host and return True if it responds."""
    system = platform.system().lower()

    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(timeout), host]
    else:
        cmd = ["ping", "-c", "1", "-W", str(max(1, timeout // 1000)), host]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
        return result.returncode == 0
    except Exception:
        return False


def ping_sweep(cidr: str, max_workers: int = 100):
    """Ping every host in a CIDR block and return a list of responsive IPs."""
    network = ipaddress.ip_network(cidr, strict=False)
    hosts = [str(h) for h in network.hosts()]
    alive = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_ping_host, h): h for h in hosts}
        for future in as_completed(futures):
            host = futures[future]
            if future.result():
                alive.append(host)

    return alive


# ------------------------------------------------------------
# Port Scanner
# ------------------------------------------------------------

def _scan_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """Attempt to connect to a TCP port; return True if open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False


def port_scan(host: str, ports: range, max_workers: int = 200):
    """Scan a range of ports on a host and return a sorted list of open ports."""
    open_ports = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_scan_port, host, p): p for p in ports}
        for future in as_completed(futures):
            port = futures[future]
            if future.result():
                open_ports.append(port)

    return sorted(open_ports)


# ------------------------------------------------------------
# DNS Lookup
# ------------------------------------------------------------

def dns_lookup(hostname: str, record_type: str = "A"):
    """Perform a DNS lookup for a given record type."""
    if not HAS_DNSPYTHON:
        raise RuntimeError("dnspython is required for DNS lookup (pip install dnspython)")

    try:
        resolver = dns.resolver.Resolver()
        answers = resolver.resolve(hostname, record_type)
        return [r.to_text() for r in answers]
    except Exception as e:
        raise RuntimeError(f"DNS lookup failed: {e}")


# ------------------------------------------------------------
# Traceroute
# ------------------------------------------------------------

def traceroute(target: str, max_hops: int = 30):
    """Run system traceroute/tracert and return the raw output."""
    system = platform.system().lower()

    if system == "windows":
        cmd = ["tracert", "-h", str(max_hops), target]
    else:
        cmd = ["traceroute", "-m", str(max_hops), target]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout
    except FileNotFoundError:
        return "Error: traceroute command not found on this system."


# ------------------------------------------------------------
# CLI Helpers
# ------------------------------------------------------------

def _parse_ports(spec: str):
    """Parse port input like '1-1024' or '80,443,8080' into a range."""
    ports = set()

    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            try:
                start, end = part.split("-", 1)
                ports.update(range(int(start), int(end) + 1))
            except ValueError:
                continue
        else:
            try:
                ports.add(int(part))
            except ValueError:
                continue

    if not ports:
        return range(0)

    return range(min(ports), max(ports) + 1)


# ------------------------------------------------------------
# Main CLI Entry Point
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="netutil",
        description="Network Utility Toolkit: ping sweep, port scan, DNS lookup, traceroute"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Ping sweep
    ps = subparsers.add_parser("ping-sweep", help="Ping sweep a CIDR range")
    ps.add_argument("cidr", help="CIDR block, e.g. 192.168.1.0/24")

    # Port scan
    pscan = subparsers.add_parser("port-scan", help="Scan ports on a host")
    pscan.add_argument("host", help="Target host/IP")
    pscan.add_argument("--ports", default="1-1024",
                       help="Port range, e.g. 1-1024 or 80,443,8080")

    # DNS lookup
    dns_p = subparsers.add_parser("dns", help="DNS lookup")
    dns_p.add_argument("hostname", help="Hostname to resolve")
    dns_p.add_argument("-t", "--type", default="A",
                       help="Record type (A, AAAA, MX, TXT, etc.)")

    # Traceroute
    tr = subparsers.add_parser("traceroute", help="Traceroute to target")
    tr.add_argument("target", help="Target host/IP")
    tr.add_argument("--max-hops", type=int, default=30)

    args = parser.parse_args()

    # Command routing
    if args.command == "ping-sweep":
        print(f"Ping sweep: {args.cidr}")
        alive = ping_sweep(args.cidr)
        for host in alive:
            print(f"+ {host}")
        print(f"Total alive: {len(alive)}")

    elif args.command == "port-scan":
        ports = _parse_ports(args.ports)
        print(f"Port scan: {args.host} ({len(ports)} ports)")
        open_ports = port_scan(args.host, ports)
        for p in open_ports:
            print(f"open {p}")
        print(f"Total open: {len(open_ports)}")

    elif args.command == "dns":
        print(f"DNS {args.type} for {args.hostname}")
        try:
            for record in dns_lookup(args.hostname, args.type):
                print(record)
        except RuntimeError as e:
            print(e)

    elif args.command == "traceroute":
        print(f"Traceroute to {args.target}")
        print(traceroute(args.target, args.max_hops))


if __name__ == "__main__":
    main()
