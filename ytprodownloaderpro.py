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
    if os.path.exists(FFMPEG_EXE):
        return
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
    try:
        import yt_dlp
    except:
        messagebox.showinfo("Setup", "Installing yt-dlp (one-time)...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "yt-dlp", "--no-warn-script-location"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
root = None

# ===================== HELPERS =====================
def sanitize(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def format_bytes(b):
    if not b: return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if b < 1024: return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"

# ===================== LOAD VIDEO =====================
def load_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Enter YouTube URL")
        return

    status_label.config(text="Loading video info...", fg="#00d4aa")
    quality_combo['values'] = []
    quality_combo.set("")
    quality_combo.config(state="disabled")
    progress_var.set(0)

    def run():
        try:
            with YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                video_info.clear()
                video_info.update(info)

            title = info.get('title', 'Unknown Video')
            root.after(0, lambda: title_label.config(text=title))

            formats = [f for f in info.get('formats', []) 
                      if f.get('ext') == 'mp4' and f.get('vcodec') != 'none']
            
            quality_list = []
            for f in sorted(formats, key=lambda x: x.get('height', 0), reverse=True):
                h = f.get('height')
                size = f.get('filesize') or f.get('filesize_approx')
                size_str = format_bytes(size) if size else "Unknown"
                label = f"{h}p - {size_str}"
                quality_list.append((label, f['format_id']))

            root.after(0, lambda: [
                quality_combo.config(values=[q[0] for q in quality_list], state="readonly"),
                quality_combo.set(quality_list[0][0] if quality_list else ""),
                status_label.config(text="Ready to download", fg="#00ff00")
            ])

        except Exception as e:
            root.after(0, lambda: [
                status_label.config(text="Failed to load", fg="red"),
                messagebox.showerror("Error", str(e))
            ])

    threading.Thread(target=run, daemon=True).start()

# ===================== DOWNLOAD =====================
def start_download():
    url = url_entry.get().strip()
    if not url or not video_info:
        messagebox.showerror("Error", "Load video first!")
        return

    folder = filedialog.askdirectory(title="Select Download Folder")
    if not folder:
        return

    choice = download_var.get()
    quality_label = quality_combo.get()
    if not quality_label:
        messagebox.showerror("Error", "No quality available")
        return

    formats = [f for f in video_info.get('formats', []) 
               if f.get('ext') == 'mp4' and f.get('vcodec') != 'none']
    format_id = next((f['format_id'] for f in formats 
                     if f"{f.get('height')}p - {format_bytes(f.get('filesize') or f.get('filesize_approx'))}" == quality_label), 
                     'bestvideo[ext=mp4]')

    title = sanitize(video_info.get('title', 'video'))
    status_label.config(text="Downloading...", fg="#00d4aa")
    progress_var.set(0)
    download_btn.config(state="disabled")

    def run():
        try:
            if choice == "Video + Audio":
                final_path = os.path.join(folder, f"{title}.mp4")
                ydl = YoutubeDL({
                    'format': f"{format_id}+bestaudio",
                    'outtmpl': final_path,
                    'merge_output_format': 'mp4',
                    'ffmpeg_location': FFMPEG_EXE,
                    'quiet': True,
                    'progress_hooks': [lambda d: progress_hook(d)],
                })
                ydl.download([url])

            elif choice == "Video Only":
                video_path = os.path.join(folder, f"{title}_video.mp4")
                ydl = YoutubeDL({
                    'format': format_id,
                    'outtmpl': video_path,
                    'ffmpeg_location': FFMPEG_EXE,
                    'quiet': True,
                    'progress_hooks': [lambda d: progress_hook(d)],
                })
                ydl.download([url])

            elif choice == "Audio Only (MP3)":
                audio_path = os.path.join(folder, f"{title}.mp3")
                ydl = YoutubeDL({
                    'format': 'bestaudio',
                    'outtmpl': audio_path,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                    }],
                    'ffmpeg_location': FFMPEG_EXE,
                    'quiet': True,
                    'progress_hooks': [lambda d: progress_hook(d)],
                })
                ydl.download([url])

            root.after(0, lambda: [
                progress_var.set(100),
                status_label.config(text="Download Complete!", fg="#00ff00"),
                messagebox.showinfo("Success", f"Saved to:\n{folder}"),
                download_btn.config(state="normal")
            ])

        except Exception as e:
            root.after(0, lambda: [
                status_label.config(text="Download Failed", fg="red"),
                messagebox.showerror("Error", str(e)),
                download_btn.config(state="normal")
            ])

    threading.Thread(target=run, daemon=True).start()

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').replace('%', '').strip()
        try:
            root.after(0, lambda: progress_var.set(float(percent)))
        except: pass

# ===================== RESPONSIVE GUI =====================
def create_gui():
    global root, status_label, download_btn, quality_combo, title_label, url_entry, download_var, progress_var

    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("900x700")
    root.minsize(400, 600)
    root.config(bg="#0f0f0f")

    # RESPONSIVE: Use grid weights for main window
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Logo
    try:
        response = requests.get(LOGO_URL, timeout=10)
        img = Image.open(BytesIO(response.content)).resize((64, 64), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(img)
        root.iconphoto(True, logo_img)
    except:
        pass

    style = ttk.Style()
    style.theme_use('clam')

    # === PROGRESS BAR STYLE (Fixed: Use 'thickness' instead of 'height') ===
    style.configure("Dark.Horizontal.TProgressbar",
                    background="#00d4aa",
                    troughcolor="#2a2a2a",
                    borderwidth=1,
                    lightcolor="#00d4aa",
                    darkcolor="#00d4aa",
                    thickness=25)  # This controls the height!

    style.map("Dark.Horizontal.TProgressbar",
              background=[('active', '#00ffaa')])

    # Main Container with responsive grid
    main_container = tk.Frame(root, bg="#0f0f0f")
    main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    main_container.grid_rowconfigure(1, weight=1)
    main_container.grid_columnconfigure(0, weight=1)

    # Header Section
    header = tk.Frame(main_container, bg="#0f0f0f")
    header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
    header.grid_columnconfigure(0, weight=1)
    
    tk.Label(header, text=APP_NAME, font=("Segoe UI", 24, "bold"), fg="#00d4aa", bg="#0f0f0f").grid(row=0, column=0, pady=(10, 0))
    tk.Label(header, text=f"by {OWNER}", font=("Segoe UI", 10), fg="#888", bg="#0f0f0f").grid(row=1, column=0, pady=(0, 10))

    # Content Area with Scrollbar
    content_frame = tk.Frame(main_container, bg="#0f0f0f")
    content_frame.grid(row=1, column=0, sticky="nsew")
    content_frame.grid_columnconfigure(0, weight=1)

    canvas = tk.Canvas(content_frame, bg="#0f0f0f", highlightthickness=0)
    scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#0f0f0f")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)

    scrollable_frame.grid_columnconfigure(0, weight=1)

    # URL Input Section
    url_section = tk.Frame(scrollable_frame, bg="#0f0f0f")
    url_section.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
    url_section.grid_columnconfigure(0, weight=1)

    tk.Label(url_section, text="YouTube URL", font=("Segoe UI", 12, "bold"), bg="#0f0f0f", fg="#fff", anchor='w').grid(row=0, column=0, sticky='w', pady=(0, 8))
    
    url_input_frame = tk.Frame(url_section, bg="#1a1a1a", relief="flat", bd=1)
    url_input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
    url_input_frame.grid_columnconfigure(0, weight=1)

    url_entry = tk.Entry(url_input_frame, font=("Segoe UI", 12), bg="#252525", fg="white", 
                        insertbackground="white", relief="flat", bd=0)
    url_entry.grid(row=0, column=0, sticky="ew", padx=15, pady=12, ipady=8)

    load_btn = tk.Button(url_input_frame, text="LOAD VIDEO", command=load_video, 
                        bg="#00d4aa", fg="white", font=("Segoe UI", 10, "bold"), 
                        relief="flat", bd=0, cursor="hand2")
    load_btn.grid(row=0, column=1, padx=(0, 15), pady=12, ipadx=15)

    # Video Title Section
    title_label = tk.Label(scrollable_frame, text="No video loaded", font=("Segoe UI", 13), 
                          fg="white", bg="#0f0f0f", anchor='w', justify='left', wraplength=800)
    title_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 20))

    # Options Section - Responsive grid
    options_section = tk.Frame(scrollable_frame, bg="#0f0f0f")
    options_section.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
    options_section.grid_columnconfigure(0, weight=1)
    options_section.grid_columnconfigure(1, weight=1)

    # Download Type Section
    type_frame = tk.Frame(options_section, bg="#0f0f0f")
    type_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    tk.Label(type_frame, text="Download Type", font=("Segoe UI", 12, "bold"), 
             bg="#0f0f0f", fg="#00d4aa", anchor='w').pack(anchor='w', pady=(0, 10))
    
    download_var = tk.StringVar(value="Video + Audio")
    
    type_options_frame = tk.Frame(type_frame, bg="#0f0f0f")
    type_options_frame.pack(fill='x')
    
    download_types = ["Video + Audio", "Video Only", "Audio Only (MP3)"]
    for i, text in enumerate(download_types):
        radio = tk.Radiobutton(type_options_frame, text=text, variable=download_var, 
                              value=text, bg="#0f0f0f", fg="white", selectcolor="#333", 
                              font=("Segoe UI", 10), anchor='w')
        radio.pack(fill='x', pady=5)

    # Quality Selection Section
    quality_frame = tk.Frame(options_section, bg="#0f0f0f")
    quality_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    quality_frame.grid_columnconfigure(0, weight=1)

    tk.Label(quality_frame, text="Video Quality", font=("Segoe UI", 12, "bold"), 
             bg="#0f0f0f", fg="#00d4aa", anchor='w').grid(row=0, column=0, sticky='w', pady=(0, 10))
    
    quality_combo = ttk.Combobox(quality_frame, state="readonly", font=("Segoe UI", 11), 
                                height=8, background="#252525")
    quality_combo.grid(row=1, column=0, sticky="ew", pady=5)
    quality_combo.set("Select quality after loading video")

    # Progress Section
    progress_section = tk.Frame(scrollable_frame, bg="#0f0f0f")
    progress_section.grid(row=3, column=0, sticky="ew", padx=20, pady=20)
    progress_section.grid_columnconfigure(0, weight=1)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_section, 
                                  variable=progress_var, 
                                  maximum=100, 
                                  style="Dark.Horizontal.TProgressbar")  # Removed 'height'
    progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

    # Download Button
    download_btn = tk.Button(scrollable_frame, text="DOWNLOAD NOW", command=start_download,
                           bg="#00d4aa", fg="white", font=("Segoe UI", 14, "bold"),
                           relief="flat", bd=0, cursor="hand2", height=2)
    download_btn.grid(row=4, column=0, sticky="ew", padx=20, pady=15)

    # Status Label
    status_label = tk.Label(scrollable_frame, text="Ready to download", font=("Segoe UI", 11),
                          bg="#0f0f0f", fg="#00d4aa")
    status_label.grid(row=5, column=0, pady=(0, 20))

    # Ads Section
    ads_section = tk.Frame(scrollable_frame, bg="#1a1a1a")
    ads_section.grid(row=6, column=0, sticky="ew", padx=20, pady=20)
    ads_section.grid_columnconfigure(0, weight=1)

    tk.Label(ads_section, text="Sponsored", font=("Segoe UI", 11, "bold"), 
             bg="#1a1a1a", fg="#00d4aa").pack(anchor='w', padx=15, pady=(10, 5))

    ads_container = tk.Frame(ads_section, bg="#1a1a1a")
    ads_container.pack(fill='x', padx=10, pady=(0, 10))

    for i in range(3):
        ad_frame = tk.Frame(ads_container, bg="#2a2a2a", relief="solid", bd=1, 
                           width=200, height=80)
        ad_frame.pack(side='left', expand=True, fill='both', padx=5, pady=5)
        ad_frame.pack_propagate(False)
        
        ad_label = tk.Label(ad_frame, text=f"Ad Space {i+1}\nYour Ad Here", 
                           font=("Segoe UI", 9), bg="#2a2a2a", fg="#888",
                           justify='center')
        ad_label.pack(expand=True)

    # Footer
    footer = tk.Frame(scrollable_frame, bg="#0f0f0f")
    footer.grid(row=7, column=0, sticky="ew", padx=20, pady=20)
    footer.grid_columnconfigure(0, weight=1)

    tk.Label(footer, text=f"© {OWNER} | YouTube Downloader Pro v1.0", 
             font=("Segoe UI", 9), bg="#0f0f0f", fg="#555").pack()

    # Update scrollregion when window is resized
    def update_scrollregion(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    scrollable_frame.bind("<Configure>", update_scrollregion)
    root.bind("<Configure>", update_scrollregion)

    # Mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    canvas.bind("<MouseWheel>", on_mousewheel)
    scrollable_frame.bind("<MouseWheel>", on_mousewheel)

    # Responsive behavior
    def on_resize(event):
        if event.widget != root:
            return
        new_width = max(400, event.width - 100)
        title_label.config(wraplength=new_width)
        
        if event.width < 600:
            for child in ads_container.winfo_children():
                child.pack_configure(side='top', fill='x', pady=2, padx=5)
        else:
            for child in ads_container.winfo_children():
                child.pack_configure(side='left', expand=True, fill='both', padx=5, pady=5)
    
    root.bind("<Configure>", on_resize)

    # Start setup
    if not os.path.exists(FFMPEG_EXE):
        threading.Thread(target=install_ffmpeg, daemon=True).start()
    install_ytdlp()

    # Initialize with current size
    root.after(100, lambda: on_resize(type('obj', (object,), {'widget': root, 'width': root.winfo_width()})))

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()

if __name__ == "__main__":
    create_gui()