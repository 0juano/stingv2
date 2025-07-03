#!/usr/bin/env python3
"""Parallel A/B test - runs multiple questions simultaneously"""
import asyncio
import subprocess
import time
import json
from datetime import datetime
import concurrent.futures

# 10 regulatory questions
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

def test_single_question(args):
    """Test one question (for parallel execution)"""
    question, idx = args
    start = time.time()
    
    try:
        result = subprocess.run(
            ["python3", "orchestrator_multiagent.py", question],
            capture_output=True,
            text=True,
            timeout=35
        )
        duration = time.time() - start
        output = result.stdout
        
        # Extract quality indicators
        has_reg = any(term in output for term in ["Resolución", "Decreto", "Comunicación A", "RG "])
        has_year = any(year in output for year in ["2024", "2025"])
        
        print(f"  [{idx+1}/10] Completed: {question[:30]}... {duration:.1f}s")
        
        return {
            "question": question,
            "duration": duration,
            "has_regulation": has_reg,
            "has_year": has_year,
            "success": True
        }
    except Exception as e:
        print(f"  [{idx+1}/10] Failed: {question[:30]}...")
        return {
            "question": question,
            "duration": 35.0,
            "has_regulation": False,
            "has_year": False,
            "success": False
        }

def set_search_env(enabled):
    """Set search environment variable"""
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    with open('.env', 'w') as f:
        for line in lines:
            if line.startswith("ENABLE_SEARCH="):
                f.write(f"ENABLE_SEARCH={'true' if enabled else 'false'}\n")
            else:
                f.write(line)
    
    # Quick restart key services
    subprocess.run(["docker-compose", "restart", "comex", "bcra", "senasa"], 
                   capture_output=True, timeout=20)
    time.sleep(5)

def run_parallel_tests(search_enabled):
    """Run all questions in parallel"""
    print(f"\n{'WITH' if search_enabled else 'WITHOUT'} Search - Running 10 questions in parallel...")
    print("This will take ~30-40 seconds...")
    
    # Run up to 3 questions at a time to avoid overwhelming the system
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all questions with their indices
        future_to_question = {
            executor.submit(test_single_question, (q, i)): (q, i) 
            for i, q in enumerate(QUESTIONS)
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_question):
            result = future.result()
            results.append(result)
    
    # Sort results by original question order
    results.sort(key=lambda x: QUESTIONS.index(x['question']))
    return results

# Main execution
print("🚀 PARALLEL A/B Test - 10 Questions")
print("=" * 60)
print(f"Start: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 60)

all_results = {
    "test_date": datetime.now().isoformat(),
    "questions": QUESTIONS,
    "without_search": [],
    "with_search": []
}

# Phase 1: WITHOUT search
print("\n📊 Phase 1: Testing WITHOUT search")
set_search_env(False)
all_results["without_search"] = run_parallel_tests(False)

# Phase 2: WITH search
print("\n📊 Phase 2: Testing WITH search")
set_search_env(True)
all_results["with_search"] = run_parallel_tests(True)

# Analysis
print("\n" + "=" * 60)
print("📈 RESULTS ANALYSIS")
print("=" * 60)

# Calculate times
wo_times = [r['duration'] for r in all_results['without_search'] if r['success']]
w_times = [r['duration'] for r in all_results['with_search'] if r['success']]

if wo_times and w_times:
    avg_wo = sum(wo_times) / len(wo_times)
    avg_w = sum(w_times) / len(w_times)
    
    print(f"\nTiming Results:")
    print(f"  Average WITHOUT search: {avg_wo:.1f}s")
    print(f"  Average WITH search: {avg_w:.1f}s")
    print(f"  Average overhead: {avg_w - avg_wo:+.1f}s ({(avg_w/avg_wo - 1)*100:+.0f}%)")

# Quality analysis
print(f"\nQuality Analysis:")
improvements = 0
for i in range(len(QUESTIONS)):
    wo = all_results['without_search'][i]
    w = all_results['with_search'][i]
    
    # Check improvements
    improved = False
    if w['success'] and wo['success']:
        if (w['has_regulation'] and not wo['has_regulation']) or \
           (w['has_year'] and not wo['has_year']):
            improved = True
            improvements += 1
    
    # Print comparison for each question
    print(f"\n  Q{i+1}: {QUESTIONS[i][:50]}...")
    print(f"    Without: {wo['duration']:.1f}s" + 
          (" [REG]" if wo['has_regulation'] else "") + 
          (" [YR]" if wo['has_year'] else ""))
    print(f"    With:    {w['duration']:.1f}s" + 
          (" [REG]" if w['has_regulation'] else "") + 
          (" [YR]" if w['has_year'] else "") +
          (" ✓ IMPROVED" if improved else ""))

print(f"\nTotal improvements: {improvements}/10 ({improvements*10}%)")

# Save results
filename = f"parallel_ab_results_{datetime.now().strftime('%H%M%S')}.json"
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"\n✅ Complete results saved to: {filename}")
print(f"End: {datetime.now().strftime('%H:%M:%S')}")

# Reset environment
set_search_env(False)
print("\n🔧 Environment reset (search disabled)")