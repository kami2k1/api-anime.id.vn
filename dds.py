
import subprocess
import sys



required_packages = [
    'ffmpeg-python',  # Thư viện ffmpeg
    'httpx',          # Thư viện httpx
    'PyQt6',          # Thư viện PyQt6
]


def install_missing_packages(packages):
    for package in packages:
        try:
            __import__(package)
            print(f"Package {package} is already installed.")
        except ImportError:
            print(f"Package {package} not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_missing_packages(required_packages)




import os
import sys
import uuid
import asyncio
import subprocess
import shutil
import json

# Third-Party Imports
import ffmpeg
import httpx
from PyQt6.QtWidgets import QApplication, QFileDialog

# Constants
semaphore = asyncio.Semaphore(70)  # Defined but unused in the original code
BANDWIDTH_MAP = {
    2160: 12000000, 1440: 8000000, 1080: 5000000, 720: 2800000,
    480: 1200000, 360: 800000, 240: 500000, 144: 250000
}

# Video Processing Functions
def get_video_info(input_file):
    """
    Lấy thông tin chiều rộng và cao của video bằng ffmpeg.probe.
    
    Args:
        input_file (str): Đường dẫn đến file video đầu vào.
    
    Returns:
        tuple: (width, height) của video.
    
    Raises:
        RuntimeError: Nếu có lỗi khi lấy thông tin video.
    """
    try:
        probe = ffmpeg.probe(input_file)
        video_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
        return int(video_stream["width"]), int(video_stream["height"])
    except Exception as e:
        raise RuntimeError(f"Lỗi lấy thông tin video: {e}")

def get_gpu_encoder():
    """
    Xác định bộ mã hóa GPU tốt nhất có sẵn cho ffmpeg.
    
    Returns:
        str: Tên của bộ mã hóa sẽ sử dụng.
    """
    try:
        output = subprocess.check_output(["ffmpeg", "-encoders"], stderr=subprocess.DEVNULL).decode()
        if "h264_nvenc" in output:
            return "h264_nvenc"  # NVIDIA GPU
        elif "h264_qsv" in output:
            return "h264_qsv"  # Intel QuickSync
        elif "h264_vaapi" in output:
            return "h264_vaapi"  # AMD VAAPI
    except:
        pass
    return "h264"  # CPU

GPU_ENCODER = "h264"
print(f"🔍 Sử dụng encoder: {GPU_ENCODER}")

def create_thumbnails(input_file, output_folder, sizes=[1080, 120, 180, 240, 360, 480, 60, 720], num_thumbs=1):
    """
    Tạo ảnh thumbnails từ video theo các kích thước và thời điểm chỉ định.
    
    Args:
        input_file (str): Đường dẫn đến file video đầu vào.
        output_folder (str): Thư mục để lưu thumbnails.
        sizes (list): Danh sách chiều cao của thumbnails.
        num_thumbs (int): Số lượng thumbnails cần tạo.
    
    Returns:
        dict: Đường dẫn đến các thumbnails đã tạo.
        float: Thời lượng của video.
    """
    os.makedirs(output_folder, exist_ok=True)
    try:
        probe = ffmpeg.probe(input_file)
        duration = float(probe["format"]["duration"])
    except Exception as e:
        raise RuntimeError(f"Lỗi lấy thời lượng video: {e}")
    
    timestamps = [duration * i / (num_thumbs + 1) for i in range(1, num_thumbs + 1)]
    thumb_paths = {}
    for i, timestamp in enumerate(timestamps):
        for size in sizes:
            thumb_path = os.path.join(output_folder, f"{size}p.jpg")
            subprocess.run([
                "ffmpeg", "-ss", str(timestamp), "-i", input_file,
                "-vf", f"scale=-1:{size}", "-frames:v", "1", thumb_path
            ])
            thumb_paths[str(size)] = thumb_path
    return thumb_paths, duration

async def create_hls(input_file, resolutions, original_resolution, output_folder):
    """
    Tạo các luồng HLS cho video theo các độ phân giải chỉ định.
    
    Args:
        input_file (str): Đường dẫn đến file video đầu vào.
        resolutions (list): Danh sách các độ phân giải cần tạo.
        original_resolution (int): Độ phân giải gốc của video.
        output_folder (str): Thư mục để lưu các luồng HLS.
    """
    os.makedirs(output_folder, exist_ok=True)
    tasks = []
    for res in [original_resolution] + resolutions:
        output_file = os.path.join(output_folder, f"{res}p.m3u8")
        command = [
            "ffmpeg", "-hide_banner",
            "-hwaccel", "cuda" if GPU_ENCODER == "h264_nvenc" else "auto",
            "-i", input_file, "-vf", f"scale=-2:{res}", "-c:v", GPU_ENCODER,
            "-b:v", f"{res*5}k", "-hls_time", "3", "-hls_list_size", "0",
            "-map_metadata", "-1",  # Xóa metadata
            "-fflags", "+bitexact",  # Không chèn thông tin FFmpeg
            "-f", "hls", output_file
        ]
        tasks.append(asyncio.create_subprocess_exec(*command))
    
    processes = await asyncio.gather(*tasks)
    await asyncio.gather(*(p.wait() for p in processes))

def create_master_playlist(resolutions, original_resolution, output_folder):
    """
    Tạo playlist HLS chính (master.m3u8).
    
    Args:
        resolutions (list): Danh sách các độ phân giải.
        original_resolution (int): Độ phân giải gốc.
        output_folder (str): Thư mục chứa các luồng HLS.
    """
    with open(os.path.join(output_folder, "master.m3u8"), "w") as f:
        f.write("#EXTM3U\n")
        for res in [original_resolution] + resolutions:
            f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={BANDWIDTH_MAP.get(res, res * 6000)},CODECS=\"mp4a.40.2,avc1.640028\",RESOLUTION={res}p,NAME=\"{res}\"\n")
            f.write(f"{res}p.m3u8\n")

# API Class
class Api:
    def __init__(self, api_key, custumurl="https://phim.click/"):
        self.api = api_key
        self.url = custumurl
        self.upload_url = 'http://127.0.0.1/'
        self.uploadz = "upload"
        self.client = None

    async def getc(self):
        """Khởi tạo client HTTP bất đồng bộ."""
        self.client = httpx.AsyncClient(http2=True)

    def ext(self):
        """Thoát chương trình khi có lỗi upload."""
        print("Lỗi Không thể Upload thoát Chương Trình ")
        sys.exit()

    async def send(self):
        
        """Gửi yêu cầu để lấy URL upload từ server."""
        if not self.client:
            await self.getc()
        d = await self.client.get(f"{self.url}inf?api={self.api}")
        d = d.json()
        
        self.upload_url = d['upload']
        print("Get link sex ")

    async def setorg(self,  data : list  = [], m :int = 0 ):
        url = f"{self.url}/setog?api={self.api}"
        match m :
            
            case 0 : 
                d = await  self.client.get(url)
                return d.json()
            case 1 :
                d = {
                    "data": data
                }
                d = await  self.client.post(url)
                return d.json()


    

    async def upload(self, hls_folder, file_ext, id, batch_size=20, type=1, datadz=None):
        """
        Upload các file theo batch (mỗi batch tối đa 100 file).

        Args:
            hls_folder (str): Thư mục chứa các file cần upload.
            file_ext (str): Phần mở rộng của file (e.g., '.ts', '.m3u8').
            id (int): ID (chưa rõ mục đích, giữ nguyên logic cũ).
            batch_size (int): Số file tối đa mỗi batch.
            type (int): Loại upload (1, 2, hoặc 4).
            datadz: Dữ liệu bổ sung (dùng khi type=2).

        Returns:
            list: Danh sách ID nếu type=4, None nếu type=2.
        """

        # Lấy danh sách các file trong thư mục với phần mở rộng yêu cầu
        all_files = [os.path.join(hls_folder, file_name) for file_name in os.listdir(hls_folder) if file_name.endswith(file_ext)]
        url = f"{self.upload_url}{self.uploadz}?api={self.api}&m=m" if file_ext == ".m3u8" else f"{self.upload_url}{self.uploadz}?api={self.api}"
        print(url)
        if type != 1:
            if not all_files:
                print("Không tìm thấy file phù hợp!")
                return

            dataz = {}
            id_lits = []

            cc ={}
            sned= False
            batches = [all_files[i:i + batch_size] for i in range(0, len(all_files), batch_size)]

           
            async def upload_batch(batch_files, batch_index):
                print(f"Đang upload batch {batch_index + 1}/{len(batches)} với {len(batch_files)} file(s)")
                nonlocal cc , id_lits
                files = [("file", (os.path.basename(f), open(f, "rb"))) for f in batch_files]
                try:
                    if type == 2:
                       
                       
                        files.append(("json", (None, json.dumps(datadz), "application/json")))
                        response = await self.client.post(url, files=files, json=datadz, timeout=600)
                        cc= response.json()
                        return
                     

                    response = await self.client.post(url, files=files, timeout=120)
                    print(f"Đã upload batch {batch_index + 1}/{len(batches)} {response.text}")
                    data = response.json()

                    if data['code'] == 0:
                        if file_ext == ".m3u8":
                            for i, item in data['data'].items():
                                dataz[i] = {"kami": True, "link": f"{self.url}m?id={item}"}
                        else:
                            d = True
                            s = f"{self.upload_url}/ch?api={self.api}&id={data['id']}"
                            id_lits.append(data['id'])
                            
                            while d:
                                response = await self.client.get(s)
                                data = response.json()
                                if data['code'] == 20:
                                    await asyncio.sleep(2)
                                elif data['code'] == 0:
                                    print("Đã Lấy Được data")
                                    d = False
                                else:
                                    print("lỗi ", data)
                                    self.ext()
                    else:
                        print("Lỗi Thoát App")
                        print(response.text)
                        await asyncio.sleep(2)
                        return await upload_batch(batch_files, batch_index)
                except Exception as e:
                    print(f"{response.text}")
                    print(f"Lỗi upload batch {batch_index}: {e}")
                    return await upload_batch(batch_files, batch_index)
                    
                

          
            max_concurrent_uploads = 9999
            tasks = []
            for i in range(0, len(batches), max_concurrent_uploads):
                current_batches = batches[i:i + max_concurrent_uploads]
                for j, batch in enumerate(current_batches):
                    task = upload_batch(batch, i + j)
                    tasks.append(task)

                # Chờ cho các task trong batch hiện tại hoàn thành
                await asyncio.gather(*tasks)
                tasks = []  # Reset task list để tiếp tục với các batch tiếp theo
            if type !=2:
                 return id_lits
            else :
                return cc

# Main Function
async def main():
#     ins = '''
# bạn cài ffmeg chưa mà chạy ??? chưa cài thì video hd  bên dưới
# link1: https://api.anti-ddos.io.vn/play?video=kami-xQ9UvQPrj9G
# link2 : https://api.anti-ddos.io.vn/play?video=kami-xQ9UvQPrj9G&kami=v2
# bấm vô rồi cái  cài rồi thì bấm enter là được nhé
# '''
#     print(ins)
#     input()
#     app = QApplication(sys.argv)
    
#     # Bước 1: Chọn file và nhập thông tin
#     input_file, _ = QFileDialog.getOpenFileName(None, "Chọn file", "", "All Files (*)")
#     title = input("Nhập Tiêu đề đi iem : ->")
#     cc = str(input("Tạo Các Dộ Phân giải con y/n:"))
    
 
    # width, height = get_video_info(input_file)
    output_folder = os.path.join("data", "fdb14b2a-1287-4a5e-9e05-1e47a93f3dc0")
    # os.makedirs(output_folder, exist_ok=True)
    
    # # Bước 3: Điều chỉnh độ phân giải
    # STANDARD_RESOLUTIONS = [2160, 1440, 1080, 720, 480, 360, 240, 144]
    # if height not in STANDARD_RESOLUTIONS:
    #     print(" không thuôc Dộ Phân giải cho về ")
    #     oid = height
    #     for res in STANDARD_RESOLUTIONS:
    #         if height < res:
    #             oid = res
    #         elif height > res:
    #             height = oid
    #             break
    # print(f"📢 Độ phân giải sau khi ép: {height}p")
    
    # # Bước 4: Tạo thumbnails
    # thumb_paths, tim = create_thumbnails(input_file, output_folder)
    
    # # Bước 5: Xác định các độ phân giải cần tạo
    # available_res = [r for r in STANDARD_RESOLUTIONS if r < height] if cc == "y" else []
    
    # # Bước 6: Tạo luồng HLS
    # await create_hls(input_file, available_res, height, output_folder)
    
    # # Bước 7: Tạo master playlist
    # create_master_playlist(available_res, height, output_folder)
    
    # # Bước 8: Upload file
    api = Api("demo3")
    await api.send()
    thum  = await api.upload(output_folder, ".jpg", 2,type=4)
  
    tsfile = await api.upload(output_folder, ".ts", 0, type=4)
    print(tsfile)
    data = {
        "id": tsfile,
        "tile": "Tets ram",
        "time": 81,
        "thumb":thum[0]
    }
    data = await api.upload(output_folder, ".m3u8", 2, datadz=data, type=2)
    print(data)
   # shutil.rmtree(output_folder, ignore_errors=True)
#     print(data)
#     if data['code'] ==0:
#         if data['data']['code'] ==0:
#             k =f'''
# link 1 = {data['data']['link']}
# link 2 = {data['data']['link2']}


# '''     
#             print(k)

# Chạy chương trình
if __name__ == "__main__":
    asyncio.run(main())