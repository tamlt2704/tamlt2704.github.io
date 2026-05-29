# Chapter 4: Math Tricks

[prev: Algorithms](chapter-03-algorithms.md) | [next: Graphs](chapter-05-graphs.md)

## Modular Arithmetic

Most CP problems use MOD = 10^9 + 7 (a prime). Key rules:

- (a + b) % m = ((a % m) + (b % m)) % m
- (a _ b) % m = ((a % m) _ (b % m)) % m
- (a - b) % m = ((a % m) - (b % m) + m) % m (add m to avoid negatives)

```java
static final int MOD = 1_000_000_007;

static long add(long a, long b) { return (a + b) % MOD; }
static long sub(long a, long b) { return (a - b % MOD + MOD) % MOD; }
static long mul(long a, long b) { return a % MOD * (b % MOD) % MOD; }
```

**Warning:** Always cast to `long` before multiplying two ints under mod to avoid overflow.

## Modular Exponentiation — O(log p)

```java
static long modpow(long base, long exp, long mod) {
    long result = 1;
    base %= mod;
    while (exp > 0) {
        if ((exp & 1) == 1) result = result * base % mod;
        base = base * base % mod;
        exp >>= 1;
    }
    return result;
}
```

## Modular Inverse — O(log mod)

For prime mod, a^(-1) = a^(mod-2) mod p (Fermat's little theorem):

```java
static long modinv(long a, long mod) {
    return modpow(a, mod - 2, mod);
}

// Division under mod: a / b mod p = a * b^(-1) mod p
static long moddiv(long a, long b, long mod) {
    return mul(a, modinv(b, mod));
}
```

## GCD / LCM — O(log(min(a,b)))

```java
static long gcd(long a, long b) {
    while (b != 0) { long t = b; b = a % b; a = t; }
    return a;
}
static long lcm(long a, long b) { return a / gcd(a, b) * b; }
```

## Prime Sieve (Eratosthenes) — O(n log log n)

```java
static boolean[] sieve(int n) {
    boolean[] isComposite = new boolean[n + 1];
    for (int i = 2; (long) i * i <= n; i++) {
        if (!isComposite[i]) {
            for (int j = i * i; j <= n; j += i)
                isComposite[j] = true;
        }
    }
    return isComposite;
}
```

**BitSet version** for memory efficiency (sieve up to 10^8):

```java
static BitSet sieveBitSet(int n) {
    BitSet bs = new BitSet(n + 1);
    bs.set(0); bs.set(1);
    for (int i = 2; (long) i * i <= n; i++) {
        if (!bs.get(i)) {
            for (int j = i * i; j <= n; j += i) bs.set(j);
        }
    }
    return bs; // bs.get(x) == false means x is prime
}
```

## Combinatorics (nCr mod p) — O(n) precompute, O(1) query

```java
static long[] fact, invFact;

static void precompute(int n, long mod) {
    fact = new long[n + 1];
    invFact = new long[n + 1];
    fact[0] = 1;
    for (int i = 1; i <= n; i++) fact[i] = fact[i - 1] * i % mod;
    invFact[n] = modpow(fact[n], mod - 2, mod);
    for (int i = n - 1; i >= 0; i--) invFact[i] = invFact[i + 1] * (i + 1) % mod;
}

static long nCr(int n, int r, long mod) {
    if (r < 0 || r > n) return 0;
    return fact[n] % mod * invFact[r] % mod * invFact[n - r] % mod;
}
```

## BigInteger

Use only when needed (numbers exceeding 10^18). Much slower than primitive arithmetic.

```java
import java.math.BigInteger;

BigInteger a = BigInteger.valueOf(123456789L);
BigInteger b = new BigInteger("999999999999999999999");
BigInteger sum = a.add(b);
BigInteger prod = a.multiply(b);
BigInteger mod = a.mod(BigInteger.valueOf(MOD));
BigInteger power = a.modPow(BigInteger.valueOf(exp), BigInteger.valueOf(MOD));
BigInteger gcd = a.gcd(b);
```

**Performance:** BigInteger multiply is O(n^1.585) (Karatsuba). For numbers under 10^18, always use `long`.

## Matrix Exponentiation — O(k^3 log n)

For linear recurrences (Fibonacci, etc.) in O(log n):

```java
static long[][] matmul(long[][] A, long[][] B, long mod) {
    int n = A.length;
    long[][] C = new long[n][n];
    for (int i = 0; i < n; i++)
        for (int k = 0; k < n; k++) if (A[i][k] != 0)
            for (int j = 0; j < n; j++)
                C[i][j] = (C[i][j] + A[i][k] * B[k][j]) % mod;
    return C;
}

static long[][] matpow(long[][] M, long p, long mod) {
    int n = M.length;
    long[][] result = new long[n][n];
    for (int i = 0; i < n; i++) result[i][i] = 1; // identity
    while (p > 0) {
        if ((p & 1) == 1) result = matmul(result, M, mod);
        M = matmul(M, M, mod);
        p >>= 1;
    }
    return result;
}

// Fibonacci in O(log n)
static long fib(long n) {
    if (n <= 1) return n;
    long[][] M = {{1, 1}, {1, 0}};
    long[][] res = matpow(M, n - 1, MOD);
    return res[0][0];
}
```

## Relevant Problems

- **Codeforces 1359C** — Modular arithmetic
- **LeetCode 50** — Pow(x, n) (modpow pattern)
- **Codeforces 1228C** — Prime sieve + combinatorics
- **AtCoder ABC 129F** — Matrix exponentiation
- **Codeforces 1114F** — nCr with mod
