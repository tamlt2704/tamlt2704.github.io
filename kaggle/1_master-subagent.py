"""Master/Sub-Agent Architecture v2.

MASTER:
  - Reads market prices/trends
  - Sets macro strategy (what to buy, when to expand, target animal count)
  - Emits high-level tasks: FEED_CYCLE, PLANT, WATER, HARVEST, BUILD+PLACE, COLLECT
  - Does NOT micro-manage movement — agents figure that out

SUB-AGENT:
  - Takes a task and executes it to completion
  - Figures out WHERE to go (nearest target), HOW to get there (BFS)
  - Reports back when done (becomes idle for next task)

KEY STRATEGY:
  - COW is best value ($180/day: $100 fert + $80 milk)
  - MELON is best crop ($250/unit, 6 max yield, but sq price curve — sell small batches)
  - Build pastures NEAR shed (minimize travel)
  - Day 0: DON'T all-in. Hire workers + buy seeds. Workers plant crops.
  - Day 1-2: Farmer feeds animals solo from wheat crops harvest
  - Day 3+: Compound — sell products, buy more cows, expand
"""
from collections import deque
from dataclasses import dataclass
from typing import Optional, Tuple, List
import sys

TD = 30


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING — prints go to Kaggle agent logs (kaggle competitions logs <id>)
# ═══════════════════════════════════════════════════════════════════════════════

class Logger:
    """Lightweight logger. Outputs per-day summaries + key events.
    Kaggle captures stdout as agent logs."""
    def __init__(self):
        self.day_stats = {}
        self.current_day = -1

    def new_day(self, day, money, animals, plants, hands, shed):
        if self.current_day >= 0 and self.current_day in self.day_stats:
            self._flush_day()
        self.current_day = day
        self.day_stats[day] = {
            'money_start': money, 'animals': animals, 'plants': plants,
            'hands': hands, 'actions': [], 'market': [],
            'sells': {}, 'buys': {}, 'hires': 0,
            'fert_collected': 0, 'fert_sold': 0,
            'animals_fed': 0, 'animals_lost': 0,
            'harvests': 0, 'plants_died': 0,
        }

    def log_market(self, orders):
        if self.current_day not in self.day_stats:
            return
        d = self.day_stats[self.current_day]
        for o in orders:
            if not o:
                continue
            if o[0] == 'SELL':
                item, qty = o[1], o[2] if len(o) > 2 else 1
                d['sells'][item] = d['sells'].get(item, 0) + qty
                if item == 'FERTILIZER':
                    d['fert_sold'] += qty
            elif o[0] == 'HIRE':
                d['hires'] += 1
            elif o[0] in ('BUY_SEED', 'BUY_PRODUCT', 'BUY_ANIMAL'):
                key = o[1]
                qty = o[2] if len(o) > 2 else 1
                d['buys'][key] = d['buys'].get(key, 0) + qty

    def log_action(self, unit_id, action, task_kind=None):
        if self.current_day not in self.day_stats:
            return
        d = self.day_stats[self.current_day]
        act = action[0] if action else 'PASS'
        if act == 'FEED':
            d['animals_fed'] += 1
        elif act == 'HARVEST':
            d['harvests'] += 1
        elif act == 'COLLECT_FERTILIZER':
            d['fert_collected'] += 1

    def log_event(self, msg):
        """Log a notable event (animal escape, plant death, big sell, etc.)"""
        print("[D%d] %s" % (self.current_day, msg), file=sys.stderr)

    def end_game(self, final_money):
        self._flush_day()
        print("=== GAME OVER: $%.0f ===" % final_money, file=sys.stderr)

    def _flush_day(self):
        day = self.current_day
        if day not in self.day_stats:
            return
        d = self.day_stats[day]
        sells_str = " ".join("%s:%d" % (k, v) for k, v in sorted(d['sells'].items(), key=lambda x: -x[1])[:5])
        buys_str = " ".join("%s:%d" % (k, v) for k, v in sorted(d['buys'].items(), key=lambda x: -x[1])[:4])
        print("D%02d $%5.0f | A:%d P:%d H:%d | Fed:%d Fert:%d/%d Harv:%d | SELL[%s] BUY[%s]" % (
            day, d['money_start'], d['animals'], d['plants'], d['hands'],
            d['animals_fed'], d['fert_collected'], d['fert_sold'],
            d['harvests'], sells_str, buys_str
        ), file=sys.stderr)


LOG = Logger()


# ═══════════════════════════════════════════════════════════════════════════════
# TASK
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Task:
    kind: str
    target: Optional[Tuple[int, int]] = None
    item: Optional[str] = None
    priority: int = 50


# ═══════════════════════════════════════════════════════════════════════════════
# SUB-AGENT: executes one task at a time, autonomously decides pathfinding
# ═══════════════════════════════════════════════════════════════════════════════

class SubAgent:
    def __init__(self):
        self.task: Optional[Task] = None
        self.phase: int = 0

    @property
    def idle(self):
        return self.task is None

    def assign(self, task: Task):
        self.task = task
        self.phase = 0

    def done(self):
        self.task = None
        self.phase = 0

    def step(self, pos, farm, inv, shed, seeds, bs) -> list:
        """Execute one step. Agent autonomously decides movement."""
        if self.task is None:
            return ["PASS"]

        h = bs // 2
        sa_set = set(self._shed_tiles(bs))
        tile = farm["tiles"][pos[1]][pos[0]] if 0 <= pos[0] < bs and 0 <= pos[1] < bs else None

        # OPPORTUNISTIC: if standing on a dry plant, water it first (free action!)
        # This prevents plants dying while workers walk past them
        if (tile and isinstance(tile, dict) and tile.get("kind") == "PLANT"
                and not tile.get("watered_today") and self.task.kind != "WATER"):
            return ["WATER"]

        k = self.task.kind

        # ── FEED_CYCLE: get wheat → walk to unfed animal → FEED → CARE ──
        if k == "FEED_CYCLE":
            return self._do_feed(pos, tile, farm, inv, shed, bs, sa_set)

        # ── WATER: walk to unwatered plant → WATER ──
        elif k == "WATER":
            target = self._find_nearest(pos, farm, bs, kind="PLANT", condition=lambda t: not t.get("watered_today"))
            if target is None:
                self.done(); return ["PASS"]
            if pos == target:
                self.done(); return ["WATER"]
            return [self._move(pos, target, bs)]

        # ── FERTILIZE_PLANT: pickup fertilizer from shed → walk to plant → FERTILIZE ──
        elif k == "FERTILIZE_PLANT":
            if self.phase == 0:
                # Need fertilizer in inventory
                if inv.get("FERTILIZER", 0) > 0:
                    self.phase = 1
                elif pos in sa_set and shed.get("FERTILIZER", 0) > 0:
                    self.phase = 1; return ["PICKUP", "FERTILIZER", 1]
                elif shed.get("FERTILIZER", 0) > 0:
                    return [self._move(pos, self._nearest_shed(pos, bs), bs)]
                else:
                    self.done(); return ["PASS"]
            if self.phase == 1:
                # Find unfertilized melon/strawberry plant (high-value only)
                target = self._find_nearest(pos, farm, bs, kind="PLANT",
                    condition=lambda t: t.get("crop") in ("MELON", "STRAWBERRY")
                    and t.get("fertilized_until_day", -1) < 0)
                if target is None:
                    self.done(); return ["PASS"]
                if pos == target:
                    self.done(); return ["FERTILIZE"]
                return [self._move(pos, target, bs)]

        # ── HARVEST: walk to harvestable tile → HARVEST ──
        elif k == "HARVEST":
            target = self._find_nearest(pos, farm, bs, condition=lambda t: t.get("yield_units", 0) > 0)
            if target is None:
                self.done(); return ["PASS"]
            if pos == target:
                self.done(); return ["HARVEST"]
            return [self._move(pos, target, bs)]

        # ── COLLECT_FERT: walk to animal with fert → collect → go shed → drop ──
        elif k == "COLLECT_FERT":
            if self.phase == 0:
                target = self._find_nearest(pos, farm, bs, has_animal=True,
                                            condition=lambda t: t.get("fertilizer_available"))
                if target is None:
                    self.done(); return ["PASS"]
                if pos == target:
                    self.phase = 1; return ["COLLECT_FERTILIZER"]
                return [self._move(pos, target, bs)]
            else:
                # Return to shed and drop
                if pos in sa_set:
                    self.done(); return ["DROP"]
                return [self._move(pos, self._nearest_shed(pos, bs), bs)]

        # ── BUILD_PASTURE: pickup animal FIRST → walk to target → build → place immediately ──
        elif k == "BUILD_PASTURE":
            animal = self.task.item or "COW"
            if self.phase == 0:
                # Phase 0: pickup animal from shed first
                if inv.get(animal, 0) > 0:
                    self.phase = 1  # already carrying, go build
                elif pos in sa_set and shed.get(animal, 0) > 0:
                    self.phase = 1; return ["PICKUP", animal, 1]
                elif shed.get(animal, 0) > 0:
                    return [self._move(pos, self._nearest_shed(pos, bs), bs)]
                else:
                    # No animal to place — just build the pasture
                    self.phase = 1
            if self.phase == 1:
                # Phase 1: walk to target and build
                target = self.task.target
                if target is None:
                    self.done(); return ["PASS"]
                if pos == target:
                    if farm["tiles"][target[1]][target[0]] is None:
                        self.phase = 2; return ["BUILD_PASTURE"]
                    self.done(); return ["PASS"]
                return [self._move(pos, target, bs)]
            if self.phase == 2:
                # Phase 2: place animal immediately (same tile, no walking!)
                if inv.get(animal, 0) > 0:
                    self.done(); return ["PLACE", animal]
                self.done(); return ["PASS"]

        # ── PLACE_ANIMAL: go shed → pickup → find empty pasture → place ──
        elif k == "PLACE_ANIMAL":
            animal = self.task.item or "COW"
            if self.phase == 0:
                if inv.get(animal, 0) > 0:
                    self.phase = 1
                elif pos in sa_set and shed.get(animal, 0) > 0:
                    self.phase = 1; return ["PICKUP", animal, 1]
                else:
                    return [self._move(pos, self._nearest_shed(pos, bs), bs)]
            if self.phase == 1:
                target = self._find_nearest(pos, farm, bs, kind="PASTURE",
                                            condition=lambda t: "animal" not in t)
                if target is None:
                    self.done(); return ["PASS"]
                if pos == target:
                    self.done(); return ["PLACE", animal]
                return [self._move(pos, target, bs)]

        # ── PLANT_CROP: walk to empty tile → plant ──
        elif k == "PLANT_CROP":
            crop = self.task.item or "WHEAT"
            if seeds.get(crop, 0) <= 0:
                self.done(); return ["PASS"]
            target = self.task.target
            if target is None:
                # Find nearest empty tile
                target = self._find_nearest_empty(pos, farm, bs)
                if target is None:
                    self.done(); return ["PASS"]
            if pos == target:
                if farm["tiles"][target[1]][target[0]] is None:
                    self.done(); return ["PLANT", crop]
                self.done(); return ["PASS"]
            return [self._move(pos, target, bs)]

        # ── SELL_RUN: go to shed and drop everything ──
        elif k == "SELL_RUN":
            if pos in sa_set:
                if any(inv.get(p, 0) > 0 for p in inv):
                    self.done(); return ["DROP"]
                self.done(); return ["PASS"]
            return [self._move(pos, self._nearest_shed(pos, bs), bs)]

        self.done()
        return ["PASS"]

    def _do_feed(self, pos, tile, farm, inv, shed, bs, sa_set):
        """FULL SERVICE: pickup wheat → go animal → FEED → CARE → COLLECT → HARVEST → go shed → DROP.
        Does everything on one animal before leaving."""
        if self.phase == 0:
            # Get wheat
            if inv.get("WHEAT", 0) > 0:
                self.phase = 1
            elif pos in sa_set and shed.get("WHEAT", 0) > 0:
                self.phase = 1
                return ["PICKUP", "WHEAT", min(6, shed.get("WHEAT", 0))]
            else:
                return [self._move(pos, self._nearest_shed(pos, bs), bs)]

        if self.phase == 1:
            # Find nearest unfed animal (or uncared if all fed)
            target = self._find_nearest(pos, farm, bs, has_animal=True,
                                        condition=lambda t: not t.get("fed_today"))
            if target is None:
                target = self._find_nearest(pos, farm, bs, has_animal=True,
                                            condition=lambda t: t.get("fed_today") and not t.get("cared_today"))
            if target is None:
                # All fed and cared — try collecting fertilizer
                target = self._find_nearest(pos, farm, bs, has_animal=True,
                                            condition=lambda t: t.get("fertilizer_available"))
                if target is None:
                    self.phase = 10  # go drop products at shed
                else:
                    if pos == target:
                        self.phase = 4; return ["COLLECT_FERTILIZER"]
                    return [self._move(pos, target, bs)]
                return [self._move(pos, self._nearest_shed(pos, bs), bs)]
            if pos == target:
                t = farm["tiles"][pos[1]][pos[0]]
                if isinstance(t, dict) and "animal" in t and not t.get("fed_today") and inv.get("WHEAT", 0) > 0:
                    self.phase = 2; return ["FEED"]
                elif isinstance(t, dict) and "animal" in t and t.get("fed_today") and not t.get("cared_today"):
                    self.phase = 3; return ["CARE"]
                else:
                    self.phase = 4
                    return ["PASS"]
            return [self._move(pos, target, bs)]

        if self.phase == 2:
            # Just fed — now CARE (same tile)
            t = farm["tiles"][pos[1]][pos[0]]
            if isinstance(t, dict) and "animal" in t:
                if t.get("fed_today") and not t.get("cared_today"):
                    self.phase = 3; return ["CARE"]
            self.phase = 4; return ["PASS"]

        if self.phase == 3:
            # Just cared — check for COLLECT_FERTILIZER (same tile)
            t = farm["tiles"][pos[1]][pos[0]]
            if isinstance(t, dict) and "animal" in t:
                if t.get("fertilizer_available"):
                    self.phase = 4; return ["COLLECT_FERTILIZER"]
                if t.get("yield_units", 0) > 0:
                    self.phase = 5; return ["HARVEST"]
            self.phase = 5; return ["PASS"]

        if self.phase == 4:
            # Collected fertilizer — check HARVEST (same tile)
            t = farm["tiles"][pos[1]][pos[0]]
            if isinstance(t, dict) and "animal" in t and t.get("yield_units", 0) > 0:
                self.phase = 5; return ["HARVEST"]
            self.phase = 5; return ["PASS"]

        if self.phase == 5:
            # Done with this animal — still have wheat? Go to next unfed animal
            if inv.get("WHEAT", 0) > 0:
                next_target = self._find_nearest(pos, farm, bs, has_animal=True,
                                                 condition=lambda t: not t.get("fed_today"))
                if next_target and next_target != pos:
                    self.phase = 1; return [self._move(pos, next_target, bs)]
            # No more wheat or no more unfed — go shed to DROP products
            self.phase = 10
            return ["PASS"]

        if self.phase == 10:
            # Return to shed and drop
            if pos in sa_set:
                if any(inv.get(p, 0) > 0 for p in ["FERTILIZER", "MILK", "WOOL", "EGG"]):
                    self.done(); return ["DROP"]
                self.done(); return ["PASS"]
            return [self._move(pos, self._nearest_shed(pos, bs), bs)]

        self.done()
        return ["PASS"]

    # ── Utility ──

    def _move(self, src, dst, bs):
        if src == dst:
            return "PASS"
        p = {src: None}
        q = deque([src])
        while q:
            cx, cy = q.popleft()
            if (cx, cy) == dst:
                break
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < bs and 0 <= ny < bs and (nx, ny) not in p:
                    p[(nx, ny)] = (cx, cy)
                    q.append((nx, ny))
        if dst not in p:
            return "PASS"
        cur = dst
        while p[cur] != src:
            cur = p[cur]
        dx, dy = cur[0] - src[0], cur[1] - src[1]
        return {(1, 0): "EAST", (-1, 0): "WEST", (0, 1): "SOUTH", (0, -1): "NORTH"}.get((dx, dy), "PASS")

    def _shed_tiles(self, bs):
        h = bs // 2
        return [(h, h), (h-1, h), (h, h-1), (h-1, h-1)]

    def _nearest_shed(self, pos, bs):
        tiles = self._shed_tiles(bs)
        return min(tiles, key=lambda t: abs(t[0]-pos[0]) + abs(t[1]-pos[1]))

    def _find_nearest(self, pos, farm, bs, kind=None, has_animal=False, condition=None):
        """Find nearest tile matching criteria."""
        best, best_d = None, 999
        for y in range(bs):
            for x in range(bs):
                t = farm["tiles"][y][x]
                if not isinstance(t, dict):
                    continue
                if kind and t.get("kind") != kind and not (has_animal and "animal" in t):
                    continue
                if has_animal and "animal" not in t:
                    continue
                if condition and not condition(t):
                    continue
                d = abs(x - pos[0]) + abs(y - pos[1])
                if d < best_d:
                    best_d = d
                    best = (x, y)
        return best

    def _find_nearest_empty(self, pos, farm, bs):
        """Find nearest empty tile in unlocked quadrant."""
        h = bs // 2
        unlocked = set(farm.get("unlocked_quadrants", ["NW"]))
        best, best_d = None, 999
        for y in range(bs):
            for x in range(bs):
                if farm["tiles"][y][x] is not None:
                    continue
                qn = ("N" if y < h else "S") + ("W" if x < h else "E")
                if qn not in unlocked:
                    continue
                d = abs(x - pos[0]) + abs(y - pos[1])
                if d < best_d:
                    best_d = d
                    best = (x, y)
        return best


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER: reads market, sets macro strategy, emits tasks
# ═══════════════════════════════════════════════════════════════════════════════

class Master:
    """
    Data-driven strategy from 36 top-player games ($96k avg):
    - Day 0: ALL-IN (2COW + 2SHEEP + 7wheat_seed + 12melon_seed + 9wheat_product)
    - Animals scale: 4→5→6→10→12→14 by day 13, then stop
    - Hiring: 5 day 0, 4-5 days 2-6, 10-12 from day 7+
    - Fertilizer: sell ALL immediately (no buffer)
    - Wheat: buy seeds every day (5-9), buy product for feed (animals*3)
    - Melon: harvested day 10 = $12.5k windfall
    - Strawberry: bulk buy day 11 (20+ seeds) funded by melon windfall
    """

    def __init__(self):
        pass

    def decide_market(self, obs) -> list:
        """Data-driven market orders matching top-player patterns."""
        player = obs["player"]
        farm = obs["farms"][player]
        priv = obs.get("private", {})
        money = farm["money"]
        shed = priv.get("shed", {})
        seeds = priv.get("seeds", {})
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        remaining = TD - day - 1
        nh = len(farm.get("hands", []))
        hires_today = farm.get("hires_today", 0)
        nq = len(farm.get("unlocked_quadrants", ["NW"]))
        prices = obs.get("market", {}).get("prices", {})
        tiles = farm["tiles"]
        bs = len(tiles)

        # Count animals on board + in shed
        na = sum(1 for y in range(bs) for x in range(bs)
                 if isinstance(tiles[y][x], dict) and "animal" in tiles[y][x])
        in_shed = shed.get("COW", 0) + shed.get("SHEEP", 0)
        total_animals = na + in_shed

        orders = []
        spent = 0

        # ══════════════════════════════════════════════════════════════════════
        # DAY 0 HARDCODED OPENING (100% consistent in top-player data)
        # ══════════════════════════════════════════════════════════════════════
        if day == 0 and hour <= 1 and total_animals == 0:
            return [
                ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"],
                ["BUY_ANIMAL", "COW", 2],
                ["BUY_ANIMAL", "SHEEP", 2],
                ["BUY_SEED", "WHEAT", 7],
                ["BUY_SEED", "MELON", 12],
                ["BUY_PRODUCT", "WHEAT", 6],
            ]

        # ══════════════════════════════════════════════════════════════════════
        # SELL: ALL products immediately. No buffers.
        # Top players sell fertilizer aggressively (139 on day 10!)
        # ══════════════════════════════════════════════════════════════════════
        for prod in ["FERTILIZER", "MILK", "WOOL", "MELON", "STRAWBERRY", "EGG", "CARROT"]:
            q = shed.get(prod, 0)
            if q > 0 and len(orders) < 10:
                orders.append(["SELL", prod, q])

        # Sell excess wheat (keep feed buffer for animals)
        wheat_keep = na * 2 + 4  # 2 per animal per day + small buffer
        wheat_sell = shed.get("WHEAT", 0) - wheat_keep
        if wheat_sell > 0 and len(orders) < 10:
            orders.append(["SELL", "WHEAT", wheat_sell])

        # ══════════════════════════════════════════════════════════════════════
        # LAST 2 DAYS: liquidate everything
        # ══════════════════════════════════════════════════════════════════════
        if remaining <= 1:
            orders = []
            for prod in ["FERTILIZER", "WHEAT", "MILK", "WOOL", "MELON",
                         "STRAWBERRY", "CARROT", "EGG"]:
                q = shed.get(prod, 0)
                if q > 0 and len(orders) < 10:
                    orders.append(["SELL", prod, q])
            return orders[:10]

        # ══════════════════════════════════════════════════════════════════════
        # HIRE: aggressive schedule matching data
        # Day 0=5, Day 2-6=4-5, Day 7+=10-12
        # ══════════════════════════════════════════════════════════════════════
        if hour == 0 and nh == 0 and remaining > 0:
            if day == 0:
                target_hires = 5
            elif day == 1:
                target_hires = 0  # broke after all-in
            elif day <= 6:
                target_hires = min(5, max(0, int((money - spent - 100) / 5)))
            else:
                # Day 7+: hire 10-12 (data shows avg 10-12)
                target_hires = min(12, max(0, int((money - spent - 200) / 15)))

            for i in range(target_hires):
                cost = self._fib(hires_today + i)
                if money - spent >= cost + 20 and len(orders) < 10:
                    orders.append(["HIRE"])
                    spent += cost

        # ══════════════════════════════════════════════════════════════════════
        # BUY ANIMALS: scale to 14 by day 13, then STOP
        # Data: Day 3=+1COW, Day 5=+1COW, Day 7=+1COW+1SHEEP, Day 9/11=+1-2 each
        # ══════════════════════════════════════════════════════════════════════
        if day <= 13 and in_shed == 0 and total_animals < 14 and len(orders) < 10:
            # Determine how many animals we SHOULD have by this day
            target_by_day = {0: 4, 1: 4, 2: 4, 3: 5, 4: 5, 5: 6, 6: 6,
                             7: 10, 8: 10, 9: 12, 10: 12, 11: 14, 12: 14, 13: 14}
            target = target_by_day.get(day, 14)
            deficit = target - total_animals

            if deficit > 0 and money - spent >= 500:
                # Count current mix
                n_cows = sum(1 for y in range(bs) for x in range(bs)
                             if isinstance(tiles[y][x], dict) and tiles[y][x].get("animal") == "COW")
                n_sheep = sum(1 for y in range(bs) for x in range(bs)
                              if isinstance(tiles[y][x], dict) and tiles[y][x].get("animal") == "SHEEP")
                n_cows += shed.get("COW", 0)
                n_sheep += shed.get("SHEEP", 0)

                # Buy pairs when possible (data shows bulk buys)
                if deficit >= 2 and money - spent >= 900:
                    # Prefer cow (higher daily value)
                    if n_cows <= n_sheep * 2:
                        orders.append(["BUY_ANIMAL", "COW", 2])
                        spent += 800
                    else:
                        orders.append(["BUY_ANIMAL", "SHEEP", 2])
                        spent += 1000
                elif deficit >= 1:
                    if n_cows <= n_sheep * 2 and money - spent >= 500:
                        orders.append(["BUY_ANIMAL", "COW", 1])
                        spent += 400
                    elif money - spent >= 600:
                        orders.append(["BUY_ANIMAL", "SHEEP", 1])
                        spent += 500

        # ══════════════════════════════════════════════════════════════════════
        # BUY WHEAT for feed: animals * 3 target in shed
        # Data shows 9-86 wheat/day purchased!
        # ══════════════════════════════════════════════════════════════════════
        if na > 0 and len(orders) < 10:
            wheat_have = shed.get("WHEAT", 0)
            wheat_want = na * 3  # 3 per animal (data: heavy buying)
            deficit = wheat_want - wheat_have
            if deficit > 0:
                wp = max(1, int(prices.get("WHEAT", 25)))
                # Spend up to 40% of remaining budget on wheat
                max_spend = int((money - spent) * 0.4)
                qty = min(deficit, max(1, max_spend // wp))
                if qty > 0 and money - spent >= wp * qty:
                    orders.append(["BUY_PRODUCT", "WHEAT", qty])
                    spent += wp * qty

        # ══════════════════════════════════════════════════════════════════════
        # BUY SEEDS: match exact data pattern
        # Day 0: WHEAT 7 + MELON 12 (in opening)
        # Day 4: WHEAT 7
        # Day 5: STRAWBERRY 4
        # Day 6: CARROT 7, STRAWBERRY 3
        # Day 8: STRAWBERRY 9, WHEAT 5
        # Day 11: STRAWBERRY 22!! (big reinvestment after melon windfall)
        # Day 12+: WHEAT 4-9/day
        # ══════════════════════════════════════════════════════════════════════
        if len(orders) < 10:
            # Wheat seeds: buy 5-9 every day from day 4+ (feed infrastructure)
            if day >= 4 and seeds.get("WHEAT", 0) < 5 and money - spent >= 80:
                qty = min(9, max(5, int((money - spent - 100) / 15)))
                if qty > 0:
                    orders.append(["BUY_SEED", "WHEAT", qty])
                    spent += qty * 10

            # Strawberry: bulk buy day 5-6, massive day 11
            if day == 11 and seeds.get("STRAWBERRY", 0) < 15 and money - spent >= 2200:
                orders.append(["BUY_SEED", "STRAWBERRY", 20])
                spent += 2000
            elif 5 <= day <= 8 and seeds.get("STRAWBERRY", 0) < 5 and money - spent >= 500:
                orders.append(["BUY_SEED", "STRAWBERRY", 4])
                spent += 400

            # Carrot: day 6 burst
            if day == 6 and seeds.get("CARROT", 0) < 4 and money - spent >= 160 and len(orders) < 10:
                orders.append(["BUY_SEED", "CARROT", 7])
                spent += 140

            # Extra melon if early and affordable
            if day <= 2 and seeds.get("MELON", 0) < 8 and money - spent >= 640 and len(orders) < 10:
                orders.append(["BUY_SEED", "MELON", 8])
                spent += 640

        # ══════════════════════════════════════════════════════════════════════
        # BUY LAND: day 6 (standard timing from data)
        # ══════════════════════════════════════════════════════════════════════
        if day >= 6 and nq < 2 and len(orders) < 10:
            n_empty = sum(1 for y in range(bs) for x in range(bs)
                          if tiles[y][x] is None and
                          ("N" if y < bs//2 else "S") + ("W" if x < bs//2 else "E")
                          in set(farm.get("unlocked_quadrants", ["NW"])))
            if (n_empty <= 5 or in_shed > 0) and money - spent >= 1200:
                land_cost = [1000, 2000, 4000][nq - 1] if nq <= 3 else 99999
                if money - spent >= land_cost + 200:
                    orders.append(["BUY_LAND"])
                    spent += land_cost

        return orders[:10]
        return orders[:10]

    def decide_tasks(self, obs, num_idle) -> List[Task]:
        """Master scans the board and generates prioritized tasks."""
        player = obs["player"]
        farm = obs["farms"][player]
        priv = obs.get("private", {})
        tiles = farm["tiles"]
        bs = len(tiles)
        h = bs // 2
        day = obs.get("day", 0)
        remaining = TD - day - 1
        shed = priv.get("shed", {})
        seeds = priv.get("seeds", {})
        unlocked = set(farm.get("unlocked_quadrants", ["NW"]))

        # Scan board
        unfed, uncared, fert_avail, harvestable = [], [], [], []
        unwatered, harv_plants = [], []
        empty_pastures, empty_tiles = [], []
        na = 0

        for y in range(bs):
            for x in range(bs):
                t = tiles[y][x]
                if t is None:
                    qn = ("N" if y < h else "S") + ("W" if x < h else "E")
                    if qn in unlocked:
                        empty_tiles.append((x, y))
                elif isinstance(t, dict):
                    if "animal" in t:
                        na += 1
                        if not t.get("fed_today"):
                            unfed.append((x, y))
                        elif not t.get("cared_today"):
                            uncared.append((x, y))
                        if t.get("fertilizer_available"):
                            fert_avail.append((x, y))
                        if t.get("yield_units", 0) > 0:
                            harvestable.append((x, y))
                    elif t.get("kind") == "PASTURE" and "animal" not in t:
                        empty_pastures.append((x, y))
                    elif t.get("kind") == "PLANT":
                        if not t.get("watered_today"):
                            unwatered.append((x, y))
                        if t.get("yield_units", 0) > 0:
                            harv_plants.append((x, y))

        in_shed = shed.get("COW", 0) + shed.get("SHEEP", 0)

        # Sort empty tiles by distance to center (build near shed)
        empty_tiles.sort(key=lambda p: abs(p[0] - h) + abs(p[1] - h))

        # ZONE PLANNING: center for animals, surrounding for wheat, outer for melon
        # Reserve closest tiles for future pastures (up to how many more animals we need)
        future_animals_needed = max(0, 14 - na - in_shed - len(empty_pastures))
        pasture_reserve = min(future_animals_needed, 6)  # reserve max 6 tiles
        pasture_tiles = empty_tiles[:pasture_reserve]
        crop_tiles = empty_tiles[pasture_reserve:]

        # Split crop tiles: inner = wheat (cheap, fast, feed), outer = melon/strawberry
        wheat_tiles = crop_tiles[:8]   # first 8 non-reserved tiles → wheat
        melon_tiles = crop_tiles[8:]   # rest → high-value crops

        # ═══ THINK LIKE A FARM MANAGER: split the crew into roles ═══
        # Livestock crew: feed + care + collect (1 per 4 animals)
        # Field crew: water + harvest plants (1 per 10 plants)
        # Setup crew: plant, build pastures, place animals

        livestock_need = max(1, (na + 3) // 4) if (unfed or uncared or fert_avail or harvestable) else 0
        field_need = max(1, (len(unwatered) + 9) // 10) if unwatered else 0
        field_need += 1 if harv_plants else 0

        # Budget workers: livestock first, then field, then setup
        livestock_alloc = min(livestock_need, num_idle)
        field_alloc = min(field_need, num_idle - livestock_alloc)
        setup_alloc = max(0, num_idle - livestock_alloc - field_alloc)

        # If day 0 and no animals yet, all workers go to planting
        if na == 0 and in_shed == 0:
            livestock_alloc = 0
            field_alloc = 0
            setup_alloc = num_idle
        # Day 0-1: prioritize planting to fill tiles (blocks weeds!)
        # Keep 1 worker for animal placement, rest plant
        elif day <= 1 and num_idle > 2:
            livestock_alloc = min(1, livestock_need)
            field_alloc = 0
            setup_alloc = num_idle - livestock_alloc

        tasks = []

        # LIVESTOCK CREW
        for i in range(livestock_alloc):
            tasks.append(Task("FEED_CYCLE", priority=200))

        # FIELD CREW
        for i in range(field_alloc):
            if harv_plants and i == 0:
                tasks.append(Task("HARVEST", target=harv_plants[0], priority=160))
            else:
                tasks.append(Task("WATER", priority=155))

        # FERTILIZE high-value plants if we have fertilizer (doubles yield!)
        # Only fertilize melon/strawberry — worth $1500 vs selling fert for $100
        if shed.get("FERTILIZER", 0) > 0:
            has_unfertilized = any(
                isinstance(tiles[y][x], dict) and tiles[y][x].get("kind") == "PLANT"
                and tiles[y][x].get("crop") in ("MELON", "STRAWBERRY")
                and tiles[y][x].get("fertilized_until_day", -1) < 0
                for y in range(bs) for x in range(bs)
            )
            if has_unfertilized:
                tasks.append(Task("FERTILIZE_PLANT", priority=140))

        # URGENT: Place animals from shed (stuck animal = $180/day lost!)
        # Goes into MAIN task list, not setup — must always get a worker
        if in_shed > 0:
            if empty_pastures:
                for a in ["COW", "SHEEP"]:
                    if shed.get(a, 0) > 0:
                        tasks.append(Task("PLACE_ANIMAL", item=a, priority=195))  # below FEED(200)
            elif pasture_tiles:
                animal = "COW" if shed.get("COW", 0) > 0 else "SHEEP"
                tasks.append(Task("BUILD_PASTURE", target=pasture_tiles[0], item=animal, priority=195))
            elif empty_tiles:
                # No reserved pasture tiles left — use any empty tile
                animal = "COW" if shed.get("COW", 0) > 0 else "SHEEP"
                tasks.append(Task("BUILD_PASTURE", target=empty_tiles[0], item=animal, priority=195))

        # SETUP CREW (planting only — animal placement moved to main tasks above)
        setup_tasks = []

        # Plant crops — ZONED + SHOP AWARE
        # Check which shops are open → plant crops they consume
        # SHOPS: BAKERY[EGG,WHEAT], PIZZA[MILK,TOMATO,WHEAT], BRUNCH[EGG,WHEAT,STRAWBERRY]
        #        YARN_STORE[WOOL], ICE_CREAM[STRAWBERRY,MILK,WHEAT], PET_CAFE[CARROT]
        #        SMOOTHIE[STRAWBERRY,MILK], FARMERS_MARKET[WHEAT,CARROT,TOMATO,STRAWBERRY]
        town = obs.get("town", {})
        open_shops = town.get("unlocked_shops", [])

        # Count demand per crop from shops
        shop_demand = {"WHEAT": 0, "STRAWBERRY": 0, "CARROT": 0, "TOMATO": 0}
        shop_products = {
            "BAKERY": ["WHEAT"], "PIZZA_SHOP": ["WHEAT", "TOMATO"],
            "BRUNCH_SPOT": ["WHEAT", "STRAWBERRY"], "ICE_CREAM_SHOP": ["WHEAT", "STRAWBERRY"],
            "PET_CAFE": ["CARROT"], "SMOOTHIE_SHOP": ["STRAWBERRY"],
            "FARMERS_MARKET": ["WHEAT", "CARROT", "STRAWBERRY"],
        }
        for shop in open_shops:
            for crop in shop_products.get(shop, []):
                if crop in shop_demand:
                    shop_demand[crop] += 1

        # Pick best outer crop based on shop demand + value
        best_outer_crop = "MELON"  # default: melon is highest base value
        if remaining >= 13 and seeds.get("MELON", 0) > 0:
            best_outer_crop = "MELON"
        elif shop_demand.get("STRAWBERRY", 0) >= 2 and seeds.get("STRAWBERRY", 0) > 0 and remaining >= 10:
            best_outer_crop = "STRAWBERRY"  # multiple shops want it
        elif seeds.get("STRAWBERRY", 0) > 0 and remaining >= 10:
            best_outer_crop = "STRAWBERRY"

        if remaining > 3:
            # Inner zone: plant wheat (always useful — feed + 5 shops consume it)
            for pos in wheat_tiles[:max(setup_alloc, 2)]:
                if seeds.get("WHEAT", 0) > 0:
                    setup_tasks.append(Task("PLANT_CROP", target=pos, item="WHEAT", priority=100))
            # Outer zone: plant based on shop demand
            for pos in melon_tiles[:max(setup_alloc, 1)]:
                if best_outer_crop == "MELON" and seeds.get("MELON", 0) > 0:
                    setup_tasks.append(Task("PLANT_CROP", target=pos, item="MELON", priority=90))
                elif best_outer_crop == "STRAWBERRY" and seeds.get("STRAWBERRY", 0) > 0:
                    setup_tasks.append(Task("PLANT_CROP", target=pos, item="STRAWBERRY", priority=90))
                elif seeds.get("WHEAT", 0) > 0:
                    setup_tasks.append(Task("PLANT_CROP", target=pos, item="WHEAT", priority=85))

        tasks.extend(setup_tasks[:max(setup_alloc, 1)])  # at least 1 setup task

        tasks.sort(key=lambda t: t.priority, reverse=True)
        return tasks

    def _fib(self, n):
        a, b = 1, 1
        for _ in range(n):
            a, b = b, a + b
        return a


# ═══════════════════════════════════════════════════════════════════════════════
# GAME AGENT: connects Master + SubAgents
# ═══════════════════════════════════════════════════════════════════════════════

class GameAgent:
    def __init__(self):
        self.master = Master()
        self.agents: List[SubAgent] = []

    def __call__(self, obs, cfg=None):
        player = obs["player"]
        farm = obs["farms"][player]
        priv = obs.get("private", {})
        hands = farm.get("hands", [])
        num_workers = 1 + len(hands)
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)

        # --- Logging: new day summary ---
        if hour == 0:
            tiles = farm["tiles"]
            bs = len(tiles)
            na = sum(1 for y in range(bs) for x in range(bs)
                     if isinstance(tiles[y][x], dict) and "animal" in tiles[y][x])
            np = sum(1 for y in range(bs) for x in range(bs)
                     if isinstance(tiles[y][x], dict) and tiles[y][x].get("kind") == "PLANT")
            LOG.new_day(day, farm["money"], na, np, len(hands), priv.get("shed", {}))

        # Resize agent pool
        while len(self.agents) < num_workers:
            self.agents.append(SubAgent())
        self.agents = self.agents[:num_workers]

        # Master decides market orders
        market_orders = self.master.decide_market(obs)
        LOG.log_market(market_orders)

        # Count idle agents
        idle_count = sum(1 for a in self.agents if a.idle)

        # Master generates tasks for idle workers
        if idle_count > 0:
            tasks = self.master.decide_tasks(obs, idle_count)
            # Assign tasks to idle agents (highest priority first)
            task_idx = 0
            for a in self.agents:
                if a.idle and task_idx < len(tasks):
                    a.assign(tasks[task_idx])
                    task_idx += 1

        # All agents execute one step
        bs = len(farm["tiles"])
        shed = priv.get("shed", {})
        seeds = priv.get("seeds", {})
        inv_list = priv.get("inventories", [{}])
        positions = [tuple(farm["farmer"])] + [tuple(h) for h in hands]

        farmer_action = ["PASS"]
        hand_actions = []

        for i, ag in enumerate(self.agents):
            pos = positions[i] if i < len(positions) else (bs // 2, bs // 2)
            inv = inv_list[i] if i < len(inv_list) else {}
            action = ag.step(pos, farm, inv, shed, seeds, bs)
            LOG.log_action(i, action, ag.task.kind if ag.task else None)
            if i == 0:
                farmer_action = action
            else:
                hand_actions.append(action)

        return {
            "farmer": farmer_action,
            "hands": hand_actions,
            "market": market_orders,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

_game_agent = None

def agent(obs, cfg=None):
    global _game_agent
    if _game_agent is None:
        _game_agent = GameAgent()
    return _game_agent(obs, cfg)
