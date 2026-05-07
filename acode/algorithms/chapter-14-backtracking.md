# Chapter 14: Delivery Zones — Recursion and Backtracking

[← Chapter 13: Dynamic Programming](chapter-13-dynamic-programming.md) | [Chapter 15: Staying Fast →](chapter-15-amortized.md)

---

## The Problem

RouteMaster divides the city into 12 delivery zones. Each morning, 8 drivers need to be assigned to zones such that:
- Every zone is covered by at least one driver
- No driver covers more than 3 zones (they'd be overloaded)
- Adjacent zones should share a driver (reduces travel between zones)
- Some drivers can't cover certain zones (Marcus refuses the highway zone)

Dispatch Dan has been doing this manually. It takes him 20 minutes every morning and he often misses constraints. You need to automate it.

This isn't a sorting problem or a shortest-path problem. It's a **constraint satisfaction problem** — find an assignment that satisfies all rules. The approach: try assignments systematically, and **backtrack** when you hit a dead end.

## Recursion: The Foundation

Backtracking is built on recursion. Let's start with the pattern:

```python
def solve(state):
    """Generic recursive backtracking template."""
    if is_complete(state):
        return state  # Found a solution

    for choice in get_choices(state):
        if is_valid(state, choice):
            make_choice(state, choice)
            result = solve(state)
            if result is not None:
                return result
            undo_choice(state, choice)  # Backtrack

    return None  # No solution from this state
```

The key: **undo_choice**. When a path leads to a dead end, we undo the last decision and try the next option. This systematically explores the solution space without getting stuck.

## Zone Assignment: The Implementation

```python
class ZoneAssigner:
    def __init__(self, zones, drivers, adjacency, restrictions):
        self.zones = zones              # List of zone names
        self.drivers = drivers          # List of driver names
        self.adjacency = adjacency      # {zone: [adjacent_zones]}
        self.restrictions = restrictions # {driver: [zones_they_cant_cover]}
        self.max_zones_per_driver = 3

    def solve(self):
        """Find a valid assignment of drivers to zones."""
        # assignment[zone] = driver assigned to it
        assignment = {}
        if self._backtrack(assignment, 0):
            return assignment
        return None  # No valid assignment exists

    def _backtrack(self, assignment, zone_idx):
        """Try to assign a driver to zone at zone_idx."""
        if zone_idx == len(self.zones):
            return True  # All zones assigned

        zone = self.zones[zone_idx]

        for driver in self.drivers:
            if self._is_valid(assignment, zone, driver):
                # Make choice
                assignment[zone] = driver

                # Recurse
                if self._backtrack(assignment, zone_idx + 1):
                    return True

                # Backtrack
                del assignment[zone]

        return False  # No driver works for this zone

    def _is_valid(self, assignment, zone, driver):
        """Check all constraints."""
        # Constraint 1: Driver can't cover this zone
        if zone in self.restrictions.get(driver, []):
            return False

        # Constraint 2: Driver not overloaded
        driver_zones = [z for z, d in assignment.items() if d == driver]
        if len(driver_zones) >= self.max_zones_per_driver:
            return False

        # Constraint 3: Adjacent zones should share a driver (soft preference)
        # (We'll handle this as optimization, not hard constraint)

        return True
```

```python
# RouteMaster's setup
zones = ["North", "South", "East", "West", "Central", "Harbor",
         "Industrial", "Residential", "University", "Airport", "Mall", "Hospital"]

drivers = ["Marcus", "Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace"]

adjacency = {
    "North": ["Central", "East", "University"],
    "South": ["Central", "West", "Harbor"],
    "Central": ["North", "South", "East", "West"],
    # ...
}

restrictions = {
    "Marcus": ["Airport"],  # Marcus refuses highway zone
    "Alice": ["Industrial"],  # Alice's van can't handle industrial roads
}

assigner = ZoneAssigner(zones, drivers, adjacency, restrictions)
result = assigner.solve()
# {"North": "Marcus", "South": "Alice", "East": "Marcus", ...}
```

## Pruning: Making Backtracking Fast

Naive backtracking explores too many dead ends. **Pruning** cuts branches early:

```python
def _backtrack_with_pruning(self, assignment, zone_idx):
    if zone_idx == len(self.zones):
        return True

    zone = self.zones[zone_idx]

    # Pruning: check if remaining zones can still be covered
    remaining_zones = len(self.zones) - zone_idx
    available_capacity = sum(
        self.max_zones_per_driver - len([z for z, d in assignment.items() if d == driver])
        for driver in self.drivers
    )
    if available_capacity < remaining_zones:
        return False  # Impossible — prune this branch

    for driver in self.drivers:
        if self._is_valid(assignment, zone, driver):
            assignment[zone] = driver
            if self._backtrack_with_pruning(assignment, zone_idx + 1):
                return True
            del assignment[zone]

    return False
```

With pruning, the algorithm detects dead ends early and skips entire subtrees. Typical speedup: 10-100x.

## N-Queens: Classic Backtracking

The canonical backtracking problem: place N queens on an N×N chessboard so no two attack each other.

```python
def solve_n_queens(n):
    """Place n queens on an n×n board. No two attack each other."""
    board = [-1] * n  # board[row] = column where queen is placed

    def is_safe(row, col):
        for prev_row in range(row):
            prev_col = board[prev_row]
            if prev_col == col:
                return False  # Same column
            if abs(prev_col - col) == abs(prev_row - row):
                return False  # Same diagonal
        return True

    def backtrack(row):
        if row == n:
            return True  # All queens placed

        for col in range(n):
            if is_safe(row, col):
                board[row] = col
                if backtrack(row + 1):
                    return True
                board[row] = -1  # Backtrack

        return False

    if backtrack(0):
        return board
    return None
```

## Generating All Valid Schedules

Sometimes you need ALL solutions, not just one:

```python
def find_all_assignments(self):
    """Find all valid zone assignments."""
    solutions = []
    assignment = {}
    self._find_all(assignment, 0, solutions)
    return solutions

def _find_all(self, assignment, zone_idx, solutions):
    if zone_idx == len(self.zones):
        solutions.append(assignment.copy())  # Found one — save it
        return  # Don't stop — keep looking

    zone = self.zones[zone_idx]
    for driver in self.drivers:
        if self._is_valid(assignment, zone, driver):
            assignment[zone] = driver
            self._find_all(assignment, zone_idx + 1, solutions)
            del assignment[zone]
```

## Sudoku Solver: Constraint Propagation + Backtracking

A more complex example combining constraint propagation with backtracking:

```python
def solve_sudoku(board):
    """Solve a 9x9 Sudoku puzzle."""
    empty = find_empty(board)
    if not empty:
        return True  # Solved

    row, col = empty

    for num in range(1, 10):
        if is_valid_placement(board, row, col, num):
            board[row][col] = num
            if solve_sudoku(board):
                return True
            board[row][col] = 0  # Backtrack

    return False

def is_valid_placement(board, row, col, num):
    # Check row
    if num in board[row]:
        return False
    # Check column
    if num in [board[r][col] for r in range(9)]:
        return False
    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if board[r][c] == num:
                return False
    return True
```

## Backtracking Complexity

Worst case: exponential. For zone assignment with 12 zones and 8 drivers: 8¹² = 68 billion possibilities without pruning. With pruning and constraints: typically explores < 10,000 nodes.

| Problem | Without pruning | With pruning |
|---|---|---|
| Zone assignment (12 zones, 8 drivers) | O(8¹²) | ~10,000 nodes |
| N-Queens (8×8) | O(8⁸) | ~100 nodes |
| Sudoku | O(9⁸¹) | ~1,000 nodes |

Pruning is what makes backtracking practical.

## When to Use Backtracking

| Signal | Backtracking likely |
|---|---|
| "Find an assignment that satisfies..." | Yes |
| "Generate all valid configurations" | Yes |
| "Is there a way to..." (constraint satisfaction) | Yes |
| Multiple constraints that interact | Yes |
| Solution is a sequence of choices | Yes |

## What You Learned

- **Backtracking** — try choices, recurse, undo on failure
- **Pruning** — cut dead-end branches early
- **Constraint satisfaction** — find assignments meeting all rules
- **All solutions** — don't stop at first, collect all valid configurations
- **Complexity** — exponential worst case, but pruning makes it practical
- **Template** — make choice → recurse → undo choice

Dispatch Dan's 20-minute manual process now takes 0.3 seconds. Every zone is covered. No driver is overloaded. Marcus doesn't get the highway zone.

One chapter left. CEO Lena's growth projections mean RouteMaster's data doubles every 6 months. When should you rebuild an index vs patch it? When is O(n) amortized actually fine? How do you keep the system fast as it scales?

That's Chapter 15.

---

[← Chapter 13: Dynamic Programming](chapter-13-dynamic-programming.md) | [Chapter 15: Staying Fast →](chapter-15-amortized.md)
