# Missing real assets — every placeholder is listed

Do not replace these frames with invented evidence. Dates must come from actual captures. PNG/JPG assets should be readable at the stated size.

| Slide | Asset / filename | Needed information / minimum size |
|---|---|---|
| S1 | team.txt | Actual registered team name and presenter names; no team name assumed |
| S4 | assets/official-schedule-al.png | Real official page screenshot, URL, capture date; 1400×900 or larger |
| S4 | assets/secondary-tax-guide.png | Real secondary page screenshot, URL, capture date; 1400×900 or larger; do not infer assessment year |
| S4 | capture-dates.txt | Date of each screenshot above, recorded by the capturer |
| S5 | assets/verified-result.json | Values, quote, source URL and checked_at copied from a genuine non-mock run |
| S6 | assets/captured-answer.json | Raw answer, model, date and question produced by capture script, not illustrative text |
| S6 | assets/recorded-run.mp4 OR live-url.txt | Real run recording or verified reachable deployment URL; record date and models; 1920×1080 recommended |
| S6 | assets/recording-metadata.json | Recorded-run date and model IDs, no invented timestamps |
| S7 | ../benchmark/results/*.json | Actual benchmark runner output with models/date/commit, n, accuracy, false-current rate, baseline and p50/p95 |

Author status in author_status.yaml starts planned. Mark verified only after testing the feature with real configuration. The builder keeps unsupported features planned. No live recording or current benchmark was created during this build.
