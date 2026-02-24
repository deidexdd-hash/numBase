#Requires -RunAsAdministrator
# PowerShell setup script for Ancestral Numerology System

param(
    [switch]$Force,
    [switch]$DryRun
)

$PythonVersion = "3.11.9"
$PythonUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe"
$TesseractUrl = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.1.20250102/tesseract-ocr-w64-setup-5.4.1.20250102.exe"
$PopplerUrl = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip"

$TempDir = "$env:TEMP\AncestralSetup"
$LogFile = "$TempDir\install.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] $Message" | Add-Content -Path $LogFile -ErrorAction SilentlyContinue
    Write-Host $Message
}

function Test-Admin {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-Python {
    try {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if ($python) {
            $ver = & python --version 2>&1
            Write-Log "Python found: $ver"
            return $true
        }
    } catch {}
    Write-Log "Python not found"
    return $false
}

function Test-Tesseract {
    try {
        $tess = Get-Command tesseract -ErrorAction SilentlyContinue
        if ($tess) {
            $ver = & tesseract --version 2>&1 | Select-Object -First 1
            Write-Log "Tesseract found: $ver"
            return $true
        }
    } catch {}
    Write-Log "Tesseract not found"
    return $false
}

function Test-Poppler {
    try {
        $pdf = Get-Command pdftoppm -ErrorAction SilentlyContinue
        if ($pdf) {
            Write-Log "Poppler found: $($pdf.Source)"
            return $true
        }
    } catch {}
    Write-Log "Poppler not found"
    return $false
}

function Install-Python {
    Write-Log "Installing Python $PythonVersion..."
    
    if (-not $Force) {
        $confirm = Read-Host "Install Python $PythonVersion? (y/n)"
        if ($confirm -notin @('y','yes')) { return $false }
    }
    
    try {
        New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
        $installer = "$TempDir\python-installer.exe"
        
        Write-Log "Downloading Python..."
        Invoke-WebRequest -Uri $PythonUrl -OutFile $installer -UseBasicParsing
        
        Write-Log "Installing Python (this may take a few minutes)..."
        $proc = Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0" -Wait -PassThru
        
        if ($proc.ExitCode -eq 0) {
            Write-Log "Python installed successfully"
            return $true
        }
    } catch {
        Write-Log "Error installing Python: $_"
    }
    return $false
}

function Install-Tesseract {
    Write-Log "Installing Tesseract-OCR..."
    
    if (-not $Force) {
        $confirm = Read-Host "Install Tesseract-OCR with Russian language? (y/n)"
        if ($confirm -notin @('y','yes')) { return $false }
    }
    
    try {
        $installer = "$TempDir\tesseract.exe"
        
        Write-Log "Downloading Tesseract..."
        Invoke-WebRequest -Uri $TesseractUrl -OutFile $installer -UseBasicParsing
        
        Write-Log "Installing Tesseract..."
        $proc = Start-Process -FilePath $installer -ArgumentList "/S" -Wait -PassThru
        
        if ($proc.ExitCode -eq 0) {
            # Add to PATH
            $path = "C:\Program Files\Tesseract-OCR"
            $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
            if ($currentPath -notlike "*$path*") {
                [Environment]::SetEnvironmentVariable("Path", "$currentPath;$path", "Machine")
                Write-Log "Added Tesseract to PATH"
            }
            Write-Log "Tesseract installed successfully"
            return $true
        }
    } catch {
        Write-Log "Error installing Tesseract: $_"
    }
    return $false
}

function Install-Poppler {
    Write-Log "Installing Poppler..."
    
    if (-not $Force) {
        $confirm = Read-Host "Install Poppler? (y/n)"
        if ($confirm -notin @('y','yes')) { return $false }
    }
    
    try {
        $zip = "$TempDir\poppler.zip"
        
        Write-Log "Downloading Poppler..."
        Invoke-WebRequest -Uri $PopplerUrl -OutFile $zip -UseBasicParsing
        
        Write-Log "Extracting Poppler..."
        Expand-Archive -Path $zip -DestinationPath "C:\poppler" -Force
        
        # Add to PATH
        $binPath = "C:\poppler\bin"
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
        if ($currentPath -notlike "*$binPath*") {
            [Environment]::SetEnvironmentVariable("Path", "$currentPath;$binPath", "Machine")
            Write-Log "Added Poppler to PATH"
        }
        
        Write-Log "Poppler installed successfully"
        return $true
    } catch {
        Write-Log "Error installing Poppler: $_"
    }
    return $false
}

function Install-PipPackages {
    Write-Log "Installing Python packages..."
    
    if (-not $Force) {
        $confirm = Read-Host "Install Python libraries (pytesseract, pdf2image, pillow)? (y/n)"
        if ($confirm -notin @('y','yes')) { return $false }
    }
    
    try {
        # Check if pip works
        $pipTest = & python -m pip --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Error: pip not found"
            return $false
        }
        
        Write-Log "Installing packages..."
        & python -m pip install --upgrade pip
        & python -m pip install pytesseract pdf2image pillow
        
        Write-Log "Python packages installed successfully"
        return $true
    } catch {
        Write-Log "Error installing packages: $_"
    }
    return $false
}

# Main
if (-not (Test-Admin)) {
    Write-Error "This script requires Administrator privileges!"
    exit 1
}

New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

Write-Log "================================"
Write-Log "ANCESTRAL NUMEROLOGY SETUP"
Write-Log "================================"
Write-Log ""

if ($DryRun) {
    Write-Log "DRY RUN MODE - Nothing will be installed"
    Write-Log ""
}

# Check current status
$hasPython = Test-Python
$hasTesseract = Test-Tesseract
$hasPoppler = Test-Poppler

Write-Log ""
Write-Log "Current status:"
Write-Log "  Python: $(if($hasPython){'OK'}else{'Missing'})"
Write-Log "  Tesseract: $(if($hasTesseract){'OK'}else{'Missing'})"
Write-Log "  Poppler: $(if($hasPoppler){'OK'}else{'Missing'})"
Write-Log ""

if ($DryRun) {
    Write-Log "Run without -DryRun to install missing components"
    exit 0
}

# Install missing components
$installed = @()

if (-not $hasPython) {
    if (Install-Python) { $installed += "Python" }
}

if (-not $hasTesseract) {
    if (Install-Tesseract) { $installed += "Tesseract" }
}

if (-not $hasPoppler) {
    if (Install-Poppler) { $installed += "Poppler" }
}

# Always install pip packages
if (Install-PipPackages) { $installed += "Python Libraries" }

# Summary
Write-Log ""
Write-Log "================================"
Write-Log "INSTALLATION COMPLETE"
Write-Log "================================"
Write-Log ""

if ($installed.Count -gt 0) {
    Write-Log "Installed:"
    $installed | ForEach-Object { Write-Log "  + $_" }
} else {
    Write-Log "All components were already installed"
}

Write-Log ""
Write-Log "IMPORTANT: Restart your computer to apply PATH changes!"
Write-Log ""
Write-Log "After restart, run:"
Write-Log "  cd knowledge_base_v2"
Write-Log "  python start.py"
Write-Log ""

# Cleanup
Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue

Read-Host "Press Enter to exit..."
