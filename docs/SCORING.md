# Freshness scoring (heuristic)

Current: round(60 + 40 × c × a). Changed: round(20 × (1 − c × a)). Unconfirmed: null (—).

c is mean verifier confidence, multiplied by 0.9 for single-model mode. A conclusive verdict requires every cited quote to exist verbatim (at most 25 words) in its own cited Tier-1 evidence. Thus the implemented authority factor a is 1.0: Tier-2-only corroboration never produces a verdict. The specification's optional 0.8 context-only factor is not applied, since the supporting citation must be official.

Cross-model agreement requires the same relation AND current_value, deliberately conservative. Single mode requires confidence ≥ 0.8. Any absent official source, failed quote check, disagreement or insufficiency yields no score.

Summary weights are high=3, medium=2, low=1; average only CURRENT and CHANGED scores. No verified claims means null, never zero. Headline denominator is verified claims, not all extracted claims. Scores are not calibrated probabilities; they do not measure legal or financial safety.
