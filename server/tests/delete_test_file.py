from server.services.storage.storage_service import StorageService

def delete_test_file():
    storage = StorageService()
    # Replace with the file path from your test output
    file_path = 'uploads/20250416_160408_test.txt'
    
    print(f"Deleting file: {file_path}")
    result = storage.delete_file(file_path)
    print(f"Delete result: {result}")

if __name__ == "__main__":
    delete_test_file() 