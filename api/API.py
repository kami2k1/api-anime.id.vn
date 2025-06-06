import httpx
class Path:
    def __init__(self):
        self.login = "/api/login"
        self.video_list = "/video/list"
        self.orgin = "/api/orgin"

class API:
    def __init__(self, user, pw):
        self.user, self.pw = user, pw
        self.req = httpx.Client(http2=True)
        self.req.headers = {
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        }
        self.url = "https://anime.id.vn"
        self.path = Path()
        self.key = ""
        self.up = 0
        self.orgin = []
        self.islogin = self.login()

    def login(self):
        try:
            prams = {
                "user": self.user,
                "password": self.pw
            }
            r = self.req.post(self.url + self.path.login, params=prams)
            try:
                r_json = r.json()
            except Exception as e:
                print("Không thể parse JSON:", e)
                print("Nội dung trả về:", r.text)
                return False
            if r_json.get('code') == 0:
                self.key = r_json['data']['api_key']
                self.up = r_json['data']['up']
                self.orgin = r_json['data']['orgin'] 
                return True
            else:
                print(f"Lỗi đăng nhập: {r_json.get('code')}")
        except Exception as e:
            print(e)
        return False

    def get_video_list(self, limit=2, page=1):
        """
        Lấy danh sách video đã upload.
        Trả về dict kết quả hoặc None nếu lỗi.
        """
        params = {
            "limit": limit,
            "page": page,
            "api": self.key
        }
        try:
            r = self.req.get(self.url + self.path.video_list, params=params)
            try:
                r_json = r.json()
            except Exception as e:
                print("Không thể parse JSON:", e)
                print("Nội dung trả về:", r.text)
                return None
            return r_json
        except Exception as e:
            print(e)
            return None

    def update_orgin(self, neworgin):
        """
        Cập nhật danh sách web được nhúng.
        neworgin: list các domain, ví dụ ["http://127.0.0.1", "web2"]
        Trả về dict kết quả hoặc None nếu lỗi.
        """
        params = {
            "api": self.key
        }
        data = {
            "orgin": neworgin
        }
        try:
            r = self.req.post(self.url + self.path.orgin, params=params, json=data)
            try:
                r_json = r.json()
            except Exception as e:
                print("Không thể parse JSON:", e)
                print("Nội dung trả về:", r.text)
                return None
            return r_json
        except Exception as e:
            print(e)
            return None