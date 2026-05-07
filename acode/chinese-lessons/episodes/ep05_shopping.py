"""EP05 — Shopping (购物)"""
from common.scene_base import ChineseLessonScene

VOCAB = [
    ("多少钱", "duōshao qián", "how much money"),
    ("便宜", "piányi", "cheap"),
    ("贵", "guì", "expensive"),
    ("大", "dà", "big"),
    ("小", "xiǎo", "small"),
    ("颜色", "yánsè", "color"),
    ("红色", "hóngsè", "red"),
    ("蓝色", "lánsè", "blue"),
    ("试试", "shìshi", "to try"),
    ("买", "mǎi", "to buy"),
]

PHRASES = [
    ("这个多少钱？", "Zhège duōshao qián?", "How much is this?"),
    ("太贵了！", "Tài guì le!", "Too expensive!"),
    ("能便宜一点吗？", "Néng piányi yìdiǎn ma?", "Can it be a bit cheaper?"),
    ("有没有大一点的？", "Yǒu méiyǒu dà yìdiǎn de?", "Do you have a bigger one?"),
    ("我想试试这件。", "Wǒ xiǎng shìshi zhè jiàn.", "I'd like to try this one on."),
    ("有什么颜色？", "Yǒu shénme yánsè?", "What colors do you have?"),
    ("我要买这个。", "Wǒ yào mǎi zhège.", "I want to buy this one."),
    ("可以刷卡吗？", "Kěyǐ shuākǎ ma?", "Can I pay by card?"),
]

DIALOGUE_1 = [
    {"speaker": "A", "chinese": "你好，我想买一件衣服。", "pinyin": "Nǐ hǎo, wǒ xiǎng mǎi yí jiàn yīfu.", "english": "Hello, I'd like to buy some clothes."},
    {"speaker": "B", "chinese": "好的，你喜欢什么颜色？", "pinyin": "Hǎo de, nǐ xǐhuan shénme yánsè?", "english": "Sure, what color do you like?"},
    {"speaker": "A", "chinese": "有红色的吗？", "pinyin": "Yǒu hóngsè de ma?", "english": "Do you have red?"},
    {"speaker": "B", "chinese": "有，你试试这件。", "pinyin": "Yǒu, nǐ shìshi zhè jiàn.", "english": "Yes, try this one."},
    {"speaker": "A", "chinese": "这件太小了，有大一点的吗？", "pinyin": "Zhè jiàn tài xiǎo le, yǒu dà yìdiǎn de ma?", "english": "This one is too small, do you have a bigger one?"},
    {"speaker": "B", "chinese": "有，你看这件。", "pinyin": "Yǒu, nǐ kàn zhè jiàn.", "english": "Yes, look at this one."},
    {"speaker": "A", "chinese": "很好！多少钱？", "pinyin": "Hěn hǎo! Duōshao qián?", "english": "Great! How much is it?"},
    {"speaker": "B", "chinese": "两百块。", "pinyin": "Liǎng bǎi kuài.", "english": "Two hundred yuan."},
    {"speaker": "A", "chinese": "太贵了！能便宜一点吗？", "pinyin": "Tài guì le! Néng piányi yìdiǎn ma?", "english": "Too expensive! Can it be cheaper?"},
    {"speaker": "B", "chinese": "好吧，一百五。", "pinyin": "Hǎo ba, yì bǎi wǔ.", "english": "Okay, one hundred fifty."},
]

DIALOGUE_2 = [
    {"speaker": "A", "chinese": "你好，我想看看手机。", "pinyin": "Nǐ hǎo, wǒ xiǎng kànkan shǒujī.", "english": "Hello, I'd like to look at phones."},
    {"speaker": "B", "chinese": "好的，你想要什么颜色的？", "pinyin": "Hǎo de, nǐ xiǎng yào shénme yánsè de?", "english": "Sure, what color would you like?"},
    {"speaker": "A", "chinese": "蓝色的。这个多少钱？", "pinyin": "Lánsè de. Zhège duōshao qián?", "english": "Blue. How much is this one?"},
    {"speaker": "B", "chinese": "三千块。", "pinyin": "Sān qiān kuài.", "english": "Three thousand yuan."},
    {"speaker": "A", "chinese": "有没有便宜一点的？", "pinyin": "Yǒu méiyǒu piányi yìdiǎn de?", "english": "Do you have a cheaper one?"},
    {"speaker": "B", "chinese": "这个两千块，也很好。", "pinyin": "Zhège liǎng qiān kuài, yě hěn hǎo.", "english": "This one is two thousand, also very good."},
    {"speaker": "A", "chinese": "我可以试试吗？", "pinyin": "Wǒ kěyǐ shìshi ma?", "english": "Can I try it?"},
    {"speaker": "B", "chinese": "当然可以。", "pinyin": "Dāngrán kěyǐ.", "english": "Of course."},
    {"speaker": "A", "chinese": "好，我要买这个。可以刷卡吗？", "pinyin": "Hǎo, wǒ yào mǎi zhège. Kěyǐ shuākǎ ma?", "english": "Good, I'll buy this one. Can I pay by card?"},
    {"speaker": "B", "chinese": "可以，没问题。", "pinyin": "Kěyǐ, méi wèntí.", "english": "Yes, no problem."},
]


class EP05Shopping(ChineseLessonScene):
    episode_id = "ep05"
    episode_title = "购物"
    episode_subtitle = "Shopping"

    def construct(self):
        self.show_title()
        self.show_section("生词 Vocabulary", "Key words for this lesson")
        for zh, py, en in VOCAB:
            self.show_vocab(zh, py, en)
        self.show_section("句子 Phrases", "Useful sentences")
        for zh, py, en in PHRASES:
            self.show_phrase(zh, py, en)
        self.show_section("对话一 Dialogue 1", "Buying clothes at a market")
        self.show_dialogue(DIALOGUE_1)
        self.show_section("对话二 Dialogue 2", "At an electronics store")
        self.show_dialogue(DIALOGUE_2)
        self.show_section("复习 Review")
        self.show_review([{"chinese": zh, "pinyin": py, "english": en} for zh, py, en in VOCAB])
        self.show_end_card()
