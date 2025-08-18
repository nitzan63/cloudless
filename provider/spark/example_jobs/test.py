from pyspark.sql import SparkSession
from pyspark.sql.functions import rand, randn, when, col, round as spark_round, monotonically_increasing_id
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
import random

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("RandomDataGenerator") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# =============================================================================
# CONFIGURATION - Adjust these parameters to change DataFrame size
# =============================================================================
NUM_CUSTOMERS = 10000      # Size of customers DataFrame
NUM_ORDERS = 25000         # Size of orders DataFrame
NUM_PRODUCTS = 1000        # Size of products DataFrame

print(f"Generating DataFrames with:")
print(f"- Customers: {NUM_CUSTOMERS:,} rows")
print(f"- Orders: {NUM_ORDERS:,} rows") 
print(f"- Products: {NUM_PRODUCTS:,} rows")
print("-" * 50)

# =============================================================================
# Generate Customers DataFrame
# =============================================================================
print("1. Generating Customers DataFrame...")

# Create customers with random data
customers_df = spark.range(1, NUM_CUSTOMERS + 1).select(
    col("id").alias("customer_id"),
    # Random customer names (simplified)
    when(rand() < 0.3, "John").when(rand() < 0.6, "Jane").otherwise("Alex").alias("first_name"),
    when(rand() < 0.25, "Smith").when(rand() < 0.5, "Johnson").when(rand() < 0.75, "Williams").otherwise("Brown").alias("last_name"),
    # Random age between 18 and 80
    (rand() * 62 + 18).cast("int").alias("age"),
    # Random city
    when(rand() < 0.2, "New York").when(rand() < 0.4, "Los Angeles").when(rand() < 0.6, "Chicago").when(rand() < 0.8, "Houston").otherwise("Phoenix").alias("city"),
    # Random salary between 30k and 150k
    spark_round(rand() * 120000 + 30000, 2).alias("annual_salary"),
    # Random customer status
    when(rand() < 0.7, "Active").when(rand() < 0.9, "Inactive").otherwise("Premium").alias("status")
)

print(f"Customers DataFrame created with {customers_df.count():,} rows")
customers_df.show(10)

# =============================================================================
# Generate Products DataFrame  
# =============================================================================
print("\n2. Generating Products DataFrame...")

products_df = spark.range(1, NUM_PRODUCTS + 1).select(
    col("id").alias("product_id"),
    # Random product categories
    when(rand() < 0.2, "Electronics").when(rand() < 0.4, "Clothing").when(rand() < 0.6, "Books").when(rand() < 0.8, "Home").otherwise("Sports").alias("category"),
    # Random prices between $10 and $500
    spark_round(rand() * 490 + 10, 2).alias("price"),
    # Random stock quantity between 0 and 1000
    (rand() * 1000).cast("int").alias("stock_quantity"),
    # Random rating between 1 and 5
    spark_round(rand() * 4 + 1, 1).alias("rating")
)

print(f"Products DataFrame created with {products_df.count():,} rows")
products_df.show(10)

# =============================================================================
# Generate Orders DataFrame
# =============================================================================
print("\n3. Generating Orders DataFrame...")

orders_df = spark.range(1, NUM_ORDERS + 1).select(
    col("id").alias("order_id"),
    # Random customer_id (foreign key to customers)
    (rand() * NUM_CUSTOMERS + 1).cast("int").alias("customer_id"),
    # Random product_id (foreign key to products) 
    (rand() * NUM_PRODUCTS + 1).cast("int").alias("product_id"),
    # Random quantity between 1 and 10
    (rand() * 9 + 1).cast("int").alias("quantity"),
    # Random order value between $20 and $2000
    spark_round(rand() * 1980 + 20, 2).alias("order_value"),
    # Random order status
    when(rand() < 0.6, "Completed").when(rand() < 0.8, "Pending").when(rand() < 0.95, "Shipped").otherwise("Cancelled").alias("order_status")
)

print(f"Orders DataFrame created with {orders_df.count():,} rows")
orders_df.show(10)

# =============================================================================
# FILTERING OPERATIONS
# =============================================================================
print("\n" + "="*60)
print("PERFORMING FILTERING OPERATIONS")
print("="*60)

# Filter 1: High-value customers (salary > 80k and Active status)
print("\n4. Filtering high-value active customers (salary > $80k)...")
high_value_customers = customers_df.filter(
    (col("annual_salary") > 80000) & (col("status") == "Active")
)
print(f"Found {high_value_customers.count():,} high-value active customers")
high_value_customers.show(5)

# Filter 2: Premium products (price > 200 and rating > 4.0)
print("\n5. Filtering premium products (price > $200, rating > 4.0)...")
premium_products = products_df.filter(
    (col("price") > 200) & (col("rating") > 4.0)
)
print(f"Found {premium_products.count():,} premium products")
premium_products.show(5)

# Filter 3: Large completed orders (quantity > 5 and status = Completed)
print("\n6. Filtering large completed orders (quantity > 5)...")
large_orders = orders_df.filter(
    (col("quantity") > 5) & (col("order_status") == "Completed")
)
print(f"Found {large_orders.count():,} large completed orders")
large_orders.show(5)

# =============================================================================
# JOIN OPERATIONS
# =============================================================================
print("\n" + "="*60)
print("PERFORMING JOIN OPERATIONS") 
print("="*60)

# Join 1: Orders with Customer Information
print("\n7. Joining Orders with Customer Information...")
orders_with_customers = orders_df.join(
    customers_df, 
    orders_df.customer_id == customers_df.customer_id,
    "inner"
).select(
    orders_df.order_id,
    orders_df.customer_id,
    customers_df.first_name,
    customers_df.last_name,
    customers_df.city,
    orders_df.order_value,
    orders_df.quantity,
    orders_df.order_status
)

print(f"Orders with customer info: {orders_with_customers.count():,} rows")
orders_with_customers.show(10)

# Join 2: Orders with Product Information
print("\n8. Joining Orders with Product Information...")
orders_with_products = orders_df.join(
    products_df,
    orders_df.product_id == products_df.product_id,
    "inner"
).select(
    orders_df.order_id,
    orders_df.customer_id,
    products_df.category,
    products_df.price.alias("unit_price"),
    orders_df.quantity,
    orders_df.order_value,
    products_df.rating,
    orders_df.order_status
)

print(f"Orders with product info: {orders_with_products.count():,} rows")
orders_with_products.show(10)

# Join 3: Complete Order Information (Orders + Customers + Products)
print("\n9. Creating complete order view (3-way join)...")
complete_orders = orders_df \
    .join(customers_df, orders_df.customer_id == customers_df.customer_id, "inner") \
    .join(products_df, orders_df.product_id == products_df.product_id, "inner") \
    .select(
        orders_df.order_id,
        customers_df.first_name,
        customers_df.last_name,
        customers_df.city,
        customers_df.age,
        products_df.category,
        products_df.price.alias("unit_price"),
        orders_df.quantity,
        orders_df.order_value,
        products_df.rating,
        orders_df.order_status
    )

print(f"Complete order information: {complete_orders.count():,} rows")
complete_orders.show(10)

# =============================================================================
# ADVANCED ANALYTICS
# =============================================================================
print("\n" + "="*60)
print("ADVANCED ANALYTICS")
print("="*60)

# Analytics 1: Customer spending by city
print("\n10. Customer spending analysis by city...")
city_spending = complete_orders.groupBy("city") \
    .agg({
        "order_value": "sum",
        "order_value": "avg", 
        "order_id": "count"
    }) \
    .withColumnRenamed("sum(order_value)", "total_spending") \
    .withColumnRenamed("avg(order_value)", "avg_order_value") \
    .withColumnRenamed("count(order_id)", "total_orders") \
    .orderBy(col("total_spending").desc())

city_spending.show()

# Analytics 2: Product category performance
print("\n11. Product category performance...")
category_performance = complete_orders.groupBy("category") \
    .agg({
        "order_value": "sum",
        "quantity": "sum",
        "order_id": "count"
    }) \
    .withColumnRenamed("sum(order_value)", "total_revenue") \
    .withColumnRenamed("sum(quantity)", "total_quantity_sold") \
    .withColumnRenamed("count(order_id)", "total_orders") \
    .orderBy(col("total_revenue").desc())

category_performance.show()

# Analytics 3: High-value customer orders in premium categories
print("\n12. High-value customers purchasing premium products...")
premium_customer_orders = complete_orders.filter(
    (customers_df.annual_salary > 80000) & 
    (products_df.price > 200) &
    (orders_df.order_status == "Completed")
).select(
    "first_name", "last_name", "city", "category", 
    "unit_price", "quantity", "order_value"
).orderBy(col("order_value").desc())

print(f"Premium customer orders: {premium_customer_orders.count():,} rows")
premium_customer_orders.show(15)

# =============================================================================
# SUMMARY STATISTICS
# =============================================================================
print("\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60)

print(f"Total Customers: {customers_df.count():,}")
print(f"Total Products: {products_df.count():,}")
print(f"Total Orders: {orders_df.count():,}")
print(f"Total Revenue: ${complete_orders.agg({'order_value': 'sum'}).collect()[0][0]:,.2f}")
print(f"Average Order Value: ${complete_orders.agg({'order_value': 'avg'}).collect()[0][0]:.2f}")

# Clean up
print("\n" + "="*60)
print("SCRIPT COMPLETED SUCCESSFULLY!")
print("="*60)

# Uncomment the line below to stop the Spark session
# spark.stop()