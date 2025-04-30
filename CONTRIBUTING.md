# Contributing to ADPhoneMatcher

Спасибо за интерес к проекту! Вот инструкции, как внести вклад.

## Как внести изменения

1. **Форкните репозиторий**:

   ```bash
   git clone https://github.com/SkyrocketStan/ADPhoneMatcher.git
   cd ADPhoneMatcher
   ```

2. **Создайте ветку**:

   ```bash
   git checkout -b feature/your-feature
   ```

3. **Сделайте изменения**:
   - Следуйте PEP 8 для Python.
   - Обновляйте документацию (`README.md`, `docs/Technical_Specification.md`).
   - Добавляйте тесты для новых функций.

4. **Протестируйте**:

   ```bash
   python3 -m phone_matcher.main data/ad_input/ad_input.csv -v
   ```

5. **Коммит**:

   ```bash
   git add .
   git commit -m "Добавлена фича: описание"
   ```

6. **Отправьте Pull Request**:
   - Укажите, что изменено и почему.
   - Ссылка на связанные issues.

## Стандарты кода

- Python: PEP 8.
- Коммиты: ясные сообщения, например, "Fix: исправлено логирование".
- Документация: Markdown, анонимизированная. Используйте вымышленные данные (например, "Иван Иванов", "123456", "<ivan.ivanov@company.com>") в примерах.

## Сообщение об ошибках

- Откройте issue с тегом `bug`.
- Укажите:
  - Описание проблемы.
  - Шаги для воспроизведения.
  - Ожидаемое поведение.
  - Логи (`logs/log_*.log`) и анонимизированный лог аномалий (`logs/anomalies_*.log`), если он создан.
  - Используйте вымышленные данные в примерах.

## Контакты

- Репозиторий: <https://github.com/SkyrocketStan/ADPhoneMatcher>
