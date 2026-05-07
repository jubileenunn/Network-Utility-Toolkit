#!/usr/bin/env python3
"""
Network Utility Toolkit (single file)

Enhancements:
- JSON output mode
- Colored terminal output
- Progress bars
- Verbose mode
- Quiet mode
"""

import argparse
import ipaddress
import json
import platform
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# Rich for colors + progress bars
from rich import print
from rich.progress import Progress

# Optional dependency: dnspython
try:
    import dns.resolver
    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False


# ------------------------------------------------------------
# Ping Sweep
# ------------------------------------------------------------

def _ping_host(host: str, timeout: int = 1000, verbose=False) -> bool:
    system = platform.system().lower()

    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(timeout), host]
    else:
        cmd = ["ping", "-c", "1", "-W", str(max(1, timeout // 1000)), host]

    if verbose:
        print(f"[cyan]Pinging {host}[/cyan]")

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


def ping_sweep(cidr: str, max_workers: int = 100, verbose=False, quiet=False):
    network = ipaddress.ip_network(cidr, strict=False)
    hosts = [str(h) for h in network.hosts()]
    alive = []

    with Progress() as progress:
        task = progress.add_task("[green]Scanning hosts...", total=len(hosts))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_ping_host, h, verbose): h for h in hosts}

            for future in as_completed(futures):
                host = futures[future]
                if future.result():
                    alive.append(host)
                    if not quiet:
                        print(f"[green]+[/green] {host}")
                progress.update(task, advance=1)

    return alive


# ------------------------------------------------------------
# Port Scanner
# ------------------------------------------------------------

def _scan_port(host: str, port: int, timeout: float = 1.0, verbose=False) -> bool:
    if verbose:
        print(f"[cyan]Checking port {port}[/cyan]")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except Exception:
            return False


def port_scan(host: str, ports: range, max_workers: int = 200, verbose=False, quiet=False):
    open_ports = []

    with Progress() as progress:
        task = progress.add_task("[green]Scanning ports...", total=len(ports))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_scan_port, host, p, verbose): p for p in ports}

            for future in as_completed(futures):
                port = futures[future]
                if future.result():
                    open_ports.append(port)
                    if not quiet:
                        print(f"[green]open[/green] {port}")
                progress.update(task, advance=1)

    return sorted(open_ports)


# ------------------------------------------------------------
# DNS Lookup
# ------------------------------------------------------------

def dns_lookup(hostname: str, record_type: str = "A"):
    if not HAS_DNSPYTHON:
        raise RuntimeError("dnspython is required (pip install dnspython)")

    resolver = dns.resolver.Resolver()
    answers = resolver.resolve(hostname, record_type)
    return [r.to_text() for r in answers]


# ------------------------------------------------------------
# Traceroute
# ------------------------------------------------------------

def traceroute(target: str, max_hops: int = 30):
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
        return "Error: traceroute command not found."


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _parse_ports(spec: str):
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
# Main CLI
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="netutil",
        description="Network Utility Toolkit"
    )

    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")

    subparsers = parser.add_subparsers(dest="command", required=True)

    ps = subparsers.add_parser("ping-sweep")
    ps.add_argument("cidr")

    pscan = subparsers.add_parser("port-scan")
    pscan.add_argument("host")
    pscan.add_argument("--ports", default="1-1024")

    dns_p = subparsers.add_parser("dns")
    dns_p.add_argument("hostname")
    dns_p.add_argument("-t", "--type", default="A")

    tr = subparsers.add_parser("traceroute")
    tr.add_argument("target")
    tr.add_argument("--max-hops", type=int, default=30)

    args = parser.parse_args()

    # Routing
    if args.command == "ping-sweep":
        result = ping_sweep(args.cidr, verbose=args.verbose, quiet=args.quiet)

    elif args.command == "port-scan":
        ports = _parse_ports(args.ports)
        result = port_scan(args.host, ports, verbose=args.verbose, quiet=args.quiet)

    elif args.command == "dns":
        result = dns_lookup(args.hostname, args.type)

    elif args.command == "traceroute":
        result = traceroute(args.target, args.max_hops)

    # JSON output
    if args.json:
        print(json.dumps({"result": result}, indent=2))
    else:
        if isinstance(result, list):
            for item in result:
                print(item)
        else:
            print(result)


if __name__ == "__main__":
    main()
