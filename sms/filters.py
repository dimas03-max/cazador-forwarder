def _norm(v):
    return str(v or "").strip().lower()

def allowed(sms, cfg):
    number = _norm(sms.get("number") or sms.get("address"))
    body = _norm(sms.get("body"))

    if cfg.blocked_numbers and any(_norm(x) in number for x in cfg.blocked_numbers):
        return False, "blocked number"

    if cfg.allowed_numbers and not any(_norm(x) in number for x in cfg.allowed_numbers):
        return False, "not in allowed numbers"

    if cfg.block_keywords and any(_norm(x) in body for x in cfg.block_keywords):
        return False, "blocked keyword"

    if cfg.keywords and not any(_norm(x) in body for x in cfg.keywords):
        return False, "keyword not matched"

    return True, ""
