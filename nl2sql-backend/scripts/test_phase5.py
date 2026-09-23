"""Phase 5 Test Suite: NL-to-SQL Benchmark across 18 English Questions.

Tests 18 questions spanning varying SQL complexity (aggregations, GROUP BY,
multi-table JOINs, sorting, and date filters) across both Hospital and Ecommerce
demo databases against the live running server.
"""

import sys
import json
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

HOSPITAL_QUESTIONS = [
    (1, "How many patients are there in total", {"expect_non_empty": True}),
    (2, "List all doctors in the Cardiology department", {"expect_non_empty": True}),
    (3, "Show me patients admitted after March 1st 2024", {"expect_non_empty": True}),
    (4, "What is the average age of all patients", {"expect_non_empty": True}),
    (5, "How many appointments does each doctor have", {"expect_group_by": True, "expect_non_empty": True}),
    (6, "List patients along with their doctor's name for each appointment", {"expect_join": True, "expect_non_empty": True}),
    (7, "Show me the youngest patient", {"expect_non_empty": True}),
    (8, "How many patients have a diagnosis of Pneumonia", {"expect_non_empty": True}),
    (9, "List all doctors sorted by name alphabetically", {"expect_order_by": True, "expect_non_empty": True}),
]

ECOMMERCE_QUESTIONS = [
    (10, "How many customers signed up in total", {"expect_non_empty": True}),
    (11, "What is the total revenue from all orders", {"expect_non_empty": True}),
    (12, "List the top 3 most expensive products", {"expect_order_by": True, "expect_limit": True, "expect_non_empty": True}),
    (13, "How many orders did each customer place", {"expect_group_by": True, "expect_non_empty": True}),
    (14, "Show me all orders with the customer name and product name", {"expect_join": True, "expect_non_empty": True}),
    (15, "Which product category has the most products", {"expect_group_by": True, "expect_non_empty": True}),
    # Note: Question 16 uses 'Chicago' as verified from seeded customers table in demo_ecommerce.db
    (16, "List customers who signed up from Chicago", {"expect_non_empty": True}),
    (17, "What is the average order amount", {"expect_non_empty": True}),
    (18, "Show me orders placed in February 2024", {"expect_non_empty": True}),
]


def evaluate_response(q_num: int, q_text: str, resp_data: dict, expectations: dict):
    """Determine PASS vs REVIEW based on confidence, row count, and SQL logic."""
    reasons = []

    sql = resp_data.get("sql", "").strip()
    confidence = float(resp_data.get("confidence", 0.0))
    result = resp_data.get("result", [])
    explanation = resp_data.get("explanation", "")
    row_count = len(result)

    # Check 1: Empty or missing SQL
    if not sql:
        reasons.append("Generated SQL is empty.")

    # Check 2: Confidence score threshold
    if confidence < 0.7:
        reasons.append(f"Confidence score ({confidence}) is below threshold 0.7.")

    # Check 3: Unexpected empty results
    if expectations.get("expect_non_empty") and row_count == 0:
        reasons.append("Result set is empty when seeded data has matching rows.")

    # Check 4: Expected GROUP BY clause
    if expectations.get("expect_group_by") and "group by" not in sql.lower():
        reasons.append("Expected GROUP BY clause in SQL for aggregation breakdown.")

    # Check 5: Expected JOIN clause
    if expectations.get("expect_join") and "join" not in sql.lower():
        reasons.append("Expected JOIN across multiple tables in SQL.")

    # Check 6: Expected ORDER BY clause
    if expectations.get("expect_order_by") and "order by" not in sql.lower():
        reasons.append("Expected ORDER BY clause for ranking/sorting.")

    # Check 7: Blocked or execution error
    if "only supports read" in explanation.lower() or "syntax" in explanation.lower() or "failed" in explanation.lower():
        reasons.append(f"Query returned error/validation message: {explanation}")

    status = "REVIEW" if len(reasons) > 0 else "PASS"
    return status, reasons


def run_benchmark():
    print("=" * 75)
    print("  PHASE 5 TEST SUITE: 18-QUESTION NL-TO-SQL BENCHMARK")
    print(f"  Target Server: {BASE_URL}")
    print("=" * 75)

    results_summary = []

    # -------------------------------------------------------------------------
    # PART 1: Hospital Demo Database (Questions 1 - 9)
    # -------------------------------------------------------------------------
    print("\n" + "#" * 75)
    print("  PART 1: HOSPITAL DEMO DATABASE (Questions 1 - 9)")
    print("#" * 75)

    print("\nConnecting to 'hospital' database...")
    connect_resp = requests.post(f"{BASE_URL}/api/connect-db", json={"db_type": "demo", "demo_name": "hospital"})
    if connect_resp.status_code != 200:
        print(f"FAILED to connect to hospital DB: {connect_resp.status_code} {connect_resp.text}")
        sys.exit(1)

    hospital_session_id = connect_resp.json()["session_id"]
    print(f"Connected! Session ID: {hospital_session_id}\n")

    for q_num, q_text, exp in HOSPITAL_QUESTIONS:
        time.sleep(1.0)  # Gentle spacing for Gemini API rate limits
        print("-" * 75)
        print(f"Question {q_num}: \"{q_text}\"")

        payload = {"session_id": hospital_session_id, "text": q_text, "language": "en"}
        resp = requests.post(f"{BASE_URL}/api/query", json=payload)

        if resp.status_code != 200:
            print(f"  [ERROR] HTTP {resp.status_code}: {resp.text}")
            results_summary.append({
                "q_num": q_num,
                "q_text": q_text,
                "status": "REVIEW",
                "sql": "N/A",
                "confidence": 0.0,
                "row_count": 0,
                "reasons": [f"HTTP {resp.status_code} error from server"]
            })
            continue

        data = resp.json()
        status, reasons = evaluate_response(q_num, q_text, data, exp)

        print(f"  Generated SQL: {data.get('sql')}")
        print(f"  Confidence:    {data.get('confidence')}")
        print(f"  Result Rows:   {len(data.get('result', []))}")
        print(f"  Status:        [{status}]")
        if reasons:
            print(f"  Review Notes:  {'; '.join(reasons)}")
        if data.get("result"):
            sample = data["result"][:2]
            print(f"  Sample Output: {json.dumps(sample)}")

        results_summary.append({
            "q_num": q_num,
            "q_text": q_text,
            "status": status,
            "sql": data.get("sql", ""),
            "confidence": data.get("confidence", 0.0),
            "row_count": len(data.get("result", [])),
            "reasons": reasons,
            "data": data
        })

    # -------------------------------------------------------------------------
    # PART 2: Ecommerce Demo Database (Questions 10 - 18)
    # -------------------------------------------------------------------------
    print("\n\n" + "#" * 75)
    print("  PART 2: ECOMMERCE DEMO DATABASE (Questions 10 - 18)")
    print("#" * 75)

    print("\nConnecting to 'ecommerce' database...")
    connect_resp_ecom = requests.post(f"{BASE_URL}/api/connect-db", json={"db_type": "demo", "demo_name": "ecommerce"})
    if connect_resp_ecom.status_code != 200:
        print(f"FAILED to connect to ecommerce DB: {connect_resp_ecom.status_code} {connect_resp_ecom.text}")
        sys.exit(1)

    ecom_session_id = connect_resp_ecom.json()["session_id"]
    print(f"Connected! Session ID: {ecom_session_id}\n")

    for q_num, q_text, exp in ECOMMERCE_QUESTIONS:
        time.sleep(1.0)  # Gentle spacing for Gemini API rate limits
        print("-" * 75)
        print(f"Question {q_num}: \"{q_text}\"")

        payload = {"session_id": ecom_session_id, "text": q_text, "language": "en"}
        resp = requests.post(f"{BASE_URL}/api/query", json=payload)

        if resp.status_code != 200:
            print(f"  [ERROR] HTTP {resp.status_code}: {resp.text}")
            results_summary.append({
                "q_num": q_num,
                "q_text": q_text,
                "status": "REVIEW",
                "sql": "N/A",
                "confidence": 0.0,
                "row_count": 0,
                "reasons": [f"HTTP {resp.status_code} error from server"]
            })
            continue

        data = resp.json()
        status, reasons = evaluate_response(q_num, q_text, data, exp)

        print(f"  Generated SQL: {data.get('sql')}")
        print(f"  Confidence:    {data.get('confidence')}")
        print(f"  Result Rows:   {len(data.get('result', []))}")
        print(f"  Status:        [{status}]")
        if reasons:
            print(f"  Review Notes:  {'; '.join(reasons)}")
        if data.get("result"):
            sample = data["result"][:2]
            print(f"  Sample Output: {json.dumps(sample)}")

        results_summary.append({
            "q_num": q_num,
            "q_text": q_text,
            "status": status,
            "sql": data.get("sql", ""),
            "confidence": data.get("confidence", 0.0),
            "row_count": len(data.get("result", [])),
            "reasons": reasons,
            "data": data
        })

    # -------------------------------------------------------------------------
    # SUMMARY REPORT
    # -------------------------------------------------------------------------
    print("\n\n" + "=" * 75)
    print("  PHASE 5 BENCHMARK FINAL SUMMARY")
    print("=" * 75)

    total_q = len(results_summary)
    pass_count = sum(1 for r in results_summary if r["status"] == "PASS")
    review_count = sum(1 for r in results_summary if r["status"] == "REVIEW")

    print(f"Total Questions Evaluated: {total_q}")
    print(f"  PASS:   {pass_count} / {total_q} ({pass_count/total_q*100:.1f}%)")
    print(f"  REVIEW: {review_count} / {total_q} ({review_count/total_q*100:.1f}%)")

    review_items = [r for r in results_summary if r["status"] == "REVIEW"]
    if review_items:
        print("\n" + "-" * 75)
        print("  ITEMS FLAGGED FOR REVIEW:")
        print("-" * 75)
        for item in review_items:
            print(f"\n[Question {item['q_num']}] \"{item['q_text']}\"")
            print(f"  SQL:        {item['sql']}")
            print(f"  Confidence: {item['confidence']}")
            print(f"  Rows:       {item['row_count']}")
            print(f"  Reasons:    {'; '.join(item['reasons'])}")
    else:
        print("\nAll 18 questions PASSED with flying colors!")

    print("\n" + "=" * 75)


if __name__ == "__main__":
    run_benchmark()
