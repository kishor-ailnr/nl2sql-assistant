"""Phase 3 Test Script: Crash-proofing and Validation Pipeline.

Tests:
  Case A: Regression check ("List all patients older than 40")
  Case B: Write query blocked ("Delete all patients older than 90") with DB row count check
  Case C: Bad SQL handled cleanly by execution_engine.run_select("SELEC * FROM patients")
"""

import sys
import json
import sqlite3
from pathlib import Path
import requests

# Add backend root to sys.path so we can import execution_engine directly for Case C
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.services.execution_engine import run_select

BASE_URL = "http://127.0.0.1:8000"
HOSPITAL_DB_PATH = BACKEND_DIR / "data" / "demo_hospital.db"


def get_patients_count() -> int:
    """Read the exact row count of the patients table directly from the SQLite database."""
    conn = sqlite3.connect(str(HOSPITAL_DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def print_separator(title: str):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def main():
    print("=================================================================")
    print("  Starting Phase 3 Test Suite against running server at", BASE_URL)
    print("=================================================================")

    # Step 0: Connect to Hospital Demo Database
    print("\n[Step 0] Connecting to Hospital Demo Database...")
    resp = requests.post(
        f"{BASE_URL}/api/connect-db",
        json={"db_type": "demo", "demo_name": "hospital"}
    )
    if resp.status_code != 200:
        print(f"FAILED to connect: {resp.status_code} {resp.text}")
        sys.exit(1)

    connect_data = resp.json()
    session_id = connect_data["session_id"]
    print(f"Connected successfully! Session ID: {session_id}")
    print(f"Discovered Tables: {connect_data.get('tables')}")

    # =========================================================================
    # Case A (Regression Check): "List all patients older than 40"
    # =========================================================================
    print_separator("CASE A (Regression Check): 'List all patients older than 40'")
    payload_a = {
        "session_id": session_id,
        "text": "List all patients older than 40",
        "language": "en"
    }
    resp_a = requests.post(f"{BASE_URL}/api/query", json=payload_a)
    print(f"HTTP Status Code: {resp_a.status_code}")
    assert resp_a.status_code == 200, f"Expected 200 OK, got {resp_a.status_code}"
    
    data_a = resp_a.json()
    print("\nResponse Details:")
    print(f"  Query ID:     {data_a.get('query_id')}")
    print(f"  SQL:          {data_a.get('sql')}")
    print(f"  Explanation:  {data_a.get('explanation')}")
    print(f"  Confidence:   {data_a.get('confidence')}")
    print(f"  Query Type:   {data_a.get('query_type')}")
    print(f"  Chart Type:   {data_a.get('chart_type')}")
    print(f"  Row Count:    {len(data_a.get('result', []))}")
    print("\nResult Rows:")
    print(json.dumps(data_a.get("result", []), indent=2))

    # Assertions for Case A
    assert len(data_a.get("result", [])) > 0, "Case A should return rows"
    assert data_a.get("confidence") > 0, "Case A confidence should be positive"
    print("\n>>> Case A PASSED: Valid SELECT query succeeded and returned data as expected.")

    # =========================================================================
    # Case B (Write Blocked): "Delete all patients older than 90"
    # =========================================================================
    print_separator("CASE B (Write Blocked): 'Delete all patients older than 90'")
    
    count_before = get_patients_count()
    print(f"Patients row count BEFORE query: {count_before}")

    payload_b = {
        "session_id": session_id,
        "text": "Delete all patients older than 90",
        "language": "en"
    }
    resp_b = requests.post(f"{BASE_URL}/api/query", json=payload_b)
    print(f"HTTP Status Code: {resp_b.status_code}")
    assert resp_b.status_code == 200, f"Expected 200 OK without server crash, got {resp_b.status_code}"

    data_b = resp_b.json()
    print("\nResponse Details:")
    print(f"  Query ID:     {data_b.get('query_id')}")
    print(f"  Attempted SQL:{data_b.get('sql')}")
    print(f"  Explanation:  {data_b.get('explanation')}")
    print(f"  Confidence:   {data_b.get('confidence')}")
    print(f"  Query Type:   {data_b.get('query_type')}")
    print(f"  Chart Type:   {data_b.get('chart_type')}")
    print(f"  Row Count:    {len(data_b.get('result', []))}")
    print(f"  Result:       {data_b.get('result')}")

    count_after = get_patients_count()
    print(f"\nPatients row count AFTER query:  {count_after}")
    print(f"Row count difference:           {count_after - count_before}")

    # Assertions for Case B
    assert count_before == count_after, "Database row count changed! Deletion was NOT blocked!"
    assert data_b.get("confidence") == 0, "Confidence should be 0 for blocked query"
    assert data_b.get("result") == [], "Result should be empty list [] for blocked query"
    assert "only supports read" in data_b.get("explanation", "").lower() or "syntax" in data_b.get("explanation", "").lower(), \
        f"Unexpected explanation message: {data_b.get('explanation')}"
    print("\n>>> Case B PASSED: Non-read query safely blocked! Zero rows modified in database.")

    # =========================================================================
    # Case C (Bad SQL Handled): Direct execution_engine.run_select call
    # =========================================================================
    print_separator("CASE C (Bad SQL Handled): execution_engine.run_select('SELEC * FROM patients')")
    from app.services.session_store import set_session
    set_session(session_id, {"db_path": str(HOSPITAL_DB_PATH)})

    broken_sql = "SELEC * FROM patients"
    print(f"Calling run_select(session_id='{session_id}', sql='{broken_sql}')...")

    try:
        result_c = run_select(session_id, broken_sql)
        print("\nDirect run_select return value:")
        print(json.dumps(result_c, indent=2))
        
        assert isinstance(result_c, dict), f"Expected dict return on error, got {type(result_c)}"
        assert "error" in result_c, f"Expected 'error' key in dict, got: {result_c}"
        print(f"\nError captured cleanly: {result_c['error']}")
        print("No exception crashed or halted the script!")
        print("\n>>> Case C PASSED: Bad SQL handled cleanly by execution_engine without crashing.")
    except Exception as exc:
        print(f"\nFAILED: Exception was raised instead of caught: {exc}")
        sys.exit(1)

    print("\n" + "=" * 65)
    print("  ALL PHASE 3 TESTS PASSED SUCCESSFULLY (Case A, Case B, Case C)!")
    print("=" * 65)


if __name__ == "__main__":
    main()
