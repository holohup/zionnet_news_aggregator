import json


def parse_data(data: str) -> dict:
    return json.loads(data)
