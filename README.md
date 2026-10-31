# log-time

[![build](https://github.com/imalextaiwan/log-time/actions/workflows/build.yml/badge.svg)](https://github.com/imalextaiwan/log-time/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

從 LOG 裡抓 `HH:MM:SS` 時間（例如 `00:01:44`），報出**開始、結束、總共時間**。

*English: a small Windows tool (Python, packaged with PyInstaller) that reads a log file, finds `HH:MM:SS` timestamps, and prints the start time, end time and total duration (handles midnight rollover). Drag a log file onto `log-time.exe`, or run `log-time.exe file.log`.*

## 下載
**[下載 log-time.exe](https://github.com/imalextaiwan/log-time/releases/latest/download/log-time.exe)**（Windows 10／11 64 位元，不用安裝）

其他版本與 SHA-256 在 [Releases](https://github.com/imalextaiwan/log-time/releases)。

> 沒有數位簽章，第一次開啟若出現「Windows 已保護您的電腦」，按「其他資訊」→「仍要執行」。

有 Python 3.8 以上也可以不用 EXE：`python log_time.py run.log`

## 用法
| 方式 | 做法 |
|---|---|
| 拖放 | 把 LOG 檔拖到 `log-time.exe` 的圖示上，跑完按 Enter 關閉 |
| 雙擊 | 開啟後輸入或拖入 LOG 檔路徑（可一次拖多個），按 Enter；算完可以接著輸入下一個，直接按 Enter 結束 |
| 命令列 | `log-time.exe run.log`、`log-time.exe a.log b.log`、`type run.log \| log-time.exe` |

## 輸出範例
[`examples/sample.log`](examples/sample.log)：
```
[00:01:44] 開始處理
[00:02:10] 讀取設定
[00:05:31] 第 1 批完成
[00:09:03] 全部完成
```
```
> log-time.exe examples\sample.log
== examples\sample.log
  開始：00:01:44（第 1 行）
  結束：00:09:03（第 4 行）
  總共：00:07:19
  （共 4 筆時間）
```

跨午夜（[`examples/overnight.log`](examples/overnight.log)，23:58:02 → 00:03:09）：
```
  開始：23:58:02（第 1 行）
  結束：00:03:09（第 4 行）
  總共：00:05:07
  （共 4 筆時間，跨午夜 1 次）
```

## 規則
- 每行取**第一個** `HH:MM:SS`（或 `H:MM:SS`），沒有時間的行略過；前後有 `[ ]`、日期、毫秒都沒關係
- 時間比上一個小 → 視為跨過午夜，加 24 小時
- 總共時間＝最後一個時間 − 第一個時間
- 編碼自動判斷：UTF-8、UTF-16（有無 BOM）、Big5
- 路徑有空白、中文、引號都可以

## 自己編譯
需要 Python 3.8 以上，在 Windows 上：
```
python -m unittest discover -s tests
pip install pyinstaller
pyinstaller --onefile --console --name log-time log_time.py
```
EXE 在 `dist\log-time.exe`。推送到 `main` 時，GitHub Actions 會在 Windows 上自動測試、編譯、實際執行一次，並依 `log_time.py` 的 `__version__` 發布到 Releases（含 `.sha256`）。

## 授權
[MIT](LICENSE)
