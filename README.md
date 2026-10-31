# log-time

從 LOG 裡抓 `HH:MM:SS` 時間（例如 `00:01:44`），報出**開始、結束、總共時間**。

## 下載
直接下載 [`log-time.exe`](log-time.exe)（Windows 64 位元，不用安裝）。

## 用法
- **拖放**：把 LOG 檔拖到 `log-time.exe` 上，跑完按 Enter 關閉
- **雙擊**：開啟後輸入（或拖入）LOG 檔路徑，按 Enter
- **命令列**：
  ```
  log-time.exe run.log
  log-time.exe a.log b.log
  type run.log | log-time.exe
  ```

## 輸出範例
```
== run.log
  開始：00:01:44（第 2 行）
  結束：00:09:03（第 9 行）
  總共：00:07:19
  （共 8 筆時間）
```

## 規則
- 每行取第一個 `HH:MM:SS`（或 `H:MM:SS`），沒有時間的行略過；前後有 `[ ]` 等字元沒關係
- 時間比上一個小 → 視為跨過午夜，加 24 小時
- 總共時間＝最後一個時間 − 第一個時間

## 自己編譯
需要 Go 1.24 以上：
```
GOOS=windows GOARCH=amd64 go build -trimpath -ldflags="-s -w" -o log-time.exe .
```
