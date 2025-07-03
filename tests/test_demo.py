#!/usr/bin/env python3
"""Quick demo of the bureaucracy oracle with a few test queries"""
import asyncio
from orchestrator import BureaucracyOracle

async def demo():
    """Run a quick demo with 5 diverse queries"""
    
    test_queries = [
        {
            "code": 111,
            "question": "¿Cuál es el saldo disponible de la cuota SIRA para pagar importaciones de insumos médicos en julio 2025?",
            "expected": "bcra"
        },
        {
            "code": 104,
            "question": "Si quiero vender carne bovina congelada a China, ¿qué certificado HGP free exige Senasa, qué arancel paga en Aduana y cómo liquido las divisas según la Comunicación A 7622?",
            "expected": "multiple (senasa, comex, bcra)"
        },
        {
            "code": 127,
            "question": "¿Qué beneficios otorga la Ley de Economía del Conocimiento al exportar servicios de software?",
            "expected": "comex"
        },
        {
            "code": 116,
            "question": "Indicá los límites máximos de residuos de pesticidas para arándanos frescos destinados a la Unión Europea.",
            "expected": "senasa"
        },
        {
            "code": 109,
            "question": "Al prefinanciar exportaciones de trigo con un banco del exterior, ¿qué tasa de interés máxima admite el BCRA y cómo registro la operación en el SIMI?",
            "expected": "bcra/comex"
        }
    ]
    
    oracle = BureaucracyOracle()
    
    print("🏛️ BUREAUCRACY ORACLE DEMO")
    print("=" * 70)
    print("Testing 5 diverse queries to show system capabilities\n")
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}/5 (Q{test['code']})")
        print(f"Expected: {test['expected']}")
        print(f"Question: {test['question']}\n")
        
        try:
            result = await oracle.process_query(test['question'])
            
            if result["success"]:
                print(result["response"])
                print(f"\n💰 Cost: ${result['total_cost']:.4f}")
            else:
                print(f"❌ {result['message']}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Small delay between queries
        if i < len(test_queries):
            await asyncio.sleep(2)
    
    print(f"\n{'='*70}")
    print(f"Demo complete! Total cost: ${oracle.total_cost:.4f}")

if __name__ == "__main__":
    asyncio.run(demo())