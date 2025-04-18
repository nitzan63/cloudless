from services.script_processor import ScriptProcessor
import pytest
import ray
from ray.util.client.ray_client_helpers import ray_start_client_server

def test_wrap_script():
    # Sample script that would be submitted by a user
    test_script = '''
def main(file_path, epochs=10):
    # Simulate ML training
    print(f"Training model using {file_path} for {epochs} epochs")
    return f"Model trained using {file_path} for {epochs} epochs"
'''
    
    processor = ScriptProcessor()
    execute_func = processor.wrap_script(test_script)
    
    # Start Ray in debug mode
    with ray_start_client_server():
        # Test the function
        result = ray.get(execute_func.remote("data.csv", epochs=5))
        
        # Verify the result
        assert result["status"] == "success"
        assert "Model trained using data.csv for 5 epochs" in result["result"]

def test_wrap_script_preserves_functionality():
    # Test script with nested functions and classes
    test_script = '''
def helper_function():
    return "helper"

def main(file_path, param1=None):
    def nested_function():
        return "nested"
        
    result = helper_function()
    return f"Processed {file_path} with result {result}"
'''
    
    processor = ScriptProcessor()
    execute_func = processor.wrap_script(test_script)
    
    # Start Ray in debug mode
    with ray_start_client_server():
        # Test the function
        result = ray.get(execute_func.remote("test.txt", param1="value"))
        
        # Verify the result
        assert result["status"] == "success"
        assert "Processed test.txt with result helper" in result["result"]

def test_validate_script_valid():
    test_script = '''
def main(file_path, param1=None):
    return f"Processing {file_path}"
'''
    processor = ScriptProcessor()
    assert processor.validate_script(test_script) is True

def test_validate_script_invalid_syntax():
    test_script = '''
def main(file_path)
    return "Invalid syntax"
'''
    processor = ScriptProcessor()
    assert processor.validate_script(test_script) is False

def test_validate_script_missing_main():
    test_script = '''
def process(file_path):
    return "No main function"
'''
    processor = ScriptProcessor()
    assert processor.validate_script(test_script) is False

def test_validate_script_wrong_arguments():
    test_script = '''
def main(wrong_arg):
    return "Wrong argument name"
'''
    processor = ScriptProcessor()
    assert processor.validate_script(test_script) is False

def test_wrap_script_invalid_raises():
    test_script = '''
def wrong_name(file_path):
    return "No main function"
'''
    processor = ScriptProcessor()
    with pytest.raises(ValueError, match="Invalid script: Must contain a main"):
        processor.wrap_script(test_script)

def test_wrap_script_error_handling():
    test_script = '''
def main(file_path, **kwargs):
    raise ValueError("Test error")
'''
    processor = ScriptProcessor()
    execute_func = processor.wrap_script(test_script)
    
    # Start Ray in debug mode
    with ray_start_client_server():
        # Test the function
        result = ray.get(execute_func.remote("test.txt"))
        
        # Verify error handling
        assert result["status"] == "error"
        assert "Test error" in result["error"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 