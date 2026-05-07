"""EP03 — At the Restaurant (在餐厅)"""
from common.scene_base import ChineseLessonScene

VOCAB = [
    ("菜单", "cài dān", "menu"),
    ("点菜", "diǎn cài", "to order food"),
    ("米饭", "mǐ fàn", "rice"),
    ("面条", "miàn tiáo", "noodles"),
    ("水", "shuǐ", "water"),
    ("茶", "chá", "tea"),
    ("鸡肉", "jī ròu", "chicken"),
    ("牛肉", "niú ròu", "beef"),
    ("好吃", "hǎo chī", "delicious"),
    ("买单", "mǎi dān", "to pay the bill"),
    ("服务员", "fú wù yuán", "waiter / waitress"),
    ("辣", "là", "spicy"),
]

PHRASES = [
    ("请给我菜单。", "qǐng gěi wǒ cài dān.", "Please give me the menu."),
    ("我要点菜。", "wǒ yào diǎn cài.", "I'd like to order."),
    ("有什么推荐的吗？", "yǒu shén me tuī jiàn de ma?", "Do you have any recommendations?"),
    ("我不吃辣。", "wǒ bù chī là.", "I don't eat spicy food."),
    ("请来一碗米饭。", "qǐng lái yī wǎn mǐ fàn.", "A bowl of rice, please."),
    ("这道菜好吃吗？", "zhè dào cài hǎo chī ma?", "Is this dish delicious?"),
    ("买单，谢谢。", "mǎi dān, xiè xie.", "The bill, please."),
    ("可以用微信支付吗？", "kě yǐ yòng wēi xìn zhī fù ma?", "Can I pay with WeChat Pay?"),
]

DIALOGUE_1 = [
    {"speaker": "A", "chinese": "服务员，你好！我们要点菜。", "pinyin": "fú wù yuán, nǐ hǎo! wǒ men yào diǎn cài.", "english": "Waiter, hello! We'd like to order."},
    {"speaker": "B", "chinese": "好的，请看菜单。", "pinyin": "hǎo de, qǐng kàn cài dān.", "english": "OK, please look at the menu."},
    {"speaker": "A", "chinese": "有什么推荐的吗？", "pinyin": "yǒu shén me tuī jiàn de ma?", "english": "Do you have any recommendations?"},
    {"speaker": "B", "chinese": "我们的红烧牛肉很受欢迎。", "pinyin": "wǒ men de hóng shāo niú ròu hěn shòu huān yíng.", "english": "Our braised beef is very popular."},
    {"speaker": "A", "chinese": "好，来一份红烧牛肉，再来一个西红柿炒鸡蛋。", "pinyin": "hǎo, lái yī fèn hóng shāo niú ròu, zài lái yī gè xī hóng shì chǎo jī dàn.", "english": "OK, one braised beef and one tomato scrambled eggs."},
    {"speaker": "B", "chinese": "要米饭还是面条？", "pinyin": "yào mǐ fàn hái shì miàn tiáo?", "english": "Would you like rice or noodles?"},
    {"speaker": "A", "chinese": "两碗米饭，谢谢。", "pinyin": "liǎng wǎn mǐ fàn, xiè xie.", "english": "Two bowls of rice, thanks."},
    {"speaker": "B", "chinese": "喝什么？", "pinyin": "hē shén me?", "english": "What would you like to drink?"},
    {"speaker": "A", "chinese": "一壶茶就好了。", "pinyin": "yī hú chá jiù hǎo le.", "english": "A pot of tea will be fine."},
    {"speaker": "B", "chinese": "好的，请稍等。", "pinyin": "hǎo de, qǐng shāo děng.", "english": "OK, please wait a moment."},
]

DIALOGUE_2 = [
    {"speaker": "A", "chinese": "这道菜是什么？看起来很好吃。", "pinyin": "zhè dào cài shì shén me? kàn qǐ lái hěn hǎo chī.", "english": "What is this dish? It looks delicious."},
    {"speaker": "B", "chinese": "这是宫保鸡丁，有一点辣。", "pinyin": "zhè shì gōng bǎo jī dīng, yǒu yī diǎn là.", "english": "This is Kung Pao chicken, it's a little spicy."},
    {"speaker": "A", "chinese": "我不太能吃辣，有不辣的菜吗？", "pinyin": "wǒ bù tài néng chī là, yǒu bù là de cài ma?", "english": "I can't handle spicy food well. Do you have non-spicy dishes?"},
    {"speaker": "B", "chinese": "清蒸鱼不辣，味道也很好。", "pinyin": "qīng zhēng yú bù là, wèi dào yě hěn hǎo.", "english": "The steamed fish isn't spicy, and it tastes great too."},
    {"speaker": "A", "chinese": "好，那就来一份清蒸鱼。", "pinyin": "hǎo, nà jiù lái yī fèn qīng zhēng yú.", "english": "OK, I'll have the steamed fish then."},
    {"speaker": "B", "chinese": "好的，还需要别的吗？", "pinyin": "hǎo de, hái xū yào bié de ma?", "english": "OK, do you need anything else?"},
    {"speaker": "A", "chinese": "不用了，谢谢。可以买单吗？", "pinyin": "bù yòng le, xiè xie. kě yǐ mǎi dān ma?", "english": "No, thanks. Can I get the bill?"},
    {"speaker": "B", "chinese": "好的，一共一百二十八块。", "pinyin": "hǎo de, yī gòng yī bǎi èr shí bā kuài.", "english": "OK, the total is 128 yuan."},
    {"speaker": "A", "chinese": "可以用微信支付吗？", "pinyin": "kě yǐ yòng wēi xìn zhī fù ma?", "english": "Can I pay with WeChat Pay?"},
    {"speaker": "B", "chinese": "可以，请扫这个二维码。", "pinyin": "kě yǐ, qǐng sǎo zhè ge èr wéi mǎ.", "english": "Yes, please scan this QR code."},
]


class EP03Restaurant(ChineseLessonScene):
    episode_id = "ep03"
    episode_title = "在餐厅"
    episode_subtitle = "At the Restaurant"

    def construct(self):
        self.show_title()
        self.show_section("生词 Vocabulary", "Key words for this lesson")
        for zh, py, en in VOCAB:
            self.show_vocab(zh, py, en)
        self.show_section("句子 Phrases", "Useful sentences")
        for zh, py, en in PHRASES:
            self.show_phrase(zh, py, en)
        self.show_section("对话一 Dialogue 1", "Ordering at a restaurant")
        self.show_dialogue(DIALOGUE_1)
        self.show_section("对话二 Dialogue 2", "Asking about dishes and paying the bill")
        self.show_dialogue(DIALOGUE_2)
        self.show_section("复习 Review")
        self.show_review([{"chinese": zh, "pinyin": py, "english": en} for zh, py, en in VOCAB])
        self.show_end_card()
