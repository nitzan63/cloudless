import os
import asyncio
from urllib.parse import quote
from dotenv import load_dotenv
load_dotenv()
import subprocess

def submit_to_spark(file_path):
    cmd = (
        f"docker exec spark-master bin/spark-submit  "
        f"--conf spark.driver.host={os.environ.get('DRIVER_HOST')} "
        f"--conf spark.driver.port={os.environ.get('DRIVER_PORT')} "
        f"--conf spark.blockManager.port={os.environ.get('BLOCK_MANAGER_PORT')} "
        f"--conf spark.driver.bindAddress={os.environ.get('BIND_ADDRESS')} "
        f"--master {os.environ.get('SPARK_MASTER')} "
        f"{file_path}"
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    print("DONE")
