import json
import os
from typing import Dict, Any

class AppConfig:
    """Quản lý cấu hình ứng dụng"""
    
    def __init__(self, config_file: str = "app_settings.json"):
        self.config_file = config_file
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Tải cài đặt từ file"""
        default_settings = {
            "ffmpeg_checked": False,
            "ffmpeg_warning_shown": False,
            "last_upload_folder": "",
            "default_create_lower_res": True,
            "default_use_gpu": False,
            "theme": "dark",
            "language": "vi"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge với default settings để đảm bảo có đầy đủ keys
                    default_settings.update(loaded_settings)
            except (json.JSONDecodeError, IOError):
                pass
        
        return default_settings
    
    def save_settings(self):
        """Lưu cài đặt vào file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
    
    def get(self, key: str, default=None) -> Any:
        """Lấy giá trị cài đặt"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Đặt giá trị cài đặt"""
        self.settings[key] = value
        self.save_settings()
    
    def get_ffmpeg_checked(self) -> bool:
        """Kiểm tra xem FFmpeg đã được kiểm tra chưa"""
        return self.get("ffmpeg_checked", False)
    
    def set_ffmpeg_checked(self, checked: bool):
        """Đặt trạng thái kiểm tra FFmpeg"""
        self.set("ffmpeg_checked", checked)
    
    def get_ffmpeg_warning_shown(self) -> bool:
        """Kiểm tra xem cảnh báo FFmpeg đã được hiển thị chưa"""
        return self.get("ffmpeg_warning_shown", False)
    
    def set_ffmpeg_warning_shown(self, shown: bool):
        """Đặt trạng thái hiển thị cảnh báo FFmpeg"""
        self.set("ffmpeg_warning_shown", shown)

# Instance toàn cục
app_config = AppConfig()
