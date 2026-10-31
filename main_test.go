package main

import (
	"strings"
	"testing"
)

func TestScan(t *testing.T) {
	cases := []struct {
		name                string
		in                  string
		first, last, total  string
		firstNo, lastNo, ct int
		wraps               int
	}{
		{"basic", "x\n[00:01:44] a\nno time\n[00:09:03] b\n", "00:01:44", "00:09:03", "00:07:19", 2, 4, 2, 0},
		{"midnight", "23:58:02 a\n00:03:09 b\n", "23:58:02", "00:03:09", "00:05:07", 1, 2, 2, 1},
		{"single digit hour", "9:00:00 a\n10:30:15 b\n", "09:00:00", "10:30:15", "01:30:15", 1, 2, 2, 0},
		{"first time per line", "00:00:10 to 00:05:00\n00:01:00\n", "00:00:10", "00:01:00", "00:00:50", 1, 2, 2, 0},
		{"ignore date and long numbers", "2026-10-31 123:45:67\n00:00:05\n", "00:00:05", "00:00:05", "00:00:00", 2, 2, 1, 0},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			r, err := scan(strings.NewReader(c.in))
			if err != nil || r == nil {
				t.Fatalf("scan = %v, %v", r, err)
			}
			got := []any{fmtSec(r.first % 86400), fmtSec(r.last % 86400), fmtSec(r.last - r.first), r.firstNo, r.lastNo, r.count, r.wraps}
			want := []any{c.first, c.last, c.total, c.firstNo, c.lastNo, c.ct, c.wraps}
			for i := range got {
				if got[i] != want[i] {
					t.Errorf("got %v, want %v", got, want)
					break
				}
			}
		})
	}
}

func TestScanNoTime(t *testing.T) {
	if r, _ := scan(strings.NewReader("hello\nworld\n")); r != nil {
		t.Errorf("want nil, got %+v", r)
	}
}
