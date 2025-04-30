import os
import pathlib

def save_file(file_path: pathlib.Path, content: list) -> None:
    """Сохраняет файл с указанным содержимым и устанавливает права."""
    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as out:
        out.write("".join(content))
    mode = 0o755 if file_path.name == "run.sh" else 0o644
    os.chmod(file_path, mode)

def deploy_project(input_file: str) -> None:
    """Разворачивает файлы проекта из текстового файла."""
    current_dir = pathlib.Path.cwd()
    current_file = None
    file_content = []

    # Создаём директории
    os.makedirs(current_dir / "data" / "ad_input", exist_ok=True)
    os.makedirs(current_dir / "data" / "phone_data", exist_ok=True)
    os.makedirs(current_dir / "data" / "results", exist_ok=True)
    os.makedirs(current_dir / "data" / "archive", exist_ok=True)
    os.makedirs(current_dir / "logs", exist_ok=True)

    # Читаем input_file
    with open(input_file, "r", encoding="utf-8") as input_file_handle:
        for line in input_file_handle:
            if line.startswith("----- ") and line.endswith(" -----\n"):
                # Сохраняем предыдущий файл
                if current_file and file_content:
                    file_path = current_dir / current_file
                    save_file(file_path, file_content)
                # Новый файл
                current_file = line[6:-7].strip()  # Убираем ----- и \n
                file_content = []
            else:
                file_content.append(line)

    # Сохраняем последний файл
    if current_file and file_content:
        file_path = current_dir / current_file
        save_file(file_path, file_content)

if __name__ == "__main__":
    deploy_project("project_files.txt")
