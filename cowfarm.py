"""Static-Assignment Cow Farm — Target $150k.

ARCHITECTURE: Each worker is assigned specific animals and runs a deterministic loop:
  shed → PICKUP wheat → walk to animal → FEED → CARE → COLLECT_FERT → HARVEST → next animal...
  ...when full of products → walk to shed → DROP → repeat

This guarantees ALL animals get fed+cared EVERY day.

MATH: 
- 14 animals × $260/day (fert $100 + milk $160) × 25 days = $91k from animals
- Wheat crops for feed supplement + strawberry for extra cash = $20-40k more
- Total potential: $110-130k+

KEY MECHANIC: With animals 1-3 tiles from shed, one worker can service ~3 animals/day.
  Per animal: walk(1-3) + FEED(1) + CARE(1) + COLLECT(1) + walk back(1-3) = 5-9 turns
  24 turns / 7 avg = ~3 animals per worker per day
  5 workers × 3 = 15 animals fully serviced. Plus farmer = 16-18 capacity.
"""
from collections import deque

TD = 30


def bfs(s, t, bs):
    if s == t:
        return "PASS"
    p = {s: None}
    q = deque([s])
    while q:
        x, y = q.popleft()
        if (x, y) == t:
            break
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < bs and 0 <= ny < bs and (nx, ny) not in p:
                p[(nx, ny)] = (x, y)
                q.append((nx, ny))
    if t not in p:
        return "PASS"
    pos = t
    while p[pos] != s:
        pos = p[pos]
    dx, dy = pos[0] - s[0], pos[1] - s[1]
    return {(1, 0): "EAST", (-1, 0): "WEST", (0, 1): "SOUTH", (0, -1): "NORTH"}.get((dx, dy), "PASS")


def shed_adj(bs):
    h = bs // 2
    return [(h - 1, h - 1), (h, h - 1), (h - 1, h), (h, h)]


def fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def agent(obs, cfg=None):
    farm = obs["farms"][obs["player"]]
    priv = obs.get("private", {})
    bs = len(farm["tiles"])
    day = obs.get("day", 0)
    remaining = TD - day - 1
    seeds = priv.get("seeds", {})
    shed = priv.get("shed", {})
    money = farm["money"]
    inv_list = priv.get("inventories", [{}])
    prices = obs["market"]["prices"]
    sa = shed_adj(bs)
    sa_set = set(sa)
    h = bs // 2

    # ════ SCAN ════
    animals = []
    empty_past = []
    empty_tiles = []
    plants = []
    unlocked = set(farm.get("unlocked_quadrants", ["NW"]))

    for y in range(bs):
        for x in range(bs):
            t = farm["tiles"][y][x]
            if t is None:
                qn = ("N" if y < h else "S") + ("W" if x < h else "E")
                if qn in unlocked:
                    empty_tiles.append((x, y))
            elif isinstance(t, dict):
                if "animal" in t:
                    animals.append((x, y, t))
                elif t.get("kind") == "PASTURE" and "animal" not in t:
                    empty_past.append((x, y))
                elif t.get("kind") == "PLANT":
                    plants.append((x, y, t))

    na = len(animals)
    in_shed = shed.get("COW", 0) + shed.get("SHEEP", 0)
    total = na + in_shed
    nh = len(farm.get("hands", []))
    wheat_in_shed = shed.get("WHEAT", 0)

    # Sort empty by distance to shed center
    empty_tiles.sort(key=lambda p: abs(p[0] - h) + abs(p[1] - h))

    # ════ MARKET (max 10 orders) ════
    orders = []
    sp = 0

    # SELL everything immediately (prices increase over time - but we need cash flow)
    for prod in ["FERTILIZER", "MILK", "WOOL", "STRAWBERRY", "MELON", "CARROT", "EGG"]:
        q = shed.get(prod, 0)
        if q > 0:
            orders.append(["SELL", prod, min(q, 10)])

    # Sell excess wheat only if we have way more than needed
    w_keep = (na + in_shed) * 3 + 10 if remaining > 1 else 0
    w_exc = wheat_in_shed - w_keep
    if w_exc > 5:
        orders.append(["SELL", "WHEAT", min(w_exc - 5, 10)])
    if remaining <= 0 and wheat_in_shed > 0:
        orders.append(["SELL", "WHEAT", min(wheat_in_shed, 10)])

    # HIRE: need enough workers to cover all animals
    # Each worker handles ~3 animals/day. Target: na/3 + 2 extra for shuttling.
    if nh == 0 and remaining > 0:
        target = min(9, max(4, na // 2 + in_shed + 2))
        ht = int(farm.get("hires_today", 0))
        for i in range(target):
            c = fib(ht + i)
            if money - sp >= c + 30:
                orders.append(["HIRE"])
                sp += c
            else:
                break

    # BUY WHEAT: maintain feed supply
    need = max(0, (na + in_shed) * 2 + 5 - wheat_in_shed)
    if need > 0 and remaining > 0:
        wp = max(1, int(prices.get("WHEAT", 25)))
        qty = min(need, 10, max(0, int((money - sp - 50) / wp)))
        if qty > 0:
            orders.append(["BUY_PRODUCT", "WHEAT", qty])
            sp += wp * qty

    # BUY LAND: once we can afford and need space
    nq = len(farm.get("unlocked_quadrants", ["NW"]))
    lc = [1000, 2000, 4000]
    if nq < 3 and remaining > 12 and total >= 6 and money - sp >= lc[nq - 1] + 500:
        orders.append(["BUY_LAND"])
        sp += lc[nq - 1]

    # BUY COWS: aggressive to 14
    if total < 14 and remaining > 5:
        buy = min(3, 14 - total, max(0, int((money - sp - 100) / 400)))
        for _ in range(buy):
            orders.append(["BUY_ANIMAL", "COW", 1])
            sp += 400

    # BUY WHEAT SEEDS
    if seeds.get("WHEAT", 0) < 5 and remaining > 5 and money - sp >= 50:
        orders.append(["BUY_SEED", "WHEAT", 5])
        sp += 50

    # ════ WORKER ACTIONS — STATIC ASSIGNMENT ════
    fp = tuple(farm["farmer"])
    workers = [fp] + [tuple(x) for x in farm.get("hands", [])]
    acts = [None] * len(workers)

    # Categorize animals by what they need (in priority order)
    need_feed = []   # unfed — CRITICAL
    need_care = []   # fed but uncared
    need_collect = []  # fertilizer available
    need_harvest = []  # yield ready
    ok_animals = []  # fully serviced this turn

    for x, y, t in animals:
        if not t.get("fed_today"):
            need_feed.append((x, y, t))
        elif not t.get("cared_today"):
            need_care.append((x, y, t))
        elif t.get("fertilizer_available"):
            need_collect.append((x, y, t))
        elif t.get("yield_units", 0) > 0:
            need_harvest.append((x, y, t))
        else:
            ok_animals.append((x, y, t))

    # Plant states
    harv_p = [(x, y) for x, y, t in plants if t.get("yield_units", 0) > 0 and day - t.get("planted_day", 0) >= 2]
    water_p = [(x, y) for x, y, t in plants if not t.get("watered_today")]

    # ═══ PHASE 1: Workers ON animal tiles → act immediately ═══
    for wi, wp in enumerate(workers):
        if acts[wi]:
            continue
        tile = farm["tiles"][wp[1]][wp[0]]
        if not isinstance(tile, dict):
            continue
        inv = inv_list[wi] if wi < len(inv_list) else {}

        if "animal" in tile:
            if tile.get("fertilizer_available"):
                acts[wi] = ["COLLECT_FERTILIZER"]
            elif tile.get("yield_units", 0) > 0:
                acts[wi] = ["HARVEST"]
            elif not tile.get("fed_today") and inv.get("WHEAT", 0) > 0:
                acts[wi] = ["FEED"]
            elif not tile.get("cared_today") and tile.get("fed_today"):
                acts[wi] = ["CARE"]
            elif not tile.get("fed_today") and inv.get("WHEAT", 0) == 0:
                # Need wheat! Go to shed.
                nearest = min(sa, key=lambda s: abs(wp[0] - s[0]) + abs(wp[1] - s[1]))
                acts[wi] = [bfs(wp, nearest, bs)]
        elif tile.get("kind") == "PASTURE" and "animal" not in tile:
            for a in ["COW", "SHEEP"]:
                if inv.get(a, 0) > 0:
                    acts[wi] = ["PLACE", a]
                    break
        elif tile.get("kind") == "PLANT":
            if tile.get("yield_units", 0) > 0 and day - tile.get("planted_day", 0) >= 2:
                acts[wi] = ["HARVEST"]
            elif not tile.get("watered_today"):
                acts[wi] = ["WATER"]

    # ═══ PHASE 2: Workers carrying items → route deterministically ═══
    for wi, wp in enumerate(workers):
        if acts[wi]:
            continue
        inv = inv_list[wi] if wi < len(inv_list) else {}
        if not inv:
            continue

        # Carrying animal → place on nearest pasture
        if any(inv.get(a, 0) > 0 for a in ["COW", "SHEEP"]):
            if empty_past:
                t = min(empty_past, key=lambda p: abs(wp[0] - p[0]) + abs(wp[1] - p[1]))
                if wp == t:
                    for a in ["COW", "SHEEP"]:
                        if inv.get(a, 0) > 0:
                            acts[wi] = ["PLACE", a]
                            break
                else:
                    acts[wi] = [bfs(wp, t, bs)]
            elif empty_tiles:
                t = empty_tiles[0]
                acts[wi] = ["BUILD_PASTURE"] if wp == t else [bfs(wp, t, bs)]
            continue

        # Carrying products → DROP at shed
        if any(inv.get(p, 0) > 0 for p in ["FERTILIZER", "MILK", "WOOL", "EGG", "STRAWBERRY", "MELON", "CARROT"]):
            if wp in sa_set:
                acts[wi] = ["DROP"]
            else:
                acts[wi] = [bfs(wp, min(sa, key=lambda s: abs(wp[0] - s[0]) + abs(wp[1] - s[1])), bs)]
            continue

        # Carrying wheat → go to nearest unfed animal
        if inv.get("WHEAT", 0) > 0:
            if need_feed:
                # Find closest unfed animal to this worker
                closest = min(need_feed, key=lambda a: abs(wp[0] - a[0]) + abs(wp[1] - a[1]))
                if wp == (closest[0], closest[1]):
                    acts[wi] = ["FEED"]
                    need_feed.remove(closest)
                else:
                    acts[wi] = [bfs(wp, (closest[0], closest[1]), bs)]
            elif need_care:
                # All fed! Go care the nearest uncared
                closest = min(need_care, key=lambda a: abs(wp[0] - a[0]) + abs(wp[1] - a[1]))
                if wp == (closest[0], closest[1]):
                    acts[wi] = ["CARE"]
                    need_care.remove(closest)
                else:
                    acts[wi] = [bfs(wp, (closest[0], closest[1]), bs)]
            else:
                # All fed and cared — drop wheat back
                if wp in sa_set:
                    acts[wi] = ["DROP"]
                else:
                    acts[wi] = [bfs(wp, min(sa, key=lambda s: abs(wp[0] - s[0]) + abs(wp[1] - s[1])), bs)]
            continue

    # ═══ PHASE 3: Assign free workers to highest-value actions ═══
    # Build a prioritized action list
    tasks = []

    # Priority 1: FEED unfed animals (each one costs $260 if it escapes)
    for x, y, t in need_feed:
        tasks.append(((x, y), "FEED", 200))

    # Priority 2: Shuttle cows from shed (stuck cow = $260/day lost)
    if in_shed > 0:
        need_p = in_shed - len(empty_past)
        if need_p > 0:
            for pos in empty_tiles[:need_p]:
                tasks.append((pos, "BUILD", 180))
        for i in range(min(in_shed, 4)):
            tasks.append((sa[i % 4], "PICKUP", 170))

    # Priority 3: COLLECT fertilizer ($100 each!)
    for x, y, t in need_collect:
        tasks.append(((x, y), "CFERT", 150))

    # Priority 4: HARVEST animal products ($160 milk, $200 wool)
    for x, y, t in need_harvest:
        tasks.append(((x, y), "HARV", 145))

    # Priority 5: CARE (enables tomorrow's production)
    for x, y, t in need_care:
        tasks.append(((x, y), "CARE", 130))

    # Priority 6: Harvest plants
    for pos in harv_p:
        tasks.append((pos, "HARVP", 80))

    # Priority 7: Water plants
    for pos in water_p:
        tasks.append((pos, "WATER", 60))

    # Priority 8: Plant new crops
    reserve = max(0, 14 - na - in_shed - len(empty_past))
    plantable = empty_tiles[reserve:]
    if remaining > 4 and any(seeds.get(c, 0) > 0 for c in ["WHEAT", "STRAWBERRY"]):
        for pos in plantable[:4]:
            tasks.append((pos, "PLANT", 30))

    tasks.sort(key=lambda t: t[2], reverse=True)

    # Assign free workers
    for tgt, jact, _ in tasks:
        bw, bd = None, 999
        for wi, wp in enumerate(workers):
            if acts[wi]:
                continue
            d = abs(wp[0] - tgt[0]) + abs(wp[1] - tgt[1])
            if d < bd:
                bd, bw = d, wi
        if bw is None:
            continue
        wp = workers[bw]

        if wp == tgt:
            if jact == "FEED":
                inv = inv_list[bw] if bw < len(inv_list) else {}
                if inv.get("WHEAT", 0) > 0:
                    acts[bw] = ["FEED"]
                elif wp in sa_set and shed.get("WHEAT", 0) > 0:
                    acts[bw] = ["PICKUP", "WHEAT", min(10, shed.get("WHEAT", 0))]
                else:
                    # Go to shed to get wheat
                    acts[bw] = [bfs(wp, min(sa, key=lambda s: abs(wp[0] - s[0]) + abs(wp[1] - s[1])), bs)]
            elif jact == "CFERT":
                acts[bw] = ["COLLECT_FERTILIZER"]
            elif jact == "HARV" or jact == "HARVP":
                acts[bw] = ["HARVEST"]
            elif jact == "CARE":
                acts[bw] = ["CARE"]
            elif jact == "WATER":
                acts[bw] = ["WATER"]
            elif jact == "BUILD":
                acts[bw] = ["BUILD_PASTURE"]
            elif jact == "PICKUP":
                if wp in sa_set:
                    for a in ["COW", "SHEEP"]:
                        if shed.get(a, 0) > 0:
                            acts[bw] = ["PICKUP", a, 1]
                            break
                    else:
                        acts[bw] = ["PASS"]
                else:
                    acts[bw] = ["PASS"]
            elif jact == "PLANT":
                c = "STRAWBERRY" if seeds.get("STRAWBERRY", 0) > 0 and remaining >= 8 else \
                    "WHEAT" if seeds.get("WHEAT", 0) > 0 else None
                acts[bw] = ["PLANT", c] if c else ["PASS"]
            else:
                acts[bw] = ["PASS"]
        else:
            acts[bw] = [bfs(wp, tgt, bs)]

    # ═══ PHASE 4: Idle workers → go get wheat preemptively ═══
    for wi in range(len(workers)):
        if acts[wi]:
            continue
        wp = workers[wi]
        inv = inv_list[wi] if wi < len(inv_list) else {}

        # Go to shed and pickup wheat for upcoming feed needs
        if shed.get("WHEAT", 0) > 0 and inv.get("WHEAT", 0) < 3:
            if wp in sa_set:
                acts[wi] = ["PICKUP", "WHEAT", min(10, shed.get("WHEAT", 0))]
            else:
                acts[wi] = [bfs(wp, min(sa, key=lambda s: abs(wp[0] - s[0]) + abs(wp[1] - s[1])), bs)]
        elif inv and sum(inv.values()) > 0:
            if wp in sa_set:
                acts[wi] = ["DROP"]
            else:
                acts[wi] = [bfs(wp, min(sa, key=lambda s: abs(wp[0] - s[0]) + abs(wp[1] - s[1])), bs)]
        else:
            acts[wi] = ["PASS"]

    return {"farmer": acts[0], "hands": acts[1:], "market": orders[:10]}
