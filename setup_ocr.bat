@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo   УСТАНОВКА TESSERACT-OCR С РУССКИМ ЯЗЫКОМ
echo ============================================================
echo.

echo [1/5] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python не найден! Установите Python 3.8+
    pause
    exit /b 1
)
echo [OK] Python найден

echo.
echo [2/5] Установка Python библиотек...
pip install -q pytesseract pdf2image pillow
if errorlevel 1 (
    echo [X] Ошибка установки библиотек
    pause
    exit /b 1
)
echo [OK] Библиотеки установлены

echo.
echo [3/5] Проверка Tesseract...
where tesseract >nul 2>&1
if errorlevel 1 (
    echo [!] Tesseract не найден в PATH
    echo.
    echo Установите Tesseract:
    echo 1. Скачайте: https://github.com/UB-Mannheim/tesseract/wiki
    echo 2. Установите с опцией "Russian"
    echo 3. Добавьте в PATH: C:\Program Files\Tesseract-OCR
    echo.
    echo Открываю страницу загрузки...
    timeout /t 3 >nul
    start https://github.com/UB-Mannheim/tesseract/wiki
    pause
    exit /b 1
)
echo [OK] Tesseract найден

echo.
echo [4/5] Проверка русского языка...
python -c "import pytesseract; exit(0 if 'rus' in pytesseract.get_languages() else 1)" >nul 2>&1
if errorlevel 1 (
    echo [X] Русский язык не установлен!
    echo.
    echo Переустановите Tesseract и выберите "Russian"
    echo в списке языков при установке.
    pause
    exit /b 1
)
echo [OK] Русский язык доступен

echo.
echo [5/5] Проверка Poppler...
where pdftoppm >nul 2>&1
if errorlevel 1 (
    echo [!] Poppler не найден
    echo.
    echo Установите Poppler:
    echo 1. Скачайте: https://github.com/oschwartz10612/poppler-windows/releases
    echo 2. Распакуйте в C:\poppler
    echo 3. Добавьте в PATH: C:\poppler\bin
    echo.
    pause
    exit /b 1
)
echo [OK] Poppler найден

echo.
echo ============================================================
echo   [OK] ВСЕ КОМПОНЕНТЫ УСТАНОВЛЕНЫ!
echo ============================================================
echo.
echo Теперь можно запускать OCR обработку:
echo   cd knowledge_base_v2
echo   python processor/build_full_database.py
echo.
pause
