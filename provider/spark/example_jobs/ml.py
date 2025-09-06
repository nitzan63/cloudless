from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml import Pipeline

# Initialize Spark session
spark = SparkSession.builder \
    .appName("SimpleClassification") \
    .getOrCreate()

# Create sample data
data = spark.createDataFrame([
    (0.0, 1.0, 0.5, 0),
    (1.0, 2.0, 1.5, 1),
    (0.5, 1.5, 0.8, 0),
    (2.0, 3.0, 2.1, 1),
    (1.5, 2.5, 1.8, 1),
    (0.2, 0.8, 0.3, 0),
    (1.8, 2.8, 2.0, 1),
    (0.3, 1.2, 0.6, 0)
], ["feature1", "feature2", "feature3", "label"])

# Prepare features
assembler = VectorAssembler(
    inputCols=["feature1", "feature2", "feature3"],
    outputCol="features"
)

# Create classifier
lr = LogisticRegression(
    featuresCol="features",
    labelCol="label"
)

# Create pipeline
pipeline = Pipeline(stages=[assembler, lr])

# Split data
train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)

# Train model
model = pipeline.fit(train_data)

# Make predictions
predictions = model.transform(test_data)

# Show results
predictions.select("features", "label", "prediction", "probability").show()

# Evaluate model
evaluator = BinaryClassificationEvaluator()
auc = evaluator.evaluate(predictions)
print(f"AUC: {auc}")

spark.stop()