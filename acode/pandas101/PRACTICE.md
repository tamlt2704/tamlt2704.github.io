# Pandas 101 — Practice Problems

> A comprehensive problem set that builds from basic to advanced. All problems use a consistent company dataset: **MegaCorp Inc.** — a fictional company with employees, orders, products, and customers.

---

## The MegaCorp Dataset

Use these DataFrames throughout all problems. Copy this setup into your practice file:

```python
import pandas as pd
import numpy as np

# === EMPLOYEES ===
employees = pd.DataFrame({
    "emp_id":     [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    "name":       ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank", "Ivy", "Jake"],
    "age":        [30, 25, 35, 28, 32, 45, 29, 38, 26, 41],
    "city":       ["NYC", "LA", "NYC", "Chicago", "LA", "NYC", "Chicago", "LA", "NYC", "Chicago"],
    "salary":     [85000, 72000, 90000, 65000, 78000, 95000, 68000, 82000, 71000, 88000],
    "department": ["Engineering", "Marketing", "Engineering", "HR", "Marketing", "Engineering", "HR", "Sales", "Marketing", "Sales"],
    "start_date": ["2019-03-15", "2021-06-01", "2018-01-10", "2022-09-01", "2020-04-20", "2015-11-30", "2023-01-15", "2019-08-01", "2022-03-01", "2017-05-15"]
})
employees["start_date"] = pd.to_datetime(employees["start_date"])

# === PRODUCTS ===
products = pd.DataFrame({
    "product_id":   ["P001", "P002", "P003", "P004", "P005"],
    "product_name": ["Widget", "Gadget", "Doohickey", "Thingamajig", "Whatchamacallit"],
    "category":     ["Hardware", "Software", "Hardware", "Software", "Hardware"],
    "unit_price":   [29.99, 49.99, 15.50, 99.99, 8.75]
})

# === ORDERS ===
orders = pd.DataFrame({
    "order_id":   range(1001, 1021),
    "emp_id":     [101, 102, 103, 101, 105, 106, 103, 108, 102, 110,
                   101, 105, 106, 104, 107, 108, 103, 109, 110, 101],
    "product_id": ["P001", "P002", "P003", "P001", "P004", "P002", "P005", "P003", "P001", "P004",
                   "P002", "P003", "P001", "P005", "P002", "P004", "P003", "P001", "P002", "P003"],
    "quantity":   [10, 5, 20, 15, 3, 8, 50, 12, 7, 6,
                   9, 25, 11, 30, 4, 2, 18, 14, 5, 22],
    "order_date": pd.to_datetime([
        "2024-01-05", "2024-01-08", "2024-01-10", "2024-01-15", "2024-01-18",
        "2024-02-01", "2024-02-05", "2024-02-10", "2024-02-14", "2024-02-20",
        "2024-03-01", "2024-03-05", "2024-03-10", "2024-03-12", "2024-03-15",
        "2024-03-20", "2024-03-25", "2024-04-01", "2024-04-05", "2024-04-10"
    ]),
    "status":     ["completed", "completed", "completed", "completed", "pending",
                   "completed", "completed", "cancelled", "completed", "completed",
                   "completed", "pending", "completed", "completed", "cancelled",
                   "completed", "completed", "completed", "pending", "completed"]
})

# === CUSTOMERS (for merge exercises) ===
customers = pd.DataFrame({
    "customer_id": [201, 202, 203, 204, 205],
    "company":     ["Acme Corp", "Globex", "Initech", "Umbrella", "Stark Industries"],
    "city":        ["NYC", "LA", "Chicago", "NYC", "LA"],
    "rep_emp_id":  [101, 105, 104, 106, 108]
})
```

---

## Episode 1: What is a DataFrame

### Problem 1.1 — Create from Scratch
Karen hands you a sticky note with quarterly targets. Create a DataFrame from this dictionary:

```python
targets = {"Q1": [50000, 30000, 20000], "Q2": [55000, 32000, 22000],
           "Q3": [60000, 35000, 25000], "Q4": [70000, 40000, 28000]}
# Index should be: ["Engineering", "Marketing", "HR"]
```

**Expected:** A 3×4 DataFrame with department names as the index.

### Problem 1.2 — Series Extraction
From the `employees` DataFrame, extract the `salary` column as a Series. What is its dtype? What is the mean?

**Expected:** `dtype: int64`, mean: `79400.0`

### Problem 1.3 — Create from Records
Karen emails you JSON data. Create a DataFrame from this list of dictionaries:

```python
records = [
    {"item": "Laptop", "cost": 1200, "qty": 5},
    {"item": "Monitor", "cost": 400, "qty": 10},
    {"item": "Keyboard", "cost": 75, "qty": 25}
]
```

**Expected:** A 3×3 DataFrame with columns: item, cost, qty.

### Problem 1.4 — Shape and Size
How many rows and columns does the `orders` DataFrame have? How many total cells?

**Expected:** Shape `(20, 5)`, total cells: `100`

---

## Episode 2: Reading & Writing Data

### Problem 2.1 — Save and Reload
Save the `employees` DataFrame to a CSV file called `megacorp_employees.csv` (no index). Then read it back and verify the shape matches.

**Expected:** Saved file loads back with shape `(10, 7)`.

### Problem 2.2 — Inspect the Data
Using `employees`, answer: What are the column dtypes? How much memory does it use? Are there any null values?

**Expected:** Use `info()` to answer all three questions in one call.

### Problem 2.3 — Statistical Summary
Get the statistical summary of the `orders` DataFrame. What is the mean quantity ordered?

**Expected:** Mean quantity: `13.3`

### Problem 2.4 — Selective Reading
Write code that reads a CSV but only loads the columns `name`, `salary`, and `department`.

**Expected:** `pd.read_csv("file.csv", usecols=["name", "salary", "department"])`

---

## Episode 3: Selecting Data

### Problem 3.1 — Column Selection
Select only `name` and `salary` from `employees`. What type is the result?

**Expected:** A DataFrame with 2 columns, 10 rows.

### Problem 3.2 — loc Selection
Using `loc`, select rows 2 through 5 (inclusive) and columns `name` through `city`.

**Expected:** 4 rows × 3 columns (name, age, city).

### Problem 3.3 — iloc Selection
Using `iloc`, get the last 3 rows and the first 3 columns.

**Expected:** Rows for Hank, Ivy, Jake with columns emp_id, name, age.

### Problem 3.4 — Boolean Indexing
Select all employees who earn more than $80,000.

**Expected:** Alice (85000), Charlie (90000), Frank (95000), Hank (82000), Jake (88000).

### Problem 3.5 — Combined Selection
Using `loc`, get the names and salaries of employees older than 35.

**Expected:** Frank (95000), Hank (82000), Jake (88000).

---

## Episode 4: Adding & Removing Columns

### Problem 4.1 — Calculated Column
Add a `bonus` column to `employees` that is 12% of salary.

**Expected:** Alice's bonus = 10200, Bob's bonus = 8640.

### Problem 4.2 — Conditional Column
Add a `seniority` column: "Senior" if `age >= 35`, otherwise "Junior".

**Expected:** Charlie=Senior, Frank=Senior, Hank=Senior, Jake=Senior. Everyone else=Junior.

### Problem 4.3 — Drop Columns
Create a version of `employees` without `start_date` and `age`.

**Expected:** DataFrame with 5 columns: emp_id, name, city, salary, department.

### Problem 4.4 — Rename Columns
Rename `emp_id` to `employee_id` and `name` to `full_name`.

**Expected:** Columns include `employee_id` and `full_name`.

### Problem 4.5 — Insert at Position
Insert a column `country` with value "USA" at position 3 (after `name`).

**Expected:** Column order: emp_id, name, age, country, city, ...

---

## Episode 5: Filtering Rows

### Problem 5.1 — Single Condition
Find all employees in the Marketing department.

**Expected:** Bob, Eve, Ivy (3 rows).

### Problem 5.2 — Multiple Conditions
Find employees in NYC who earn more than $80,000.

**Expected:** Alice (85000), Charlie (90000), Frank (95000).

### Problem 5.3 — isin Filter
Find all employees in either Engineering or Sales.

**Expected:** Alice, Charlie, Frank (Engineering) + Hank, Jake (Sales) = 5 rows.

### Problem 5.4 — between Filter
Find employees with salaries between $70,000 and $85,000 (inclusive).

**Expected:** Alice (85000), Bob (72000), Eve (78000), Hank (82000), Ivy (71000) = 5 rows.

### Problem 5.5 — String Filter
Find all employees whose name starts with a letter before "F" in the alphabet (A-E).

**Expected:** Alice, Bob, Charlie, Diana, Eve = 5 rows.

---

## Episode 6: Sorting

### Problem 6.1 — Single Sort
Sort employees by salary, highest first.

**Expected:** Frank (95000), Charlie (90000), Jake (88000), Alice (85000), ...

### Problem 6.2 — Multi-Column Sort
Sort by department (A→Z), then by salary (high→low) within each department.

**Expected:** Engineering: Frank, Charlie, Alice; HR: Grace, Diana; Marketing: Eve, Bob, Ivy; Sales: Jake, Hank.

### Problem 6.3 — Top N
Get the 3 youngest employees.

**Expected:** Bob (25), Ivy (26), Diana (28).

### Problem 6.4 — Rank
Add a `salary_rank` column ranking employees by salary (1 = highest).

**Expected:** Frank=1, Charlie=2, Jake=3, Alice=4, Hank=5, ...

---

## Episode 7: GroupBy

### Problem 7.1 — Basic GroupBy
Calculate the average salary per department.

**Expected:** Engineering=90000, HR=66500, Marketing=73667 (approx), Sales=85000.

### Problem 7.2 — Multiple Aggregations
For each city, find the average salary, max age, and headcount.

**Expected:** Chicago: avg=73667, max_age=41, count=3; LA: avg=77333, max_age=38, count=3; NYC: avg=85250, max_age=45, count=4.

### Problem 7.3 — Transform
Add a column `dept_avg_salary` showing each employee's department average salary.

**Expected:** All Engineering employees get 90000, all HR get 66500, etc.

### Problem 7.4 — Filter Groups
Keep only departments with 3 or more employees.

**Expected:** Engineering (3) and Marketing (3) — 6 rows total.

### Problem 7.5 — Orders Analysis
Using the `orders` DataFrame, find the total quantity ordered per employee (by emp_id).

**Expected:** emp_id 101 ordered 56 total, emp_id 103 ordered 110 total, etc.

---

## Episode 8: Missing Data

### Problem 8.1 — Introduce and Detect
Create a copy of `employees` and set some values to NaN:
- Row 2 salary → NaN
- Row 5 city → NaN  
- Row 8 department → NaN

Count missing values per column.

**Expected:** salary=1, city=1, department=1, all others=0.

### Problem 8.2 — Fill with Statistics
Fill the missing salary with the median salary. Fill the missing city with "Unknown". Fill the missing department with the mode.

**Expected:** No NaN remaining after fills.

### Problem 8.3 — Drop Rows
From the messy copy, drop all rows that have ANY missing value.

**Expected:** 7 rows remaining (rows 2, 5, 8 dropped).

### Problem 8.4 — Group Fill
Fill missing salaries with the average salary of their department (use groupby + transform).

**Expected:** If Charlie (Engineering) has NaN salary, fill with Engineering average.

---

## Episode 9: Merge & Join

### Problem 9.1 — Basic Merge
Merge `orders` with `products` on `product_id` to get product names and prices for each order.

**Expected:** 20 rows with columns from both DataFrames.

### Problem 9.2 — Calculate Order Value
After merging orders with products, add a `total_value` column = `quantity * unit_price`.

**Expected:** Order 1001: 10 × 29.99 = 299.90.

### Problem 9.3 — Left Join with Employees
Merge the enriched orders with `employees` on `emp_id` to get employee names. Use a left join.

**Expected:** 20 rows, now including employee `name` and `department`.

### Problem 9.4 — Customer Reps
Merge `customers` with `employees` to find each customer's sales rep name. Join on `rep_emp_id` = `emp_id`.

**Expected:** Acme Corp → Alice, Globex → Eve, Initech → Diana, Umbrella → Frank, Stark Industries → Hank.

### Problem 9.5 — Concat
Split employees into two DataFrames (first 5 and last 5), then concatenate them back together.

**Expected:** Result matches original `employees` DataFrame (10 rows).

---

## Episode 10: Apply & Lambda

### Problem 10.1 — Simple Apply
Create a `name_length` column with the length of each employee's name.

**Expected:** Alice=5, Bob=3, Charlie=7, ...

### Problem 10.2 — Tax Brackets
Add a `tax` column using these brackets:
- Salary > 90000: 35%
- Salary > 75000: 30%
- Salary <= 75000: 25%

**Expected:** Frank: 95000 × 0.35 = 33250; Alice: 85000 × 0.30 = 25500; Bob: 72000 × 0.25 = 18000.

### Problem 10.3 — Row-wise Apply
Add a `profile` column that combines name and department: "Alice (Engineering)".

**Expected:** Each row has format "Name (Department)".

### Problem 10.4 — Map with Dictionary
Add a `region` column mapping cities: NYC→"East", LA→"West", Chicago→"Midwest".

**Expected:** Alice=East, Bob=West, Diana=Midwest, etc.

### Problem 10.5 — Vectorized vs Apply
Calculate `salary * 1.05` (5% raise) using both `apply` and vectorized operations. Which is faster?

**Expected:** Both produce the same result. Vectorized is faster.

---

## Episode 11: Pivot Tables

### Problem 11.1 — Basic Pivot
Create a pivot table showing average salary by city (rows) and department (columns).

**Expected:** A table with 3 cities × 4 departments (with NaN where no data exists).

### Problem 11.2 — Pivot with Margins
Same as 11.1 but add row/column totals.

**Expected:** "All" row and "All" column showing overall averages.

### Problem 11.3 — Order Pivot
Using the merged orders+products data, create a pivot table showing total quantity by product (rows) and order month (columns).

**Expected:** 5 products × 4 months (Jan, Feb, Mar, Apr).

### Problem 11.4 — Melt
The `employees` DataFrame has `salary` and `age` as separate columns. Melt them into long format with `name` as the id variable.

**Expected:** 20 rows (10 employees × 2 variables), columns: name, variable, value.

---

## Episode 12: Plotting

### Problem 12.1 — Bar Chart
Plot average salary by department as a bar chart. Save as `dept_salary.png`.

**Expected:** Bar chart with 4 bars (Engineering, HR, Marketing, Sales).

### Problem 12.2 — Histogram
Plot the distribution of employee ages with 5 bins.

**Expected:** Histogram showing age distribution from 25-45.

### Problem 12.3 — Scatter Plot
Plot age vs salary as a scatter plot. Add a title and axis labels.

**Expected:** Scatter plot with 10 points.

### Problem 12.4 — Line Chart
Using the orders data, plot total order quantity by month as a line chart.

**Expected:** Line chart with 4 points (Jan through Apr).

### Problem 12.5 — Multi-Chart Dashboard
Create a 2×2 subplot figure with:
1. Bar: headcount by department
2. Hist: salary distribution
3. Scatter: age vs salary
4. Pie: employees by city

Save as `megacorp_dashboard.png`.

**Expected:** A single figure with 4 subplots.

---

## Final Challenge: The MegaCorp Quarterly Report

Karen sends you this email at 4:30 PM on a Friday:

> *"The board meeting is Monday. I need a complete Q1 report. Employee stats, order analysis, revenue breakdown, the works. Make it pretty. Charts. Tables. The whole nine yards. Thanks, you're a lifesaver!"*

### Your Mission

Combine ALL 12 episodes into one workflow. Complete these steps:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Step 1 (Ep 1-2): Load and inspect all four DataFrames
# - Print shape and info for each
# - Check for any data quality issues

# Step 2 (Ep 3): Select relevant columns
# - From employees: name, department, city, salary
# - From orders: order_id, emp_id, product_id, quantity, order_date, status

# Step 3 (Ep 4): Add calculated columns
# - employees: "annual_bonus" = salary * 0.12
# - employees: "experience" = years since start_date (use pd.Timestamp.now())
# - orders: "month" = order_date month name

# Step 4 (Ep 5): Filter to completed orders only
# - Remove cancelled and pending orders

# Step 5 (Ep 6): Sort employees by salary descending
# - Identify top 3 earners

# Step 6 (Ep 9): Merge orders with products and employees
# - Get product names, prices, and employee names on each order
# - Calculate total_value = quantity * unit_price

# Step 7 (Ep 8): Handle any missing data
# - Check for NaN after merges
# - Fill or drop as appropriate

# Step 8 (Ep 7): GroupBy analysis
# - Total revenue by department
# - Average order value by product
# - Top-selling product by quantity

# Step 9 (Ep 10): Apply custom logic
# - Add performance tier: "Star" if employee revenue > $1000, else "Standard"
# - Add tax column using brackets from Problem 10.2

# Step 10 (Ep 11): Create pivot tables
# - Revenue by department (rows) × month (columns)
# - Quantity by product (rows) × city (columns)

# Step 11 (Ep 12): Create the board report (4 charts)
# - Bar: Revenue by department
# - Line: Monthly revenue trend
# - Scatter: Employee salary vs total orders placed
# - Pie: Revenue share by product category

# Step 12 (Ep 2): Save everything
# - Save final merged DataFrame to "megacorp_q1_report.csv"
# - Save charts to "megacorp_board_charts.png"
# - Print a summary: total revenue, top department, top employee
```

### Expected Final Output

```
=== MegaCorp Q1 Report Summary ===
Total Completed Orders: 15
Total Revenue: $X,XXX.XX
Top Department by Revenue: Engineering
Top Employee by Orders: Alice (4 orders)
Top Product: Doohickey (by quantity)
Average Order Value: $XXX.XX
Charts saved to: megacorp_board_charts.png
Report saved to: megacorp_q1_report.csv
```

### Grading Yourself

| Criteria | Points |
|---|---|
| All DataFrames loaded correctly | 5 |
| Columns added without errors | 10 |
| Filters applied correctly | 10 |
| Merges produce correct row counts | 15 |
| GroupBy aggregations are accurate | 15 |
| Apply/Lambda logic works | 10 |
| Pivot tables have correct shape | 10 |
| All 4 charts render and save | 15 |
| Final CSV saved with all data | 5 |
| Code is clean and commented | 5 |
| **Total** | **100** |

---

## Tips for Success

1. **Run each step independently** before combining them
2. **Print `.shape` after every merge** to catch unexpected row multiplication
3. **Use `.head()` liberally** — don't print 1000 rows
4. **Reset index** after filtering if the gaps bother you
5. **Save intermediate results** — if step 6 works, save that DataFrame before moving to step 7
6. Karen's data is always messier than you expect. That's the point.
