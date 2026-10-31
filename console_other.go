//go:build !windows

package main

func setupConsole()          {}
func consoleOwnedByUs() bool { return false }
