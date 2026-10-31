#!/usr/bin/env python3
"""log-time：從 LOG 抓 HH:MM:SS 時間，報出開始、結束、總共時間。

用法：
  log-time.exe run.log             一個檔
  log-time.exe a.log b.log         每個檔各算一次
  把 LOG 檔拖到 log-time.exe 上      同上，跑完按 Enter 關閉
  直接雙擊 log-time.exe             輸入（或拖入）檔案路徑，可以一直算下一個
  python log_time.py run.log       沒有 EXE 時直接用 Python 跑

規則：
- 每行取第一個 HH:MM:SS（或 H:MM:SS），沒有時間的行略過
- 時間比上一個小 → 視為跨過午夜，加 24 小時
- 總共時間＝最後一個時間 − 第一個時間
- 編碼自動判斷：UTF-8、UTF-16（有無 BOM）、Big5（cp950）
"""
import os
import re
import sys

__version__ = '1.1.0'

TIME_RE = re.compile(r'(?<!\d)(\d{1,2}):([0-5]\d):([0-5]\d)(?!\d)')


def fmt(sec):
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f'{h:02d}:{m:02d}:{s:02d}'


def scan(lines):
    """回傳 dict（first, last, first_no, last_no, count, wraps）；沒有時間回傳 None。"""
    res = None
    day = 0
    prev = None
    for no, line in enumerate(lines, 1):
        m = TIME_RE.search(line)
        if not m:
            continue
        h, mi, s = map(int, m.groups())
        if h > 23:
            continue
        t = h * 3600 + mi * 60 + s
        if prev is not None and t < prev:
            day += 1
        prev = t
        abs_t = day * 86400 + t
        if res is None:
            res = {'first': abs_t, 'first_no': no, 'count': 0}
        res['last'], res['last_no'] = abs_t, no
        res['count'] += 1
        res['wraps'] = day
    return res


def decode(data):
    """把檔案內容轉成文字，自動判斷編碼。"""
    if data.startswith(b'\xef\xbb\xbf'):
        return data[3:].decode('utf-8', errors='replace')
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        return data.decode('utf-16', errors='replace')
    head = data[:4096]
    if head and head.count(b'\x00') > len(head) // 4:
        # 沒有 BOM 的 UTF-16：0 位元組在奇數位置是 LE，偶數位置是 BE
        le = head[1::2].count(b'\x00') >= head[0::2].count(b'\x00')
        return data.decode('utf-16-le' if le else 'utf-16-be', errors='replace')
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return data.decode('cp950', errors='replace')


def report(name, text):
    print(f'== {name}')
    r = scan(text.splitlines())
    if r is None:
        print('  找不到 HH:MM:SS 時間')
        return
    print(f'  開始：{fmt(r["first"] % 86400)}（第 {r["first_no"]} 行）')
    print(f'  結束：{fmt(r["last"] % 86400)}（第 {r["last_no"]} 行）')
    print(f'  總共：{fmt(r["last"] - r["first"])}')
    extra = f'，跨午夜 {r["wraps"]} 次' if r['wraps'] else ''
    print(f'  （共 {r["count"]} 筆時間{extra}）')


def report_file(path):
    try:
        with open(path, 'rb') as f:
            data = f.read()
    except OSError as e:
        print(f'== {path}\n  開不了檔案：{e.strerror or e}')
        return
    report(path, decode(data))


def parse_paths(line):
    """把輸入的一行拆成路徑。整行是一個存在的檔就直接用；否則拆引號，拖入多個檔時會是 "a b.log" "c.log"。"""
    line = line.strip()
    if not line:
        return []
    bare = line.strip('"\'')
    if os.path.isfile(bare):
        return [bare]
    if '"' in line:
        return [a or b for a, b in re.findall(r'"([^"]+)"|(\S+)', line)]
    return [bare]


def interactive_loop():
    print(f'log-time {__version__}：算 LOG 的開始、結束、總共時間')
    while True:
        try:
            line = input('\n請輸入或拖入 LOG 檔案路徑，按 Enter（直接按 Enter 結束）：')
        except (EOFError, KeyboardInterrupt):
            return
        paths = parse_paths(line)
        if not paths:
            return
        for p in paths:
            report_file(p)


def launched_by_double_click():
    """Windows 上雙擊或拖放開啟時，主控台只有這個程式在用；從 cmd 執行時還有 cmd 本身。"""
    if os.name != 'nt':
        return False
    try:
        import ctypes
        ids = (ctypes.c_uint32 * 8)()
        return ctypes.windll.kernel32.GetConsoleProcessList(ids, 8) <= 2  # PyInstaller 的啟動程式也算一個
    except Exception:
        return False


def main(argv):
    if argv and argv[0] in ('-v', '--version'):
        print(__version__)
        return
    if argv:
        for p in argv:
            report_file(p)
        if launched_by_double_click():
            try:
                input('\n按 Enter 關閉…')
            except (EOFError, KeyboardInterrupt):
                pass
        return
    if not sys.stdin.isatty():
        report('stdin', decode(sys.stdin.buffer.read()))
        return
    interactive_loop()


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(errors='replace')
    main(sys.argv[1:])
