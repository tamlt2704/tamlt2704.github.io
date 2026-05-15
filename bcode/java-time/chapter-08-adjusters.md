# Chapter 8 — Temporal Adjusters

[← Formatting & Parsing](./chapter-07-formatting.md) | [Next: Daylight Saving Traps →](./chapter-09-dst.md)

---

## The Problem

MeetSync's billing team needs date rules that sound simple in English but are tricky in code:

- "Invoice due on the **next business day** after the 15th"
- "Recurring standup every **first Monday of the month**"
- "Payment processed on the **last Friday of each month**"

Writing this logic from scratch means loops, edge cases, and bugs. Java's `TemporalAdjusters` class provides pre-built solutions for exactly these patterns.

---

## Built-in Adjusters

```java
import java.time.LocalDate;
import java.time.DayOfWeek;
import java.time.temporal.TemporalAdjusters;

LocalDate today = LocalDate.of(2024, 3, 20); // Wednesday

// First/last day of month
LocalDate firstOfMonth = today.with(TemporalAdjusters.firstDayOfMonth());
System.out.println(firstOfMonth); // 2024-03-01

LocalDate lastOfMonth = today.with(TemporalAdjusters.lastDayOfMonth());
System.out.println(lastOfMonth); // 2024-03-31

// First/last day of year
LocalDate firstOfYear = today.with(TemporalAdjusters.firstDayOfYear());
System.out.println(firstOfYear); // 2024-01-01

// First day of next month
LocalDate nextMonth = today.with(TemporalAdjusters.firstDayOfNextMonth());
System.out.println(nextMonth); // 2024-04-01
```

---

## Day-of-Week Adjusters

```java
LocalDate wednesday = LocalDate.of(2024, 3, 20); // Wednesday

// Next specific day (strictly after today)
LocalDate nextFriday = wednesday.with(TemporalAdjusters.next(DayOfWeek.FRIDAY));
System.out.println(nextFriday); // 2024-03-22

// Next-or-same (returns today if it matches)
LocalDate nextWed = wednesday.with(TemporalAdjusters.nextOrSame(DayOfWeek.WEDNESDAY));
System.out.println(nextWed); // 2024-03-20 (today IS Wednesday)

// Previous specific day
LocalDate prevMonday = wednesday.with(TemporalAdjusters.previous(DayOfWeek.MONDAY));
System.out.println(prevMonday); // 2024-03-18

// Previous-or-same
LocalDate prevWed = wednesday.with(TemporalAdjusters.previousOrSame(DayOfWeek.WEDNESDAY));
System.out.println(prevWed); // 2024-03-20
```

---

## Ordinal Day-in-Month

"First Monday", "Third Thursday", "Last Friday":

```java
LocalDate march2024 = LocalDate.of(2024, 3, 1);

// First Monday of March
LocalDate firstMonday = march2024.with(
    TemporalAdjusters.firstInMonth(DayOfWeek.MONDAY));
System.out.println(firstMonday); // 2024-03-04

// Third Thursday of March
LocalDate thirdThursday = march2024.with(
    TemporalAdjusters.dayOfWeekInMonth(3, DayOfWeek.THURSDAY));
System.out.println(thirdThursday); // 2024-03-21

// Last Friday of March
LocalDate lastFriday = march2024.with(
    TemporalAdjusters.lastInMonth(DayOfWeek.FRIDAY));
System.out.println(lastFriday); // 2024-03-29
```

---

## MeetSync: Payment Due Dates

```java
public class BillingService {

    /**
     * Invoice due on the last business day of the month.
     */
    public LocalDate invoiceDueDate(LocalDate billingMonth) {
        LocalDate lastDay = billingMonth.with(TemporalAdjusters.lastDayOfMonth());
        // If last day is weekend, roll back to Friday
        return rollToBusinessDay(lastDay);
    }

    /**
     * Payroll runs on the last Friday of each month.
     */
    public LocalDate payrollDate(int year, int month) {
        return LocalDate.of(year, month, 1)
            .with(TemporalAdjusters.lastInMonth(DayOfWeek.FRIDAY));
    }

    private LocalDate rollToBusinessDay(LocalDate date) {
        if (date.getDayOfWeek() == DayOfWeek.SATURDAY) {
            return date.minusDays(1);
        } else if (date.getDayOfWeek() == DayOfWeek.SUNDAY) {
            return date.minusDays(2);
        }
        return date;
    }
}

BillingService billing = new BillingService();
System.out.println(billing.invoiceDueDate(LocalDate.of(2024, 3, 1)));
// 2024-03-29 (March 31 is Sunday → rolls to Friday 29th)

System.out.println(billing.payrollDate(2024, 3));
// 2024-03-29
```

---

## Custom Adjusters with Lambdas

`TemporalAdjuster` is a functional interface. Write your own:

```java
import java.time.temporal.TemporalAdjuster;
import java.time.temporal.Temporal;

// Next business day (skip weekends)
TemporalAdjuster nextBusinessDay = temporal -> {
    LocalDate date = LocalDate.from(temporal);
    LocalDate next = date.plusDays(1);
    while (next.getDayOfWeek() == DayOfWeek.SATURDAY 
        || next.getDayOfWeek() == DayOfWeek.SUNDAY) {
        next = next.plusDays(1);
    }
    return next;
};

LocalDate friday = LocalDate.of(2024, 3, 22); // Friday
System.out.println(friday.with(nextBusinessDay)); // 2024-03-25 (Monday)

LocalDate saturday = LocalDate.of(2024, 3, 23);
System.out.println(saturday.with(nextBusinessDay)); // 2024-03-25 (Monday)
```

---

## Reusable Adjuster Class

For more complex logic, implement the interface directly:

```java
public class NextBusinessDayAdjuster implements TemporalAdjuster {
    private final Set<LocalDate> holidays;

    public NextBusinessDayAdjuster(Set<LocalDate> holidays) {
        this.holidays = holidays;
    }

    @Override
    public Temporal adjustInto(Temporal temporal) {
        LocalDate date = LocalDate.from(temporal).plusDays(1);
        while (isNonBusinessDay(date)) {
            date = date.plusDays(1);
        }
        return date;
    }

    private boolean isNonBusinessDay(LocalDate date) {
        return date.getDayOfWeek() == DayOfWeek.SATURDAY
            || date.getDayOfWeek() == DayOfWeek.SUNDAY
            || holidays.contains(date);
    }
}

// Usage with holidays
Set<LocalDate> holidays = Set.of(
    LocalDate.of(2024, 12, 25), // Christmas
    LocalDate.of(2024, 12, 26)  // Boxing Day
);
TemporalAdjuster adjuster = new NextBusinessDayAdjuster(holidays);

LocalDate christmas = LocalDate.of(2024, 12, 24); // Tuesday
System.out.println(christmas.with(adjuster)); // 2024-12-27 (Friday)
```

---

## Recurring Meeting Rules

MeetSync generates recurring meeting dates:

```java
public List<LocalDate> recurringMeetings(
        LocalDate start, int count, TemporalAdjuster rule) {
    List<LocalDate> dates = new ArrayList<>();
    LocalDate current = start;
    for (int i = 0; i < count; i++) {
        current = current.with(rule);
        dates.add(current);
    }
    return dates;
}

// "Every first Monday" for the next 4 months
TemporalAdjuster firstMondayNextMonth = temporal -> {
    LocalDate date = LocalDate.from(temporal);
    LocalDate nextMonth = date.with(TemporalAdjusters.firstDayOfNextMonth());
    return nextMonth.with(TemporalAdjusters.firstInMonth(DayOfWeek.MONDAY));
};

List<LocalDate> standups = recurringMeetings(
    LocalDate.of(2024, 3, 1), 4, firstMondayNextMonth);
// [2024-04-01, 2024-05-06, 2024-06-03, 2024-07-01]
```

---

## What You Learned

- `TemporalAdjusters` provides pre-built date rules: first/last day, next/previous weekday
- `dayOfWeekInMonth(n, day)` finds the nth occurrence of a weekday in a month
- `lastInMonth(DayOfWeek.FRIDAY)` finds the last Friday (or any day) of the month
- Custom adjusters are lambdas: `temporal -> { ... return adjusted; }`
- Combine adjusters for complex business rules (skip weekends AND holidays)
- Use `.with(adjuster)` to apply any adjuster to a date
- Adjusters compose well for recurring event generation

---

*Next up: What happens when 2:30 AM occurs twice in one night — or not at all? [Chapter 9](./chapter-09-dst.md) tackles Daylight Saving Time traps.*
