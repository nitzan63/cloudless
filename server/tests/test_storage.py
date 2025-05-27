from server.services.storage_service import StorageService
import os

def test_storage_service():
    # Initialize the storage service
    storage = StorageService()
    
    # Test file content
    test_content = "Hello, Cloudless Storage!"
    test_filename = "test.txt"
    
    # Test upload
    print("Testing file upload...")
    upload_result = storage.upload_file(test_content, test_filename)
    print(f"Upload result: {upload_result}")
    
    if upload_result['status'] == 'success':
        print("✅ Upload test successful!")
        print(f"File path: {upload_result['file_path']}")
    else:
        print("❌ Upload test failed!")
        print(f"Error: {upload_result['message']}")

if __name__ == "__main__":
    test_storage_service() 