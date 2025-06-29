import customtkinter as ctk
from PIL import Image
import requests
from io import BytesIO
import threading
import webbrowser
from . import settings
import time
import tkinter.font as tkFont

# Cấu hình font tối ưu cho Windows
def get_best_font():
    """Lấy font tốt nhất có sẵn trên hệ thống"""
    try:
        families = tkFont.families()
        if "Arial" in families:
            return "Arial"
        elif "Segoe UI" in families:
            return "Segoe UI" 
        elif "MS Shell Dlg 2" in families:
            return "MS Shell Dlg 2"
        else:
            return "TkDefaultFont"
    except:
        return "Arial"

# Font chính cho ứng dụng
MAIN_FONT = get_best_font()

class VideoManagerFrame(ctk.CTkFrame):
    def __init__(self, parent, api):
        super().__init__(parent)
        self.api = api
        self.parent = parent 
        
        # Cache để tối ưu hiệu suất
        self.thumbnail_cache = {}
        self.max_cache_size = 50
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar and main container
        self.sidebar = Sidebar(self, self.show_videos, self.show_settings, self.show_upload, self.show_settingsz)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.main_container = ctk.CTkFrame(self)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Initialize frames
        self.upload_frame = None
        self.video_frame = None
        self.settings_frame = None
        self.set = None
        
        # Loading state để tránh treo app
        self.is_loading = False
        
        # Show videos với loading animation
        self.show_videos()

    def clear_thumbnail_cache(self):
        """Xóa cache thumbnail để tiết kiệm memory"""
        if len(self.thumbnail_cache) > self.max_cache_size:
            # Xóa một nửa cache cũ nhất
            items = list(self.thumbnail_cache.items())
            for i in range(len(items) // 2):
                del self.thumbnail_cache[items[i][0]]

    def show_videos(self):
        """Hiển thị danh sách video với loading animation"""
        if self.is_loading:
            return
            
        self.clear_main()
        
        # Hiển thị loading screen với animation
        self.show_loading_screen("🎬 Đang tải danh sách video...")
        
        # Load videos trong thread riêng để không block UI
        self.is_loading = True
        thread = threading.Thread(target=self._load_videos_background, daemon=True)
        thread.start()

    def _load_videos_background(self):
        """Load videos trong background thread"""
        try:
            # Load data thực từ API trước
            params = {"limit": 50, "page": 1}
            result = self.api.get_video_list(**params)
            
            # Chuyển về main thread để tạo UI với data đã load
            self.after(0, lambda: self._on_videos_loaded(result))
            
        except Exception as e:
            print(f"Lỗi khi tải video: {e}")
            self.after(0, lambda: self._on_videos_error(str(e)))

    def _on_videos_loaded(self, videos_data):
        """Callback khi videos đã được load xong"""
        self.is_loading = False
        self.clear_main()
        
        # Tạo video frame trong main thread với data đã load
        if self.video_frame is None:
            self.video_frame = VideoListFrame(self.main_container, self.api, self.parent, videos_data)
        else:
            # Update data nếu frame đã tồn tại
            self.video_frame.update_videos_data(videos_data)
        self.video_frame.grid(row=0, column=0, sticky="nsew")

    def _on_videos_error(self, error_message):
        """Callback khi có lỗi load videos"""
        self.is_loading = False
        self.clear_main()
        
        # Hiển thị error frame với nút retry
        error_frame = ctk.CTkFrame(self.main_container, fg_color="#18191A")
        error_frame.grid(row=0, column=0, sticky="nsew")
        error_frame.grid_rowconfigure(0, weight=1)
        error_frame.grid_columnconfigure(0, weight=1)
        
        error_container = ctk.CTkFrame(error_frame, fg_color="#23272F", corner_radius=20)
        error_container.grid(row=0, column=0)
        
        ctk.CTkLabel(
            error_container,
            text="❌ Lỗi tải video",
            font=(MAIN_FONT, 18, "bold"),
            text_color="#FF6B6B"
        ).grid(row=0, column=0, padx=30, pady=(30, 10))
        
        ctk.CTkLabel(
            error_container,
            text=error_message,
            font=(MAIN_FONT, 12),
            text_color="#AAA",
            wraplength=300
        ).grid(row=1, column=0, padx=30, pady=(0, 20))
        
        ctk.CTkButton(
            error_container,
            text="🔄 Thử lại",
            command=self.show_videos,
            fg_color="#00BFFF",
            hover_color="#0099CC",
            font=(MAIN_FONT, 14, "bold")
        ).grid(row=2, column=0, padx=30, pady=(0, 30))

    def show_loading_screen(self, message="Đang tải..."):
        """Hiển thị màn hình loading với animation đẹp"""
        loading_frame = ctk.CTkFrame(self.main_container, fg_color="#18191A")
        loading_frame.grid(row=0, column=0, sticky="nsew")
        loading_frame.grid_rowconfigure(0, weight=1)
        loading_frame.grid_columnconfigure(0, weight=1)
        
        # Loading container với shadow effect
        loading_container = ctk.CTkFrame(loading_frame, fg_color="#23272F", corner_radius=20)
        loading_container.grid(row=0, column=0)
        
        # Animated loading spinner
        self.loading_progress = ctk.CTkProgressBar(
            loading_container,
            width=280,
            height=12,
            mode="indeterminate",
            progress_color="#00BFFF",
            fg_color="#2C2F36"
        )
        self.loading_progress.grid(row=0, column=0, padx=40, pady=(40, 20))
        self.loading_progress.start()
        
        # Loading icon với animation
        self.loading_label = ctk.CTkLabel(
            loading_container,
            text="📺",
            font=(MAIN_FONT, 50)
        )
        self.loading_label.grid(row=1, column=0, padx=40, pady=(0, 15))
        
        # Loading text
        ctk.CTkLabel(
            loading_container,
            text=message,
            font=(MAIN_FONT, 18, "bold"),
            text_color="#00BFFF"
        ).grid(row=2, column=0, padx=40, pady=(0, 10))
        
        # Loading hint
        ctk.CTkLabel(
            loading_container,
            text="Vui lòng chờ trong giây lát...",
            font=(MAIN_FONT, 12),
            text_color="#888"
        ).grid(row=3, column=0, padx=40, pady=(0, 40))
        
        # Animate loading icon
        self._animate_loading_icon()

    def _animate_loading_icon(self):
        """Animate loading icon với rotating effect"""
        if hasattr(self, 'loading_label') and self.loading_label.winfo_exists():
            icons = ["📺", "📹", "🎬", "🎭", "🎪", "🎨", "🎯", "🎮"]
            current_icon = getattr(self, '_current_icon_index', 0)
            
            if hasattr(self, 'loading_label'):
                try:
                    self.loading_label.configure(text=icons[current_icon])
                    self._current_icon_index = (current_icon + 1) % len(icons)
                    
                    # Continue animation nếu vẫn đang loading
                    if self.is_loading:
                        self.after(400, self._animate_loading_icon)
                except:
                    pass

    def show_settings(self):
        """Hiển thị settings frame với animation"""
        self.clear_main()
        
        # Hiển thị loading ngắn cho smooth transition
        self.show_loading_screen("⚙️ Đang mở cài đặt...")
        
        def load_settings():
            time.sleep(0.3)  # Brief loading for smooth transition
            self.after(0, self._show_settings_frame)
        
        threading.Thread(target=load_settings, daemon=True).start()
    
    def _show_settings_frame(self):
        """Hiển thị settings frame"""
        self.clear_main()
        if self.settings_frame is None:
            self.settings_frame = SettingsFrame(self.main_container, self.api, self.on_save)
        self.settings_frame.grid(row=0, column=0, sticky="nsew")
        
    def on_save(self):
        """Callback khi save settings"""
        print("Settings saved!")
        
    def show_settingsz(self):
        """Hiển thị FFmpeg settings"""
        self.clear_main()
        
        # Hiển thị loading ngắn cho smooth transition
        self.show_loading_screen("🔧 Đang mở FFmpeg settings...")
        
        def load_settings():
            time.sleep(0.3)  # Brief loading for smooth transition
            self.after(0, self._show_ffmpeg_settings)
        
        threading.Thread(target=load_settings, daemon=True).start()
    
    def _show_ffmpeg_settings(self):
        """Hiển thị FFmpeg settings"""
        self.clear_main()
        if self.set is None:
            self.set = settings.SettingsFrame(self.main_container)
        self.set.grid(row=0, column=0, sticky="nsew")
        
    def show_upload(self):
        """Hiển thị upload frame với animation"""
        self.clear_main()
        
        # Hiển thị loading ngắn cho smooth transition
        self.show_loading_screen("⬆️ Đang mở trang upload...")
        
        def load_upload():
            time.sleep(0.3)  # Brief loading for smooth transition
            self.after(0, self._show_upload_frame)
        
        threading.Thread(target=load_upload, daemon=True).start()
    
    def _show_upload_frame(self):
        """Hiển thị upload frame"""
        self.clear_main()
        if self.upload_frame is None:
            from gui.upload import UploadFrame
            self.upload_frame = UploadFrame(self.main_container, self.api)
        self.upload_frame.grid(row=0, column=0, sticky="nsew")

    def clear_main(self):
        """Xóa tất cả widget trong main container"""
        # Stop loading progress nếu đang chạy
        if hasattr(self, 'loading_progress'):
            try:
                self.loading_progress.stop()
            except:
                pass
        
        # Reset loading state
        self.is_loading = False
                
        for widget in self.main_container.winfo_children():
            widget.grid_forget()


class VideoListFrame(ctk.CTkFrame):
    def __init__(self, parent, api, pt, videos_data=None):
        self.pt = pt
        self.search_timer = None
        super().__init__(parent)
        self.api = api
        self.page = 1
        self.limit = 50
        self.search_query = ""
        self.all_videos = []
        self.limit_update_id = None
        self.page_update_id = None

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Videos container with better styling
        self.videos_frame = ctk.CTkScrollableFrame(self, fg_color="#18191A")
        self.videos_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=10)

        # Bottom controls frame with enhanced styling
        controls = ctk.CTkFrame(self, fg_color="#23272F", corner_radius=15)
        controls.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))

        # Left side - Search and Reload
        search_reload_frame = ctk.CTkFrame(controls, fg_color="transparent")
        search_reload_frame.pack(side="left", padx=20, pady=10)

        # Enhanced search entry với font đẹp hơn
        self.search_entry = ctk.CTkEntry(
            search_reload_frame, 
            placeholder_text="🔍 Tìm kiếm video...", 
            width=220,
            height=35,
            font=(MAIN_FONT, 12)
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.update_search)

        # Enhanced reload button
        self.reload_button = ctk.CTkButton(
            search_reload_frame, 
            text="🔄 Reload", 
            command=self.reload_videos, 
            width=90,
            height=35,
            font=(MAIN_FONT, 12, "bold"),
            fg_color="#00BFFF",
            hover_color="#0099CC"
        )
        self.reload_button.pack(side="left", padx=5)

        # Enhanced limit input
        self.limit_entry = ctk.CTkEntry(
            search_reload_frame, 
            placeholder_text="Limit", 
            width=80,
            height=35,
            font=(MAIN_FONT, 12)
        )
        self.limit_entry.pack(side="left", padx=5)
        self.limit_entry.insert(0, str(self.limit))
        self.limit_entry.bind("<KeyRelease>", self.schedule_limit_update)

        # Right side - Pagination
        pagination_frame = ctk.CTkFrame(controls, fg_color="transparent")
        pagination_frame.pack(side="right", padx=20, pady=10)

        # Enhanced page controls
        ctk.CTkButton(
            pagination_frame, 
            text="◀ Prev", 
            command=self.prev_page, 
            width=80,
            height=35,
            font=(MAIN_FONT, 12, "bold"),
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(side="left", padx=5)

        self.page_entry = ctk.CTkEntry(
            pagination_frame, 
            placeholder_text="Page", 
            width=70,
            height=35,
            font=(MAIN_FONT, 12)
        )
        self.page_entry.pack(side="left", padx=5)
        self.page_entry.insert(0, str(self.page))
        self.page_entry.bind("<KeyRelease>", self.schedule_page_update)

        ctk.CTkButton(
            pagination_frame, 
            text="Next ▶", 
            command=self.next_page, 
            width=80,
            height=35,
            font=(MAIN_FONT, 12, "bold"),
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(side="left", padx=5)

        # Load initial data
        if videos_data:
            self.all_videos = videos_data
            self.display_videos(videos_data)
        else:
            self.load_videos()

    def update_videos_data(self, videos_data):
        """Update videos data and refresh display"""
        self.all_videos = videos_data
        self.display_videos(videos_data)

    def load_videos(self):
        params = {"limit": self.limit, "page": self.page}
        try:
            self.all_videos = self.api.get_video_list(**params)
            self.display_videos(self.all_videos)
        except Exception as e:
            print(f"Error loading videos: {e}")

    def display_videos(self, videos):
        # Clear existing videos
        for widget in self.videos_frame.winfo_children():
            widget.destroy()

        if not videos:
            no_videos_label = ctk.CTkLabel(
                self.videos_frame,
                text="📭 Không có video nào",
                font=(MAIN_FONT, 18, "bold"),
                text_color="#666"
            )
            no_videos_label.pack(pady=50)
            return

        # Header with count
        count_header = ctk.CTkFrame(self.videos_frame, fg_color="#23272F", corner_radius=15)
        count_header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            count_header,
            text=f"📺 Hiển thị {len(videos)} video (Trang {self.page})",
            font=(MAIN_FONT, 16, "bold"),
            text_color="#00BFFF"
        ).pack(pady=15)

        # Display video cards
        for video in videos:
            card = VideoCard(self.videos_frame, video)
            card.pack(fill="x", padx=10, pady=8)

    def update_search(self, event=None):
        if self.search_timer:
            self.after_cancel(self.search_timer)
        self.search_timer = self.after(300, self._perform_search)

    def _perform_search(self):
        search_text = self.search_entry.get().strip().lower()
        
        if not search_text:
            self.display_videos(self.all_videos)
            return
            
        filtered_videos = [
            video for video in self.all_videos
            if (search_text in video.get("tile", "").lower() or
                search_text in str(video.get("id", "")) or 
                search_text in str(video.get("data", "")) or
                search_text in video.get("created_at", "").lower())
        ]
        
        self.display_videos(filtered_videos)

    def reload_videos(self):
        self.search_entry.delete(0, 'end')
        self.load_videos()

    def schedule_limit_update(self, event=None):
        if self.limit_update_id:
            self.after_cancel(self.limit_update_id)
        self.limit_update_id = self.after(700, self.update_limit)

    def update_limit(self):
        try:
            new_limit = int(self.limit_entry.get())
            if new_limit > 0:
                self.limit = new_limit
                self.load_videos()
            else:
                print("Limit must be greater than 0")
        except ValueError:
            print("Invalid limit value")

    def schedule_page_update(self, event=None):
        if self.page_update_id:
            self.after_cancel(self.page_update_id)
        self.page_update_id = self.after(700, self.update_page)

    def update_page(self):
        try:
            new_page = int(self.page_entry.get())
            if new_page > 0:
                self.page = new_page
                self.load_videos()
            else:
                print("Page must be greater than 0")
        except ValueError:
            print("Invalid page value")

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.page_entry.delete(0, 'end')
            self.page_entry.insert(0, str(self.page))
            self.load_videos()

    def next_page(self):
        self.page += 1
        self.page_entry.delete(0, 'end')
        self.page_entry.insert(0, str(self.page))
        self.load_videos()


class VideoCard(ctk.CTkFrame):
    def __init__(self, parent, video_data):
        super().__init__(parent, fg_color="#23272F", corner_radius=15)
        self.grid_columnconfigure(1, weight=1)
        self.video_data = video_data
        
        # Info container
        info = ctk.CTkFrame(self, fg_color="transparent") 
        info.grid(row=0, column=0, sticky="nsew", padx=15, pady=12)
        
        # Video details with better formatting
        title = video_data.get('tile', 'Không có tiêu đề')
        duration = video_data.get('time', 0)
        video_id = video_data.get('id', 'N/A')
        created = video_data.get('created_at', 'N/A')
        
        details_text = (
            f"📺 {title}\n"
            f"⏱️ Thời lượng: {duration}s\n"
            f"🆔 ID: {video_id}\n"
            f"📅 Tạo: {created}"
        )
        
        # Show thumbnail and info side by side
        thumb_frame = ctk.CTkFrame(info, width=240, height=135, corner_radius=10)
        thumb_frame.grid(row=0, column=0, padx=(0,15))
        thumb_frame.grid_propagate(False)
        
        # Load thumbnail với cache
        thumb_url = video_data.get("thumb", {}).get("1080")
        if thumb_url:
            try:
                response = requests.get(thumb_url, timeout=5)
                img = Image.open(BytesIO(response.content))
                photo = ctk.CTkImage(img, size=(240, 135))
                ctk.CTkLabel(thumb_frame, image=photo, text="").place(relx=0.5, rely=0.5, anchor="center")
            except:
                ctk.CTkLabel(
                    thumb_frame, 
                    text="🖼️\nKhông có ảnh", 
                    font=(MAIN_FONT, 14),
                    text_color="#666"
                ).place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(
                thumb_frame, 
                text="🖼️\nKhông có ảnh", 
                font=(MAIN_FONT, 14),
                text_color="#666"
            ).place(relx=0.5, rely=0.5, anchor="center")

        # Text info next to thumbnail
        text_info = ctk.CTkLabel(
            info,
            text=details_text,
            font=(MAIN_FONT, 13),
            justify="left",
            text_color="#E0E0E0"
        )
        text_info.grid(row=0, column=1, sticky="nw")
        
        # Actions on right side with enhanced styling
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e", padx=15, pady=12)
        
        # Play button
        if video_data.get("link"):
            ctk.CTkButton(
                actions,
                text="▶️ Play",
                command=lambda: webbrowser.open(video_data.get("link", "")),
                width=110,
                height=35,
                font=(MAIN_FONT, 12, "bold"),
                fg_color="#4CAF50",
                hover_color="#45A049"
            ).grid(row=0, column=0, pady=3)
        
        # Copy link buttons
        link1 = video_data.get("link", "")
        link2 = video_data.get("link2", "")
        
        if link1:
            ctk.CTkButton(
                actions,
                text="📋 Link 1",
                command=lambda: self.copy_text(link1),
                width=110,
                height=35,
                font=(MAIN_FONT, 12, "bold"),
                fg_color="#00BFFF",
                hover_color="#0099CC"
            ).grid(row=1, column=0, pady=3)
        
        if link2 and len(link2) > 5:
            ctk.CTkButton(
                actions,
                text="📋 Link 2",
                command=lambda: self.copy_text(link2),
                width=110,
                height=35,
                font=(MAIN_FONT, 12, "bold"),
                fg_color="#FF9800",
                hover_color="#F57C00"
            ).grid(row=2, column=0, pady=3)

    def copy_text(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        print(f"✅ Đã copy: {text[:50]}...")


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, show_videos_callback, show_settings_callback, show_upload_callback, show_ffmpeg_info):
        super().__init__(parent, width=220, fg_color="#23272F")
        self.parent = parent
        self.grid_propagate(False)
        self.api = parent.api
        
        # Header với styling đẹp hơn
        header_frame = ctk.CTkFrame(self, fg_color="#2C2F36", corner_radius=15)
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header_frame,
            text="🎬 MENU",
            font=(MAIN_FONT, 18, "bold"),
            text_color="#00BFFF"
        ).pack(pady=15)
        
        # Enhanced menu buttons với màu sắc phân biệt
        buttons = [
            ("📺 Videos", show_videos_callback, "#00BFFF"),
            ("⬆️ Upload", show_upload_callback, "#4CAF50"),
            ("⚙️ Settings", show_settings_callback, "#FF9800"),
            ("🔧 FFmpeg", show_ffmpeg_info, "#9C27B0"),
            ("🔑 API Key", self.show_token, "#F44336")
        ]
        
        for i, (text, command, color) in enumerate(buttons):
            btn = ctk.CTkButton(
                self,
                text=text,
                command=command,
                width=180,
                height=45,
                font=(MAIN_FONT, 14, "bold"),
                fg_color=color,
                hover_color=self._darken_color(color),
                corner_radius=10
            )
            btn.grid(row=i+1, column=0, padx=15, pady=8)
            
        # Github button với styling đặc biệt
        github_btn = ctk.CTkButton(
            self,
            text="💻 GitHub",
            command=lambda: webbrowser.open("https://github.com"),
            width=180,
            height=45,
            font=(MAIN_FONT, 14, "bold"),
            fg_color="#6366F1",
            hover_color="#5B5CDB",
            corner_radius=10
        )
        github_btn.grid(row=len(buttons)+1, column=0, padx=15, pady=(30, 15))

    def _darken_color(self, color):
        """Tạo màu tối hơn cho hover effect"""
        color_map = {
            "#00BFFF": "#0099CC",
            "#4CAF50": "#45A049", 
            "#FF9800": "#F57C00",
            "#9C27B0": "#7B1FA2",
            "#F44336": "#D32F2F",
            "#6366F1": "#5B5CDB"
        }
        return color_map.get(color, color)

    def show_token(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("🔑 API Key")
        dialog.geometry("450x180")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        ctk.CTkLabel(
            dialog, 
            text="🔑 Your API Key", 
            font=(MAIN_FONT, 18, "bold"),
            text_color="#00BFFF"
        ).pack(pady=(20, 10))
        
        # API key display
        key_frame = ctk.CTkFrame(dialog, fg_color="#23272F", corner_radius=10)
        key_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            key_frame, 
            text=self.api.key, 
            font=("Courier New", 12),
            text_color="#E0E0E0"
        ).pack(pady=15, padx=15)
        
        # Copy button
        ctk.CTkButton(
            dialog, 
            text="📋 Copy to Clipboard", 
            command=lambda: self.copy_text(self.api.key),
            font=(MAIN_FONT, 12, "bold"),
            fg_color="#00BFFF",
            hover_color="#0099CC"
        ).pack(pady=10)
        
    def copy_text(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        print(f"✅ Đã copy API key!")


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, api, on_save):
        super().__init__(parent, fg_color="#18191A")
        self.api = api
        
        # Header với styling đẹp
        header = ctk.CTkFrame(self, fg_color="#23272F", corner_radius=18)
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        ctk.CTkLabel(
            header, 
            text="📊 Cấu Hình Origin", 
            font=(MAIN_FONT, 24, "bold"),
            text_color="#00BFFF"
        ).pack(pady=20)
        
        # Description
        desc_frame = ctk.CTkFrame(self, fg_color="#2C2F36", corner_radius=15)
        desc_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(
            desc_frame,
            text="💡 Mỗi dòng là một website được phép nhúng video",
            font=(MAIN_FONT, 14),
            text_color="#AAA"
        ).pack(pady=15)
        
        # Main content area
        content_frame = ctk.CTkFrame(self, fg_color="#23272F", corner_radius=18)
        content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Textbox với styling đẹp hơn
        self.origins = ctk.CTkTextbox(
            content_frame, 
            height=300,
            font=("Consolas", 13),
            fg_color="#2C2F36",
            corner_radius=10
        )
        self.origins.pack(fill="both", expand=True, padx=20, pady=20)
        self.origins.insert("1.0", "\n".join(self.api.orgin))
        
        # Save button với styling đẹp
        ctk.CTkButton(
            content_frame, 
            text="💾 Lưu Cấu Hình", 
            command=self.save,
            font=(MAIN_FONT, 16, "bold"),
            fg_color="#4CAF50",
            hover_color="#45A049",
            height=45
        ).pack(pady=(0, 20))

    def save(self):
        origins = [o.strip() for o in self.origins.get("1.0", "end-1c").split("\n") if o.strip()]
        threading.Thread(target=lambda: self.api.update_orgin(origins), daemon=True).start()
        print("✅ Đã lưu cấu hình origin!")
