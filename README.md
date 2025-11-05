# YouTube Downloader Pro – **The Ultimate YouTube Toolkit**

> **Download videos, audio, and more — with a single click. No Python needed.**

![YouTube Downloader Pro](https://img.shields.io/badge/YouTube%20Downloader%20Pro-v1.0-red?style=for-the-badge&logo=youtube&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg?style=for-the-badge&logo=python)
![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
![Cross Platform](https://img.shields.io/badge/Windows%20%7C%20macOS-00d4aa?style=for-the-badge)

---

## Download (No Installation Required)

### Windows Users
**Click below to download the standalone `.exe` file:**

[Download YouTube Downloader Pro.exe](https://raw.githubusercontent.com/Rupesh9369/ytdownloaderpro/refs/heads/main/YouTube%20Downloader%20Pro.exe)

> Double-click to run. First launch auto-downloads FFmpeg (30 seconds).

### macOS Users
Coming soon!  
Check [Releases](https://github.com/Rupesh9369/ytdownloaderpro/releases) for `.app` bundle.

---

## Features

| Feature | Status |
|--------|--------|
| Video + Audio Download (MP4) | Done |
| Audio Only (MP3) with Bitrate | Done |
| Quality Selection + File Size Preview | Done |
| Real-Time Progress Bar | Done |
| Dark Theme GUI | Done |
| Auto FFmpeg Setup | Done |
| Windows `.exe` (Portable) | Done |
| macOS `.app` (Bundle) | In Progress |

---

## For New Users (Zero Setup)

### Step 1: Download
Click the **Windows download link above**.

### Step 2: Run
1. Double-click `YouTube Downloader Pro.exe`
2. **First run**: It will download `ffmpeg.exe` (~30 MB) — wait 30 seconds
3. Done! App opens.

### Step 3: Use
1. Paste any YouTube link
2. Click **"LOAD VIDEO"**
3. Choose:
   - `Video + Audio` → MP4
   - `Audio Only (MP3)` → Shows quality + size
4. Click **"DOWNLOAD NOW"**
5. Pick save folder → Done!

> **No Python, no admin rights, no installers.**

---

## For Developers (Contribute & Extend)

> **You are allowed and encouraged to rebuild, modify, and improve this tool!**  
> MIT License — Free for personal & commercial use.

### Run from Source

```bash
# Clone repo
git clone https://github.com/Rupesh9369/ytdownloaderpro.git
cd ytdownloaderpro

# Install dependencies
pip install -r requirements.txt

# Run app
python ytprodownloaderpro.py
```

### Rebuild Executables

#### Windows (.exe)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --name="YouTube Downloader Pro" ytprodownloaderpro.py
```

#### macOS (.app)
```bash
pip3 install pyinstaller
pyinstaller --onefile --windowed --icon=icon.png --name="YouTube Downloader Pro" ytprodownloaderpro.py
```

---

### Project Structure

```
ytdownloaderpro/
├── ytprodownloaderpro.py     # Main GUI + logic
├── icon.ico                  # Windows icon
├── icon.png                  # macOS icon (1024x1024)
├── requirements.txt          # yt-dlp, Pillow, requests
├── LICENSE                   # MIT License
├── README.md                 # This file
└── .github/
    └── workflows/
        └── build.yml         # Auto-builds .exe & .app
```

---

### Contribute (Make It a Full YouTube Toolkit!)

We’re building the **ultimate YouTube tool** — help us add:

| Feature | Difficulty |
|--------|------------|
| Channel Info (Subs, Logo, Banner) | Easy |
| Live Subscriber Counter | Medium |
| Playlist Bulk Download | Easy |
| Export to CSV/JSON | Easy |
| Video Tags & Description Scraper | Easy |
| Search & Trending Videos | Medium |
| Thumbnail Downloader | Easy |

#### How to Help
1. Fork this repo
2. Create branch: `git checkout -b feature/live-subcount`
3. Code → Test → Commit
4. Push & Open Pull Request

> All contributors get credit in `CONTRIBUTORS.md`!

---

## Roadmap

| Version | Features |
|--------|----------|
| **v1.0** | Video/Audio Downloader (Done) |
| **v2.0** | Channel Info + Logo/Banner |
| **v3.0** | Live Sub Count + Charts |
| **v4.0** | Full Analytics Dashboard |
| **v5.0** | 100+ Feature Toolkit |

---

## Acknowledgments

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** – Best YouTube downloader
- **[PyInstaller](https://pyinstaller.org/)** – For `.exe` & `.app`
- **[GitHub Actions](https://github.com/features/actions)** – Free macOS builds
- **You** – For using and improving this tool!

---

## License

**MIT License** – Free to use, modify, and distribute.  
See [`LICENSE`](LICENSE) for details.

---

> **Star this repo** if you like it!  
> **Fork & Build** the future of YouTube tools with us!  
> **Report bugs** or **request features** via [Issues](https://github.com/Rupesh9369/ytdownloaderpro/issues)

---

**Made with passion by [Rupesh Sharma](https://github.com/Rupesh9369)**  
**Let’s make the best YouTube tool ever — together!**

--- 

**Download Now** → [Windows .exe](https://raw.githubusercontent.com/Rupesh9369/ytdownloaderpro/refs/heads/main/YouTube%20Downloader%20Pro.exe)  
**Join the Revolution** → [Contribute](#-for-developers)