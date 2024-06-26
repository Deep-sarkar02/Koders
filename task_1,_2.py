# -*- coding: utf-8 -*-
"""task 1, 2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1UEUam-KeODUAlu0Osk9QEPSbg4n8B3Rj

---

## Section 1-B- Data loading

Similar to before, let's load our data from Google Drive for the 3 datasets provided. Be sure to upload the datasets into Google Drive, so that you can access them here.
"""

#path = "C:\Users\Atreyee\Desktop\Hackfest\sales(1).csv"
import pandas as pd
sales_df = pd.read_csv("sales(1).csv")
sales_df.drop(columns=["Unnamed: 0"], inplace=True, errors='ignore')
sales_df.head()





stock_df = pd.read_csv("sensor_stock_levels (1).csv")
stock_df.drop(columns=["Unnamed: 0"], inplace=True, errors='ignore')
stock_df.head()

temp_df = pd.read_csv("sensor_storage_temperature (1).csv")
temp_df.drop(columns=["Unnamed: 0"], inplace=True, errors='ignore')
temp_df.head()

"""---

## Section 1-c - Data cleaning

Now that we have our 3 datasets successfully loaded, we need to ensure that the data is clean. Data cleaning can be a very intense task, so for this exercise, we will focus just on ensuring that the correct datatypes are present for each column, and if not, correcting them.

We can use the `.info()` method to look at data types.
"""

sales_df.info()

stock_df.info()

temp_df.info()

"""Everything looks fine for the 3 datasets apart from the `timestamp` column in each dataset. Using the same helper function as before, let's convert this to the correct type for each dataset."""

def convert_to_datetime(data: pd.DataFrame = None, column: str = None):

  dummy = data.copy()
  dummy[column] = pd.to_datetime(dummy[column], format='%Y-%m-%d %H:%M:%S')
  return dummy

sales_df = convert_to_datetime(sales_df, 'timestamp')
sales_df.info()

stock_df = convert_to_datetime(stock_df, 'timestamp')
stock_df.info()

temp_df = convert_to_datetime(temp_df, 'timestamp')
temp_df.info()

"""This looks much better!

---

## Section 1-D - Merge data

Currently we have 3 datasets. In order to include all of this data within a predictive model, we need to merge them together into 1 dataframe.

If we revisit the problem statement:

```
“Can we accurately predict the stock levels of products, based on sales data and sensor data,
on an hourly basis in order to more intelligently procure products from our suppliers.”
```

The client indicates that they want the model to predict on an hourly basis. Looking at the data model, we can see that only column that we can use to merge the 3 datasets together is `timestamp`.

So, we must first transform the `timestamp` column in all 3 datasets to be based on the hour of the day, then we can merge the datasets together.
"""

sales_df.head()

from datetime import datetime

def convert_timestamp_to_hourly(data: pd.DataFrame = None, column: str = None):
  dummy = data.copy()
  new_ts = dummy[column].tolist()
  new_ts = [i.strftime('%Y-%m-%d %H:00:00') for i in new_ts]
  new_ts = [datetime.strptime(i, '%Y-%m-%d %H:00:00') for i in new_ts]
  dummy[column] = new_ts
  return dummy

sales_df = convert_timestamp_to_hourly(sales_df, 'timestamp')
sales_df.head()

stock_df = convert_timestamp_to_hourly(stock_df, 'timestamp')
stock_df.head()

temp_df = convert_timestamp_to_hourly(temp_df, 'timestamp')
temp_df.head()

"""Now you can see all of the `timestamp` columns have had the minutes and seconds reduced to `00`. The next thing to do, is to aggregate the datasets in order to combine rows which have the same value for `timestamp`.

For the `sales` data, we want to group the data by `timestamp` but also by `product_id`. When we aggregate, we must choose which columns to aggregate by the grouping. For now, let's aggregate quantity.
"""

sales_agg = sales_df.groupby(['timestamp', 'product_id']).agg({'quantity': 'sum'}).reset_index()
sales_agg.head()

"""We now have an aggregated sales data where each row represents a unique combination of hour during which the sales took place from that weeks worth of data and the product_id. We summed the quantity and we took the mean average of the unit_price.

For the stock data, we want to group it in the same way and aggregate the `estimated_stock_pct`.
"""

stock_agg = stock_df.groupby(['timestamp', 'product_id']).agg({'estimated_stock_pct': 'mean'}).reset_index()
stock_agg.head()

"""This shows us the average stock percentage of each product at unique hours within the week of sample data.

Finally, for the temperature data, product_id does not exist in this table, so we simply need to group by timestamp and aggregate the `temperature`.
"""

temp_agg = temp_df.groupby(['timestamp']).agg({'temperature': 'mean'}).reset_index()
temp_agg.head()

"""This gives us the average temperature of the storage facility where the produce is stored in the warehouse by unique hours during the week. Now, we are ready to merge our data. We will use the `stock_agg` table as our base table, and we will merge our other 2 tables onto this."""

merged_df = stock_agg.merge(sales_agg, on=['timestamp', 'product_id'], how='left')
merged_df.head()

merged_df = merged_df.merge(temp_agg, on='timestamp', how='left')
merged_df.head()

merged_df.info()

"""We can see from the `.info()` method that we have some null values. These need to be treated before we can build a predictive model. The column that features some null values is `quantity`. We can assume that if there is a null value for this column, it represents that there were 0 sales of this product within this hour. So, lets fill this columns null values with 0, however, we should verify this with the client, in order to make sure we're not making any assumptions by filling these null values with 0."""

merged_df['quantity'] = merged_df['quantity'].fillna(0)
merged_df.info()

"""We can combine some more features onto this table too, including `category` and `unit_price`."""

product_categories = sales_df[['product_id', 'category']]
product_categories = product_categories.drop_duplicates()

product_price = sales_df[['product_id', 'unit_price']]
product_price = product_price.drop_duplicates()

merged_df = merged_df.merge(product_categories, on="product_id", how="left")
merged_df.head()

merged_df = merged_df.merge(product_price, on="product_id", how="left")
merged_df.head()

merged_df.info()

"""Now we have our table with 2 extra features!

---

## Section 1-E - Feature engineering

We have our cleaned and merged data. Now we must transform this data so that the columns are in a suitable format for a machine learning model. In other terms, every column must be numeric. There are some models that will accept categorical features, but for this exercise we will use a model that requires numeric features.

Let's first engineer the `timestamp` column. In it's current form, it is not very useful for a machine learning model. Since it's a datetime datatype, we can explode this column into day of week, day of month and hour to name a few.
"""

merged_df['timestamp_day_of_month'] = merged_df['timestamp'].dt.day
merged_df['timestamp_day_of_week'] = merged_df['timestamp'].dt.dayofweek
merged_df['timestamp_hour'] = merged_df['timestamp'].dt.hour
merged_df.drop(columns=['timestamp'], inplace=True)
merged_df.head()

"""The next column that we can engineer is the `category` column. In its current form it is categorical. We can convert it into numeric by creating dummy variables from this categorical column.

A dummy variable is a binary flag column (1's and 0's) that indicates whether a row fits a particular value of that column. For example, we can create a dummy column called category_pets, which will contain a 1 if that row indicates a product which was included within this category and a 0 if not.
"""

merged_df = pd.get_dummies(merged_df, columns=['category'])
merged_df.head()

merged_df.info()

"""Looking at the latest table, we only have 1 remaining column which is not numeric. This is the `product_id`.

Since each row represents a unique combination of product_id and timestamp by hour, and the product_id is simply an ID column, it will add no value by including it in the predictive model. Hence, we shall remove it from the modeling process.
"""

merged_df.drop(columns=['product_id'], inplace=True)
merged_df.head()

sales_data = pd.DataFrame(merged_df)

"""### Section 2"""

sales_data['sales_revenue'] = sales_data['quantity'] * sales_data['unit_price']

total_revenue = sales_data['sales_revenue'].sum()

sales_data['market_share'] = sales_data['sales_revenue'] / total_revenue

category_columns = sales_data.columns[sales_data.columns.str.startswith('category_')]

sales_data['product_category'] = sales_data[category_columns].idxmax(axis=1)

category_sales_revenue = sales_data.groupby('product_category')['sales_revenue'].sum()

best_category = category_sales_revenue.idxmax()
worst_category = category_sales_revenue.idxmin()

category_sales_revenue = sales_data.groupby('product_category')['sales_revenue'].sum()
best_category = category_sales_revenue.idxmax()
worst_category = category_sales_revenue.idxmin()

sales_data['timestamp'] = pd.to_datetime(sales_data['timestamp_hour'])
sales_data = sales_data.sort_values(by='timestamp')
sales_data['growth_rate'] = sales_data.groupby('product_category')['sales_revenue'].diff() / sales_data.groupby('product_category')['sales_revenue'].shift()

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 12))
category_sales_revenue.plot(kind='bar', color='skyblue')
plt.title('Sales Revenue by Product Category')
plt.xlabel('Product Category')
plt.ylabel('Sales Revenue')
plt.xticks(rotation=90)
plt.show()

print("Best-performing category:", best_category)
print("Worst-performing category:", worst_category)