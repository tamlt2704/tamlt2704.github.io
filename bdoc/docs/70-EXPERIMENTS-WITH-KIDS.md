# Chapter 70: Cool Experiments to Build with Kids — Science, Code, and Craft

## What you'll learn

- 30 experiments across science, coding, electronics, and craft
- Each takes 10-60 minutes with household/cheap materials
- Age-appropriate: marked for 4+, 6+, 8+, 10+
- The "wow factor" — impressive results from simple setups
- Learning sneaked in: physics, chemistry, biology, programming, engineering

---

## 🔬 SCIENCE EXPERIMENTS

### 1. Volcano Eruption (Ages 4+, 5 min)
```
MATERIALS: Baking soda, vinegar, dish soap, food colouring, container

BUILD:
  1. Put 2 tablespoons baking soda in a container (or shape clay around it)
  2. Add a squirt of dish soap + food colouring
  3. Pour vinegar in

RESULT: Foaming eruption! 🌋

SCIENCE: Acid (vinegar) + base (baking soda) → CO₂ gas
         Soap traps the gas → foam bubbles overflow

EXTEND: Try different amounts. What makes the BIGGEST eruption?
```

### 2. Walking Water Rainbow (Ages 4+, 30 min setup + 2 hours waiting)
```
MATERIALS: 7 glasses, water, food colouring (red, yellow, blue), paper towels

BUILD:
  1. Fill glasses 1, 3, 5, 7 with water
  2. Add colours: glass 1=red, 3=yellow, 5=blue, 7=red
  3. Leave glasses 2, 4, 6 EMPTY
  4. Fold paper towels into strips, bridge between each glass
  5. Wait 2 hours...

RESULT: Water "walks" up the paper towels! Empty glasses fill with
        mixed colours (orange, green, purple). A rainbow of glasses! 🌈

SCIENCE: Capillary action — water molecules climb through tiny paper fibres
         (same way trees move water from roots to leaves)
```

### 3. Density Tower (Ages 5+, 10 min)
```
MATERIALS: Tall glass, honey, corn syrup, dish soap, water, vegetable oil, rubbing alcohol

BUILD:
  1. Pour in this order (SLOWLY down the side):
     - Honey (bottom)
     - Corn syrup
     - Dish soap
     - Water (add food colouring)
     - Vegetable oil
     - Rubbing alcohol (add different food colouring)

RESULT: 6 distinct layers! They don't mix! 🏗️

SCIENCE: Each liquid has different density (mass per volume).
         Heavier liquids sink, lighter ones float.

EXTEND: Drop small objects in. Which layer do they stop at?
        (grape, cherry tomato, plastic LEGO, cork)
```

### 4. Invisible Ink (Ages 5+, 10 min)
```
MATERIALS: Lemon juice, cotton bud/paintbrush, white paper, lamp/iron

BUILD:
  1. Dip cotton bud in lemon juice
  2. Write a secret message on white paper
  3. Let it dry (message disappears!)
  4. Hold paper near a warm lamp or iron it gently

RESULT: Message appears in brown! 🕵️

SCIENCE: Lemon juice is organic. Heat causes oxidation (same reaction
         that turns apples brown), making it visible.

EXTEND: Try other "inks": milk, vinegar, onion juice. Which works best?
```

### 5. Egg in a Bottle (Ages 6+, 5 min)
```
MATERIALS: Hard-boiled egg (peeled), glass bottle (opening slightly smaller than egg), matches/paper

BUILD:
  1. Boil and peel an egg
  2. Light a small piece of paper, drop it INTO the bottle
  3. Quickly place the egg on top of the bottle opening
  4. Watch...

RESULT: The egg gets SUCKED into the bottle! 🥚

SCIENCE: Fire uses oxygen → air pressure drops inside bottle →
         higher pressure OUTSIDE pushes the egg in.
         (It's not suction — it's the atmosphere pushing!)

⚠️ Adult supervision for fire.
```

### 6. Non-Newtonian Fluid / Oobleck (Ages 4+, 10 min)
```
MATERIALS: Cornstarch (cornflour), water, bowl

BUILD:
  1. Mix 2 cups cornstarch + 1 cup water
  2. Stir slowly (it flows like liquid)
  3. Punch it (it's SOLID!)
  4. Roll into ball (solid) → stop squeezing (melts back to liquid)

RESULT: A substance that's BOTH solid and liquid! 🤯

SCIENCE: Non-Newtonian fluid — viscosity changes with force.
         Fast force = particles lock together (solid).
         Slow force = particles slide past each other (liquid).

EXTEND: Can you run across a tub of it? (Yes! YouTube it.)
```

### 7. Homemade Lava Lamp (Ages 5+, 10 min)
```
MATERIALS: Clear bottle, water, vegetable oil, food colouring, Alka-Seltzer (or baking soda + vinegar)

BUILD:
  1. Fill bottle 1/4 with water + food colouring
  2. Fill rest with vegetable oil (oil floats on top)
  3. Drop in a piece of Alka-Seltzer tablet
  4. Watch the bubbles!

RESULT: Coloured blobs rise and fall like a lava lamp! 💡

SCIENCE: Alka-Seltzer creates CO₂ bubbles that carry coloured water up.
         At the top, gas escapes, water sinks back down. Repeats!
```

### 8. Crystal Growing (Ages 6+, 15 min + 3-7 days waiting)
```
MATERIALS: Sugar OR borax OR salt, hot water, jar, string, pencil

BUILD (sugar crystals):
  1. Boil 1 cup water, dissolve 3 cups sugar (supersaturated solution)
  2. Tie string to pencil, lay pencil across jar opening
  3. Pour sugar solution into jar (string hangs in liquid)
  4. Wait 3-7 days...

RESULT: Beautiful crystals grow on the string! 💎

SCIENCE: As water evaporates, dissolved sugar has nowhere to go →
         deposits as crystals. String provides a "seed" surface.

EXTEND: Add food colouring for coloured crystals.
        Try different substances: salt (cubes), borax (larger crystals).
```

---

## 💻 CODING EXPERIMENTS

### 9. Scratch Animation (Ages 6+, 30 min)
```
TOOL: scratch.mit.edu (free, browser-based, no install)

BUILD:
  1. Go to scratch.mit.edu → Create
  2. Choose a character (sprite)
  3. Drag blocks:
     "When green flag clicked"
     "forever"
       "move 10 steps"
       "if on edge, bounce"
  4. Click green flag → character bounces around!

EXTEND:
  • Add sound on bounce
  • Make two sprites chase each other
  • Build a simple game (catch falling apples)
  • Tell a story with scene changes

LEARNING: Loops, conditions, events, coordinates (sneaky algebra!)
```

### 10. Python Turtle Art (Ages 8+, 20 min)
```python
# Open Python (IDLE or Thonny — great for kids)
import turtle

t = turtle.Turtle()
t.speed(0)  # fastest

# Draw a colorful spiral
colours = ["red", "orange", "yellow", "green", "blue", "purple"]
for i in range(360):
    t.color(colours[i % 6])
    t.forward(i * 0.5)
    t.left(59)  # not exactly 60 — creates a spiral!

turtle.done()
```
```
RESULT: Beautiful geometric spiral art! 🌀

EXTEND:
  • Change the angle (59 → 61 → 91 → 121) — completely different patterns!
  • Make a flower: repeat a circle pattern rotated each time
  • Challenge: draw their name using turtle commands
  • Challenge: draw a house, then a street of houses (functions!)
```

### 11. Build a Website About Their Pet (Ages 8+, 30 min)
```html
<!-- Save as mypet.html, open in browser -->
<!DOCTYPE html>
<html>
<head>
  <title>My Pet</title>
  <style>
    body { font-family: Arial; background: #fffde7; text-align: center; }
    h1 { color: #f57c00; }
    img { width: 300px; border-radius: 20px; }
    .fact { background: #fff3e0; padding: 10px; margin: 10px; border-radius: 10px; }
  </style>
</head>
<body>
  <h1>🐕 Meet Buddy!</h1>
  <img src="buddy.jpg" alt="My dog Buddy">
  
  <div class="fact">🎂 Age: 3 years old</div>
  <div class="fact">🍖 Favourite food: Chicken</div>
  <div class="fact">🎾 Favourite toy: Tennis ball</div>
  <div class="fact">😴 Favourite spot: The sofa</div>
  
  <button onclick="alert('Woof woof!')">Click for Buddy to bark!</button>
</body>
</html>
```
```
RESULT: A real website! They can show friends, put their photo.

LEARNING: HTML structure, CSS styling, basic JavaScript (events).
EXTEND: Add more pages (link them), add a photo gallery, add a quiz.
```

### 12. Minecraft Mods with JavaScript (Ages 10+, 30 min)
```
TOOL: ScriptCraft (minecraft mod) or MakeCode for Minecraft Education

EXAMPLE (ScriptCraft — builds structures with code):
  /js box(blocks.gold, 10, 5, 10)   // build a gold box!
  /js cylinder(blocks.glass, 8, 20) // glass tower!
  
  // Build a pyramid:
  for (let i = 10; i > 0; i--) {
    box(blocks.sandstone, i*2, 1, i*2)
    up(1)  // move up one block
  }

RESULT: Build HUGE structures instantly with code! 🏰

LEARNING: Loops, variables, coordinates, 3D thinking
```

### 13. Chatbot (Ages 10+, 20 min)
```python
# Simple rule-based chatbot
import random

responses = {
    "hi": ["Hello!", "Hey there!", "Hi! How are you?"],
    "how are you": ["I'm great! I'm a robot!", "Beep boop! I'm fine!"],
    "what's your name": ["I'm ChatBot 3000!", "Call me Sparky!"],
    "joke": [
        "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
        "What's a computer's favourite snack? Microchips! 🍟",
    ],
    "bye": ["Goodbye! 👋", "See you later, alligator!"],
}

print("🤖 ChatBot 3000 is online! (type 'bye' to exit)")
while True:
    user = input("You: ").lower()
    if user == "bye":
        print("Bot: Goodbye! 👋")
        break
    
    reply = None
    for key in responses:
        if key in user:
            reply = random.choice(responses[key])
            break
    
    if reply:
        print(f"Bot: {reply}")
    else:
        print(f"Bot: Hmm, I don't understand '{user}'. Try: hi, joke, bye")
```

---

## ⚡ ELECTRONICS / ENGINEERING

### 14. Cardboard Marble Run (Ages 4+, 30-60 min)
```
MATERIALS: Cardboard tubes (toilet rolls), tape, cardboard boxes, marble

BUILD:
  1. Cut toilet rolls in half lengthwise (makes channels)
  2. Tape them at angles on a large cardboard backdrop
  3. Create curves, drops, funnels, jumps
  4. Test with marble — adjust angles until it flows!

RESULT: Custom marble rollercoaster! 🎢

ENGINEERING: Trial and error, gravity, angles, problem-solving.
EXTEND: Add a bell at the end. Time different routes. Build the LONGEST run.
```

### 15. LED Throwies (Ages 6+, 5 min)
```
MATERIALS: LED (any colour), coin battery (CR2032), tape, small magnet

BUILD:
  1. Put LED legs on BOTH sides of battery (long leg = +, short = -)
  2. It lights up!
  3. Tape it together with a magnet
  4. Throw onto any metal surface → glowing light!

RESULT: Instant light-up art pieces! ✨ Stick them on the fridge, mailbox, bike.

SCIENCE: Circuit! Battery provides voltage, LED converts to light.
COST: ~$0.30 each. Make 20 and decorate the house!
⚠️ Don't eat batteries (obvious but: small children supervision).
```

### 16. Simple Motor (Ages 8+, 15 min)
```
MATERIALS: AA battery, magnet, copper wire, tape

BUILD:
  1. Tape a small strong magnet to the flat (-) end of AA battery
  2. Shape copper wire into a heart/spiral that balances on the (+) top
  3. Wire's bottom tip lightly touches the magnet
  4. Watch it SPIN!

RESULT: A working electric motor from 3 parts! ⚡

SCIENCE: Current flows through wire → creates magnetic field →
         interacts with permanent magnet → ROTATION (Lorentz force).
         Same principle as every motor in the world.
```

### 17. Paper Airplane Launcher (Ages 6+, 20 min)
```
MATERIALS: Rubber bands, cardboard, paper, tape, popsicle sticks

BUILD:
  1. Make a V-shape channel from cardboard (runway)
  2. Stretch rubber band across the back (catapult)
  3. Fold paper airplane
  4. Load airplane in channel, pull back rubber band, release!

RESULT: Airplanes launch across the room! ✈️

ENGINEERING: Energy storage (elastic potential → kinetic), aerodynamics.
EXTEND: Competition! Who can fly furthest? Modify airplane design.
        Measure distance. Record in a "science journal."
```

### 18. Raspberry Pi Weather Station (Ages 10+, 1-2 hours)
```
MATERIALS: Raspberry Pi (any), DHT11 sensor ($2), jumper wires, breadboard

BUILD:
  1. Connect DHT11 to Pi (3 wires: power, ground, data)
  2. Write Python script to read temperature + humidity
  3. Display on screen or send to a web page

PYTHON:
  import Adafruit_DHT
  sensor = Adafruit_DHT.DHT11
  humidity, temperature = Adafruit_DHT.read_retry(sensor, 4)
  print(f"Temp: {temperature}°C, Humidity: {humidity}%")

RESULT: Real weather data from their own sensor! 🌡️

EXTEND: Log data to file, plot graphs, compare with weather forecast.
        Add more sensors: light, air pressure, soil moisture (garden monitor!).
```

---

## 🎨 ART + SCIENCE

### 19. Milk Fireworks (Ages 3+, 5 min)
```
MATERIALS: Plate, whole milk, food colouring (3-4 colours), dish soap, cotton bud

BUILD:
  1. Pour milk into plate (thin layer)
  2. Drop 3-4 colours in the milk (don't stir!)
  3. Dip cotton bud in dish soap
  4. Touch the soapy cotton bud to the milk surface

RESULT: Colours EXPLODE outward in swirling patterns! 🎆

SCIENCE: Soap breaks surface tension → fat molecules in milk rush away
         from soap → carry colour with them. Looks like fireworks!
```

### 20. Balloon Rocket (Ages 4+, 5 min)
```
MATERIALS: Balloon, string (3+ metres), straw, tape

BUILD:
  1. Thread string through straw
  2. Tie string across the room (taut between two chairs)
  3. Blow up balloon (DON'T tie it — hold the end)
  4. Tape balloon to the straw (opening facing backward)
  5. Let go!

RESULT: Balloon rockets across the room on the string! 🚀

SCIENCE: Newton's 3rd Law — air shoots backward (action) →
         balloon moves forward (reaction). Same as real rockets.

EXTEND: Race! Two strings, two balloons. Whose reaches the end first?
        Try different balloon shapes. Does bigger = faster?
```

### 21. Sun Prints (Ages 4+, 5 min prep + 2-4 hours sun)
```
MATERIALS: Sun-sensitive paper (or construction paper), objects with interesting shapes, sunlight

BUILD:
  1. Place objects on sun-sensitive paper (leaves, keys, toys, lace)
  2. Leave in direct sunlight for 2-4 hours
  3. Remove objects

RESULT: Silhouette art! Paper bleaches around objects, leaving shapes. 🌞

SCIENCE: UV radiation from sunlight fades the paper colour.
         Objects block UV → paper underneath stays original colour.

EXTEND: Use their handprints, flowers, ferns. Frame as wall art!
```

---

## 🧪 QUICK HITS (5 minutes each)

| # | Experiment | Ages | Wow factor |
|---|-----------|------|-----------|
| 22 | **Pepper & soap** — pepper floats on water, touch with soap → pepper runs away | 3+ | Surface tension demo |
| 23 | **Bag of water + pencils** — fill bag with water, stab pencils through → no leak! | 4+ | Polymer chains seal around |
| 24 | **Dancing raisins** — raisins in carbonated water bounce up and down | 4+ | CO₂ bubbles = buoyancy |
| 25 | **Static electricity butterfly** — rub balloon, tissue paper wings "fly" toward it | 4+ | Electric charge attraction |
| 26 | **Vinegar + steel wool** — put in jar, watch thermometer rise (exothermic reaction) | 6+ | Chemical heat |
| 27 | **Straw bridge** — how many books can a bridge of paper straws hold? | 6+ | Structural engineering |
| 28 | **Balloon hovercraft** — CD + balloon + bottle cap = glides on air | 6+ | Friction reduction |
| 29 | **Magnetic slime** — slime + iron filings → moves toward magnets | 8+ | Ferromagnetism |
| 30 | **Lemon battery** — lemon + copper penny + zinc nail → powers an LED | 8+ | Electrochemistry |

---

## How to Make It Educational (Without Killing the Fun)

```
THE RULE: Fun FIRST. Learning is the secret bonus.

1. LET THEM PREDICT:
   "What do you think will happen when I pour vinegar in?"
   → Their prediction engages their brain (right or wrong — both are good)

2. ASK "WHY?" AFTER (not before):
   Don't explain the science first. Let them experience wonder first.
   Then: "Why do you think that happened?"
   Let them guess. Guide, don't lecture.

3. LET THEM FAIL:
   Marble run doesn't work? GOOD. "What could we change?"
   Failure → iteration → solution = the engineering mindset.

4. DOCUMENT IT:
   Take photos/videos. "Let's make a science journal!"
   Draw what happened. Write one sentence about why.
   → Writing about science IS science (observation + explanation).

5. EXTEND WITH QUESTIONS:
   "What if we used MORE vinegar?"
   "What if we tried a BIGGER balloon?"
   "What if we did it in the DARK?"
   → These questions ARE the scientific method. They just don't know it yet.
```

---

## Summary

✅ 30 experiments: science (10), coding (5), electronics (5), art+science (3), quick hits (9)
✅ Ages 3-10+: something for every age group
✅ Household materials: most need things you already have
✅ Impressive results: volcanoes, rainbows, robots, rockets, crystals, art
✅ Real learning: physics, chemistry, biology, programming, engineering — all disguised as play

## Key takeaway

**Kids don't need expensive kits or fancy equipment.** A balloon, some vinegar, and a bit of curiosity = genuine science. The goal isn't to teach them "science" — it's to teach them that THE WORLD IS INTERESTING and they can figure out HOW THINGS WORK by trying stuff. That mindset — curiosity + experimentation + iteration — is the foundation of everything: science, engineering, programming, and life.

---

→ [Back to Chapter 69: Engineering Manager](./69-ENGINEERING-MANAGER.md)
