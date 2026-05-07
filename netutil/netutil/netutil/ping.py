import ipaddress
import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich import print
from rich.progress import Progress


def _ping_host(host, timeout=1000, verbose=False):
    system = platform.system().lower()

    cmd = (
        ["ping", "-n", "1", "-w", str(timeout), host]
        if system == "windows"
        else ["ping", "-c", "1", "-W", str(max(1, timeout // 1000)), host]
    )

    if verbose:
        print(f"[cyan]Pinging {host}[/cyan]")

    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False


def ping_sweep(cidr, max_workers=100, verbose=False, quiet=False):
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
