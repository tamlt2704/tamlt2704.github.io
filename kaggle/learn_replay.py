"""$157k replay-inspired agent: Animals in a LINE for sequential feeding.

KEY INSIGHT: Place cows in a line along y=4 (the shed row).
Workers pickup 10 wheat, walk the line feeding each cow in 1 turn each.
No wasted turns walking back to shed between feeds!

Layout (from $157k replay):
  Row 4: C C C C C C C  (7 cows)
  Row 3:       S S S    (3 sheep near shed)  
  Row 2:          C C   (2 cows at shed corners)
  = 12-14 animals ALL within 0-4 tiles of shed

Pasture build order (close to shed first, then extending the line):
  Phase 1 (day 0): (3,3)(4,3)(3,4)(4,4) — shed-adjacent
  Phase 2 (day 1-4): (2,4)(4,2) — shed ring
  Phase 3 (day 5-7): (5,4)(6,4)(5,3)(5,2) — NE after land buy
  Phase 4 (day 8-11): (7,4)(8,4)(6,3)(7,3) — extend line + fill
"""
from collections import deque

TD = 30

# Pre-computed pasture build order (optimal from replay analysis)
# These are the positions where animals should be placed, in priority order
PASTURE_ORDER = [
    (3, 3), (4, 3), (3, 4), (4, 4),   # Phase 1: shed-adjacent (NW)
    (2, 4), (4, 2), (2, 3),            # Phase 2: shed ring (NW)
    (5, 4), (6, 4), (5, 3), (5, 2),   # Phase 3: after 1st land buy (NE)
    (7, 4), (8, 4), (6, 3), (7, 3),   # Phase 4: after 2nd land buy
    (9, 4), (8, 3), (9, 3),            # Extra if needed
]


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
    occupied = set()
    unlocked = set(farm.get("unlocked_quadrants", ["NW"]))

    for y in range(bs):
        for x in range(bs):
            t = farm["tiles"][y][x]
            if t is None:
                qn = ("N" if y < h else "S") + ("W" if x < h else "E")
                if qn in unlocked:
                    empty_tiles.append((x, y))
            elif isinstance(t, dict):
                occupied.add((x, y))
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
    wheat_s = shed.get("WHEAT", 0)
    nq = len(farm.get("unlocked_quadrants", ["NW"]))

    # Next pasture positions from pre-computed order
    next_pastures = [p for p in PASTURE_ORDER if p not in occupied and p in set(empty_tiles)]

    # Plantable tiles = empty tiles NOT reserved for pastures
    reserved = set(next_pastures[:max(0, 14 - na - in_shed - len(empty_past))])
    plantable = [p for p in empty_tiles if p not in reserved]
    plantable.sort(key=lambda p: abs(p[0] - h) + abs(p[1] - h))

    # ════ MARKET ════
    orders = []
    sp = 0

    # SELL all products
    for prod in ["FERTILIZER", "MILK", "WOOL", "MELON", "STRAWBERRY", "CARROT", "EGG"]:
        q = shed.get(prod, 0)
        if q > 0 and len(orders) < 10:
            orders.append(["SELL", prod, min(q, 10)])
    # Wheat: keep 3-day buffer
    w_keep = (na + in_shed) * 3 + 10
    if wheat_s - w_keep > 5 and len(orders) < 10:
        orders.append(["SELL", "WHEAT", min(wheat_s - w_keep - 5, 10)])
    if remaining <= 0:
        for prod in ["WHEAT", "FERTILIZER", "MILK", "WOOL", "MELON", "STRAWBERRY", "CARROT", "EGG"]:
            q = shed.get(prod, 0)
            if q > 0 and len(orders) < 10:
                orders.append(["SELL", prod, min(q, 10)])
        return {"farmer": ["PASS"], "hands": [["PASS"]] * nh, "market": orders[:10]}

    # HIRE (replay: 5 day0, 0 day1, 4 day2-6, 8 day7, 11-12 day8+)
    if nh == 0:
        target = 5 if day == 0 else (0 if day == 1 else (4 if day < 7 else (8 if day == 7 else 12)))
        ht = int(farm.get("hires_today", 0))
        for i in range(target):
            if len(orders) >= 10:
                break
            c = fib(ht + i)
            if money - sp >= c + 20:
                orders.append(["HIRE"])
                sp += c
            else:
                break

    # BUY WHEAT (feed buffer)
    feed_need = (na + in_shed) * 2 + 6
    deficit = max(0, feed_need - wheat_s)
    if deficit > 0 and len(orders) < 10:
        wp = max(1, int(prices.get("WHEAT", 25)))
        qty = min(deficit, 10, max(0, int((money - sp - 50) / wp)))
        if qty > 0:
            orders.append(["BUY_PRODUCT", "WHEAT", qty])
            sp += wp * qty

    # BUY LAND (day 5+ and day 10+)
    if nq == 1 and day >= 5 and money - sp >= 1200 and len(orders) < 10:
        orders.append(["BUY_LAND"])
        sp += 1000
    elif nq == 2 and day >= 10 and money - sp >= 2200 and len(orders) < 10:
        orders.append(["BUY_LAND"])
        sp += 2000

    # BUY ANIMALS (replay: 2cow+2sheep day0, then 1/day on days 3,5,7,7,9,11)
    if day == 0 and total < 4 and len(orders) < 10:
        if money - sp >= 1800:
            orders.append(["BUY_ANIMAL", "COW", 2])
            sp += 800
            if len(orders) < 10:
                orders.append(["BUY_ANIMAL", "SHEEP", 2])
                sp += 1000
    elif total < 14 and remaining > 5 and len(orders) < 10:
        buy = min(2, 14 - total, max(0, int((money - sp - 100) / 400)))
        for _ in range(buy):
            if len(orders) >= 10:
                break
            orders.append(["BUY_ANIMAL", "COW", 1])
            sp += 400

    # BUY SEEDS (replay: melon+wheat day0, strawberry day5+, wheat throughout)
    if day == 0 and len(orders) < 10:
        if seeds.get("MELON", 0) < 12 and money - sp >= 960:
            orders.append(["BUY_SEED", "MELON", 12])
            sp += 960
        if seeds.get("WHEAT", 0) < 7 and money - sp >= 70 and len(orders) < 10:
            orders.append(["BUY_SEED", "WHEAT", 7])
            sp += 70
    elif len(orders) < 10:
        if seeds.get("WHEAT", 0) < 10 and money - sp >= 100:
            orders.append(["BUY_SEED", "WHEAT", 10])
            sp += 100
        if seeds.get("STRAWBERRY", 0) < 5 and day >= 4 and remaining >= 8 and money - sp >= 500 and len(orders) < 10:
            orders.append(["BUY_SEED", "STRAWBERRY", 5])
            sp += 500

    # ════ WORKERS ════
    fp = tuple(farm["farmer"])
    workers = [fp] + [tuple(x) for x in farm.get("hands", [])]
    acts = [None] * len(workers)

    unfed = [(x, y) for x, y, t in animals if not t.get("fed_today")]
    uncared = [(x, y) for x, y, t in animals if not t.get("cared_today")]
    fert_a = [(x, y) for x, y, t in animals if t.get("fertilizer_available")]
    harv_a = [(x, y) for x, y, t in animals if t.get("yield_units", 0) > 0]
    water_p = [(x, y) for x, y, t in plants if not t.get("watered_today")]
    harv_p = [(x, y) for x, y, t in plants if t.get("yield_units", 0) > 0 and day - t.get("planted_day", 0) >= 2]

    # ═══ IMMEDIATE: act on current tile ═══
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
                if wp in fert_a: fert_a.remove(wp)
            elif tile.get("yield_units", 0) > 0:
                acts[wi] = ["HARVEST"]
                if wp in harv_a: harv_a.remove(wp)
            elif not tile.get("fed_today") and inv.get("WHEAT", 0) > 0:
                acts[wi] = ["FEED"]
                if wp in unfed: unfed.remove(wp)
            elif not tile.get("cared_today") and tile.get("fed_today"):
                acts[wi] = ["CARE"]
                if wp in uncared: uncared.remove(wp)
        elif tile.get("kind") == "PASTURE" and "animal" not in tile:
            for a in ["COW", "SHEEP"]:
                if inv.get(a, 0) > 0:
                    acts[wi] = ["PLACE", a]
                    break
        elif tile.get("kind") == "PLANT":
            if tile.get("yield_units", 0) > 0 and day - tile.get("planted_day", 0) >= 2:
                acts[wi] = ["HARVEST"]
                if wp in harv_p: harv_p.remove(wp)
            elif not tile.get("watered_today"):
                acts[wi] = ["WATER"]
                if wp in water_p: water_p.remove(wp)

    # ═══ CARRY ═══
    for wi, wp in enumerate(workers):
        if acts[wi]:
            continue
        inv = inv_list[wi] if wi < len(inv_list) else {}
        if not inv:
            continue

        if any(inv.get(a, 0) > 0 for a in ["COW", "SHEEP"]):
            # Place on nearest empty pasture, OR build at next pre-computed spot
            if empty_past:
                t = min(empty_past, key=lambda p: abs(wp[0]-p[0])+abs(wp[1]-p[1]))
                if wp == t:
                    for a in ["COW","SHEEP"]:
                        if inv.get(a,0)>0: acts[wi]=["PLACE",a]; break
                else: acts[wi] = [bfs(wp, t, bs)]
            elif next_pastures:
                t = next_pastures[0]
                acts[wi] = ["BUILD_PASTURE"] if wp == t else [bfs(wp, t, bs)]
            continue

        if any(inv.get(p,0)>0 for p in ["FERTILIZER","MILK","WOOL","EGG","STRAWBERRY","MELON","CARROT"]):
            if wp in sa_set: acts[wi] = ["DROP"]
            else: acts[wi] = [bfs(wp, min(sa, key=lambda s: abs(wp[0]-s[0])+abs(wp[1]-s[1])), bs)]
            continue

        # KEY: Worker with wheat walks the animal LINE feeding sequentially!
        if inv.get("WHEAT", 0) > 0:
            if unfed:
                t = min(unfed, key=lambda p: abs(wp[0]-p[0])+abs(wp[1]-p[1]))
                if wp == t: acts[wi] = ["FEED"]; unfed.remove(t)
                else: acts[wi] = [bfs(wp, t, bs)]
            else:
                if wp in sa_set: acts[wi] = ["DROP"]
                else: acts[wi] = [bfs(wp, min(sa, key=lambda s: abs(wp[0]-s[0])+abs(wp[1]-s[1])), bs)]
            continue

    # ═══ JOBS ═══
    jobs = []
    for p in unfed: jobs.append((p, "FEED", 200))

    if in_shed > 0:
        need_p = in_shed - len(empty_past)
        if need_p > 0:
            for pos in next_pastures[:need_p]:
                jobs.append((pos, "BUILD", 170))
        for i in range(min(in_shed, 5)):
            jobs.append((sa[i % 4], "PICKUP", 165))

    for p in fert_a: jobs.append((p, "CFERT", 150))
    for p in harv_a: jobs.append((p, "HARV", 145))
    for p in uncared: jobs.append((p, "CARE", 130))
    for p in harv_p: jobs.append((p, "HARVP", 100))
    for p in water_p: jobs.append((p, "WATER", 90))

    if remaining > 3 and any(seeds.get(c,0)>0 for c in ["WHEAT","MELON","STRAWBERRY"]):
        for pos in plantable[:8]:
            jobs.append((pos, "PLANT", 50))

    jobs.sort(key=lambda j: j[2], reverse=True)

    for tgt, jact, _ in jobs:
        bw, bd = None, 999
        for wi, wp in enumerate(workers):
            if acts[wi]: continue
            d = abs(wp[0]-tgt[0])+abs(wp[1]-tgt[1])
            if d < bd: bd, bw = d, wi
        if bw is None: continue
        wp = workers[bw]

        if wp == tgt:
            if jact == "FEED":
                inv = inv_list[bw] if bw < len(inv_list) else {}
                if inv.get("WHEAT",0)>0: acts[bw] = ["FEED"]
                elif wp in sa_set and wheat_s > 0:
                    acts[bw] = ["PICKUP","WHEAT",min(10, wheat_s)]
                else: acts[bw] = [bfs(wp, min(sa, key=lambda s: abs(wp[0]-s[0])+abs(wp[1]-s[1])), bs)]
            elif jact == "CFERT": acts[bw] = ["COLLECT_FERTILIZER"]
            elif jact in ("HARV","HARVP"): acts[bw] = ["HARVEST"]
            elif jact == "CARE": acts[bw] = ["CARE"]
            elif jact == "WATER": acts[bw] = ["WATER"]
            elif jact == "BUILD": acts[bw] = ["BUILD_PASTURE"]
            elif jact == "PICKUP":
                if wp in sa_set:
                    for a in ["COW","SHEEP"]:
                        if shed.get(a,0)>0: acts[bw]=["PICKUP",a,1]; break
                    else: acts[bw] = ["PASS"]
                else: acts[bw] = ["PASS"]
            elif jact == "PLANT":
                c = "MELON" if seeds.get("MELON",0)>0 and remaining>=13 else \
                    "STRAWBERRY" if seeds.get("STRAWBERRY",0)>0 and remaining>=8 else \
                    "WHEAT" if seeds.get("WHEAT",0)>0 else None
                acts[bw] = ["PLANT",c] if c else ["PASS"]
            else: acts[bw] = ["PASS"]
        else:
            acts[bw] = [bfs(wp, tgt, bs)]

    # ═══ IDLE: pickup wheat ═══
    for wi in range(len(workers)):
        if acts[wi]: continue
        wp = workers[wi]
        inv = inv_list[wi] if wi < len(inv_list) else {}
        if wheat_s > 0 and inv.get("WHEAT",0) < 3:
            if wp in sa_set: acts[wi] = ["PICKUP","WHEAT",min(10, wheat_s)]
            else: acts[wi] = [bfs(wp, min(sa, key=lambda s: abs(wp[0]-s[0])+abs(wp[1]-s[1])), bs)]
        elif inv and sum(inv.values()) > 0:
            if wp in sa_set: acts[wi] = ["DROP"]
            else: acts[wi] = [bfs(wp, min(sa, key=lambda s: abs(wp[0]-s[0])+abs(wp[1]-s[1])), bs)]
        else: acts[wi] = ["PASS"]

    return {"farmer": acts[0], "hands": acts[1:], "market": orders[:10]}
