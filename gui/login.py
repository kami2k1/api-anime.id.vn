import customtkinter as ctk

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, on_login , data : dict):
        super().__init__(parent)
        self.on_login = on_login
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create login container
        self.login_frame = ctk.CTkFrame(self, corner_radius=15)
        self.login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Login title
        self.title = ctk.CTkLabel(
            self.login_frame, 
            text="Anime Manager Login",
            font=("Arial", 20, "bold")
        )
        self.title.grid(row=0, column=0, padx=20, pady=(20, 0))

        # Username
        self.username_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Username",
            width=200
        )
        self.username_entry.grid(row=1, column=0, padx=20, pady=(20, 0))

        # Password
        self.password_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Password",
            show="●",
            width=200
        )
        self.password_entry.grid(row=2, column=0, padx=20, pady=(20, 0))

        # Login button
        self.login_button = ctk.CTkButton(
            self.login_frame,
            text="Đăng Nhập",
            command=self._handle_login,
            width=200
        )
        self.login_button.grid(row=3, column=0, padx=20, pady=20)
        
        if "user" in data:
            self.username_entry.insert(0, data['user'])  # Insert the username into the entry field
        if "pw" in data:
            self.password_entry.insert(0, data['pw'])  # Insert the password into the entry field

    def _handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.on_login(username, password)