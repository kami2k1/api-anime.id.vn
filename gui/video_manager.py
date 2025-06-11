import customtkinter as ctk
from PIL import Image
import requests
from io import BytesIO
import threading
import webbrowser
from . import settings

class VideoManagerFrame(ctk.CTkFrame):
    def __init__(self, parent, api):
        super().__init__(parent)
        self.api = api
        self.parent = parent 
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar and main container
        self.sidebar = Sidebar(self, self.show_videos, self.show_settings, self.show_upload,self.show_settingsz)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.upload_frame = None  # Khởi tạo upload_frame nếu chưa có
        self.main_container = ctk.CTkFrame(self)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.video_frame = None  # Khởi tạo video_frame nếu chưa có
        self.settings_frame = None  # Khởi tạo settings_frame nếu chưa có
        # self.content_frame = ctk.CTkFrame(self)  # Tạo content_frame nếu chưa có
        # self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)


        self.set = None  # Khởi tạo set nếu chưa có
        self.show_videos()
  # Hiển thị lại màn hình đăng nhập

    def show_videos(self):
        self.clear_main()
        if self.video_frame is None:
            self.video_frame = VideoListFrame(self.main_container, self.api, self.parent)
        self.video_frame.grid(row=0, column=0, sticky="nsew")

    def show_settings(self):
        self.clear_main()
        if self.settings_frame is None:
             self.settings_frame = SettingsFrame(self.main_container, self.api, self.show_videos)
        self.settings_frame.grid(row=0, column=0, sticky="nsew")
    def show_settingsz(self):
        self.clear_main()
        if self.set is None:
            self.set = settings.SettingsFrame(self.main_container)
        self.set.grid(row=0, column=0, sticky="nsew")
    def show_upload(self):
        self.clear_main()
        if self.upload_frame is None:
            from gui.upload import UploadFrame
            self.upload_frame = UploadFrame(self.main_container, self.api)
        self.upload_frame.grid(row=0, column=0, sticky="nsew")

    def clear_main(self):
        for widget in self.main_container.winfo_children():
            widget.grid_forget()

class VideoListFrame(ctk.CTkFrame):
    def __init__(self, parent, api , pt):
        self.pt = pt
        self.search_timer = None
        super().__init__(parent)
        self.api = api
        self.page = 1
        self.limit = 50
        self.search_query = ""  # Biến lưu nội dung tìm kiếm
        self.all_videos = []  # Lưu toàn bộ dữ liệu video để tìm kiếm
        self.limit_update_id = None  # ID của hàm `after` cho limit
        self.page_update_id = None  # ID của hàm `after` cho page

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Videos container
        self.videos_frame = ctk.CTkScrollableFrame(self)
        self.videos_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        # Bottom controls frame
        controls = ctk.CTkFrame(self)
        controls.grid(row=1, column=0, sticky="e", padx=20, pady=10)
        

        # Left side - Search and Reload
        search_reload_frame = ctk.CTkFrame(controls, fg_color="transparent")
        search_reload_frame.pack(side="left", padx=(0, 20))

        self.search_entry = ctk.CTkEntry(search_reload_frame, placeholder_text="Search...", width=200)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.update_search)  # Cập nhật tìm kiếm khi nhập từng ký tự

        self.reload_button = ctk.CTkButton(search_reload_frame, text="Reload", command=self.reload_videos, width=80)
        self.reload_button.pack(side="left", padx=5)

        # Limit input
        self.limit_entry = ctk.CTkEntry(search_reload_frame, placeholder_text="Limit", width=50)
        self.limit_entry.insert(0, str(self.limit))  # Hiển thị giá trị mặc định
        self.limit_entry.pack(side="left", padx=5)
        self.limit_entry.bind("<KeyRelease>", self.schedule_limit_update)  # Lên lịch cập nhật limit

        # Right side - Page navigation
        nav_frame = ctk.CTkFrame(controls, fg_color="transparent")
        nav_frame.pack(side="left")

        self.prev_btn = ctk.CTkButton(nav_frame, text="<", command=self.prev_page, width=40)
        self.prev_btn.pack(side="left", padx=5)

        self.page_entry = ctk.CTkEntry(nav_frame, width=50)
        self.page_entry.insert(0, str(self.page))  # Hiển thị giá trị mặc định
        self.page_entry.pack(side="left", padx=5)
        self.page_entry.bind("<KeyRelease>", self.schedule_page_update)  # Lên lịch cập nhật page

        self.next_btn = ctk.CTkButton(nav_frame, text=">", command=self.next_page, width=40)
        self.next_btn.pack(side="left", padx=5)

        logout_button = ctk.CTkButton(controls, text="Đăng xuất", command=self.logout, width=80)
        logout_button.pack(side="right", padx=20, pady=10)  # Sử dụng pack thay vì grid

        self.load_videos()
    def logout(self):
        # Xử lý logic đăng xuất
        self.destroy()  # Đóng giao diện hiện tại
        self.pt.show_login()
    def load_videos(self):
        try:
            params = {"limit": self.limit, "page": self.page}
            result = self.api.get_video_list(**params)
            if not result or result.get("code") != 0:
                return

            self.all_videos = result["data"]  # Lưu toàn bộ dữ liệu để tìm kiếm
            self.display_videos(self.all_videos)

        except Exception as e:
            print(f"Error loading videos: {e}")

    def display_videos(self, videos):
        for widget in self.videos_frame.winfo_children():
            widget.destroy()

        self.next_btn.configure(state="normal" if len(videos) >= self.limit else "disabled")
        self.prev_btn.configure(state="normal" if self.page > 1 else "disabled")

        for video in videos:
            VideoCard(self.videos_frame, video).pack(fill="x", pady=5)

    def update_search(self, event=None):
        # Hủy timer trước đó nếu có
        if self.search_timer:
            self.after_cancel(self.search_timer)
        
        # Lên lịch tìm kiếm mới sau 300ms
        self.search_timer = self.after(300, self._perform_search)
    def _perform_search(self):
        search_text = self.search_entry.get().strip().lower()
        
        if not search_text:
            self.display_videos(self.all_videos)
            return
            
        # Dùng list comprehension để tăng hiệu suất
        filtered_videos = [
            video for video in self.all_videos
            if (search_text in video.get("tile", "").lower() or
                search_text in str(video.get("id", "")) or 

                search_text in str(video.get("data", "")) or
                search_text in video.get("created_at", "").lower())
                
        ]
        
        self.display_videos(filtered_videos)

    def reload_videos(self):
        self.search_entry.delete(0, 'end')  # Xóa nội dung tìm kiếm
        self.load_videos()

    def schedule_limit_update(self, event=None):
        if self.limit_update_id:
            self.after_cancel(self.limit_update_id)  # Hủy lịch trình trước đó nếu có
        self.limit_update_id = self.after(700, self.update_limit)  # Lên lịch cập nhật sau 0.7 giây

    def update_limit(self):
        try:
            new_limit = int(self.limit_entry.get())
            if new_limit > 0:  # Đảm bảo giá trị hợp lệ
                self.limit = new_limit
                self.load_videos()  # Tải lại dữ liệu của trang hiện tại
            else:
                print("Limit must be greater than 0")
        except ValueError:
            print("Invalid limit value")

    def schedule_page_update(self, event=None):
        if self.page_update_id:
            self.after_cancel(self.page_update_id)  # Hủy lịch trình trước đó nếu có
        self.page_update_id = self.after(700, self.update_page)  # Lên lịch cập nhật sau 0.7 giây

    def update_page(self):
        try:
            new_page = int(self.page_entry.get())
            if new_page > 0:  # Đảm bảo giá trị hợp lệ
                self.page = new_page
                self.load_videos()  # Tải lại dữ liệu của trang mới
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
        super().__init__(parent)
        self.grid_columnconfigure(1, weight=1)
        self.video_data = video_data
        
        # Info container
        info = ctk.CTkFrame(self, fg_color="transparent") 
        info.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        
        # Video details
        details_text = (
            f"Title: {video_data.get('tile', '')}\n"
            f"Duration: {video_data.get('time', 0)}s\n"
            f"ID: {video_data.get('id', '')}\n"
            f"Data: {video_data.get('data', '')}\n"
            f"Created: {video_data.get('created_at', '')}"
        )
        
        # Show thumbnail and info side by side
        thumb_frame = ctk.CTkFrame(info, width=240, height=135)
        thumb_frame.grid(row=0, column=0, padx=(0,10))
        thumb_frame.grid_propagate(False)
        
        thumb_url = video_data.get("thumb", {}).get("1080")
        if thumb_url:
            try:
                response = requests.get(thumb_url)
                img = Image.open(BytesIO(response.content))
                photo = ctk.CTkImage(img, size=(240, 135))
                ctk.CTkLabel(thumb_frame, image=photo, text="").place(relx=0.5, rely=0.5, anchor="center")
            except:
                ctk.CTkLabel(thumb_frame, text="No Thumbnail").place(relx=0.5, rely=0.5, anchor="center")

        # Text info next to thumbnail
        text_info = ctk.CTkLabel(
            info,
            text=details_text,
            font=("Arial", 12),
            justify="left"
        )
        text_info.grid(row=0, column=1, sticky="w")
        
        # Actions on right side
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=0, column=1, padx=10)
        
        ctk.CTkButton(
            actions,
            text="Play",
            command=lambda: webbrowser.open(video_data.get("link", "")),
            width=100,
            height=30
        ).grid(row=0, column=0, pady=5)
        
        link1 = video_data.get("link", "")
        link2 = video_data.get("link2", "")
        
        if link1:
            ctk.CTkButton(
                actions,
                text="Copy Link 1",
                command=lambda: self.copy_text(link1),
                width=100,
                height=30
            ).grid(row=1, column=0, pady=5)
        
        if link2 and len(link2) > 5:
            ctk.CTkButton(
                actions,
                text="Copy Link 2",
                command=lambda: self.copy_text(link2),
                width=100,
                height=30
            ).grid(row=2, column=0, pady=5)

    def copy_text(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, show_videos_callback, show_settings_callback, show_upload_callback,show_ffmpeg_info):
        super().__init__(parent, width=200)
        self.parent = parent
        self.grid_propagate(False)
        self.api = parent.api
        self.set  = None
        
        buttons = [
            ("Videos", show_videos_callback),
            ("Upload", show_upload_callback),
            ("Origin", show_settings_callback),
            ("Token", self.show_token),
            ("Settings", show_ffmpeg_info)
        ]
        
        for i, (text, command) in enumerate(buttons):
            ctk.CTkButton(self, text=text, command=command, width=160).grid(row=i, column=0, padx=20, pady=10)
        # Thêm nút Github ở dưới cùng
        ctk.CTkButton(
            self,
            text="Github",
            command=lambda: webbrowser.open("https://github.com/kami2k1/api-anime.id.vn"),
            width=160
        ).grid(row=len(buttons), column=0, padx=20, pady=(30,10))

    def show_token(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Your API Key")
        dialog.geometry("400x150")
        
        ctk.CTkLabel(dialog, text=self.api.key, font=("Arial", 14)).pack(pady=20)
        ctk.CTkButton(dialog, text="Copy", command=lambda: self.copy_text(self.api.key)).pack(pady=10)
        
    def copy_text(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, api, on_save):
        super().__init__(parent)
        self.api = api
        
        ctk.CTkLabel(self, text="Cấu Hình Nhúng \n mỗi một dòng  là 1 website", font=("Arial", 16, "bold")).pack(pady=20)
        
        self.origins = ctk.CTkTextbox(self, height=300)
        self.origins.pack(fill="x", padx=20)
        self.origins.insert("1.0", "\n".join(self.api.orgin))
        
        ctk.CTkButton(self, text="Save", command=self.save).pack(pady=20)

    def save(self):
        origins = [o.strip() for o in self.origins.get("1.0", "end-1c").split("\n") if o.strip()]
        threading.Thread(target=lambda: self.api.update_orgin(origins), daemon=True).start()