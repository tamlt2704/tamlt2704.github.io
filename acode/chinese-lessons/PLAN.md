# Learn Chinese Conversation — Video Series Plan

## Tech Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Animation | **Manim CE 0.20.1** | Already installed |
| TTS | **edge-tts** (Microsoft Neural Voices) | Free, no API key, natural-sounding Chinese voices, runs locally via async HTTP — no GPU needed |
| Chinese voice | `zh-CN-XiaoxiaoNeural` (female) | Most natural Mandarin voice available |
| English voice | `en-US-JennyNeural` (female) | Clear pronunciation for English translations |
| Video compose | **ffmpeg** | Already installed, merge audio + animation |
| Python | 3.x with CPU-only torch | Quadro P1000 (4GB) too small for Qwen3-TTS models |

### Why NOT Qwen3-TTS?

- Qwen3-TTS requires **GPU with CUDA** — your torch is CPU-only build
- Smallest model (0.6B) still needs ~2GB+ VRAM in bfloat16, plus tokenizer
- Your Quadro P1000 (4GB WDDM) would struggle even if CUDA torch were installed
- **edge-tts** uses Microsoft Azure Neural TTS — same quality as native speakers, zero setup

### Why NOT Coqui TTS?

- Coqui's Chinese models are mediocre compared to edge-tts
- edge-tts Chinese voices (XiaoxiaoNeural) are production-grade, natural prosody

---

## Episode Plan (10 episodes, ~5 min each)

### EP01 — Greetings & Self-Introduction (打招呼和自我介绍)
- 你好 / 你好吗 / 我很好
- 我叫... / 你叫什么名字？
- 认识你很高兴
- Mini dialogue: Two people meeting for the first time

### EP02 — Numbers & Counting (数字)
- Numbers 1-10, then 100, 1000
- 几 / 多少
- Phone number, age (你几岁？/ 你多大？)
- Mini dialogue: Exchanging phone numbers

### EP03 — At the Restaurant (在餐厅)
- 我要... / 我想吃...
- 菜单 / 点菜 / 买单
- 多少钱？/ 太贵了
- Mini dialogue: Ordering food

### EP04 — Directions & Transportation (问路和交通)
- 左 / 右 / 前 / 后 / 直走
- 地铁 / 公交车 / 出租车
- ...在哪里？/ 怎么去...？
- Mini dialogue: Asking for directions

### EP05 — Shopping (购物)
- 这个多少钱？/ 便宜一点
- 大 / 小 / 颜色
- 可以试试吗？/ 我要这个
- Mini dialogue: Buying clothes

### EP06 — Time & Daily Routine (时间和日常)
- 现在几点？/ 今天星期几？
- 早上 / 中午 / 下午 / 晚上
- 起床 / 吃饭 / 上班 / 睡觉
- Mini dialogue: Describing your day

### EP07 — Family & Relationships (家庭)
- 爸爸 / 妈妈 / 哥哥 / 姐姐
- 你家有几口人？
- 他/她是谁？
- Mini dialogue: Introducing your family

### EP08 — Weather & Seasons (天气和季节)
- 今天天气怎么样？
- 热 / 冷 / 下雨 / 晴天
- 春 / 夏 / 秋 / 冬
- Mini dialogue: Talking about weather

### EP09 — Hobbies & Free Time (爱好)
- 你喜欢什么？/ 我喜欢...
- 看电影 / 听音乐 / 运动 / 旅游
- 周末你做什么？
- Mini dialogue: Discussing hobbies

### EP10 — Emergency & Useful Phrases (紧急情况和常用语)
- 帮帮我！/ 我不舒服
- 对不起 / 没关系 / 谢谢
- 我听不懂 / 请再说一次
- Mini dialogue: Getting help in China

---

## Animation Style (per episode)

Each episode follows a consistent visual template:

```
[0:00-0:15]  Title card — episode number + topic (animated text)
[0:15-1:00]  Vocabulary section — Chinese character + pinyin + English
             Each word: write-on animation → TTS speaks Chinese → English translation fades in
[1:00-3:00]  Phrase building — sentences appear with highlight animations
             TTS reads each phrase, synced with text highlight
[3:00-4:30]  Mini dialogue — two "speaker" icons alternate
             Speech bubbles animate in, TTS voices alternate
[4:30-5:00]  Review — quick flash of all vocabulary with audio
```

### Visual Design
- **Background**: Dark gradient (navy → black) — easy on eyes
- **Chinese text**: Large, white, center screen
- **Pinyin**: Smaller, colored (coral/orange) above Chinese
- **English**: Gray, below Chinese
- **Transitions**: Smooth FadeIn/FadeOut, Write animations for characters
- **Speaker indicators**: Colored circles (blue = Speaker A, pink = Speaker B)
- **Progress bar**: Subtle bottom bar showing lesson progress

---

## File Structure

```
chinese-lessons/
├── PLAN.md                  # This file
├── render.py                # Main build script — renders all episodes
├── common/
│   ├── __init__.py
│   ├── styles.py            # Colors, fonts, layout constants
│   ├── tts_engine.py        # edge-tts wrapper (async generate audio)
│   └── scene_base.py        # Base Manim scene class with shared methods
├── episodes/
│   ├── ep01_greetings.py
│   ├── ep02_numbers.py
│   ├── ep03_restaurant.py
│   ├── ep04_directions.py
│   ├── ep05_shopping.py
│   ├── ep06_time.py
│   ├── ep07_family.py
│   ├── ep08_weather.py
│   ├── ep09_hobbies.py
│   └── ep10_emergency.py
├── audio/                   # Generated TTS audio files (per episode)
│   ├── ep01/
│   ├── ep02/
│   └── ...
└── output/                  # Final rendered videos
    ├── ep01_greetings.mp4
    ├── ep02_numbers.mp4
    └── ...
```

---

## Build Pipeline

```
1. Generate TTS audio    →  python render.py --tts ep01
   (edge-tts creates .mp3 files with known durations)

2. Render Manim scene    →  python render.py --render ep01
   (scene uses audio durations for timing/sync)

3. Merge audio + video   →  python render.py --merge ep01
   (ffmpeg combines silent manim video with TTS audio track)

4. Build all             →  python render.py --all
```

Each step is independent so you can re-generate audio without re-rendering, or vice versa.

---

## Voice Sync Strategy

1. **Pre-generate all audio** for an episode using edge-tts
2. **Measure duration** of each audio clip using ffmpeg/mutagen
3. **Pass durations into Manim scene** — each animation segment's `run_time` matches its audio clip
4. **Render silent video** with correct timing
5. **Merge** audio clips into a single track, overlay onto video

This ensures perfect lip-sync without real-time audio playback during rendering.
