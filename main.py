import psycopg2

from serviceWhoIs import get_whois

try:
    connection = psycopg2.connect(
        host = "95.213.151.56",
        user = "ruslan",
        password = "phanuB2E",
        database = "tg_bot"
    )

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM public."Domains" ORDER BY id ASC ')
        domains = cursor.fetchall()
        for domain_info in domains:

            domain_id = domain_info[0]
            domain = domain_info[2]
            registrar = None
            creation_date = None
            expiration_date = None

            whois_info = get_whois(domain)
            registrar = whois_info["registrar"]
            if whois_info["creation_date"]:
                creation_date = whois_info["creation_date"].date()
            if whois_info["expiration_date"]:
                expiration_date = whois_info["expiration_date"].date()

            default_value = 'default'
            cursor.execute("""
                    SELECT id FROM public."Checks" 
                    WHERE domain = %s
                    AND COALESCE(registrar, %s) = %s
                    AND COALESCE(creation_date, '1000-10-10') = %s
                    AND COALESCE(expiration_date, '1000-10-10') = %s;
                """, (domain_id, default_value, registrar or default_value,
                      creation_date or '1000-10-10', expiration_date or '1000-10-10'))

            if not cursor.fetchone():
                cursor.execute("INSERT INTO public.\"Checks\" (date, domain, registrar, creation_date, expiration_date) VALUES (NOW(), %s, %s, %s, %s);", (domain_id, registrar, creation_date, expiration_date))
                connection.commit()

except Exception as ex:
    print("Err: ", ex)

finally:
    if connection:
        connection.close()