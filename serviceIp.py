import socket


def get_ip(domain):
    ip_info = socket.gethostbyname(domain)
    return ip_info