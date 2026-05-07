"""EP08 — Weather & Seasons (天气和季节)"""
from common.scene_base import ChineseLessonScene

VOCAB = [
    ("天气", "tiānqì", "weather"),
    ("热", "rè", "hot"),
    ("冷", "lěng", "cold"),
    ("下雨", "xiàyǔ", "to rain"),
    ("晴天", "qíngtiān", "sunny day"),
    ("风", "fēng", "wind"),
    ("雪", "xuě", "snow"),
    ("春天", "chūntiān", "spring"),
    ("夏天", "xiàtiān", "summer"),
    ("秋天", "qiūtiān", "autumn"),
    ("冬天", "dōngtiān", "winter"),
]

PHRASES = [
    ("今天天气怎么样？", "Jīntiān tiānqì zěnmeyàng?", "How's the weather today?"),
    ("今天很热。", "Jīntiān hěn rè.", "It's very hot today."),
    ("外面下雨了。", "Wàimiàn xiàyǔ le.", "It's raining outside."),
    ("明天是晴天。", "Míngtiān shì qíngtiān.", "Tomorrow will be sunny."),
    ("冬天会下雪。", "Dōngtiān huì xiàxuě.", "It snows in winter."),
    ("今天风很大。", "Jīntiān fēng hěn dà.", "It's very windy today."),
    ("春天不冷也不热。", "Chūntiān bù lěng yě bú rè.", "Spring is neither cold nor hot."),
    ("你最喜欢哪个季节？", "Nǐ zuì xǐhuān nǎge jìjié?", "Which season do you like most?"),
]

DIALOGUE_1 = [
    {"speaker": "A", "chinese": "今天天气怎么样？", "pinyin": "Jīntiān tiānqì zěnmeyàng?", "english": "How's the weather today?"},
    {"speaker": "B", "chinese": "我看一下……外面在下雨。", "pinyin": "Wǒ kàn yíxià... wàimiàn zài xiàyǔ.", "english": "Let me check... it's raining outside."},
    {"speaker": "A", "chinese": "真的吗？我想出去买东西。", "pinyin": "Zhēn de ma? Wǒ xiǎng chūqù mǎi dōngxi.", "english": "Really? I want to go out shopping."},
    {"speaker": "B", "chinese": "你带伞了吗？", "pinyin": "Nǐ dài sǎn le ma?", "english": "Did you bring an umbrella?"},
    {"speaker": "A", "chinese": "没有，我没带伞。", "pinyin": "Méiyǒu, wǒ méi dài sǎn.", "english": "No, I didn't bring an umbrella."},
    {"speaker": "B", "chinese": "那你等一下吧，下午可能是晴天。", "pinyin": "Nà nǐ děng yíxià ba, xiàwǔ kěnéng shì qíngtiān.", "english": "Then wait a bit, it might be sunny this afternoon."},
    {"speaker": "A", "chinese": "好吧。今天冷不冷？", "pinyin": "Hǎo ba. Jīntiān lěng bù lěng?", "english": "Okay. Is it cold today?"},
    {"speaker": "B", "chinese": "不太冷，但是风很大。", "pinyin": "Bú tài lěng, dànshì fēng hěn dà.", "english": "Not too cold, but it's very windy."},
    {"speaker": "A", "chinese": "那我多穿一件衣服。", "pinyin": "Nà wǒ duō chuān yí jiàn yīfu.", "english": "Then I'll put on an extra layer."},
    {"speaker": "B", "chinese": "好主意！", "pinyin": "Hǎo zhǔyi!", "english": "Good idea!"},
]

DIALOGUE_2 = [
    {"speaker": "A", "chinese": "你最喜欢哪个季节？", "pinyin": "Nǐ zuì xǐhuān nǎge jìjié?", "english": "Which season do you like most?"},
    {"speaker": "B", "chinese": "我最喜欢秋天，不冷也不热。你呢？", "pinyin": "Wǒ zuì xǐhuān qiūtiān, bù lěng yě bú rè. Nǐ ne?", "english": "I like autumn most, neither cold nor hot. How about you?"},
    {"speaker": "A", "chinese": "我喜欢春天，花很漂亮。", "pinyin": "Wǒ xǐhuān chūntiān, huā hěn piàoliang.", "english": "I like spring, the flowers are beautiful."},
    {"speaker": "B", "chinese": "春天也不错。你喜欢夏天吗？", "pinyin": "Chūntiān yě búcuò. Nǐ xǐhuān xiàtiān ma?", "english": "Spring is also nice. Do you like summer?"},
    {"speaker": "A", "chinese": "不太喜欢，夏天太热了。", "pinyin": "Bú tài xǐhuān, xiàtiān tài rè le.", "english": "Not really, summer is too hot."},
    {"speaker": "B", "chinese": "对，而且经常下雨。", "pinyin": "Duì, érqiě jīngcháng xiàyǔ.", "english": "Right, and it rains often."},
    {"speaker": "A", "chinese": "冬天呢？你觉得冬天怎么样？", "pinyin": "Dōngtiān ne? Nǐ juéde dōngtiān zěnmeyàng?", "english": "What about winter? What do you think of winter?"},
    {"speaker": "B", "chinese": "冬天太冷了，但是下雪很好看。", "pinyin": "Dōngtiān tài lěng le, dànshì xiàxuě hěn hǎokàn.", "english": "Winter is too cold, but snow is beautiful."},
    {"speaker": "A", "chinese": "是啊，我也觉得雪很漂亮。", "pinyin": "Shì a, wǒ yě juéde xuě hěn piàoliang.", "english": "Yeah, I also think snow is beautiful."},
]


class EP08Weather(ChineseLessonScene):
    episode_id = "ep08"
    episode_title = "天气和季节"
    episode_subtitle = "Weather & Seasons"

    def construct(self):
        self.show_title()
        self.show_section("生词 Vocabulary", "Key words for this lesson")
        for zh, py, en in VOCAB:
            self.show_vocab(zh, py, en)
        self.show_section("句子 Phrases", "Useful sentences")
        for zh, py, en in PHRASES:
            self.show_phrase(zh, py, en)
        self.show_section("对话一 Dialogue 1", "Checking weather before going out")
        self.show_dialogue(DIALOGUE_1)
        self.show_section("对话二 Dialogue 2", "Discussing favorite seasons")
        self.show_dialogue(DIALOGUE_2)
        self.show_section("复习 Review")
        self.show_review([{"chinese": zh, "pinyin": py, "english": en} for zh, py, en in VOCAB])
        self.show_end_card()
