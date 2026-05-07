"""EP02 — Numbers & Counting (数字)"""
from common.scene_base import ChineseLessonScene

VOCAB = [
    ("一", "yī", "one"),
    ("二", "èr", "two"),
    ("三", "sān", "three"),
    ("四", "sì", "four"),
    ("五", "wǔ", "five"),
    ("六", "liù", "six"),
    ("七", "qī", "seven"),
    ("八", "bā", "eight"),
    ("九", "jiǔ", "nine"),
    ("十", "shí", "ten"),
    ("百", "bǎi", "hundred"),
    ("千", "qiān", "thousand"),
    ("多少", "duō shǎo", "how many / how much"),
    ("几", "jǐ", "how many (small number)"),
]

PHRASES = [
    ("你多大了？", "nǐ duō dà le?", "How old are you?"),
    ("我二十五岁。", "wǒ èr shí wǔ suì.", "I am 25 years old."),
    ("你的电话号码是多少？", "nǐ de diàn huà hào mǎ shì duō shǎo?", "What is your phone number?"),
    ("一共多少钱？", "yī gòng duō shǎo qián?", "How much is it in total?"),
    ("三百二十块。", "sān bǎi èr shí kuài.", "320 yuan."),
    ("你要几个？", "nǐ yào jǐ gè?", "How many do you want?"),
    ("我要两个。", "wǒ yào liǎng gè.", "I want two."),
    ("太贵了！", "tài guì le!", "Too expensive!"),
]

DIALOGUE_1 = [
    {"speaker": "A", "chinese": "你好！我们交换一下电话号码吧。", "pinyin": "nǐ hǎo! wǒ men jiāo huàn yī xià diàn huà hào mǎ ba.", "english": "Hi! Let's exchange phone numbers."},
    {"speaker": "B", "chinese": "好啊！你的号码是多少？", "pinyin": "hǎo a! nǐ de hào mǎ shì duō shǎo?", "english": "Sure! What's your number?"},
    {"speaker": "A", "chinese": "我的号码是一三八六五五二九七零三。", "pinyin": "wǒ de hào mǎ shì yāo sān bā liù wǔ wǔ èr jiǔ qī líng sān.", "english": "My number is 13865529703."},
    {"speaker": "B", "chinese": "等一下，一三八……后面是什么？", "pinyin": "děng yī xià, yāo sān bā... hòu miàn shì shén me?", "english": "Wait, 138... what comes after?"},
    {"speaker": "A", "chinese": "六五五二九七零三。", "pinyin": "liù wǔ wǔ èr jiǔ qī líng sān.", "english": "65529703."},
    {"speaker": "B", "chinese": "好，记下来了。我的是一五零九八八三六一四二。", "pinyin": "hǎo, jì xià lái le. wǒ de shì yāo wǔ líng jiǔ bā bā sān liù yāo sì èr.", "english": "OK, got it. Mine is 15098836142."},
    {"speaker": "A", "chinese": "一五零九八八三六一四二，对吗？", "pinyin": "yāo wǔ líng jiǔ bā bā sān liù yāo sì èr, duì ma?", "english": "15098836142, right?"},
    {"speaker": "B", "chinese": "对的！我加你微信吧。", "pinyin": "duì de! wǒ jiā nǐ wēi xìn ba.", "english": "That's right! I'll add you on WeChat."},
    {"speaker": "A", "chinese": "好的，回头聊！", "pinyin": "hǎo de, huí tóu liáo!", "english": "OK, talk later!"},
]

DIALOGUE_2 = [
    {"speaker": "A", "chinese": "你好，这个多少钱？", "pinyin": "nǐ hǎo, zhè ge duō shǎo qián?", "english": "Hi, how much is this?"},
    {"speaker": "B", "chinese": "这个四十五块。", "pinyin": "zhè ge sì shí wǔ kuài.", "english": "This one is 45 yuan."},
    {"speaker": "A", "chinese": "那个呢？", "pinyin": "nà ge ne?", "english": "What about that one?"},
    {"speaker": "B", "chinese": "那个八十块。", "pinyin": "nà ge bā shí kuài.", "english": "That one is 80 yuan."},
    {"speaker": "A", "chinese": "我要两个这个，一个那个。", "pinyin": "wǒ yào liǎng gè zhè ge, yī gè nà ge.", "english": "I want two of these and one of those."},
    {"speaker": "B", "chinese": "好的。两个四十五加一个八十，一共一百七十块。", "pinyin": "hǎo de. liǎng gè sì shí wǔ jiā yī gè bā shí, yī gòng yī bǎi qī shí kuài.", "english": "OK. Two at 45 plus one at 80, that's 170 yuan total."},
    {"speaker": "A", "chinese": "能便宜一点吗？一百五十块行不行？", "pinyin": "néng pián yi yī diǎn ma? yī bǎi wǔ shí kuài xíng bù xíng?", "english": "Can you make it cheaper? How about 150 yuan?"},
    {"speaker": "B", "chinese": "一百六十块吧，不能再少了。", "pinyin": "yī bǎi liù shí kuài ba, bù néng zài shǎo le.", "english": "160 yuan, I can't go lower."},
    {"speaker": "A", "chinese": "好吧，一百六十。给你钱。", "pinyin": "hǎo ba, yī bǎi liù shí. gěi nǐ qián.", "english": "OK, 160. Here's the money."},
    {"speaker": "B", "chinese": "谢谢！欢迎下次再来！", "pinyin": "xiè xie! huān yíng xià cì zài lái!", "english": "Thanks! Welcome back next time!"},
]


class EP02Numbers(ChineseLessonScene):
    episode_id = "ep02"
    episode_title = "数字"
    episode_subtitle = "Numbers & Counting"

    def construct(self):
        self.show_title()
        self.show_section("生词 Vocabulary", "Key words for this lesson")
        for zh, py, en in VOCAB:
            self.show_vocab(zh, py, en)
        self.show_section("句子 Phrases", "Useful sentences")
        for zh, py, en in PHRASES:
            self.show_phrase(zh, py, en)
        self.show_section("对话一 Dialogue 1", "Exchanging phone numbers")
        self.show_dialogue(DIALOGUE_1)
        self.show_section("对话二 Dialogue 2", "Shopping and asking prices")
        self.show_dialogue(DIALOGUE_2)
        self.show_section("复习 Review")
        self.show_review([{"chinese": zh, "pinyin": py, "english": en} for zh, py, en in VOCAB])
        self.show_end_card()
