import whois


def get_whois(domain):
    whois_info = whois.whois(domain)
    return whois_info
