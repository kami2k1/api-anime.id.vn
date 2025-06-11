# Script tự động cài đặt FFmpeg cho Windows
# Chạy script này với quyền Administrator

param(
    [switch]$UseChocolatey,
    [switch]$UseWinget,
    [switch]$Manual
)

Write-Host "=== Trình cài đặt FFmpeg tự động ===" -ForegroundColor Green
Write-Host ""

function Test-FFmpeg {
    try {
        $version = & ffmpeg -version 2>$null
        if ($version) {
            Write-Host "✅ FFmpeg đã được cài đặt!" -ForegroundColor Green
            Write-Host "Phiên bản: $($version[0])" -ForegroundColor Gray
            return $true
        }
    }
    catch {
        return $false
    }
    return $false
}

function Install-FFmpegChocolatey {
    Write-Host "📦 Cài đặt FFmpeg bằng Chocolatey..." -ForegroundColor Yellow
    
    # Kiểm tra Chocolatey
    try {
        $chocoVersion = & choco --version 2>$null
        if (-not $chocoVersion) {
            throw "Chocolatey không tìm thấy"
        }
    }
    catch {
        Write-Host "⚠️ Chocolatey chưa được cài đặt. Đang cài đặt..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    }
    
    # Cài đặt FFmpeg
    & choco install ffmpeg -y
    
    if (Test-FFmpeg) {
        Write-Host "✅ FFmpeg đã được cài đặt thành công bằng Chocolatey!" -ForegroundColor Green
        return $true
    }
    return $false
}

function Install-FFmpegWinget {
    Write-Host "📦 Cài đặt FFmpeg bằng Windows Package Manager..." -ForegroundColor Yellow
    
    try {
        & winget install ffmpeg --accept-package-agreements --accept-source-agreements
        
        if (Test-FFmpeg) {
            Write-Host "✅ FFmpeg đã được cài đặt thành công bằng Winget!" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "❌ Lỗi khi cài đặt bằng Winget: $_" -ForegroundColor Red
    }
    return $false
}

function Install-FFmpegManual {
    Write-Host "📦 Hướng dẫn cài đặt FFmpeg thủ công..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Truy cập: https://ffmpeg.org/download.html" -ForegroundColor Cyan
    Write-Host "2. Chọn 'Windows builds'" -ForegroundColor Cyan  
    Write-Host "3. Tải và giải nén vào C:\ffmpeg" -ForegroundColor Cyan
    Write-Host "4. Thêm C:\ffmpeg\bin vào biến môi trường PATH" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Sau khi hoàn thành, khởi động lại ứng dụng." -ForegroundColor Yellow
}

# Kiểm tra FFmpeg hiện tại
if (Test-FFmpeg) {
    Write-Host "FFmpeg đã sẵn sàng sử dụng!" -ForegroundColor Green
    Read-Host "Nhấn Enter để thoát"
    exit 0
}

Write-Host "❌ FFmpeg chưa được cài đặt hoặc không tìm thấy trong PATH" -ForegroundColor Red
Write-Host ""

# Xử lý tham số
if ($UseChocolatey) {
    if (Install-FFmpegChocolatey) { exit 0 } else { exit 1 }
}
elseif ($UseWinget) {
    if (Install-FFmpegWinget) { exit 0 } else { exit 1 }
}
elseif ($Manual) {
    Install-FFmpegManual
    exit 0
}

# Menu tương tác
Write-Host "Chọn phương pháp cài đặt:" -ForegroundColor Yellow
Write-Host "1. Chocolatey (Khuyến nghị)" -ForegroundColor Cyan
Write-Host "2. Windows Package Manager (winget)" -ForegroundColor Cyan
Write-Host "3. Hướng dẫn cài đặt thủ công" -ForegroundColor Cyan
Write-Host "4. Thoát" -ForegroundColor Gray
Write-Host ""

do {
    $choice = Read-Host "Nhập lựa chọn của bạn (1-4)"
    
    switch ($choice) {
        "1" { 
            if (Install-FFmpegChocolatey) { 
                Write-Host "Hoàn tất!" -ForegroundColor Green
                Read-Host "Nhấn Enter để thoát"
                exit 0 
            } else { 
                Write-Host "Cài đặt thất bại. Thử phương pháp khác." -ForegroundColor Red
            }
        }
        "2" { 
            if (Install-FFmpegWinget) { 
                Write-Host "Hoàn tất!" -ForegroundColor Green
                Read-Host "Nhấn Enter để thoát"
                exit 0 
            } else { 
                Write-Host "Cài đặt thất bại. Thử phương pháp khác." -ForegroundColor Red
            }
        }
        "3" { 
            Install-FFmpegManual
            Read-Host "Nhấn Enter để thoát"
            exit 0 
        }
        "4" { 
            Write-Host "Thoát..." -ForegroundColor Gray
            exit 0 
        }
        default { 
            Write-Host "Lựa chọn không hợp lệ. Vui lòng chọn 1-4." -ForegroundColor Red 
        }
    }
} while ($true)
