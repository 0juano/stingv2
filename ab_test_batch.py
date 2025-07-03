#!/usr/bin/env python3
"""Run A/B test in batches to avoid timeout"""
import subprocess
import time
import json
from datetime import datetime

# 10 questions in 2 batches
BATCH_1 = [
    "¿Qué aranceles pagan los notebooks?",
    "¿Cuáles son los límites para pagos de Netflix?",
    "¿Qué documentación necesito para importar celulares?",
    "¿Cómo exportar vino a Brasil?",
    "¿Qué protocolo se usa para exportar carne a China?"
]

BATCH_2 = [
    "¿Cuáles son los requisitos para transferir dólares?",
    "¿Cómo gestionar el SIMI para importar?",
    "¿Qué permisos necesito para exportar miel?",
    "¿Cómo importar maquinaria industrial?",
    "¿Qué necesito para exportar limones a Europa?"
]

def test_question(q):
    """Test a single question"""
    start = time.time()
    try:
        result = subprocess.run(
            ["python3", "orchestrator_multiagent.py", q],
            capture_output=True,
            text=True,
            timeout=35
        )
        duration = time.time() - start
        output = result.stdout
        
        return {
            "question": q,
            "duration": duration,
            "has_reg": any(x in output for x in ["Resolución", "Decreto", "Comunicación", "RG "]),
            "has_year": any(y in output for y in ["2024", "2025"]),
            "success": True
        }
    except:
        return {
            "question": q,
            "duration": 35.0,
            "has_reg": False,
            "has_year": False,
            "success": False
        }

def run_batch(questions, search_enabled, batch_name):
    """Run a batch of questions"""
    # Set search
    with open('.env', 'r') as f:
        lines = f.readlines()
    with open('.env', 'w') as f:
        for line in lines:
            if line.startswith("ENABLE_SEARCH="):
                f.write(f"ENABLE_SEARCH={'true' if search_enabled else 'false'}\n")
            else:
                f.write(line)
    
    # Quick restart
    subprocess.run(["docker-compose", "restart", "comex", "bcra", "senasa"], 
                   capture_output=True)
    time.sleep(5)
    
    print(f"\n{batch_name} - Search {'ON' if search_enabled else 'OFF'}:")
    results = []
    
    for i, q in enumerate(questions, 1):
        print(f"  [{i}/5] {q[:35]}...", end=" ", flush=True)
        r = test_question(q)
        results.append(r)
        print(f"{r['duration']:.1f}s" + 
              (" [REG]" if r['has_reg'] else "") + 
              (" [YR]" if r['has_year'] else ""))
    
    return results

# Run test
print("🔬 A/B Test - 10 Questions (2 Batches)")
print("=" * 50)

all_results = {
    "without_search": [],
    "with_search": []
}

# Batch 1
print("\n📦 BATCH 1 (Questions 1-5)")
all_results["without_search"].extend(run_batch(BATCH_1, False, "Without Search"))
all_results["with_search"].extend(run_batch(BATCH_1, True, "With Search"))

# Batch 2
print("\n📦 BATCH 2 (Questions 6-10)")
all_results["without_search"].extend(run_batch(BATCH_2, False, "Without Search"))
all_results["with_search"].extend(run_batch(BATCH_2, True, "With Search"))

# Summary
print("\n📊 FINAL RESULTS")
print("=" * 50)

# Calculate averages
wo_times = [r['duration'] for r in all_results['without_search'] if r['success']]
w_times = [r['duration'] for r in all_results['with_search'] if r['success']]

avg_wo = sum(wo_times) / len(wo_times) if wo_times else 0
avg_w = sum(w_times) / len(w_times) if w_times else 0

print(f"Average WITHOUT search: {avg_wo:.1f}s")
print(f"Average WITH search: {avg_w:.1f}s")
print(f"Overhead: +{avg_w - avg_wo:.1f}s ({(avg_w/avg_wo - 1)*100:.0f}%)")

# Quality improvements
improvements = 0
for i in range(10):
    wo = all_results['without_search'][i]
    w = all_results['with_search'][i]
    if (w['has_reg'] and not wo['has_reg']) or (w['has_year'] and not wo['has_year']):
        improvements += 1

print(f"Quality improvements: {improvements}/10")

# Save
filename = f"ab_results_{datetime.now().strftime('%H%M%S')}.json"
with open(filename, 'w') as f:
    json.dump(all_results, f, indent=2)

print(f"\n✅ Saved to: {filename}")