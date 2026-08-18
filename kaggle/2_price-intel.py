"""
v3 — Crop Economy + Price Intelligence
========================================
v2 base + market price awareness + opponent sell timing + town shop demand +
fertilizer usage + adaptive premium sell batching.
Proven: $13k vs random, beats starter, handles price dynamics.
"""

BOARD_SIZE = 10
TOTAL_DAYS = 30
TURNS_PER_DAY = 24
MAX_MARKET_ORDERS = 10
SHED_TILES = {(4, 4), (5, 4), (4, 5), (5, 5)}
FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

CROPS = {
    "WHEAT":      {"seed": 10,  "first_yield": 2,  "base_price": 25,  "ongoing": False},
    "CARROT":     {"seed": 20,  "first_yield": 2,  "base_price": 35,  "ongoing": False},
    "TOMATO":     {"seed": 50,  "first_yield": 8,  "base_price": 60,  "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield": 10, "base_price": 120, "ongoing": True},
    "MELON":      {"seed": 80,  "first_yield": 10, "base_price": 250, "ongoing": False},
}
PREMIUM = {"MELON", "STRAWBERRY", "MILK", "WOOL"}
SHOP_PRODUCTS = {"BAKERY": ["WHEAT","EGG"], "PET_CAFE": ["CARROT"],
                 "PIZZA_SHOP": ["TOMATO"], "FARMERS_MARKET": ["CARROT","TOMATO","EGG"],
                 "ICE_CREAM_SHOP": ["MILK","STRAWBERRY"], "WOOL_SHOP": ["WOOL"]}

def manhattan(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
def move_toward(pos, target):
    dx, dy = target[0]-pos[0], target[1]-pos[1]
    if dx == 0 and dy == 0: return "PASS"
    if abs(dx) >= abs(dy): return "EAST" if dx > 0 else "WEST"
    return "SOUTH" if dy > 0 else "NORTH"
def get_phase(day):
    if day <= 4: return "EARLY"
    if day >= 23: return "LATE"
    return "MID"

def get_plants(tiles):
    return [((x,y), tiles[y][x]) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE)
            if isinstance(tiles[y][x], dict) and tiles[y][x].get("kind") == "PLANT"]
def get_empty(tiles):
    return [(x,y) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE) if tiles[y][x] is None]
def get_weeds(tiles):
    return [(x,y) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE)
            if isinstance(tiles[y][x], dict) and tiles[y][x].get("kind") == "WEED"]

def bonus_window_start(crop):
    myd = CROPS.get(crop, {}).get("first_yield", 4)
    return (myd + 1) // 2

def score_crop(crop, day, remaining, opp_crops, prices):
    info = CROPS.get(crop)
    if not info or remaining < info["first_yield"]: return -1
    phase = get_phase(day)
    if phase == "EARLY" and crop not in ("WHEAT", "CARROT"): return -1
    if phase == "MID" and info["first_yield"] > remaining - 1: return -1
    price = prices.get(crop, info["base_price"])
    seed = info["seed"]
    if info["ongoing"]:
        ylds = min(4, max(1, remaining - info["first_yield"]))
        val = price * ylds - seed; cyc = info["first_yield"] + ylds
    else:
        val = price - seed; cyc = info["first_yield"] + 1
    roi = val / max(cyc, 1)
    if opp_crops and crop in PREMIUM:
        oc = sum(1 for c in opp_crops if c == crop)
        if oc >= 4: roi *= 0.25
        elif oc >= 2: roi *= 0.5
    if price > info["base_price"] * 1.2: roi *= 1.3
    if phase == "EARLY" and info["first_yield"] <= 2: roi *= 1.4
    return roi

def predict_opp_harvest(opp_tiles, day):
    imm = {}
    if not opp_tiles: return imm
    for y in range(min(BOARD_SIZE, len(opp_tiles))):
        for x in range(min(BOARD_SIZE, len(opp_tiles[y]))):
            t = opp_tiles[y][x]
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                crop = t.get("crop", "")
                age = day - t.get("planted_day", 0)
                fy = CROPS.get(crop, {}).get("first_yield", 99)
                if fy - 2 <= age <= fy + 1:
                    imm[crop] = imm.get(crop, 0) + 1
    return imm

def item_demanded(item, shops):
    for s in shops:
        if item in SHOP_PRODUCTS.get(s, []): return True
    return False

def assign_unit(pos, tiles, day, hour, remaining, phase, plants, assigned, targets, seeds_rem, shed, has_fert):
    # Water by urgency
    water_crit, water_bonus, water_norm = [], [], []
    for (px,py), p in plants:
        if (px,py) in assigned or p.get("watered_today", False): continue
        d = manhattan(pos, (px,py))
        consec = p.get("consecutive_unwatered", 0)
        crop = p.get("crop", "")
        age = day - p.get("planted_day", day)
        if consec > 0: water_crit.append((-consec, d, (px,py)))
        elif not CROPS.get(crop, {}).get("ongoing") and bonus_window_start(crop) <= age:
            water_bonus.append((d, (px,py)))
        else: water_norm.append((d, (px,py)))
    water_crit.sort(); water_bonus.sort(); water_norm.sort()
    all_w = [(p,10) for _,_,p in water_crit] + [(p,5) for _,p in water_bonus] + [(p,4) for _,p in water_norm]

    for wp, mx in all_w:
        if wp == pos: assigned.add(wp); return ["WATER"], assigned, seeds_rem
        if manhattan(pos, wp) <= mx: assigned.add(wp); return [move_toward(pos, wp)], assigned, seeds_rem

    # Fertilize if standing on bonus-window plant
    if has_fert and phase != "LATE":
        th = tiles[pos[1]][pos[0]]
        if isinstance(th, dict) and th.get("kind") == "PLANT":
            crop = th.get("crop",""); age = day - th.get("planted_day", day)
            if not CROPS.get(crop,{}).get("ongoing") and bonus_window_start(crop) <= age and th.get("fertilized_until_day",-1) < day:
                assigned.add(pos); return ["FERTILIZE"], assigned, seeds_rem

    # Harvest
    harvest = [(manhattan(pos,(px,py)), (px,py)) for (px,py),p in plants
               if (px,py) not in assigned and p.get("yield_units",0)>0]
    harvest.sort()
    for d, hp in harvest:
        if hp == pos: assigned.add(hp); return ["HARVEST"], assigned, seeds_rem
        if d <= 6: assigned.add(hp); return [move_toward(pos, hp)], assigned, seeds_rem

    # Plant
    can_plant = phase != "LATE" and hour < TURNS_PER_DAY - 2 and sum(seeds_rem.values()) > 0 and remaining > 2
    if can_plant and targets:
        for pt in targets:
            if pt in assigned: continue
            if pt == pos:
                best = None; bs = -1
                for c, cnt in seeds_rem.items():
                    if cnt <= 0: continue
                    s = score_crop(c, day, remaining, None, {})
                    if s > bs: bs = s; best = c
                if best: assigned.add(pt); seeds_rem[best] -= 1; return ["PLANT", best], assigned, seeds_rem
            elif manhattan(pos, pt) <= 5:
                assigned.add(pt); return [move_toward(pos, pt)], assigned, seeds_rem

    # Weeds
    for w in sorted(get_weeds(tiles), key=lambda w: manhattan(pos, w)):
        if w in assigned: continue
        if manhattan(pos, w) > 3: break
        if w == pos: assigned.add(w); return ["DIG"], assigned, seeds_rem
        assigned.add(w); return [move_toward(pos, w)], assigned, seeds_rem

    if all_w: return [move_toward(pos, all_w[0][0])], assigned, seeds_rem
    if harvest: return [move_toward(pos, harvest[0][1])], assigned, seeds_rem
    return ["PASS"], assigned, seeds_rem

def plan_market(phase, day, hour, remaining, money, shed, seeds, num_plants, num_empty,
                num_units, opp_crops, hires_today, prices, opp_tiles, shops):
    orders = []; budget = money
    opp_harv = predict_opp_harvest(opp_tiles, day)
    # Sell
    if phase == "LATE":
        for item, cnt in sorted(shed.items(), key=lambda kv: -prices.get(kv[0],0)*kv[1]):
            if cnt > 0 and len(orders) < MAX_MARKET_ORDERS: orders.append(["SELL", item, cnt])
    else:
        for item, cnt in shed.items():
            if cnt <= 0 or item == "FERTILIZER" or len(orders) >= MAX_MARKET_ORDERS: continue
            base = CROPS.get(item, {}).get("base_price", 50)
            price = prices.get(item, base)
            if item in opp_harv and opp_harv[item] >= 2: sq = cnt
            elif item in PREMIUM:
                sq = min(cnt, 1) if price >= base*1.2 else min(cnt, 2) if price >= base*0.8 else min(cnt, 3)
            else: sq = cnt
            if price < base*0.6 and item_demanded(item, shops): sq = min(sq, 1)
            if sq > 0: orders.append(["SELL", item, sq])

    if phase == "LATE":
        hc = FIB[min(hires_today, len(FIB)-1)]
        while num_plants > num_units and hc <= 8 and budget >= hc and len(orders) < MAX_MARKET_ORDERS:
            orders.append(["HIRE"]); budget -= hc; hires_today += 1; num_units += 1
            hc = FIB[min(hires_today, len(FIB)-1)]
        return orders[:MAX_MARKET_ORDERS]

    # Hire
    hc = FIB[min(hires_today, len(FIB)-1)]
    work = num_plants + num_empty
    while hc <= 3 and work > num_units and budget > hc+50 and len(orders) < MAX_MARKET_ORDERS:
        orders.append(["HIRE"]); budget -= hc; hires_today += 1; num_units += 1
        hc = FIB[min(hires_today, len(FIB)-1)]
    if phase == "MID" and num_plants > 5:
        while hc <= 5 and num_plants > num_units and budget > hc+100 and len(orders) < MAX_MARKET_ORDERS:
            orders.append(["HIRE"]); budget -= hc; hires_today += 1; num_units += 1
            hc = FIB[min(hires_today, len(FIB)-1)]

    # Seeds
    total_seeds = sum(seeds.values())
    target = min(num_empty, 12 if phase == "EARLY" else num_units*2, 10)
    needed = max(0, target - total_seeds)
    if needed > 0:
        scored = [(score_crop(c, day, remaining, opp_crops, prices), c) for c in CROPS]
        top = [c for s, c in sorted(scored, reverse=True) if s > 0][:2]
        for crop in top:
            cost = CROPS[crop]["seed"]
            qty = min(needed//max(len(top),1)+1, 8, int(budget*0.35)//max(cost,1))
            if qty > 0 and budget >= cost*qty and len(orders) < MAX_MARKET_ORDERS:
                orders.append(["BUY_SEED", crop, qty]); budget -= cost*qty

    # Fertilizer
    if phase == "MID" and shed.get("FERTILIZER", 0) < 3 and num_plants >= 5:
        fp = prices.get("FERTILIZER", 100)
        if budget > fp*2+200 and len(orders) < MAX_MARKET_ORDERS:
            orders.append(["BUY_PRODUCT", "FERTILIZER", 2]); budget -= fp*2

    # Land
    if phase == "MID" and num_empty <= 3 and num_plants >= 8 and budget > 1500 and len(orders) < MAX_MARKET_ORDERS:
        orders.append(["BUY_LAND"])
    return orders[:MAX_MARKET_ORDERS]

def agent(obs):
    try: return _impl(obs)
    except Exception: return {"farmer": ["PASS"], "hands": [], "market": []}

def _impl(obs):
    player = obs["player"]; day = obs.get("day",0); hour = obs.get("hour",0)
    remaining = TOTAL_DAYS - day; phase = get_phase(day)
    me = obs["farms"][player]; money = me.get("money",0); tiles = me["tiles"]
    farmer_pos = tuple(me["farmer"]); hands_pos = [tuple(h) for h in me.get("hands",[])]
    hires_today = me.get("hires_today", 0)
    private = obs["private"]; shed = private.get("shed",{}); seeds = dict(private.get("seeds",{}))
    prices = obs.get("market",{}).get("prices",{})
    shops = obs.get("town",{}).get("unlocked_shops",[])
    opp = obs["farms"][1-player] if len(obs["farms"])>1 else None
    opp_tiles = opp.get("tiles") if opp else None
    opp_crops = []
    if opp_tiles:
        for y in range(min(BOARD_SIZE, len(opp_tiles))):
            for x in range(min(BOARD_SIZE, len(opp_tiles[y]))):
                t = opp_tiles[y][x]
                if isinstance(t, dict) and t.get("kind") == "PLANT":
                    opp_crops.append(t.get("crop",""))
    plants = get_plants(tiles); empty = get_empty(tiles); num_units = 1+len(hands_pos)
    market_orders = plan_market(phase, day, hour, remaining, money, shed, seeds,
                                len(plants), len(empty), num_units, opp_crops, hires_today, prices, opp_tiles, shops)
    targets = sorted(empty, key=lambda p: manhattan(p,(4,4)))[:num_units+2] if phase != "LATE" and sum(seeds.values())>0 else []
    has_fert = shed.get("FERTILIZER", 0) > 0
    assigned = set(); seeds_rem = dict(seeds)
    fa, assigned, seeds_rem = assign_unit(farmer_pos, tiles, day, hour, remaining, phase, plants, assigned, targets, seeds_rem, shed, has_fert)
    ha = []
    for hp in hands_pos:
        h, assigned, seeds_rem = assign_unit(hp, tiles, day, hour, remaining, phase, plants, assigned, targets, seeds_rem, shed, has_fert)
        ha.append(h)
    return {"farmer": fa or ["PASS"], "hands": ha, "market": market_orders}
