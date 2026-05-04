"""EP09 — Hobbies & Free Time (爱好)"""
from common.scene_base import ChineseLessonScene

VOCAB = [
    ("喜欢", "xǐhuān", "to like"),
    ("看电影", "kàn diànyǐng", "to watch movies"),
    ("听音乐", "tīng yīnyuè", "to listen to music"),
    ("运动", "yùndòng", "exercise / sports"),
    ("旅游", "lǚyóu", "to travel"),
    ("读书", "dúshū", "to read books"),
    ("游泳", "yóuyǒng", "to swim"),
    ("跑步", "pǎobù", "to run / jogging"),
    ("周末", "zhōumò", "weekend"),
    ("有意思", "yǒu yìsi", "interesting"),
]

PHRASES = [
    ("你有什么爱好？", "Nǐ yǒu shénme àihào?", "What hobbies do you have?"),
    ("我喜欢看电影。", "Wǒ xǐhuān kàn diànyǐng.", "I like watching movies."),
    ("周末你一般做什么？", "Zhōumò nǐ yìbān zuò shénme?", "What do you usually do on weekends?"),
    ("我每天都跑步。", "Wǒ měitiān dōu pǎobù.", "I run every day."),
    ("游泳很有意思。", "Yóuyǒng hěn yǒu yìsi.", "Swimming is very interesting."),
    ("你喜欢听什么音乐？", "Nǐ xǐhuān tīng shénme yīnyuè?", "What music do you like to listen to?"),
    ("我想去旅游。", "Wǒ xiǎng qù lǚyóu.", "I want to go traveling."),
    ("我们一起去运动吧！", "Wǒmen yìqǐ qù yùndòng ba!", "Let's go exercise together!"),
]

DIALOGUE_1 = [
    {"speaker": "A", "chinese": "你好！你有什么爱好？", "pinyin": "Nǐ hǎo! Nǐ yǒu shénme àihào?", "english": "Hi! What hobbies do you have?"},
    {"speaker": "B", "chinese": "我喜欢听音乐和看电影。你呢？", "pinyin": "Wǒ xǐhuān tīng yīnyuè hé kàn diànyǐng. Nǐ ne?", "english": "I like listening to music and watching movies. You?"},
    {"speaker": "A", "chinese": "我喜欢运动，特别是游泳。", "pinyin": "Wǒ xǐhuān yùndòng, tèbié shì yóuyǒng.", "english": "I like sports, especially swimming."},
    {"speaker": "B", "chinese": "游泳很好！你经常游泳吗？", "pinyin": "Yóuyǒng hěn hǎo! Nǐ jīngcháng yóuyǒng ma?", "english": "Swimming is great! Do you swim often?"},
    {"speaker": "A", "chinese": "对，我每个周末都去游泳。", "pinyin": "Duì, wǒ měige zhōumò dōu qù yóuyǒng.", "english": "Yes, I go swimming every weekend."},
    {"speaker": "B", "chinese": "你也喜欢跑步吗？", "pinyin": "Nǐ yě xǐhuān pǎobù ma?", "english": "Do you also like running?"},
    {"speaker": "A", "chinese": "喜欢，我每天早上跑步。", "pinyin": "Xǐhuān, wǒ měitiān zǎoshang pǎobù.", "english": "Yes, I run every morning."},
    {"speaker": "B", "chinese": "真厉害！我不太喜欢运动。", "pinyin": "Zhēn lìhai! Wǒ bú tài xǐhuān yùndòng.", "english": "Impressive! I don't really like sports."},
    {"speaker": "A", "chinese": "那你喜欢读书吗？", "pinyin": "Nà nǐ xǐhuān dúshū ma?", "english": "Then do you like reading?"},
    {"speaker": "B", "chinese": "喜欢！读书很有意思。", "pinyin": "Xǐhuān! Dúshū hěn yǒu yìsi.", "english": "Yes! Reading is very interesting."},
]

DIALOGUE_2 = [
    {"speaker": "A", "chinese": "这个周末你有什么计划？", "pinyin": "Zhège zhōumò nǐ yǒu shénme jìhuà?", "english": "Do you have any plans this weekend?"},
    {"speaker": "B", "chinese": "还没有，你呢？", "pinyin": "Hái méiyǒu, nǐ ne?", "english": "Not yet, how about you?"},
    {"speaker": "A", "chinese": "我想去看电影，你想一起去吗？", "pinyin": "Wǒ xiǎng qù kàn diànyǐng, nǐ xiǎng yìqǐ qù ma?", "english": "I want to go see a movie, do you want to come?"},
    {"speaker": "B", "chinese": "好啊！看什么电影？", "pinyin": "Hǎo a! Kàn shénme diànyǐng?", "english": "Sure! What movie?"},
    {"speaker": "A", "chinese": "有一部新的中国电影，很有意思。", "pinyin": "Yǒu yí bù xīn de Zhōngguó diànyǐng, hěn yǒu yìsi.", "english": "There's a new Chinese movie, it's very interesting."},
    {"speaker": "B", "chinese": "太好了！看完电影以后我们做什么？", "pinyin": "Tài hǎo le! Kàn wán diànyǐng yǐhòu wǒmen zuò shénme?", "english": "Great! What shall we do after the movie?"},
    {"speaker": "A", "chinese": "我们可以去游泳，你觉得怎么样？", "pinyin": "Wǒmen kěyǐ qù yóuyǒng, nǐ juéde zěnmeyàng?", "english": "We could go swimming, what do you think?"},
    {"speaker": "B", "chinese": "游泳太累了。我们去听音乐吧。", "pinyin": "Yóuyǒng tài lèi le. Wǒmen qù tīng yīnyuè ba.", "english": "Swimming is too tiring. Let's go listen to music."},
    {"speaker": "A", "chinese": "也行！附近有一个音乐会。", "pinyin": "Yě xíng! Fùjìn yǒu yíge yīnyuèhuì.", "english": "That works too! There's a concert nearby."},
    {"speaker": "B", "chinese": "太好了，那我们周末见！", "pinyin": "Tài hǎo le, nà wǒmen zhōumò jiàn!", "english": "Great, see you this weekend!"},
]


class EP09Hobbies(ChineseLessonScene):
    episode_id = "ep09"
    episode_title = "爱好"
    episode_subtitle = "Hobbies & Free Time"

    def construct(self):
        self.show_title()
        self.show_section("生词 Vocabulary", "Key words for this lesson")
        for zh, py, en in VOCAB:
            self.show_vocab(zh, py, en)
        self.show_section("句子 Phrases", "Useful sentences")
        for zh, py, en in PHRASES:
            self.show_phrase(zh, py, en)
        self.show_section("对话一 Dialogue 1", "Getting to know someone's hobbies")
        self.show_dialogue(DIALOGUE_1)
        self.show_section("对话二 Dialogue 2", "Making weekend plans together")
        self.show_dialogue(DIALOGUE_2)
        self.show_section("复习 Review")
        self.show_review([{"chinese": zh, "pinyin": py, "english": en} for zh, py, en in VOCAB])
        self.show_end_card()
