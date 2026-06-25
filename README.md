# BiliEasy - B站视频下载工具

**一个免费、开源的 B站视频下载工具，让你轻松保存喜爱的视频。**

---

## ✨ 功能亮点

- 🎬 **多清晰度下载**：支持 1080p / 720p / 480p / 360p
- 📂 **批量下载**：支持合集下载、指定集数下载、收藏夹批量下载
- 💬 **弹幕支持**：
  - 下载弹幕并保存为独立文件
  - 将弹幕**烧录/硬字幕**嵌入视频画面
- 🎵 **保留原始文件**：可选择保留音频和视频原文件，方便二次处理
- 🖥️ **Windows 原生体验**：提供可直接运行的 `.exe` 文件直接使用即可，无需安装 Python

---

## 🛠️ 技术栈

- **语言**：Python
- **界面框架**：PyQt6
- **核心**：爬虫,弹幕protobuf解析

---
## 🎬 功能演示

观看视频了解 BiliEasy 的完整使用教程（B站）：
[点击观看：BiliEasy 使用教程]
https://www.bilibili.com/video/BV1eejE6SEPx/?spm_id_from=333.1387.homepage.video_card.click&vd_source=726e4efb47a201228fe295f8e1d6e5c2

## 🚀 快速开始

### 方式一：直接下载 EXE（推荐）
1. 前往右侧 **Releases** 页面
2. 下载最新版本的 `.exe` 文件
3. 双击运行，无需任何配置



### 方式二：源码运行（适合有Python基础的用户）
> ⚠️ 如果你只是想用这个工具，建议直接下载上面的 EXE 版本，exe版本已经将ffmpeg打包进去了,无需安装任何环境。
### ⚠️ 重要：使用前请先安装 ffmpeg

使用源码下载视频后需要将音频和视频合并为一个完整的 MP4 文件，这个过程依赖外部工具 **ffmpeg**。

**如果你的电脑没有安装 ffmpeg，下载的视频将无法合并，会分别保存为 `.mp4`（无声音）和 `.m4a`（纯音频）两个文件。**

---

### 如何安装 ffmpeg？

**方法一：直接下载 exe 文件**

1. 访问 ffmpeg 官方下载页面：https://ffmpeg.org/download.html
2. 找到 Windows 版本，点击 **"Windows builds"**（或直接访问 https://www.gyan.dev/ffmpeg/builds/）
3. 下载最新版本的 **ffmpeg-release-full.7z** 或 **ffmpeg-release-full.zip**
4. 解压后，进入 `bin` 文件夹，找到 `ffmpeg.exe`
5. 将 `ffmpeg.exe` **复制或剪切**到python文件的同一目录下（和 `main.py`  放在一起）

如果你希望从源码运行，请按以下步骤操作：

**第一步：安装 Python**

1. 访问 https://www.python.org/downloads/
2. 点击黄色的 **Download Python 3.10.x**（或更高版本）
3. 下载完成后，双击安装包
4. **⚠️ 重要：** 安装时务必勾选 **"Add Python to PATH"**（添加到环境变量）
5. 点击 "Install Now" 完成安装
如果没把握可以在bilibili上搜索python安装教程

**第二步：下载本项目代码**

1. 在 GitHub 项目页面，点击绿色的 **"Code"** 按钮
2. 选择 **"Download ZIP"**
3. 下载完成后，解压到任意文件夹

**第三步：安装依赖库（推荐使用 PyCharm / VSCode）**

如果你有 PyCharm 或 VSCode，在软件里打开项目文件夹后，IDE 通常会自动识别并提示安装 requirements.txt 里的依赖，比手动敲命令行更方便。

```bash
pip install -r requirements.txt
```
**第四步：运行(使用 PyCharm / VSCode)直接运行main.py文件即可**
