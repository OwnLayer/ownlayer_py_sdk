from datetime import datetime, timezone

def now():
    return int(datetime.now(timezone.utc).timestamp() * 1000)

def get_metadata():
    return { "_source": "ownlayer_py_sdk", "_sdk_version": "0.3.0" }