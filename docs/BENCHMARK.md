# Honest benchmark procedure

The seed is explicitly authorized by the user; no other row is human-labelled by the builder. Add candidate JSONL rows only after opening the official URL. Fields: id, pack, claim_text, claim_source_note, expected (CURRENT/CHANGED/UNCONFIRMED_EXPECTED), ground_truth_value, ground_truth_source_url, checked_on, label_status.

A human must independently verify the rule, jurisdiction, applicable year and source date before changing proposed_needs_human to human_verified. Aim for at least 40 balanced candidate claims and 20 verified labels; include unconfirmable examples. Recheck labels before measuring.

Run `make bench` with MOCK_MODE=false and actual provider/Tavily credentials after activating domains. The runner refuses mock mode and aborts on provider errors. Only human_verified labels are scored. Fewer than 20 yields SMALL SAMPLE. False-CURRENT denominator is stale (expected CHANGED) rows. Missed-change is any non-CHANGED result on those rows. Accuracy includes Unconfirmed as a distinct outcome. Credit counts are estimated. Cache hits can reduce measured cost; record cache state when comparing runs.

The no-retrieval baseline uses Bifrost and the extractor model. Baseline and pipeline latency are measured separately. Results include commit, model IDs and UTC timestamp. Do not extrapolate the one-row seed.

Reports are generated only by actual API runs, saved under results, and copied to the frontend public benchmark path. Run scripts/update_readme_results.py and rebuild to publish measured results. No results currently exist.
