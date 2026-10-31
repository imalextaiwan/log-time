import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from log_time import decode, fmt, parse_paths, scan  # noqa: E402


def summary(text):
    r = scan(text.splitlines())
    return (fmt(r['first'] % 86400), fmt(r['last'] % 86400), fmt(r['last'] - r['first']),
            r['first_no'], r['last_no'], r['count'], r['wraps'])


class ScanTest(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(summary('x\n[00:01:44] a\nno time\n[00:09:03] b\n'),
                         ('00:01:44', '00:09:03', '00:07:19', 2, 4, 2, 0))

    def test_midnight(self):
        self.assertEqual(summary('23:58:02 a\n00:03:09 b\n'),
                         ('23:58:02', '00:03:09', '00:05:07', 1, 2, 2, 1))

    def test_single_digit_hour(self):
        self.assertEqual(summary('9:00:00 a\n10:30:15 b\n'),
                         ('09:00:00', '10:30:15', '01:30:15', 1, 2, 2, 0))

    def test_first_time_per_line(self):
        self.assertEqual(summary('00:00:10 to 00:05:00\n00:01:00\n'),
                         ('00:00:10', '00:01:00', '00:00:50', 1, 2, 2, 0))

    def test_milliseconds_and_dates(self):
        self.assertEqual(summary('2026-10-31 123:45:67\n2026/10/31 00:00:05.123\n00:00:09,9\n'),
                         ('00:00:05', '00:00:09', '00:00:04', 2, 3, 2, 0))

    def test_no_time(self):
        self.assertIsNone(scan(['hello', 'world']))


class DecodeTest(unittest.TestCase):
    TEXT = '[00:01:44] 開始\r\n[00:09:03] 結束\r\n'

    def test_encodings(self):
        for data in (self.TEXT.encode('utf-8'),
                     b'\xef\xbb\xbf' + self.TEXT.encode('utf-8'),
                     self.TEXT.encode('utf-16'),
                     self.TEXT.encode('utf-16-le'),
                     self.TEXT.encode('utf-16-be'),
                     self.TEXT.encode('cp950')):
            with self.subTest(data=data[:6]):
                self.assertEqual(decode(data), self.TEXT)


class ParsePathsTest(unittest.TestCase):
    def test_paths(self):
        with tempfile.TemporaryDirectory() as d:
            spaced = os.path.join(d, 'OneDrive - Gigabyte 桌面.log')
            open(spaced, 'w').close()
            self.assertEqual(parse_paths(f'  {spaced} '), [spaced])
            self.assertEqual(parse_paths(f'"{spaced}"'), [spaced])
        self.assertEqual(parse_paths('"C:\\a b\\x.log" "C:\\y.log"'), ['C:\\a b\\x.log', 'C:\\y.log'])
        self.assertEqual(parse_paths('"C:\\a b\\x.log" C:\\y.log'), ['C:\\a b\\x.log', 'C:\\y.log'])
        self.assertEqual(parse_paths('   '), [])


if __name__ == '__main__':
    unittest.main()
