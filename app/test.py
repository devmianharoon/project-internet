from tool import get_providers

def test_get_providers():
       try:
           # Test case 1: Valid provider names
           providers = get_providers(["AT&T", "Xfinity"])
           print("Test 1 - Valid providers:")
           print(providers)

       except Exception as e:
           print(f"Test failed: {e}")

if __name__ == "__main__":
       test_get_providers()