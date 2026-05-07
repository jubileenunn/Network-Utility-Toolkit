# Network Utility Toolkit

A lightweight, extensible Python CLI toolkit for common network diagnostic tasks.

Includes:
- Ping sweep (CIDR)
- Port scanner
- DNS lookup
- Traceroute
- JSON output mode (`--json`)
- Colored terminal output (via Rich)
- Progress bars
- Verbose mode (`-v`)
- Quiet mode (`-q`)

---

## 🚀 Features

### ✔ Ping Sweep  
Scan an entire subnet and identify live hosts.

### ✔ Port Scanner  
Fast multi-threaded TCP port scanning.

### ✔ DNS Lookup  
Resolve A, AAAA, MX, TXT, and other DNS records.

### ✔ Traceroute  
Trace the network path to a target host.

### ✔ JSON Output Mode  
Machine‑readable output for automation and scripting.

### ✔ Colored Output  
Readable, color‑coded results using the `rich` library.

### ✔ Progress Bars  
Live progress indicators for long-running scans.

### ✔ Verbose & Quiet Modes  
- `-v` shows detailed actions  
- `-q` suppresses non-essential output  

---

## 📦 Installation

```bash
git clone https://github.com/jubileenunn/Network-Utility-Toolkit.git
cd Network-Utility-Toolkit
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
