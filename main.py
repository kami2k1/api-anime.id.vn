import customtkinter as ctk
from gui.login import LoginFrame 
from gui.video_manager import VideoManagerFrame
from api.API import API 
from api import data

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Quản Lý video anime.id.vn")
        self.geometry("1280x720")  # 16:9 ratio
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.data  = data.load()
        # Start with login
        self.show_login()
        
    def show_login(self):
        self.clear_window()
        self.login_frame = LoginFrame(self, self.handle_login, self.data)
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        
    def show_manager(self, api):
        self.clear_window()
        self.manager_frame = VideoManagerFrame(self, api)
        self.manager_frame.grid(row=0, column=0, sticky="nsew")
        
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
            
    def handle_login(self, username, password):
        api = API(username, password)
        if api.islogin:
            self.data['user'] = username
            self.data['pw'] = password
            data.save(self.data)
                
            self.show_manager(api)
        else:
             if hasattr(self, "error_label"):
                 self.error_label.configure(text="Login failed. Please check your credentials.")
             else:
                 # Tạo label lỗi và sử dụng grid để hiển thị
                 self.error_label = ctk.CTkLabel(self, text="Login failed. Please check your credentials.", text_color="red")
                 self.error_label.grid(row=2, column=0, pady=10, sticky="w")  # Điều chỉnh vị trí phù hợp

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue") 
    app = App()
    app.mainloop()