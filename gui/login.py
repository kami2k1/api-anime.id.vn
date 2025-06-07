import customtkinter as ctk

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, on_login , data : dict):
        super().__init__(parent)
        self.on_login = on_login

        # Nền đen
        self.configure(fg_color="#18191A")

        # Căn giữa card đăng nhập
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Card-style login frame với bo góc và màu đen
        self.login_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#23272F")
        self.login_frame.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        self.login_frame.grid_rowconfigure((0,1,2,3,4,5), weight=0)
        self.login_frame.grid_columnconfigure(0, weight=1)

        # Tiêu đề đăng nhập
        self.title = ctk.CTkLabel(
            self.login_frame, 
            text="Đăng nhập quản lý Anime",
            font=("Segoe UI", 28, "bold"),
            text_color="#00BFFF"
        )
        self.title.grid(row=0, column=0, padx=20, pady=(30, 10))

        # Ô nhập tên đăng nhập
        self.username_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Tên đăng nhập",
            width=260,
            height=38,
            font=("Segoe UI", 14),
            corner_radius=10,
            fg_color="#18191A",
            text_color="#F5F6FA",
            placeholder_text_color="#888"
        )
        self.username_entry.grid(row=1, column=0, padx=30, pady=(10, 0))

        # Ô nhập mật khẩu
        self.password_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Mật khẩu",
            show="●",
            width=260,
            height=38,
            font=("Segoe UI", 14),
            corner_radius=10,
            fg_color="#18191A",
            text_color="#F5F6FA",
            placeholder_text_color="#888"
        )
        self.password_entry.grid(row=2, column=0, padx=30, pady=(15, 0))

        # Nút đăng nhập
        self.login_button = ctk.CTkButton(
            self.login_frame,
            text="Đăng nhập",
            command=self._handle_login,
            width=260,
            height=40,
            font=("Segoe UI", 16, "bold"),
            fg_color="#00BFFF",
            text_color="#18191A",
            hover_color="#0099CC",
            corner_radius=12
        )
        self.login_button.grid(row=3, column=0, padx=30, pady=(30, 20))

        # Tự động điền nếu có dữ liệu
        if "user" in data:
            self.username_entry.insert(0, data['user'])
        if "pw" in data:
            self.password_entry.insert(0, data['pw'])

    def _handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.on_login(username, password)