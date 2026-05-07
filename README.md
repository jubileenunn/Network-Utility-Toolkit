# Network Utility Toolkit

A lightweight, extensible Python CLI toolkit for everyday network diagnostics and exploration.

This project bundles several essential tools into one clean interface:

- Ping sweep (CIDR)
- Port scanner
- DNS lookup
- Traceroute
- JSON output mode (--json)
- Colored terminal output (via Rich)
- Progress bars
- Verbose mode (`-v`)
- Quiet mode (`-q`)

---

## ✨ Features

### Ping Sweep  
Scan an entire subnet and quickly identify which hosts are alive.

### Port Scanner  
Fast, multi-threaded TCP port scanning with clean, readable output.

### DNS Lookup  
Resolve A, AAAA, MX, TXT, and other DNS record types.

### Traceroute  
Trace the network path to a target host and inspect each hop.

### JSON Output Mode  
Perfect for automation, scripting, or piping results into other tools.

### Colored Output  
Rich-powered color formatting for clarity and readability.

### Progress Bars  
Live progress indicators for long-running scans.

### Verbose & Quiet Modes  
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
