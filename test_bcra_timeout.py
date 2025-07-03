import requests
import time
import json

def test_bcra_directly():
    """Test BCRA agent directly with the pharmaceutical import query"""
    
    query = "¿Proceso completo para importar productos farmacéuticos?"
    
    print(f"Testing BCRA agent with query: {query}")
    print("-" * 60)
    
    # Test BCRA agent directly
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8002/answer",
            json={"question": query},
            timeout=120  # Give it more time
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ BCRA responded in {elapsed:.2f}s")
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"✗ BCRA error: Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"✗ BCRA timeout after {elapsed:.2f}s")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ BCRA error after {elapsed:.2f}s: {str(e)}")

if __name__ == "__main__":
    test_bcra_directly()