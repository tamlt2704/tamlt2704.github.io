"""
3-Layer Architecture: Master → Group Leaders → Workers
=======================================================
Layer 1 — MASTER: Macro economy (market orders, hires, high-level goals)
Layer 2 — GROUP LEADERS: Tactical planning (animal leader, crop leader, logistics)
Layer 3 — WORKERS: Multi-turn execution with BFS pathfinding, mixed duties

Based on top-player analysis ($96k avg, 36 games):
- Animals in tight ring around shed (dist 0-2)
- Farmer = dedicated feeder (FEED+CARE circuit)
- Hands = water/harvest/collect/plant
- 12 hires/day from day 7, sell ALL fertilizer immediately
"""
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict
import sys

TD = 30


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

class Log:
    def __init__(self):
        self.day = -1
        self.data = {}
    def new_day(self, day, money, na, np, nh):
        if self.day >= 0:
            d = self.data
            sells = " ".join("%s:%d" % (k,v) for k,v in sorted(d.get('sells',{}).items(), key=lambda x:-x[1])[:5])
            buys = " ".join("%s:%d" % (k,v) for k,v in sorted(d.get('buys',{}).items(), key=lambda x:-x[1])[:4])
            print("D%02d $%5.0f|A:%d P:%d H:%d|Fed:%d Fert:%d|S[%s]B[%s]" % (
                self.day, d.get('m',0), d.get('a',0), d.get('p',0), d.get('h',0),
                d.get('fed',0), d.get('fert',0), sells, buys), file=sys.stderr)
        self.day = day
        self.data = {'m': money, 'a': na, 'p': np, 'h': nh, 'fed': 0, 'fert': 0, 'sells': {}, 'buys': {}}
    def sell(self, item, qty):
        self.data['sells'][item] = self.data['sells'].get(item, 0) + qty
    def buy(self, item, qty):
        self.data['buys'][item] = self.data['buys'].get(item, 0) + qty
    def fed(self): self.data['fed'] = self.data.get('fed', 0) + 1
    def fert(self): self.data['fert'] = self.data.get('fert', 0) + 1

LOG = Log()


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def bfs_move(src, dst, bs):
    """BFS shortest path, return first step direction. All tiles passable."""
    if src == dst:
        return "PASS"
    parent = {src: None}
    q = deque([src])
    while q:
        cx, cy = q.popleft()
        if (cx, cy) == dst:
            break
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            nx, ny = cx+dx, cy+dy
            if 0 <= nx < bs and 0 <= ny < bs and (nx, ny) not in parent:
                parent[(nx, ny)] = (cx, cy)
                q.append((nx, ny))
    if dst not in parent:
        return "PASS"
    cur = dst
    while parent[cur] != src:
        cur = parent[cur]
    dx, dy = cur[0]-src[0], cur[1]-src[1]
    return {(1,0):"EAST",(-1,0):"WEST",(0,1):"SOUTH",(0,-1):"NORTH"}.get((dx,dy),"PASS")

def dist(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

SHED_TILES = [(5,5),(4,5),(5,4),(4,4)]

def nearest_shed(pos):
    return min(SHED_TILES, key=lambda s: dist(pos, s))

def is_shed_adj(pos):
    return pos in SHED_TILES


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 3: WORKER — executes multi-turn tasks autonomously
# ═══════════════════════════════════════════════════════════════════════════════

class Worker:
    def __init__(self):
        self.task = None   # (kind, params)
        self.phase = 0
        self.target = None

    @property
    def idle(self):
        return self.task is None

    def assign(self, task, target=None):
        self.task = task
        self.phase = 0
        self.target = target

    def done(self):
        self.task = None
        self.phase = 0
        self.target = None

    def step(self, pos, tiles, inv, shed, seeds, bs):
        """Execute one turn. Returns action list."""
        if self.task is None:
            return ["PASS"]

        tile_here = tiles[pos[1]][pos[0]] if 0<=pos[0]<bs and 0<=pos[1]<bs else None

        # Opportunistic: water a dry plant we're standing on (free value!)
        if (tile_here and isinstance(tile_here, dict) and tile_here.get("kind") == "PLANT"
                and not tile_here.get("watered_today") and self.task != "WATER_ONE"):
            return ["WATER"]

        k = self.task

        # ── FEED_CIRCUIT: pickup wheat → walk animals → feed+care each → drop ──
        if k == "FEED_CIRCUIT":
            return self._feed_circuit(pos, tiles, inv, shed, bs)

        # ── WATER_RUN: find unwatered → water → find next → water → ... ──
        # NEVER stop until all reachable plants are watered!
        elif k == "WATER_RUN":
            # Priority: 1) urgent (will die tomorrow) 2) high-value crops first
            # Melon($250) > Strawberry($120) > Carrot($35) > Wheat($25)
            CROP_VALUE = {"MELON": 4, "STRAWBERRY": 3, "CARROT": 2, "WHEAT": 1}
            best_target = None
            best_score = -1
            for y in range(bs):
                for x in range(bs):
                    t = tiles[y][x]
                    if not isinstance(t, dict) or t.get("kind") != "PLANT": continue
                    if t.get("watered_today"): continue
                    # Score: urgent(10) + crop_value(1-4) - distance*0.1
                    score = 0
                    if t.get("consecutive_unwatered", 0) > 0:
                        score += 10  # URGENT — will die!
                    score += CROP_VALUE.get(t.get("crop", ""), 1)
                    score -= dist(pos, (x, y)) * 0.1  # slight distance penalty
                    if score > best_score:
                        best_score = score
                        best_target = (x, y)
            if best_target is None:
                self.done(); return ["PASS"]
            if pos == best_target:
                return ["WATER"]  # chain — find next on next turn
            return [bfs_move(pos, best_target, bs)]

        # ── HARVEST_RUN: find harvestable → walk → harvest → find next → ... ──
        elif k == "HARVEST_RUN":
            target = self._nearest_tile(pos, tiles, bs,
                        cond=lambda t: t.get("yield_units", 0) > 0)
            if target is None:
                self.done(); return ["PASS"]
            if pos == target:
                return ["HARVEST"]  # don't mark done — chain to next
            return [bfs_move(pos, target, bs)]

        # ── COLLECT_RUN: collect fertilizer → deliver to plant OR shed ──
        # Smart routing: collect from animal, then fertilize nearest premium plant
        # Only drop at shed if no plants need fertilizing
        elif k == "COLLECT_RUN":
            if self.phase == 0:
                # Find animal with fertilizer to collect
                target = self._nearest_tile(pos, tiles, bs, has_animal=True,
                            cond=lambda t: t.get("fertilizer_available"))
                if target is None:
                    # No fert to collect — if carrying fert, deliver to plant
                    if inv.get("FERTILIZER", 0) > 0:
                        self.phase = 2  # go fertilize a plant
                    else:
                        self.done(); return ["PASS"]
                elif pos == target:
                    self.phase = 1; LOG.fert(); return ["COLLECT_FERTILIZER"]
                else:
                    return [bfs_move(pos, target, bs)]
            if self.phase == 1:
                # Just collected — deliver to plant ONLY if all plants are already watered
                # Otherwise just drop at shed (don't waste time on detour)
                all_watered = not any(
                    isinstance(tiles[y][x], dict) and tiles[y][x].get("kind") == "PLANT"
                    and not tiles[y][x].get("watered_today")
                    for y in range(bs) for x in range(bs))
                
                if inv.get("FERTILIZER", 0) > 0 and all_watered:
                    plant_target = self._nearest_tile(pos, tiles, bs, kind="PLANT",
                        cond=lambda t: t.get("crop") in ("MELON", "STRAWBERRY")
                        and t.get("fertilized_until_day", -1) < 0)
                    if plant_target and dist(pos, plant_target) <= 3:
                        self.phase = 2
                    else:
                        self.phase = 3  # too far, just go shed
                else:
                    self.phase = 3  # plants need water, don't detour
                return ["PASS"]
            if self.phase == 2:
                # Deliver fertilizer to a plant
                plant_target = self._nearest_tile(pos, tiles, bs, kind="PLANT",
                    cond=lambda t: t.get("crop") in ("MELON", "STRAWBERRY", "WHEAT")
                    and t.get("fertilized_until_day", -1) < 0)
                if plant_target is None or inv.get("FERTILIZER", 0) <= 0:
                    self.phase = 3; return ["PASS"]  # no target, go shed
                if pos == plant_target:
                    # Fertilize! Then look for more work
                    self.phase = 0  # loop back to collect more
                    return ["FERTILIZE"]
                return [bfs_move(pos, plant_target, bs)]
            if self.phase == 3:
                # Go shed to drop remaining items
                if is_shed_adj(pos):
                    self.done(); return ["DROP"]
                return [bfs_move(pos, nearest_shed(pos), bs)]
            # Fallback
            if is_shed_adj(pos):
                self.done(); return ["DROP"]
            return [bfs_move(pos, nearest_shed(pos), bs)]

        # ── BUILD_PLACE: walk to tile → build → pickup animal → place ──
        elif k == "BUILD_PLACE":
            animal = self.target or "COW"
            if self.phase == 0:
                # Pickup animal from shed
                if inv.get(animal, 0) > 0:
                    self.phase = 1
                elif is_shed_adj(pos) and shed.get(animal, 0) > 0:
                    self.phase = 1; return ["PICKUP", animal, 1]
                else:
                    return [bfs_move(pos, nearest_shed(pos), bs)]
            if self.phase == 1:
                # Find empty tile NEAR SHED for pasture (animals go inner ONLY)
                target = self._nearest_inner(pos, tiles, bs)
                if target is None:
                    self.done(); return ["PASS"]  # wait — don't build on plant tiles
                if target is None:
                    self.done(); return ["PASS"]
                if pos == target:
                    self.phase = 2; return ["BUILD_PASTURE"]
                return [bfs_move(pos, target, bs)]
            if self.phase == 2:
                # Place animal
                if inv.get(animal, 0) > 0:
                    self.done(); return ["PLACE", animal]
                self.done(); return ["PASS"]

        # ── PLACE_ANIMAL: pickup → walk to empty structure → place ──
        elif k == "PLACE_ANIMAL":
            animal = self.target or "COW"
            if self.phase == 0:
                if inv.get(animal, 0) > 0:
                    self.phase = 1
                elif is_shed_adj(pos) and shed.get(animal, 0) > 0:
                    self.phase = 1; return ["PICKUP", animal, 1]
                else:
                    return [bfs_move(pos, nearest_shed(pos), bs)]
            if self.phase == 1:
                target = self._nearest_tile(pos, tiles, bs, kind="PASTURE",
                            cond=lambda t: "animal" not in t)
                if target is None:
                    self.done(); return ["PASS"]
                if pos == target:
                    self.done(); return ["PLACE", animal]
                return [bfs_move(pos, target, bs)]

        # ── PLANT_ONE: walk to empty → plant → walk to next → plant → ... ──
        # Chains until out of seeds or empty tiles (like WATER_RUN)
        # ── PLANT_ONE: plant on outer tiles only (inner = animals) ──
        # ── PLANT_ONE: go to ASSIGNED tile and plant ──
        elif k == "PLANT_ONE":
            # Target format: "CROP:X:Y" from PlantingLeader
            parts = (self.target or "WHEAT:0:0").split(":")
            crop = parts[0] if parts else "WHEAT"
            tx = int(parts[1]) if len(parts) > 1 else 0
            ty = int(parts[2]) if len(parts) > 2 else 0
            target = (tx, ty)
            if seeds.get(crop, 0) <= 0:
                self.done(); return ["PASS"]
            # If at target tile and it is empty → plant
            if pos == target:
                tile_here = tiles[pos[1]][pos[0]]
                if tile_here is None:
                    self.done(); return ["PLANT", crop]
                else:
                    self.done(); return ["PASS"]  # tile taken
            # Walk to assigned tile
            return [bfs_move(pos, target, bs)]

        # ── SELL_DROP: go to shed → drop ──
        elif k == "SELL_DROP":
            if is_shed_adj(pos):
                self.done(); return ["DROP"]
            return [bfs_move(pos, nearest_shed(pos), bs)]

        # ── DIG_WEED: walk to weed → dig ──
        # ── DIG_WEED: chain through all weeds ──
        elif k == "DIG_WEED":
            target = self._nearest_tile(pos, tiles, bs, kind="WEED")
            if target is None:
                self.done(); return ["PASS"]
            if pos == target:
                return ["DIG"]  # chain — find next weed next turn
            return [bfs_move(pos, target, bs)]


        self.done()
        return ["PASS"]

    def _feed_circuit(self, pos, tiles, inv, shed, bs):
        """Farmer's dedicated FEED+CARE circuit."""
        if self.phase == 0:
            # Get wheat
            if inv.get("WHEAT", 0) > 0:
                self.phase = 1
            elif is_shed_adj(pos) and shed.get("WHEAT", 0) > 0:
                self.phase = 1
                return ["PICKUP", "WHEAT", min(8, shed.get("WHEAT", 0))]
            else:
                return [bfs_move(pos, nearest_shed(pos), bs)]

        if self.phase == 1:
            # Find nearest unfed animal
            target = self._nearest_tile(pos, tiles, bs, has_animal=True,
                        cond=lambda t: not t.get("fed_today"))
            if target is None:
                # All fed — find uncared
                target = self._nearest_tile(pos, tiles, bs, has_animal=True,
                            cond=lambda t: t.get("fed_today") and not t.get("cared_today"))
                if target is None:
                    self.phase = 9; return ["PASS"]  # done
                if pos == target:
                    return ["CARE"]
                return [bfs_move(pos, target, bs)]
            if pos == target:
                t = tiles[pos[1]][pos[0]]
                if isinstance(t, dict) and "animal" in t:
                    if not t.get("fed_today") and inv.get("WHEAT", 0) > 0:
                        self.phase = 2; LOG.fed(); return ["FEED"]
                    elif t.get("fed_today") and not t.get("cared_today"):
                        self.phase = 3; return ["CARE"]
                self.phase = 4; return ["PASS"]
            return [bfs_move(pos, target, bs)]

        if self.phase == 2:
            # Just fed → CARE same tile
            t = tiles[pos[1]][pos[0]]
            if isinstance(t, dict) and "animal" in t and t.get("fed_today") and not t.get("cared_today"):
                self.phase = 4; return ["CARE"]
            self.phase = 4; return ["PASS"]

        if self.phase == 3:
            self.phase = 4; return ["PASS"]

        if self.phase == 4:
            # Next animal
            if inv.get("WHEAT", 0) > 0:
                nxt = self._nearest_tile(pos, tiles, bs, has_animal=True,
                          cond=lambda t: not t.get("fed_today"))
                if nxt and nxt != pos:
                    self.phase = 1; return [bfs_move(pos, nxt, bs)]
                nxt = self._nearest_tile(pos, tiles, bs, has_animal=True,
                          cond=lambda t: t.get("fed_today") and not t.get("cared_today"))
                if nxt:
                    if nxt == pos: return ["CARE"]
                    self.phase = 1; return [bfs_move(pos, nxt, bs)]
            self.phase = 9; return ["PASS"]

        if self.phase == 9:
            # Return to shed, drop
            if is_shed_adj(pos):
                if sum(v for k,v in inv.items() if k != "WHEAT") > 0:
                    self.done(); return ["DROP"]
                self.done(); return ["PASS"]
            return [bfs_move(pos, nearest_shed(pos), bs)]

        self.done()
        return ["PASS"]

    def _nearest_tile(self, pos, tiles, bs, kind=None, has_animal=False, cond=None):
        best, best_d = None, 999
        for y in range(bs):
            for x in range(bs):
                t = tiles[y][x]
                if not isinstance(t, dict): continue
                if kind and t.get("kind") != kind and not (has_animal and "animal" in t): continue
                if has_animal and "animal" not in t: continue
                if cond and not cond(t): continue
                d = dist(pos, (x,y))
                if d < best_d: best_d = d; best = (x,y)
        return best

    def _nearest_empty(self, pos, tiles, bs):
        # Find empty PLANT tile closest to SHED CENTER (creates round ring)
        # Primary sort: distance from shed center (fills ring evenly)
        # Secondary: distance from worker (reachable)
        best, best_d = None, 999
        for y in range(bs):
            for x in range(bs):
                if tiles[y][x] is not None: continue
                # Score: primarily by shed distance (round ring), tiebreak by worker dist
                shed_dist = abs(x - 4) + abs(y - 4)
                worker_dist = dist(pos, (x, y))
                d = shed_dist * 3 + worker_dist  # strong shed-center bias
                if d < best_d: best_d = d; best = (x, y)
        return best

    def _nearest_inner(self, pos, tiles, bs):
        # Find nearest empty ANIMAL tile (inner layer per Master's farm plan)
        best, best_d = None, 999
        for y in range(bs):
            for x in range(bs):
                if tiles[y][x] is not None: continue
                if not Master.is_animal_tile(x, y): continue  # only animal tiles
                d = dist(pos, (x, y))
                if d < best_d: best_d = d; best = (x, y)
        return best


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 2: GROUP LEADERS
# ═══════════════════════════════════════════════════════════════════════════════

class AnimalLeader:
    """Plans animal operations: who feeds, who collects, who builds."""
    def plan(self, tiles, bs, shed, na, in_shed, empty_pastures):
        tasks = []
        # Farmer does FEED_CIRCUIT (handles up to ~10 animals solo)
        if na > 0:
            tasks.append(("FEED_CIRCUIT", None, 200))

        # Priority 2: Place animals stuck in shed
        if in_shed > 0:
            animal = "COW" if shed.get("COW", 0) > 0 else "SHEEP"
            if empty_pastures:
                tasks.append(("PLACE_ANIMAL", animal, 195))
            else:
                tasks.append(("BUILD_PLACE", animal, 195))

        # Priority 3: Collect fertilizer (max 2 workers)
        fert_count = sum(1 for y in range(bs) for x in range(bs)
                         if isinstance(tiles[y][x], dict) and "animal" in tiles[y][x]
                         and tiles[y][x].get("fertilizer_available"))
        if fert_count > 0:
            tasks.append(("COLLECT_RUN", None, 180))
            if fert_count > 5:
                tasks.append(("COLLECT_RUN", None, 178))

        # Priority 4: Harvest animal products (max 1)
        has_harvest = any(isinstance(tiles[y][x], dict) and "animal" in tiles[y][x]
                         and tiles[y][x].get("yield_units", 0) > 0
                         for y in range(bs) for x in range(bs))
        if has_harvest:
            tasks.append(("HARVEST_RUN", None, 170))

        return tasks


class CropLeader:
    """Plans MAINTENANCE: water and harvest. NEVER let plants dry!
    
    RULE: A plant that misses 2 days of water DIES (becomes weed).
    Watering is the HIGHEST priority after animal feeding.
    Every dead plant = wasted seed + wasted turns + lost revenue.
    
    Priority hierarchy:
      198 = URGENT water (consecutive_unwatered > 0, dies tomorrow!)
      155 = NORMAL water (not watered yet today, will become urgent tomorrow)
      140 = HARVEST (ready crops, no urgency — they don't die from waiting)
    """
    def plan(self, tiles, bs):
        tasks = []
        urgent_water = 0
        normal_water = 0
        harvestable = 0

        for y in range(bs):
            for x in range(bs):
                t = tiles[y][x]
                if not isinstance(t, dict) or t.get("kind") != "PLANT": continue
                if not t.get("watered_today"):
                    if t.get("consecutive_unwatered", 0) > 0:
                        urgent_water += 1
                    else:
                        normal_water += 1
                if t.get("yield_units", 0) > 0:
                    harvestable += 1

        # URGENT: plants that WILL DIE tomorrow if not watered TODAY
        if urgent_water > 0:
            urgent_tasks = max(1, (urgent_water + 1) // 2)
            for i in range(urgent_tasks):
                tasks.append(("WATER_RUN", None, 198))

        # NORMAL: unwatered today — only assign if there ARE unwatered plants
        # Don't generate empty water tasks that block workers from planting!
        if normal_water > 0:
            normal_tasks = max(1, (normal_water + 2) // 3)
            for i in range(normal_tasks):
                tasks.append(("WATER_RUN", None, 155))

        # HARVEST: ready crops. Lower priority — they don't die.
        if harvestable > 0:
            harvest_tasks = max(1, (harvestable + 2) // 3)
            for i in range(harvest_tasks):
                tasks.append(("HARVEST_RUN", None, 140))

        return tasks


class PlantingLeader:
    """Plans WHERE and WHAT to plant. Owns zone allocation and crop timing.
    
    Zone strategy (from top-player data):
    - Inner ring (dist 0-2 from shed): reserved for ANIMALS (don't plant here)
    - Middle zone (dist 3-4): WHEAT (fast cycle, feed infrastructure)
    - Outer zone (dist 5+): MELON / STRAWBERRY (premium, long cycle)
    
    Timing:
    - Day 0: plant melon (12 seeds, matures day 10)
    - Day 0-4: plant wheat (feed supply)
    - Day 5+: strawberry (ongoing revenue)
    - Day 21+: wheat/carrot only (fast crops that mature before end)
    - Day 27+: STOP PLANTING (nothing can mature)
    
    Replant rule: any empty tile in an unlocked quadrant should have a crop.
    """
    
    # Animal ring tiles (near shed). Only reserve what we STILL NEED.
    ANIMAL_RING = [(4,3),(5,3),(3,3),(6,3),(4,2),(5,2),(3,4),(6,4),
                   (2,4),(7,4),(3,5),(6,5)]

    def plan(self, tiles, bs, seeds, day, remaining, hour, unlocked_quads, prices=None):
        tasks = []

        if hour >= 22 or remaining <= 2 or day >= 28:
            return tasks

        total_seeds = sum(seeds.values())
        if total_seeds <= 0:
            return tasks

        # Count animals+pastures to determine how many tiles to reserve
        num_animals = sum(1 for y in range(bs) for x in range(bs)
                         if isinstance(tiles[y][x], dict) and 'animal' in tiles[y][x])
        num_pastures = sum(1 for y in range(bs) for x in range(bs)
                          if isinstance(tiles[y][x], dict) and tiles[y][x].get('kind') in ('COOP','PASTURE'))
        # Only reserve tiles we STILL NEED for future pastures
        pastures_still_needed = max(0, 14 - num_animals - num_pastures)
        reserved = set(self.ANIMAL_RING[:pastures_still_needed])

        # Scan plantable tiles (empty + unlocked + not reserved for animals)
        plantable = []
        for y in range(bs):
            for x in range(bs):
                if tiles[y][x] is not None:
                    continue
                qn = ('N' if y < bs//2 else 'S') + ('W' if x < bs//2 else 'E')
                if qn not in unlocked_quads:
                    continue
                if (x, y) in reserved:
                    continue
                if not Master.is_plant_tile(x, y, day):
                    continue
                plantable.append((x, y))
        
        if not plantable:
            return tasks
        
        # Decide WHAT to plant based on zone and timing
        # Sort tiles: inner (near shed) → wheat, outer → premium
        shed_center = (4, 4)
        plantable.sort(key=lambda p: dist(p, shed_center))
        
        # Determine crop priority for this day
        crop_plan = self._decide_crops(seeds, day, remaining, prices or {})
        
        # PlantingLeader assigns SPECIFIC tiles to workers (no self-navigation)
        # Each task carries (crop, target_tile) so worker goes directly there
        planted_count = 0
        for tile_pos in plantable:
            if planted_count >= 2: break  # max 2 planters (rest water existing)
            tile_dist = dist(tile_pos, shed_center)
            crop = self._pick_crop_for_zone(tile_dist, crop_plan, seeds, remaining, day)
            if crop and seeds.get(crop, 0) > planted_count:
                # Target = "CROP:X:Y" encoded in the target field
                target_str = "%s:%d:%d" % (crop, tile_pos[0], tile_pos[1])
                tasks.append(("PLANT_ONE", target_str, 130))
                planted_count += 1
        
        # Weed clearing on prime tiles (blocks replanting)
        for y in range(bs):
            for x in range(bs):
                t = tiles[y][x]
                if isinstance(t, dict) and t.get("kind") == "WEED":
                    if (x, y) not in set(self.ANIMAL_RING):  # only clear non-animal tiles
                        tasks.append(("DIG_WEED", None, 135))
                        tasks.append(("DIG_WEED", None, 135))
        
        return tasks
    
    def _decide_crops(self, seeds, day, remaining, prices):
        """Market-aware crop selection. Plant what is PROFITABLE at current prices."""
        available = {}
        BASE = {"WHEAT": 25, "CARROT": 35, "MELON": 250, "STRAWBERRY": 120}
        MIN_DAYS = {"WHEAT": 3, "CARROT": 3, "MELON": 11, "STRAWBERRY": 12}

        for crop, base in BASE.items():
            if seeds.get(crop, 0) <= 0:
                continue
            if remaining < MIN_DAYS[crop]:
                continue

            price = prices.get(crop, base)
            price_ratio = price / max(base, 1)

            # Base priority by crop economics and timing
            if crop == "MELON":
                prio = 8 if day <= 5 else 3
            elif crop == "STRAWBERRY":
                prio = 7 if day >= 5 else 1
            elif crop == "CARROT":
                prio = 5
            else:
                prio = 4

            # Market signal: high price = scarcity = plant more!
            if price_ratio > 1.3:
                prio += 3
            elif price_ratio > 1.1:
                prio += 1
            elif price_ratio < 0.5:
                prio -= 4
            elif price_ratio < 0.7:
                prio -= 2

            if prio <= 0:
                continue
            if day >= 25 and crop not in ("WHEAT", "CARROT"):
                continue

            zone = "outer" if crop in ("MELON", "STRAWBERRY") else "inner"
            available[crop] = {"zone": zone, "priority": prio}

        return available

    
    def _pick_crop_for_zone(self, tile_dist, crop_plan, seeds, remaining, day=0):
        """Crop by distance + game phase.
        Early (day 0-5): wheat near center (fast cycle, feed, frees tile for animals)
        Mid+ (day 6+): melon/carrot everywhere (animals already placed, maximize value)
        """
        if day <= 5:
            # EARLY: wheat near center (quick harvest → convert tile to pasture)
            if tile_dist <= 3:
                if "WHEAT" in crop_plan and seeds.get("WHEAT", 0) > 0:
                    return "WHEAT"
            # Outer: melon (day-10 windfall)
            for crop in ["MELON", "CARROT", "WHEAT"]:
                if crop in crop_plan and seeds.get(crop, 0) > 0:
                    return crop
        else:
            # MID/LATE crop selection:
            # Day 6-10: still plant MELON (big $250 harvest, initial windfall)
            # Day 11+: STRAWBERRY preferred (keeps tile occupied 16 days, less replanting)
            if day <= 10 and remaining >= 11:
                for crop in ["MELON", "STRAWBERRY", "CARROT"]:
                    if crop in crop_plan and seeds.get(crop, 0) > 0:
                        return crop
            elif remaining >= 12:
                # After day 10: strawberry first (sustained, tile stays full)
                for crop in ["STRAWBERRY", "MELON", "CARROT"]:
                    if crop in crop_plan and seeds.get(crop, 0) > 0:
                        return crop
            elif remaining >= 11:
                for crop in ["MELON", "CARROT"]:
                    if crop in crop_plan and seeds.get(crop, 0) > 0:
                        return crop
            else:
                for crop in ["CARROT", "WHEAT"]:
                    if crop in crop_plan and seeds.get(crop, 0) > 0:
                        return crop
        # Fallback
        for crop in ["MELON", "CARROT", "STRAWBERRY", "WHEAT"]:
            if crop in crop_plan and seeds.get(crop, 0) > 0:
                return crop
        return None

class LogisticsLeader:
    """Handles shed overflow, weeds, and worker drops."""
    def plan(self, tiles, bs, inventories):
        tasks = []
        # Check if any worker is carrying stuff and should drop
        for i, inv in enumerate(inventories):
            if isinstance(inv, dict):
                carried = sum(v for k,v in inv.items() if k != "WHEAT")
                if carried > 3:
                    tasks.append(("SELL_DROP", None, 140))
                    break

        # Weed clearing
        has_weeds = any(isinstance(tiles[y][x], dict) and tiles[y][x].get("kind") == "WEED"
                       for y in range(bs) for x in range(bs))
        if has_weeds:
            tasks.append(("DIG_WEED", None, 50))

        return tasks


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 1: MASTER — Macro strategy + market orders
# ═══════════════════════════════════════════════════════════════════════════════

class Master:
    """Data-driven market strategy + farm layout plan.
    
    FARM PLAN (communicated to all leaders):
      Layer 0 — SHED: (4,4), (5,4), (4,5), (5,5) — access only
      Layer 1 — ANIMALS: tiles with dist 1-2 from shed center — pastures
      Layer 2 — PLANTS: all other unlocked tiles — crops
    
    The Master owns the plan. Leaders query it to know WHERE to build/plant.
    """
    
    # Fixed layout: which tiles are for animals vs plants
    SHED_CENTER = [(4, 4), (5, 4), (4, 5), (5, 5)]
    # Animal ring: tiles adjacent to shed (dist 1-2) — build pastures here
    # Animals within dist <= 3 from shed center (4,4). Spread across all quadrants.
    # When new land is bought, new animal tiles become available automatically.
    ANIMAL_TILES = [
        # Dist 1 (adjacent to shed)
        (3, 4), (4, 3), (5, 3), (6, 4),
        # Dist 2 
        (3, 3), (3, 5), (5, 5), (6, 5), (4, 6), (5, 6), (6, 3), (2, 4),
        # Dist 3 (max — don't go further, farmer circuit stays short)
        (2, 3), (3, 6), (6, 6), (6, 2),
    ]

    @classmethod
    def is_animal_tile(cls, x, y):
        """Should this tile have a pasture?"""
        return (x, y) in cls.ANIMAL_TILES or (x, y) in cls.SHED_CENTER
    
    @classmethod
    def is_plant_tile(cls, x, y, day=99):
        """Can this tile have a crop?
        Early game (day 0-3): ALL tiles can be planted (including animal tiles)
        Later: only non-animal tiles."""
        if (x, y) in cls.SHED_CENTER:
            return False
        if day <= 3:
            return True  # early: plant everywhere (wheat on inner, melon on outer)
        return not cls.is_animal_tile(x, y)

    def decide_market(self, obs):
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

        na = sum(1 for y in range(bs) for x in range(bs)
                 if isinstance(tiles[y][x], dict) and "animal" in tiles[y][x])
        in_shed = shed.get("COW", 0) + shed.get("SHEEP", 0)
        total_animals = na + in_shed

        orders = []
        spent = 0

        # === DAY 0 OPENING ===
        # 12 melon is critical for day-10 windfall ($3000+)
        # 12 wheat product ensures animals survive days 0-3 even with zero income
        # Day 1 hires 2 hands ($2 total) to water all 12 melons + wheat
        if day == 0 and hour <= 1 and total_animals == 0:
            return [["HIRE"],["HIRE"],["HIRE"],["HIRE"],["HIRE"],
                    ["BUY_ANIMAL","COW",2],["BUY_ANIMAL","SHEEP",2],
                    ["BUY_SEED","WHEAT",5],["BUY_SEED","MELON",8],
                    ["BUY_PRODUCT","WHEAT",16]]

        # === CRITICAL: BUY WHEAT FOR FEED (after sells so we have cash) ===
        # Moved back after SELL — sells generate cash to buy wheat with
        
        # === SELL ALL (every turn) ===
        for prod in ["FERTILIZER","MILK","WOOL","MELON","STRAWBERRY","EGG","CARROT"]:
            q = shed.get(prod, 0)
            if q > 0 and len(orders) < 10:
                orders.append(["SELL", prod, q])
                LOG.sell(prod, q)
        # Sell wheat ONLY excess beyond feed buffer
        wheat_keep = na * 2 + 6
        wheat_sell = shed.get("WHEAT", 0) - wheat_keep
        if wheat_sell > 0 and len(orders) < 10:
            orders.append(["SELL", "WHEAT", wheat_sell])
            LOG.sell("WHEAT", wheat_sell)

        # === LIQUIDATION ===
        if remaining <= 1:
            orders = []
            for prod in ["FERTILIZER","WHEAT","MILK","WOOL","MELON","STRAWBERRY","CARROT","EGG"]:
                q = shed.get(prod, 0)
                if q > 0 and len(orders) < 10:
                    orders.append(["SELL", prod, q])
            return orders[:10]


        # Account for sell revenue in budget (sells execute before buys)
        sell_revenue = int(sum(o[2] * prices.get(o[1], 50) for o in orders if o[0] == "SELL") * 0.7)
        spent -= sell_revenue  # effectively adds revenue to available budget

        # === HIRE (proportional to actual workload) ===
        # Workload: each animal needs ~2 actions/day, each plant needs ~1 action/day
        # Farmer handles 6 animal feeds. Hands handle the rest.
        # Rule: hire enough that total_workforce * 5 >= total_work
        if hour == 0 and nh == 0 and remaining > 0:
            n_plants = sum(1 for y in range(bs) for x in range(bs)
                          if isinstance(tiles[y][x], dict) and tiles[y][x].get("kind") == "PLANT")
            work_needed = na * 2 + n_plants + 5  # animals + plants + overhead
            # Each worker handles ~5 useful actions per day (50% movement overhead)
            workers_needed = max(2, (work_needed + 4) // 5)
            target = min(workers_needed, 12)  # cap at 12
            
            # Day 0 always 5 (opening), Day 1-2 minimum 3
            # Day 3-6: minimum 5 IF we can afford it (broke = hire less)
            # Day 7+: minimum 10
            if day == 0:
                target = 5
            elif day <= 2:
                target = max(target, 3)
            elif day <= 6:
                target = max(target, 5 if money - spent > 100 else 3)
            elif day >= 7:
                target = max(target, 10)
            
            for i in range(target):
                cost = self._fib(hires_today + i)
                if money - spent >= cost and len(orders) < 10:
                    orders.append(["HIRE"])
                    spent += cost

        # === BUY WHEAT FOR FEED (after sells give us cash) ===
        if na > 0 and len(orders) < 10:
            wheat_have = shed.get("WHEAT", 0)
            wheat_need = na * 2 + 6  # buffer for 2 days + safety
            deficit = wheat_need - wheat_have
            if deficit > 0:
                wp = max(1, int(prices.get("WHEAT", 25)))
                max_qty = max(0, (money - spent - 50) // wp)
                qty = min(deficit, max_qty)
                if qty > 0:
                    orders.append(["BUY_PRODUCT","WHEAT",qty]); spent += wp*qty
                    LOG.buy("WHEAT", qty)

        # === BUY ANIMALS (capacity-driven, not day-driven) ===
        # Rule: only buy animals if the farmer circuit can handle them
        # Farmer can FEED+CARE ~6 animals solo in 24 turns (2 actions + 2 moves each = ~4 turns/animal)
        # Each hired hand assigned to FEED_CYCLE can handle ~4 more animals
        # Also: only buy if we have enough wheat to feed them all
        if in_shed == 0 and total_animals < 10 and remaining > 8 and len(orders) < 10:
            # How many animals can we reliably service?
            # Farmer: ~8 animals per day (with tight ring layout)
            # Each extra FEED helper from hands: ~5 animals per day
            n_hands_available = nh if nh > 0 else (2 if day <= 2 else 4)
            feed_capacity = 8 + (n_hands_available // 2) * 5
            
            # Don't exceed what we can feed
            safe_target = min(10, feed_capacity)
            
            # Also don't buy if wheat supply is too low
            wheat_supply = shed.get("WHEAT", 0)
            can_afford_feed = wheat_supply >= total_animals  # at least 1 day buffer
            
            if total_animals < safe_target and can_afford_feed and money - spent >= 500:
                deficit = safe_target - total_animals
                if deficit >= 2 and money - spent >= 900:
                    orders.append(["BUY_ANIMAL","COW",2]); spent += 800
                    LOG.buy("COW", 2)
                elif deficit >= 1:
                    orders.append(["BUY_ANIMAL","COW",1]); spent += 400
                    LOG.buy("COW", 1)


        # === BUY SEEDS (state-driven, not day-driven) ===
        # On hour 0: hires take priority. On hour 1+: seeds get their own turn.
        # This prevents the 10-order cap from blocking seed purchases.
        if remaining > 3 and (hour >= 1 or len(orders) < 8):
            total_seeds = sum(seeds.values())
            
            # How many empty tiles can we plant? (demand for seeds)
            n_empty = sum(1 for y in range(bs) for x in range(bs) if tiles[y][x] is None)
            seeds_wanted = max(0, min(n_empty, 10) - total_seeds)
            
            if seeds_wanted > 0 and money - spent >= 50:
                # Score each crop by current market profitability
                BASE = {"WHEAT": 25, "CARROT": 35, "MELON": 250, "STRAWBERRY": 120}
                MIN_DAYS = {"WHEAT": 3, "CARROT": 3, "MELON": 11, "STRAWBERRY": 12}
                SEED_COST = {"WHEAT": 10, "CARROT": 20, "MELON": 80, "STRAWBERRY": 100}
                
                crop_scores = {}
                for crop, base in BASE.items():
                    if remaining < MIN_DAYS[crop]:
                        continue
                    price = prices.get(crop, base)
                    cost = SEED_COST[crop]
                    # ROI = (sell_price - seed_cost) / days_to_harvest
                    roi = (price - cost) / MIN_DAYS[crop]
                    # Bonus if price above base (scarcity)
                    if price > base * 1.2:
                        roi *= 1.5
                    # Penalty if price crashed
                    if price < base * 0.5:
                        roi *= 0.2
                    # Always need SOME wheat for animal feed
                    if crop == "WHEAT" and na > 0 and seeds.get("WHEAT", 0) < 3:
                        roi += 5  # feed insurance bonus
                    # STRAWBERRY: sustained ($480/16 days, keeps tile occupied)
                    if crop == "STRAWBERRY" and remaining >= 13:
                        roi *= 2.0
                    # MELON: big windfall early ($250 harvest day 10)
                    elif crop == "MELON" and remaining >= 12:
                        roi *= 1.8
                    crop_scores[crop] = roi
                
                if crop_scores:
                    # Buy top 2 crops by score
                    ranked = sorted(crop_scores, key=crop_scores.get, reverse=True)
                    budget_for_seeds = int((money - spent) * 0.3)  # max 30% on seeds
                    
                    for crop in ranked[:2]:
                        cost = SEED_COST[crop]
                        qty = min(seeds_wanted, 6, budget_for_seeds // max(cost, 1))
                        if qty > 0 and money - spent >= cost * qty and len(orders) < 10:
                            orders.append(["BUY_SEED", crop, qty])
                            spent += cost * qty
                            seeds_wanted -= qty

        # === BUY LAND (only when actually needed) ===
        # Expand ONLY when: animals stuck in shed with no inner tile available,
        # OR zero empty plant tiles and seeds to plant.
        # Don't expand just because we can afford it — use current land fully first.
        if len(orders) < 10 and nq < 4:
            land_costs = [1000, 2000, 4000]
            cost = land_costs[nq - 1] if nq <= 3 else 99999
            n_empty = sum(1 for y in range(bs) for x in range(bs) if tiles[y][x] is None)
            animals_stuck = in_shed > 0 and self._nearest_inner_available(tiles, bs) is None
            no_plant_space = n_empty == 0 and sum(seeds.values()) > 0
            # With $10k+, expand to grow the business
            flush_cash = money - spent >= 10000
            
            if (animals_stuck or no_plant_space or flush_cash) and money - spent >= cost + 500:
                orders.append(["BUY_LAND"]); spent += cost

        # Reorder: HIRE first on hour 0 (workers get max turns of work)
        if hour == 0:
            hire_orders = [o for o in orders if o[0] == "HIRE"]
            other_orders = [o for o in orders if o[0] != "HIRE"]
            orders = hire_orders + other_orders

        return orders[:10]

    def _nearest_inner_available(self, tiles, bs):
        """Check if any ANIMAL_TILE is empty (available for pasture)."""
        for x, y in self.ANIMAL_TILES:
            if 0 <= x < bs and 0 <= y < bs and tiles[y][x] is None:
                return (x, y)
        return None

    def _fib(self, n):
        a, b = 1, 1
        for _ in range(n):
            a, b = b, a+b
        return a


# ═══════════════════════════════════════════════════════════════════════════════
# GAME AGENT: Orchestrates all 3 layers
# ═══════════════════════════════════════════════════════════════════════════════

class GameAgent:
    def __init__(self):
        self.master = Master()
        self.animal_leader = AnimalLeader()
        self.crop_leader = CropLeader()
        self.planting_leader = PlantingLeader()
        self.logistics_leader = LogisticsLeader()
        self.workers: List[Worker] = []

    def __call__(self, obs, cfg=None):
        player = obs["player"]
        farm = obs["farms"][player]
        priv = obs.get("private", {})
        tiles = farm["tiles"]
        bs = len(tiles)
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        remaining = TD - day - 1
        hands = farm.get("hands", [])
        num_workers = 1 + len(hands)
        shed = priv.get("shed", {})
        seeds = priv.get("seeds", {})
        inv_list = priv.get("inventories", [{}])
        unlocked_quads = set(farm.get("unlocked_quadrants", ["NW"]))

        # Logging
        if hour == 0:
            na = sum(1 for y in range(bs) for x in range(bs)
                     if isinstance(tiles[y][x], dict) and "animal" in tiles[y][x])
            np = sum(1 for y in range(bs) for x in range(bs)
                     if isinstance(tiles[y][x], dict) and tiles[y][x].get("kind") == "PLANT")
            LOG.new_day(day, farm["money"], na, np, len(hands))

        # Resize worker pool
        while len(self.workers) < num_workers:
            self.workers.append(Worker())
        self.workers = self.workers[:num_workers]

        # === LAYER 1: Master decides market ===
        market_orders = self.master.decide_market(obs)

        # === LAYER 2: Group leaders plan tasks ===
        prices = obs.get("market", {}).get("prices", {})
        na = sum(1 for y in range(bs) for x in range(bs)
                 if isinstance(tiles[y][x], dict) and "animal" in tiles[y][x])
        in_shed = shed.get("COW", 0) + shed.get("SHEEP", 0)
        empty_pastures = [(x,y) for y in range(bs) for x in range(bs)
                          if isinstance(tiles[y][x], dict) and tiles[y][x].get("kind") == "PASTURE"
                          and "animal" not in tiles[y][x]]

        animal_tasks = self.animal_leader.plan(tiles, bs, shed, na, in_shed, empty_pastures)
        crop_tasks = self.crop_leader.plan(tiles, bs)
        planting_tasks = self.planting_leader.plan(tiles, bs, seeds, day, remaining, hour, unlocked_quads, prices)
        logistics_tasks = self.logistics_leader.plan(tiles, bs, inv_list)

        # Merge all tasks, sort by priority
        all_tasks = animal_tasks + crop_tasks + planting_tasks + logistics_tasks
        all_tasks.sort(key=lambda t: t[2], reverse=True)

        # CRITICAL: Ensure planting gets workers!
        # ALWAYS reserve 2 slots for PLANT tasks by capping COLLECT/HARVEST
        if planting_tasks:
            num_workers_total = len(self.workers)
            max_animal_tasks = max(1, num_workers_total - 3)  # leave 2-3 for plant+water
            animal_task_count = 0
            capped_tasks = []
            for task in all_tasks:
                if task[0] in ("COLLECT_RUN", "HARVEST_RUN"):
                    animal_task_count += 1
                    if animal_task_count > max_animal_tasks:
                        continue
                capped_tasks.append(task)
            all_tasks = capped_tasks

        # === LAYER 2→3: Assign tasks to idle workers ===
        # Rule: worker[0] (farmer) gets FIRST FEED_CIRCUIT, hands get remaining tasks
        task_idx = 0
        for i, w in enumerate(self.workers):
            if not w.idle:
                continue
            if task_idx >= len(all_tasks):
                break
            kind, target, prio = all_tasks[task_idx]
            # Farmer (i==0) should always get a FEED_CIRCUIT if available
            if i == 0 and kind != "FEED_CIRCUIT":
                for j in range(task_idx, len(all_tasks)):
                    if all_tasks[j][0] == "FEED_CIRCUIT":
                        all_tasks[task_idx], all_tasks[j] = all_tasks[j], all_tasks[task_idx]
                        kind, target, prio = all_tasks[task_idx]
                        break
            w.assign(kind, target)
            task_idx += 1

        # === LAYER 3: Workers execute ===
        positions = [tuple(farm["farmer"])] + [tuple(h) for h in hands]
        farmer_action = ["PASS"]
        hand_actions = []

        for i, w in enumerate(self.workers):
            pos = positions[i] if i < len(positions) else (4, 4)
            inv = inv_list[i] if i < len(inv_list) else {}
            action = w.step(pos, tiles, inv, shed, seeds, bs)
            if i == 0:
                farmer_action = action
            else:
                hand_actions.append(action)

        return {"farmer": farmer_action, "hands": hand_actions, "market": market_orders}


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

_game_agent = None

def agent(obs, cfg=None):
    global _game_agent
    if _game_agent is None:
        _game_agent = GameAgent()
    return _game_agent(obs, cfg)
