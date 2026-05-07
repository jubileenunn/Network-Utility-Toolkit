#!/usr/bin/env python3
"""
Network Utility Toolkit (single file)

This toolkit bundles several essential network diagnostic tools into one
clean, easy-to-use command-line interface.

Included tools:
- Ping sweep (CIDR)
- Port scanner
- DNS lookup
- Traceroute

Enhancements:
- JSON output mode
- Colored terminal output (Rich)
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

def _ping_host(host: str, timeout: int = 1000, verbose: bool = False) -> bool:
    """Send a single ping to a host and return True if it responds."""
    system = platform.system().lower()

    cmd = (
        ["ping", "-n", "1", "-w", str(timeout), host]
        if system == "windows"
        else ["ping", "-c", "1", "-W", str(max(1, timeout // 1000)), host]
    )

    if verbose:
        print(f"[cyan]Pinging {host}[/cyan]")

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def ping_sweep(cidr: str, max_workers: int = 100, verbose=False, quiet=False):
    """Ping every host in a CIDR block and return a list of responsive IPs."""
    network = ipaddress.ip_network(cidr, strict=False)
    hosts = [str(h) for h in network.hosts()]
    alive_hosts = []

    with Progress() as progress:
        task = progress.add_task("[green]Scanning hosts...", total=len(hosts))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_ping_host, h, verbose): h for h in hosts}

            for future in as_completed(futures):
                host = futures[future]
                if future.result():
                    alive_hosts.append(host)
                    if not quiet:
                        print(f"[green]+[/green] {host}")
                progress.update(task, advance=1)

    return alive_hosts


# ------------------------------------------------------------
# Port Scanner
# ------------------------------------------------------------

def _scan_port(host: str, port: int, timeout: float = 1.0, verbose=False) -> bool:
    """Attempt to connect to a TCP port; return True if open."""
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
    """Scan a range of ports on a host and return a sorted list of open ports."""
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
    """Perform a DNS lookup for a given record type."""
    if not HAS_DNSPYTHON:
        raise RuntimeError("dnspython is required (pip install dnspython)")

    resolver = dns.resolver.Resolver()
    answers = resolver.resolve(hostname, record_type)
    return [r.to_text() for r in answers]


# ------------------------------------------------------------
# Traceroute
# ------------------------------------------------------------

def traceroute(target: str, max_hops: int = 30):
    """Run system traceroute/tracert and return the raw output."""
    system = platform.system().lower()

    cmd = (
        ["tracert", "-h", str(max_hops), target]
        if system == "windows"
        else ["traceroute", "-m", str(max_hops), target]
    )

    try:
