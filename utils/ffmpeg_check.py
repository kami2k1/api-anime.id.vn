import subprocess
import customtkinter as ctk
import threading
import webbrowser
from tkinter import messagebox

def check_ffmpeg_installed():
    """
    Kiểm tra xem FFmpeg có được cài đặt trong hệ thống không
    Returns: True nếu FFmpeg có sẵn, False nếu không
    """
    try:
        # Thử chạy ffmpeg với flag version
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5,
                              creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return False

class FFmpegWarningDialog:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
        
    def show_warning(self):
        """Hiển thị dialog cảnh báo FFmpeg không được tìm thấy"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Cảnh báo - FFmpeg không tìm thấy")
        self.dialog.geometry("500x350")
        self.dialog.resizable(False, False)
        
        # Đặt dialog ở giữa màn hình
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Icon cảnh báo (sử dụng emoji)
        icon_label = ctk.CTkLabel(self.dialog, text="⚠️", font=("Arial", 40))
        icon_label.pack(pady=20)
        
        # Tiêu đề
        title_label = ctk.CTkLabel(self.dialog, 
                                 text="FFmpeg Không Được Tìm Thấy", 
                                 font=("Arial", 18, "bold"),
                                 text_color="orange")
        title_label.pack(pady=(0, 10))
        
        # Nội dung cảnh báo
        message_text = """Ứng dụng cần FFmpeg để xử lý video và tạo thumbnail.

Vui lòng cài đặt FFmpeg trước khi sử dụng tính năng upload video.

Bạn có thể tải FFmpeg từ trang web chính thức."""
        
        message_label = ctk.CTkLabel(self.dialog, 
                                   text=message_text,
                                   font=("Arial", 12),
                                   justify="center",
                                   wraplength=400)
        message_label.pack(pady=10, padx=20)
        
        # Frame cho các nút
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(pady=20, fill="x", padx=20)
        
        # Nút tải FFmpeg
        download_btn = ctk.CTkButton(button_frame, 
                                   text="Tải FFmpeg",
                                   command=self.open_ffmpeg_download,
                                   fg_color="green",
                                   hover_color="darkgreen")
        download_btn.pack(side="left", padx=(0, 5), expand=True, fill="x")
        
        # Nút cài đặt tự động
        auto_install_btn = ctk.CTkButton(button_frame,
                                       text="Cài đặt tự động",
                                       command=self.run_auto_installer,
                                       fg_color="blue", 
                                       hover_color="darkblue")
        auto_install_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        # Nút tiếp tục
        continue_btn = ctk.CTkButton(button_frame,
                                   text="Đóng", 
                                   command=self.close_dialog,
                                   fg_color="gray",
                                   hover_color="darkgray")
        continue_btn.pack(side="right", padx=(5, 0), expand=True, fill="x")
        
        # Focus vào dialog
        self.dialog.focus()
        
        # Thêm protocol để đóng dialog khi nhấn X
        self.dialog.protocol("WM_DELETE_WINDOW", self.close_dialog)
        
    def open_ffmpeg_download(self):
        """Mở trang download FFmpeg"""
        webbrowser.open("https://ffmpeg.org/download.html")
        self.close_dialog()  # Đóng dialog sau khi mở trang web
        
    def run_auto_installer(self):
        """Chạy script cài đặt tự động FFmpeg"""
        import subprocess
        import os
        
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "install_ffmpeg.ps1")
        if os.path.exists(script_path):
            try:
                # Chạy PowerShell script với quyền admin
                subprocess.Popen([
                    "powershell.exe", 
                    "-ExecutionPolicy", "Bypass",
                    "-File", script_path
                ], creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                # Thông báo cho user
                messagebox.showinfo(
                    "Đang cài đặt FFmpeg",
                    "Script cài đặt tự động đã được mở trong cửa sổ mới.\n\n"
                    "Vui lòng làm theo hướng dẫn trong cửa sổ PowerShell.\n"
                    "Sau khi cài đặt xong, khởi động lại ứng dụng."
                )
                self.close_dialog()  # Đóng dialog sau khi chạy installer
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể chạy script cài đặt: {str(e)}")
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy script cài đặt tự động.")
        
    def close_dialog(self):
        """Đóng dialog"""
        if self.dialog:
            self.dialog.destroy()
            self.dialog = None

def check_and_warn_ffmpeg(parent_window):
    """
    Kiểm tra FFmpeg và hiển thị cảnh báo nếu cần
    Args:
        parent_window: Cửa sổ cha để hiển thị dialog
    """
    def check_in_thread():
        if not check_ffmpeg_installed():
            # Chạy dialog trong main thread
            parent_window.after(0, lambda: FFmpegWarningDialog(parent_window).show_warning())
    
    # Chạy kiểm tra trong background thread để không block UI
    thread = threading.Thread(target=check_in_thread, daemon=True)
    thread.start()
