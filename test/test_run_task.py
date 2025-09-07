import requests
import time
import os
import sys
from pathlib import Path

# Add the project root to the Python path to import modules
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

SERVER_URL = "http://34.61.53.245:8000"

def test_submit_wordcount_task():
    """
    Test submitting the wordcount.py task to the server endpoint
    """
    # Server configuration
    TASK_ENDPOINT = f"{SERVER_URL}/api/tasks"
    
    # Path to the wordcount.py file
    wordcount_file_path = project_root / "provider" / "spark" / "example_jobs" / "wordcount.py"
    
    print(f"Testing task submission with wordcount.py")
    print(f"Server URL: {SERVER_URL}")
    print(f"Wordcount file path: {wordcount_file_path}")
    
    # Check if the wordcount.py file exists
    if not wordcount_file_path.exists():
        print(f"❌ Error: Wordcount file not found at {wordcount_file_path}")
        return False
    
    # Check if server is running
    try:
        health_response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print(f"❌ Server health check failed: {health_response.status_code}")
            return False
        print("✅ Server is healthy")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Prepare the task submission
    task_data = {
        'created_by': 'admin',
        'requested_workers_amount': '1'
    }
    
    # Prepare the file for upload
    files = {
        'file': ('wordcount.py', open(wordcount_file_path, 'rb'), 'text/plain')
    }
    
    print("\n📤 Submitting task...")
    
    try:
        # Submit the task
        response = requests.post(
            TASK_ENDPOINT,
            data=task_data,
            files=files,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Task submitted successfully!")
            print(f"Task details: {result}")
            
            # Extract task ID for monitoring
            task_id = result.get('task', {}).get('task_id')
            if task_id:
                print(f"\n📋 Task ID: {task_id}")
                return monitor_task_status(SERVER_URL, task_id)
            else:
                print("⚠️  No task ID returned in response")
                return True
        else:
            print(f"❌ Task submission failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        # Close the file
        files['file'][1].close()

def monitor_task_status(server_url, task_id, max_wait_time=300):
    """
    Monitor the status of a submitted task
    
    Args:
        server_url: The base URL of the server
        task_id: The ID of the task to monitor
        max_wait_time: Maximum time to wait for task completion (seconds)
    
    Returns:
        bool: True if task completed successfully, False otherwise
    """
    print(f"\n📊 Monitoring task {task_id}...")
    print(f"Max wait time: {max_wait_time} seconds")
    
    start_time = time.time()
    check_interval = 5  # Check every 5 seconds
    
    while time.time() - start_time < max_wait_time:
        try:
            # Get task status
            response = requests.get(f"{server_url}/api/tasks/{task_id}", timeout=10)
            
            if response.status_code == 200:
                task = response.json()
                status = task.get('status', 'unknown')
                print(f"⏱️  [{time.strftime('%H:%M:%S')}] Task status: {status}")
                
                # Check if task is completed
                if status in ['completed', 'finished', 'done']:
                    print("✅ Task completed successfully!")
                    print(f"Final task details: {task}")
                    return True
                elif status in ['failed', 'error', 'cancelled']:
                    print(f"❌ Task failed with status: {status}")
                    print(f"Task details: {task}")
                    return False
                elif status in ['running', 'processing', 'executing']:
                    print("🔄 Task is running...")
                else:
                    print(f"⏳ Task is in status: {status}")
            else:
                print(f"⚠️  Failed to get task status: {response.status_code}")
                print(f"Response: {response.text}")
            
            # Wait before next check
            time.sleep(check_interval)
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Error checking task status: {e}")
            time.sleep(check_interval)
        except Exception as e:
            print(f"❌ Unexpected error monitoring task: {e}")
            return False
    
    print(f"⏰ Timeout reached ({max_wait_time}s). Task may still be running.")
    return False

def test_get_all_tasks():
    """
    Test getting all tasks from the server
    """
    SERVER_URL = "http://localhost:8000"
    
    print(f"\n📋 Testing get all tasks...")
    
    try:
        response = requests.get(f"{SERVER_URL}/api/tasks", timeout=10)
        
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ Retrieved {len(tasks)} tasks")
            for i, task in enumerate(tasks):
                print(f"  Task {i+1}: ID={task.get('task_id')}, Status={task.get('status')}, Created by={task.get('created_by')}")
            return True
        else:
            print(f"❌ Failed to get tasks: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """
    Main test function
    """
    print("🚀 Starting task submission test")
    print("=" * 50)
    
    # Test 1: Submit wordcount task
    success = test_submit_wordcount_task()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ Task submission test completed successfully!")
    else:
        print("\n" + "=" * 50)
        print("❌ Task submission test failed!")
    
    # Test 2: Get all tasks (optional)
    print("\n" + "=" * 50)
    test_get_all_tasks()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    main()
