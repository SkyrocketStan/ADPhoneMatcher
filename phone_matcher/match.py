from typing import Dict, List, Tuple

from .utils import log_verbose


def match_phones(
    phones: List[Tuple[str, str]],
    ad_data: Dict[str, List[Tuple[str, str, str]]]
) -> List[Tuple[str, str, str, str]]:
    """Сопоставляет номера с данными AD.

    Args:
        phones: Список (номер, имя_файла).
        ad_data: Словарь {номер: [(ФИО, email, Enabled), ...]}.

    Returns:
        Список (номер, ФИО, email, Активный), где ненайденные — ",,,".
    """
    matches = []
    multiple_records = {phone: len(records) for phone, records in ad_data.items() if len(records) > 1}
    if multiple_records:
        num_duplicates = len(multiple_records)
        max_records = max(multiple_records.values())
        examples = ", ".join(f"{phone}: {count}" for phone, count in list(multiple_records.items())[:3])
        log_verbose(f"Найдено {num_duplicates} номеров с множественными записями в AD, максимум {max_records} записей, примеры: {examples}")

    for phone, source_file in phones:
        if phone in ad_data:
            for display_name, email, enabled in ad_data[phone]:
                matches.append((phone, display_name, email, enabled))
                log_verbose(f"Добавлен номер {phone} с данными ({display_name}, {email}, {enabled})")
        else:
            matches.append((phone, "", "", ""))
            log_verbose(f"Номер {phone} из {source_file} не найден в AD")
    return matches
