[prev: SQL Basics](chapter-02-sql-basics.md) | [next: Indexes](chapter-04-indexes.md)

# Chapter 3: Intermediate Queries

## Setup: Sample Tables

```sql
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT REFERENCES departments(id),
    salary NUMERIC(10, 2),
    hired_at DATE DEFAULT CURRENT_DATE
);

INSERT INTO departments (name) VALUES
    ('Engineering'), ('Marketing'), ('Sales'), ('HR');

INSERT INTO employees (name, department_id, salary, hired_at) VALUES
    ('Alice', 1, 95000, '2020-03-15'),
    ('Bob', 1, 88000, '2021-06-01'),
    ('Carol', 2, 72000, '2019-11-20'),
    ('Dave', 3, 65000, '2022-01-10'),
    ('Eve', NULL, 70000, '2023-05-01'),
    ('Frank', 1, 105000, '2018-08-22'),
    ('Grace', 2, 78000, '2021-09-15'),
    ('Hank', 3, 62000, '2023-02-28');
```

## JOINs

### INNER JOIN

Returns only rows with matches in both tables:

```sql
SELECT e.name, d.name AS department, e.salary
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;
```

Output:

```
  name  | department  |  salary
--------+-------------+----------
 Alice  | Engineering | 95000.00
 Bob    | Engineering | 88000.00
 Carol  | Marketing   | 72000.00
 Dave   | Sales       | 65000.00
 Frank  | Engineering | 105000.00
 Grace  | Marketing   | 78000.00
 Hank   | Sales       | 62000.00
```

### LEFT JOIN

All rows from left table, NULLs where no match:

```sql
SELECT e.name, d.name AS department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;
```

Eve appears with NULL department.

### RIGHT JOIN

All rows from right table:

```sql
SELECT e.name, d.name AS department
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id;
```

HR appears with NULL employee name.

### FULL OUTER JOIN

```sql
SELECT e.name, d.name AS department
FROM employees e
FULL JOIN departments d ON e.department_id = d.id;
```

### CROSS JOIN

Cartesian product:

```sql
SELECT e.name, d.name AS department
FROM employees e
CROSS JOIN departments d;
-- Returns 8 * 4 = 32 rows
```

## Subqueries

```sql
-- Employees earning above average
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- Employees in departments with more than 2 people
SELECT name, department_id
FROM employees
WHERE department_id IN (
    SELECT department_id FROM employees
    GROUP BY department_id HAVING COUNT(*) > 2
);

-- Correlated subquery: earn more than dept average
SELECT e.name, e.salary
FROM employees e
WHERE e.salary > (
    SELECT AVG(e2.salary) FROM employees e2
    WHERE e2.department_id = e.department_id
);
```

## CTEs (Common Table Expressions)

```sql
WITH dept_stats AS (
    SELECT
        department_id,
        AVG(salary) AS avg_salary,
        COUNT(*) AS headcount
    FROM employees
    WHERE department_id IS NOT NULL
    GROUP BY department_id
)
SELECT d.name, ds.avg_salary, ds.headcount
FROM dept_stats ds
JOIN departments d ON ds.department_id = d.id
ORDER BY ds.avg_salary DESC;
```

### Recursive CTE

```sql
WITH RECURSIVE dates AS (
    SELECT DATE '2024-01-01' AS d
    UNION ALL
    SELECT d + 1 FROM dates WHERE d < '2024-01-07'
)
SELECT d FROM dates;
```

## UNION / INTERSECT / EXCEPT

```sql
-- UNION: combine, remove duplicates
SELECT name FROM employees WHERE department_id = 1
UNION
SELECT name FROM employees WHERE salary > 90000;

-- INTERSECT: rows in both
SELECT name FROM employees WHERE department_id = 1
INTERSECT
SELECT name FROM employees WHERE salary > 90000;

-- EXCEPT: in first but not second
SELECT name FROM employees WHERE department_id = 1
EXCEPT
SELECT name FROM employees WHERE salary > 100000;
```

## GROUP BY and HAVING

```sql
SELECT d.name, COUNT(*) AS headcount, AVG(e.salary) AS avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.name
HAVING AVG(e.salary) > 70000;
```

## Window Functions

### ROW_NUMBER

```sql
SELECT name, salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS rank_overall
FROM employees;
```

### RANK with PARTITION

```sql
SELECT name, department_id, salary,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank
FROM employees
WHERE department_id IS NOT NULL;
```

### LAG and LEAD

```sql
SELECT name, hired_at,
    LAG(hired_at) OVER (ORDER BY hired_at) AS prev_hire,
    LEAD(hired_at) OVER (ORDER BY hired_at) AS next_hire
FROM employees;
```

### SUM OVER (Running Total)

```sql
SELECT name, salary,
    SUM(salary) OVER (ORDER BY hired_at) AS running_total,
    SUM(salary) OVER (PARTITION BY department_id) AS dept_total
FROM employees
WHERE department_id IS NOT NULL
ORDER BY hired_at;
```

### Top earner per department

```sql
WITH ranked AS (
    SELECT e.name, d.name AS department, e.salary,
        ROW_NUMBER() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS rn
    FROM employees e
    JOIN departments d ON e.department_id = d.id
)
SELECT name, department, salary FROM ranked WHERE rn = 1;
```

## Exercises

1. Find all employees who have no department using LEFT JOIN

2. Using a CTE, find departments where total salary exceeds 150,000

3. Use `ROW_NUMBER()` to get the 2nd highest paid employee per department

4. Write a query using `LAG()` to show salary difference from previously hired employee

5. Use `EXCEPT` to find departments that have no employees

6. Write a recursive CTE that generates numbers 1 through 20
