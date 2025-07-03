#!/usr/bin/env python3
"""Run ACTUAL A/B test with 10 questions"""
import subprocess
import time
import json
from datetime import datetime

# 10 natural regulatory questions (no explicit temporal keywords)
QUESTIONS = [
    "¿Qué aranceles pagan los notebooks?",
    "¿Cuáles son los límites para pagos de Netflix?",
    "¿Qué documentación necesito para importar celulares?",
    "¿Cómo exportar vino a Brasil?",
    "¿Qué protocolo se usa para exportar carne a China?",
    "¿Cuáles son los requisitos para transferir dólares?",
    "¿Cómo gestionar el SIMI para importar?",
    "¿Qué permisos necesito para exportar miel?",
    "¿Cómo importar maquinaria industrial?",
    "¿Qué necesito para exportar limones a Europa?"
]

def run_single_test(question, iteration):
    """Run a single test and return timing"""
    print(f"  [{iteration}/10] {question[:40]}...", end=" ", flush=True)
    start = time.time()
    
    try:
        result = subprocess.run(
            ["python3", "orchestrator_multiagent.py", question],
            capture_output=True,
            text=True,
            timeout=45
        )
        duration = time.time() - start
        
        # Extract quality indicators
        output = result.stdout
        has_specific_reg = any(term in output for term in ["Resolución", "Decreto", "Comunicación A", "RG "])
        has_year = any(year in output for year in ["2024", "2025"])
        
        print(f"{duration:.1f}s" + (" [REG]" if has_specific_reg else "") + (" [YEAR]" if has_year else ""))
        
        return {
            "question": question,
            "duration": duration,
            "has_specific_reg": has_specific_reg,
            "has_year": has_year,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        return {
            "question": question,
            "duration": 45.0,
            "has_specific_reg": False,
            "has_year": False,
            "success": False
        }

def set_search(enabled):
    """Enable or disable search"""
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    with open('.env', 'w') as f:
        for line in lines:
            if line.startswith("ENABLE_SEARCH="):
                f.write(f"ENABLE_SEARCH={'true' if enabled else 'false'}\n")
            else:
                f.write(line)
    
    # Restart services
    subprocess.run(["docker-compose", "restart", "comex", "bcra", "senasa"], 
                   capture_output=True, timeout=30)
    time.sleep(8)

print("🔬 REAL A/B Test - 10 Questions")
print("=" * 60)
print(f"Start time: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 60)

results = {
    "test_date": datetime.now().isoformat(),
    "without_search": [],
    "with_search": []
}

# Phase 1: WITHOUT search
print("\n📊 Phase 1: WITHOUT Search")
set_search(False)

for i, q in enumerate(QUESTIONS, 1):
    result = run_single_test(q, i)
    results["without_search"].append(result)

# Phase 2: WITH search
print("\n📊 Phase 2: WITH Search")
set_search(True)

for i, q in enumerate(QUESTIONS, 1):
    result = run_single_test(q, i)
    results["with_search"].append(result)

# Analysis
print("\n📈 RESULTS SUMMARY")
print("=" * 60)

# Time analysis
without_times = [r['duration'] for r in results['without_search'] if r['success']]
with_times = [r['duration'] for r in results['with_search'] if r['success']]

if without_times and with_times:
    avg_without = sum(without_times) / len(without_times)
    avg_with = sum(with_times) / len(with_times)
    
    print(f"Average time WITHOUT search: {avg_without:.1f}s")
    print(f"Average time WITH search: {avg_with:.1f}s")
    print(f"Average overhead: +{avg_with - avg_without:.1f}s ({(avg_with/avg_without - 1)*100:.0f}%)")

# Quality analysis
quality_improvements = 0
for i in range(len(QUESTIONS)):
    wo = results['without_search'][i]
    w = results['with_search'][i]
    if (w['has_specific_reg'] and not wo['has_specific_reg']) or \
       (w['has_year'] and not wo['has_year']):
        quality_improvements += 1

print(f"\nQuality improvements: {quality_improvements}/10 ({quality_improvements*10}%)")

# Save results
filename = f"real_ab_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ Results saved to: {filename}")

# Reset
set_search(False)
print("\nSearch disabled (reset)")
print(f"End time: {datetime.now().strftime('%H:%M:%S')}")