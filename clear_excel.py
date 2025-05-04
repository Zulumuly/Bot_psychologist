import os

file_path = "export.xlsx"

if os.path.exists(file_path):
    os.remove(file_path)
    print("Файл удалён.")
else:
    print("Файл не найден.")
