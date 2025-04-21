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
    ignore_patterns.add("__pycache__")  # Явно исключаем __pycache__
    return ignore_patterns

def is_ignored(file_path: pathlib.Path, ignore_patterns: set, base_dir: pathlib.Path) -> bool:
    """Проверяет, игнорируется ли файл согласно .gitignore."""
    rel_path = file_path.relative_to(base_dir).as_posix()
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(rel_path, f"{pattern}/*"):
            return True
    return False

def pack_project(output_file: str) -> None:
    """Создаёт текстовый файл с содержимым проекта для пересылки."""
    project_files = []
    base_dir = pathlib.Path.cwd()
    ignore_patterns = load_gitignore(base_dir)

    # Файлы в phone_matcher/
    phone_matcher_dir = base_dir / "phone_matcher"
    if phone_matcher_dir.exists():
        for file_path in phone_matcher_dir.glob("*.py"):
            if not is_ignored(file_path, ignore_patterns, base_dir):
                project_files.append(file_path)
    # run.sh
    run_script = base_dir / "run.sh"
    if run_script.exists() and not is_ignored(run_script, ignore_patterns, base_dir):
        project_files.append(run_script)

    # Создаём output_file
    with open(output_file, "w", encoding="utf-8") as output_file_handle:
        for file_path in sorted(project_files):
            rel_path = file_path.relative_to(base_dir)
            output_file_handle.write(f"----- {rel_path} -----\n")
            with open(file_path, "r", encoding="utf-8") as source_file:
                output_file_handle.write(source_file.read())
            output_file_handle.write("\n")

if __name__ == "__main__":
    pack_project("project_files.txt")
