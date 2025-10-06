import uuid

def generate_unique_uuid():
    return str(uuid.uuid4())[:4]