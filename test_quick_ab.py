#!/usr/bin/env python3
"""Quick A/B comparison"""
import subprocess
import time
import os

# Questions that need current info
questions = [
    "¿Qué arancel pagan los notebooks importados?",
    "¿Cuál es el límite para pagar Netflix?",
    "¿Cuál es la cotización del dólar MEP?"
]

def test_with_search(enable):
    # Update .env
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    with open('.env', 'w') as f:
        for line in lines:
            if line.startswith("ENABLE_SEARCH="):
                f.write(f"ENABLE_SEARCH={'true' if enable else 'false'}\n")
            else:
                f.write(line)
    
    # Restart comex
    subprocess.run(["docker-compose", "restart", "comex"], capture_output=True)
    time.sleep(3)
    
    results = []
    for q in questions:
        start = time.time()
        result = subprocess.run(
            ["python3", "orchestrator_multiagent.py", q],
            capture_output=True,
            text=True
        )
        duration = time.time() - start
        
        # Extract key info from output
        output = result.stdout
        has_2024 = "2024" in output
        has_percent = "%" in output
        
        results.append({
            "question": q,
            "duration": duration,
            "has_2024": has_2024,
            "has_percent": has_percent
        })
    
    return results

print("🔬 Quick A/B Test\n")

# Test without search
print("Testing WITHOUT search...")
without = test_with_search(False)

# Test with search
print("\nTesting WITH search...")
with_search = test_with_search(True)

# Compare
print("\n📊 RESULTS:")
print("-" * 60)
print(f"{'Question':<40} {'Without':<10} {'With':<10}")
print("-" * 60)

for i, q in enumerate(questions):
    w_time = without[i]['duration']
    s_time = with_search[i]['duration']
    diff = s_time - w_time
    
    print(f"{q[:38]:<40} {w_time:.1f}s      {s_time:.1f}s (+{diff:.1f}s)")
    
    if with_search[i]['has_2024'] and not without[i]['has_2024']:
        print(f"  → WITH search includes 2024 info!")

avg_without = sum(r['duration'] for r in without) / len(without)
avg_with = sum(r['duration'] for r in with_search) / len(with_search)

print(f"\nAverage time WITHOUT search: {avg_without:.1f}s")
print(f"Average time WITH search: {avg_with:.1f}s")
print(f"Average overhead: +{avg_with - avg_without:.1f}s ({(avg_with/avg_without - 1)*100:.0f}% increase)")