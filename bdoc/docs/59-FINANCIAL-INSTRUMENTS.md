# Chapter 59: Financial Instruments — OTC, NDF, Basis, Overnight Index, Credit Swaps

## What you'll learn

- How financial markets work (exchange vs OTC)
- Over-The-Counter (OTC) trading: what it means and why it exists
- Non-Deliverable Forwards (NDF): currency bets without physical delivery
- Basis trading: profiting from the gap between related instruments
- Overnight Index Swaps (OIS): the benchmark for interest rates
- Credit Default Swaps (CDS): insurance against default
- How these instruments connect to each other in the real world

---

## PART 1: Market Structure

## 59.1 Exchange-traded vs OTC

```
EXCHANGE-TRADED:                       OTC (Over-The-Counter):
┌────────────────────────────┐         ┌────────────────────────────┐
│     EXCHANGE (centralised) │         │   DIRECT (bilateral)       │
│                            │         │                            │
│  Buyer ──► EXCHANGE ◄── Seller       │  Bank A ◄──────────► Bank B │
│            (middleman)     │         │      (negotiate directly)  │
│                            │         │                            │
│  • Standardised contracts  │         │  • Custom terms            │
│  • Public prices           │         │  • Private (no price feed) │
│  • Clearing house (no      │         │  • Counterparty risk       │
│    counterparty risk)      │         │    (what if they don't pay?)│
│  • Regulated               │         │  • Less regulated          │
│  • Small investors OK      │         │  • Institutional only      │
│                            │         │                            │
│  Examples:                 │         │  Examples:                 │
│  • Stock exchange (NYSE)   │         │  • Interest rate swaps     │
│  • Futures (CME)           │         │  • FX forwards / NDF       │
│  • Listed options          │         │  • Credit default swaps    │
└────────────────────────────┘         │  • Exotic derivatives      │
                                       └────────────────────────────┘
```

**Why OTC exists:**
- Banks need CUSTOM contracts (specific amounts, dates, currencies)
- Exchanges only offer standardised products ($100K lots, fixed expiry dates)
- Large institutional trades don't fit exchange "one-size-fits-all" contracts
- Some products are too complex for exchange standardisation

**OTC market size:** ~$600 TRILLION in notional value (dwarfs exchange-traded markets)

## 59.2 Key participants

```
SELL-SIDE (make markets, provide liquidity):
  • Investment banks (Goldman Sachs, JP Morgan, TP ICAP, ICAP)
  • Broker-dealers
  • Inter-dealer brokers (match bank-to-bank trades)

BUY-SIDE (use markets, take positions):
  • Hedge funds
  • Pension funds
  • Asset managers
  • Corporations (hedging business risks)
  • Central banks

INFRASTRUCTURE:
  • Clearing houses (LCH, CME Clearing) — reduce counterparty risk
  • Trade repositories — report OTC trades for regulatory transparency
  • Electronic platforms — move OTC toward electronic execution
```

---

## PART 2: Non-Deliverable Forwards (NDF)

## 59.3 What is an NDF?

An NDF is a **currency forward contract** that settles in cash (usually USD) instead of delivering the actual foreign currency.

```
NORMAL FX FORWARD:
  "I agree to buy 10M Brazilian Real in 3 months at rate 5.20 BRL/USD"
  → In 3 months: I deliver USD, you deliver BRL (physical exchange)

NDF:
  "I agree that the BRL/USD rate in 3 months will be 5.20"
  → In 3 months: compare agreed rate vs actual market rate
  → ONLY THE DIFFERENCE is paid (in USD)
  → No BRL actually changes hands

  Example:
    Agreed rate: 5.20 BRL/USD (notional: $10M)
    Actual rate at expiry: 5.40 BRL/USD (BRL weakened)
    
    Difference: (5.40 - 5.20) / 5.40 × $10M = $37,037
    The seller pays the buyer $37,037 (in USD)
```

## 59.4 Why NDFs exist

```
PROBLEM: Some currencies have capital controls (can't freely move in/out)
  • Chinese Yuan (CNY/CNH)
  • Brazilian Real (BRL)
  • Indian Rupee (INR)
  • Korean Won (KRW)
  • Taiwan Dollar (TWD)

These governments RESTRICT foreign exchange to protect their economy.
You can't just buy $100M of CNY and move it offshore freely.

SOLUTION: NDF settles in USD (or another freely convertible currency).
No restricted currency ever moves. Only the profit/loss settles.

WHO USES NDFs:
  • Corporations hedging revenue in restricted currencies
    ("We'll earn 500M INR next quarter — lock in the USD value now")
  • Hedge funds speculating on EM currency moves
  • Banks making markets for their clients
```

## 59.5 NDF lifecycle

```
DAY 0: TRADE
  Bank A and Bank B agree:
    Currency pair: USD/BRL
    Notional: $10,000,000
    Forward rate: 5.2000
    Fixing date: 3 months from now
    Settlement date: fixing + 2 business days
    Fixing source: PTAX (Brazilian central bank rate)

DAY 90: FIXING
  PTAX publishes: USD/BRL = 5.3500
  
  Settlement amount = Notional × (NDF rate - Fixing rate) / Fixing rate
                    = $10M × (5.2000 - 5.3500) / 5.3500
                    = $10M × (-0.1500 / 5.3500)
                    = -$280,374

  Negative = Bank A pays Bank B $280,374 (BRL weakened, Bank B was right)

DAY 92: SETTLEMENT
  $280,374 transferred via wire (USD — no BRL moves)
```

---

## PART 3: Basis Trading

## 59.6 What is "basis"?

**Basis** = the price difference between two related instruments that SHOULD be similar but aren't exactly the same.

```
BASIS = Instrument A price − Instrument B price

Examples:
  • Cash bond price vs futures price (bond basis)
  • Spot FX rate vs forward FX rate (FX basis)
  • Onshore CNY rate vs offshore CNH rate (CNY/CNH basis)
  • CDS spread vs bond spread (CDS-bond basis)
  • LIBOR vs OIS rate (LIBOR-OIS basis)
  • Cross-currency basis (borrowing in USD vs EUR + swapping)
```

## 59.7 Why basis exists (and why traders care)

```
In a PERFECT market: basis = 0 (instruments are identical in value)
In REALITY: basis ≠ 0 because of:
  • Supply/demand imbalances
  • Credit risk differences
  • Liquidity differences
  • Regulatory costs
  • Market stress (flight to safety widens basis)

BASIS TRADING = bet that the basis will narrow (converge) or widen (diverge)

Example — Bond-Futures Basis:
  US Treasury bond: $101.50
  Treasury futures (equivalent): $101.20
  Basis: $0.30

  Trade: Buy futures + sell bond (or vice versa)
  Profit when: basis narrows to $0.10 → you made $0.20 per unit

This is "relative value" trading — you don't bet on DIRECTION
(will bonds go up or down?). You bet on the RELATIONSHIP between two things.
```

## 59.8 Cross-currency basis (the most important in FX)

```
THE CONCEPT:
  A European bank needs USD to fund USD assets.
  Option A: Borrow USD directly in money markets
  Option B: Borrow EUR (cheap) → swap into USD using FX swap

  If these SHOULD be equivalent, the difference is the cross-currency basis.

  BASIS = FX swap implied USD rate − direct USD borrowing rate

  When basis is NEGATIVE (e.g., EUR/USD basis = -30 bps):
    It costs 30bps MORE to get USD via EUR swap than borrowing directly.
    This means: high demand for USD globally (dollar shortage)

  When basis is NEAR ZERO:
    Markets are balanced. No funding stress.

WHY IT MATTERS:
  • Negative basis = dollar shortage = stress signal
  • Widened during 2008 crisis (banks couldn't get USD — panic)
  • Central banks provide swap lines to reduce basis in crises
  • Traders trade the basis directly as a position
```

---

## PART 4: Overnight Index Swap (OIS)

## 59.9 What is an OIS?

An OIS is an interest rate swap where one leg pays a **fixed rate** and the other pays the **overnight rate compounded daily** over the swap period.

```
STRUCTURE:
  ┌──────────────┐    Fixed rate (e.g., 5.25%)     ┌──────────────┐
  │   Party A    │ ──────────────────────────────► │   Party B    │
  │              │                                  │              │
  │              │ ◄────────────────────────────── │              │
  └──────────────┘   Overnight rate compounded     └──────────────┘
                     (e.g., SOFR average over period)

SETTLEMENT (end of period):
  Fixed payment: Notional × Fixed Rate × Days/360
  Float payment: Notional × Compound(daily overnight rates) × Days/360
  Net: only the DIFFERENCE is exchanged

EXAMPLE:
  Notional: $100M, 1 month, Fixed = 5.25%
  SOFR average (compounded daily): 5.30%

  Fixed pays: $100M × 5.25% × (30/360) = $437,500
  Float pays: $100M × 5.30% × (30/360) = $441,667
  Net: Party A receives $4,167 (float was higher than fixed)
```

## 59.10 Overnight rates (the benchmarks)

| Currency | Overnight Rate | Full Name |
|----------|---------------|-----------|
| USD | **SOFR** | Secured Overnight Financing Rate |
| EUR | **€STR** (ESTER) | Euro Short-Term Rate |
| GBP | **SONIA** | Sterling Overnight Index Average |
| JPY | **TONAR** | Tokyo Overnight Average Rate |
| CHF | **SARON** | Swiss Average Rate Overnight |

These replaced LIBOR (which was discontinued due to manipulation scandal).

```
SOFR: based on ~$1 TRILLION of actual daily repo transactions
  → Very hard to manipulate (based on real trades, not surveys)
  → Published daily by the NY Fed
  → Currently ~5.30% (as of 2024)

LIBOR (the old benchmark — now dead):
  → Based on bank ESTIMATES ("what rate COULD you borrow at?")
  → Easily manipulated (banks lied for profit — Barclays scandal 2012)
  → Discontinued 2023 for most currencies
```

## 59.11 Why OIS matters

```
1. BENCHMARK FOR "RISK-FREE" RATE:
   OIS rate = market's expectation of future central bank rates
   If 1-year OIS is 4.75% and current SOFR is 5.30%
   → Market expects rate CUTS in the next year

2. DISCOUNTING CURVE:
   All derivatives (swaps, options) are valued using OIS discounting
   (replaced LIBOR discounting after 2008 crisis)

3. CREDIT INDICATOR:
   LIBOR-OIS spread (historically): when it widens = bank stress
   2007: spread went from 10bps to 350bps (banks didn't trust each other)

4. HEDGING OVERNIGHT RATE EXPOSURE:
   Money market funds, banks with overnight lending → use OIS to hedge
```

---

## PART 5: Credit Default Swap (CDS)

## 59.12 What is a CDS?

A CDS is **insurance against a borrower defaulting on their debt.**

```
STRUCTURE:
  ┌────────────────┐   Periodic premium (e.g., 100bps/year)   ┌────────────────┐
  │  PROTECTION    │ ──────────────────────────────────────► │  PROTECTION    │
  │  BUYER         │                                          │  SELLER        │
  │  (wants        │ ◄────────────────────────────────────── │  (takes the    │
  │   insurance)   │   IF DEFAULT: pays face value of bond    │   credit risk) │
  └────────────────┘                                          └────────────────┘

ANALOGY: Car insurance
  • You pay a premium (say $1000/year)
  • If your car is destroyed, insurance pays replacement value
  • If nothing happens, you lose the premium (but you slept well)

CDS:
  • You pay a premium (say 100 basis points/year on $10M notional)
  • If the company DEFAULTS, seller pays you $10M (loss recovery)
  • If no default, seller keeps all your premium payments

EXAMPLE:
  Buy protection on $10M of Tesla bonds, 5 years, at 150bps annually
  Annual premium: $10M × 1.50% = $150,000/year
  Total premium over 5 years: $750,000
  
  If Tesla defaults in year 3:
    Recovery rate: 40% (you'd get back 40 cents per dollar from bankruptcy)
    CDS payout: $10M × (1 - 40%) = $6,000,000
    Your net gain: $6M - $450K (premiums paid for 3 years) = $5.55M

  If Tesla doesn't default:
    You paid $750K total for peace of mind (or speculation). Lost.
```

## 59.13 Who uses CDS and why

```
1. HEDGING (the original purpose):
   "I own $50M of Ford bonds. I'm worried Ford might default."
   → Buy CDS on Ford. If Ford defaults, CDS pays out → offsets bond loss.
   → If Ford is fine, bond pays interest, CDS premium is the cost of insurance.

2. SPECULATION (most of the market):
   "I think Company X is going bankrupt but I don't own their bonds."
   → Buy CDS (naked protection) — profit if they default.
   → This is controversial: betting on someone's failure.

3. EXPRESSING CREDIT VIEW WITHOUT BUYING BONDS:
   "I think Ford's creditworthiness is IMPROVING."
   → SELL CDS (collect premium). If Ford improves, CDS spread narrows →
     you can close at a profit (buy back cheaper).

4. INDEX TRADING (most liquid):
   CDX.NA.IG: index of 125 investment-grade North American names
   iTraxx Europe: index of 125 European investment-grade names
   → Trade the "average" credit risk of an entire market segment
```

## 59.14 CDS spread — what it tells you

```
CDS SPREAD = annual premium to insure $10M of debt (in basis points)

  30-50 bps:   Very safe (Apple, Microsoft, US Government)
  100-200 bps: Normal corporate (Ford, AT&T)
  300-500 bps: Stressed / high-yield (BB rated)
  500-1000 bps: Distressed (likely to restructure)
  1000+ bps:   Market expects default (implied default probability > 30%)

READING MARKET SIGNALS:
  Tesla CDS widens from 100bps to 300bps → market thinks Tesla's credit is deteriorating
  Italy sovereign CDS widens → market worried about Italian government debt

THE 2008 CONNECTION:
  • Banks sold CDS on mortgage-backed securities (thought housing was safe)
  • Housing collapsed → all those CDS triggered → sellers owed TRILLIONS
  • AIG sold $500B of CDS without enough capital to pay claims
  • Government bailed out AIG for $182B (largest bailout in history)
  • Lesson: CDS sellers need enough capital (collateral) to pay if triggered
```

## 59.15 Credit events (what triggers a CDS payout)

```
A CDS pays out when a "credit event" occurs:

1. FAILURE TO PAY: borrower misses an interest or principal payment
2. BANKRUPTCY: borrower files for bankruptcy protection
3. RESTRUCTURING: borrower changes terms (extend maturity, reduce coupon)
   → sometimes controversial (is it really a "default" if they negotiate?)

Determined by: ISDA Determinations Committee (group of dealers who vote)
Settlement: usually "auction settlement" — ISDA runs an auction to determine
            the recovery rate, then CDS pays (1 - recovery) × notional.
```

---

## PART 6: How They All Connect

## 59.16 The web of relationships

```
                    Central Bank sets overnight rate (SOFR)
                              │
                              ▼
                 ┌─────────── OIS ──────────┐
                 │ (market's expectation     │
                 │  of future rates)         │
                 ▼                           ▼
        INTEREST RATE SWAPS          FX FORWARDS / NDF
        (fixed vs float)             (future exchange rate)
                 │                           │
                 │                           ▼
                 │                  CROSS-CURRENCY BASIS
                 │                  (cost of swapping one
                 │                   currency for another)
                 ▼
          BOND PRICING                       │
          (discounted at OIS)                │
                 │                           │
                 ▼                           ▼
              CDS SPREAD            FX CARRY TRADES
          (cost of insuring         (borrow low-rate currency,
           against default)          invest in high-rate)
                 │
                 ▼
          BASIS TRADES
          (CDS vs Bond spread,
           cross-currency basis)

EVERYTHING IS CONNECTED:
  • If the Fed raises rates → SOFR rises → OIS rates rise → all swaps reprice
  • If USD funding gets tight → cross-currency basis widens → NDF rates move
  • If a company's credit deteriorates → CDS widens → bond prices fall
  • If EM currency weakens → NDF settlement amounts change → basis shifts
```

## 59.17 Key metrics traders watch

| Metric | What it signals | Normal | Stressed |
|--------|----------------|--------|----------|
| OIS rate vs central bank rate | Market's rate expectations | Close (±10bps) | Divergent (cuts/hikes priced) |
| SOFR-OIS spread | Money market stress | ~0 bps | > 20 bps |
| Cross-currency basis (EUR/USD) | Dollar funding pressure | -5 to -20 bps | < -50 bps |
| CDX.NA.IG spread | US corporate credit health | 50-80 bps | > 150 bps |
| VIX (equity volatility) | Overall market fear | 12-20 | > 30 |
| NDF implied rate vs spot | EM currency stress | Small gap | Large gap (capital flight) |

---

## Summary

✅ OTC vs Exchange: OTC is bilateral, custom, institutional; exchange is standardised, public, cleared
✅ NDF: currency forward settled in cash (for restricted currencies — CNY, BRL, INR, KRW)
✅ Basis: price gap between related instruments — trades on convergence/divergence
✅ Cross-currency basis: cost of converting one currency to another via swaps (negative = dollar shortage)
✅ OIS: fixed rate vs compounded overnight rate — benchmark for risk-free rates, replaced LIBOR
✅ SOFR/€STR/SONIA: overnight benchmarks based on real transactions (not estimates like LIBOR)
✅ CDS: insurance against debt default — pay premium, receive payout on credit event
✅ CDS spread: market price of credit risk (30bps = safe, 1000bps = near default)
✅ Everything connects: central bank rate → OIS → swaps → bonds → CDS → basis

## Key takeaways

**OTC markets are where the real size lives.** $600 trillion notional in OTC derivatives dwarfs stock markets. Every large corporation, bank, and institution uses OTC products to manage risk.

**NDFs solve a real problem.** When countries restrict currency movement, NDFs let international businesses hedge their exposure without moving the restricted currency. It's financial engineering around regulatory walls.

**Basis is the language of relative value.** Professional traders rarely bet on absolute direction ("will rates go up?"). They bet on relationships ("will the gap between these two rates narrow?"). Basis trades are lower-risk because both legs move similarly — you only need the DIFFERENCE to change.

**CDS is a thermometer for credit health.** When CDS spreads widen, the market is saying "this company/country is getting riskier." It's one of the fastest-moving indicators of credit stress — often moving before bond prices or credit ratings.

---

→ [Back to Chapter 58: QR Codes](./58-QR-CODES.md)
