"""Manual test script for Phase 2 NL-to-SQL pipeline.
Tests /api/connect-db and /api/query end-to-end with multiple sample queries.
"""

import json
import requests

BASE_URL = "http://127.0.0.1:8000"


def test_query(session_id: str, question: str):
    print(f"\n==================================================")
    print(f"Querying: \"{question}\"")
    print(f"Session ID: {session_id}")
    print(f"==================================================")

    payload = {
        "session_id": session_id,
        "text": question,
        "language": "en"
    }

    resp = requests.post(f"{BASE_URL}/api/query", json=payload)
    if resp.status_code != 200:
        print(f"ERROR ({resp.status_code}): {resp.text}")
        return None

    data = resp.json()
    print("\n--- Response Details ---")
    print(f"Query ID:     {data.get('query_id')}")
    print(f"SQL:          {data.get('sql')}")
    print(f"Explanation:  {data.get('explanation')}")
    print(f"Confidence:   {data.get('confidence')}")
    print(f"Query Type:   {data.get('query_type')}")
    print(f"Chart Type:   {data.get('chart_type')}")
    print(f"Results Count: {len(data.get('result', []))} rows")
    print("\nResult Rows:")
    print(json.dumps(data.get("result", []), indent=2))
    return data


def main():
    print("Testing Phase 2 NL-to-SQL Flow against running server at", BASE_URL)

    # 1. Connect to Hospital Demo Database
    print("\n[Step 1] Connecting to 'hospital' demo database...")
    resp = requests.post(
        f"{BASE_URL}/api/connect-db",
        json={"db_type": "demo", "demo_name": "hospital"}
    )
    if resp.status_code != 200:
        print(f"Failed to connect to hospital DB: {resp.status_code} {resp.text}")
        return

    hospital_data = resp.json()
    hospital_session_id = hospital_data["session_id"]
    print(f"Connected! Session ID: {hospital_session_id}")
    print(f"Discovered Tables: {hospital_data.get('tables')}")

    # Primary Required Test: "List all patients older than 40"
    test_query(hospital_session_id, "List all patients older than 40")

    # Additional Test 1: "How many doctors are there in Cardiology"
    test_query(hospital_session_id, "How many doctors are there in Cardiology")

    # 2. Connect to Ecommerce Demo Database
    print("\n\n[Step 2] Connecting to 'ecommerce' demo database...")
    resp_ecom = requests.post(
        f"{BASE_URL}/api/connect-db",
        json={"db_type": "demo", "demo_name": "ecommerce"}
    )
    if resp_ecom.status_code != 200:
        print(f"Failed to connect to ecommerce DB: {resp_ecom.status_code} {resp_ecom.text}")
        return

    ecom_data = resp_ecom.json()
    ecom_session_id = ecom_data["session_id"]
    print(f"Connected! Session ID: {ecom_session_id}")
    print(f"Discovered Tables: {ecom_data.get('tables')}")

    # Additional Test 2: "Show me all orders over 5000 rupees"
    test_query(ecom_session_id, "Show me all orders over 5000 rupees")


if __name__ == "__main__":
    main()
