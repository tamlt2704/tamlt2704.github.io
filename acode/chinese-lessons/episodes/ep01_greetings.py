"""EP01 — Greetings & Self-Introduction (打招呼和自我介绍)"""
from common.scene_base import ChineseLessonScene

VOCAB = [
    ("你好", "nǐ hǎo", "Hello"),
    ("你好吗", "nǐ hǎo ma", "How are you?"),
    ("我很好", "wǒ hěn hǎo", "I'm fine"),
    ("谢谢", "xiè xie", "Thank you"),
    ("再见", "zài jiàn", "Goodbye"),
    ("不客气", "bú kè qi", "You're welcome"),
    ("对不起", "duì bu qǐ", "Sorry"),
    ("没关系", "méi guānxi", "It's okay"),
    ("请", "qǐng", "Please"),
    ("早上好", "zǎo shang hǎo", "Good morning"),
]

PHRASES = [
    ("我叫小明", "wǒ jiào Xiǎo Míng", "My name is Xiao Ming"),
    ("你叫什么名字？", "nǐ jiào shénme míngzi?", "What is your name?"),
    ("认识你很高兴", "rènshi nǐ hěn gāoxìng", "Nice to meet you"),
    ("你是哪国人？", "nǐ shì nǎ guó rén?", "Where are you from?"),
    ("我是美国人", "wǒ shì Měiguó rén", "I am American"),
    ("你呢？", "nǐ ne?", "And you?"),
    ("我是中国人", "wǒ shì Zhōngguó rén", "I am Chinese"),
    ("你会说中文吗？", "nǐ huì shuō Zhōngwén ma?", "Can you speak Chinese?"),
]

DIALOGUE_1 = [
    {"speaker": "A", "chinese": "你好！我叫小明。",
     "pinyin": "nǐ hǎo! wǒ jiào Xiǎo Míng.",
     "english": "Hello! My name is Xiao Ming."},
    {"speaker": "B", "chinese": "你好！我叫小红。你好吗？",
     "pinyin": "nǐ hǎo! wǒ jiào Xiǎo Hóng. nǐ hǎo ma?",
     "english": "Hello! I'm Xiao Hong. How are you?"},
    {"speaker": "A", "chinese": "我很好，谢谢！你呢？",
     "pinyin": "wǒ hěn hǎo, xiè xie! nǐ ne?",
     "english": "I'm fine, thanks! And you?"},
    {"speaker": "B", "chinese": "我也很好。你是哪国人？",
     "pinyin": "wǒ yě hěn hǎo. nǐ shì nǎ guó rén?",
     "english": "I'm fine too. Where are you from?"},
    {"speaker": "A", "chinese": "我是美国人。你呢？",
     "pinyin": "wǒ shì Měiguó rén. nǐ ne?",
     "english": "I'm American. And you?"},
    {"speaker": "B", "chinese": "我是中国人。你会说中文吗？",
     "pinyin": "wǒ shì Zhōngguó rén. nǐ huì shuō Zhōngwén ma?",
     "english": "I'm Chinese. Can you speak Chinese?"},
    {"speaker": "A", "chinese": "会一点点。我在学中文。",
     "pinyin": "huì yì diǎndiǎn. wǒ zài xué Zhōngwén.",
     "english": "A little bit. I'm learning Chinese."},
    {"speaker": "B", "chinese": "你的中文很好！认识你很高兴！",
     "pinyin": "nǐ de Zhōngwén hěn hǎo! rènshi nǐ hěn gāoxìng!",
     "english": "Your Chinese is great! Nice to meet you!"},
    {"speaker": "A", "chinese": "谢谢！认识你很高兴！再见！",
     "pinyin": "xiè xie! rènshi nǐ hěn gāoxìng! zài jiàn!",
     "english": "Thanks! Nice to meet you! Goodbye!"},
    {"speaker": "B", "chinese": "再见！",
     "pinyin": "zài jiàn!", "english": "Goodbye!"},
]

DIALOGUE_2 = [
    {"speaker": "A", "chinese": "早上好！",
     "pinyin": "zǎo shang hǎo!", "english": "Good morning!"},
    {"speaker": "B", "chinese": "早上好！你好吗？",
     "pinyin": "zǎo shang hǎo! nǐ hǎo ma?",
     "english": "Good morning! How are you?"},
    {"speaker": "A", "chinese": "我很好。对不起，你叫什么名字？",
     "pinyin": "wǒ hěn hǎo. duì bu qǐ, nǐ jiào shénme míngzi?",
     "english": "I'm fine. Sorry, what is your name?"},
    {"speaker": "B", "chinese": "没关系！我叫大卫。你呢？",
     "pinyin": "méi guānxi! wǒ jiào Dàwèi. nǐ ne?",
     "english": "No problem! I'm David. And you?"},
    {"speaker": "A", "chinese": "我叫李华。认识你很高兴，大卫！",
     "pinyin": "wǒ jiào Lǐ Huá. rènshi nǐ hěn gāoxìng, Dàwèi!",
     "english": "I'm Li Hua. Nice to meet you, David!"},
    {"speaker": "B", "chinese": "认识你很高兴，李华！谢谢！",
     "pinyin": "rènshi nǐ hěn gāoxìng, Lǐ Huá! xiè xie!",
     "english": "Nice to meet you, Li Hua! Thanks!"},
    {"speaker": "A", "chinese": "不客气！再见！",
     "pinyin": "bú kè qi! zài jiàn!", "english": "You're welcome! Goodbye!"},
    {"speaker": "B", "chinese": "再见！",
     "pinyin": "zài jiàn!", "english": "Goodbye!"},
]


class EP01Greetings(ChineseLessonScene):
    episode_id = "ep01"
    episode_title = "打招呼和自我介绍"
    episode_subtitle = "Greetings & Self-Introduction"

    def construct(self):
        self.show_title()

        self.show_section("生词 Vocabulary", "Key words for this lesson")
        for zh, py, en in VOCAB:
            self.show_vocab(zh, py, en)

        self.show_section("句子 Phrases", "Useful sentences")
        for zh, py, en in PHRASES:
            self.show_phrase(zh, py, en)

        self.show_section("对话一 Dialogue 1", "Xiao Ming meets Xiao Hong")
        self.show_dialogue(DIALOGUE_1)

        self.show_section("对话二 Dialogue 2", "A morning greeting at work")
        self.show_dialogue(DIALOGUE_2)

        self.show_section("复习 Review")
        self.show_review([{"chinese": zh, "pinyin": py, "english": en}
                          for zh, py, en in VOCAB])

        self.show_end_card()
