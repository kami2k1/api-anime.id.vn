# Hướng dẫn cài đặt FFmpeg

## Tổng quan
FFmpeg là một thư viện mã nguồn mở dùng để xử lý âm thanh và video. Ứng dụng này cần FFmpeg để:
- Tạo thumbnail từ video
- Chuyển đổi video sang nhiều độ phân giải khác nhau
- Tạo luồng HLS để phát video trực tuyến

## Cài đặt FFmpeg trên Windows

### Phương pháp 1: Tải trực tiếp (Khuyến nghị)

1. **Truy cập trang chính thức:**
   - Vào https://ffmpeg.org/download.html
   - Chọn "Windows" 
   - Chọn "Windows builds by BtbN" hoặc "Windows builds from gyan.dev"

2. **Tải về:**
   - Tải file zip (chọn phiên bản "release" mới nhất)
   - Giải nén vào thư mục như `C:\ffmpeg`

3. **Thêm vào PATH:**
   - Mở "Environment Variables" (tìm trong Start Menu)
   - Trong "System Variables", tìm biến "Path" và nhấn "Edit"
   - Nhấn "New" và thêm đường dẫn `C:\ffmpeg\bin`
   - Nhấn "OK" để lưu

4. **Kiểm tra cài đặt:**
   - Mở Command Prompt hoặc PowerShell
   - Gõ `ffmpeg -version`
   - Nếu thấy thông tin phiên bản FFmpeg thì đã cài đặt thành công

### Phương pháp 2: Sử dụng Chocolatey

1. **Cài đặt Chocolatey** (nếu chưa có):
   - Mở PowerShell với quyền Administrator
   - Chạy: `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`

2. **Cài đặt FFmpeg:**
   - Chạy: `choco install ffmpeg`

### Phương pháp 3: Sử dụng Windows Package Manager (winget)

1. **Cài đặt bằng winget:**
   - Mở Command Prompt hoặc PowerShell
   - Chạy: `winget install ffmpeg`

## Kiểm tra cài đặt

Sau khi cài đặt, hãy:
1. Khởi động lại ứng dụng
2. Thử chọn một file video để kiểm tra
3. Nếu vẫn thấy cảnh báo, hãy khởi động lại máy tính

## Xử lý sự cố

### FFmpeg không được nhận diện
- Đảm bảo đã thêm đúng đường dẫn vào PATH
- Khởi động lại Command Prompt/PowerShell
- Khởi động lại ứng dụng

### Lỗi quyền truy cập
- Chạy Command Prompt với quyền Administrator
- Đảm bảo thư mục FFmpeg không bị chặn bởi antivirus

### Video không được xử lý
- Kiểm tra định dạng video có được FFmpeg hỗ trợ
- Thử với file video khác
- Kiểm tra đường dẫn file không chứa ký tự đặc biệt

## Liên hệ hỗ trợ

Nếu gặp vấn đề trong quá trình cài đặt, vui lòng:
1. Kiểm tra kỹ các bước trên
2. Thử khởi động lại máy tính
3. Liên hệ qua GitHub Issues nếu vẫn không giải quyết được
