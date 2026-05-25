---
name: bench-ocr
argument-hint: [dataset-path]
---

Run OCR benchmarks to verify accuracy and performance.
1. Identify the dataset in [dataset-path] or use default benchmarks/data/raw/.
2. Run `python benchmarks/scripts/evaluator.py`.
3. Compare results with `evaluation_report.json`.
4. Summarize performance (time per page) and accuracy (field-level).
