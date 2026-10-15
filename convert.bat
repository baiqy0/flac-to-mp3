@echo off
chcp 65001 >nul
cd /d "%~dp0"
setlocal

rem  ============================================================
rem   FLAC to MP3 Converter  /  FLAC 转 MP3 一键运行
rem
rem   双击这个文件即可。程序会自动把 flac 文件夹里的所有
rem   .flac 转换成 mp3，保存到 mp3 文件夹。
rem
rem   本工具完全独立：ffmpeg 放在 bin 文件夹里，不会往系统
rem   里写任何东西，也不会改动你的 Python 环境。
rem  ============================================================

echo.
echo  Looking for Python...

rem  --- 1. Python launcher (py -3) ---
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -c "import sys" >nul 2>nul
    if %errorlevel%==0 (
        py -3 convert.py %*
        goto :finished
    )
)

rem  --- 2. python on PATH ---
where python >nul 2>nul
if %errorlevel%==0 (
    python convert.py %*
    goto :finished
)

rem  --- 3. WorkBuddy bundled Python ---
if exist "%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe" (
    "%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe" convert.py %*
    goto :finished
)

rem  --- 4. System Python 3.10 ---
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" convert.py %*
    goto :finished
)

echo.
echo  [ERROR] Python not found on this computer.
echo  Please install Python 3 from https://www.python.org/downloads/
echo  (During install, CHECK the box "Add Python to PATH")
echo.
pause
exit /b 1

:finished
echo.
echo  ------------------------------------------------------------
echo  Done. Press any key to close this window.
pause >nul
