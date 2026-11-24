"""Track AI chatbot response times per tool and endpoint.

Usage: python3 main.py responses.json [--slow-ms 2000]
The JSON file is a list of samples: {"tool", "endpoint",
"response_ms"}. Per tool this reports the sample count, the
average and the p95 response time, plus the slowest endpoint.
Verdict: SLOW when the p95 is over --slow-ms (default 2000),
otherwise OK. Slowest p95 first. Samples with a missing key
or a non-numeric response_ms are reported as skipped, not
silently dropped.
"""
import argparse, json, math, sys

def _p95(values):
    ordered = sorted(values)
    index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return ordered[index]

def track(samples, slow_ms=2000):
    tools = {}
    skipped = 0
    for sample in samples:
        try:
            tool = str(sample["tool"]).strip()
            endpoint = str(sample["endpoint"]).strip()
            response_ms = int(sample["response_ms"])
            if not tool or not endpoint:
                raise ValueError("missing value")
        except (KeyError, AttributeError, ValueError, TypeError):
            skipped += 1
            continue
        entry = tools.setdefault(tool, {"times": [], "slowest": (None, -1)})
        entry["times"].append(response_ms)
        if response_ms > entry["slowest"][1]:
            entry["slowest"] = (endpoint, response_ms)
    out = []
    for tool, data in tools.items():
        times = data["times"]
        average = sum(times) / len(times)
        p95 = _p95(times)
        verdict = "SLOW" if p95 > slow_ms else "OK"
        out.append((tool, len(times), average, p95, data["slowest"], verdict))
    out.sort(key=lambda r: (-r[3], r[0]))
    return out, skipped

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    parser.add_argument("--slow-ms", type=int, default=2000)
    args = parser.parse_args(argv)
    with open(args.path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print("Input must be a JSON list of samples.")
        return 1
    results, skipped = track(data, args.slow_ms)
    for tool, count, average, p95, (endpoint, slowest), verdict in results:
        print(f"{tool}: {verdict} - {count} sample(s), average {average:.0f} ms, "
              f"p95 {p95} ms, slowest endpoint {endpoint} ({slowest} ms)")
    slow = sum(1 for *_, verdict in results if verdict == "SLOW")
    print(f"{slow} slow tool(s), {len(results) - slow} ok out of "
          f"{len(results)} tool(s).")
    if skipped:
        print(f"Skipped {skipped} invalid sample(s).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
