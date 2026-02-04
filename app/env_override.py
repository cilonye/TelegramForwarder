import os

def apply_env_overrides(config):
    tg = config.setdefault("telegram", {})

    if "TF_SOURCE_CHAT_ID" in os.environ:
        tg["source_chat_id"] = int(os.environ["TF_SOURCE_CHAT_ID"])

    if "TF_DESTINATION_CHAT_IDS" in os.environ:
        tg["destination_chat_ids"] = [
            int(x) for x in os.environ["TF_DESTINATION_CHAT_IDS"].split(",")
        ]

    if "TF_KEYWORDS" in os.environ:
        tg["keywords"] = [x.lower() for x in os.environ["TF_KEYWORDS"].split(",")]

    if os.environ.get("TF_DISABLE_KEYWORDS", "").lower() == "true":
        tg["keywords"] = []

    return config
