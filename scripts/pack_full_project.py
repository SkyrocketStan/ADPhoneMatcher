import argparse
import pathlib
import fnmatch

def load_gitignore(base_dir: pathlib.Path) -> set:
    """Читает .gitignore и возвращает множество игнорируемых шаблонов."""
    ignore_patterns = set()
    gitignore_path = base_dir / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8") as gitignore_file:
            for line in gitignore_file:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.add(line.rstrip("/"))
    ignore_patterns.add("__pycache__")
    ignore_patterns.add(".git")  # Исключаем .git/ по умолчанию
    return ignore_patterns

def is_ignored(file_path: pathlib.Path, ignore_patterns: set, base_dir: pathlib.Path) -> bool:
    """Проверяет, игнорируется ли файл согласно шаблонам."""
    rel_path = file_path.relative_to(base_dir).as_posix()
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(rel_path, f"{pattern}/*"):
            return True
    return False

def pack_full_project(base_dir: pathlib.Path, output_file: str, exclude_patterns: list) -> None:
    """Создаёт листинг всех файлов проекта, не входящих в .gitignore."""
    ignore_patterns = load_gitignore(base_dir).union(set(exclude_patterns))
    project_files = []

    for file_path in base_dir.rglob("*"):
        if file_path.is_file() and not is_ignored(file_path, ignore_patterns, base_dir):
            project_files.append(file_path)

    # Перезаписываем выходной файл
    with open(output_file, "w", encoding="utf-8") as output_handle:
        for file_path in sorted(project_files):
            rel_path = file_path.relative_to(base_dir)
            output_handle.write(f"----- {rel_path} -----\n")
            try:
                with open(file_path, "r", encoding="utf-8") as source_file:
                    output_handle.write(source_file.read())
            except (UnicodeDecodeError, IOError):
                output_handle.write("[Невозможно прочитать файл]\n")
            output_handle.write("\n")
    
    return len(project_files)

def main():
    """Обрабатывает аргументы командной строки и запускает сбор листинга."""
    parser = argparse.ArgumentParser(description="Создаёт полный листинг проекта")
    parser.add_argument("--base-dir", default=".", help="Корень проекта")
    parser.add_argument("--output", default="full_project_files.txt", help="Выходной файл")
    parser.add_argument("--exclude", action="append", default=[], help="Дополнительные исключения")
    args = parser.parse_args()
    
    try:
        num_files = pack_full_project(pathlib.Path(args.base_dir).resolve(), args.output, args.exclude)
        print(f"Листинг успешно создан: {args.output} ({num_files} файлов)")
    except Exception as e:
        print(f"Ошибка при создании листинга: {e}")

if __name__ == "__main__":
    main()
