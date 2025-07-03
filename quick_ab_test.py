#!/usr/bin/env python3
"""Quick A/B test - 3 questions, no restarts"""
import subprocess
import time
import json
import os

# Just 3 diverse questions
QUESTIONS = [
    "¿Qué aranceles pagan los notebooks?",
    "¿Cuáles son los límites para pagos de Netflix?", 
    "¿Cómo exportar carne vacuna a China?"
]

def test_question(q):
    """Test a single question"""
    start = time.time()
    result = subprocess.run(
        ["python3", "orchestrator_multiagent.py", q],
        capture_output=True,
        text=True
    )
    duration = time.time() - start
    
    output = result.stdout
    has_reg = any(x in output for x in ["Resolución", "Decreto", "Comunicación", "RG "])
    has_year = any(y in output for y in ["2024", "2025"])
    
    # Extract specific values if present
    import re
    percentages = re.findall(r'\d+(?:\.\d+)?%', output)
    regulations = re.findall(r'(?:RG|Resolución|Comunicación A)\s*\d+/\d+', output)
    
    return {
        "duration": duration,
        "has_regulation": has_reg,
        "has_year": has_year,
        "percentages": percentages[:3],  # First 3 percentages found
        "regulations": regulations[:3],   # First 3 regulations found
        "output_preview": output[:200] if output else "No output"
    }

print("🚀 Quick A/B Test - 3 Questions")
print("=" * 50)

results = {"without_search": [], "with_search": []}

# Test WITHOUT search
print("\n📊 WITHOUT Search:")
os.environ['ENABLE_SEARCH'] = 'false'

for i, q in enumerate(QUESTIONS, 1):
    print(f"[{i}/3] {q[:40]}...", end=" ", flush=True)
    r = test_question(q)
    results["without_search"].append({**r, "question": q})
    print(f"{r['duration']:.1f}s")

# Test WITH search  
print("\n📊 WITH Search:")
os.environ['ENABLE_SEARCH'] = 'true'

for i, q in enumerate(QUESTIONS, 1):
    print(f"[{i}/3] {q[:40]}...", end=" ", flush=True)
    r = test_question(q)
    results["with_search"].append({**r, "question": q})
    print(f"{r['duration']:.1f}s" + (" [REG]" if r['regulations'] else ""))

# Compare results
print("\n📈 COMPARISON:")
print("-" * 70)

for i in range(3):
    q = QUESTIONS[i]
    wo = results["without_search"][i]
    w = results["with_search"][i]
    
    print(f"\n{q}:")
    print(f"  Without: {wo['duration']:.1f}s - {wo['regulations'] or 'No specific regulations'}")
    print(f"  With:    {w['duration']:.1f}s - {w['regulations'] or 'No specific regulations'}")
    
    if w['regulations'] and not wo['regulations']:
        print(f"  ✓ Search added: {w['regulations']}")
    elif w['regulations'] != wo['regulations']:
        print(f"  ✓ Search improved: {wo['regulations']} → {w['regulations']}")

# Summary
avg_wo = sum(r['duration'] for r in results['without_search']) / 3
avg_w = sum(r['duration'] for r in results['with_search']) / 3

print(f"\n📊 SUMMARY:")
print(f"Average WITHOUT search: {avg_wo:.1f}s")
print(f"Average WITH search: {avg_w:.1f}s")
print(f"Overhead: {avg_w - avg_wo:+.1f}s ({(avg_w/avg_wo - 1)*100:+.0f}%)")

# Save
with open('quick_ab_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\n✅ Results saved to quick_ab_results.json")