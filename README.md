# 🎵 FLAC → MP3 批量转换工具

> 一个**零依赖、零环境污染**的本地批量音频转换小工具。
> 把 `flac/` 里的 FLAC 一键转成 MP3，FFmpeg 直接打包在项目目录里——不写系统目录、不碰 PATH、不污染你的 Python 环境，删掉文件夹就彻底卸载。

[English](#english) · [特性](#-特性) · [快速开始](#-快速开始) · [参数](#-命令行参数) · [常见问题](#-常见问题)

---

## ✨ 特性

- **一键转换** —— 双击 `convert.bat` 即可，不需要任何命令行基础。
- **零环境污染** —— FFmpeg 放在项目内的 `bin/`，不写入系统目录、不修改 `PATH`、不写注册表。
- **零 Python 依赖** —— 只用 Python 标准库，不需要 `pip install` 任何东西。
- **保留元数据** —— 歌名、歌手、专辑、内嵌封面全部保留。
- **保持目录结构** —— `flac/` 下的子文件夹会原样镜像到 `mp3/`。
- **顺手整理** —— `flac/` 里混进来的 MP3 也会一并收集到 `mp3/`（源文件保留，不删除）。
- **智能跳过** —— 已经转换过的文件不会重复劳动（除非加 `--force`）。
- **并行加速** —— 默认 4 个文件同时转换，大批量也不慢。

---

## 📁 目录结构

```text
music_convert/
├── convert.bat          # Windows 双击入口
├── convert.py           # 转换程序本体（纯标准库）
├── README.md            # 你正在看的这份说明
├── .gitignore           # 忽略音乐文件和 FFmpeg 二进制
├── bin/
│   └── ffmpeg.exe       # 转换核心（仅存在于本地，不进 git）
├── flac/                # 放待转换的源文件
└── mp3/                 # 转换结果输出到这里
```

---

## 🚀 快速开始

### Windows（最省事）

1. 把要转换的 `.flac` 文件丢进 `flac/` 文件夹（可以建子文件夹）。
2. **双击 `convert.bat`**。
3. 转换好的 MP3 会出现在 `mp3/` 文件夹里。默认 320 kbps 高音质。

> 第一次使用需要先获取 FFmpeg，见下方 [获取 FFmpeg](#-获取-ffmpeg)。

### macOS / Linux

```bash
# 1. 安装 ffmpeg（macOS）
brew install ffmpeg
# 或 Linux (Debian/Ubuntu)
sudo apt install ffmpeg

# 2. 把 .flac 放进 flac/，然后运行
python3 convert.py
```

> 非 Windows 平台请把 `convert.py` 顶部的 `FFMPEG` 路径改成你系统里的 `ffmpeg`
> （例如 `FFMPEG = "ffmpeg"`），其余逻辑完全一致。

---

## ⚙️ 命令行参数

在 `convert.bat` 所在文件夹按住 `Shift` + 右键，选「在此处打开终端」，然后：

```bash
python convert.py                       # 转换 flac/ 下所有 .flac 到 mp3/
python convert.py --bitrate 192k       # 换成 192 kbps（文件更小）
python convert.py --bitrate V0         # 可变码率，音质更好、体积更小
python convert.py --force              # 已转过的文件也重新转一遍
python convert.py --workers 2          # 同时只转 2 个（电脑卡时可用）
python convert.py --no-copy-mp3        # 只转 FLAC，不顺手收集 flac 里已有的 mp3
```

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--bitrate` | MP3 码率，可选 `192k` / `256k` / `320k` / `V0` | `320k` |
| `--force` | 覆盖 `mp3/` 里已存在的同名文件 | 关（默认跳过） |
| `--workers` | 同时转换的文件数 | `4` |
| `--no-copy-mp3` | 只转 FLAC，不顺手复制 `flac/` 里已有的 mp3 | 关（默认**会**复制） |

---

## 🎨 关于音质与封面

- **音质**：默认 320 kbps CBR，是 MP3 格式的最高档，日常听感几乎无损。想要更小体积用
  `--bitrate 192k`；想要更聪明地省空间用 `--bitrate V0`（lame 可变码率）。
- **封面**：FLAC 内嵌的封面会以**原样**复制到 MP3（不会重新压缩）。所以如果原文件是
  一张 3000×3000 的高清图，MP3 也会保留这张大图、体积会相应大一些——这是正常现象，
  不是 bug。

---

## 🔧 获取 FFmpeg

本项目**不把 FFmpeg 二进制提交进 git**（约 98 MB，不适合放仓库）。两种获取方式：

### 方式一：从官网下载（推荐）

1. 打开 [gyan.dev FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/)。
2. 下载 **`ffmpeg-release-essentials.zip`**。
3. 解压，把里面的 `bin/ffmpeg.exe` 复制到本项目的 `bin/` 文件夹下即可。

（macOS / Linux 用户直接用系统包管理器安装，见上方快速开始。）

### 方式二：从 Release 页面下载

本项目的 GitHub **Releases** 里提供了已打包好 `bin/ffmpeg.exe` 的完整压缩包，
下载解压即可直接使用，无需自己找 FFmpeg。

> 已在本机运行过本工具的人不受影响——你本地的 `bin/ffmpeg.exe` 一直在，照常工作。

---

## ❓ 常见问题

**Q：`flac/` 里本来就是 MP3 的文件会怎样？**
A：默认会顺手把它们也复制到 `mp3/`（源文件保留、不删除），并自动保持子文件夹结构。
如果只想转 FLAC、完全不碰这些 mp3，加 `--no-copy-mp3` 参数即可。

**Q：双击 `convert.bat` 后窗口一闪就没了？**
A：程序报错了但窗口太快关闭。请手动打开终端看原因：
按住 `Shift` + 右键 → 打开终端 → 输入 `python convert.py`。

**Q：提示找不到 Python？**
A：去 [python.org](https://www.python.org/downloads/) 下载安装，
安装时**务必勾选「Add Python to PATH」**。

**Q：为什么有的 MP3 比别的大一圈？**
A：如果 FLAC 内嵌了高清封面（比如 3000×3000 的图），封面会原样保留到 MP3 里，
占几 MB。这是正常的。

**Q：转换很慢是为什么？**
A：FLAC 是无损格式，解码需要时间。一般一首 5 分钟的歌 10~30 秒；文件多的时候会
4 个同时转，是正常的。

---

## 📜 许可证

- 本工具的代码以 **MIT License** 发布，可自由使用、修改、分发。
- [FFmpeg](https://ffmpeg.org/) 是独立项目，遵循 **GPL** 许可证。本工具仅调用其可执行文件，
  未修改、未链接其源码。请遵守 FFmpeg 的许可条款。

---

## English

### FLAC → MP3 Batch Converter

A zero-dependency, zero-pollution local batch audio converter. Drop your `.flac`
files into `flac/`, double-click `convert.bat` (Windows) and get 320 kbps MP3s in
`mp3/`. FFmpeg ships inside the project's `bin/` folder — it never touches your
system `PATH` or registry, and deleting the folder fully uninstalls the tool.

**Highlights**

- One-click on Windows, or `python3 convert.py` anywhere.
- No `pip install` needed — pure Python standard library.
- Keeps tags and embedded cover art; mirrors the subfolder layout.
- Also collects pre-existing MP3s from `flac/` into `mp3/` (source kept).
- Skips already-converted files unless `--force`.

**Get FFmpeg:** download `ffmpeg-release-essentials.zip` from
[gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and place `bin/ffmpeg.exe` into
this project's `bin/`. On macOS/Linux use your package manager and point the
`FFMPEG` variable in `convert.py` at your `ffmpeg`.

See the Chinese sections above for the full parameter table and FAQ.
