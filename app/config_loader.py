import yaml
from env_override import apply_env_overrides

_cached = None
_mtime = 0

def load_config(path):
    global _cached, _mtime
    stat = path.stat().st_mtime

    if stat != _mtime:
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        _validate(config)
        _cached = apply_env_overrides(config)
        _mtime = stat

    return _cached

def _validate(config):
    tg = config.get("telegram")
    if not tg:
        raise ValueError("telegram section missing")

    if not isinstance(tg.get("destination_chat_ids"), list):
        raise ValueError("destination_chat_ids must be list")
