import argparse
from .ping import ping_sweep
from .scan import port_scan
from .dns_lookup import dns_lookup
from .trace import traceroute
from .utils import parse_ports


def build_parser():
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

    return parser


def run():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ping-sweep":
        result = ping_sweep(args.cidr, verbose=args.verbose, quiet=args.quiet)

    elif args.command == "port-scan":
        ports = parse_ports(args.ports)
        result = port_scan(args.host, ports, verbose=args.verbose, quiet=args.quiet)

    elif args.command == "dns":
        result = dns_lookup(args.hostname, args.type)

    elif args.command == "traceroute":
        result = traceroute(args.target, args.max_hops)

    # Output formatting
    if args.json:
        import json
        print(json.dumps({"result": result}, indent=2))
    else:
        if isinstance(result, list):
            for item in result:
                print(item)
        else:
            print(result)
