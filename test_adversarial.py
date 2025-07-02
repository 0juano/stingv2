#!/usr/bin/env python3
"""Adversarial test cases to check for overfitting"""
import asyncio
import httpx
import json

async def test_adversarial():
    """Test with edge cases and ambiguous queries"""
    
    test_cases = [
        # Edge cases - ambiguous or tricky queries
        {
            "question": "¿Cómo registro una empresa?",  # Corporate law - should be out_of_scope
            "expected": "out_of_scope",
            "reason": "Corporate registration is not covered by BCRA/Comex/Senasa"
        },
        {
            "question": "¿Qué impuestos pago por exportar?",  # Tax question - not directly covered
            "expected": "out_of_scope",  # or maybe comex
            "reason": "Tax questions are AFIP domain, not covered"
        },
        {
            "question": "¿Puedo exportar oro?",  # Ambiguous - could be BCRA or Comex
            "expected": ["bcra", "comex"],
            "reason": "Gold involves both monetary (BCRA) and export (Comex) regulations"
        },
        {
            "question": "Necesito un préstamo para importar",  # Banking, not regulations
            "expected": "out_of_scope",
            "reason": "Loan requests are banking services, not regulatory guidance"
        },
        {
            "question": "¿Cuánto vale el dólar hoy?",  # Exchange rate query
            "expected": "out_of_scope",
            "reason": "Current rates are not regulatory guidance"
        },
        {
            "question": "Quiero vender software al exterior",  # Services export
            "expected": ["bcra", "comex"],
            "reason": "Software exports involve both trade procedures and currency regulations"
        },
        {
            "question": "¿Cómo importo un auto usado para uso personal?",  # Personal import
            "expected": "comex",
            "reason": "Personal vehicle imports are customs matters"
        },
        {
            "question": "bicicletas china antidumping",  # Minimal context
            "expected": "comex",
            "reason": "Antidumping is a trade/customs issue"
        },
        {
            "question": "SIMI SIRA pago",  # Just acronyms
            "expected": "bcra",
            "reason": "SIMI/SIRA are BCRA payment systems"
        },
        {
            "question": "certificado",  # Too vague
            "expected": "out_of_scope",
            "reason": "Too vague without context"
        },
        # Queries with misleading keywords
        {
            "question": "¿El banco central controla las exportaciones de soja?",
            "expected": "senasa",  # Despite mentioning BCRA, it's about soy exports
            "reason": "Soy exports are agricultural, primarily Senasa domain"
        },
        {
            "question": "¿Qué dice Senasa sobre el pago de importaciones?",
            "expected": "bcra",  # Despite mentioning Senasa, it's about payments
            "reason": "Import payments are BCRA domain"
        },
        # Multi-language or typos
        {
            "question": "How to export meat to China?",  # English
            "expected": ["senasa", "comex"],
            "reason": "Should handle English queries"
        },
        {
            "question": "Quiero esportar cane bovina a china",  # Typos
            "expected": ["senasa", "comex"],
            "reason": "Should handle typos"
        },
        # Complex scenarios
        {
            "question": "Mi empresa de tecnología quiere facturar servicios cloud a Brasil, cobrar en reales y traer los fondos, ¿qué necesito?",
            "expected": ["bcra", "comex"],
            "reason": "Complex service export with currency considerations"
        }
    ]
    
    print("🧪 Running Adversarial Tests")
    print("=" * 60)
    
    correct = 0
    total = len(test_cases)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}/{total}] Testing: {test['question'][:60]}...")
        print(f"Expected: {test['expected']}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8001/route",
                    json={"question": test["question"]},
                    timeout=30.0
                )
                result = response.json()
                
            decision = result['decision']
            selected = decision.get('primary_agent') or decision.get('agent')
            agents = decision.get('agents', [])
            confidence = decision.get('confidence', 0)
            
            # Check if correct
            if isinstance(test['expected'], list):
                # For multi-agent cases, check if primary agent is in expected list
                is_correct = selected in test['expected']
            else:
                is_correct = selected == test['expected']
            
            if is_correct:
                correct += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            
            print(f"Selected: {selected} (confidence: {confidence:.0%}) {status}")
            if agents:
                print(f"All agents: {agents}")
            print(f"Reason: {decision.get('reason', 'N/A')}")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"Results: {correct}/{total} passed ({correct/total*100:.1f}%)")
    print("\nAnalysis:")
    print("- If score is too high (>90%), might indicate overfitting")
    print("- If score is moderate (60-80%), shows good generalization")
    print("- Check which types of queries fail most often")

if __name__ == "__main__":
    asyncio.run(test_adversarial())