"""EP06 — Time & Daily Routine (时间和日常)"""
from common.scene_base import ChineseLessonScene

VOCAB = [
    ("现在", "xiànzài", "now"),
    ("几点", "jǐ diǎn", "what time"),
    ("今天", "jīntiān", "today"),
    ("明天", "míngtiān", "tomorrow"),
    ("昨天", "zuótiān", "yesterday"),
    ("早上", "zǎoshang", "morning"),
    ("中午", "zhōngwǔ", "noon"),
    ("下午", "xiàwǔ", "afternoon"),
    ("晚上", "wǎnshang", "evening"),
    ("星期", "xīngqī", "week / day of the week"),
]

PHRASES = [
    ("现在几点？", "Xiànzài jǐ diǎn?", "What time is it now?"),
    ("现在八点半。", "Xiànzài bā diǎn bàn.", "It's 8:30 now."),
    ("今天星期几？", "Jīntiān xīngqī jǐ?", "What day is it today?"),
    ("我早上七点起床。", "Wǒ zǎoshang qī diǎn qǐchuáng.", "I get up at 7 in the morning."),
    ("你中午吃什么？", "Nǐ zhōngwǔ chī shénme?", "What do you eat at noon?"),
    ("我们明天见！", "Wǒmen míngtiān jiàn!", "See you tomorrow!"),
    ("昨天晚上你做了什么？", "Zuótiān wǎnshang nǐ zuò le shénme?", "What did you do last night?"),
    ("下午三点可以吗？", "Xiàwǔ sān diǎn kěyǐ ma?", "Is 3 PM okay?"),
]

DIALOGUE_1 = [
    {"speaker": "A", "chinese": "今天我们做什么？", "pinyin": "Jīntiān wǒmen zuò shénme?", "english": "What shall we do today?"},
    {"speaker": "B", "chinese": "早上我想去跑步。", "pinyin": "Zǎoshang wǒ xiǎng qù pǎobù.", "english": "I want to go running in the morning."},
    {"speaker": "A", "chinese": "几点去？", "pinyin": "Jǐ diǎn qù?", "english": "What time?"},
    {"speaker": "B", "chinese": "早上七点，好吗？", "pinyin": "Zǎoshang qī diǎn, hǎo ma?", "english": "7 AM, okay?"},
    {"speaker": "A", "chinese": "好的。中午一起吃饭吧。", "pinyin": "Hǎo de. Zhōngwǔ yìqǐ chīfàn ba.", "english": "Okay. Let's eat lunch together."},
    {"speaker": "B", "chinese": "好啊！下午你有时间吗？", "pinyin": "Hǎo a! Xiàwǔ nǐ yǒu shíjiān ma?", "english": "Great! Are you free in the afternoon?"},
    {"speaker": "A", "chinese": "下午我要学中文。", "pinyin": "Xiàwǔ wǒ yào xué Zhōngwén.", "english": "I'm studying Chinese in the afternoon."},
    {"speaker": "B", "chinese": "几点到几点？", "pinyin": "Jǐ diǎn dào jǐ diǎn?", "english": "From what time to what time?"},
    {"speaker": "A", "chinese": "两点到四点。", "pinyin": "Liǎng diǎn dào sì diǎn.", "english": "From 2 to 4."},
    {"speaker": "B", "chinese": "那晚上我们去看电影吧！", "pinyin": "Nà wǎnshang wǒmen qù kàn diànyǐng ba!", "english": "Then let's go see a movie in the evening!"},
]

DIALOGUE_2 = [
    {"speaker": "A", "chinese": "你每个星期都很忙吗？", "pinyin": "Nǐ měi ge xīngqī dōu hěn máng ma?", "english": "Are you busy every week?"},
    {"speaker": "B", "chinese": "是的。星期一到星期五我上班。", "pinyin": "Shì de. Xīngqī yī dào xīngqī wǔ wǒ shàngbān.", "english": "Yes. I work Monday to Friday."},
    {"speaker": "A", "chinese": "你几点上班？", "pinyin": "Nǐ jǐ diǎn shàngbān?", "english": "What time do you start work?"},
    {"speaker": "B", "chinese": "早上九点到下午六点。", "pinyin": "Zǎoshang jiǔ diǎn dào xiàwǔ liù diǎn.", "english": "9 AM to 6 PM."},
    {"speaker": "A", "chinese": "星期六你做什么？", "pinyin": "Xīngqī liù nǐ zuò shénme?", "english": "What do you do on Saturday?"},
    {"speaker": "B", "chinese": "星期六我学中文，下午去运动。", "pinyin": "Xīngqī liù wǒ xué Zhōngwén, xiàwǔ qù yùndòng.", "english": "Saturday I study Chinese, and exercise in the afternoon."},
    {"speaker": "A", "chinese": "星期天呢？", "pinyin": "Xīngqī tiān ne?", "english": "What about Sunday?"},
    {"speaker": "B", "chinese": "星期天我休息，在家看书。", "pinyin": "Xīngqī tiān wǒ xiūxi, zài jiā kànshū.", "english": "Sunday I rest and read at home."},
    {"speaker": "A", "chinese": "昨天晚上你做了什么？", "pinyin": "Zuótiān wǎnshang nǐ zuò le shénme?", "english": "What did you do last night?"},
    {"speaker": "B", "chinese": "我和朋友一起吃了晚饭。", "pinyin": "Wǒ hé péngyou yìqǐ chī le wǎnfàn.", "english": "I had dinner with a friend."},
]


class EP06Time(ChineseLessonScene):
    episode_id = "ep06"
    episode_title = "时间和日常"
    episode_subtitle = "Time & Daily Routine"

    def construct(self):
        self.show_title()
        self.show_section("生词 Vocabulary", "Key words for this lesson")
        for zh, py, en in VOCAB:
            self.show_vocab(zh, py, en)
        self.show_section("句子 Phrases", "Useful sentences")
        for zh, py, en in PHRASES:
            self.show_phrase(zh, py, en)
        self.show_section("对话一 Dialogue 1", "Making plans for the day")
        self.show_dialogue(DIALOGUE_1)
        self.show_section("对话二 Dialogue 2", "Discussing weekly schedule")
        self.show_dialogue(DIALOGUE_2)
        self.show_section("复习 Review")
        self.show_review([{"chinese": zh, "pinyin": py, "english": en} for zh, py, en in VOCAB])
        self.show_end_card()
