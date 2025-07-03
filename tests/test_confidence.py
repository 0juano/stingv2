#!/usr/bin/env python3
"""Test confidence scoring implementation"""
import json

# Test agent response formats
test_responses = [
    {
        "name": "High confidence response",
        "agent": "senasa",
        "response": {
            "Respuesta": "Para exportar carne bovina a China, debe cumplir con los requisitos sanitarios establecidos [Resolución SENASA 68/2023, art. 5]. El establecimiento debe estar habilitado específicamente para China [Resolución SENASA 15/2024, art. 12].",
            "Normativa": [
                {"tipo": "Resolución", "número": "68/2023", "artículo": "5", "año": "2023"},
                {"tipo": "Resolución", "número": "15/2024", "artículo": "12", "año": "2024"}
            ],
            "RequisitosSanitarios": ["Certificación de libre de aftosa", "Análisis de residuos"],
            "CertificadosRequeridos": ["Certificado sanitario internacional", "Certificado de habilitación"],
            "PlazoProcesamiento": "15 días hábiles",
            "confidence": 0.9,
            "confidence_factors": {
                "has_specific_regulations": True,
                "has_exact_articles": True,
                "has_complete_procedures": True,
                "has_recent_updates": True,
                "contains_insufficient_context": False
            }
        }
    },
    {
        "name": "Medium confidence response",
        "agent": "comex",
        "response": {
            "Respuesta": "La exportación de software requiere inscripción en el registro de exportadores y declaración ante AFIP.",
            "Normativa": [
                {"tipo": "Resolución SC", "número": "26/2024", "artículo": "", "año": "2024"}
            ],
            "PasosRequeridos": ["Inscripción en registro", "Declaración AFIP"],
            "confidence": 0.65,
            "confidence_factors": {
                "has_specific_regulations": True,
                "has_exact_articles": False,
                "has_complete_procedures": True,
                "has_ncm_codes": False,
                "has_tariff_rates": False
            }
        }
    },
    {
        "name": "Low confidence response",
        "agent": "bcra",
        "response": {
            "Respuesta": "INSUFFICIENT_CONTEXT - No se encontró normativa específica sobre este tema particular.",
            "confidence": 0.2,
            "confidence_factors": {
                "has_specific_communications": False,
                "has_exact_points": False,
                "has_complete_requirements": False,
                "has_recent_updates": False,
                "contains_insufficient_context": True
            }
        }
    }
]

def calculate_expected_confidence(factors):
    """Calculate confidence based on factors"""
    confidence = 0.5  # Base
    
    if factors.get("contains_insufficient_context"):
        return 0.2
    
    if factors.get("has_specific_regulations") or factors.get("has_specific_communications"):
        confidence += 0.2
    if factors.get("has_exact_articles") or factors.get("has_exact_points"):
        confidence += 0.15
    if factors.get("has_complete_procedures") or factors.get("has_complete_requirements"):
        confidence += 0.1
    if factors.get("has_recent_updates"):
        confidence += 0.05
    if factors.get("has_ncm_codes") or factors.get("has_tariff_rates"):
        confidence += 0.05
        
    return min(confidence, 0.95)

# Test calculations
print("🧪 Testing Confidence Calculations")
print("=" * 60)

for test in test_responses:
    print(f"\n{test['name']} ({test['agent'].upper()}):")
    response = test['response']
    
    # Check if confidence is present
    if 'confidence' in response:
        actual = response['confidence']
        factors = response.get('confidence_factors', {})
        expected = calculate_expected_confidence(factors)
        
        print(f"  Actual confidence: {actual:.2f} ({actual*100:.0f}%)")
        print(f"  Expected confidence: {expected:.2f} ({expected*100:.0f}%)")
        print(f"  Factors: {json.dumps(factors, indent=4)}")
        
        # Verify calculation is reasonable
        if abs(actual - expected) < 0.1:
            print("  ✅ Confidence calculation looks correct")
        else:
            print("  ⚠️  Confidence differs from expected calculation")
    else:
        print("  ❌ No confidence score in response")

print("\n" + "=" * 60)
print("Summary:")
print("- High confidence (90%): Specific regulations with exact articles")
print("- Medium confidence (65%): General regulations without specifics")  
print("- Low confidence (20%): INSUFFICIENT_CONTEXT responses")
print("\nImplementation Notes:")
print("- Agents now calculate their own confidence based on response quality")
print("- Auditor extracts and uses agent confidence (no more hardcoded 95%)")
print("- Final display shows actual confidence with explanations for low scores")