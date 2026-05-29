# Chapter 4: Relationships

[prev: Repositories](chapter-03-repositories.md) | [next: N+1 Problem](chapter-05-n-plus-one.md)

## @ManyToOne (most common)

The owning side — holds the foreign key.

```java
@Entity
@Table(name = "orders")
@Getter @Setter @NoArgsConstructor
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id", nullable = false)
    private Customer customer;

    @Enumerated(EnumType.STRING)
    private OrderStatus status;
}
```

## @OneToMany (inverse side)

```java
@Entity
@Table(name = "customers")
@Getter @Setter @NoArgsConstructor
public class Customer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @OneToMany(mappedBy = "customer", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Order> orders = new ArrayList<>();

    public void addOrder(Order order) {
        orders.add(order);
        order.setCustomer(this);
    }

    public void removeOrder(Order order) {
        orders.remove(order);
        order.setCustomer(null);
    }
}
```

**Key points:**

- `mappedBy = "customer"` means Order.customer owns the relationship
- Always use helper methods (`addOrder`/`removeOrder`) to keep both sides in sync
- `orphanRemoval = true` deletes orders removed from the list

## @OneToOne

```java
@Entity
@Table(name = "users")
@Getter @Setter @NoArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String username;

    @OneToOne(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private UserProfile profile;
}

@Entity
@Table(name = "user_profiles")
@Getter @Setter @NoArgsConstructor
public class UserProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String bio;
    private String avatarUrl;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", unique = true)
    private User user;
}
```

Note: `@OneToOne` with `mappedBy` on the parent side cannot be truly lazy without bytecode enhancement. Consider using `@ManyToOne` with a unique constraint instead if lazy loading is critical.

## @ManyToMany

```java
@Entity
@Table(name = "students")
@Getter @Setter @NoArgsConstructor
public class Student {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @ManyToMany(cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    @JoinTable(
        name = "student_courses",
        joinColumns = @JoinColumn(name = "student_id"),
        inverseJoinColumns = @JoinColumn(name = "course_id")
    )
    private Set<Course> courses = new HashSet<>();

    public void addCourse(Course course) {
        courses.add(course);
        course.getStudents().add(this);
    }

    public void removeCourse(Course course) {
        courses.remove(course);
        course.getStudents().remove(this);
    }
}

@Entity
@Table(name = "courses")
@Getter @Setter @NoArgsConstructor
public class Course {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;

    @ManyToMany(mappedBy = "courses")
    private Set<Student> students = new HashSet<>();
}
```

**Use `Set` not `List`** for `@ManyToMany` — Hibernate handles removal more efficiently with Sets.

## Cascade Types

| Type      | Effect                                 |
| --------- | -------------------------------------- |
| `PERSIST` | Save child when parent is saved        |
| `MERGE`   | Update child when parent is merged     |
| `REMOVE`  | Delete child when parent is deleted    |
| `REFRESH` | Refresh child when parent is refreshed |
| `DETACH`  | Detach child when parent is detached   |
| `ALL`     | All of the above                       |

```java
// Common patterns:
@OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)  // parent owns children completely
@ManyToMany(cascade = {CascadeType.PERSIST, CascadeType.MERGE})  // never CASCADE REMOVE on ManyToMany
```

**Never use `CascadeType.REMOVE` or `CascadeType.ALL` on `@ManyToMany`** — it would delete the other entity, not just the join table row.

## Fetch Types

|               | Default | Recommendation |
| ------------- | ------- | -------------- |
| `@ManyToOne`  | EAGER   | Change to LAZY |
| `@OneToOne`   | EAGER   | Change to LAZY |
| `@OneToMany`  | LAZY    | Keep LAZY      |
| `@ManyToMany` | LAZY    | Keep LAZY      |

```java
@ManyToOne(fetch = FetchType.LAZY)  // always set this explicitly
@JoinColumn(name = "customer_id")
private Customer customer;
```

**Rule: Make everything LAZY, then optimize fetching where needed** (see [Chapter 5: N+1 Problem](chapter-05-n-plus-one.md)).

## Bidirectional Mapping Summary

| Relationship          | Owning Side           | Inverse Side         |
| --------------------- | --------------------- | -------------------- |
| OneToMany / ManyToOne | ManyToOne (has FK)    | OneToMany (mappedBy) |
| OneToOne              | Side with @JoinColumn | Side with mappedBy   |
| ManyToMany            | Side with @JoinTable  | Side with mappedBy   |

The owning side controls the foreign key. Changes to the inverse side alone are NOT persisted — you must always update the owning side.

## Exercises

1. Model a Blog: `Post` has many `Comment`s (OneToMany with cascade ALL and orphanRemoval)
2. Add a `@ManyToMany` between `Post` and `Tag` with a join table
3. Write a test that adds a Comment via `post.addComment()` and verify cascade persist works
4. Test orphanRemoval: remove a comment from the list and verify it is deleted from the database
5. Change `@ManyToOne` from EAGER to LAZY, enable SQL logging, and observe the difference
