import geoacumen
import maxminddb
from flask import current_app

IP_ADDR_LOOKUP = maxminddb.open_database(
    current_app.config.get("GEOIP_DATABASE_PATH", geoacumen.db_path)
)


def lookup_ip_address(addr):
    response = IP_ADDR_LOOKUP.get(addr)
    try:
        return response["country"]["iso_code"]
    except KeyError:
        return None

def lookup_ip_address2(addr):
    response = IP_ADDR_LOOKUP.get(addr)
    try:
        return response["school"]["iso_code"]
    except KeyError:
        return None
