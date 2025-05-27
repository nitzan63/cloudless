from pyspark.sql import SparkSession

def main():
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("TestSparkJob") \
        .getOrCreate()
    
    # Create a simple DataFrame
    data = [("Alice", 1), ("Bob", 2), ("Charlie", 3)]
    df = spark.createDataFrame(data, ["name", "value"])
    
    # Show the DataFrame
    df.show()
    
    # Stop Spark session
    spark.stop()

if __name__ == "__main__":
    main() 