import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ray
from services.script_processor import ScriptProcessor

# Example script that we want to wrap
test_script = '''
def main(file_path, epochs=10):
    # This is a simple script that simulates ML training
    print(f"Starting training with {file_path}")
    
    # Simulate some work
    import time
    time.sleep(2)
    
    # Return results
    return f"Finished training on {file_path} after {epochs} epochs"
'''

def load_script_from_file(file_path: str) -> str:
    """Load a script from a file."""
    with open(file_path, 'r') as f:
        return f.read()

def main():
    # Initialize Ray
    ray.init(address="ray://34.134.59.39:10001")
    
    # Initialize the script processor
    processor = ScriptProcessor()
    
    # Example 1: Wrap and execute a string script
    print("\nExample 1: Wrapping and executing a string script")
    print("=" * 50)
    execute_func = processor.wrap_script(test_script)
    print("\nExecuting script...")
    result = ray.get(execute_func.remote("data.csv", epochs=5))
    print(f"Result: {result}")
    print("=" * 50)
    
    # Example 2: Wrap and execute a script from file
    print("\nExample 2: Wrapping and executing a script from file")
    print("=" * 50)
    script_path = os.path.join(os.path.dirname(__file__), 'simple_script.py')
    file_script = load_script_from_file(script_path)
    execute_func = processor.wrap_script(file_script)
    print("\nExecuting script...")
    result = ray.get(execute_func.remote("test.txt"))
    print(f"Result: {result}")
    print("=" * 50)
    
    # Example 3: Try to wrap an invalid script
    print("\nExample 3: Trying to wrap an invalid script")
    print("=" * 50)
    invalid_script_path = os.path.join(os.path.dirname(__file__), 'simple_script_not_valid.py')
    invalid_script = load_script_from_file(invalid_script_path)
    try:
        execute_func = processor.wrap_script(invalid_script)
        print("\nExecuting script...")
        result = ray.get(execute_func.remote("test.txt"))
        print(f"Result: {result}")
    except ValueError as e:
        print(f"Error as expected: {str(e)}")
    print("=" * 50)

if __name__ == "__main__":
    main() 