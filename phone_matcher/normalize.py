from typing import Optional
from . import config

def normalize_phone(phone: str, is_ad: bool = False) -> Optional[str]:
    """Нормализует номер телефона, оставляя только цифры.

    Args:
        phone: Входной номер телефона (строка).
        is_ad: Если True, обрабатывается номер из AD (все цифры сохраняются).

    Returns:
        Строку с цифрами или None, если номер некорректен.
    """
    if not phone:
        return None
    cleaned = phone.strip()
    digits = ''.join(c for c in cleaned if c.isdigit())
    return digits if digits else None
    