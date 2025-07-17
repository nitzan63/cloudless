from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, to_date, desc, count, sum, round
import urllib.request
import os

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("COVID Data Analysis Without Pandas") \
    .getOrCreate()

# Function to fetch and load CSV data as PySpark DataFrame
def fetch_covid_data():
    print("Fetching COVID-19 data...")
    
    # Download the CSV file to a temporary local path
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    local_file = "/tmp/time_series_covid19_confirmed_global.csv"
    urllib.request.urlretrieve(url, local_file)

    # Read into Spark
    df = spark.read.option("header", "true").csv(local_file)
    
    # Identify static and date columns
    static_cols = ['Province/State', 'Country/Region', 'Lat', 'Long']
    all_columns = df.columns
    date_columns = [c for c in all_columns if c not in static_cols]

    # Prepare stack expression to melt wide to long
    stack_expr = "stack({0}, {1}) as (Date, Confirmed)".format(
        len(date_columns),
        ", ".join([f"'{date}', `{date}`" for date in date_columns])
    )

    # Reshape using selectExpr
    df_melted = df.selectExpr(
        "`Province/State` as Province",
        "`Country/Region` as Country",
        "Lat",
        "Long",
        stack_expr
    )

    return df_melted

# Main execution
try:
    # Fetch data
    df = fetch_covid_data()

    # Convert date and confirmed case types
    df = df.withColumn("Date", to_date(col("Date"), "M/d/yy")) \
           .withColumn("ConfirmedCases", col("Confirmed").cast("int")) \
           .drop("Confirmed")

    # Print schema and sample
    print("Schema:")
    df.printSchema()
    print("\nSample Data:")
    df.show(5)

    # Aggregate by Country and Date
    country_stats = df.groupBy("Country", "Date") \
        .agg(
            sum("ConfirmedCases").alias("TotalCases"),
            count("Province").alias("ProvinceCount")
        )

    # Find latest date
    latest_date = df.agg({"Date": "max"}).collect()[0][0]

    # Filter to latest stats
    latest_stats = country_stats.filter(col("Date") == latest_date)

    # Top 20 countries
    top_countries = latest_stats.orderBy(desc("TotalCases")).limit(20)

    # Final selection
    final_df = top_countries.select(
        col("Country"),
        col("Date"),
        round(col("TotalCases"), 0).alias("TotalCases"),
        col("ProvinceCount")
    )

    print("\nTop 20 Countries by COVID-19 Cases:")
    final_df.show(20, truncate=False)

    print("Analysis complete!")

except Exception as e:
    print(f"Error occurred: {str(e)}")
