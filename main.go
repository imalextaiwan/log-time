// log-time：從 LOG 抓 HH:MM:SS 時間，報出開始、結束、總共時間。
//
// 用法：
//
//	log-time.exe run.log            一個檔
//	log-time.exe a.log b.log        每個檔各算一次
//	把 LOG 檔拖到 log-time.exe 上     同上，跑完按 Enter 關閉
//	直接雙擊 log-time.exe            會請你輸入（或拖入）檔案路徑
//
// 規則：
//   - 每行取第一個 HH:MM:SS（或 H:MM:SS），沒有時間的行略過
//   - 時間比上一個小 → 視為跨過午夜，加 24 小時
//   - 總共時間＝最後一個時間 − 第一個時間
package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"regexp"
	"strconv"
	"strings"
)

var timeRe = regexp.MustCompile(`(^|[^0-9])([0-9]{1,2}):([0-5][0-9]):([0-5][0-9])([^0-9]|$)`)

type result struct {
	first, last     int
	firstNo, lastNo int
	count, wraps    int
}

func fmtSec(sec int) string {
	return fmt.Sprintf("%02d:%02d:%02d", sec/3600, sec%3600/60, sec%60)
}

func scan(r io.Reader) (*result, error) {
	var res *result
	sc := bufio.NewScanner(r)
	sc.Buffer(make([]byte, 1024*1024), 64*1024*1024)
	day, prev, no := 0, -1, 0
	for sc.Scan() {
		no++
		m := timeRe.FindStringSubmatch(sc.Text())
		if m == nil {
			continue
		}
		h, _ := strconv.Atoi(m[2])
		mi, _ := strconv.Atoi(m[3])
		s, _ := strconv.Atoi(m[4])
		if h > 23 {
			continue
		}
		t := h*3600 + mi*60 + s
		if prev >= 0 && t < prev {
			day++
		}
		prev = t
		abs := day*86400 + t
		if res == nil {
			res = &result{first: abs, firstNo: no}
		}
		res.last, res.lastNo = abs, no
		res.count++
		res.wraps = day
	}
	return res, sc.Err()
}

func report(name string, r io.Reader) {
	fmt.Printf("== %s\n", name)
	res, err := scan(r)
	if err != nil {
		fmt.Printf("  讀取失敗：%v\n", err)
		return
	}
	if res == nil {
		fmt.Println("  找不到 HH:MM:SS 時間")
		return
	}
	fmt.Printf("  開始：%s（第 %d 行）\n", fmtSec(res.first%86400), res.firstNo)
	fmt.Printf("  結束：%s（第 %d 行）\n", fmtSec(res.last%86400), res.lastNo)
	fmt.Printf("  總共：%s\n", fmtSec(res.last-res.first))
	extra := ""
	if res.wraps > 0 {
		extra = fmt.Sprintf("，跨午夜 %d 次", res.wraps)
	}
	fmt.Printf("  （共 %d 筆時間%s）\n", res.count, extra)
}

func reportFile(path string) {
	f, err := os.Open(path)
	if err != nil {
		fmt.Printf("== %s\n  開不了檔案：%v\n", path, err)
		return
	}
	defer f.Close()
	report(path, f)
}

func isTerminal(f *os.File) bool {
	st, err := f.Stat()
	return err == nil && st.Mode()&os.ModeCharDevice != 0
}

func pause() {
	fmt.Print("\n按 Enter 關閉…")
	bufio.NewReader(os.Stdin).ReadString('\n')
}

func main() {
	setupConsole()
	args := os.Args[1:]
	interactive := isTerminal(os.Stdin)

	if len(args) == 0 && !interactive {
		report("stdin", os.Stdin)
		return
	}
	if len(args) == 0 {
		fmt.Print("請輸入或拖入 LOG 檔案路徑，按 Enter：")
		line, _ := bufio.NewReader(os.Stdin).ReadString('\n')
		line = strings.Trim(strings.TrimSpace(line), `"'`)
		if line == "" {
			return
		}
		args = []string{line}
	}
	for _, p := range args {
		reportFile(p)
	}
	if interactive && consoleOwnedByUs() {
		pause()
	}
}
