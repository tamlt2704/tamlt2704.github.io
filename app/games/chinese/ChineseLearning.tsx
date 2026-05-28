"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import HanziWriter from "hanzi-writer";

interface Word {
  hanzi: string;
  pinyin: string;
  english: string;
}

const TOPICS: Record<string, { label: string; words: Word[] }> = {
  greetings: {
    label: "👋 Greetings",
    words: [
      { hanzi: "你好", pinyin: "nǐ hǎo", english: "hello" },
      { hanzi: "谢谢", pinyin: "xiè xie", english: "thank you" },
      { hanzi: "再见", pinyin: "zài jiàn", english: "goodbye" },
      { hanzi: "请", pinyin: "qǐng", english: "please" },
      { hanzi: "对不起", pinyin: "duì bu qǐ", english: "sorry" },
      { hanzi: "没关系", pinyin: "méi guān xi", english: "no problem" },
      { hanzi: "早上好", pinyin: "zǎo shang hǎo", english: "good morning" },
      { hanzi: "晚安", pinyin: "wǎn ān", english: "good night" },
    ],
  },
  numbers: {
    label: "🔢 Numbers",
    words: [
      { hanzi: "一", pinyin: "yī", english: "one" },
      { hanzi: "二", pinyin: "èr", english: "two" },
      { hanzi: "三", pinyin: "sān", english: "three" },
      { hanzi: "四", pinyin: "sì", english: "four" },
      { hanzi: "五", pinyin: "wǔ", english: "five" },
      { hanzi: "六", pinyin: "liù", english: "six" },
      { hanzi: "七", pinyin: "qī", english: "seven" },
      { hanzi: "八", pinyin: "bā", english: "eight" },
      { hanzi: "九", pinyin: "jiǔ", english: "nine" },
      { hanzi: "十", pinyin: "shí", english: "ten" },
    ],
  },
  family: {
    label: "👨‍👩‍👧 Family",
    words: [
      { hanzi: "爸爸", pinyin: "bà ba", english: "father" },
      { hanzi: "妈妈", pinyin: "mā ma", english: "mother" },
      { hanzi: "哥哥", pinyin: "gē ge", english: "older brother" },
      { hanzi: "姐姐", pinyin: "jiě jie", english: "older sister" },
      { hanzi: "弟弟", pinyin: "dì di", english: "younger brother" },
      { hanzi: "妹妹", pinyin: "mèi mei", english: "younger sister" },
      { hanzi: "儿子", pinyin: "ér zi", english: "son" },
      { hanzi: "女儿", pinyin: "nǚ ér", english: "daughter" },
    ],
  },
  food: {
    label: "🍜 Food",
    words: [
      { hanzi: "米饭", pinyin: "mǐ fàn", english: "rice" },
      { hanzi: "面条", pinyin: "miàn tiáo", english: "noodles" },
      { hanzi: "水", pinyin: "shuǐ", english: "water" },
      { hanzi: "茶", pinyin: "chá", english: "tea" },
      { hanzi: "鸡蛋", pinyin: "jī dàn", english: "egg" },
      { hanzi: "鱼", pinyin: "yú", english: "fish" },
      { hanzi: "肉", pinyin: "ròu", english: "meat" },
      { hanzi: "菜", pinyin: "cài", english: "vegetable" },
    ],
  },
  colors: {
    label: "🎨 Colors",
    words: [
      { hanzi: "红", pinyin: "hóng", english: "red" },
      { hanzi: "蓝", pinyin: "lán", english: "blue" },
      { hanzi: "绿", pinyin: "lǜ", english: "green" },
      { hanzi: "黄", pinyin: "huáng", english: "yellow" },
      { hanzi: "白", pinyin: "bái", english: "white" },
      { hanzi: "黑", pinyin: "hēi", english: "black" },
      { hanzi: "紫", pinyin: "zǐ", english: "purple" },
      { hanzi: "橙", pinyin: "chéng", english: "orange" },
    ],
  },
  animals: {
    label: "🐾 Animals",
    words: [
      { hanzi: "猫", pinyin: "māo", english: "cat" },
      { hanzi: "狗", pinyin: "gǒu", english: "dog" },
      { hanzi: "鸟", pinyin: "niǎo", english: "bird" },
      { hanzi: "鱼", pinyin: "yú", english: "fish" },
      { hanzi: "马", pinyin: "mǎ", english: "horse" },
      { hanzi: "牛", pinyin: "niú", english: "cow" },
      { hanzi: "羊", pinyin: "yáng", english: "sheep" },
      { hanzi: "龙", pinyin: "lóng", english: "dragon" },
    ],
  },
  body: {
    label: "🧍 Body",
    words: [
      { hanzi: "头", pinyin: "tóu", english: "head" },
      { hanzi: "手", pinyin: "shǒu", english: "hand" },
      { hanzi: "脚", pinyin: "jiǎo", english: "foot" },
      { hanzi: "眼睛", pinyin: "yǎn jing", english: "eye" },
      { hanzi: "耳朵", pinyin: "ěr duo", english: "ear" },
      { hanzi: "嘴", pinyin: "zuǐ", english: "mouth" },
      { hanzi: "鼻子", pinyin: "bí zi", english: "nose" },
      { hanzi: "心", pinyin: "xīn", english: "heart" },
    ],
  },
  time: {
    label: "🕐 Time",
    words: [
      { hanzi: "今天", pinyin: "jīn tiān", english: "today" },
      { hanzi: "明天", pinyin: "míng tiān", english: "tomorrow" },
      { hanzi: "昨天", pinyin: "zuó tiān", english: "yesterday" },
      { hanzi: "年", pinyin: "nián", english: "year" },
      { hanzi: "月", pinyin: "yuè", english: "month" },
      { hanzi: "日", pinyin: "rì", english: "day" },
      { hanzi: "星期", pinyin: "xīng qī", english: "week" },
      { hanzi: "小时", pinyin: "xiǎo shí", english: "hour" },
    ],
  },
  nature: {
    label: "🌿 Nature",
    words: [
      { hanzi: "天", pinyin: "tiān", english: "sky" },
      { hanzi: "地", pinyin: "dì", english: "earth" },
      { hanzi: "山", pinyin: "shān", english: "mountain" },
      { hanzi: "河", pinyin: "hé", english: "river" },
      { hanzi: "火", pinyin: "huǒ", english: "fire" },
      { hanzi: "风", pinyin: "fēng", english: "wind" },
      { hanzi: "雨", pinyin: "yǔ", english: "rain" },
      { hanzi: "花", pinyin: "huā", english: "flower" },
      { hanzi: "树", pinyin: "shù", english: "tree" },
      { hanzi: "太阳", pinyin: "tài yáng", english: "sun" },
      { hanzi: "月亮", pinyin: "yuè liang", english: "moon" },
      { hanzi: "星星", pinyin: "xīng xing", english: "star" },
    ],
  },
  places: {
    label: "🏠 Places",
    words: [
      { hanzi: "家", pinyin: "jiā", english: "home" },
      { hanzi: "学校", pinyin: "xué xiào", english: "school" },
      { hanzi: "医院", pinyin: "yī yuàn", english: "hospital" },
      { hanzi: "商店", pinyin: "shāng diàn", english: "shop" },
      { hanzi: "饭店", pinyin: "fàn diàn", english: "restaurant" },
      { hanzi: "银行", pinyin: "yín háng", english: "bank" },
      { hanzi: "机场", pinyin: "jī chǎng", english: "airport" },
      { hanzi: "公园", pinyin: "gōng yuán", english: "park" },
    ],
  },
  verbs: {
    label: "🏃 Actions",
    words: [
      { hanzi: "吃", pinyin: "chī", english: "eat" },
      { hanzi: "喝", pinyin: "hē", english: "drink" },
      { hanzi: "看", pinyin: "kàn", english: "look/watch" },
      { hanzi: "听", pinyin: "tīng", english: "listen" },
      { hanzi: "说", pinyin: "shuō", english: "speak" },
      { hanzi: "写", pinyin: "xiě", english: "write" },
      { hanzi: "读", pinyin: "dú", english: "read" },
      { hanzi: "走", pinyin: "zǒu", english: "walk" },
      { hanzi: "跑", pinyin: "pǎo", english: "run" },
      { hanzi: "买", pinyin: "mǎi", english: "buy" },
      { hanzi: "卖", pinyin: "mài", english: "sell" },
      { hanzi: "学", pinyin: "xué", english: "study" },
    ],
  },
  adjectives: {
    label: "✨ Adjectives",
    words: [
      { hanzi: "大", pinyin: "dà", english: "big" },
      { hanzi: "小", pinyin: "xiǎo", english: "small" },
      { hanzi: "好", pinyin: "hǎo", english: "good" },
      { hanzi: "多", pinyin: "duō", english: "many" },
      { hanzi: "少", pinyin: "shǎo", english: "few" },
      { hanzi: "快", pinyin: "kuài", english: "fast" },
      { hanzi: "慢", pinyin: "màn", english: "slow" },
      { hanzi: "新", pinyin: "xīn", english: "new" },
      { hanzi: "热", pinyin: "rè", english: "hot" },
      { hanzi: "冷", pinyin: "lěng", english: "cold" },
      { hanzi: "长", pinyin: "cháng", english: "long" },
      { hanzi: "短", pinyin: "duǎn", english: "short" },
    ],
  },
  travel: {
    label: "✈️ Travel",
    words: [
      { hanzi: "车", pinyin: "chē", english: "car" },
      { hanzi: "飞机", pinyin: "fēi jī", english: "airplane" },
      { hanzi: "火车", pinyin: "huǒ chē", english: "train" },
      { hanzi: "地铁", pinyin: "dì tiě", english: "subway" },
      { hanzi: "出租车", pinyin: "chū zū chē", english: "taxi" },
      { hanzi: "地图", pinyin: "dì tú", english: "map" },
      { hanzi: "护照", pinyin: "hù zhào", english: "passport" },
      { hanzi: "酒店", pinyin: "jiǔ diàn", english: "hotel" },
    ],
  },
  weather: {
    label: "🌤️ Weather",
    words: [
      { hanzi: "晴天", pinyin: "qíng tiān", english: "sunny" },
      { hanzi: "下雨", pinyin: "xià yǔ", english: "rainy" },
      { hanzi: "下雪", pinyin: "xià xuě", english: "snowy" },
      { hanzi: "多云", pinyin: "duō yún", english: "cloudy" },
      { hanzi: "冷", pinyin: "lěng", english: "cold" },
      { hanzi: "热", pinyin: "rè", english: "hot" },
      { hanzi: "风", pinyin: "fēng", english: "windy" },
      { hanzi: "温度", pinyin: "wēn dù", english: "temperature" },
    ],
  },
  emotions: {
    label: "😊 Emotions",
    words: [
      { hanzi: "高兴", pinyin: "gāo xìng", english: "happy" },
      { hanzi: "难过", pinyin: "nán guò", english: "sad" },
      { hanzi: "生气", pinyin: "shēng qì", english: "angry" },
      { hanzi: "害怕", pinyin: "hài pà", english: "afraid" },
      { hanzi: "累", pinyin: "lèi", english: "tired" },
      { hanzi: "饿", pinyin: "è", english: "hungry" },
      { hanzi: "渴", pinyin: "kě", english: "thirsty" },
      { hanzi: "爱", pinyin: "ài", english: "love" },
    ],
  },
  clothing: {
    label: "👕 Clothing",
    words: [
      { hanzi: "衣服", pinyin: "yī fu", english: "clothes" },
      { hanzi: "裤子", pinyin: "kù zi", english: "pants" },
      { hanzi: "鞋子", pinyin: "xié zi", english: "shoes" },
      { hanzi: "帽子", pinyin: "mào zi", english: "hat" },
      { hanzi: "裙子", pinyin: "qún zi", english: "skirt" },
      { hanzi: "外套", pinyin: "wài tào", english: "coat" },
      { hanzi: "袜子", pinyin: "wà zi", english: "socks" },
      { hanzi: "眼镜", pinyin: "yǎn jìng", english: "glasses" },
    ],
  },
  school: {
    label: "📚 School",
    words: [
      { hanzi: "书", pinyin: "shū", english: "book" },
      { hanzi: "笔", pinyin: "bǐ", english: "pen" },
      { hanzi: "老师", pinyin: "lǎo shī", english: "teacher" },
      { hanzi: "学生", pinyin: "xué shēng", english: "student" },
      { hanzi: "考试", pinyin: "kǎo shì", english: "exam" },
      { hanzi: "作业", pinyin: "zuò yè", english: "homework" },
      { hanzi: "教室", pinyin: "jiào shì", english: "classroom" },
      { hanzi: "问题", pinyin: "wèn tí", english: "question" },
    ],
  },
  conv_greeting: {
    label: "💬 Meeting People",
    words: [
      { hanzi: "你好吗", pinyin: "nǐ hǎo ma", english: "How are you?" },
      { hanzi: "我很好", pinyin: "wǒ hěn hǎo", english: "I'm fine" },
      { hanzi: "你叫什么名字", pinyin: "nǐ jiào shén me míng zi", english: "What's your name?" },
      { hanzi: "我叫", pinyin: "wǒ jiào", english: "My name is..." },
      { hanzi: "认识你很高兴", pinyin: "rèn shi nǐ hěn gāo xìng", english: "Nice to meet you" },
      { hanzi: "你是哪国人", pinyin: "nǐ shì nǎ guó rén", english: "Where are you from?" },
      { hanzi: "你多大了", pinyin: "nǐ duō dà le", english: "How old are you?" },
      { hanzi: "你做什么工作", pinyin: "nǐ zuò shén me gōng zuò", english: "What do you do?" },
    ],
  },
  conv_directions: {
    label: "🧭 Directions",
    words: [
      { hanzi: "请问", pinyin: "qǐng wèn", english: "Excuse me (asking)" },
      { hanzi: "在哪里", pinyin: "zài nǎ lǐ", english: "Where is...?" },
      { hanzi: "怎么走", pinyin: "zěn me zǒu", english: "How to get there?" },
      { hanzi: "左转", pinyin: "zuǒ zhuǎn", english: "turn left" },
      { hanzi: "右转", pinyin: "yòu zhuǎn", english: "turn right" },
      { hanzi: "一直走", pinyin: "yì zhí zǒu", english: "go straight" },
      { hanzi: "远", pinyin: "yuǎn", english: "far" },
      { hanzi: "近", pinyin: "jìn", english: "near" },
      { hanzi: "前面", pinyin: "qián miàn", english: "in front" },
      { hanzi: "后面", pinyin: "hòu miàn", english: "behind" },
      { hanzi: "旁边", pinyin: "páng biān", english: "next to" },
      { hanzi: "对面", pinyin: "duì miàn", english: "opposite" },
    ],
  },
  conv_market: {
    label: "🛒 At the Market",
    words: [
      { hanzi: "多少钱", pinyin: "duō shao qián", english: "How much?" },
      { hanzi: "太贵了", pinyin: "tài guì le", english: "Too expensive" },
      { hanzi: "便宜一点", pinyin: "pián yi yì diǎn", english: "A bit cheaper" },
      { hanzi: "我要这个", pinyin: "wǒ yào zhè ge", english: "I want this one" },
      { hanzi: "可以试试吗", pinyin: "kě yǐ shì shi ma", english: "Can I try?" },
      { hanzi: "有没有", pinyin: "yǒu méi yǒu", english: "Do you have...?" },
      { hanzi: "买单", pinyin: "mǎi dān", english: "Pay the bill" },
      { hanzi: "找钱", pinyin: "zhǎo qián", english: "Give change" },
      { hanzi: "一斤", pinyin: "yì jīn", english: "one jin (500g)" },
      { hanzi: "打折", pinyin: "dǎ zhé", english: "discount" },
    ],
  },
  conv_restaurant: {
    label: "🍽️ At Restaurant",
    words: [
      { hanzi: "菜单", pinyin: "cài dān", english: "menu" },
      { hanzi: "点菜", pinyin: "diǎn cài", english: "order food" },
      { hanzi: "服务员", pinyin: "fú wù yuán", english: "waiter" },
      { hanzi: "我要一个", pinyin: "wǒ yào yí gè", english: "I'd like one..." },
      { hanzi: "不要辣", pinyin: "bú yào là", english: "no spicy" },
      { hanzi: "好吃", pinyin: "hǎo chī", english: "delicious" },
      { hanzi: "吃饱了", pinyin: "chī bǎo le", english: "I'm full" },
      { hanzi: "打包", pinyin: "dǎ bāo", english: "take away" },
    ],
  },
  conv_transport: {
    label: "🚌 Taking Transport",
    words: [
      { hanzi: "去哪里", pinyin: "qù nǎ lǐ", english: "Where to?" },
      { hanzi: "到了吗", pinyin: "dào le ma", english: "Are we there?" },
      { hanzi: "下一站", pinyin: "xià yí zhàn", english: "next stop" },
      { hanzi: "我要下车", pinyin: "wǒ yào xià chē", english: "I want to get off" },
      { hanzi: "几路车", pinyin: "jǐ lù chē", english: "Which bus number?" },
      { hanzi: "坐地铁", pinyin: "zuò dì tiě", english: "take the subway" },
      { hanzi: "换乘", pinyin: "huàn chéng", english: "transfer" },
      { hanzi: "票", pinyin: "piào", english: "ticket" },
    ],
  },
  conv_hotel: {
    label: "🏨 At Hotel",
    words: [
      { hanzi: "订房间", pinyin: "dìng fáng jiān", english: "book a room" },
      { hanzi: "住几天", pinyin: "zhù jǐ tiān", english: "stay how many days?" },
      { hanzi: "退房", pinyin: "tuì fáng", english: "check out" },
      { hanzi: "钥匙", pinyin: "yào shi", english: "key" },
      { hanzi: "空调", pinyin: "kōng tiáo", english: "air conditioning" },
      { hanzi: "热水", pinyin: "rè shuǐ", english: "hot water" },
      { hanzi: "无线网", pinyin: "wú xiàn wǎng", english: "WiFi" },
      { hanzi: "早餐", pinyin: "zǎo cān", english: "breakfast" },
    ],
  },
};

type Mode = "learn" | "quiz" | "write" | "worksheet";

export default function ChineseLearning() {
  const [topic, setTopic] = useState("greetings");
  const [index, setIndex] = useState(0);
  const [mode, setMode] = useState<Mode>("learn");
  const [showAnswer, setShowAnswer] = useState(false);
  const [charIndex, setCharIndex] = useState(0);
  const writerRef = useRef<HTMLDivElement>(null);
  const writerInstance = useRef<HanziWriter | null>(null);

  const words = TOPICS[topic].words;
  const word = words[index];
  const currentChar = word.hanzi[charIndex];

  const next = () => {
    setIndex((i) => (i + 1) % words.length);
    setShowAnswer(false);
    setCharIndex(0);
  };
  const prev = () => {
    setIndex((i) => (i - 1 + words.length) % words.length);
    setShowAnswer(false);
    setCharIndex(0);
  };

  const initWriter = useCallback(() => {
    if (!writerRef.current || !currentChar) return;
    writerRef.current.innerHTML = "";
    writerInstance.current = HanziWriter.create(writerRef.current, currentChar, {
      width: 200,
      height: 200,
      padding: 10,
      showOutline: true,
      strokeAnimationSpeed: 1,
      delayBetweenStrokes: 200,
      showCharacter: false,
      showHintAfterMisses: 3,
      highlightOnComplete: true,
      drawingWidth: 20,
    });
    writerInstance.current.quiz();
  }, [currentChar]);

  useEffect(() => {
    if (mode === "write") initWriter();
    return () => {
      writerInstance.current = null;
    };
  }, [mode, initWriter]);

  const animateStroke = () => {
    if (!writerRef.current || !currentChar) return;
    writerRef.current.innerHTML = "";
    const w = HanziWriter.create(writerRef.current, currentChar, {
      width: 200,
      height: 200,
      padding: 10,
      strokeAnimationSpeed: 1,
      delayBetweenStrokes: 300,
    });
    w.animateCharacter();
  };

  const nextChar = () => {
    if (charIndex < word.hanzi.length - 1) setCharIndex((c) => c + 1);
  };
  const prevChar = () => {
    if (charIndex > 0) setCharIndex((c) => c - 1);
  };

  return (
    <div className="flex flex-col items-center gap-6 p-6">
      <h1 className="text-2xl font-bold">学中文 — Learn Chinese</h1>

      {/* Topic selector */}
      <div className="flex flex-wrap justify-center gap-2">
        {Object.entries(TOPICS).map(([key, { label }]) => (
          <button
            key={key}
            onClick={() => {
              setTopic(key);
              setIndex(0);
              setCharIndex(0);
              setShowAnswer(false);
            }}
            className={`rounded-full px-4 py-1.5 text-sm transition ${
              topic === key
                ? "bg-teal-600 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Mode tabs */}
      <div className="flex gap-1 rounded-lg bg-gray-100 p-1">
        {(
          [
            ["learn", "📖 Learn"],
            ["quiz", "❓ Quiz"],
            ["write", "✍️ Write"],
            ["worksheet", "📝 Worksheet"],
          ] as [Mode, string][]
        ).map(([m, label]) => (
          <button
            key={m}
            onClick={() => {
              setMode(m);
              setShowAnswer(false);
            }}
            className={`rounded-md px-4 py-2 text-sm font-medium transition ${
              mode === m ? "bg-white shadow" : "hover:bg-gray-200"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Card */}
      <div className="flex min-h-[280px] w-full max-w-md flex-col items-center justify-center rounded-xl border-2 border-gray-200 bg-white p-8 shadow-sm">
        {mode === "learn" && (
          <>
            <p className="text-6xl">{word.hanzi}</p>
            <p className="mt-4 text-xl text-gray-600">{word.pinyin}</p>
            <p className="mt-2 text-lg text-gray-500">{word.english}</p>
            <p className="mt-4 text-sm text-gray-400">
              {index + 1} / {words.length}
            </p>
          </>
        )}

        {mode === "quiz" && (
          <>
            <p className="text-6xl">{word.hanzi}</p>
            {showAnswer ? (
              <>
                <p className="mt-4 text-xl text-teal-600">{word.pinyin}</p>
                <p className="mt-2 text-lg text-gray-500">{word.english}</p>
              </>
            ) : (
              <button
                onClick={() => setShowAnswer(true)}
                className="mt-6 rounded bg-teal-600 px-4 py-2 text-white hover:bg-teal-700"
              >
                Show Answer
              </button>
            )}
            <p className="mt-4 text-sm text-gray-400">
              {index + 1} / {words.length}
            </p>
          </>
        )}

        {mode === "write" && (
          <>
            <p className="mb-2 text-sm text-gray-500">
              Write: <span className="text-lg font-bold">{currentChar}</span>
              <span className="ml-2 text-gray-400">
                ({word.pinyin} — {word.english})
              </span>
            </p>
            {word.hanzi.length > 1 && (
              <div className="mb-2 flex gap-2">
                {word.hanzi.split("").map((ch, i) => (
                  <span
                    key={i}
                    className={`cursor-pointer rounded px-2 py-1 text-2xl ${
                      i === charIndex ? "bg-teal-100 font-bold text-teal-700" : "text-gray-400"
                    }`}
                    onClick={() => setCharIndex(i)}
                  >
                    {ch}
                  </span>
                ))}
              </div>
            )}
            <div ref={writerRef} className="rounded-lg border bg-gray-50" />
            <div className="mt-3 flex gap-2">
              <button
                onClick={animateStroke}
                className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700"
              >
                Show Stroke Order
              </button>
              <button
                onClick={initWriter}
                className="rounded bg-gray-600 px-3 py-1 text-sm text-white hover:bg-gray-700"
              >
                Retry
              </button>
              {word.hanzi.length > 1 && (
                <>
                  <button
                    onClick={prevChar}
                    disabled={charIndex === 0}
                    className="rounded bg-gray-300 px-3 py-1 text-sm disabled:opacity-40"
                  >
                    ← Prev
                  </button>
                  <button
                    onClick={nextChar}
                    disabled={charIndex === word.hanzi.length - 1}
                    className="rounded bg-gray-300 px-3 py-1 text-sm disabled:opacity-40"
                  >
                    Next →
                  </button>
                </>
              )}
            </div>
          </>
        )}

        {mode === "worksheet" && <p className="text-sm text-gray-500">See worksheet below ↓</p>}
      </div>

      {/* Worksheet */}
      {mode === "worksheet" && (
        <>
          <button
            onClick={() => window.print()}
            className="no-print rounded bg-purple-600 px-4 py-2 text-white hover:bg-purple-700"
          >
            🖨️ Print Worksheet
          </button>
          <div id="print-worksheet" className="w-full max-w-4xl">
            <h2 className="no-print mb-4 text-center text-xl font-bold">
              {TOPICS[topic].label} — Stroke Order Worksheet
            </h2>
            <div className="space-y-6">
              {words.map((w, wi) => (
                <div key={wi} className="rounded-lg border p-4">
                  <div className="mb-2 flex items-baseline gap-3">
                    <span className="text-2xl font-bold">{w.hanzi}</span>
                    <span className="text-gray-600">{w.pinyin}</span>
                    <span className="text-gray-400">— {w.english}</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {w.hanzi.split("").map((ch, ci) => (
                      <WorksheetChar key={`${wi}-${ci}`} char={ch} />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Navigation */}
      {mode !== "worksheet" && (
        <div className="flex gap-4">
          <button onClick={prev} className="rounded bg-gray-200 px-4 py-2 hover:bg-gray-300">
            ← Previous
          </button>
          <button onClick={next} className="rounded bg-gray-200 px-4 py-2 hover:bg-gray-300">
            Next →
          </button>
        </div>
      )}

      <style>{`
        @media print {
          body * { visibility: hidden; }
          #print-worksheet, #print-worksheet * { visibility: visible; }
          #print-worksheet { position: absolute; top: 0; left: 0; width: 100%; padding: 10mm; }
          .no-print { display: none !important; }
        }
      `}</style>
    </div>
  );
}

function WorksheetChar({ char }: { char: string }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    containerRef.current.innerHTML = "";

    HanziWriter.loadCharacterData(char).then((data) => {
      if (!containerRef.current || !data) return;
      const numStrokes = data.strokes.length;

      // Create progressive stroke boxes: stroke 1, strokes 1-2, strokes 1-3, etc.
      for (let i = 0; i <= numStrokes; i++) {
        const div = document.createElement("div");
        div.className = "inline-block border rounded bg-white m-0.5";
        containerRef.current.appendChild(div);

        const writer = HanziWriter.create(div, char, {
          width: 56,
          height: 56,
          padding: 3,
          showOutline: true,
          strokeColor: "#333",
          outlineColor: "#e2e8f0",
          showCharacter: false,
        });

        // Reveal strokes one by one up to i
        if (i > 0) {
          // Use animateStroke sequentially with 0 duration to show them instantly
          let chain = Promise.resolve();
          for (let s = 0; s < i; s++) {
            const strokeIdx = s;
            chain = chain.then(() => {
              return new Promise<void>((resolve) => {
                writer.animateStroke(strokeIdx, {
                  onComplete: () => resolve(),
                });
              });
            });
          }
        }
      }

      // Add empty practice boxes
      for (let i = 0; i < 4; i++) {
        const div = document.createElement("div");
        div.className =
          "inline-flex items-center justify-center border border-dashed border-gray-300 rounded bg-gray-50 m-0.5 text-gray-300 text-lg";
        div.style.width = "56px";
        div.style.height = "56px";
        div.textContent = i === 0 ? char : "";
        containerRef.current.appendChild(div);
      }
    });
  }, [char]);

  return (
    <div className="flex flex-col">
      <div ref={containerRef} className="flex flex-wrap items-center" />
    </div>
  );
}
