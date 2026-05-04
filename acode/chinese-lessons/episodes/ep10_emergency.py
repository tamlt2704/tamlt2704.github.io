"""EP10 — Emergency & Useful Phrases (紧急情况和常用语)"""
from common.scene_base import ChineseLessonScene

VOCAB = [
    ("帮忙", "bāngmáng", "to help"),
    ("医院", "yīyuàn", "hospital"),
    ("警察", "jǐngchá", "police"),
    ("不舒服", "bù shūfu", "uncomfortable / unwell"),
    ("疼", "téng", "painful / to hurt"),
    ("药", "yào", "medicine"),
    ("危险", "wēixiǎn", "dangerous"),
    ("小心", "xiǎoxīn", "be careful"),
    ("打电话", "dǎ diànhuà", "to make a phone call"),
    ("重要", "zhòngyào", "important"),
]

PHRASES = [
    ("请帮帮我！", "Qǐng bāngbang wǒ!", "Please help me!"),
    ("我不舒服。", "Wǒ bù shūfu.", "I don't feel well."),
    ("我头很疼。", "Wǒ tóu hěn téng.", "My head hurts a lot."),
    ("请带我去医院。", "Qǐng dài wǒ qù yīyuàn.", "Please take me to the hospital."),
    ("请帮我打电话叫警察。", "Qǐng bāng wǒ dǎ diànhuà jiào jǐngchá.", "Please call the police for me."),
    ("这里危险，小心！", "Zhèlǐ wēixiǎn, xiǎoxīn!", "It's dangerous here, be careful!"),
    ("附近有药店吗？", "Fùjìn yǒu yàodiàn ma?", "Is there a pharmacy nearby?"),
    ("这很重要。", "Zhè hěn zhòngyào.", "This is very important."),
]

DIALOGUE_1 = [
    {"speaker": "A", "chinese": "你怎么了？脸色不太好。", "pinyin": "Nǐ zěnme le? Liǎnsè bú tài hǎo.", "english": "What's wrong? You don't look well."},
    {"speaker": "B", "chinese": "我不舒服，肚子很疼。", "pinyin": "Wǒ bù shūfu, dùzi hěn téng.", "english": "I don't feel well, my stomach really hurts."},
    {"speaker": "A", "chinese": "你需要去医院吗？", "pinyin": "Nǐ xūyào qù yīyuàn ma?", "english": "Do you need to go to the hospital?"},
    {"speaker": "B", "chinese": "先不用，我想买点药。", "pinyin": "Xiān búyòng, wǒ xiǎng mǎi diǎn yào.", "english": "Not yet, I want to buy some medicine first."},
    {"speaker": "A", "chinese": "好，附近有一家药店。", "pinyin": "Hǎo, fùjìn yǒu yì jiā yàodiàn.", "english": "Okay, there's a pharmacy nearby."},
    {"speaker": "B", "chinese": "太好了，你能带我去吗？", "pinyin": "Tài hǎo le, nǐ néng dài wǒ qù ma?", "english": "Great, can you take me there?"},
    {"speaker": "A", "chinese": "当然可以，我们走吧。", "pinyin": "Dāngrán kěyǐ, wǒmen zǒu ba.", "english": "Of course, let's go."},
    {"speaker": "B", "chinese": "谢谢你帮忙！", "pinyin": "Xièxie nǐ bāngmáng!", "english": "Thank you for your help!"},
    {"speaker": "A", "chinese": "不客气。如果吃了药还不舒服，我们就去医院。", "pinyin": "Bú kèqi. Rúguǒ chī le yào hái bù shūfu, wǒmen jiù qù yīyuàn.", "english": "You're welcome. If you still feel unwell after taking medicine, we'll go to the hospital."},
    {"speaker": "B", "chinese": "好的，谢谢你。", "pinyin": "Hǎo de, xièxie nǐ.", "english": "Okay, thank you."},
]

DIALOGUE_2 = [
    {"speaker": "A", "chinese": "请问，你能帮帮我吗？", "pinyin": "Qǐngwèn, nǐ néng bāngbang wǒ ma?", "english": "Excuse me, can you help me?"},
    {"speaker": "B", "chinese": "怎么了？", "pinyin": "Zěnme le?", "english": "What's wrong?"},
    {"speaker": "A", "chinese": "我迷路了，找不到我的酒店。", "pinyin": "Wǒ mílù le, zhǎo bú dào wǒ de jiǔdiàn.", "english": "I'm lost, I can't find my hotel."},
    {"speaker": "B", "chinese": "你知道酒店的名字吗？", "pinyin": "Nǐ zhīdào jiǔdiàn de míngzi ma?", "english": "Do you know the hotel's name?"},
    {"speaker": "A", "chinese": "知道，但是我的手机没电了。", "pinyin": "Zhīdào, dànshì wǒ de shǒujī méi diàn le.", "english": "Yes, but my phone is dead."},
    {"speaker": "B", "chinese": "没关系，你可以用我的手机打电话。", "pinyin": "Méi guānxi, nǐ kěyǐ yòng wǒ de shǒujī dǎ diànhuà.", "english": "No problem, you can use my phone to make a call."},
    {"speaker": "A", "chinese": "太感谢了！这对我很重要。", "pinyin": "Tài gǎnxiè le! Zhè duì wǒ hěn zhòngyào.", "english": "Thank you so much! This is very important to me."},
    {"speaker": "B", "chinese": "不客气。你也可以问那边的警察。", "pinyin": "Bú kèqi. Nǐ yě kěyǐ wèn nàbiān de jǐngchá.", "english": "You're welcome. You can also ask the police over there."},
    {"speaker": "A", "chinese": "好的，谢谢你帮忙！", "pinyin": "Hǎo de, xièxie nǐ bāngmáng!", "english": "Okay, thank you for your help!"},
    {"speaker": "B", "chinese": "小心一点，祝你好运！", "pinyin": "Xiǎoxīn yìdiǎn, zhù nǐ hǎoyùn!", "english": "Be careful, good luck!"},
]


class EP10Emergency(ChineseLessonScene):
    episode_id = "ep10"
    episode_title = "紧急情况和常用语"
    episode_subtitle = "Emergency & Useful Phrases"

    def construct(self):
        self.show_title()
        self.show_section("生词 Vocabulary", "Key words for this lesson")
        for zh, py, en in VOCAB:
            self.show_vocab(zh, py, en)
        self.show_section("句子 Phrases", "Useful sentences")
        for zh, py, en in PHRASES:
            self.show_phrase(zh, py, en)
        self.show_section("对话一 Dialogue 1", "Feeling sick and going to a pharmacy")
        self.show_dialogue(DIALOGUE_1)
        self.show_section("对话二 Dialogue 2", "Lost and asking for help")
        self.show_dialogue(DIALOGUE_2)
        self.show_section("复习 Review")
        self.show_review([{"chinese": zh, "pinyin": py, "english": en} for zh, py, en in VOCAB])
        self.show_end_card()
