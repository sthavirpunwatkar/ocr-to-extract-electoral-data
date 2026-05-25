# Benchmarking Framework for Electoral Roll OCR

This directory contains the tools and data for measuring the accuracy of the OCR pipeline.

## Directory Structure
- `data/raw/`: Store original PDF or image files of electoral rolls here.
- `data/ground_truth/`: Store manually verified JSON files matching the structure of expected OCR output.
- `data/extracted/`: Store the output of the OCR pipeline here for comparison.
- `scripts/evaluator.py`: Python script to compare extraction results with ground truth.

## Metrics
- **Character Error Rate (CER)**: Measures the edit distance between expected and actual text strings.
- **Field Accuracy**: Exact match percentage for specific fields like Name, EPIC, Age, etc.
- **Booth Accuracy**: Accuracy of header information (Assembly Constituency, Booth No).

## How to Run Evaluation
1. Place your ground truth JSON files in `data/ground_truth/`.
2. Place your OCR output JSON files in `data/extracted/` with the same filenames as the ground truth.
3. Run the evaluator:
   ```bash
   python scripts/evaluator.py data/ground_truth/ data/extracted/
   ```
4. Check `evaluation_report.json` for detailed results.

## Data Sources
Publicly available electoral rolls can be found at:
- [Voters' Service Portal (ECI)](https://voters.eci.gov.in/download-eroll)
- [CEO Uttar Pradesh](http://ceouttarpradesh.nic.in/)
- [CEO Delhi](https://ceodelhi.gov.in/)
- [CEO Maharashtra](https://ceo.maharashtra.gov.in/)

*Note: Automated downloading is often restricted by CAPTCHAs. For development, 2-3 samples have been mocked in the `ground_truth` and `extracted` folders.*

## Extensibility
The `evaluator.py` script is designed to handle multi-lingual data (UTF-8) and can be extended to include more fields by updating the `fields` list in the `evaluate_file` function.
