import random
import string
import os

X_ACCOUNT = os.getenv("X_ACCOUNT", "")

def makeid(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def register_entity(id_map, entity):
    key = entity.get("id") or entity.get("identifier")
    if key is not None:
        id_map[key] = entity
    else:
        raise ValueError("Entity must have 'id' or 'identifier'")

def find_entity(id_map, entity_id):
    return id_map.get(entity_id)

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "x-account": X_ACCOUNT,
        "Content-Type": "application/json"
    }

def record_api_info(request, method, url, payload, response):
    request.node._api_info = {
        "method": method,
        "url": url,
        "payload": payload,
        "response": response.json() if response else None
    }


