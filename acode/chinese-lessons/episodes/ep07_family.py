"""EP07 — Family & Relationships (家庭)"""
from common.scene_base import ChineseLessonScene

VOCAB = [
    ("爸爸", "bàba", "father / dad"),
    ("妈妈", "māma", "mother / mom"),
    ("哥哥", "gēge", "older brother"),
    ("姐姐", "jiějie", "older sister"),
    ("弟弟", "dìdi", "younger brother"),
    ("妹妹", "mèimei", "younger sister"),
    ("家", "jiā", "home / family"),
    ("几口人", "jǐ kǒu rén", "how many people (in a family)"),
    ("孩子", "háizi", "child / children"),
    ("爱", "ài", "love"),
]

PHRASES = [
    ("你家有几口人？", "Nǐ jiā yǒu jǐ kǒu rén?", "How many people are in your family?"),
    ("我家有四口人。", "Wǒ jiā yǒu sì kǒu rén.", "There are four people in my family."),
    ("你有兄弟姐妹吗？", "Nǐ yǒu xiōngdì jiěmèi ma?", "Do you have siblings?"),
    ("我有一个哥哥和一个妹妹。", "Wǒ yǒu yí ge gēge hé yí ge mèimei.", "I have an older brother and a younger sister."),
    ("你爸爸做什么工作？", "Nǐ bàba zuò shénme gōngzuò?", "What does your father do for work?"),
    ("我很爱我的家人。", "Wǒ hěn ài wǒ de jiārén.", "I love my family very much."),
    ("她有两个孩子。", "Tā yǒu liǎng ge háizi.", "She has two children."),
    ("这是我姐姐。", "Zhè shì wǒ jiějie.", "This is my older sister."),
]

DIALOGUE_1 = [
    {"speaker": "A", "chinese": "这是你的家人吗？", "pinyin": "Zhè shì nǐ de jiārén ma?", "english": "Is this your family?"},
    {"speaker": "B", "chinese": "是的。来，我介绍一下。", "pinyin": "Shì de. Lái, wǒ jièshào yíxià.", "english": "Yes. Come, let me introduce them."},
    {"speaker": "B", "chinese": "这是我爸爸，这是我妈妈。", "pinyin": "Zhè shì wǒ bàba, zhè shì wǒ māma.", "english": "This is my dad, this is my mom."},
    {"speaker": "A", "chinese": "叔叔阿姨好！", "pinyin": "Shūshu āyí hǎo!", "english": "Hello, uncle and auntie!"},
    {"speaker": "B", "chinese": "这是我哥哥，他在北京工作。", "pinyin": "Zhè shì wǒ gēge, tā zài Běijīng gōngzuò.", "english": "This is my older brother, he works in Beijing."},
    {"speaker": "A", "chinese": "你还有弟弟妹妹吗？", "pinyin": "Nǐ hái yǒu dìdi mèimei ma?", "english": "Do you also have younger siblings?"},
    {"speaker": "B", "chinese": "有，我有一个妹妹，她还在上学。", "pinyin": "Yǒu, wǒ yǒu yí ge mèimei, tā hái zài shàngxué.", "english": "Yes, I have a younger sister, she's still in school."},
    {"speaker": "A", "chinese": "你家有几口人？", "pinyin": "Nǐ jiā yǒu jǐ kǒu rén?", "english": "How many people are in your family?"},
    {"speaker": "B", "chinese": "五口人：爸爸、妈妈、哥哥、妹妹和我。", "pinyin": "Wǔ kǒu rén: bàba, māma, gēge, mèimei hé wǒ.", "english": "Five: dad, mom, older brother, younger sister, and me."},
    {"speaker": "A", "chinese": "你的家人都很好！", "pinyin": "Nǐ de jiārén dōu hěn hǎo!", "english": "Your family is all so nice!"},
]

DIALOGUE_2 = [
    {"speaker": "A", "chinese": "这张照片是什么时候拍的？", "pinyin": "Zhè zhāng zhàopiàn shì shénme shíhou pāi de?", "english": "When was this photo taken?"},
    {"speaker": "B", "chinese": "去年春节的时候。", "pinyin": "Qùnián Chūnjié de shíhou.", "english": "During last year's Spring Festival."},
    {"speaker": "A", "chinese": "这个是你姐姐吗？", "pinyin": "Zhège shì nǐ jiějie ma?", "english": "Is this your older sister?"},
    {"speaker": "B", "chinese": "对，她旁边是她的孩子。", "pinyin": "Duì, tā pángbiān shì tā de háizi.", "english": "Yes, next to her is her child."},
    {"speaker": "A", "chinese": "好可爱！几岁了？", "pinyin": "Hǎo kě'ài! Jǐ suì le?", "english": "So cute! How old?"},
    {"speaker": "B", "chinese": "三岁了。我们都很爱他。", "pinyin": "Sān suì le. Wǒmen dōu hěn ài tā.", "english": "Three years old. We all love him."},
    {"speaker": "A", "chinese": "这个是你弟弟吗？他很高！", "pinyin": "Zhège shì nǐ dìdi ma? Tā hěn gāo!", "english": "Is this your younger brother? He's so tall!"},
    {"speaker": "B", "chinese": "是的，他今年十八岁。", "pinyin": "Shì de, tā jīnnián shíbā suì.", "english": "Yes, he's eighteen this year."},
    {"speaker": "A", "chinese": "你爸爸妈妈看起来很年轻。", "pinyin": "Nǐ bàba māma kàn qǐlái hěn niánqīng.", "english": "Your parents look very young."},
    {"speaker": "B", "chinese": "谢谢！我爱我的家。", "pinyin": "Xièxie! Wǒ ài wǒ de jiā.", "english": "Thanks! I love my family."},
]


class EP07Family(ChineseLessonScene):
    episode_id = "ep07"
    episode_title = "家庭"
    episode_subtitle = "Family & Relationships"

    def construct(self):
        self.show_title()
        self.show_section("生词 Vocabulary", "Key words for this lesson")
        for zh, py, en in VOCAB:
            self.show_vocab(zh, py, en)
        self.show_section("句子 Phrases", "Useful sentences")
        for zh, py, en in PHRASES:
            self.show_phrase(zh, py, en)
        self.show_section("对话一 Dialogue 1", "Introducing your family to a friend")
        self.show_dialogue(DIALOGUE_1)
        self.show_section("对话二 Dialogue 2", "Looking at family photos together")
        self.show_dialogue(DIALOGUE_2)
        self.show_section("复习 Review")
        self.show_review([{"chinese": zh, "pinyin": py, "english": en} for zh, py, en in VOCAB])
        self.show_end_card()
