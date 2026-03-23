import ctypes
import subprocess
import sys


def read_clipboard_linux():
    try:
        return subprocess.run(["xclip", "-selection", "clipboard", "-o"],
                              capture_output=True, text=True).stdout
    except FileNotFoundError:
        return subprocess.run(["xsel", "--clipboard", "--output"],
                              capture_output=True, text=True).stdout

def read_clipboard_macos():
    return subprocess.run("pbpaste", capture_output=True, text=True).stdout


def read_clipboard_windows():
    CF_UNICODETEXT = 13
    ctypes.windll.user32.OpenClipboard(0)
    handle = ctypes.windll.user32.GetClipboardData(CF_UNICODETEXT)
    text = ctypes.wstring_at(handle)
    ctypes.windll.user32.CloseClipboard()
    return text


def read_clipboard():
    if sys.platform == "win32":
        return read_clipboard_windows()
    elif sys.platform == "darwin":
        return read_clipboard_macos()
    else:
        return read_clipboard_linux()