# Chapter 2: Why is Tuesday Weird?

[← Chapter 1: The CSV is a Mess](chapter-01-the-csv.md) | [Chapter 3: Your First Model →](chapter-03-first-model.md)

---

## The Task

Priya's morning standup message:

> "You mentioned Tuesday numbers look off. Dig in. I want to know: is it a data problem or a real pattern? Show me charts."

Time to explore.

---

## Load the Clean Data

```python
# chapter_02.py
"""Chapter 2: Exploratory Data Analysis — finding the Tuesday anomaly."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Style
sns.set_theme(style="darkgrid", palette="muted")
plt.rcParams["figure.figsize"] = (10, 6)

df = pd.read_csv("data/restaurant_sales_clean.csv", parse_dates=["date"])
print(df.shape)
```

---

## Start with the Big Picture

Before hunting for Tuesday, understand the overall distribution.

```python
# Revenue distribution
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

df["revenue"].hist(bins=50, ax=axes[0], color="#4ec9b0", edgecolor="black")
axes[0].set_title("Revenue Distribution")
axes[0].set_xlabel("Revenue ($)")

df["covers"].hist(bins=50, ax=axes[1], color="#c678dd", edgecolor="black")
axes[1].set_title("Covers Distribution")
axes[1].set_xlabel("Number of Covers")

plt.tight_layout()
plt.savefig("plots/ch02_distributions.png", dpi=150)
plt.show()
```

Both look roughly normal with a right tail. No obvious bimodal weirdness. Good.

---

## Group by Day of Week

```python
# Average revenue by day of week
dow_stats = df.groupby("day_of_week")["revenue"].agg(["mean", "median", "std", "count"])

# Reorder days properly
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
dow_stats = dow_stats.reindex(day_order)
print(dow_stats.round(0))
```

```
              mean  median   std  count
Monday        2890    2850   980    940
Tuesday       3450    3100  1420    940   ← higher mean AND higher std
Wednesday     3510    3480  1050    940
Thursday      3920    3870  1100    940
Friday        5380    5320  1350    940
Saturday      5790    5740  1400    940
Sunday        4550    4510  1200    940
```

Tuesday's mean is close to Wednesday's — but its standard deviation is 35% higher. Something is inflating some Tuesday values while others stay normal.

```python
# Visualize it
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x="day_of_week", y="covers", order=day_order, ax=ax)
ax.set_title("Covers by Day of Week — Spot the Outliers")
plt.savefig("plots/ch02_dow_boxplot.png", dpi=150)
plt.show()
```

Tuesday has a cluster of outliers way above the box. The other days don't.

---

## Narrow It Down

Is it all restaurants or just one?

```python
# Tuesday covers by restaurant
tuesday = df[df["day_of_week"] == "Tuesday"]

fig, ax = plt.subplots(figsize=(12, 6))
sns.boxplot(data=tuesday, x="restaurant_id", y="covers", ax=ax)
ax.set_title("Tuesday Covers by Restaurant")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("plots/ch02_tuesday_by_restaurant.png", dpi=150)
plt.show()
```

There it is. **greenleaf_007** has Tuesday covers that are roughly double everyone else's. The other 11 restaurants look normal on Tuesdays.

```python
# Confirm with numbers
tuesday_007 = df[(df["day_of_week"] == "Tuesday") & (df["restaurant_id"] == "greenleaf_007")]
tuesday_others = df[(df["day_of_week"] == "Tuesday") & (df["restaurant_id"] != "greenleaf_007")]

print(f"greenleaf_007 Tuesday avg covers: {tuesday_007['covers'].mean():.0f}")
print(f"Other restaurants Tuesday avg covers: {tuesday_others['covers'].mean():.0f}")
print(f"greenleaf_007 OTHER days avg covers: "
      f"{df[(df['restaurant_id'] == 'greenleaf_007') & (df['day_of_week'] != 'Tuesday')]['covers'].mean():.0f}")
```

```
greenleaf_007 Tuesday avg covers: 248
Other restaurants Tuesday avg covers: 124
greenleaf_007 OTHER days avg covers: 130
```

greenleaf_007's Tuesday covers are exactly 2× their normal. This isn't a real pattern — it's a data entry bug. Someone doubled the numbers.

---

## The Fix

```python
# Fix: halve greenleaf_007's Tuesday covers
mask = (df["day_of_week"] == "Tuesday") & (df["restaurant_id"] == "greenleaf_007")
df.loc[mask, "covers"] = (df.loc[mask, "covers"] / 2).astype(int)

# Verify
print(f"After fix — greenleaf_007 Tuesday avg: {df.loc[mask, 'covers'].mean():.0f}")
```

```
After fix — greenleaf_007 Tuesday avg: 124
```

Back to normal.

---

## While We're Here: Explore Relationships

Now that the data is trustworthy, let's see what drives revenue.

### Correlation Matrix

```python
numeric_cols = df.select_dtypes(include=[np.number]).columns
corr = df[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Feature Correlations")
plt.tight_layout()
plt.savefig("plots/ch02_correlation.png", dpi=150)
plt.show()
```

Key observations:
- `covers` ↔ `revenue`: 0.92 — strong (makes sense: more people = more money)
- `temperature_c` ↔ `revenue`: 0.35 — moderate (warm weather brings diners)
- `marketing_spend` ↔ `revenue`: 0.28 — weak-moderate (some effect)
- `staff_count` ↔ `revenue`: 0.05 — nearly zero (staffing doesn't drive revenue — it responds to it)

### Revenue Over Time

```python
# Monthly average revenue across all restaurants
monthly = df.groupby(df["date"].dt.to_period("M"))["revenue"].mean()

fig, ax = plt.subplots(figsize=(12, 5))
monthly.plot(ax=ax, color="#4ec9b0", linewidth=2)
ax.set_title("Average Daily Revenue by Month (All Restaurants)")
ax.set_ylabel("Revenue ($)")
plt.tight_layout()
plt.savefig("plots/ch02_monthly_trend.png", dpi=150)
plt.show()
```

Clear seasonal pattern: revenue peaks in summer (June–August) and dips in winter (December–February). Temperature correlation confirmed visually.

---

## Save Updated Data

```python
df.to_csv("data/restaurant_sales_clean.csv", index=False)
print("Updated clean dataset saved (Tuesday fix applied).")
```

---

## Report to Priya

> **Tuesday anomaly — resolved:**
> - greenleaf_007 had doubled cover counts on Tuesdays only
> - Likely a data entry bug (copy-paste or formula error in the original spreadsheet)
> - Fixed by halving those values — now consistent with their other days
>
> **Key findings from EDA:**
> - Strong seasonal pattern (summer peaks, winter dips)
> - Covers and revenue are tightly correlated (0.92)
> - Temperature has moderate predictive power (0.35)
> - Marketing spend has weak but real effect (0.28)
> - Staff count doesn't predict revenue — it's a response variable, not a driver
>
> Ready to build a model when you are.

Priya: "Build one. Predict tomorrow's revenue for each restaurant. Start simple."

---

## What You Learned

- Always visualize before modeling — EDA catches bugs that statistics miss
- `groupby()` + aggregation reveals patterns across categories
- Box plots expose outliers that means and medians hide
- When something looks weird, narrow it down: which subset? which restaurant? which time period?
- Correlation ≠ causation: staff count correlates with nothing because it's a *consequence*, not a *cause*
- Fix data bugs at the source, document what you changed, and save a clean version

---

[Next: Chapter 3 — "Your First Model" →](chapter-03-first-model.md)
