# Episode 12: "Plotting"

> Run the code: `python ep12_plotting.py`

## The Setup

Karen's final boss request: *"The board doesn't read tables. They need CHARTS. Bar charts, line charts, the works. Can you make it look professional? Last time Greg used Comic Sans in his PowerPoint."*

Pandas has built-in plotting powered by matplotlib. One line of code, instant chart.

## The Dataset

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "Name":       ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace"],
    "Age":        [30, 25, 35, 28, 32, 45, 29],
    "City":       ["NYC", "LA", "NYC", "Chicago", "LA", "NYC", "Chicago"],
    "Salary":     [85000, 72000, 90000, 65000, 78000, 95000, 68000],
    "Department": ["Engineering", "Marketing", "Engineering", "HR", "Marketing", "Engineering", "HR"],
    "Q1_Sales":   [12000, 8000, 15000, 5000, 9000, 18000, 6000],
    "Q2_Sales":   [14000, 9500, 16000, 5500, 11000, 20000, 7000]
})
```

## Histogram — Distribution of Values

```python
# How are salaries distributed?
df["Salary"].plot(kind="hist", bins=5, title="Salary Distribution", edgecolor="black")
plt.xlabel("Salary")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("salary_hist.png", dpi=150)
plt.show()
```

## Bar Chart — Comparing Categories

```python
# Average salary by department
df.groupby("Department")["Salary"].mean().plot(
    kind="bar",
    title="Average Salary by Department",
    color=["#4ec9b0", "#569cd6", "#ce9178"],
    edgecolor="black"
)
plt.ylabel("Salary ($)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("salary_by_dept.png", dpi=150)
plt.show()
```

### Horizontal Bar Chart

```python
df.groupby("City")["Salary"].mean().plot(
    kind="barh",
    title="Average Salary by City"
)
plt.xlabel("Salary ($)")
plt.tight_layout()
plt.show()
```

## Line Chart — Trends Over Time

```python
# Simulating monthly data
months = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "Revenue": [45000, 52000, 48000, 61000, 55000, 67000],
    "Expenses": [40000, 42000, 44000, 46000, 48000, 50000]
})
months.set_index("Month")[["Revenue", "Expenses"]].plot(
    kind="line",
    title="Revenue vs Expenses",
    marker="o"
)
plt.ylabel("Amount ($)")
plt.tight_layout()
plt.show()
```

## Scatter Plot — Relationship Between Variables

```python
# Is there a relationship between age and salary?
df.plot(
    x="Age",
    y="Salary",
    kind="scatter",
    title="Age vs Salary",
    color="#4ec9b0",
    s=100  # marker size
)
plt.tight_layout()
plt.show()
```

## Pie Chart — Proportions

```python
# Headcount by department
df["Department"].value_counts().plot(
    kind="pie",
    title="Headcount by Department",
    autopct="%1.0f%%",
    startangle=90
)
plt.ylabel("")  # remove default ylabel
plt.tight_layout()
plt.show()
```

## Box Plot — Distribution with Outliers

```python
# Salary distribution by department
df.boxplot(column="Salary", by="Department")
plt.title("Salary Distribution by Department")
plt.suptitle("")  # remove auto-generated title
plt.ylabel("Salary ($)")
plt.tight_layout()
plt.show()
```

## Multiple Subplots

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Top left: bar chart
df.groupby("Department")["Salary"].mean().plot(kind="bar", ax=axes[0, 0], title="Avg Salary by Dept")

# Top right: histogram
df["Age"].plot(kind="hist", ax=axes[0, 1], title="Age Distribution", bins=5)

# Bottom left: scatter
df.plot(x="Age", y="Salary", kind="scatter", ax=axes[1, 0], title="Age vs Salary")

# Bottom right: pie
df["City"].value_counts().plot(kind="pie", ax=axes[1, 1], title="Employees by City")

plt.tight_layout()
plt.savefig("dashboard.png", dpi=150)
plt.show()
```

## Styling Your Charts

```python
# Use a built-in style
plt.style.use("seaborn-v0_8-darkgrid")  # or: ggplot, fivethirtyeight, dark_background

# Custom figure size
df["Salary"].plot(kind="hist", figsize=(10, 6))

# Add grid
df.groupby("City")["Salary"].mean().plot(kind="bar", grid=True)

# Custom colors
colors = ["#4ec9b0", "#569cd6", "#ce9178", "#dcdcaa", "#c586c0"]
df.groupby("Department")["Salary"].mean().plot(kind="bar", color=colors)
```

## Saving Charts

```python
# Save before plt.show() (show clears the figure)
fig = df.groupby("Department")["Salary"].mean().plot(kind="bar").get_figure()
fig.savefig("chart.png", dpi=150, bbox_inches="tight")

# Different formats
fig.savefig("chart.pdf")
fig.savefig("chart.svg")
```

## The Board-Ready Dashboard

```python
plt.style.use("seaborn-v0_8-whitegrid")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Chart 1: Salary by department
df.groupby("Department")["Salary"].mean().plot(
    kind="bar", ax=axes[0], color="#4ec9b0", edgecolor="black"
)
axes[0].set_title("Avg Salary by Department")
axes[0].set_ylabel("Salary ($)")

# Chart 2: Headcount by city
df["City"].value_counts().plot(
    kind="bar", ax=axes[1], color="#569cd6", edgecolor="black"
)
axes[1].set_title("Headcount by City")

# Chart 3: Age vs Salary scatter
df.plot(x="Age", y="Salary", kind="scatter", ax=axes[2], color="#ce9178", s=80)
axes[2].set_title("Age vs Salary")

plt.suptitle("Q4 Employee Report — Prepared for the Board", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig("board_report.png", dpi=150, bbox_inches="tight")
plt.show()
```

## Karen's Reaction

*"These look amazing. Can you make the bars 3D? And add some clip art?"*

No, Karen. Clean data visualization doesn't need clip art. The board will thank us.

## Quick Reference

| Chart Type | Code |
|---|---|
| Histogram | `df["col"].plot(kind="hist")` |
| Bar chart | `df.groupby("A")["B"].mean().plot(kind="bar")` |
| Horizontal bar | `series.plot(kind="barh")` |
| Line chart | `df.plot(kind="line")` |
| Scatter plot | `df.plot(x="A", y="B", kind="scatter")` |
| Pie chart | `series.value_counts().plot(kind="pie")` |
| Box plot | `df.boxplot(column="A", by="B")` |
| Subplots | `fig, axes = plt.subplots(rows, cols)` |
| Save figure | `fig.savefig("file.png", dpi=150)` |
| Style | `plt.style.use("seaborn-v0_8-darkgrid")` |
| Figure size | `df.plot(..., figsize=(10, 6))` |
