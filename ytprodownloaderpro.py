import os
import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from yt_dlp import YoutubeDL
import subprocess
import sys
import requests
import zipfile
import urllib.request
from io import BytesIO
from PIL import Image, ImageTk

# ===================== CONFIG =====================
APP_NAME = "YouTube Downloader Pro"
OWNER = "Rupesh Sharma"
LOGO_URL = "https://images.icon-icons.com/195/PNG/256/YouTube_23392.png"
FFMPEG_URL = "https://github.com/GyanD/codexffmpeg/releases/download/7.0.1/ffmpeg-7.0.1-essentials_build.zip"
TEMP_DIR = os.path.join(os.getenv('TEMP'), "yt_downloader_pro")
os.makedirs(TEMP_DIR, exist_ok=True)
FFMPEG_EXE = os.path.join(TEMP_DIR, "ffmpeg.exe")

# ===================== DEPENDENCY SETUP =====================
def install_ffmpeg():
    if os.path.exists(FFMPEG_EXE): return
    messagebox.showinfo("Setup", "Downloading ffmpeg (one-time)...")
    try:
        zip_path, _ = urllib.request.urlretrieve(FFMPEG_URL)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith("ffmpeg.exe"):
                    with open(FFMPEG_EXE, "wb") as f:
                        f.write(zip_ref.read(file))
                    break
        os.remove(zip_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to install ffmpeg:\n{e}")

def install_ytdlp():
    try: import yt_dlp
    except:
        messagebox.showinfo("Setup", "Installing yt-dlp (one-time)...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "--upgrade", "--no-warn-script-location"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install yt-dlp:\n{e}")

# ===================== GLOBALS =====================
video_info = {}
progress_var = None
status_label = None
download_btn = None
quality_combo = None
title_label = None
url_entry = None
download_var = None
thumb_label = None
thumb_url = None
percent_label = None
root = None
current_mode = "video"
from_entry = None
to_entry = None

# ===================== HELPERS =====================
def sanitize(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def format_bytes(b):
    if not b: return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if b < 1024: return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"

def time_to_sec(t):
    if not t: return None
    try:
        parts = list(map(int, t.split(':')))
        if len(parts) == 3:
            h, m, s = parts
        elif len(parts) == 2:
            h, m, s = 0, parts[0], parts[1]
        else:
            return None
        return h * 3600 + m * 60 + s
    except:
        return None

# ===================== AUTO LOAD VIDEO =====================
def auto_load_video(*args):
    url = url_entry.get().strip()
    if not url or ("youtube.com" not in url and "youtu.be" not in url):
        return
    root.after(800, load_video_info)

def load_video_info():
    global video_info, thumb_url
    url = url_entry.get().strip()
    if not url: return

    status_label.config(text="Loading video...", fg="#00d4aa")
    quality_combo['values'] = []
    quality_combo.set("")
    quality_combo.config(state="disabled")
    progress_var.set(0)
    percent_label.config(text="0%")

    def run():
        try:
            # Suppress warnings + use latest extractor
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'format': 'best',
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            if info.get('_type') == 'playlist':
                root.after(0, lambda: messagebox.showerror("Error", "Playlist URLs are not supported!\nPlease enter a single video URL."))
                return

            video_info.clear()
            video_info.update(info)

            title = info.get('title', 'Unknown Video')
            thumb_url = max(info.get('thumbnails', []), key=lambda x: x.get('width', 0))['url']

            root.after(0, lambda: [
                title_label.config(text=title),
                load_thumbnail(thumb_url),
                update_quality_list(),
                status_label.config(text="Ready", fg="#00ff00")
            ])
        except Exception as e:
            root.after(0, lambda: [
                status_label.config(text="Failed to load", fg="red"),
                messagebox.showerror("Error", str(e))
            ])

    threading.Thread(target=run, daemon=True).start()

def load_thumbnail(url):
    try:
        resp = requests.get(url, timeout=10)
        img = Image.open(BytesIO(resp.content)).resize((320, 180), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        thumb_label.config(image=photo, text="")
        thumb_label.image = photo
    except:
        thumb_label.config(image="", text="No Thumbnail")

def update_quality_list():
    global current_mode
    choice = download_var.get()
    formats = video_info.get('formats', [])

    if choice == "Audio Only (MP3)":
        current_mode = "audio"
        audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
        audio_list = []
        for f in sorted(audio_formats, key=lambda x: x.get('abr', 0), reverse=True):
            abr = f.get('abr', 0)
            size = f.get('filesize') or f.get('filesize_approx')
            size_str = format_bytes(size) if size else "Unknown"
            label = f"{abr} kbps - {size_str}"
            audio_list.append((label, f['format_id'], abr))
        quality_combo.config(values=[q[0] for q in audio_list])
        quality_combo.set(audio_list[0][0] if audio_list else "")
    else:
        current_mode = "video"
        video_formats = [f for f in formats if f.get('ext') == 'mp4' and f.get('vcodec') != 'none']
        video_list = []
        for f in sorted(video_formats, key=lambda x: x.get('height', 0), reverse=True):
            h = f.get('height')
            fps = f.get('fps', 0)
            vbitrate = f.get('vcodec') != 'none' and f.get('tbr') or 0
            size = f.get('filesize') or f.get('filesize_approx')
            size_str = format_bytes(size) if size else "Unknown"
            label = f"{h}p @ {fps}fps - {vbitrate} kbps - {size_str}"
            video_list.append((label, f['format_id'], h))
        quality_combo.config(values=[q[0] for q in video_list])
        quality_combo.set(video_list[0][0] if video_list else "")

    quality_combo.config(state="readonly")

# ===================== DOWNLOAD + TRIM + THUMBNAIL =====================
def start_download():
    url = url_entry.get().strip()
    if not url or not video_info:
        messagebox.showerror("Error", "Load video first!")
        return

    folder = filedialog.askdirectory(title="Select Download Folder")
    if not folder: return

    choice = download_var.get()
    quality_label = quality_combo.get()
    if not quality_label:
        messagebox.showerror("Error", "No quality available")
        return

    # Get format_id safely
    if current_mode == "audio":
        audio_list = [(f"{f.get('abr', 0)} kbps - {format_bytes(f.get('filesize') or f.get('filesize_approx'))}", f['format_id'], f.get('abr', 0))
                      for f in video_info.get('formats', []) if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
        format_id = next((x[1] for x in audio_list if x[0] == quality_label), 'bestaudio')
    else:
        video_list = [(f"{f.get('height')}p @ {f.get('fps', 0)}fps - {f.get('tbr', 0)} kbps - {format_bytes(f.get('filesize') or f.get('filesize_approx'))}", f['format_id'], f.get('height'))
                      for f in video_info.get('formats', []) if f.get('ext') == 'mp4' and f.get('vcodec') != 'none']
        format_id = next((x[1] for x in video_list if x[0] == quality_label), 'bestvideo[ext=mp4]')

    title = sanitize(video_info.get('title', 'video'))
    temp_video = os.path.join(TEMP_DIR, f"{title}_full.mp4")
    final_path = os.path.join(folder, f"{title}.mp4" if choice != "Audio Only (MP3)" else f"{title}.mp3")
    thumb_path = os.path.join(folder, f"{title}_thumb.png")

    # Parse timestamps
    from_time = from_entry.get().strip()
    to_time = to_entry.get().strip()
    start_sec = time_to_sec(from_time)
    end_sec = time_to_sec(to_time) if to_time else None

    status_label.config(text="Downloading...", fg="#00d4aa")
    progress_var.set(0)
    percent_label.config(text="0%")
    download_btn.config(state="disabled")

    def run():
        try:
            # === 1. Download Full Video ===
            if choice == "Video + Audio":
                ydl = YoutubeDL({
                    'format': f"{format_id}+bestaudio/best",
                    'outtmpl': temp_video,
                    'merge_output_format': 'mp4',
                    'ffmpeg_location': FFMPEG_EXE,
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [progress_hook],
                })
                ydl.download([url])
            elif choice == "Video Only":
                ydl = YoutubeDL({
                    'format': format_id,
                    'outtmpl': temp_video,
                    'ffmpeg_location': FFMPEG_EXE,
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [progress_hook],
                })
                ydl.download([url])
            else:  # Audio Only
                ydl = YoutubeDL({
                    'format': format_id,
                    'outtmpl': final_path,
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
                    'ffmpeg_location': FFMPEG_EXE,
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [progress_hook],
                })
                ydl.download([url])
                # Download thumbnail
                try:
                    resp = requests.get(thumb_url)
                    with open(thumb_path, 'wb') as f:
                        f.write(resp.content)
                except: pass
                root.after(0, lambda: [
                    progress_var.set(100),
                    percent_label.config(text="100%"),
                    status_label.config(text="Download Complete!", fg="#00ff00"),
                    messagebox.showinfo("Success", f"Audio + Thumbnail saved:\n{folder}"),
                    download_btn.config(state="normal")
                ])
                return

            # === 2. Download Thumbnail ===
            try:
                resp = requests.get(thumb_url)
                with open(thumb_path, 'wb') as f:
                    f.write(resp.content)
            except: pass

            # === 3. Trim Video (if needed) ===
            if start_sec is not None:
                status_label.config(text="Trimming video...", fg="#00d4aa")
                progress_var.set(0)
                percent_label.config(text="Trimming...")

                cmd = [FFMPEG_EXE, '-y', '-i', temp_video]
                if end_sec:
                    duration = end_sec - start_sec
                    cmd += ['-ss', str(start_sec), '-t', str(duration)]
                else:
                    cmd += ['-ss', str(start_sec)]
                cmd += ['-c', 'copy', '-avoid_negative_ts', 'make_zero', final_path]

                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # Delete full video
                if os.path.exists(temp_video):
                    os.remove(temp_video)
            else:
                if os.path.exists(temp_video):
                    os.replace(temp_video, final_path)

            root.after(0, lambda: [
                progress_var.set(100),
                percent_label.config(text="100%"),
                status_label.config(text="Download Complete!", fg="#00ff00"),
                messagebox.showinfo("Success", f"Video + Thumbnail saved:\n{folder}"),
                download_btn.config(state="normal")
            ])

        except Exception as e:
            root.after(0, lambda: [
                status_label.config(text="Download Failed", fg="red"),
                percent_label.config(text="Error"),
                messagebox.showerror("Error", str(e)),
                download_btn.config(state="normal")
            ])

    threading.Thread(target=run, daemon=True).start()

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').replace('%', '').strip()
        try:
            p = float(percent)
            root.after(0, lambda: [
                progress_var.set(p),
                percent_label.config(text=f"{p:.1f}%")
            ])
        except: pass

# ===================== THUMBNAIL DOWNLOAD =====================
def download_thumbnail():
    if not thumb_url or not video_info:
        messagebox.showerror("Error", "No thumbnail to download")
        return
    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")],
        initialfile=sanitize(video_info.get('title', 'thumbnail')) + ".png"
    )
    if not save_path: return
    try:
        resp = requests.get(thumb_url)
        with open(save_path, 'wb') as f:
            f.write(resp.content)
        messagebox.showinfo("Success", f"Thumbnail saved:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ===================== COPY TITLE =====================
def copy_title():
    title = title_label.cget("text")
    if title and title != "No video loaded":
        root.clipboard_clear()
        root.clipboard_append(title)
        messagebox.showinfo("Copied", "Title copied to clipboard!")

# ===================== GUI =====================
def create_gui():
    global root, status_label, download_btn, quality_combo, title_label, url_entry, download_var
    global progress_var, thumb_label, percent_label, from_entry, to_entry

    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("1050x820")
    root.minsize(700, 600)
    root.config(bg="#0f0f0f")

    # Logo
    try:
        resp = requests.get(LOGO_URL, timeout=10)
        img = Image.open(BytesIO(resp.content)).resize((64, 64), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(img)
        root.iconphoto(True, logo_img)
    except: pass

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Dark.Horizontal.TProgressbar", background="#00d4aa", troughcolor="#2a2a2a", thickness=25)

    # Scrollable
    canvas = tk.Canvas(root, bg="#0f0f0f", highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable = tk.Frame(canvas, bg="#0f0f0f")
    scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Header
    header = tk.Frame(scrollable, bg="#0f0f0f")
    header.pack(pady=15, fill='x')
    tk.Label(header, text=APP_NAME, font=("Segoe UI", 24, "bold"), fg="#00d4aa", bg="#0f0f0f").pack()
    tk.Label(header, text=f"by {OWNER}", font=("Segoe UI", 10), fg="#888", bg="#0f0f0f").pack()

    # URL
    url_frame = tk.Frame(scrollable, bg="#1a1a1a", relief="flat", bd=1)
    url_frame.pack(fill='x', padx=40, pady=10)
    tk.Label(url_frame, text="YouTube URL", font=("Segoe UI", 11), bg="#1a1a1a", fg="#aaa").pack(anchor='w', padx=15, pady=8)
    url_entry = tk.Entry(url_frame, font=("Segoe UI", 12), bg="#252525", fg="white", insertbackground="white", relief="flat")
    url_entry.pack(fill='x', padx=15, pady=(0,10), ipady=10)
    url_entry.bind("<KeyRelease>", auto_load_video)

    # Thumbnail + Title
    info_frame = tk.Frame(scrollable, bg="#0f0f0f")
    info_frame.pack(fill='x', padx=40, pady=10)
    info_frame.grid_columnconfigure(1, weight=1)

    thumb_label = tk.Label(info_frame, text="No Thumbnail", bg="#1a1a1a", width=40, height=10)
    thumb_label.grid(row=0, column=0, rowspan=3, padx=(0,15), sticky='ns')

    title_label = tk.Label(info_frame, text="No video loaded", font=("Segoe UI", 13, "bold"), fg="white", bg="#0f0f0f", anchor='w', wraplength=500)
    title_label.grid(row=0, column=1, sticky='ew')

    btn_frame = tk.Frame(info_frame, bg="#0f0f0f")
    btn_frame.grid(row=1, column=1, sticky='w', pady=5)
    tk.Button(btn_frame, text="Copy Title", command=copy_title, bg="#333", fg="white", font=("Segoe UI", 9)).pack(side='left', padx=2)
    tk.Button(btn_frame, text="Download Thumbnail", command=download_thumbnail, bg="#333", fg="white", font=("Segoe UI", 9)).pack(side='left', padx=2)

    # Trim Section
    trim_frame = tk.Frame(info_frame, bg="#0f0f0f")
    trim_frame.grid(row=2, column=1, sticky='w', pady=5)
    tk.Label(trim_frame, text="Trim (optional):", font=("Segoe UI", 10), fg="#aaa", bg="#0f0f0f").pack(side='left')
    from_entry = tk.Entry(trim_frame, width=10, font=("Segoe UI", 10))
    from_entry.pack(side='left', padx=2)
    from_entry.insert(0, "00:00:00")
    tk.Label(trim_frame, text="to", fg="#aaa", bg="#0f0f0f").pack(side='left')
    to_entry = tk.Entry(trim_frame, width=10, font=("Segoe UI", 10))
    to_entry.pack(side='left', padx=2)

    # Options
    opts_frame = tk.Frame(scrollable, bg="#0f0f0f")
    opts_frame.pack(fill='x', padx=40, pady=10)
    opts_frame.grid_columnconfigure(0, weight=1)
    opts_frame.grid_columnconfigure(1, weight=1)

    tk.Label(opts_frame, text="Download Type:", font=("Segoe UI", 11, "bold"), bg="#0f0f0f", fg="#00d4aa").grid(row=0, column=0, sticky='w', pady=5)
    download_var = tk.StringVar(value="Video + Audio")
    for i, text in enumerate(["Video + Audio", "Video Only", "Audio Only (MP3)"]):
        rb = tk.Radiobutton(opts_frame, text=text, variable=download_var, value=text, bg="#0f0f0f", fg="white", selectcolor="#333", font=("Segoe UI", 10))
        rb.grid(row=i+1, column=0, sticky='w', pady=2)
        rb.config(command=update_quality_list)

    tk.Label(opts_frame, text="Quality:", font=("Segoe UI", 11, "bold"), bg="#0f0f0f", fg="#00d4aa").grid(row=0, column=1, sticky='w', padx=(40,0), pady=5)
    quality_combo = ttk.Combobox(opts_frame, state="readonly", font=("Segoe UI", 10), width=50)
    quality_combo.grid(row=1, column=1, rowspan=3, padx=(40,0), sticky='w')

    # Progress
    prog_frame = tk.Frame(scrollable, bg="#0f0f0f")
    prog_frame.pack(fill='x', padx=40, pady=15)
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(prog_frame, variable=progress_var, maximum=100, style="Dark.Horizontal.TProgressbar")
    progress_bar.pack(fill='x', side='left', expand=True)
    percent_label = tk.Label(prog_frame, text="0%", font=("Segoe UI", 11, "bold"), fg="#00d4aa", bg="#0f0f0f")
    percent_label.pack(side='right', padx=(10,0))

    # Download
    download_btn = tk.Button(scrollable, text="DOWNLOAD NOW", command=start_download, bg="#00d4aa", fg="white", font=("Segoe UI", 14, "bold"), height=2)
    download_btn.pack(pady=15, fill='x', padx=100)

    # Status
    status_label = tk.Label(scrollable, text="Paste a YouTube link to start", font=("Segoe UI", 10), bg="#0f0f0f", fg="#666")
    status_label.pack(pady=5)

    # Ads
    ads_frame = tk.Frame(scrollable, bg="#1a1a1a")
    ads_frame.pack(fill='x', padx=40, pady=15)
    tk.Label(ads_frame, text="Advertisement", font=("Segoe UI", 10, "bold"), bg="#1a1a1a", fg="#00d4aa").pack(anchor='w', padx=15, pady=5)
    ads_inner = tk.Frame(ads_frame, bg="#1a1a1a")
    ads_inner.pack(fill='x', padx=10)
    for i in range(3):
        ad = tk.Frame(ads_inner, bg="#2a2a2a", relief="solid", bd=1, width=220, height=60)
        ad.pack(side='left', expand=True, fill='both', padx=8, pady=8)
        ad.pack_propagate(False)
        tk.Label(ad, text="PUT YOUR ADS HERE", font=("Segoe UI", 9), bg="#2a2a2a", fg="#888").pack(expand=True)

    # Footer
    tk.Label(scrollable, text=f"© {OWNER} | v1.0", font=("Segoe UI", 9), bg="#0f0f0f", fg="#555").pack(side='bottom', pady=15)

    # Setup
    if not os.path.exists(FFMPEG_EXE):
        threading.Thread(target=install_ffmpeg, daemon=True).start()
    install_ytdlp()

    root.mainloop()

if __name__ == "__main__":
    create_gui()