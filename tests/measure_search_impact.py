#!/usr/bin/env python3
"""Measure search impact on 3 questions"""
import subprocess
import time
import os

# Natural questions without temporal keywords
questions = [
    "¿Qué documentación necesito para importar notebooks?",
    "¿Cuáles son los límites para pagos de Netflix?", 
    "¿Cómo exportar carne vacuna a China?"
]

def measure_question(q, search_enabled):
    # Set search flag
    os.environ['ENABLE_SEARCH'] = 'true' if search_enabled else 'false'
    
    start = time.time()
    try:
        # Direct call to avoid subprocess overhead
        import orchestrator_multiagent
        result = orchestrator_multiagent.main(q)
        duration = time.time() - start
        
        # Check for quality indicators
        has_2024 = "2024" in str(result)
        has_specific_reg = any(term in str(result) for term in ["Decreto", "Comunicación A", "Resolución"])
        
        return {
            "duration": duration,
            "has_2024": has_2024,
            "has_specific_reg": has_specific_reg,
            "success": True
        }
    except:
        # Fallback to subprocess
        start = time.time()
        result = subprocess.run(
            ["python3", "orchestrator_multiagent.py", q],
            capture_output=True,
            text=True,
            timeout=40
        )
        duration = time.time() - start
        
        output = result.stdout
        return {
            "duration": duration,
            "has_2024": "2024" in output,
            "has_specific_reg": any(term in output for term in ["Decreto", "Comunicación A", "Resolución"]),
            "success": result.returncode == 0
        }

print("📊 Measuring Search Impact\n")

results = {"without": [], "with": []}

# Test without search
print("Testing WITHOUT search:")
for q in questions:
    print(f"  • {q[:40]}...", end=" ", flush=True)
    r = measure_question(q, False)
    results["without"].append(r)
    print(f"{r['duration']:.1f}s")

print("\nTesting WITH search:")
for q in questions:
    print(f"  • {q[:40]}...", end=" ", flush=True)
    r = measure_question(q, True)
    results["with"].append(r)
    print(f"{r['duration']:.1f}s" + (" [2024]" if r['has_2024'] else "") + (" [REG]" if r['has_specific_reg'] else ""))

# Summary
print("\n📈 SUMMARY:")
avg_without = sum(r['duration'] for r in results['without']) / len(results['without'])
avg_with = sum(r['duration'] for r in results['with']) / len(results['with'])

print(f"Average time WITHOUT search: {avg_without:.1f}s")
print(f"Average time WITH search: {avg_with:.1f}s")
print(f"Search overhead: +{avg_with - avg_without:.1f}s ({(avg_with/avg_without - 1)*100:.0f}%)")

quality_improvements = sum(1 for i in range(len(questions)) 
                         if (results['with'][i]['has_2024'] and not results['without'][i]['has_2024']) or
                            (results['with'][i]['has_specific_reg'] and not results['without'][i]['has_specific_reg']))

print(f"Quality improvements: {quality_improvements}/{len(questions)}")

# Save for HTML update
import json
with open('search_impact_results.json', 'w') as f:
    json.dump({
        'questions': questions,
        'results': results,
        'summary': {
            'avg_without': avg_without,
            'avg_with': avg_with,
            'overhead_seconds': avg_with - avg_without,
            'overhead_percent': (avg_with/avg_without - 1)*100,
            'quality_improvements': quality_improvements
        }
    }, f, indent=2)