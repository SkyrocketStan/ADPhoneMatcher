from typing import Optional


def normalize_phone(phone: str) -> Optional[str]:
    """Нормализует номер телефона, оставляя только цифры.

    Args:
        phone: Входной номер телефона (строка).

    Returns:
        Строку с цифрами или None, если номер некорректен.
    """
    if not phone:
        return None
    cleaned = phone.strip()
    digits = ''.join(c for c in cleaned if c.isdigit())
    return digits if digits else None
