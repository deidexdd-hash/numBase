#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Скрипт полноценного развертывания системы Ancestral Numerology
    
.DESCRIPTION
    Устанавливает:
    - Python 3.11 (если не установлен)
    - Tesseract-OCR с русским языком
    - Poppler
    - Python библиотеки
    - Настраивает переменные среды
    
    Все действия выполняются с подтверждением пользователя
#>

param(
    [switch]$Force,  # Пропустить подтверждения
    [switch]$DryRun  # Только показать, что будет сделано
)

# Настройки
$PythonVersion = "3.11.9"
$PythonInstaller = "python-$PythonVersion-amd64.exe"
$PythonUrl = "https://www.python.org/ftp/python/$PythonVersion/$PythonInstaller"
$TempDir = "$env:TEMP\AncestralSetup"
$LogFile = "$TempDir\install.log"

# Цвета
$SuccessColor = "Green"
$WarningColor = "Yellow"
$ErrorColor = "Red"
$InfoColor = "Cyan"

# Хранилище для отката
$Global:Changes = @()
$Global:InstalledComponents = @()

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $logEntry -ErrorAction SilentlyContinue
    
    switch ($Level) {
        "SUCCESS" { Write-Host $Message -ForegroundColor $SuccessColor }
        "WARNING" { Write-Host $Message -ForegroundColor $WarningColor }
        "ERROR"   { Write-Host $Message -ForegroundColor $ErrorColor }
        "INFO"    { Write-Host $Message -ForegroundColor $InfoColor }
        default   { Write-Host $Message }
    }
}

function Show-Banner {
    Clear-Host
    Write-Host @"
================================================================================
    🔮 СИСТЕМА РАЗВЕРТЫВАНИЯ
    Ансестология и Нумерология
================================================================================

    ⚠️  ВНИМАНИЕ: Этот скрипт выполнит следующие действия:
    
    1. Проверит и установит Python 3.11 (если не установлен)
    2. Установит Tesseract-OCR с русским языком
    3. Установит Poppler для работы с PDF
    4. Добавит пути в системную переменную PATH
    5. Установит Python библиотеки
    
    📋 Требования:
    • Windows 10/11 (64-bit)
    • Подключение к интернету
    • ~500 MB свободного места
    • Права администратора
    
================================================================================
"@ -ForegroundColor $InfoColor
}

function Show-Menu {
    Write-Host ""
    Write-Host "Выберите действие:" -ForegroundColor $InfoColor
    Write-Host "1. Полная установка (рекомендуется)"
    Write-Host "2. Только проверка (без установки)"
    Write-Host "3. Установка выборочная"
    Write-Host "4. Отмена"
    Write-Host ""
    
    $choice = Read-Host "Введите номер (1-4)"
    return $choice
}

function Test-AdminRights {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-PythonInstalled {
    Write-Log "Проверка Python..." -Level "INFO"
    
    try {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if ($python) {
            $version = & python --version 2>&1
            Write-Log "✓ Python найден: $version" -Level "SUCCESS"
            
            # Проверяем версию
            if ($version -match "3\.(8|9|10|11|12)") {
                Write-Log "  Версия совместима" -Level "SUCCESS"
                return $true
            } else {
                Write-Log "⚠ Версия $version может быть несовместима (рекомендуется 3.11)" -Level "WARNING"
                return $false
            }
        }
    } catch {
        Write-Log "✗ Python не найден" -Level "WARNING"
    }
    
    return $false
}

function Test-TesseractInstalled {
    Write-Log "Проверка Tesseract-OCR..." -Level "INFO"
    
    try {
        $tesseract = Get-Command tesseract -ErrorAction SilentlyContinue
        if ($tesseract) {
            $version = & tesseract --version 2>&1 | Select-Object -First 1
            Write-Log "✓ Tesseract найден: $version" -Level "SUCCESS"
            
            # Проверяем русский язык
            $langs = & tesseract --list-langs 2>&1
            if ($langs -contains "rus") {
                Write-Log "  Русский язык доступен" -Level "SUCCESS"
                return $true
            } else {
                Write-Log "⚠ Русский язык не установлен" -Level "WARNING"
                return $false
            }
        }
    } catch {
        Write-Log "✗ Tesseract не найден" -Level "WARNING"
    }
    
    return $false
}

function Test-PopplerInstalled {
    Write-Log "Проверка Poppler..." -Level "INFO"
    
    try {
        $pdftoppm = Get-Command pdftoppm -ErrorAction SilentlyContinue
        if ($pdftoppm) {
            Write-Log "✓ Poppler найден: $($pdftoppm.Source)" -Level "SUCCESS"
            return $true
        }
    } catch {
        Write-Log "✗ Poppler не найден" -Level "WARNING"
    }
    
    return $false
}

function Install-Python {
    param([switch]$SkipConfirm)
    
    Write-Log "" 
    Write-Log "=== УСТАНОВКА PYTHON $PythonVersion ===" -Level "INFO"
    
    if (-not $SkipConfirm -and -not $Force) {
        Write-Log "Будет установлен Python $PythonVersion" -Level "INFO"
        Write-Log "  • Загрузка: ~27 MB" -Level "INFO"
        Write-Log "  • Установка: C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311" -Level "INFO"
        Write-Log "  • Добавление в PATH" -Level "INFO"
        
        $confirm = Read-Host "Продолжить установку Python? (y/n)"
        if ($confirm -notin @('y', 'yes', 'д', 'да')) {
            Write-Log "Пропуск установки Python" -Level "WARNING"
            return $false
        }
    }
    
    try {
        # Создаем временную папку
        New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
        $installerPath = "$TempDir\$PythonInstaller"
        
        # Загружаем установщик
        Write-Log "Загрузка Python..." -Level "INFO"
        Invoke-WebRequest -Uri $PythonUrl -OutFile $installerPath -UseBasicParsing
        Write-Log "✓ Загружено: $installerPath" -Level "SUCCESS"
        
        # Устанавливаем (тихая установка)
        Write-Log "Установка Python..." -Level "INFO"
        $arguments = "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0"
        $process = Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait -PassThru
        
 if ($process.ExitCode -eq 0) {
            Write-Log "✓ Python установлен успешно" -Level "SUCCESS"
            $Global:InstalledComponents += "Python $PythonVersion"
            $Global:Changes += @{Type = "Software"; Name = "Python $PythonVersion"; Path = $installerPath}
            return $true
        } else {
            Write-Log "✗ Ошибка установки Python (код: $($process.ExitCode))" -Level "ERROR"
            return $false
        }
    } catch {
        Write-Log "✗ Ошибка: $_" -Level "ERROR"
        return $false
    }
}

function Install-Tesseract {
    param([switch]$SkipConfirm)
    
    Write-Log ""
    Write-Log "=== УСТАНОВКА TESSERACT-OCR ===" -Level "INFO"
    
    if (-not $SkipConfirm -and -not $Force) {
        Write-Log "Будет установлен Tesseract-OCR 5.4.1 с русским языком" -Level "INFO"
        Write-Log "  • Загрузка: ~300 MB" -Level "INFO"
        Write-Log "  • Установка: C:\Program Files\Tesseract-OCR" -Level "INFO"
        Write-Log "  • Языки: English, Russian" -Level "INFO"
        
        $confirm = Read-Host "Продолжить установку Tesseract? (y/n)"
        if ($confirm -notin @('y', 'yes', 'д', 'да')) {
            Write-Log "Пропуск установки Tesseract" -Level "WARNING"
            return $false
        }
    }
    
    try {
        $tesseractUrl = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.1.20250102/tesseract-ocr-w64-setup-5.4.1.20250102.exe"
        $installerPath = "$TempDir\tesseract-setup.exe"
        
        # Загружаем
        Write-Log "Загрузка Tesseract..." -Level "INFO"
        Invoke-WebRequest -Uri $tesseractUrl -OutFile $installerPath -UseBasicParsing
        Write-Log "✓ Загружено" -Level "SUCCESS"
        
        # Устанавливаем (тихая установка с русским языком)
        Write-Log "Установка Tesseract..." -Level "INFO"
        $arguments = "/S /D=C:\Program Files\Tesseract-OCR"
        $process = Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            # Добавляем в PATH
            Write-Log "Добавление Tesseract в PATH..." -Level "INFO"
            $tesseractPath = "C:\Program Files\Tesseract-OCR"
            $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
            
            if ($currentPath -notlike "*$tesseractPath*") {
                [Environment]::SetEnvironmentVariable("Path", "$currentPath;$tesseractPath", "Machine")
                $Global:Changes += @{Type = "PATH"; Value = $tesseractPath}
                Write-Log "✓ Добавлено в PATH" -Level "SUCCESS"
            }
            
            Write-Log "✓ Tesseract установлен успешно" -Level "SUCCESS"
            $Global:InstalledComponents += "Tesseract-OCR"
            return $true
        } else {
            Write-Log "✗ Ошибка установки Tesseract" -Level "ERROR"
            return $false
        }
    } catch {
        Write-Log "✗ Ошибка: $_" -Level "ERROR"
        return $false
    }
}

function Install-Poppler {
    param([switch]$SkipConfirm)
    
    Write-Log ""
    Write-Log "=== УСТАНОВКА POPPLER ===" -Level "INFO"
    
    if (-not $SkipConfirm -and -not $Force) {
        Write-Log "Будет установлен Poppler" -Level "INFO"
        Write-Log "  • Загрузка: ~50 MB" -Level "INFO"
        Write-Log "  • Установка: C:\poppler" -Level "INFO"
        
        $confirm = Read-Host "Продолжить установку Poppler? (y/n)"
        if ($confirm -notin @('y', 'yes', 'д', 'да')) {
            Write-Log "Пропуск установки Poppler" -Level "WARNING"
            return $false
        }
    }
    
    try {
        $popplerUrl = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip"
        $zipPath = "$TempDir\poppler.zip"
        $extractPath = "C:\poppler"
        
        # Загружаем
        Write-Log "Загрузка Poppler..." -Level "INFO"
        Invoke-WebRequest -Uri $popplerUrl -OutFile $zipPath -UseBasicParsing
        Write-Log "✓ Загружено" -Level "SUCCESS"
        
        # Распаковываем
        Write-Log "Распаковка Poppler..." -Level "INFO"
        Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
        Write-Log "✓ Распаковано в $extractPath" -Level "SUCCESS"
        
        # Добавляем в PATH
        Write-Log "Добавление Poppler в PATH..." -Level "INFO"
        $popplerBin = "$extractPath\bin"
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
        
        if ($currentPath -notlike "*$popplerBin*") {
            [Environment]::SetEnvironmentVariable("Path", "$currentPath;$popplerBin", "Machine")
            $Global:Changes += @{Type = "PATH"; Value = $popplerBin}
            Write-Log "✓ Добавлено в PATH" -Level "SUCCESS"
        }
        
        Write-Log "✓ Poppler установлен успешно" -Level "SUCCESS"
        $Global:InstalledComponents += "Poppler"
        return $true
    } catch {
        Write-Log "✗ Ошибка: $_" -Level "ERROR"
        return $false
    }
}

function Install-PythonPackages {
    param([switch]$SkipConfirm)
    
    Write-Log ""
    Write-Log "=== УСТАНОВКА PYTHON БИБЛИОТЕК ===" -Level "INFO"
    
    if (-not $SkipConfirm -and -not $Force) {
        Write-Log "Будут установлены библиотеки:" -Level "INFO"
        Write-Log "  • pytesseract (интерфейс к Tesseract)" -Level "INFO"
        Write-Log "  • pdf2image (конвертация PDF в изображения)" -Level "INFO"
        Write-Log "  • pillow (обработка изображений)" -Level "INFO"
        
        $confirm = Read-Host "Продолжить установку библиотек? (y/n)"
        if ($confirm -notin @('y', 'yes', 'д', 'да')) {
            Write-Log "Пропуск установки библиотек" -Level "WARNING"
            return $false
        }
    }
    
    try {
        Write-Log "Установка библиотек..." -Level "INFO"
        
        # Проверяем, что python доступен
        $python = Get-Command python -ErrorAction SilentlyContinue
        if (-not $python) {
            Write-Log "✗ Python не найден в PATH" -Level "ERROR"
            return $false
        }
        
        # Устанавливаем
        & python -m pip install --upgrade pip
        & python -m pip install pytesseract pdf2image pillow
        
        Write-Log "✓ Библиотеки установлены" -Level "SUCCESS"
        $Global:InstalledComponents += "Python Libraries"
        return $true
    } catch {
        Write-Log "✗ Ошибка установки библиотек: $_" -Level "ERROR"
        return $false
    }
}

function Show-Summary {
    Write-Log ""
    Write-Log "================================================================================" -Level "INFO"
    Write-Log "                    ИТОГИ УСТАНОВКИ" -Level "INFO"
    Write-Log "================================================================================" -Level "INFO"
    
    if ($Global:InstalledComponents.Count -eq 0) {
        Write-Log "Ничего не было установлено" -Level "WARNING"
    } else {
        Write-Log "Установленные компоненты:" -Level "SUCCESS"
        foreach ($comp in $Global:InstalledComponents) {
            Write-Log "  ✓ $comp" -Level "SUCCESS"
        }
    }
    
    Write-Log ""
    Write-Log "Проверка установки:" -Level "INFO"
    
    # Проверяем все компоненты
    $pythonOk = Test-PythonInstalled
    $tesseractOk = Test-TesseractInstalled
    $popplerOk = Test-PopplerInstalled
    
    if ($pythonOk -and $tesseractOk -and $popplerOk) {
        Write-Log ""
        Write-Log "🎉 ВСЕ КОМПОНЕНТЫ УСТАНОВЛЕНЫ УСПЕШНО!" -Level "SUCCESS"
        Write-Log ""
        Write-Log "Теперь можно использовать OCR:" -Level "INFO"
        Write-Log "  python run_ocr.py" -Level "INFO"
        Write-Log "  python start.py" -Level "INFO"
    } else {
        Write-Log ""
        Write-Log "⚠️  НЕКОТОРЫЕ КОМПОНЕНТЫ НЕ УСТАНОВЛЕНЫ" -Level "WARNING"
        Write-Log ""
        Write-Log "Проверьте лог: $LogFile" -Level "INFO"
    }
    
    Write-Log ""
    Write-Log "⚠️  ВАЖНО: Перезагрузите компьютер для применения изменений PATH!" -Level "WARNING"
    Write-Log ""
    Write-Log "После перезагрузки запустите:" -Level "INFO"
    Write-Log "  cd knowledge_base_v2" -Level "INFO"
    Write-Log "  python start.py" -Level "INFO"
}

function Invoke-Rollback {
    Write-Log ""
    Write-Log "=== ОТКАТ ИЗМЕНЕНИЙ ===" -Level "WARNING"
    
    foreach ($change in $Global:Changes) {
        try {
            switch ($change.Type) {
                "PATH" {
                    Write-Log "Удаление из PATH: $($change.Value)" -Level "INFO"
                    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
                    $newPath = $currentPath -replace [regex]::Escape(";" + $change.Value), ""
                    [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
                }
                "Software" {
                    Write-Log "Удаление программы: $($change.Name)" -Level "INFO"
                    # Для Python можно запустить uninstaller
                    if ($change.Name -like "Python*") {
                        $uninstaller = $change.Path -replace "\.exe$", "_uninstall.exe"
                        if (Test-Path $uninstaller) {
                            Start-Process -FilePath $uninstaller -ArgumentList "/S" -Wait
                        }
                    }
                }
            }
        } catch {
            Write-Log "Ошибка отката: $_" -Level "ERROR"
        }
    }
}

# === ГЛАВНАЯ ЛОГИКА ===

# Проверяем права администратора
if (-not (Test-AdminRights)) {
    Write-Error "Этот скрипт требует права администратора! Запустите PowerShell от имени администратора."
    exit 1
}

# Создаем временную папку
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

# Показываем баннер
Show-Banner

# Режим dry-run
if ($DryRun) {
    Write-Log "РЕЖИМ ПРОВЕРКИ (Dry Run) - ничего не будет установлено" -Level "WARNING"
    Write-Log ""
}

# Получаем выбор пользователя
$choice = Show-Menu

switch ($choice) {
    "1" {  # Полная установка
        Write-Log "Выбрана полная установка" -Level "INFO"
        
        if (-not $DryRun) {
            # Проверяем что уже установлено
            $havePython = Test-PythonInstalled
            $haveTesseract = Test-TesseractInstalled
            $havePoppler = Test-PopplerInstalled
            
            # Устанавливаем что нужно
            if (-not $havePython) {
                Install-Python -SkipConfirm:$Force
            }
            
            if (-not $haveTesseract) {
                Install-Tesseract -SkipConfirm:$Force
            }
            
            if (-not $havePoppler) {
                Install-Poppler -SkipConfirm:$Force
            }
            
            # Всегда устанавливаем библиотеки
            Install-PythonPackages -SkipConfirm:$Force
            
            # Показываем итоги
            Show-Summary
        } else {
            Write-Log "В режиме проверки установка пропущена" -Level "WARNING"
        }
    }
    
    "2" {  # Только проверка
        Write-Log "РЕЖИМ ПРОВЕРКИ" -Level "INFO"
        Write-Log ""
        
        Test-PythonInstalled
        Test-TesseractInstalled
        Test-PopplerInstalled
        
        Write-Log ""
        Write-Log "Проверка завершена. Для установки запустите скрипт снова и выберите 'Полная установка'" -Level "INFO"
    }
    
    "3" {  # Выборочная установка
        Write-Log "ВЫБОРОЧНАЯ УСТАНОВКА" -Level "INFO"
        Write-Log ""
        
        if ((Read-Host "Установить Python? (y/n)") -in @('y', 'yes')) {
            Install-Python
        }
        
        if ((Read-Host "Установить Tesseract-OCR? (y/n)") -in @('y', 'yes')) {
            Install-Tesseract
        }
        
        if ((Read-Host "Установить Poppler? (y/n)") -in @('y', 'yes')) {
            Install-Poppler
        }
        
        if ((Read-Host "Установить Python библиотеки? (y/n)") -in @('y', 'yes')) {
            Install-PythonPackages
        }
        
        Show-Summary
    }
    
    "4" {  # Отмена
        Write-Log "Установка отменена пользователем" -Level "WARNING"
        exit 0
    }
    
    default {
        Write-Log "Неверный выбор" -Level "ERROR"
        exit 1
    }
}

# Очистка
Write-Log ""
Write-Log "Очистка временных файлов..." -Level "INFO"
Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
Write-Log "✓ Готово" -Level "SUCCESS"

Write-Log ""
Write-Log "Лог установки сохранен в: $LogFile" -Level "INFO"

Read-Host "`nНажмите Enter для выхода..."
