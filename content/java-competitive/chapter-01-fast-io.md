# Chapter 1: Fast I/O

[prev: Overview](chapter-00-overview.md) | [next: Data Structures](chapter-02-data-structures.md)

## Why Scanner Is Slow

`Scanner` uses regex internally for parsing. For a problem reading 10^5 integers, Scanner can be 10-50x slower than BufferedReader + StringTokenizer.

**Benchmark (reading 10^6 integers):**

- Scanner: ~2000ms
- BufferedReader + StringTokenizer: ~150ms
- Custom FastReader (byte-level): ~80ms

In C++, `scanf` or `cin` with `ios::sync_with_stdio(false)` handles this natively. In Java, you must explicitly use fast I/O.

## BufferedReader + StringTokenizer Pattern

The standard competitive programming I/O pattern:

```java
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));

        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            int x = Integer.parseInt(st.nextToken());
            out.println(x);
        }

        out.flush();
        out.close();
    }
}
```

**Key points:**

- `BufferedReader` reads large chunks from stdin at once
- `StringTokenizer` splits by whitespace without regex
- `PrintWriter` with `BufferedOutputStream` batches output
- Always call `out.flush()` before exit

## Custom FastReader Class

For maximum speed, read bytes directly. This avoids String allocation entirely:

```java
import java.io.*;

class FastReader {
    private final InputStream in;
    private final byte[] buf = new byte[1 << 16];
    private int bufPtr = 0, bytesRead = 0;

    FastReader(InputStream in) { this.in = in; }

    private int read() throws IOException {
        if (bufPtr == bytesRead) {
            bytesRead = in.read(buf);
            bufPtr = 0;
        }
        return (bytesRead == -1) ? -1 : buf[bufPtr++];
    }

    int nextInt() throws IOException {
        int c, sign = 1, x = 0;
        do { c = read(); } while (c <= ' ');
        if (c == '-') { sign = -1; c = read(); }
        do { x = x * 10 + (c - '0'); c = read(); } while (c >= '0');
        return x * sign;
    }

    long nextLong() throws IOException {
        int c, sign = 1;
        long x = 0;
        do { c = read(); } while (c <= ' ');
        if (c == '-') { sign = -1; c = read(); }
        do { x = x * 10 + (c - '0'); c = read(); } while (c >= '0');
        return x * sign;
    }

    String next() throws IOException {
        int c;
        StringBuilder sb = new StringBuilder();
        do { c = read(); } while (c <= ' ');
        do { sb.append((char) c); c = read(); } while (c > ' ');
        return sb.toString();
    }

    double nextDouble() throws IOException {
        return Double.parseDouble(next());
    }

    boolean hasNext() throws IOException {
        int c;
        do { c = read(); } while (c <= ' ' && c != -1);
        if (c == -1) return false;
        bufPtr--;
        return true;
    }
}
```

## Reading Until EOF

```java
// With BufferedReader
BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
String line;
while ((line = br.readLine()) != null && !line.isEmpty()) {
    StringTokenizer st = new StringTokenizer(line);
    // process
}

// With FastReader
FastReader fr = new FastReader(System.in);
while (fr.hasNext()) {
    int n = fr.nextInt();
    // process
}
```

## Fast Output

`System.out.println()` flushes on every call. Use PrintWriter or StringBuilder:

```java
// Option 1: PrintWriter (recommended)
PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));
for (int i = 0; i < n; i++) out.println(ans[i]);
out.flush();

// Option 2: StringBuilder for massive output
StringBuilder sb = new StringBuilder();
for (int i = 0; i < n; i++) sb.append(ans[i]).append('\n');
System.out.print(sb);
```

For 10^6 lines of output, StringBuilder can be faster because it makes a single system call.

## Complete Contest Template

```java
import java.io.*;
import java.util.*;

public class Main {
    static BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
    static PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));
    static StringTokenizer st;

    static String next() throws IOException {
        while (st == null || !st.hasMoreTokens())
            st = new StringTokenizer(br.readLine());
        return st.nextToken();
    }
    static int nextInt() throws IOException { return Integer.parseInt(next()); }
    static long nextLong() throws IOException { return Long.parseLong(next()); }

    public static void main(String[] args) throws IOException {
        int t = nextInt();
        while (t-- > 0) solve();
        out.flush();
    }

    static void solve() throws IOException {
        int n = nextInt();
        // your solution here
    }
}
```

## Relevant Problems

- **Codeforces**: Any problem with n up to 10^5 or 10^6 will TLE with Scanner
- **AtCoder**: ABC problems often have tight time limits where fast I/O matters
- **LeetCode**: Less critical (function-based I/O), but custom readers help in contest mode
