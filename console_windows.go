package main

import (
	"syscall"
	"unsafe"
)

var kernel32 = syscall.NewLazyDLL("kernel32.dll")

// 讓 cmd 視窗正確顯示中文
func setupConsole() {
	kernel32.NewProc("SetConsoleOutputCP").Call(65001)
	kernel32.NewProc("SetConsoleCP").Call(65001)
}

// 雙擊或拖放開啟時，主控台只有這個程式在用；從 cmd 執行時還有 cmd 本身
func consoleOwnedByUs() bool {
	ids := make([]uint32, 4)
	n, _, _ := kernel32.NewProc("GetConsoleProcessList").Call(
		uintptr(unsafe.Pointer(&ids[0])), uintptr(len(ids)))
	return n == 1
}
