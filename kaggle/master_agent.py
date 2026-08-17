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

TD = 30


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

        # ── BUILD_PASTURE: walk to target → build ──
        elif k == "BUILD_PASTURE":
            target = self.task.target
            if target is None:
                self.done(); return ["PASS"]
            if pos == target:
                if farm["tiles"][target[1]][target[0]] is None:
                    self.done(); return ["BUILD_PASTURE"]
                self.done(); return ["PASS"]
            return [self._move(pos, target, bs)]

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
    Macro strategy:
    - COW is king ($180/day). Buy cows steadily, not all-in.
    - MELON is best crop ($250 base, 6 yield). Plant early.
    - Build pastures NEAR shed center (1-2 tiles away).
    - Sell small batches (wool/melon have sq curves — crash fast).
    - Don't all-in day 0. Buy seeds + a few animals. Let crops bootstrap income.
    """

    def __init__(self):
        self.target_cows = 10
        self.target_sheep = 4

    def decide_market(self, obs) -> list:
        """Master reads market state and generates orders."""
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

        # Count animals
        na = sum(1 for y in range(bs) for x in range(bs)
                 if isinstance(tiles[y][x], dict) and "animal" in tiles[y][x])
        in_shed = shed.get("COW", 0) + shed.get("SHEEP", 0)

        orders = []
        spent = 0

        # ── Last day: liquidate ──
        if remaining <= 0:
            for prod in ["WHEAT", "FERTILIZER", "MILK", "WOOL", "MELON",
                         "STRAWBERRY", "CARROT", "EGG"]:
                q = shed.get(prod, 0)
                if q > 0 and len(orders) < 10:
                    orders.append(["SELL", prod, min(q, 10)])
            return orders[:10]

        # ── SELL products (small batches to avoid crashing price) ──
        for prod in ["FERTILIZER", "MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "CARROT"]:
            q = shed.get(prod, 0)
            if q > 0 and len(orders) < 10:
                # Wool/Melon have sq curve — sell max 3-4 at a time
                max_sell = 4 if prod in ("WOOL", "MELON") else 10
                orders.append(["SELL", prod, min(q, max_sell)])

        # Sell excess wheat (keep enough for feed)
        wheat_keep = (na + in_shed) * 2 + 8
        wheat_excess = shed.get("WHEAT", 0) - wheat_keep
        if wheat_excess > 4 and len(orders) < 10:
            orders.append(["SELL", "WHEAT", min(int(wheat_excess), 8)])

        # ── HIRE workers (proportional to ACTUAL WORK available) ──
        if hour == 0 and nh == 0 and remaining > 0:
            # Count actual jobs that need doing TODAY
            jobs_today = 0
            jobs_today += na  # each animal needs feed+care (farmer can do ~4 solo)
            jobs_today += in_shed  # animals to place
            # Count plantable tiles
            n_plantable = 0
            for y in range(bs):
                for x in range(bs):
                    if tiles[y][x] is None:
                        qn = ("N" if y < bs//2 else "S") + ("W" if x < bs//2 else "E")
                        if qn in set(farm.get("unlocked_quadrants", ["NW"])):
                            n_plantable += 1
            plant_seeds = sum(seeds.get(c, 0) for c in ["WHEAT", "MELON", "STRAWBERRY", "CARROT"])
            jobs_today += min(n_plantable, plant_seeds)  # planting work

            if day == 1:
                need = 0  # farmer solo day 1 (save money for wheat)
            else:
                # 1 worker per ~6 jobs (they have 24 hours, each job ~4 turns avg)
                need = max(0, (jobs_today - 4) // 5)  # subtract 4 (farmer handles those)
                need = min(need, 8)  # cap at 8

            for i in range(need):
                cost = self._fib(hires_today + i)
                if money - spent >= cost + 30 and len(orders) < 10:
                    orders.append(["HIRE"])
                    spent += cost

        # ── BUY ANIMALS (steady growth, not all-in) ──
        if in_shed == 0 and remaining > 5 and len(orders) < 10:
            total = na + in_shed
            # Buy 1 cow at a time when we can afford it + feed
            if total < self.target_cows and money - spent >= 500:
                orders.append(["BUY_ANIMAL", "COW", 1])
                spent += 400
            elif total < self.target_cows + self.target_sheep and money - spent >= 600:
                orders.append(["BUY_ANIMAL", "SHEEP", 1])
                spent += 500

        # ── BUY WHEAT (feed buffer — ALWAYS maintain) ──
        if na > 0 and len(orders) < 10:
            wheat_have = shed.get("WHEAT", 0)
            wheat_want = na * 2 + 4  # 2 per animal + buffer
            deficit = wheat_want - wheat_have
            if deficit > 0:
                wp = max(1, int(prices.get("WHEAT", 25)))
                qty = min(deficit, 8, max(0, int((money - spent - 50) / wp)))
                if qty > 0:
                    orders.append(["BUY_PRODUCT", "WHEAT", qty])
                    spent += wp * qty

        # ── BUY SEEDS (melon early, wheat always, strawberry mid-game) ──
        if len(orders) < 10:
            if day <= 2 and seeds.get("MELON", 0) < 8 and money - spent >= 640:
                orders.append(["BUY_SEED", "MELON", 8])
                spent += 640
            if seeds.get("WHEAT", 0) < 5 and money - spent >= 50 and len(orders) < 10:
                orders.append(["BUY_SEED", "WHEAT", 5])
                spent += 50
            if day >= 5 and seeds.get("STRAWBERRY", 0) < 3 and money - spent >= 300 and len(orders) < 10:
                orders.append(["BUY_SEED", "STRAWBERRY", 3])
                spent += 300

        # ── BUY LAND (when we need space and can afford) ──
        if nq == 1 and na >= 4 and money - spent >= 1200 and remaining > 12 and len(orders) < 10:
            orders.append(["BUY_LAND"])
            spent += 1000
        elif nq == 2 and na >= 8 and money - spent >= 2500 and remaining > 8 and len(orders) < 10:
            orders.append(["BUY_LAND"])
            spent += 2000

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

        tasks = []

        # P200: Feed unfed animals (CRITICAL — escape after 2 unfed days)
        for pos in unfed:
            tasks.append(Task("FEED_CYCLE", target=pos, priority=200))

        # P190: Care for fed animals (bonus yield)
        for pos in uncared:
            tasks.append(Task("FEED_CYCLE", target=pos, priority=190))

        # P180: Place animals from shed (stranded = lost income)
        if in_shed > 0:
            if empty_pastures:
                for a in ["COW", "SHEEP"]:
                    if shed.get(a, 0) > 0:
                        tasks.append(Task("PLACE_ANIMAL", item=a, priority=180))
            else:
                # Need to build pasture first — NEAR shed
                if empty_tiles:
                    tasks.append(Task("BUILD_PASTURE", target=empty_tiles[0], priority=185))

        # P160: Collect fertilizer ($100 each!)
        for pos in fert_avail:
            tasks.append(Task("COLLECT_FERT", target=pos, priority=160))

        # P150: Harvest animals (milk/wool/egg)
        for pos in harvestable:
            tasks.append(Task("HARVEST", target=pos, priority=150))

        # P120: Water plants (prevents death, enables yield)
        for pos in unwatered:
            tasks.append(Task("WATER", target=pos, priority=120))

        # P110: Harvest ready plants
        for pos in harv_plants:
            tasks.append(Task("HARVEST", target=pos, priority=110))

        # P60: Plant crops (melon > strawberry > wheat)
        if remaining > 3 and len(empty_tiles) > 0:
            crop = None
            if seeds.get("MELON", 0) > 0 and remaining >= 13:
                crop = "MELON"
            elif seeds.get("STRAWBERRY", 0) > 0 and remaining >= 10:
                crop = "STRAWBERRY"
            elif seeds.get("WHEAT", 0) > 0:
                crop = "WHEAT"
            if crop:
                # Don't plant on tiles reserved for future pastures
                reserved = max(0, self.target_cows + self.target_sheep - na - in_shed - len(empty_pastures))
                for pos in empty_tiles[reserved:reserved + num_idle]:
                    tasks.append(Task("PLANT_CROP", target=pos, item=crop, priority=60))

        # Sort by priority
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

        # Resize agent pool
        while len(self.agents) < num_workers:
            self.agents.append(SubAgent())
        self.agents = self.agents[:num_workers]

        # Master decides market orders
        market_orders = self.master.decide_market(obs)

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
