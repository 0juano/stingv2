#!/usr/bin/env python3
"""
A/B Test with 10 regulatory-focused questions
"""
import subprocess
import time
import json
from datetime import datetime

# 10 representative regulatory questions
TEST_QUESTIONS = [
    # BCRA (2 questions)
    {
        "question": "¿Cuáles son los límites vigentes del BCRA para pagos de servicios digitales al exterior?",
        "agents": ["bcra"],
        "category": "payment_limits"
    },
    {
        "question": "¿Qué requisitos pide el BCRA para transferir dólares al exterior en 2024?",
        "agents": ["bcra"],
        "category": "transfer_requirements"
    },
    
    # COMEX (3 questions)
    {
        "question": "¿Qué documentación y aranceles necesito para importar notebooks según normativa 2024?",
        "agents": ["comex"],
        "category": "import_tariffs"
    },
    {
        "question": "¿Cómo gestionar el SIMI para importación de insumos médicos?",
        "agents": ["comex"],
        "category": "import_process"
    },
    {
        "question": "¿Qué licencias necesito para importar productos electrónicos?",
        "agents": ["comex"],
        "category": "import_licenses"
    },
    
    # SENASA (2 questions)
    {
        "question": "¿Qué protocolo sanitario vigente aplica para exportar carne vacuna a China?",
        "agents": ["senasa"],
        "category": "export_protocol"
    },
    {
        "question": "¿Cuáles son los pasos para obtener certificado fitosanitario para limones a Europa?",
        "agents": ["senasa"],
        "category": "phytosanitary_cert"
    },
    
    # Multi-agent (3 questions)
    {
        "question": "¿Cómo importar maquinaria industrial y gestionar el pago según normativa actual?",
        "agents": ["comex", "bcra"],
        "category": "import_and_payment"
    },
    {
        "question": "¿Qué permisos necesito para exportar miel orgánica y cómo liquido las divisas?",
        "agents": ["senasa", "comex", "bcra"],
        "category": "export_complete"
    },
    {
        "question": "¿Procedimiento completo para importar productos farmacéuticos en 2024?",
        "agents": ["comex", "senasa"],
        "category": "pharma_import"
    }
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
    
    # Restart all services
    print(f"  {'Enabling' if enable else 'Disabling'} search and restarting services...")
    subprocess.run(["docker-compose", "restart"], capture_output=True)
    time.sleep(10)  # Give services time to restart

def test_question(question_data):
    """Test a single question"""
    start = time.time()
    result = subprocess.run(
        ["python3", "orchestrator_multiagent.py", question_data["question"]],
        capture_output=True,
        text=True
    )
    duration = time.time() - start
    
    # Extract key information
    output = result.stdout
    has_2024 = "2024" in output
    has_decree = "Decreto" in output or "Resolución" in output or "Comunicación" in output
    has_error = "error" in result.stderr.lower() if result.stderr else False
    
    return {
        "question": question_data["question"],
        "category": question_data["category"],
        "expected_agents": question_data["agents"],
        "duration": duration,
        "has_2024": has_2024,
        "has_decree": has_decree,
        "has_error": has_error,
        "output_length": len(output)
    }

def main():
    print("🔬 A/B Test: Regulatory Questions")
    print("=" * 60)
    print(f"Testing {len(TEST_QUESTIONS)} questions")
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    results = {
        "test_date": datetime.now().isoformat(),
        "questions_tested": len(TEST_QUESTIONS),
        "without_search": [],
        "with_search": []
    }
    
    # Test WITHOUT search
    print("\n📊 Phase 1: Testing WITHOUT search...")
    toggle_search(False)
    
    for i, q in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[{i}/{len(TEST_QUESTIONS)}] {q['question'][:60]}...")
        result = test_question(q)
        results["without_search"].append(result)
        print(f"  ⏱️  {result['duration']:.1f}s | Agents: {', '.join(q['agents'])}")
        if result['has_error']:
            print("  ❌ Error occurred")
    
    # Test WITH search
    print("\n\n📊 Phase 2: Testing WITH search...")
    toggle_search(True)
    
    for i, q in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[{i}/{len(TEST_QUESTIONS)}] {q['question'][:60]}...")
        result = test_question(q)
        results["with_search"].append(result)
        print(f"  ⏱️  {result['duration']:.1f}s | Agents: {', '.join(q['agents'])}")
        if result['has_2024']:
            print("  📅 Contains 2024 information")
        if result['has_decree']:
            print("  📋 Contains specific regulations")
    
    # Analysis
    print("\n\n📈 RESULTS ANALYSIS")
    print("=" * 60)
    
    # Calculate averages
    without_times = [r['duration'] for r in results['without_search'] if not r['has_error']]
    with_times = [r['duration'] for r in results['with_search'] if not r['has_error']]
    
    avg_without = sum(without_times) / len(without_times) if without_times else 0
    avg_with = sum(with_times) / len(with_times) if with_times else 0
    
    print(f"\nTime Analysis:")
    print(f"  Average WITHOUT search: {avg_without:.1f}s")
    print(f"  Average WITH search: {avg_with:.1f}s")
    print(f"  Average overhead: +{avg_with - avg_without:.1f}s ({((avg_with/avg_without - 1) * 100):.0f}% increase)")
    
    # Quality improvements
    improvements = 0
    for i in range(len(TEST_QUESTIONS)):
        w_result = results['with_search'][i]
        wo_result = results['without_search'][i]
        
        if (w_result['has_2024'] and not wo_result['has_2024']) or \
           (w_result['has_decree'] and not wo_result['has_decree']):
            improvements += 1
    
    print(f"\nQuality Analysis:")
    print(f"  Questions improved with search: {improvements}/{len(TEST_QUESTIONS)} ({improvements/len(TEST_QUESTIONS)*100:.0f}%)")
    print(f"  2024 references added: {sum(1 for r in results['with_search'] if r['has_2024'])}")
    print(f"  Specific regulations found: {sum(1 for r in results['with_search'] if r['has_decree'])}")
    
    # Save detailed results
    filename = f"ab_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Detailed results saved to: {filename}")
    
    # Reset to original state
    toggle_search(False)
    print("\n🔧 Search disabled (reset to original state)")

if __name__ == "__main__":
    main()