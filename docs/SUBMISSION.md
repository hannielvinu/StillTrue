# Submission copy kit

Theme: **Build a Stale-Answer Detector for AI Applications** (uses both Tavily and Bifrost).

## One-line pitch
Paste any AI answer: StillTrue checks every price, version and deadline against the organisation that publishes it, live, with a word-for-word official quote.

## Problem
AI answers go out of date silently, and people act on them. In our test a strong model called all 7 recent software releases "outdated" because they came after its training.

## Solution
StillTrue extracts actionable claims, searches each fact's official publisher with Tavily, has two independent models (via Bifrost) judge the evidence, and only issues a verdict when a quote is found word for word on an official page.

## Measured result (21 Nov 2026, 28 labelled claims)
22/28 correct vs 17/28 for the same model alone; 6/7 vs 0/7 on facts newer than the model's training; right 22 of 23 times when it commits to a verdict.

## AI usage
LLMs (Groq gpt-oss-20b, gpt-oss-120b; NVIDIA Nemotron 3.5 Lightning) through Bifrost extract claims, verify evidence and rewrite the answer. An AI coding assistant helped build and test the code.

## Technologies
Bifrost, Tavily, Groq, NVIDIA API catalog, Python, FastAPI, Pydantic, httpx, SQLite, React, TypeScript, Vite, Tailwind CSS, Docker, GitHub Actions.
