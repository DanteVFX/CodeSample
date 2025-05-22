# CodeSample

# ActionVFX-Nuke-Plugin
The plugin connect Nuke to ActionVFX API

# 🎬 ActionVFX Plugin for Nuke (In Development)

This project is a custom Nuke plugin that connects directly to the [ActionVFX](https://www.actionvfx.com/) API. It allows Nuke users to log in, browse, preview, and download high-quality VFX assets without leaving their compositing environment.

---

## 🔧 Current Status

> ⚠️ This project is under active development. The plugin currently supports full API integration, authentication, media previews, and dynamic asset browsing. Download functionality is being finalized.

---

## 📁 Project Structure

| Module | Responsibility |
|--------|----------------|
| `auth.py` | Handles secure login using token-based auth and encrypted local sessions |
| `api_request.py` | Wraps authenticated API requests (`GET`, `POST`) using the stored session |
| `ui_main.py` | Manages login UI, dashboard layout, and navigation |
| `ui_container_base.py` | Base class for paginated grid browsing of assets (2D, FreeFootage, Owned) |
| `ui_items_detail.py` | Displays video preview, thumbnails, description, and resolution options |
| `menu.py` | Integrates plugin into Nuke’s native menu system |

---

## 🧩 Key Features

- 🔐 Secure user authentication with encrypted session storage
- 🎛 PySide2 interface for seamless UI integration in Nuke
- 🎥 Video playback with OpenCV embedded in the UI
- 🖼 Lazy-loading of thumbnails and infinite scroll asset browsing
- 📦 Organized into 3 main libraries:
  - **2D Elements**
  - **FreeFootage**
  - **MyDownloads** (user-owned assets)
- 📥 Resolution variant dropdown for downloads
- 🔌 Direct communication with:
  - `/users/sign_in`
  - `/collections/`
  - `/scenes/`
  - `/ownership/`
  - `/variant_downloads/`

---

## 🚧 In Progress

- Implementing full download logic using correct API endpoints per asset type
- Progress feedback for downloads
- Reducing initial plugin load time in Nuke

---

## 📷 Screenshots




- Free Clips
![loading (1)](https://github.com/user-attachments/assets/0b2090ae-6c8f-48f1-acd3-735b3fa24c53)




---

## 🧑‍💻 Developed By

**Dante Rueda**  
FX Artist & Pipeline Tools Developer  
March 2025

---
