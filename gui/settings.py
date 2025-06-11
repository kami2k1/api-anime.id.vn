import customtkinter as ctk
import threading
import webbrowser
from tkinter import messagebox
from utils.ffmpeg_check import check_ffmpeg_installed, FFmpegWarningDialog
from utils.app_config import app_config

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Nền đen
        self.configure(fg_color="#18191A")
        
        # Cấu hình lưới
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkFrame(self, fg_color="#23272F", corner_radius=18)
        header.grid(row=0, column=0, sticky="ew", padx=40, pady=(30, 0))
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header, 
            text="Cài đặt hệ thống", 
            font=("Segoe UI", 28, "bold"),
            text_color="#00BFFF"
        ).grid(row=0, column=0, sticky="w", pady=18, padx=30)
        
        # Main content
        content = ctk.CTkFrame(self, fg_color="#23272F", corner_radius=18)
        content.grid(row=1, column=0, sticky="ew", padx=40, pady=20)
        content.grid_columnconfigure(1, weight=1)
        
        # FFmpeg Section
        ffmpeg_section = ctk.CTkFrame(content, fg_color="#2C2F36", corner_radius=12)
        ffmpeg_section.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        ffmpeg_section.grid_columnconfigure(1, weight=1)
        
        # FFmpeg status
        ctk.CTkLabel(
            ffmpeg_section, 
            text="🎬 FFmpeg", 
            font=("Segoe UI", 16, "bold"),
            text_color="#00BFFF"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.ffmpeg_status_label = ctk.CTkLabel(
            ffmpeg_section,
            text="Đang kiểm tra...",
            font=("Segoe UI", 12),
            text_color="#888"
        )
        self.ffmpeg_status_label.grid(row=0, column=1, sticky="e", padx=20, pady=(15, 5))
        
        # FFmpeg description
        ctk.CTkLabel(
            ffmpeg_section,
            text="FFmpeg cần thiết để xử lý video và tạo thumbnail",
            font=("Segoe UI", 11),
            text_color="#AAA",
            justify="left"
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 10))
        
        # FFmpeg buttons
        ffmpeg_btn_frame = ctk.CTkFrame(ffmpeg_section, fg_color="transparent")
        ffmpeg_btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 15))
        ffmpeg_btn_frame.grid_columnconfigure(1, weight=1)
        
        self.check_ffmpeg_btn = ctk.CTkButton(
            ffmpeg_btn_frame,
            text="Kiểm tra FFmpeg",
            command=self.check_ffmpeg_status,
            fg_color="#00BFFF",
            hover_color="#0099CC",
            font=("Segoe UI", 12, "bold")
        )
        self.check_ffmpeg_btn.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.install_ffmpeg_btn = ctk.CTkButton(
            ffmpeg_btn_frame,
            text="Hướng dẫn cài đặt",
            command=self.show_ffmpeg_guide,
            fg_color="#666",
            hover_color="#555",
            font=("Segoe UI", 12)
        )
        self.install_ffmpeg_btn.grid(row=0, column=1, sticky="w", padx=10)
        
        # App Settings Section
        app_section = ctk.CTkFrame(content, fg_color="#2C2F36", corner_radius=12)
        app_section.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))
        app_section.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            app_section, 
            text="⚙️ Cài đặt ứng dụng", 
            font=("Segoe UI", 16, "bold"),
            text_color="#00BFFF"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
        
        # Reset warnings
        ctk.CTkButton(
            app_section,
            text="Đặt lại cảnh báo",
            command=self.reset_warnings,
            fg_color="#666",
            hover_color="#555",
            font=("Segoe UI", 12)
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))
        
        # Info Section
        info_section = ctk.CTkFrame(content, fg_color="#2C2F36", corner_radius=12)
        info_section.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            info_section, 
            text="ℹ️ Thông tin", 
            font=("Segoe UI", 16, "bold"),
            text_color="#00BFFF"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
        
        info_text = """• FFmpeg: Thư viện xử lý video mã nguồn mở
• Cần thiết để tạo nhiều độ phân giải và thumbnail
• Tải về từ: https://ffmpeg.org/download.html"""
        
        ctk.CTkLabel(
            info_section,
            text=info_text,
            font=("Segoe UI", 11),
            text_color="#AAA",
            justify="left"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))
        
        # Check FFmpeg status on load
        threading.Thread(target=self._check_ffmpeg_threaded, daemon=True).start()
    
    def _check_ffmpeg_threaded(self):
        """Kiểm tra trạng thái FFmpeg trong background thread"""
        is_installed = check_ffmpeg_installed()
        
        # Update UI in main thread
        self.after(0, lambda: self._update_ffmpeg_status(is_installed))
    
    def _update_ffmpeg_status(self, is_installed: bool):
        """Cập nhật trạng thái FFmpeg trên UI"""
        if is_installed:
            self.ffmpeg_status_label.configure(
                text="✅ Đã cài đặt", 
                text_color="#4CAF50"
            )
            self.install_ffmpeg_btn.configure(text="Đã sẵn sáng")
        else:
            self.ffmpeg_status_label.configure(
                text="❌ Chưa cài đặt", 
                text_color="#F44336"
            )
            self.install_ffmpeg_btn.configure(text="Cài đặt ngay")
    
    def check_ffmpeg_status(self):
        """Kiểm tra lại trạng thái FFmpeg"""
        self.ffmpeg_status_label.configure(text="Đang kiểm tra...")
        self.check_ffmpeg_btn.configure(state="disabled")
        
        # Run check in background
        threading.Thread(target=self._recheck_ffmpeg, daemon=True).start()
    
    def _recheck_ffmpeg(self):
        """Kiểm tra lại FFmpeg và cập nhật UI"""
        is_installed = check_ffmpeg_installed()
        
        self.after(0, lambda: [
            self._update_ffmpeg_status(is_installed),
            self.check_ffmpeg_btn.configure(state="normal"),
            messagebox.showinfo(
                "Kết quả kiểm tra",
                "✅ FFmpeg đã được cài đặt!" if is_installed else "❌ FFmpeg chưa được cài đặt"
            )
        ])
    
    def show_ffmpeg_guide(self):
        """Hiển thị hướng dẫn cài đặt FFmpeg"""
        if check_ffmpeg_installed():
            messagebox.showinfo(
                "FFmpeg đã sẵn sàng",
                "FFmpeg đã được cài đặt và sẵn sàng sử dụng!"
            )
        else:
            # Hiển thị dialog cài đặt
            FFmpegWarningDialog(self).show_warning()
    
    def reset_warnings(self):
        """Đặt lại tất cả cảnh báo"""
        app_config.set_ffmpeg_warning_shown(False)
        app_config.set_ffmpeg_checked(False)
        
        messagebox.showinfo(
            "Đặt lại hoàn tất",
            "Tất cả cảnh báo đã được đặt lại.\n"
            "Ứng dụng sẽ hiển thị lại các cảnh báo khi khởi động lần tiếp theo."
        )