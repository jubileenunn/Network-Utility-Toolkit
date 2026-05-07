from rich import print

try:
    import dns.resolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False


def dns_lookup(hostname, record_type="A"):
    if not HAS_DNS:
        raise RuntimeError("dnspython is required (pip install dnspython)")

    resolver = dns.resolver.Resolver()
    answers = resolver.resolve(hostname, record_type)
    return [r.to_text() for r in answers]
