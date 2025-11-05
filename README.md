# YouTube Downloader Pro – **The Ultimate YouTube Toolkit**

> **A powerful, open-source, cross-platform desktop app** that goes **far beyond video downloading** — it's your **all-in-one YouTube research, analysis, and content tool**.

![YouTube Downloader Pro](https://img.shields.io/badge/YouTube%20Downloader%20Pro-v1.0-red?style=for-the-badge&logo=youtube&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=for-the-badge&logo=python)
![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
![Cross Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-00d4aa?style=for-the-badge)

---

## Features (Current & Future Roadmap)

| Feature | Status | Description |
|-------|--------|-----------|
| **Video + Audio Download** | Done | MP4 + MP3 with quality/size preview |
| **Audio Formats & Bitrate** | Done | Real-time audio options when MP3 selected |
| **Auto FFmpeg Setup** | Done | One-time download, no manual install |
| **Dark Theme UI** | Done | Responsive, scrollable, modern look |
| **Windows .exe & macOS .app** | Done | Built via GitHub Actions |
| **Title, Description, Tags Scraper** | Coming | Copy metadata with one click |
| **Channel Info Panel** | Coming | Subs, views, join date, country |
| **Channel Logo & Banner Downloader** | Coming | Save HD logo + banner |
| **Live Subscriber Counter** | Coming | Real-time subcount with chart |
| **All Videos List** | Coming | Export titles, views, dates |
| **Video Analytics Dashboard** | Coming | Views over time, engagement |
| **Bulk Download from Playlist** | Coming | Entire playlists in one go |
| **Search & Trending Explorer** | Coming | Browse trending videos |
| **Export to CSV/JSON** | Coming | For data analysis |
| **100+ Features Planned** | In Progress | Full YouTube Toolkit |

---

## User Guide – From Zero to Pro

### For Regular Users (No Coding)

#### Option 1: **Download Pre-Built App** (Recommended)

> No Python, no setup — just double-click and go!

1. Go to **[Releases](https://github.com/Rupesh9369/ytdownloaderpro/releases)**
2. Download:
   - **Windows**: `YouTube Downloader Pro.exe`
   - **macOS**: `YouTube Downloader Pro.app`
3. Run it!
   - **Windows**: Double-click `.exe`
   - **macOS**: Drag `.app` to Applications → Right-click → Open (first time)

> First run: It will **auto-download FFmpeg** (one-time, 30 seconds).

---

#### Option 2: **Run with Python** (If you have Python)

> Perfect for developers or advanced users.

##### Step 1: Install Python
- **Windows**: [python.org](https://www.python.org/downloads/) → Check **"Add to PATH"**
- **macOS**: Already has Python, or install via [Homebrew](https://brew.sh): `brew install python`

##### Step 2: Clone & Install
```bash
git clone https://github.com/Rupesh9369/ytdownloaderpro.git
cd ytdownloaderpro
pip install -r requirements.txt
```

##### Step 3: Run
```bash
python ytprodownloaderpro.py
```

---

### How to Use (Step-by-Step)

1. **Paste YouTube URL**
   - Video: `https://youtube.com/watch?v=...`
   - Channel: `https://youtube.com/@ChannelName`
   - Playlist: `https://youtube.com/playlist?...`

2. **Click "LOAD VIDEO"**
   - Wait 2–5 seconds → Title appears

3. **Choose Download Type**
   - `Video + Audio` → MP4
   - `Audio Only (MP3)` → Shows audio formats + size

4. **Select Quality**
   - Shows resolution + file size (e.g., `1080p - 120MB`)

5. **Click "DOWNLOAD NOW"**
   - Choose folder → Download starts
   - Real-time progress bar

6. **Done!** File saved with clean name.

---

## Developer Guide – Rebuild, Extend, Contribute

> **You are allowed and encouraged to rebuild, modify, and add features!**  
> This is **open source under MIT License** — make it **even better**.

### Rebuild the App Locally

#### Windows (.exe)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --name="YouTube Downloader Pro" ytprodownloaderpro.py
```

#### macOS (.app)
```bash
pip3 install pyinstaller
pyinstaller --onefile --windowed --icon=icon.png --name="YouTube Downloader Pro" ytprodownloaderpro.py
mv dist/YouTube\ Downloader\ Pro.app ./
```

---

### Add New Features (Examples)

#### 1. **Scrape Title, Description, Tags**
```python
info = ydl.extract_info(url, download=False)
title = info['title']
desc = info['description']
tags = ', '.join(info['tags'])
```

#### 2. **Channel Info from Channel URL**
```python
if 'channel' in url or '@' in url:
    info = ydl.extract_info(url, download=False)
    channel_name = info['uploader']
    subs = info.get('subscriber_count', 'N/A')
    logo_url = info.get('uploader_url') + '/photo.jpg'
```

#### 3. **Download Channel Logo**
```python
urllib.request.urlretrieve(logo_url, "channel_logo.jpg")
```

#### 4. **Live Sub Count (API)**
Use [YouTube Data API v3](https://developers.google.com/youtube/v3) or [Social Blade API].

---

### Project Structure
```
ytdownloaderpro/
├── ytprodownloaderpro.py     # Main GUI + logic
├── icon.ico                  # Windows icon
├── icon.png                  # macOS icon
├── requirements.txt          # pip dependencies
├── LICENSE                   # MIT License
├── README.md                 # This file
└── .github/workflows/build.yml  # Auto-builds .exe & .app
```

---

### Contribute & Make It a **Full YouTube Toolkit**

We need **100+ features** — here’s how **you** can help:

| Feature | Difficulty | Status |
|--------|-----------|--------|
| Playlist Downloader | Easy | Open |
| Live Sub Count Chart | Medium | Open |
| Export to CSV | Easy | Open |
| Dark/Light Mode Toggle | Easy | Open |
| Search YouTube | Medium | Open |
| Video Thumbnail Downloader | Easy | Open |
| Comments Scraper | Hard | Open |

#### How to Contribute
1. **Fork** this repo
2. Create branch: `git checkout -b feature/live-subcount`
3. Code → Test → Commit
4. Push & **Open Pull Request**

> All contributors get credit in `CONTRIBUTORS.md`!

---

## Roadmap to **YouTube Toolkit Pro**

| Phase | Goal |
|------|------|
| **v1.0** | Video + Audio Downloader (Done) |
| **v2.0** | Channel Info + Logo/Banner |
| **v3.0** | Live Sub Count + Charts |
| **v4.0** | Full Analytics Dashboard |
| **v5.0** | 100+ Features Toolkit |

---

## Acknowledgments

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** – The best YouTube downloader engine
- **[PyInstaller](https://pyinstaller.org/)** – For `.exe` & `.app` builds
- **[GitHub Actions](https://github.com/features/actions)** – Free macOS builds
- **You** – For using, sharing, and improving this tool!

---

## License

**MIT License** – Free to use, modify, and distribute.  
See [`LICENSE`](LICENSE) for details.

---

> **Star this repo** if you like it!  
> **Fork & Build** the ultimate YouTube Toolkit with us!  
> **Report bugs** or **request features** via [Issues](https://github.com/Rupesh9369/ytdownloaderpro/issues)

---

**Made with passion by [Rupesh Sharma](https://github.com/Rupesh9369)**  
**Let’s make the best YouTube tool ever — together!**

--- 

**Download Now** → [Latest Release](https://github.com/Rupesh9369/ytdownloaderpro/releases/latest)  
**Join the Revolution** → [Contribute](#-developer-guide)