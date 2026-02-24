@echo off
chcp 1251 >nul
title OCR Proverka i Zapusk
color 0A

cls
echo.
echo  ===========================================
echo   OCR Proverka i Ustanovka
echo  ===========================================
echo.

cd /d "%~dp0"

:: Proverjaem Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [X] Python ne najden!
    echo  Ustanovite Python 3.8+ s python.org
    pause
    exit /b 1
)

echo  [OK] Python najden
echo.

:: Zapuskaem proverku
echo  Zapusk proverki OCR...
echo.
python check_ocr.py

if errorlevel 1 (
    echo.
    echo  ===========================================
    echo   Ustanovka Python paketov...
    echo  ===========================================
    echo.
    pip install -q pytesseract pdf2image pillow
    echo  [OK] Python pakety ustanovleny
    echo.
    echo  Vnimanie! Dlja zavershenija ustanovki:
    echo  1. Ustanovite Tesseract-OCR s russkim jazykom
    echo     https://github.com/UB-Mannheim/tesseract/wiki
    echo  2. Ustanovite Poppler
    echo     https://github.com/oschwartz10612/poppler-windows
    echo  3. Dobavte oba v PATH
    echo  4. Perezapustite jetot skript
    echo.
) else (
    echo.
    echo  ===========================================
    echo   Vyberite dejstvie:
    echo  ===========================================
    echo  1. Raspoznat odin PDF fajl
    echo  2. Raspoznat vse PDF v papke
    echo  3. Peresobrat bazu s OCR
    echo  4. Vyhod
    echo.
    
    set /p choice="Vash vybor (1-4): "
    
    if "%choice%"=="1" (
        set /p file="Vvedite put k PDF: "
        python processor\ocr_utils.py "%file%" --output output.txt
        if exist output.txt (
            echo.
            echo  Rezultat sohranen v: output.txt
            start output.txt
        )
    )
    
    if "%choice%"=="2" (
        set /p dir="Vvedite put k papke s PDF: "
        if not exist ocr_output mkdir ocr_output
        python processor\ocr_utils.py --directory "%dir%" --output-dir ocr_output
        echo.
        echo  Rezultaty sohraneny v papke: ocr_output
    )
    
    if "%choice%"=="3" (
        echo.
        echo  Peresborka bazy s OCR...
        echo  Eto zajmet 10-30 minut...
        python processor\build_full_database.py
    )
)

echo.
pause
