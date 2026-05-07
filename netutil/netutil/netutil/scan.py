import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich import print
from rich.progress import Progress


def _scan_port(host, port, timeout=1.0, verbose=False):
    if verbose:
        print(f"[cyan]Checking port {port}[/cyan]")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except Exception:
            return False


def port_scan(host, ports, max_workers=200, verbose=False, quiet=False):
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
