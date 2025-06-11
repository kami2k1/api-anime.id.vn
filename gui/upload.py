import customtkinter as ctk
import threading
import asyncio
import os
import sys
import uuid
import shutil
import subprocess
import json
from tkinter import StringVar, IntVar, BooleanVar
import ffmpeg
import httpx
from PIL import Image
from utils import ffmpeg_check

class UploadFrame(ctk.CTkFrame):
    def __init__(self, parent, api):
        super().__init__(parent)
        self.api = api

        # Nền đen
        self.configure(fg_color="#18191A")

        # Cấu hình lưới
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header - card đen
        header = ctk.CTkFrame(self, fg_color="#23272F", corner_radius=18)
        header.grid(row=0, column=0, sticky="ew", padx=40, pady=(30, 0))
        header.grid_columnconfigure(0, weight=1)
        text = " [ hoạt động ]" if ffmpeg_check.check_ffmpeg_installed() else " [ không hoạt động] - Vui lòng cài đặt FFmpeg để sử dụng tính năng này"
        ctk.CTkLabel(
            header, 
            text="Tải lên video" + text, 
            font=("Segoe UI", 28, "bold"),
            text_color="#00BFFF"
        ).grid(row=0, column=0, sticky="w", pady=18, padx=30)

        # Form - card đen
        form = ctk.CTkFrame(self, fg_color="#23272F", corner_radius=18)
        form.grid(row=1, column=0, sticky="ew", padx=40, pady=20)
        form.grid_columnconfigure(1, weight=1)

        # Biến
        self.file_path = StringVar(value="")
        self.title = StringVar(value="")
        self.create_lower_res = BooleanVar(value=True)
        self.use_gpu = BooleanVar(value=False)
        self.status = StringVar(value="Sẵn sàng tải lên")
        self.progress_text = StringVar(value="")

        # Chọn file
        ctk.CTkLabel(form, text="Chọn file video:", font=("Segoe UI", 14, "bold"), text_color="#00BFFF").grid(row=0, column=0, sticky="w", pady=12, padx=10)
        file_frame = ctk.CTkFrame(form, fg_color="transparent")
        file_frame.grid(row=0, column=1, sticky="ew", pady=12)
        file_frame.grid_columnconfigure(0, weight=1)
        self.file_entry = ctk.CTkEntry(file_frame, textvariable=self.file_path, font=("Segoe UI", 13), height=36, corner_radius=10, fg_color="#18191A", text_color="#F5F6FA", placeholder_text_color="#888")
        self.file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkButton(
            file_frame, 
            text="Chọn...", 
            command=self.browse_file,
            width=100,
            font=("Segoe UI", 13, "bold"),
            fg_color="#00BFFF",
            text_color="#18191A",
            hover_color="#0099CC",
            corner_radius=10
        ).grid(row=0, column=1)

        # Tiêu đề
        ctk.CTkLabel(form, text="Tiêu đề:", font=("Segoe UI", 14, "bold"), text_color="#00BFFF").grid(row=1, column=0, sticky="w", pady=12, padx=10)
        ctk.CTkEntry(form, textvariable=self.title, font=("Segoe UI", 13), height=36, corner_radius=10, fg_color="#18191A", text_color="#F5F6FA", placeholder_text_color="#888").grid(row=1, column=1, sticky="ew", pady=12)

        # Tùy chọn tạo độ phân giải thấp hơn
        ctk.CTkCheckBox(
            form, 
            text="Tạo thêm phiên bản độ phân giải thấp",
            variable=self.create_lower_res,
            onvalue=True,
            offvalue=False,
            font=("Segoe UI", 13),
            text_color="#00BFFF"
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=10, padx=5)

        # Tùy chọn GPU
        ctk.CTkCheckBox(
            form, 
            text="Sử dụng GPU (nếu có Cần cài driver của GPU mới nhất để sử dụng)",
            variable=self.use_gpu,
            onvalue=True,
            offvalue=False,
            command=self.check_gpu_availability,
            font=("Segoe UI", 13),
            text_color="#00BFFF"
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=10, padx=5)

        # Progress - card đen
        progress = ctk.CTkFrame(self, fg_color="#23272F", corner_radius=18)
        progress.grid(row=2, column=0, sticky="nsew", padx=40, pady=30)
        progress.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(progress, textvariable=self.status, font=("Segoe UI", 16, "bold"), text_color="#00BFFF").grid(row=0, column=0, sticky="ew", pady=8)
        self.log_text = ctk.CTkTextbox(progress, height=200, wrap="word", font=("Consolas", 12), corner_radius=10, fg_color="#18191A", text_color="#F5F6FA")
        self.log_text.grid(row=1, column=0, sticky="nsew", pady=10, padx=10)
        self.progress_bar = ctk.CTkProgressBar(progress, height=18, corner_radius=8, progress_color="#00BFFF")
        self.progress_bar.grid(row=2, column=0, sticky="ew", pady=10, padx=10)
        self.progress_bar.set(0)
        ctk.CTkLabel(progress, textvariable=self.progress_text, font=("Segoe UI", 12), text_color="#00BFFF").grid(row=3, column=0, sticky="ew", pady=5)
        button_frame = ctk.CTkFrame(progress, fg_color="transparent")
        button_frame.grid(row=4, column=0, sticky="e", pady=20, padx=10)
        if ffmpeg_check.check_ffmpeg_installed():
            self.upload_button = ctk.CTkButton(
                button_frame,
                text="Tải lên",
                command=self.start_upload,
                width=150,
            font=("Segoe UI", 15, "bold"),
            fg_color="#00BFFF",
            text_color="#18191A",
            hover_color="#0099CC",
            corner_radius=10
            )   
        else:
            self.upload_button = ctk.CTkButton(
                button_frame,
                text="cài ffmpeg để dùng tính năng này",
                command=lambda: ffmpeg_check.check_and_warn_ffmpeg(self),
                width=150,
                font=("Segoe UI", 15, "bold"),
                fg_color="#00BFFF",
                text_color="#18191A",
                hover_color="#0099CC",
                corner_radius=10
            )
        self.upload_button.grid(row=0, column=0, padx=5)
        ctk.CTkButton(
            button_frame, 
            text="Xóa", 
            command=self.clear_form,
            width=100,
            font=("Segoe UI", 13, "bold"),
            fg_color="#393e46",
            text_color="#00BFFF",
            hover_color="#232526",
            corner_radius=10
        ).grid(row=0, column=1, padx=5)

        # Initialize
        self.check_gpu_availability()
        self.log("Ready to upload video.")

    def browse_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Video File", 
            filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv *.wmv"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path.set(file_path)
            # Auto-fill title from filename
            filename = os.path.basename(file_path)
            file_title, _ = os.path.splitext(filename)
            self.title.set(file_title)
            
            # Log file selection
            self.log(f"Selected file: {file_path}")
            self.check_video_info()

    def check_video_info(self):
        """Check video information and display it in the log"""
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            return
            
        self.log("Đang phân tích file video...")
        try:
            # Run in a thread to avoid UI freeze
            threading.Thread(target=self._analyze_video_threaded, args=(file_path,), daemon=True).start()
        except Exception as e:
            self.log(f"Lỗi khi phân tích video: {str(e)}")

    def _analyze_video_threaded(self, file_path):
        try:
            probe = ffmpeg.probe(file_path)
            video_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
            
            width = int(video_stream["width"])
            height = int(video_stream["height"])
            duration = float(probe["format"]["duration"])
            file_size = os.path.getsize(file_path) / (1024*1024)  # Convert to MB
            
            self.log(f"Thông tin video:")
            self.log(f"• Độ phân giải: {width}x{height}")
            self.log(f"• Thời gian: {int(duration // 60)}m {int(duration % 60)}s")
            self.log(f"• Kích thước file: {file_size:.2f} MB")
            
            # Standard resolutions for comparison
            STANDARD_RESOLUTIONS = [2160, 1440, 1080, 720, 480, 360, 240, 144]
            if height not in STANDARD_RESOLUTIONS:
                # Find closest standard resolution
                target_res = next((res for res in sorted(STANDARD_RESOLUTIONS, reverse=True) if res <= height), 
                                STANDARD_RESOLUTIONS[-1])
                self.log(f"Lưu ý: Chiều cao video ({height}p) sẽ được điều chỉnh về độ phân giải chuẩn ({target_res}p)")
        except Exception as e:
            self.log(f"Lỗi khi phân tích video: {str(e)}")

    def check_gpu_availability(self):
        """Check GPU encoder availability and update UI accordingly"""
        if self.use_gpu.get():
            threading.Thread(target=self._check_gpu_threaded, daemon=True).start()

    def _check_gpu_threaded(self):
        gpu_encoder = self._get_gpu_encoder()
        if gpu_encoder == "h264":
            self.use_gpu.set(False)
            self.log("Mã hóa GPU không khả dụng. Đang sử dụng mã hóa CPU.")
        else:
            self.log(f"Đang sử dụng bộ mã hóa GPU: {gpu_encoder}")

    def _get_gpu_encoder(self):
        """Determine the best available GPU encoder for ffmpeg"""
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
        return "h264"  # CPU fallback

    def clear_form(self):
        """Clear the form fields"""
        self.file_path.set("")
        self.title.set("")
        self.log_text.delete("1.0", "end")
        self.progress_bar.set(0)
        self.progress_text.set("")
        self.status.set("Sẵn sàng tải lên")
        self.log("Đã xóa form. Sẵn sàng cho một lần tải lên mới.")

    def log(self, message):
        """Add a message to the log text area"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")  # Scroll to the bottom

    def start_upload(self):
        """Start the upload process"""
        file_path = self.file_path.get()
        title = self.title.get()
        
        if not file_path or not os.path.exists(file_path):
            self.log("Lỗi: Vui lòng chọn một file video hợp lệ")
            return
            
        if not title.strip():
            self.log("Lỗi: Vui lòng nhập tiêu đề cho video")
            return
            
        # Disable upload button during processing
        self.upload_button.configure(state="disabled")
        self.status.set("Đang xử lý video...")
        
        # Use asyncio to handle the upload process
        threading.Thread(target=self._run_upload_async, daemon=True).start()

    def _run_upload_async(self):
        """Run the upload process in an asyncio event loop"""
        asyncio.run(self._process_upload())

    async def _process_upload(self):
        """Process the video upload in separate steps"""
        try:
            file_path = self.file_path.get()
            title = self.title.get()
            create_lower_res = self.create_lower_res.get()
            use_gpu = self.use_gpu.get()
            
            # Setup progress reporting
            self.update_progress(0.05, "Chuẩn bị xử lý...")
            
            # Create a unique output folder
            output_folder = os.path.join("data", str(uuid.uuid4()))
            os.makedirs(output_folder, exist_ok=True)
            
            self.log(f"Đang xử lý trong thư mục tạm thời: {output_folder}")
            
            # Get video info
            self.update_progress(0.1, "Đang phân tích video...")
            width, height = await self._run_async(self._get_video_info, file_path)
            
            # Adjust resolution if needed
            STANDARD_RESOLUTIONS = [2160, 1440, 1080, 720, 480, 360, 240, 144]
            if height not in STANDARD_RESOLUTIONS:
                self.log("Chiều cao video không khớp với các độ phân giải chuẩn.")
                oid = height
                for res in STANDARD_RESOLUTIONS:
                    if height < res:
                        oid = res
                    elif height > res:
                        height = oid
                        break
                self.log(f"Đã điều chỉnh độ phân giải thành: {height}p")
            
            # Create thumbnails
            self.update_progress(0.2, "Đang tạo hình thu nhỏ...")
            thumb_paths, duration = await self._run_async(self._create_thumbnails, file_path, output_folder)
            
            # Determine resolutions to create
            available_res = [r for r in STANDARD_RESOLUTIONS if r < height] if create_lower_res else []
            
            # Configure encoder
            gpu_encoder = "h264_nvenc" if use_gpu else "h264"
            
            # Create HLS streams
            self.update_progress(0.3, "Đang tạo luồng HLS...")
            self.log(f"Đang tạo luồng HLS cho độ phân giải: {height}p")
            if available_res:
                self.log(f"Đang tạo thêm các luồng cho độ phân giải: {', '.join(str(r) + 'p' for r in available_res)}")
                
            await self._create_hls(file_path, available_res, height, output_folder, gpu_encoder)
            
            # Create master playlist
            self.update_progress(0.6, "Đang tạo danh sách phát chính...")
            self._create_master_playlist(available_res, height, output_folder)
            
            # Upload files
            self.update_progress(0.7, "Đang tải lên các tệp...")
            
            # Initialize API
            api = self._create_api_instance()
           
            await api.getc()
            await api.send()
            
            # Upload thumbnails
            asyncio.create_task(api.Check_Idlist())
            self.log("Đang tải lên hình thu nhỏ...")
            thum = await api.upload(output_folder, ".jpg", 2, type=4)
            
            # Upload TS segments
            self.update_progress(0.8, "Đang tải lên các đoạn video...")
            tsfile = await api.upload(output_folder, ".ts", 0, type=4)
            
            # Upload manifest
            self.update_progress(0.9, "Đang tải lên tệp danh sách phát...")
            data = {
                "id": tsfile,
                "tile": title,
                "time": duration,
                "thumb": thum[0]
            }
            result = await api.upload(output_folder, ".m3u8", 2, datadz=data, type=2)
            
            # Cleanup
            self.update_progress(0.95, "Đang dọn dẹp...")
            shutil.rmtree(output_folder, ignore_errors=True)
            
            # Complete
            self.update_progress(1.0, "Tải lên hoàn tất!")
            self.status.set("Tải lên thành công!")
            
            # Display results
            if result and result.get('code') == 0:
                if 'data' in result and result['data'].get('code') == 0:
                    self.log("Tải lên hoàn tất thành công!")
                    self.log(f"Liên kết 1: {result['data'].get('link', '')}")
                    self.log(f"Liên kết 2: {result['data'].get('link2', '')}")
                else:
                    self.log(f"Tải lên hoàn tất với trạng thái: {result}")
            else:
                self.log(f"Kết quả tải lên: {result}")
                
        except Exception as e:
            self.log(f"Lỗi trong quá trình tải lên: {str(e)}")
            self.status.set("Tải lên thất bại")
        finally:

            api.runcheck = False
            self.upload_button.configure(state="normal")

    def update_progress(self, value, text=""):
        """Update progress bar and text"""
        self.progress_bar.set(value)
        if text:
            self.progress_text.set(text)
            self.log(text)

    async def _run_async(self, func, *args, **kwargs):
        """Run a synchronous function asynchronously"""
        return await asyncio.to_thread(func, *args, **kwargs)

    def _get_video_info(self, input_file):
        """Get video dimensions synchronously"""
        try:
            probe = ffmpeg.probe(input_file)
            video_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
            return int(video_stream["width"]), int(video_stream["height"])
        except Exception as e:
            raise RuntimeError(f"Error getting video info: {e}")

    def _create_thumbnails(self, input_file, output_folder, sizes=[1080, 120, 180, 240, 360, 480, 60, 720], num_thumbs=1):
        """Tạo thumbnail không hiện cửa sổ CMD ffmpeg"""
        os.makedirs(output_folder, exist_ok=True)
        try:
            probe = ffmpeg.probe(input_file)
            duration = float(probe["format"]["duration"])
        except Exception as e:
            raise RuntimeError(f"Error getting video duration: {e}")
        timestamps = [duration * i / (num_thumbs + 1) for i in range(1, num_thumbs + 1)]
        thumb_paths = {}
        for i, timestamp in enumerate(timestamps):
            for size in sizes:
                thumb_path = os.path.join(output_folder, f"{size}p.jpg")
                command = [
                    "ffmpeg", "-ss", str(timestamp), "-i", input_file,
                    "-vf", f"scale=-1:{size}", "-frames:v", "1", thumb_path
                ]
                if sys.platform == "win32":
                    CREATE_NO_WINDOW = 0x08000000
                    subprocess.run(command, creationflags=CREATE_NO_WINDOW)
                else:
                    subprocess.run(command)
                thumb_paths[str(size)] = thumb_path
        return thumb_paths, duration
    async def run_ffmpeg_hidden(self, command):
        CREATE_NO_WINDOW = 0x08000000
        if sys.platform == "win32":
            proc = await asyncio.create_subprocess_exec(
                *command,
                creationflags=CREATE_NO_WINDOW
            )
        else:
            proc = await asyncio.create_subprocess_exec(*command)
        await proc.wait()
        return proc

    async def _create_hls(self, input_file, resolutions, original_resolution, output_folder, encoder):
        """Tạo các luồng HLS không hiện cửa sổ CMD ffmpeg"""
        os.makedirs(output_folder, exist_ok=True)
        tasks = []
        hwaccel = "cuda" if encoder == "h264_nvenc" else "auto"
        for res in [original_resolution] + resolutions:
            output_file = os.path.join(output_folder, f"{res}p.m3u8")
            command = [
                "ffmpeg", "-hide_banner",
                "-hwaccel", hwaccel,
                "-i", input_file, 
                "-vf", f"scale=-2:{res}", 
                "-c:v", encoder,
                "-b:v", f"{res*5}k", 
                "-hls_time", "3", 
                "-hls_list_size", "0",
                "-map_metadata", "-1",
                "-fflags", "+bitexact",
                "-f", "hls", output_file
            ]
            self.log(f"Đang tạo luồng HLS cho độ phân giải {res}p")
            tasks.append(self.run_ffmpeg_hidden(command))
        await asyncio.gather(*tasks)

    def _create_master_playlist(self, resolutions, original_resolution, output_folder):
        """Create the master playlist file"""
        BANDWIDTH_MAP = {
            2160: 12000000, 1440: 8000000, 1080: 5000000, 720: 2800000,
            480: 1200000, 360: 800000, 240: 500000, 144: 250000
        }
        
        with open(os.path.join(output_folder, "master.m3u8"), "w") as f:
            f.write("#EXTM3U\n")
            for res in [original_resolution] + resolutions:
                f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={BANDWIDTH_MAP.get(res, res * 6000)},CODECS=\"mp4a.40.2,avc1.640028\",RESOLUTION={res}p,NAME=\"{res}\"\n")
                f.write(f"{res}p.m3u8\n")
                
        self.log(f"Đã tạo danh sách phát chính với {len(resolutions) + 1} luồng")

    def _create_api_instance(self):
        """Create an API instance for uploading files"""
        class Api:
            def __init__(self, api_key,max_upload=5, custumurl="https://phim.click/"):
                self.maxupload = max_upload
                self.maxsizebath = 95 * 1024 * 1024  # 95 MB ## cloudflare limit
                self.max = asyncio.Semaphore(self.maxupload)
                self.api = api_key
                self.url = custumurl
                self.upload_url = 'http://127.0.0.1/'
                self.uploadz = "upload"
                self.client = None
                self.req = httpx.Client(http2=True)
                self.runcheck = True
                self.idlist = []
                self._id = {}
                
            async def Check_Idlist(self):
                """Check the id list for updates."""
                url = f"{self.upload_url}ch?api={self.api}"

                while self.runcheck:
                    if self.idlist:
                        try:
                            data = {
                                "data": self.idlist.copy(),
                            }
                           
                            r = self.req.post(url, json=data, timeout=30)  # giảm timeout
                            r = r.json()
                            
                            for item in r.get('data', []):
                                if item.get('ok'):
                                    if item['id'] in self._id:
                                        self._id[item['id']].set()
                                        self.idlist.remove(item['id'])
                        except Exception as e:
                            print(f"Error checking id list: {e}")
                        await asyncio.sleep(1)  # luôn sleep sau mỗi lần check
                    else:
                        await asyncio.sleep(1)  # sleep khi không có idlist

            async def getc(self):
                """Initialize async HTTP client."""
                self.client = httpx.AsyncClient(http2=True)

            def ext(self):
                """Exit program on upload error."""
                print("Error: Upload failed")
                return

            async def send(self):
                """Send request to get upload URL from server."""
                if not self.client:
                    await self.getc()
                d = await self.client.get(f"{self.url}inf?api={self.api}")
                d = d.json()
                
                self.upload_url = d['upload']
                print("Got upload URL")

            async def upload(self, hls_folder, file_ext, id, batch_size=20, type=1, datadz=None):
                """Upload files in batches."""
                all_files = [os.path.join(hls_folder, file_name) for file_name in os.listdir(hls_folder) 
                            if file_name.endswith(file_ext)]
                url = (f"{self.upload_url}{self.uploadz}?api={self.api}&m=m" if file_ext == ".m3u8" 
                       else f"{self.upload_url}{self.uploadz}?api={self.api}")
                
                if type != 1:
                    if not all_files:
                        print("No matching files found!")
                        return

                    dataz = {}
                    id_lits = []
                    cc = {}
                    batches = [all_files[i:i + batch_size] for i in range(0, len(all_files), batch_size)]

                    async def upload_batch(batch_files, batch_index):
                      async with self.max:
                      

                        nonlocal cc, id_lits
                        files = [("file", (os.path.basename(f), open(f, "rb"))) for f in batch_files]
                        try:
                            if type == 2:
                                files.append(("json", (None, json.dumps(datadz), "application/json")))
                                response = await self.client.post(url, files=files, json=datadz, timeout=600)
                                cc = response.json()
                                return

                            response = await self.client.post(url, files=files, timeout=120)
                            data = response.json()

                            if data['code'] == 0:
                                if file_ext == ".m3u8":
                                    for i, item in data['data'].items():
                                        dataz[i] = {"kami": True, "link": f"{self.url}m?id={item}"}
                                else:
                                    d = True
                                    s = f"{self.upload_url}/ch?api={self.api}&id={data['id']}"
                                    id_lits.append(data['id'])
                                    self.idlist.append(data['id'])
                                    self._id[data['id']] = asyncio.Event()
                                    await self._id[data['id']].wait() ## < chờ đuọc thức tỉnh 
                                    # while d:
                                    #     response = await self.client.get(s)
                                    #     data = response.json()
                                    #     if data['code'] == 20:
                                    #         await asyncio.sleep(2)
                                    #     elif data['code'] == 0:
                                    #         print("Got data successfully")
                                    #         d = False
                                    #     else:
                                    #         print("Error:", data)
                                    #         return
                            else:
                                print("Upload error")
                                print(response.text)
                                await asyncio.sleep(2)
                                return await upload_batch(batch_files, batch_index)
                        except Exception as e:
                            print(f"Error in batch {batch_index}: {e}")
                            return await upload_batch(batch_files, batch_index)

                    max_concurrent_uploads = 99999
                    tasks = []
                    for i in range(0, len(batches), max_concurrent_uploads):
                        current_batches = batches[i:i + max_concurrent_uploads]
                        for j, batch in enumerate(current_batches):
                            task = upload_batch(batch, i + j)
                            tasks.append(task)

                        await asyncio.gather(*tasks)
                        tasks = []
                        
                    if type != 2:
                        return id_lits
                    else:
                        return cc

        # Use the API key from the main API object
        return Api(self.api.key, self.api.up)