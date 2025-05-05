from pyspark.sql import SparkSession

# Create a Spark session
spark = SparkSession.builder.appName("CountSparkLines").getOrCreate()

# Example data - replace with a file path if you want
data = [
    "Apache Spark is awesome.",
    "This is a test line.",
    "Spark makes big data processing easy.",
    "Nothing to see here.",
    "Spark again!"
]

# Parallelize the data
rdd = spark.sparkContext.parallelize(data)

# Count lines containing the word 'Spark'
num_spark_lines = rdd.filter(lambda line: "Spark" in line).count()

print(f"Number of lines containing 'Spark': {num_spark_lines}")

# Stop the Spark session
spark.stop()
