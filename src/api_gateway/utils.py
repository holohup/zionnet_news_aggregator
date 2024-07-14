def obfuscate_password(pwd: str) -> str:
    """Obfuscates passwords so that they do not get exposed in logs."""

    return '*' * len(pwd)
