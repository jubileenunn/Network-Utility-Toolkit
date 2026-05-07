import platform
import subprocess


def traceroute(target, max_hops=30):
    system = platform.system().lower()

    cmd = (
        ["tracert", "-h", str(max_hops), target]
        if system == "windows"
        else ["traceroute", "-m", str(max_hops), target]
    )

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except FileNotFoundError:
        return "Error: traceroute command not found."
