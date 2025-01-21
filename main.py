import psycopg2

from serviceIp import get_ip
from serviceWhoIs import get_whois

try:
    connection = psycopg2.connect(
        host = "95.213.151.56",
        user = "ruslan",
        password = "phanuB2E",
        database = "tg_bot"
    )

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM public."Organizations" ORDER BY id ASC ')
        organizations = cursor.fetchall()
        for organization in organizations:

            id = organization[0]
            site = organization[3]
            domain = None
            registrar = None
            ip = None
            creation_date = None
            expiration_date = None

            if site:
                whois_info = get_whois(site)
                domain = whois_info["domain_name"]
                registrar = whois_info["registrar"]
                if whois_info["creation_date"]:
                    creation_date = whois_info["creation_date"].date()
                if whois_info["expiration_date"]:
                    expiration_date = whois_info["expiration_date"].date()
                if domain:
                    ip = get_ip(domain)

                default_value = 'default'
                cursor.execute("""
                    SELECT id FROM public."Checks" 
                    WHERE organization_id = %s
                    AND COALESCE(domain_name, %s) = %s
                    AND COALESCE(registrar, %s) = %s
                    AND COALESCE(ip, %s) = %s
                    AND COALESCE(creation_date, '1000-10-10') = %s
                    AND COALESCE(expiration_date, '1000-10-10') = %s;
                """, (id, default_value, domain or default_value, default_value,
                      registrar or default_value, default_value, ip or default_value,
                      creation_date or '1000-10-10', expiration_date or '1000-10-10'))

                if not cursor.fetchone():
                    cursor.execute("INSERT INTO public.\"Checks\" (organization_id, check_date, domain_name, registrar, ip, creation_date, expiration_date) VALUES (%s, NOW(), %s, %s, %s, %s, %s);", (id, domain, registrar, ip, creation_date, expiration_date))
                    connection.commit()

except Exception as ex:
    print("Err: ", ex)

finally:
    if connection:
        connection.close()