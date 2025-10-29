import os
import json

print("=== Storage Debug Test ===")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

# Test if we can create and write to a file
test_file = "favorites.json"
test_data = {"test": "data"}

try:
    with open(test_file, 'w') as f:
        json.dump(test_data, f)
    print("✓ Successfully wrote to favorites.json")
    
    with open(test_file, 'r') as f:
        loaded_data = json.load(f)
    print(f"✓ Successfully read from favorites.json: {loaded_data}")
    
    # Clean up
    os.remove(test_file)
    print("✓ Successfully deleted test file")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"Error type: {type(e).__name__}")