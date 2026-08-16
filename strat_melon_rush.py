"""Strategy 1: MELON RUSH — All-in melons, buy land early, fertilize, massive harvest day 12+."""
from collections import deque

CROPS = {"WHEAT": {"seed": 10, "fy": 2, "my": 4}, "CARROT": {"seed": 20, "fy": 2, "my": 3}, "MELON": {"seed": 80, "fy": 10, "my": 12}}
ANIMALS = {"GOOSE": {"cost": 300, "s": "COOP"}, "COW": {"cost": 400, "s": "PASTURE"}, "SHEEP": {"cost": 500, "s": "PASTURE"}}
PRODUCTS = ["WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER"]
TD, TPD, LP = 30, 24, [1000, 2000, 4000]

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

def agent(obs, cfg=None):
    farm = obs["farms"][obs["player"]]
    priv = obs.get("private", {})
    bs = len(farm["tiles"])
    day, remaining = obs["day"], TD - obs["day"] - 1
    seeds = priv.get("seeds", {}); shed = priv.get("shed", {})
    money = farm["money"]; nq = len(farm.get("unlocked_quadrants", []))
    nh = len(farm.get("hands", []))
    inv_list = priv.get("inventories", [{}])

    # Count tiles
    empty = [(x,y) for y in range(bs) for x in range(bs) if farm["tiles"][y][x] is None]
    plants = [(x,y,farm["tiles"][y][x]) for y in range(bs) for x in range(bs)
              if isinstance(farm["tiles"][y][x], dict) and farm["tiles"][y][x].get("kind") == "PLANT"]
    harvestable = [(x,y,t) for x,y,t in plants if t.get("yield_units",0)>0 and day-t.get("planted_day",0)>=CROPS.get(t.get("crop",""),{}).get("fy",999)]
    waterable = [(x,y,t) for x,y,t in plants if not t.get("watered_today")]

    # Market orders
    orders = []; spent = 0

    # Sell everything in shed
    for p in PRODUCTS:
        q = shed.get(p, 0)
        if q > 0: orders.append(["SELL", p, min(q, 8)])

    # Buy land
    if nq < 3 and remaining > 12 and money - spent >= LP[nq-1] + 200:
        orders.append(["BUY_LAND"]); spent += LP[nq-1]

    # Buy melon seeds
    if remaining >= 13:
        have = seeds.get("MELON", 0)
        need = min(len(empty), 12) - have
        if need > 0 and money - spent >= 80 * need:
            orders.append(["BUY_SEED", "MELON", need]); spent += 80 * need

    # Late game: buy carrot
    if remaining < 13 and remaining >= 3:
        have = seeds.get("CARROT", 0) + seeds.get("WHEAT", 0)
        need = min(len(empty), 8) - have
        if need > 0 and money - spent >= 20 * need:
            orders.append(["BUY_SEED", "CARROT", need]); spent += 20 * need

    # Hire hands
    work = len(plants) + len(empty)
    if nh == 0 and work >= 2 and remaining > 2:
        f = 1
        if money - spent >= f: orders.append(["HIRE"]); spent += f
        if work >= 5 and money - spent >= 1: orders.append(["HIRE"]); spent += 1
        if work >= 10 and money - spent >= 2: orders.append(["HIRE"]); spent += 2

    # Worker tasks
    farmer_pos = tuple(farm["farmer"])
    hands = [tuple(h) for h in farm.get("hands", [])]
    workers = [farmer_pos] + hands
    actions = [None] * len(workers)

    # Drop off
    for wi, wp in enumerate(workers):
        if wi < len(inv_list) and inv_list[wi] and sum(inv_list[wi].values()) > 0:
            if tuple(wp) in set(shed_adj(bs)):
                actions[wi] = ["DROP"]

    # Build task list
    tasks = []
    for x,y,t in harvestable: tasks.append((x,y,"HARVEST",100))
    for x,y,t in waterable:
        prio = 85 if t.get("crop")=="MELON" and 5<=day-t.get("planted_day",0)<=12 else 70
        tasks.append((x,y,"WATER",prio))

    # PLANT tiles: sort by distance from nearest worker (plant close tiles first!)
    if any(seeds.get(c,0)>0 for c in ["MELON","CARROT","WHEAT"]):
        for x,y in empty:
            # Priority based on proximity to any worker — closer = higher priority
            min_dist = min(abs(wp[0]-x) + abs(wp[1]-y) for wp in workers)
            # Invert distance into priority: dist 0 → prio 50, dist 8 → prio 30
            prio = max(25, 50 - min_dist * 3)
            tasks.append((x,y,"PLANT",prio))
    tasks.sort(key=lambda t: t[3], reverse=True)

    # Assign
    for tx, ty, act, prio in tasks:
        best_w, best_d = None, 999
        for wi, wp in enumerate(workers):
            if actions[wi] is not None: continue
            d = abs(wp[0]-tx) + abs(wp[1]-ty)
            if d < best_d: best_d, best_w = d, wi
        if best_w is not None:
            wp = workers[best_w]
            if wp == (tx, ty):
                if act == "HARVEST": actions[best_w] = ["HARVEST"]
                elif act == "WATER": actions[best_w] = ["WATER"]
                elif act == "PLANT":
                    c = "MELON" if seeds.get("MELON",0)>0 and remaining>=13 else "CARROT" if seeds.get("CARROT",0)>0 else "WHEAT" if seeds.get("WHEAT",0)>0 else None
                    actions[best_w] = ["PLANT", c] if c else ["PASS"]
                else: actions[best_w] = ["PASS"]
            else:
                actions[best_w] = [bfs(wp, (tx,ty), bs)]

    for wi in range(len(workers)):
        if actions[wi] is None: actions[wi] = ["PASS"]

    return {"farmer": actions[0], "hands": actions[1:], "market": orders[:10]}
