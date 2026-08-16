"""State-machine agent: scripted setup → daily FEED/CARE/COLLECT/SELL loop.
720 turns. Only final money matters. Go broke early, compound to win at turn 720.

Phase 1 (Day 0, turns 0-23): Buy cows, build pastures at shed-adj, place animals
Phase 2 (Day 1+): Daily loop: hire hands, buy wheat, FEED+CARE+COLLECT, sell fertilizer
"""
from collections import deque

TD, TPD = 30, 24

def bfs(s, t, bs):
    if s == t: return "PASS"
    p = {s: None}; q = deque([s])
    while q:
        x, y = q.popleft()
        if (x,y) == t: break
        for dx,dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<bs and 0<=ny<bs and (nx,ny) not in p:
                p[(nx,ny)] = (x,y); q.append((nx,ny))
    if t not in p: return "PASS"
    pos = t
    while p[pos] != s: pos = p[pos]
    dx, dy = pos[0]-s[0], pos[1]-s[1]
    return "EAST" if dx==1 else "WEST" if dx==-1 else "SOUTH" if dy==1 else "NORTH" if dy==-1 else "PASS"

def shed_adj(bs):
    h = bs//2; return [(h-1,h-1),(h,h-1),(h-1,h),(h,h)]

def _fib(n):
    a, b = 1, 1
    for _ in range(n): a, b = b, a + b
    return a

def agent(obs, cfg=None):
    farm = obs["farms"][obs["player"]]
    priv = obs.get("private", {})
    bs = len(farm["tiles"])
    day = obs.get("day", 0); hour = obs.get("hour", 0)
    remaining = TD - day - 1
    seeds = priv.get("seeds", {}); shed = priv.get("shed", {})
    money = farm["money"]; nh = len(farm.get("hands", []))
    inv_list = priv.get("inventories", [{}])
    prices = obs["market"]["prices"]
    sa_list = shed_adj(bs); sa = set(sa_list)

    # Scan farm
    animals = []; empty_pastures = []; empty_tiles = []
    for y in range(bs):
        for x in range(bs):
            t = farm["tiles"][y][x]
            if t is None: empty_tiles.append((x,y))
            elif isinstance(t, dict):
                if "animal" in t: animals.append((x,y,t))
                elif t.get("kind") == "PASTURE" and "animal" not in t:
                    empty_pastures.append((x,y))

    na = len(animals)
    cows_s = shed.get("COW", 0) + shed.get("SHEEP", 0)

    # ═══ MARKET ORDERS ═══
    orders = []; spent = 0

    # SELL everything valuable (fert is #1, then animal products, then crops)
    wheat_keep = na + 3
    for product in ["FERTILIZER","WOOL","MILK","STRAWBERRY","MELON","CARROT","WHEAT"]:
        qty = shed.get(product, 0)
        if product == "WHEAT": qty = max(0, qty - wheat_keep)
        if qty > 0: orders.append(["SELL", product, min(qty, 10)])

    # HIRE: every day, as many as we can afford and need
    if nh == 0 and remaining > 0:
        target = max(3, min(7, na + cows_s + 2))
        ht = int(farm.get("hires_today", 0))
        for h in range(target):
            f = _fib(ht + h)
            if money - spent >= f:
                orders.append(["HIRE"]); spent += f
            else: break

    # BUY WHEAT for feeding (critical — always keep buffer)
    wheat_have = shed.get("WHEAT", 0)
    need = max(0, (na + cows_s) * 2 - wheat_have)
    if need > 0:
        wp = max(1, int(prices.get("WHEAT", 25)))
        affordable = min(need, 10, int((money - spent) // wp)) if wp > 0 else 0
        if affordable > 0:
            orders.append(["BUY_PRODUCT", "WHEAT", affordable]); spent += wp * affordable

    # BUY ANIMALS: only if we have time for ROI and shed is mostly empty
    if cows_s <= 1 and remaining > 6 and na < 14:
        max_buy = 3 if day < 2 else 2 if day < 10 else 1
        for _ in range(max_buy):
            if money - spent >= 400:
                orders.append(["BUY_ANIMAL", "COW", 1]); spent += 400

    # BUY WHEAT SEEDS for growing (supplement market wheat)
    if seeds.get("WHEAT", 0) < 3 and len(empty_tiles) > na + 3 and money - spent >= 30:
        orders.append(["BUY_SEED", "WHEAT", 3]); spent += 30

    # ═══ WORKER ACTIONS ═══
    farmer_pos = tuple(farm["farmer"])
    workers = [farmer_pos] + [tuple(h) for h in farm.get("hands", [])]
    actions = [None] * len(workers)

    # Categorize animals by state
    unfed = [(x,y) for x,y,t in animals if not t.get("fed_today")]
    uncared = [(x,y) for x,y,t in animals if not t.get("cared_today")]
    fert_avail = [(x,y) for x,y,t in animals if t.get("fertilizer_available")]
    harvestable = [(x,y) for x,y,t in animals if t.get("yield_units",0) > 0]

    # ═══ IMMEDIATE ACTIONS: workers ON animal/pasture tiles act NOW ═══
    for wi, wp in enumerate(workers):
        if actions[wi] is not None: continue
        tx, ty = wp
        tile = farm["tiles"][ty][tx]
        if not isinstance(tile, dict): continue
        inv = inv_list[wi] if wi < len(inv_list) else {}

        # On an animal tile: COLLECT > FEED > CARE > HARVEST (in priority order)
        if "animal" in tile:
            if tile.get("fertilizer_available"):
                actions[wi] = ["COLLECT_FERTILIZER"]
                if (tx,ty) in fert_avail: fert_avail.remove((tx,ty))
            elif tile.get("yield_units", 0) > 0:
                actions[wi] = ["HARVEST"]
                if (tx,ty) in harvestable: harvestable.remove((tx,ty))
            elif not tile.get("fed_today") and inv.get("WHEAT", 0) > 0:
                actions[wi] = ["FEED"]
                if (tx,ty) in unfed: unfed.remove((tx,ty))
            elif not tile.get("cared_today") and tile.get("fed_today"):
                actions[wi] = ["CARE"]
                if (tx,ty) in uncared: uncared.remove((tx,ty))

        # On empty pasture with animal in inventory: PLACE
        elif tile.get("kind") == "PASTURE" and "animal" not in tile:
            for a in ["COW","SHEEP"]:
                if inv.get(a, 0) > 0:
                    actions[wi] = ["PLACE", a]; break

    # Workers carrying fertilizer → drop at shed
    for wi, wp in enumerate(workers):
        if actions[wi] is not None: continue
        inv = inv_list[wi] if wi < len(inv_list) else {}
        if inv.get("FERTILIZER", 0) > 0:
            if tuple(wp) in sa:
                actions[wi] = ["DROP"]
            else:
                nearest = min(sa_list, key=lambda s: abs(wp[0]-s[0])+abs(wp[1]-s[1]))
                actions[wi] = [bfs(wp, nearest, bs)]

    # Build a flat job queue: each job = (x, y, action, priority)
    jobs = []

    # TOP PRIORITY: Get animals from shed onto pastures (the whole point!)
    # This is a multi-step chain: worker needs to be at shed → PICKUP → walk to pasture → PLACE
    # We handle this as the FIRST thing — redirect idle workers before other jobs
    if cows_s > 0 and (empty_pastures or empty_tiles):
        targets = list(empty_pastures)  # existing pastures first
        # If not enough pastures, plan to build on nearest empty tiles
        if len(targets) < cows_s:
            sc = (bs//2, bs//2)
            extras = sorted([t for t in empty_tiles if t not in targets],
                           key=lambda p: abs(p[0]-sc[0])+abs(p[1]-sc[1]))
            targets.extend(extras[:cows_s - len(targets)])

        for tx, ty in targets[:cows_s]:
            jobs.append((tx, ty, "SETUP_ANIMAL", 110))  # Higher than everything!

    # Animals in shed need: BUILD_PASTURE → PICKUP → PLACE (3-step per animal)
    # Workers carrying animals need to PLACE them
    for wi, wp in enumerate(workers):
        if wi >= len(inv_list): continue
        inv = inv_list[wi]
        if not inv: continue
        # Carrying a cow/sheep? → Find nearest empty pasture or build one
        for a in ["COW", "SHEEP"]:
            if inv.get(a, 0) > 0:
                # Am I on an empty pasture? PLACE!
                tile = farm["tiles"][wp[1]][wp[0]]
                if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and "animal" not in tile:
                    actions[wi] = ["PLACE", a]
                elif empty_pastures:
                    # Go to nearest empty pasture
                    nearest = min(empty_pastures, key=lambda p: abs(wp[0]-p[0])+abs(wp[1]-p[1]))
                    actions[wi] = [bfs(wp, nearest, bs)]
                elif empty_tiles:
                    # No pastures — build one. Go to nearest empty tile.
                    nearest = min(empty_tiles, key=lambda p: abs(wp[0]-p[0])+abs(wp[1]-p[1]))
                    if wp == nearest:
                        actions[wi] = ["BUILD_PASTURE"]
                    else:
                        actions[wi] = [bfs(wp, nearest, bs)]
                break
        # Carrying wheat? → Go feed nearest unfed animal
        if actions[wi] is None and inv.get("WHEAT", 0) > 0 and unfed:
            nearest = min(unfed, key=lambda p: abs(wp[0]-p[0])+abs(wp[1]-p[1]))
            if wp == nearest:
                actions[wi] = ["FEED"]
                unfed.remove(nearest)
            else:
                actions[wi] = [bfs(wp, nearest, bs)]
        # Carrying fertilizer? → Go to shed to drop
        if actions[wi] is None and inv.get("FERTILIZER", 0) > 0:
            if tuple(wp) in sa:
                actions[wi] = ["DROP"]
            else:
                nearest = min(sa_list, key=lambda s: abs(wp[0]-s[0])+abs(wp[1]-s[1]))
                actions[wi] = [bfs(wp, nearest, bs)]

    # Remaining workers: assign to priority jobs
    # Priority: COLLECT_FERT > HARVEST > FEED > CARE > PLACE > BUILD > PLANT
    for x,y in fert_avail: jobs.append((x,y,"COLLECT_FERTILIZER",100))
    for x,y in harvestable: jobs.append((x,y,"HARVEST",95))
    for x,y in unfed: jobs.append((x,y,"FEED",92))
    for x,y in uncared: jobs.append((x,y,"CARE",85))
    # Place animals from shed
    if cows_s > 0:
        for x,y in empty_pastures: jobs.append((x,y,"PICKUP_AND_PLACE",80))
        # Build pastures near shed if needed
        if not empty_pastures:
            near = sorted(empty_tiles, key=lambda p: abs(p[0]-bs//2)+abs(p[1]-bs//2))
            for x,y in near[:cows_s]: jobs.append((x,y,"BUILD_PASTURE",78))
    # Plant wheat on spare tiles
    if seeds.get("WHEAT",0) > 0:
        sc = (bs//2, bs//2)
        spare = sorted(empty_tiles, key=lambda p: abs(p[0]-sc[0])+abs(p[1]-sc[1]))
        for x,y in spare[cows_s:cows_s+5]:  # Skip tiles reserved for pastures
            jobs.append((x,y,"PLANT",40))
    # Water/harvest existing wheat
    for y in range(bs):
        for x in range(bs):
            t = farm["tiles"][y][x]
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                if t.get("yield_units",0)>0 and day-t.get("planted_day",0)>=2:
                    jobs.append((x,y,"HARVEST_P",70))
                elif not t.get("watered_today"):
                    jobs.append((x,y,"WATER",60))

    jobs.sort(key=lambda j: j[3], reverse=True)

    # Assign free workers to jobs
    for jx, jy, jact, jprio in jobs:
        best_w, best_d = None, 999
        for wi, wp in enumerate(workers):
            if actions[wi] is not None: continue
            d = abs(wp[0]-jx)+abs(wp[1]-jy)
            if d < best_d: best_d, best_w = d, wi
        if best_w is None: continue
        wp = workers[best_w]

        if wp == (jx, jy):
            if jact == "COLLECT_FERTILIZER": actions[best_w] = ["COLLECT_FERTILIZER"]
            elif jact == "HARVEST" or jact == "HARVEST_P": actions[best_w] = ["HARVEST"]
            elif jact == "FEED":
                inv = inv_list[best_w] if best_w < len(inv_list) else {}
                if inv.get("WHEAT",0) > 0:
                    actions[best_w] = ["FEED"]
                elif shed.get("WHEAT",0) > 0 and tuple(wp) in sa:
                    actions[best_w] = ["PICKUP", "WHEAT", 5]
                else:
                    nearest = min(sa_list, key=lambda s: abs(wp[0]-s[0])+abs(wp[1]-s[1]))
                    actions[best_w] = [bfs(wp, nearest, bs)]
            elif jact == "CARE": actions[best_w] = ["CARE"]
            elif jact == "WATER": actions[best_w] = ["WATER"]
            elif jact == "BUILD_PASTURE": actions[best_w] = ["BUILD_PASTURE"]
            elif jact == "PICKUP_AND_PLACE":
                # Standing on empty pasture — need to pickup animal from shed
                if tuple(wp) in sa and cows_s > 0:
                    for a in ["COW","SHEEP"]:
                        if shed.get(a,0) > 0:
                            actions[best_w] = ["PICKUP", a, 1]; break
                else:
                    nearest = min(sa_list, key=lambda s: abs(wp[0]-s[0])+abs(wp[1]-s[1]))
                    actions[best_w] = [bfs(wp, nearest, bs)]
            elif jact == "SETUP_ANIMAL":
                # Multi-step: build pasture if needed, pickup cow, place
                tile = farm["tiles"][jy][jx]
                inv = inv_list[best_w] if best_w < len(inv_list) else {}
                # Step 1: If carrying an animal → place it (if on pasture)
                has_animal = any(inv.get(a,0)>0 for a in ["COW","SHEEP"])
                if has_animal:
                    if isinstance(tile, dict) and tile.get("kind")=="PASTURE" and "animal" not in tile:
                        for a in ["COW","SHEEP"]:
                            if inv.get(a,0)>0: actions[best_w]=["PLACE",a]; break
                    else:
                        actions[best_w] = [bfs(wp, (jx,jy), bs)]
                # Step 2: If on target and it's empty → build pasture
                elif tile is None:
                    actions[best_w] = ["BUILD_PASTURE"]
                # Step 3: If on target and it's a pasture → pickup cow from shed
                elif isinstance(tile, dict) and tile.get("kind")=="PASTURE" and "animal" not in tile:
                    if tuple(wp) in sa and cows_s > 0:
                        for a in ["COW","SHEEP"]:
                            if shed.get(a,0)>0: actions[best_w]=["PICKUP",a,1]; break
                    else:
                        # Go to shed first
                        nearest = min(sa_list, key=lambda s: abs(wp[0]-s[0])+abs(wp[1]-s[1]))
                        actions[best_w] = [bfs(wp, nearest, bs)]
                else:
                    actions[best_w] = ["PASS"]
            elif jact == "PLANT":
                c = "WHEAT" if seeds.get("WHEAT",0)>0 else None
                actions[best_w] = ["PLANT", c] if c else ["PASS"]
            else: actions[best_w] = ["PASS"]
        else:
            actions[best_w] = [bfs(wp, (jx, jy), bs)]

    # Idle workers → pass
    for wi in range(len(workers)):
        if actions[wi] is None: actions[wi] = ["PASS"]

    return {"farmer": actions[0], "hands": actions[1:], "market": orders[:10]}
