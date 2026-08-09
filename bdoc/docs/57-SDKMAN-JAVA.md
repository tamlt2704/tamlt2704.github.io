# Chapter 57: SDKMAN — Java Version & SDK Management

## What you'll learn

- What SDKMAN does (manage multiple Java versions + related tools)
- Installing and switching between Java versions (8, 11, 17, 21, 22)
- Choosing between vendors (Temurin, GraalVM, Amazon Corretto, Oracle)
- Managing build tools (Gradle, Maven, Kotlin, Scala, Spring Boot CLI)
- Per-project Java version (automatic switching)
- Common workflows for professional Java development

---

## PART 1: What is SDKMAN?

## 57.1 The problem it solves

```
WITHOUT SDKMAN:
  • Download JDK from Oracle/Adoptium website → manually extract → set JAVA_HOME
  • Need Java 17 for project A, Java 21 for project B → nightmare
  • Update Gradle? Download new zip, swap paths, hope nothing breaks
  • New team member? "Install Java" → 30 minutes of confusion

WITH SDKMAN:
  sdk install java 21.0.3-tem     ← one command
  sdk use java 17.0.11-tem        ← switch instantly
  sdk install gradle 8.8          ← one command
  cd project-a/                   ← auto-switches to project's Java version
  
  Done. 30 seconds instead of 30 minutes.
```

## 57.2 What SDKMAN manages

| Category | Tools |
|----------|-------|
| **Java JDKs** | Temurin, GraalVM, Corretto, Oracle, Zulu, Microsoft, SAP, Liberica |
| **Build tools** | Gradle, Maven, Ant, sbt |
| **Languages** | Kotlin, Scala, Groovy, Ceylon |
| **Frameworks** | Spring Boot CLI, Micronaut, Quarkus |
| **Other** | VisualVM, JBang, Leiningen, AsciidoctorJ |

---

## PART 2: Installation

## 57.3 Install SDKMAN

```bash
# Linux / macOS / WSL (one command)
curl -s "https://get.sdkman.io" | bash

# Open a new terminal (or source it)
source "$HOME/.sdkman/bin/sdkman-init.sh"

# Verify
sdk version
# SDKMAN! 5.18.2

# Windows (native — without WSL)
# Use Git Bash or install via: https://sdkman.io/install
# Windows PowerShell support is experimental
```

**What it does:**
- Creates `~/.sdkman/` directory (all SDKs live here)
- Adds itself to your shell profile (`~/.bashrc`, `~/.zshrc`)
- Manages PATH and JAVA_HOME automatically

## 57.4 Shell integration

```bash
# SDKMAN adds this to your .bashrc/.zshrc:
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"

# This means:
# • `java -version` always points to the SDKMAN-managed version
# • JAVA_HOME is set automatically
# • Switching versions updates PATH instantly
```

---

## PART 3: Managing Java Versions

## 57.5 List available Java versions

```bash
sdk list java
```

Output (abbreviated):
```
================================================================================
Available Java Versions for Linux 64bit
================================================================================
 Vendor        | Use | Version      | Dist    | Status     | Identifier
--------------------------------------------------------------------------------
 Corretto      |     | 22.0.1       | amzn    |            | 22.0.1-amzn
               |     | 21.0.3       | amzn    |            | 21.0.3-amzn
               |     | 17.0.11      | amzn    |            | 17.0.11-amzn
               |     | 11.0.23      | amzn    |            | 11.0.23-amzn
               |     | 8.0.412      | amzn    |            | 8.0.412-amzn
 GraalVM CE    |     | 22.0.1       | graalce |            | 22.0.1-graalce
               |     | 21.0.3       | graalce |            | 21.0.3-graalce
 Microsoft     |     | 21.0.3       | ms      |            | 21.0.3-ms
               |     | 17.0.11      | ms      |            | 17.0.11-ms
 Oracle        |     | 22.0.1       | oracle  |            | 22.0.1-oracle
               |     | 21.0.3       | oracle  |            | 21.0.3-oracle
 Temurin       | >>> | 21.0.3       | tem     | installed  | 21.0.3-tem
               |     | 17.0.11      | tem     |            | 17.0.11-tem
               |     | 11.0.23      | tem     |            | 11.0.23-tem
 Zulu          |     | 22.0.1       | zulu    |            | 22.0.1-zulu
               |     | 21.0.3       | zulu    |            | 21.0.3-zulu
================================================================================
Use the Identifier for installation:
    $ sdk install java 21.0.3-tem
================================================================================
```

## 57.6 Choosing a vendor

| Vendor | Identifier | Best for | Notes |
|--------|-----------|----------|-------|
| **Eclipse Temurin** | `-tem` | General development (recommended default) | Free, community-maintained, most popular |
| **Amazon Corretto** | `-amzn` | AWS deployments | Free, AWS-optimized, long-term support |
| **GraalVM CE** | `-graalce` | Native compilation, polyglot | Ahead-of-time compilation, fast startup |
| **Oracle** | `-oracle` | Oracle support contracts | Free for dev, licence for production (check terms) |
| **Azul Zulu** | `-zulu` | Embedded, specialized platforms | Wide platform support, free community edition |
| **Microsoft** | `-ms` | Azure deployments | Free, Microsoft-supported |
| **Liberica** | `-librca` | Full JavaFX included | Good for desktop apps |
| **SAP Machine** | `-sapmchn` | SAP ecosystem | SAP-supported OpenJDK |

**My recommendation:** Use **Temurin** (`-tem`) for everything unless you have a specific reason not to. It's the successor to AdoptOpenJDK — free, reliable, well-maintained.

## 57.7 Install Java versions

```bash
# Install latest Java 21 (Temurin)
sdk install java 21.0.3-tem

# Install Java 17 (for older projects)
sdk install java 17.0.11-tem

# Install Java 11 (legacy projects)
sdk install java 11.0.23-tem

# Install GraalVM (for native compilation)
sdk install java 21.0.3-graalce

# Install latest version of any vendor (short form)
sdk install java 21-tem    # resolves to latest 21.x.x-tem

# Install and make it the default
sdk install java 21.0.3-tem
# SDKMAN asks: "Do you want java 21.0.3-tem to be set as default? (Y/n)"
```

## 57.8 Switch between versions

```bash
# Switch for THIS terminal session only
sdk use java 17.0.11-tem
java -version
# openjdk version "17.0.11" 2024-04-16

sdk use java 21.0.3-tem
java -version
# openjdk version "21.0.3" 2024-04-16

# Set as the global default (persists across terminal sessions)
sdk default java 21.0.3-tem

# Check current version
sdk current java
# Using java version 21.0.3-tem

# Check all current versions
sdk current
# java: 21.0.3-tem
# gradle: 8.8
# kotlin: 2.0.0
```

## 57.9 Verify installation

```bash
java -version
# openjdk version "21.0.3" 2024-04-16
# OpenJDK Runtime Environment Temurin-21.0.3+9 (build 21.0.3+9)
# OpenJDK 64-Bit Server VM Temurin-21.0.3+9 (build 21.0.3+9, mixed mode, sharing)

echo $JAVA_HOME
# /home/user/.sdkman/candidates/java/21.0.3-tem

which java
# /home/user/.sdkman/candidates/java/current/bin/java
```

---

## PART 4: Per-Project Java Version

## 57.10 The `.sdkmanrc` file (automatic switching!)

```bash
# In your project root, create .sdkmanrc:
cd my-project/
sdk env init
# Creates .sdkmanrc with current versions

# Or create manually:
cat > .sdkmanrc << EOF
java=17.0.11-tem
gradle=8.8
EOF
```

```bash
# Now when you cd into the project:
cd my-project/
sdk env
# Using java version 17.0.11-tem in this shell.
# Using gradle version 8.8 in this shell.

cd ../other-project/
sdk env
# Using java version 21.0.3-tem in this shell.
```

**Auto-switching (optional — enable it):**
```bash
# Enable auto-env in SDKMAN config:
sdk config

# Set: sdkman_auto_env=true
# Now SDKMAN auto-switches when you cd into a directory with .sdkmanrc!
```

```properties
# ~/.sdkman/etc/config
sdkman_auto_env=true
sdkman_auto_answer=false
sdkman_colour_enable=true
sdkman_selfupdate_feature=true
```

## 57.11 Commit `.sdkmanrc` to git

```bash
# .sdkmanrc
java=21.0.3-tem
gradle=8.8

# Add to git — ensures all team members use the same versions
git add .sdkmanrc
git commit -m "chore: pin Java 21 and Gradle 8.8 via SDKMAN"
```

**Team workflow:**
1. New developer clones repo
2. `cd project/` → SDKMAN prompts: "java 21.0.3-tem is not installed. Install? (Y/n)"
3. Types Y → installed and switched automatically
4. Everyone on the same version. Always.

---

## PART 5: Managing Build Tools

## 57.12 Gradle

```bash
# List available versions
sdk list gradle

# Install latest
sdk install gradle 8.8

# Install specific version
sdk install gradle 7.6.4

# Switch
sdk use gradle 8.8
gradle --version

# NOTE: Most projects use the Gradle Wrapper (./gradlew)
# which downloads its own version. SDKMAN's Gradle is for:
# • Running `gradle init` to create new projects
# • Global Gradle when there's no wrapper
# • The wrapper uses SDKMAN's Java version (JAVA_HOME)
```

## 57.13 Maven

```bash
sdk install maven 3.9.8
sdk use maven 3.9.8
mvn --version

# Maven uses JAVA_HOME → which SDKMAN controls
# So switching Java version also changes what Maven uses
```

## 57.14 Other tools

```bash
# Kotlin
sdk install kotlin 2.0.0
sdk use kotlin 2.0.0
kotlin -version

# Spring Boot CLI
sdk install springboot 3.3.0
spring --version
spring init --dependencies=web,data-jpa my-app

# JBang (run Java scripts like shell scripts)
sdk install jbang
jbang init hello.java
jbang hello.java

# VisualVM (JVM monitoring/profiling)
sdk install visualvm

# Scala + sbt
sdk install scala 3.4.2
sdk install sbt 1.10.0
```

---

## PART 6: Advanced Usage

## 57.15 Offline mode

```bash
# Enable offline mode (use only locally installed versions)
sdk offline enable

# Disable (go back online)
sdk offline disable

# Useful for: airplanes, restricted networks, CI with pre-installed SDKs
```

## 57.16 Managing disk space

```bash
# See what's installed
sdk list java | grep installed
sdk list gradle | grep installed

# Uninstall a version you don't need
sdk uninstall java 11.0.23-tem
sdk uninstall gradle 7.6.4

# Flush download archives (frees disk space)
sdk flush archives

# Flush temp files
sdk flush temp

# Where everything lives:
ls ~/.sdkman/candidates/java/
# 11.0.23-tem  17.0.11-tem  21.0.3-tem  current -> 21.0.3-tem

du -sh ~/.sdkman/candidates/java/
# ~1.5GB (3 JDK versions)
```

## 57.17 CI/CD usage

```yaml
# GitHub Actions — install SDKMAN + Java
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup SDKMAN
        run: |
          curl -s "https://get.sdkman.io" | bash
          source "$HOME/.sdkman/bin/sdkman-init.sh"
          sdk install java 21.0.3-tem
          sdk install gradle 8.8

      - name: Build
        run: |
          source "$HOME/.sdkman/bin/sdkman-init.sh"
          gradle build

# BETTER: Use setup-java action (faster, cached):
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '21'
# setup-java is usually better for CI (caching, speed)
# SDKMAN is better for local development
```

## 57.18 SDKMAN vs alternatives

| Tool | Platforms | Java? | Other tools? | Auto-switch? |
|------|-----------|-------|-------------|-------------|
| **SDKMAN** | Linux, macOS, WSL | ✅ (many vendors) | ✅ (Gradle, Maven, Kotlin...) | ✅ (.sdkmanrc) |
| **jenv** | Linux, macOS | ✅ (switch only — doesn't install) | ❌ | ✅ (.java-version) |
| **asdf** | Linux, macOS | ✅ (via plugin) | ✅ (any language) | ✅ (.tool-versions) |
| **mise** | Linux, macOS | ✅ (via plugin) | ✅ (any language) | ✅ (.mise.toml) |
| **Homebrew** | macOS | ✅ (one version at a time) | ❌ | ❌ |
| **jabba** | All | ✅ | ❌ | ✅ (.jabbarc) |

**SDKMAN wins for Java developers** because it understands the Java ecosystem: JDK vendors, Gradle, Maven, Spring Boot CLI, Kotlin — all in one tool. For polyglot (Java + Node + Python + Ruby), consider `asdf` or `mise` instead.

---

## PART 7: Quick Reference

## 57.19 Command cheat sheet

```bash
# ─── INSTALL / UNINSTALL ───
sdk install java 21.0.3-tem       # install specific version
sdk install java 21-tem           # install latest 21.x (short form)
sdk install gradle 8.8            # install Gradle
sdk uninstall java 11.0.23-tem    # remove a version

# ─── SWITCH VERSIONS ───
sdk use java 17.0.11-tem          # switch for this session
sdk default java 21.0.3-tem       # set global default
sdk current                        # show all active versions
sdk current java                   # show active Java

# ─── EXPLORE ───
sdk list java                      # list all available Java versions
sdk list gradle                    # list all available Gradle versions
sdk list                           # list all manageable SDKs (candidates)

# ─── PROJECT ───
sdk env init                       # create .sdkmanrc from current versions
sdk env                            # apply .sdkmanrc in current directory
# (or set sdkman_auto_env=true for automatic)

# ─── MAINTENANCE ───
sdk selfupdate                     # update SDKMAN itself
sdk flush archives                 # delete downloaded archives
sdk flush temp                     # delete temp files
sdk offline enable/disable         # toggle offline mode

# ─── CONFIG ───
sdk config                         # edit SDKMAN config
sdk version                        # show SDKMAN version
sdk help                           # all commands
```

## 57.20 Typical developer setup

```bash
# First-time setup (do this ONCE):
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# Install the essentials:
sdk install java 21.0.3-tem      # latest LTS
sdk install java 17.0.11-tem     # previous LTS (many projects still use this)
sdk install gradle 8.8            # latest Gradle
sdk install maven 3.9.8           # if you use Maven
sdk install kotlin 2.0.0          # if you use Kotlin

# Set defaults:
sdk default java 21.0.3-tem
sdk default gradle 8.8

# Enable auto-switching:
sdk config
# → set sdkman_auto_env=true

# Done! Now every project with .sdkmanrc auto-switches. 🎉
```

---

## Summary

✅ SDKMAN replaces: manual JDK downloads, JAVA_HOME management, jenv, multiple version juggling
✅ Install Java: `sdk install java 21.0.3-tem` (any version, any vendor)
✅ Switch versions: `sdk use` (session) or `sdk default` (global)
✅ Vendors: Temurin (recommended default), Corretto (AWS), GraalVM (native), Oracle, Zulu
✅ Build tools: Gradle, Maven, sbt — all managed alongside Java
✅ Per-project: `.sdkmanrc` file (commit to git — team stays in sync)
✅ Auto-switching: `sdkman_auto_env=true` (cd into project → correct Java activated)
✅ Also manages: Kotlin, Spring Boot CLI, JBang, VisualVM, Scala

## Key takeaways

**SDKMAN is the `nvm` of Java.** One command to install any version, one command to switch, one file (`.sdkmanrc`) to pin per project. The entire team stays in sync by committing `.sdkmanrc` to git.

**Always use LTS versions for production** (currently Java 21, previously 17, 11). Use latest non-LTS (22, 23) only for experimentation. LTS gets security patches for years.

**Temurin is the safe default.** Eclipse Temurin (formerly AdoptOpenJDK) is free, open source, well-tested, and what most companies use. Switch to Corretto for AWS, GraalVM for native images, or Oracle only if you have specific reasons.

**Enable auto-env.** Once `sdkman_auto_env=true` is set, you never think about Java versions again. Walk into a project directory → correct Java is active. Walk out → back to your default. Magic.

---

→ [Back to Chapter 56: uv for Python](./56-UV-PYTHON.md)
