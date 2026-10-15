# -*- coding: utf-8 -*-
"""
FLAC -> MP3 批量转换工具

用法:
    python convert.py                 转换 flac/ 下所有 .flac 到 mp3/
    python convert.py --bitrate 320k  指定码率（默认 320k，可选 192k / 256k / V0）
    python convert.py --force         已存在同名 mp3 时也重新转换
    python convert.py --workers 4     4 个文件同时转换（默认 4）
    python convert.py --no-copy-mp3  只转 FLAC，不顺手复制 flac 里已有的 mp3

所有依赖都在本项目内：
    - bin/ffmpeg.exe  （转换程序，不会写入系统任何位置）
    - Python 标准库   （不需要 pip 安装任何东西）
"""

import argparse
import os
import subprocess
import sys
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 让 Windows 控制台正确显示中文
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ---------------------------------------------------------------- 路径设定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG = os.path.join(BASE_DIR, "bin", "ffmpeg.exe")
SRC_DIR = os.path.join(BASE_DIR, "flac")
DST_DIR = os.path.join(BASE_DIR, "mp3")


def human_size(num_bytes):
    """把字节数变成人类可读的形式"""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return "%.1f %s" % (size, unit)
        size /= 1024
    return "%.1f GB" % size


def find_flac_files(src_dir):
    """递归找出 src_dir 下所有 .flac 文件（不区分大小写）"""
    results = []
    for root, _dirs, files in os.walk(src_dir):
        for name in files:
            if name.lower().endswith(".flac"):
                results.append(os.path.join(root, name))
    return sorted(results)


def convert_one(src_path, bitrate, force):
    """转换单个文件，返回 (是否成功, 提示文字)"""
    rel = os.path.relpath(src_path, SRC_DIR)
    dst_path = os.path.join(DST_DIR, os.path.splitext(rel)[0] + ".mp3")
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

    if os.path.exists(dst_path) and not force:
        return True, "跳过（已存在）  %s" % rel

    cmd = [FFMPEG, "-y", "-i", src_path]

    # 只取第一条音轨；封面图（有的话）作为第二路输入原样拷贝。
    # 末尾的 "?" 表示"没有封面就算了"，避免无封面文件时报错。
    cmd += ["-map", "0:a:0", "-map", "0:v:0?"]

    # 码率设置：V0 是 lame 的可变码率最高档，音质接近无损
    if bitrate.upper() == "V0":
        cmd += ["-codec:a", "libmp3lame", "-q:a", "0"]
    else:
        cmd += ["-codec:a", "libmp3lame", "-b:a", bitrate]

    # 封面必须 copy：让 ffmpeg 重新编码的话，一张 3000x3000 的
    # 封面会被放大到好几 MB，比音乐本身还占地方。
    cmd += ["-c:v", "copy"]

    # 保留原文件的标签信息（歌名/歌手/专辑/封面）
    cmd += ["-map_metadata", "0"]
    # ID3v2.3 兼容性最好，Windows 资源管理器和多数播放器都能读封面
    cmd += ["-id3v2_version", "3"]
    # 不显示 ffmpeg 的进度刷屏，只在我们自己的界面里显示
    cmd += ["-nostdin", "-loglevel", "error"]
    cmd += [dst_path]

    start = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    elapsed = time.time() - start

    if proc.returncode != 0:
        err = (proc.stderr or "").strip().splitlines()
        last = err[-1] if err else "未知错误"
        return False, "失败  %s  ->  %s" % (rel, last)

    out_size = os.path.getsize(dst_path) if os.path.exists(dst_path) else 0
    return True, "完成  %s  ->  %s  (%s, %.1f 秒)" % (
        rel,
        os.path.relpath(dst_path, BASE_DIR),
        human_size(out_size),
        elapsed,
    )


def find_mp3_files(src_dir):
    """递归找出 src_dir 下所有 .mp3 文件（不顺手整理时不需要）。"""
    results = []
    for root, _dirs, files in os.walk(src_dir):
        for name in files:
            if name.lower().endswith(".mp3"):
                results.append(os.path.join(root, name))
    return sorted(results)


def copy_mp3_one(src_path, force):
    """把 flac 里原本就是 mp3 的文件，原样复制到 mp3 文件夹（保留源文件）。"""
    rel = os.path.relpath(src_path, SRC_DIR)
    dst_path = os.path.join(DST_DIR, rel)  # 同名，保持子目录结构
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    if os.path.exists(dst_path) and not force:
        return True, "跳过（已存在）  %s" % rel
    shutil.copy2(src_path, dst_path)
    size = os.path.getsize(dst_path)
    return True, "复制  %s  ->  %s  (%s)" % (
        rel,
        os.path.relpath(dst_path, BASE_DIR),
        human_size(size),
    )


def main():
    parser = argparse.ArgumentParser(description="把 flac 文件夹里的 FLAC 全部转成 MP3")
    parser.add_argument("--bitrate", default="320k",
                        help="MP3 码率，默认 320k（可选 192k / 256k / 320k / V0）")
    parser.add_argument("--force", action="store_true",
                        help="覆盖 mp3 文件夹里已存在的同名文件")
    parser.add_argument("--workers", type=int, default=4,
                        help="同时转换几个文件，默认 4")
    parser.add_argument("--no-copy-mp3", action="store_true",
                        help="只转 FLAC，不顺手把 flac 里已有的 mp3 也复制过去")
    args = parser.parse_args()

    print("=" * 56)
    print("  FLAC -> MP3 转换工具")
    print("=" * 56)

    if not os.path.isfile(FFMPEG):
        print("\n[错误] 找不到 %s" % os.path.relpath(FFMPEG, BASE_DIR))
        print("       请确认 bin 文件夹里的 ffmpeg.exe 没有被删除。")
        return 1

    if not os.path.isdir(SRC_DIR):
        print("\n[错误] 找不到 flac 文件夹：%s" % SRC_DIR)
        return 1

    os.makedirs(DST_DIR, exist_ok=True)

    flac_files = find_flac_files(SRC_DIR)
    copy_mp3 = not args.no_copy_mp3
    mp3_files = find_mp3_files(SRC_DIR) if copy_mp3 else []

    total_in = sum(os.path.getsize(f) for f in flac_files)
    print("\nFLAC 文件：%d 个，共 %s" % (len(flac_files), human_size(total_in)))
    if copy_mp3:
        print("MP3 文件（将顺手复制，保留源文件）：%d 个" % len(mp3_files))
    print("输出目录：%s" % DST_DIR)
    print("码率：%s\n" % args.bitrate)
    print("-" * 56)

    start = time.time()
    ok, fail = 0, 0
    failed_list = []

    if flac_files:
        workers = max(1, min(args.workers, len(flac_files)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(convert_one, f, args.bitrate, args.force): f
                       for f in flac_files}
        done = 0
        for fut in as_completed(futures):
            done += 1
            success, msg = fut.result()
            print("[%d/%d] %s" % (done, len(flac_files), msg))
            if success:
                ok += 1
            else:
                fail += 1
                failed_list.append(futures[fut])

    # 2) 顺手把 flac 里原本就是 mp3 的文件也复制过去
    if mp3_files:
        print("-" * 56)
        print("正在整理 flac 里已有的 MP3 ...")
        for i, p in enumerate(mp3_files, 1):
            success, msg = copy_mp3_one(p, args.force)
            print("[%d/%d] %s" % (i, len(mp3_files), msg))
            if success:
                ok += 1
            else:
                fail += 1
                failed_list.append(p)

    print("-" * 56)
    print("全部完成！成功 %d 个，失败 %d 个，用时 %.1f 秒"
          % (ok, fail, time.time() - start))

    if failed_list:
        print("\n以下文件处理失败：")
        for p in failed_list:
            print("  - %s" % p)

    print("\nMP3 已保存到 mp3 文件夹。")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(130)
