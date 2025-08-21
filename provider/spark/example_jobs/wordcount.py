from pyspark.sql import SparkSession
import time

# Initialize Spark Session
spark = SparkSession.builder.appName("WordCount").getOrCreate()

# Read a simple text file (change path as needed)
text_rdd = spark.sparkContext.parallelize(["hello world", "hello spark", "hello docker"])

# Process the data
word_counts = (
    text_rdd.flatMap(lambda line: line.split(" "))  # Split into words
    .map(lambda word: (word, 1))  # Map words to (word, 1)
    .reduceByKey(lambda a, b: a + b)  # Reduce by key
)

# Collect and print results
for word, count in word_counts.collect():
    print(f"{word}: {count}")

time.sleep(20)

# Stop Spark Session
spark.stop()
