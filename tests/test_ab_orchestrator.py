#!/usr/bin/env python3
"""
A/B Test using the orchestrator
"""
import subprocess
import time
import json

# Test questions that need current info
TEST_QUESTIONS = [
    "¿Qué arancel tiene la importación de notebooks?",
    "¿Cuál es el límite actual para pagos de Netflix?",
    "¿Qué requisitos hay hoy para exportar limones a Europa?"
]

def toggle_search(enable):
    """Toggle search in .env"""
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    with open('.env', 'w') as f:
        for line in lines:
            if line.startswith("ENABLE_SEARCH="):
                f.write(f"ENABLE_SEARCH={'true' if enable else 'false'}\n")
            else:
                f.write(line)
    
    # Restart services
    subprocess.run(["docker-compose", "restart"], capture_output=True)
    time.sleep(5)

def test_question(question):
    """Test a question using orchestrator"""
    start = time.time()
    result = subprocess.run(
        ["python3", "orchestrator_multiagent.py", question],
        capture_output=True,
        text=True
    )
    duration = time.time() - start
    
    return {
        "output": result.stdout,
        "error": result.stderr,
        "duration": duration
    }

def main():
    print("🔬 A/B Test: Search Integration\n")
    
    results = {"with_search": [], "without_search": []}
    
    # Test WITHOUT search
    print("1️⃣  Testing WITHOUT search...")
    toggle_search(False)
    
    for q in TEST_QUESTIONS:
        print(f"\n   Testing: {q[:50]}...")
        result = test_question(q)
        results["without_search"].append({
            "question": q,
            "duration": result["duration"],
            "has_error": bool(result["error"])
        })
        print(f"   ⏱️  {result['duration']:.1f}s")
    
    # Test WITH search  
    print("\n\n2️⃣  Testing WITH search...")
    toggle_search(True)
    
    for q in TEST_QUESTIONS:
        print(f"\n   Testing: {q[:50]}...")
        result = test_question(q)
        results["with_search"].append({
            "question": q,
            "duration": result["duration"],
            "has_error": bool(result["error"])
        })
        print(f"   ⏱️  {result['duration']:.1f}s")
    
    # Compare
    print("\n\n📊 RESULTS:")
    print("-" * 50)
    
    total_without = sum(r["duration"] for r in results["without_search"])
    total_with = sum(r["duration"] for r in results["with_search"])
    
    print(f"Average time WITHOUT search: {total_without/len(TEST_QUESTIONS):.1f}s")
    print(f"Average time WITH search: {total_with/len(TEST_QUESTIONS):.1f}s")
    print(f"Search overhead: +{(total_with - total_without)/len(TEST_QUESTIONS):.1f}s per query")
    
    # Reset to original
    toggle_search(False)

if __name__ == "__main__":
    main()