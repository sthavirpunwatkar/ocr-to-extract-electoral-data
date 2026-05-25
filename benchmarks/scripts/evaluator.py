import json
import os
import difflib
from typing import List, Dict, Any

def calculate_cer(reference: str, hypothesis: str) -> float:
    """
    Calculate Character Error Rate (CER).
    """
    if not reference:
        return 1.0 if hypothesis else 0.0
    
    s = difflib.SequenceMatcher(None, reference, hypothesis)
    # distance = sum of changes (substitutions, deletions, insertions)
    # SequenceMatcher doesn't give Levenshtein distance directly but we can estimate
    # or use a simple Levenshtein implementation.
    
    # Simple Levenshtein for CER
    n, m = len(reference), len(hypothesis)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): dp[i][0] = i
    for j in range(m + 1): dp[0][j] = j
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if reference[i-1] == hypothesis[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
    
    return dp[n][m] / n

def evaluate_fields(expected: Dict[str, Any], actual: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """
    Evaluate specific fields for accuracy.
    """
    results = {}
    for field in fields:
        exp_val = str(expected.get(field, "")).strip()
        act_val = str(actual.get(field, "")).strip()
        
        is_match = exp_val == act_val
        cer = calculate_cer(exp_val, act_val)
        
        results[field] = {
            "match": is_match,
            "cer": cer,
            "expected": exp_val,
            "actual": act_val
        }
    return results

def evaluate_file(ground_truth_path: str, extracted_path: str) -> Dict[str, Any]:
    with open(ground_truth_path, 'r', encoding='utf-8') as f:
        gt_data = json.load(f)
    
    if not os.path.exists(extracted_path):
        return {"error": f"Extracted file not found: {extracted_path}"}
        
    with open(extracted_path, 'r', encoding='utf-8') as f:
        ex_data = json.load(f)
        
    # Assume data is a list of voter records
    gt_records = gt_data.get("records", [])
    ex_records = ex_data.get("records", [])
    
    booth_info_gt = gt_data.get("booth_info", {})
    booth_info_ex = ex_data.get("booth_info", {})
    
    booth_eval = evaluate_fields(booth_info_gt, booth_info_ex, ["booth_name", "booth_no", "ac_name", "ac_no"])
    
    record_results = []
    # Match records by EPIC if possible
    gt_by_epic = {r.get("epic"): r for r in gt_records if r.get("epic")}
    ex_by_epic = {r.get("epic"): r for r in ex_records if r.get("epic")}
    
    all_epics = set(gt_by_epic.keys()) | set(ex_by_epic.keys())
    
    for epic in all_epics:
        gt_rec = gt_by_epic.get(epic, {})
        ex_rec = ex_by_epic.get(epic, {})
        
        field_eval = evaluate_fields(gt_rec, ex_rec, ["name", "relation_name", "house_no", "age", "gender"])
        record_results.append({
            "epic": epic,
            "fields": field_eval
        })
        
    # Aggregate Metrics
    total_records = len(gt_records)
    matched_records = sum(1 for r in record_results if all(f["match"] for f in r["fields"].values()))
    
    avg_cer = 0.0
    count = 0
    for r in record_results:
        for f in r["fields"].values():
            avg_cer += f["cer"]
            count += 1
    if count > 0:
        avg_cer /= count
        
    return {
        "booth_accuracy": booth_eval,
        "record_accuracy": {
            "total_expected": total_records,
            "total_extracted": len(ex_records),
            "fully_correct": matched_records,
            "accuracy_rate": matched_records / total_records if total_records > 0 else 0
        },
        "overall_avg_cer": avg_cer,
        "details": record_results
    }

def main():
    # Example usage: python evaluator.py <gt_dir> <ex_dir>
    import sys
    if len(sys.argv) < 3:
        print("Usage: python evaluator.py <ground_truth_dir> <extracted_dir>")
        return

    gt_dir = sys.argv[1]
    ex_dir = sys.argv[2]
    
    overall_results = {}
    
    for filename in os.listdir(gt_dir):
        if filename.endswith(".json"):
            gt_path = os.path.join(gt_dir, filename)
            ex_path = os.path.join(ex_dir, filename)
            
            print(f"Evaluating {filename}...")
            result = evaluate_file(gt_path, ex_path)
            overall_results[filename] = result
            
    with open("evaluation_report.json", "w", encoding='utf-8') as f:
        json.dump(overall_results, f, indent=4)
    
    print("Evaluation complete. Report saved to evaluation_report.json")

if __name__ == "__main__":
    main()
