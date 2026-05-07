"""EP04 — Directions & Transportation (问路和交通)"""
from common.scene_base import ChineseLessonScene

VOCAB = [
    ("左", "zuǒ", "left"),
    ("右", "yòu", "right"),
    ("前", "qián", "front / forward"),
    ("后", "hòu", "back / behind"),
    ("直走", "zhí zǒu", "go straight"),
    ("地铁", "dì tiě", "subway"),
    ("公交车", "gōng jiāo chē", "bus"),
    ("出租车", "chū zū chē", "taxi"),
    ("在哪里", "zài nǎ lǐ", "where is"),
    ("远", "yuǎn", "far"),
    ("近", "jìn", "near"),
    ("路口", "lù kǒu", "intersection"),
]

PHRASES = [
    ("请问，地铁站在哪里？", "qǐng wèn, dì tiě zhàn zài nǎ lǐ?", "Excuse me, where is the subway station?"),
    ("往前直走。", "wǎng qián zhí zǒu.", "Go straight ahead."),
    ("在第一个路口左转。", "zài dì yī gè lù kǒu zuǒ zhuǎn.", "Turn left at the first intersection."),
    ("离这里远吗？", "lí zhè lǐ yuǎn ma?", "Is it far from here?"),
    ("走路大概十分钟。", "zǒu lù dà gài shí fēn zhōng.", "About 10 minutes on foot."),
    ("我想坐出租车。", "wǒ xiǎng zuò chū zū chē.", "I'd like to take a taxi."),
    ("请到这个地址。", "qǐng dào zhè ge dì zhǐ.", "Please go to this address."),
    ("到了，请停车。", "dào le, qǐng tíng chē.", "We're here, please stop."),
]

DIALOGUE_1 = [
    {"speaker": "A", "chinese": "你好，请问银行在哪里？", "pinyin": "nǐ hǎo, qǐng wèn yín háng zài nǎ lǐ?", "english": "Hello, excuse me, where is the bank?"},
    {"speaker": "B", "chinese": "银行啊，从这里往前直走。", "pinyin": "yín háng a, cóng zhè lǐ wǎng qián zhí zǒu.", "english": "The bank? Go straight ahead from here."},
    {"speaker": "A", "chinese": "直走以后呢？", "pinyin": "zhí zǒu yǐ hòu ne?", "english": "After going straight?"},
    {"speaker": "B", "chinese": "在第二个路口右转。", "pinyin": "zài dì èr gè lù kǒu yòu zhuǎn.", "english": "Turn right at the second intersection."},
    {"speaker": "A", "chinese": "右转以后就能看到吗？", "pinyin": "yòu zhuǎn yǐ hòu jiù néng kàn dào ma?", "english": "Can I see it after turning right?"},
    {"speaker": "B", "chinese": "对，银行就在你的左边，旁边有一个超市。", "pinyin": "duì, yín háng jiù zài nǐ de zuǒ biān, páng biān yǒu yī gè chāo shì.", "english": "Yes, the bank is on your left, next to a supermarket."},
    {"speaker": "A", "chinese": "离这里远吗？", "pinyin": "lí zhè lǐ yuǎn ma?", "english": "Is it far from here?"},
    {"speaker": "B", "chinese": "不远，走路大概五分钟。", "pinyin": "bù yuǎn, zǒu lù dà gài wǔ fēn zhōng.", "english": "Not far, about 5 minutes on foot."},
    {"speaker": "A", "chinese": "太好了，谢谢你！", "pinyin": "tài hǎo le, xiè xie nǐ!", "english": "Great, thank you!"},
    {"speaker": "B", "chinese": "不客气！", "pinyin": "bù kè qi!", "english": "You're welcome!"},
]

DIALOGUE_2 = [
    {"speaker": "A", "chinese": "师傅，你好！去火车站。", "pinyin": "shī fu, nǐ hǎo! qù huǒ chē zhàn.", "english": "Driver, hello! To the train station."},
    {"speaker": "B", "chinese": "好的，上车吧。你赶时间吗？", "pinyin": "hǎo de, shàng chē ba. nǐ gǎn shí jiān ma?", "english": "OK, get in. Are you in a hurry?"},
    {"speaker": "A", "chinese": "有一点，我的火车三点半开。", "pinyin": "yǒu yī diǎn, wǒ de huǒ chē sān diǎn bàn kāi.", "english": "A little, my train departs at 3:30."},
    {"speaker": "B", "chinese": "没问题，大概二十分钟就到。", "pinyin": "méi wèn tí, dà gài èr shí fēn zhōng jiù dào.", "english": "No problem, about 20 minutes to get there."},
    {"speaker": "A", "chinese": "从这里到火车站远吗？", "pinyin": "cóng zhè lǐ dào huǒ chē zhàn yuǎn ma?", "english": "Is it far from here to the train station?"},
    {"speaker": "B", "chinese": "不太远，大概八公里。", "pinyin": "bù tài yuǎn, dà gài bā gōng lǐ.", "english": "Not too far, about 8 kilometers."},
    {"speaker": "A", "chinese": "大概多少钱？", "pinyin": "dà gài duō shǎo qián?", "english": "About how much will it cost?"},
    {"speaker": "B", "chinese": "二十五块左右吧。", "pinyin": "èr shí wǔ kuài zuǒ yòu ba.", "english": "Around 25 yuan."},
    {"speaker": "A", "chinese": "好的。到了，请在前面停车。", "pinyin": "hǎo de. dào le, qǐng zài qián miàn tíng chē.", "english": "OK. We're here, please stop up ahead."},
    {"speaker": "B", "chinese": "好，一共二十三块。", "pinyin": "hǎo, yī gòng èr shí sān kuài.", "english": "OK, that's 23 yuan total."},
]


class EP04Directions(ChineseLessonScene):
    episode_id = "ep04"
    episode_title = "问路和交通"
    episode_subtitle = "Directions & Transportation"

    def construct(self):
        self.show_title()
        self.show_section("生词 Vocabulary", "Key words for this lesson")
        for zh, py, en in VOCAB:
            self.show_vocab(zh, py, en)
        self.show_section("句子 Phrases", "Useful sentences")
        for zh, py, en in PHRASES:
            self.show_phrase(zh, py, en)
        self.show_section("对话一 Dialogue 1", "Asking for directions on the street")
        self.show_dialogue(DIALOGUE_1)
        self.show_section("对话二 Dialogue 2", "Taking a taxi")
        self.show_dialogue(DIALOGUE_2)
        self.show_section("复习 Review")
        self.show_review([{"chinese": zh, "pinyin": py, "english": en} for zh, py, en in VOCAB])
        self.show_end_card()
