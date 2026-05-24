#!/usr/bin/env python
# Test Groq API directly

import sys
import time
from groq_handler import GroqHandler

try:
    print("=== Initializing Groq Handler ===")
    handler = GroqHandler()
    print("✓ Handler initialized")
    
    print("\n=== Testing question: siapa presiden indonesia ===")
    start = time.time()
    result = handler.ask("siapa presiden indonesia")
    elapsed = time.time() - start
    
    print(f"\nResponse received in {elapsed:.2f} seconds")
    print(f"Response length: {len(result)} chars")
    print(f"Response: [{result}]")
    
    if not result or result.strip() == "":
        print("\n❌ ERROR: Empty response received!")
        sys.exit(1)
    else:
        print("\n✓ SUCCESS: Response received and not empty")
        
except Exception as e:
    print(f"\n❌ Exception: {type(e).__name__}")
    print(f"Message: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
