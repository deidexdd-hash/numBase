# Установка Tesseract-OCR для OCR PDF

## Windows

### 1. Скачать установщик
Откройте в браузере: https://github.com/UB-Mannheim/tesseract/wiki

Или прямая ссылка:
```
https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe
```

### 2. Установить
1. Запустите скачанный файл
2. Выберите "Русский" (Russian) в списке языков при установке
3. Запомните путь установки (обычно `C:\Program Files\Tesseract-OCR`)

### 3. Добавить в PATH
```batch
# Откройте PowerShell от администратора и выполните:
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Tesseract-OCR", "Machine")
```

Или вручную:
- Панель управления → Система → Дополнительные параметры системы
- Переменные среды
- В "Path" добавьте: `C:\Program Files\Tesseract-OCR`

### 4. Проверить установку
Откройте новое окно командной строки и выполните:
```batch
tesseract --version
```

Должно показать версию (например, 5.3.3)

### 5. Установить Python библиотеки
```batch
pip install pytesseract pdf2image pillow
```

### 6. Установить Poppler (для pdf2image)
Скачайте: https://github.com/oschwartz10612/poppler-windows/releases/

Распакуйте в `C:\poppler` и добавьте в PATH:
```
C:\poppler\bin
```

## Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-rus poppler-utils
pip install pytesseract pdf2image pillow
```

## macOS

```bash
brew install tesseract tesseract-lang
pip install pytesseract pdf2image pillow
```

## Проверка OCR

После установки проверьте:

```python
import pytesseract

# Должно показать список языков включая 'rus'
print(pytesseract.get_languages())

# Должно содержать 'rus'
```

## Решение проблем

### Ошибка: "tesseract is not installed or it's not in your PATH"
- Проверьте PATH
- Перезапустите терминал/IDE
- Проверьте: `where tesseract` (Windows) или `which tesseract` (Linux/Mac)

### Ошибка: "Failed to import Poppler"
- Windows: Установите Poppler и добавьте в PATH
- Linux: `sudo apt-get install poppler-utils`

### Низкое качество распознавания
- Убедитесь что установлен русский язык: `tesseract --list-langs` должна показать 'rus'
- Увеличьте DPI в pdf2image (по умолчанию 200, попробуйте 300)

## Запуск с OCR

После установки просто запустите:

```batch
cd knowledge_base_v2
python processor/build_full_database.py
```

Скрипт автоматически:
1. Проверит наличие Tesseract
2. Определит сканированные PDF
3. Выполнит OCR с русским языком
4. Сохранит распознанный текст в SQLite
