const phrases: Record<string, { cn: string; py: string; en: string }[]> = {
    "我": [
        { cn: "我是学生", py: "wǒ shì xuéshēng", en: "I am a student" },
        { cn: "我爱你", py: "wǒ ài nǐ", en: "I love you" },
        { cn: "我的家", py: "wǒ de jiā", en: "my home" },
    ],
    "你": [
        { cn: "你好", py: "nǐ hǎo", en: "hello" },
        { cn: "你叫什么", py: "nǐ jiào shénme", en: "what is your name?" },
        { cn: "谢谢你", py: "xièxie nǐ", en: "thank you" },
    ],
    "他": [
        { cn: "他是谁", py: "tā shì shéi", en: "who is he?" },
        { cn: "他很高", py: "tā hěn gāo", en: "he is tall" },
        { cn: "他的书", py: "tā de shū", en: "his book" },
    ],
    "她": [
        { cn: "她很美", py: "tā hěn měi", en: "she is beautiful" },
        { cn: "她是老师", py: "tā shì lǎoshī", en: "she is a teacher" },
        { cn: "她的猫", py: "tā de māo", en: "her cat" },
    ],
    "是": [
        { cn: "这是书", py: "zhè shì shū", en: "this is a book" },
        { cn: "我是中国人", py: "wǒ shì zhōngguó rén", en: "I am Chinese" },
        { cn: "他是谁", py: "tā shì shéi", en: "who is he?" },
    ],
    "不": [
        { cn: "不好", py: "bù hǎo", en: "not good" },
        { cn: "不是", py: "bú shì", en: "is not" },
        { cn: "不要", py: "bú yào", en: "don't want" },
    ],
    "大": [
        { cn: "大家好", py: "dàjiā hǎo", en: "hello everyone" },
        { cn: "很大", py: "hěn dà", en: "very big" },
        { cn: "大学", py: "dàxué", en: "university" },
    ],
    "小": [
        { cn: "小朋友", py: "xiǎo péngyou", en: "little friend / kids" },
        { cn: "小狗", py: "xiǎo gǒu", en: "puppy" },
        { cn: "小心", py: "xiǎoxīn", en: "be careful" },
    ],
    "人": [
        { cn: "中国人", py: "zhōngguó rén", en: "Chinese person" },
        { cn: "好人", py: "hǎo rén", en: "good person" },
        { cn: "人们", py: "rénmen", en: "people" },
    ],
    "中": [
        { cn: "中国", py: "zhōngguó", en: "China" },
        { cn: "中文", py: "zhōngwén", en: "Chinese language" },
        { cn: "中间", py: "zhōngjiān", en: "middle" },
    ],
    "国": [
        { cn: "中国", py: "zhōngguó", en: "China" },
        { cn: "国家", py: "guójiā", en: "country" },
        { cn: "美国", py: "měiguó", en: "America" },
    ],
    "学": [
        { cn: "学生", py: "xuéshēng", en: "student" },
        { cn: "学校", py: "xuéxiào", en: "school" },
        { cn: "学习", py: "xuéxí", en: "to study" },
    ],
    "家": [
        { cn: "回家", py: "huí jiā", en: "go home" },
        { cn: "大家", py: "dàjiā", en: "everyone" },
        { cn: "家人", py: "jiārén", en: "family" },
    ],
    "好": [
        { cn: "你好", py: "nǐ hǎo", en: "hello" },
        { cn: "好吃", py: "hǎochī", en: "delicious" },
        { cn: "好看", py: "hǎokàn", en: "good-looking" },
    ],
    "天": [
        { cn: "今天", py: "jīntiān", en: "today" },
        { cn: "天气", py: "tiānqì", en: "weather" },
        { cn: "每天", py: "měitiān", en: "every day" },
    ],
    "水": [
        { cn: "喝水", py: "hē shuǐ", en: "drink water" },
        { cn: "水果", py: "shuǐguǒ", en: "fruit" },
        { cn: "水里", py: "shuǐ lǐ", en: "in the water" },
    ],
    "火": [
        { cn: "火车", py: "huǒchē", en: "train" },
        { cn: "大火", py: "dà huǒ", en: "big fire" },
        { cn: "火山", py: "huǒshān", en: "volcano" },
    ],
    "山": [
        { cn: "山上", py: "shān shàng", en: "on the mountain" },
        { cn: "火山", py: "huǒshān", en: "volcano" },
        { cn: "高山", py: "gāo shān", en: "tall mountain" },
    ],
    "日": [
        { cn: "日本", py: "rìběn", en: "Japan" },
        { cn: "生日", py: "shēngrì", en: "birthday" },
        { cn: "今日", py: "jīnrì", en: "today" },
    ],
    "月": [
        { cn: "月亮", py: "yuèliang", en: "moon" },
        { cn: "一月", py: "yī yuè", en: "January" },
        { cn: "月饼", py: "yuèbǐng", en: "mooncake" },
    ],
    "心": [
        { cn: "开心", py: "kāixīn", en: "happy" },
        { cn: "小心", py: "xiǎoxīn", en: "be careful" },
        { cn: "心里", py: "xīnlǐ", en: "in one's heart" },
    ],
    "手": [
        { cn: "手机", py: "shǒujī", en: "phone" },
        { cn: "左手", py: "zuǒ shǒu", en: "left hand" },
        { cn: "洗手", py: "xǐ shǒu", en: "wash hands" },
    ],
    "口": [
        { cn: "开口", py: "kāikǒu", en: "open mouth / speak" },
        { cn: "门口", py: "ménkǒu", en: "doorway" },
        { cn: "人口", py: "rénkǒu", en: "population" },
    ],
    "一": [
        { cn: "一个", py: "yī gè", en: "one (thing)" },
        { cn: "第一", py: "dì yī", en: "first" },
        { cn: "一起", py: "yīqǐ", en: "together" },
    ],
    "二": [
        { cn: "二月", py: "èr yuè", en: "February" },
        { cn: "第二", py: "dì èr", en: "second" },
        { cn: "二十", py: "èr shí", en: "twenty" },
    ],
    "三": [
        { cn: "三个", py: "sān gè", en: "three (things)" },
        { cn: "三月", py: "sān yuè", en: "March" },
        { cn: "星期三", py: "xīngqī sān", en: "Wednesday" },
    ],
    "四": [
        { cn: "四月", py: "sì yuè", en: "April" },
        { cn: "四个人", py: "sì gè rén", en: "four people" },
        { cn: "四季", py: "sì jì", en: "four seasons" },
    ],
    "五": [
        { cn: "五月", py: "wǔ yuè", en: "May" },
        { cn: "五个", py: "wǔ gè", en: "five (things)" },
        { cn: "星期五", py: "xīngqī wǔ", en: "Friday" },
    ],
    "六": [
        { cn: "六月", py: "liù yuè", en: "June" },
        { cn: "六个", py: "liù gè", en: "six (things)" },
        { cn: "星期六", py: "xīngqī liù", en: "Saturday" },
    ],
    "七": [
        { cn: "七月", py: "qī yuè", en: "July" },
        { cn: "七天", py: "qī tiān", en: "seven days" },
        { cn: "七十", py: "qī shí", en: "seventy" },
    ],
    "八": [
        { cn: "八月", py: "bā yuè", en: "August" },
        { cn: "八个", py: "bā gè", en: "eight (things)" },
        { cn: "八十", py: "bā shí", en: "eighty" },
    ],
    "九": [
        { cn: "九月", py: "jiǔ yuè", en: "September" },
        { cn: "九十", py: "jiǔ shí", en: "ninety" },
        { cn: "九个", py: "jiǔ gè", en: "nine (things)" },
    ],
    "十": [
        { cn: "十月", py: "shí yuè", en: "October" },
        { cn: "十个", py: "shí gè", en: "ten (things)" },
        { cn: "十分", py: "shífēn", en: "very, extremely" },
    ],
    "吃": [
        { cn: "吃饭", py: "chī fàn", en: "eat a meal" },
        { cn: "好吃", py: "hǎochī", en: "delicious" },
        { cn: "吃水果", py: "chī shuǐguǒ", en: "eat fruit" },
    ],
    "喝": [
        { cn: "喝水", py: "hē shuǐ", en: "drink water" },
        { cn: "喝茶", py: "hē chá", en: "drink tea" },
        { cn: "喝牛奶", py: "hē niúnǎi", en: "drink milk" },
    ],
    "爱": [
        { cn: "我爱你", py: "wǒ ài nǐ", en: "I love you" },
        { cn: "爱好", py: "àihào", en: "hobby" },
        { cn: "可爱", py: "kě'ài", en: "cute" },
    ],
    "看": [
        { cn: "看书", py: "kàn shū", en: "read a book" },
        { cn: "好看", py: "hǎokàn", en: "good-looking" },
        { cn: "看见", py: "kànjiàn", en: "to see" },
    ],
    "听": [
        { cn: "听音乐", py: "tīng yīnyuè", en: "listen to music" },
        { cn: "好听", py: "hǎotīng", en: "nice to hear" },
        { cn: "听说", py: "tīngshuō", en: "heard that" },
    ],
    "说": [
        { cn: "说话", py: "shuōhuà", en: "speak / talk" },
        { cn: "听说", py: "tīngshuō", en: "heard that" },
        { cn: "怎么说", py: "zěnme shuō", en: "how to say" },
    ],
    "走": [
        { cn: "走路", py: "zǒulù", en: "walk" },
        { cn: "走吧", py: "zǒu ba", en: "let's go" },
        { cn: "走开", py: "zǒukāi", en: "go away" },
    ],
    "跑": [
        { cn: "跑步", py: "pǎobù", en: "run / jog" },
        { cn: "快跑", py: "kuài pǎo", en: "run fast!" },
        { cn: "跑来跑去", py: "pǎo lái pǎo qù", en: "running around" },
    ],
    "猫": [
        { cn: "小猫", py: "xiǎo māo", en: "kitten" },
        { cn: "猫咪", py: "māo mī", en: "kitty" },
        { cn: "花猫", py: "huā māo", en: "tabby cat" },
    ],
    "狗": [
        { cn: "小狗", py: "xiǎo gǒu", en: "puppy" },
        { cn: "热狗", py: "règǒu", en: "hot dog" },
        { cn: "狗狗", py: "gǒu gǒu", en: "doggy" },
    ],
    "鱼": [
        { cn: "小鱼", py: "xiǎo yú", en: "little fish" },
        { cn: "鱼肉", py: "yú ròu", en: "fish meat" },
        { cn: "金鱼", py: "jīnyú", en: "goldfish" },
    ],
    "鸟": [
        { cn: "小鸟", py: "xiǎo niǎo", en: "little bird" },
        { cn: "鸟儿", py: "niǎo er", en: "birdie" },
        { cn: "飞鸟", py: "fēi niǎo", en: "flying bird" },
    ],
    "花": [
        { cn: "花园", py: "huāyuán", en: "garden" },
        { cn: "开花", py: "kāihuā", en: "bloom" },
        { cn: "花朵", py: "huāduǒ", en: "flower" },
    ],
    "树": [
        { cn: "大树", py: "dà shù", en: "big tree" },
        { cn: "树叶", py: "shùyè", en: "leaf" },
        { cn: "树上", py: "shù shàng", en: "on the tree" },
    ],
    "红": [
        { cn: "红色", py: "hóngsè", en: "red color" },
        { cn: "红花", py: "hóng huā", en: "red flower" },
        { cn: "红灯", py: "hóng dēng", en: "red light" },
    ],
    "蓝": [
        { cn: "蓝色", py: "lánsè", en: "blue color" },
        { cn: "蓝天", py: "lán tiān", en: "blue sky" },
        { cn: "蓝色的海", py: "lánsè de hǎi", en: "blue sea" },
    ],
    "绿": [
        { cn: "绿色", py: "lǜsè", en: "green color" },
        { cn: "绿树", py: "lǜ shù", en: "green tree" },
        { cn: "绿灯", py: "lǜ dēng", en: "green light" },
    ],
    "白": [
        { cn: "白色", py: "báisè", en: "white color" },
        { cn: "白云", py: "bái yún", en: "white cloud" },
        { cn: "白天", py: "báitiān", en: "daytime" },
    ],
    "黑": [
        { cn: "黑色", py: "hēisè", en: "black color" },
        { cn: "黑夜", py: "hēiyè", en: "dark night" },
        { cn: "黑板", py: "hēibǎn", en: "blackboard" },
    ],
    "黄": [
        { cn: "黄色", py: "huángsè", en: "yellow color" },
        { cn: "黄河", py: "huánghé", en: "Yellow River" },
        { cn: "黄金", py: "huángjīn", en: "gold" },
    ],
    "书": [
        { cn: "看书", py: "kàn shū", en: "read a book" },
        { cn: "书包", py: "shūbāo", en: "schoolbag" },
        { cn: "图书馆", py: "túshūguǎn", en: "library" },
    ],
    "门": [
        { cn: "开门", py: "kāi mén", en: "open the door" },
        { cn: "门口", py: "ménkǒu", en: "doorway" },
        { cn: "大门", py: "dà mén", en: "main gate" },
    ],
    "车": [
        { cn: "火车", py: "huǒchē", en: "train" },
        { cn: "汽车", py: "qìchē", en: "car" },
        { cn: "上车", py: "shàng chē", en: "get on (vehicle)" },
    ],
    "马": [
        { cn: "小马", py: "xiǎo mǎ", en: "pony" },
        { cn: "马上", py: "mǎshàng", en: "immediately" },
        { cn: "骑马", py: "qí mǎ", en: "ride a horse" },
    ],
    "风": [
        { cn: "大风", py: "dà fēng", en: "strong wind" },
        { cn: "风景", py: "fēngjǐng", en: "scenery" },
        { cn: "台风", py: "táifēng", en: "typhoon" },
    ],
    "雨": [
        { cn: "下雨", py: "xià yǔ", en: "raining" },
        { cn: "雨天", py: "yǔ tiān", en: "rainy day" },
        { cn: "雨伞", py: "yǔsǎn", en: "umbrella" },
    ],
    "雪": [
        { cn: "下雪", py: "xià xuě", en: "snowing" },
        { cn: "雪人", py: "xuě rén", en: "snowman" },
        { cn: "雪花", py: "xuěhuā", en: "snowflake" },
    ],
    "星": [
        { cn: "星星", py: "xīngxing", en: "star" },
        { cn: "星期", py: "xīngqī", en: "week" },
        { cn: "明星", py: "míngxīng", en: "celebrity" },
    ],
    "飞": [
        { cn: "飞机", py: "fēijī", en: "airplane" },
        { cn: "飞鸟", py: "fēi niǎo", en: "flying bird" },
        { cn: "起飞", py: "qǐfēi", en: "take off" },
    ],
    "开": [
        { cn: "开心", py: "kāixīn", en: "happy" },
        { cn: "开门", py: "kāi mén", en: "open the door" },
        { cn: "开始", py: "kāishǐ", en: "begin" },
    ],
    "笑": [
        { cn: "笑话", py: "xiàohua", en: "joke" },
        { cn: "微笑", py: "wēixiào", en: "smile" },
        { cn: "大笑", py: "dà xiào", en: "laugh loudly" },
    ],
    "哭": [
        { cn: "哭了", py: "kū le", en: "cried" },
        { cn: "大哭", py: "dà kū", en: "cry loudly" },
        { cn: "别哭", py: "bié kū", en: "don't cry" },
    ],
    "高": [
        { cn: "很高", py: "hěn gāo", en: "very tall" },
        { cn: "高兴", py: "gāoxìng", en: "happy" },
        { cn: "高山", py: "gāo shān", en: "tall mountain" },
    ],
    "快": [
        { cn: "快乐", py: "kuàilè", en: "happy" },
        { cn: "很快", py: "hěn kuài", en: "very fast" },
        { cn: "快跑", py: "kuài pǎo", en: "run fast!" },
    ],
    "慢": [
        { cn: "慢慢", py: "mànmàn", en: "slowly" },
        { cn: "很慢", py: "hěn màn", en: "very slow" },
        { cn: "慢走", py: "màn zǒu", en: "take care (goodbye)" },
    ],
    "多": [
        { cn: "很多", py: "hěn duō", en: "very many" },
        { cn: "多少", py: "duōshao", en: "how many / how much" },
        { cn: "多大", py: "duō dà", en: "how old / how big" },
    ],
    "少": [
        { cn: "多少", py: "duōshao", en: "how many / how much" },
        { cn: "很少", py: "hěn shǎo", en: "very few" },
        { cn: "少年", py: "shàonián", en: "youth" },
    ],
};

export default phrases;
