import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unittest
from main import track

def sample(tool, endpoint, ms):
    return {"tool": tool, "endpoint": endpoint, "response_ms": ms}

class TestResponseTimeTracker(unittest.TestCase):
    def test_average_and_p95(self):
        r, _ = track([sample("ChatGPT", "/chat", 800),
                      sample("ChatGPT", "/chat", 1200),
                      sample("ChatGPT", "/chat", 900)])
        self.assertEqual(r[0][1], 3)
        self.assertAlmostEqual(r[0][2], 966.67, places=2)
        self.assertEqual(r[0][3], 1200)

    def test_slow_verdict(self):
        r, _ = track([sample("Copilot", "/complete", 2600),
                      sample("Copilot", "/complete", 2400)])
        self.assertEqual(r[0][5], "SLOW")

    def test_exactly_slow_threshold_is_ok(self):
        r, _ = track([sample("ChatGPT", "/chat", 2000)])
        self.assertEqual(r[0][5], "OK")

    def test_slowest_endpoint_reported(self):
        r, _ = track([sample("ChatGPT", "/chat", 800),
                      sample("ChatGPT", "/summarise", 1500)])
        self.assertEqual(r[0][4], ("/summarise", 1500))

    def test_slowest_p95_first(self):
        r, _ = track([sample("ChatGPT", "/chat", 800),
                      sample("Copilot", "/complete", 2600)])
        self.assertEqual(r[0][0], "Copilot")

    def test_invalid_sample_is_skipped(self):
        r, skipped = track([{"tool": "ChatGPT", "endpoint": "/chat"},
                            sample("ChatGPT", "/chat", 800)])
        self.assertEqual((len(r), skipped), (1, 1))

    def test_non_numeric_ms_is_skipped(self):
        r, skipped = track([sample("ChatGPT", "/chat", "fast")])
        self.assertEqual((r, skipped), ([], 1))

    def test_empty_input(self):
        self.assertEqual(track([]), ([], 0))
