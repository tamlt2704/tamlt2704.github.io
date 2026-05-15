# Chapter 1 — LocalDate: Days Without Time

[← Overview](./README.md) | [Next: LocalTime →](./chapter-02-localtime.md)

---

## The Problem

Monday morning at MeetSync. A support ticket lands in your queue:

> "My birthday is January 15th. Your app wished me happy birthday on January 14th."

You dig into the code. The user is in Tokyo (UTC+9). Their birthday was stored as a `Timestamp`:

```java
// The old code — storing birthday as a timestamp
Timestamp birthday = Timestamp.valueOf("1990-01-15 00:00:00");
```

When the server (running in UTC) checks "is today their birthday?", it compares against midnight UTC. But in Tokyo, January 15th 00:00 is still January 14th 15:00 UTC. The birthday check fires a day early.

The fix is obvious once you see it: **a birthday is a date, not a moment in time.** It has no timezone. It has no hours. It's just a day on a calendar.

Enter `LocalDate`.

---

## LocalDate: Just a Date

`LocalDate` represents a year-month-day with no time and no timezone. It's exactly what a birthday, anniversary, or deadline is.

```java
import java.time.LocalDate;
import java.time.Month;

// Creating dates
LocalDate today = LocalDate.now();
LocalDate birthday = LocalDate.of(1990, Month.JANUARY, 15);
LocalDate parsed = LocalDate.parse("2024-03-20"); // ISO format

System.out.println(birthday); // 1990-01-15
```

No timezone ambiguity. No midnight confusion. January 15th is January 15th everywhere.

---

## Fixing the Birthday Bug

Here's the corrected MeetSync birthday check:

```java
public boolean isBirthdayToday(LocalDate userBirthday) {
    LocalDate today = LocalDate.now();
    return today.getMonthValue() == userBirthday.getMonthValue()
        && today.getDayOfMonth() == userBirthday.getDayOfMonth();
}

// Usage
LocalDate birthday = LocalDate.of(1990, 1, 15);
if (isBirthdayToday(birthday)) {
    sendBirthdayEmail(user);
}
```

No timestamp. No timezone. Just comparing month and day.

---

## Computing Age

Users want to see their age on their profile. `Period.between()` handles the calendar math:

```java
import java.time.Period;

public int computeAge(LocalDate birthDate) {
    return Period.between(birthDate, LocalDate.now()).getYears();
}

LocalDate born = LocalDate.of(1990, 1, 15);
System.out.println("Age: " + computeAge(born)); // Age: 34 (in 2024)
```

`Period` understands months have different lengths. It won't tell you someone is 35 when they're 34.

---

## Date Arithmetic

MeetSync needs to calculate trial expiration dates and payment deadlines:

```java
LocalDate signupDate = LocalDate.of(2024, 3, 1);

// Add days
LocalDate trialEnd = signupDate.plusDays(14);
System.out.println("Trial ends: " + trialEnd); // 2024-03-15

// Add months (handles month-end correctly)
LocalDate nextBilling = signupDate.plusMonths(1);
System.out.println("Next bill: " + nextBilling); // 2024-04-01

// Subtract
LocalDate reminderDate = trialEnd.minusDays(3);
System.out.println("Send reminder: " + reminderDate); // 2024-03-12
```

---

## Day of Week and Business Logic

MeetSync doesn't send marketing emails on weekends:

```java
import java.time.DayOfWeek;

public LocalDate nextBusinessDay(LocalDate from) {
    LocalDate next = from.plusDays(1);
    while (next.getDayOfWeek() == DayOfWeek.SATURDAY
        || next.getDayOfWeek() == DayOfWeek.SUNDAY) {
        next = next.plusDays(1);
    }
    return next;
}

LocalDate friday = LocalDate.of(2024, 3, 15); // Friday
System.out.println(nextBusinessDay(friday)); // 2024-03-18 (Monday)
```

`DayOfWeek` is an enum: `MONDAY` through `SUNDAY`. No more magic numbers.

---

## Leap Year Awareness

A user born on February 29th shouldn't crash your system:

```java
LocalDate leapBirthday = LocalDate.of(2000, 2, 29);
System.out.println(leapBirthday.isLeapYear()); // true

// What happens when we add 1 year?
LocalDate nextYear = leapBirthday.plusYears(1);
System.out.println(nextYear); // 2001-02-28 (adjusted safely)

// Check any year
System.out.println(LocalDate.of(2024, 1, 1).isLeapYear()); // true
System.out.println(LocalDate.of(2023, 1, 1).isLeapYear()); // false
```

Java adjusts gracefully — no `DateTimeException`, no silent corruption.

---

## Comparing Dates

```java
LocalDate deadline = LocalDate.of(2024, 4, 1);
LocalDate today = LocalDate.of(2024, 3, 20);

System.out.println(today.isBefore(deadline)); // true
System.out.println(today.isAfter(deadline));  // false
System.out.println(today.isEqual(deadline));  // false

// Days until deadline
long daysLeft = today.until(deadline, java.time.temporal.ChronoUnit.DAYS);
System.out.println("Days remaining: " + daysLeft); // 12
```

---

## What You Learned

- `LocalDate` represents a calendar date with no time or timezone
- Use it for birthdays, deadlines, holidays — anything that's "just a day"
- `Period.between()` computes age and date differences correctly
- `plusDays()`, `plusMonths()`, `plusYears()` handle calendar quirks (leap years, month lengths)
- `DayOfWeek` enum eliminates magic numbers in business day logic
- `isLeapYear()` and safe date arithmetic prevent Feb 29 crashes
- Never store a pure date as a timestamp — that's how the birthday bug happens

---

*Next up: What about store hours? "Open 9:00 to 17:00" is a time without a date. [Chapter 2](./chapter-02-localtime.md) introduces `LocalTime`.*
