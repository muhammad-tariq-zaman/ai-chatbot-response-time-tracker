# ai-chatbot-response-time-tracker

Track AI chatbot response times per tool and endpoint: the input JSON file is a list of samples — {"tool", "endpoint", "response_ms"} — and per tool this reports the sample count, the average and the p95 response time, plus the slowest endpoint. Verdict: SLOW when the p95 is over --slow-ms (default 2000), otherwise OK — slowest p95 first. Samples with a missing key or a non-numeric response_ms are reported as skipped, not silently dropped.

Sample input is included (sample.json with nine samples across three tools, one invalid sample).

## How to run

```sh
python3 main.py sample.json
```

## Example output

```
Copilot: SLOW - 3 sample(s), average 2633 ms, p95 2900 ms, slowest endpoint /explain (2900 ms)
ChatGPT: OK - 3 sample(s), average 1167 ms, p95 1500 ms, slowest endpoint /summarise (1500 ms)
Gemini: OK - 2 sample(s), average 1025 ms, p95 1100 ms, slowest endpoint /generate (1100 ms)
1 slow tool(s), 2 ok out of 3 tool(s).
Skipped 1 invalid sample(s).
```

Standard library only. Run the tests with `python3 -m unittest discover`.
