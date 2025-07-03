#!/usr/bin/env python3
"""Quick A/B test with 3 questions"""
import subprocess
import time
import json

questions = [
    "¿Qué documentación y aranceles necesito para importar notebooks?",
    "¿Cuáles son los límites del BCRA para pagos de Netflix y Spotify?",
    "¿Qué protocolo sanitario necesito para exportar carne vacuna a China?"
]

def test_batch(enable_search):
    # Update .env
    with open('.env', 'r') as f:
        lines = f.readlines()
    with open('.env', 'w') as f:
        for line in lines:
            if line.startswith("ENABLE_SEARCH="):
                f.write(f"ENABLE_SEARCH={'true' if enable_search else 'false'}\n")
            else:
                f.write(line)
    
    # Restart services
    subprocess.run(["docker-compose", "restart", "comex", "bcra", "senasa"], capture_output=True)
    time.sleep(5)
    
    results = []
    for q in questions:
        print(f"Testing: {q[:50]}...")
        start = time.time()
        result = subprocess.run(
            ["python3", "orchestrator_multiagent.py", q],
            capture_output=True,
            text=True,
            timeout=30
        )
        duration = time.time() - start
        
        results.append({
            "question": q,
            "duration": duration,
            "has_2024": "2024" in result.stdout,
            "has_regulation": any(x in result.stdout for x in ["Decreto", "Resolución", "Comunicación", "Protocolo"]),
            "output_size": len(result.stdout)
        })
        print(f"  Done in {duration:.1f}s")
    
    return results

print("🚀 Quick A/B Test (3 questions)\n")

# Test without search
print("Testing WITHOUT search...")
without = test_batch(False)

# Test with search
print("\nTesting WITH search...")
with_search = test_batch(True)

# Results
print("\n📊 RESULTS:")
print("-" * 60)
print(f"{'Question':<35} {'Without':<10} {'With':<10} {'Diff'}")
print("-" * 60)

for i in range(3):
    q = questions[i][:33]
    w_time = without[i]['duration']
    s_time = with_search[i]['duration']
    diff = s_time - w_time
    print(f"{q:<35} {w_time:>6.1f}s    {s_time:>6.1f}s    {diff:+.1f}s")
    
    if with_search[i]['has_regulation'] and not without[i]['has_regulation']:
        print(f"  → Found specific regulations!")
    if with_search[i]['has_2024'] and not without[i]['has_2024']:
        print(f"  → Added 2024 information!")

# Save results
with open('ab_quick_results.json', 'w') as f:
    json.dump({
        "without_search": without,
        "with_search": with_search,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }, f, indent=2)

# Reset
subprocess.run(["sed", "-i", "", "s/ENABLE_SEARCH=true/ENABLE_SEARCH=false/", ".env"], capture_output=True)