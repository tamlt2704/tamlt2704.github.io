# Chapter 21: Multi-Language Course Platform

[← Chapter 20: Monetization](/blog/nextjs-ghpages/chapter-20-monetization) | [Chapter 22: Gated Resources →](/blog/nextjs-ghpages/chapter-22-gated-resources)

---

## The Vision

You teach Python. Your readers speak English, French, Vietnamese, and Chinese. You don't want four separate sites. You want one platform where:

- Content exists in multiple languages
- Readers pick their language once
- The URL reflects the language (`/en/...`, `/fr/...`, `/vi/...`, `/zh/...`)
- Shared components (Quiz, Playground) work in any language
- You can add a language without changing code

## The Folder Structure

```
content/
  en/
    python-basics/
      chapter-00-overview.md
      chapter-01-variables.md
      chapter-02-functions.md
    react-fundamentals/
      chapter-00-overview.md
  fr/
    python-basics/
      chapter-00-apercu.md
      chapter-01-variables.md
      chapter-02-fonctions.md
  vi/
    python-basics/
      chapter-00-tong-quan.md
      chapter-01-bien.md
      chapter-02-ham.md
  zh/
    python-basics/
      chapter-00-概述.md
      chapter-01-变量.md
      chapter-02-函数.md
```

Each language is a top-level folder. Series and chapters mirror each other. Filenames can differ (localized slugs) or stay the same — your choice.

## The Route

Update `app/blog/[...slug]/page.tsx` to handle the language prefix:

```tsx
interface Props {
  params: Promise<{ slug: string[] }>;
}

export async function generateStaticParams() {
  const params: { slug: string[] }[] = [];
  const langs = ["en", "fr", "vi", "zh"];

  for (const lang of langs) {
    const base = path.join(process.cwd(), "content", lang);
    if (!fs.existsSync(base)) continue;

    const folders = fs.readdirSync(base, { withFileTypes: true }).filter((d) => d.isDirectory());

    for (const folder of folders) {
      const files = fs.readdirSync(path.join(base, folder.name)).filter((f) => f.endsWith(".md"));
      for (const file of files) {
        params.push({ slug: [lang, folder.name, file.replace(".md", "")] });
      }
    }
  }
  return params;
}

export default async function BlogPage({ params }: Props) {
  const { slug } = await params;
  if (slug.length < 3) return notFound();

  const [lang, series, fileSlug] = slug;
  const filePath = path.join(process.cwd(), "content", lang, series, `${fileSlug}.md`);

  if (!fs.existsSync(filePath)) return notFound();

  const raw = fs.readFileSync(filePath, "utf-8");
  const { content } = matter(raw);

  // Get chapters for this language + series
  const seriesDir = path.join(process.cwd(), "content", lang, series);
  const chapters = fs
    .readdirSync(seriesDir)
    .filter((f) => f.endsWith(".md"))
    .sort();

  return (
    <article className="mx-auto max-w-3xl px-6 py-12">
      <LangSwitcher currentLang={lang} slug={slug} />
      <div className="prose prose-lg dark:prose-invert mt-6 max-w-none">
        <MDXRemote
          source={content}
          components={getComponents(lang)}
          options={{ mdxOptions: { remarkPlugins: [remarkGfm], format: "md" } }}
        />
      </div>
      <ChapterNav lang={lang} series={series} chapters={chapters} current={fileSlug} />
    </article>
  );
}
```

URL structure: `/blog/en/python-basics/chapter-01-variables`

## The Language Switcher

```tsx
// app/blog/components/LangSwitcher.tsx
"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";

const LANGS = [
  { code: "en", label: "English", flag: "🇬🇧" },
  { code: "fr", label: "Français", flag: "🇫🇷" },
  { code: "vi", label: "Tiếng Việt", flag: "🇻🇳" },
  { code: "zh", label: "中文", flag: "🇨🇳" },
];

interface Props {
  currentLang: string;
  slug: string[];
}

export function LangSwitcher({ currentLang, slug }: Props) {
  // Build equivalent URL in other languages
  const [_, series, chapter] = slug;

  return (
    <div className="flex items-center gap-1">
      {LANGS.map(({ code, label, flag }) => {
        // Check if this chapter exists in the target language
        // (in a real app, pass available langs from server)
        const href = `/blog/${code}/${series}/${chapter}`;
        const isActive = code === currentLang;

        return (
          <Link
            key={code}
            href={href}
            className={`rounded px-2.5 py-1 text-sm transition ${
              isActive
                ? "bg-teal-100 font-medium text-teal-800 dark:bg-teal-900/40 dark:text-teal-200"
                : "text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
            }`}
            title={label}
          >
            {flag}
          </Link>
        );
      })}
    </div>
  );
}
```

## Localized UI Strings

The interactive components need translated labels. Create a simple i18n system:

```typescript
// lib/i18n.ts
const translations: Record<string, Record<string, string>> = {
  en: {
    "quiz.correct": "Correct!",
    "quiz.wrong": "Not quite. The answer is",
    "playground.run": "▶ Run",
    "playground.reset": "Reset",
    "progress.complete": "Mark as complete",
    "progress.completed": "Chapter completed",
    "comments.title": "Comments",
    "comments.placeholder": "Leave a comment...",
    "comments.login": "Login with GitHub to comment",
    "comments.post": "Post Comment",
    "nav.prev": "← Previous",
    "nav.next": "Next →",
    views: "views",
    "coffee.message": "Found this helpful?",
    "coffee.button": "Buy me a coffee",
  },
  fr: {
    "quiz.correct": "Correct !",
    "quiz.wrong": "Pas tout à fait. La réponse est",
    "playground.run": "▶ Exécuter",
    "playground.reset": "Réinitialiser",
    "progress.complete": "Marquer comme terminé",
    "progress.completed": "Chapitre terminé",
    "comments.title": "Commentaires",
    "comments.placeholder": "Laisser un commentaire...",
    "comments.login": "Connectez-vous avec GitHub pour commenter",
    "comments.post": "Publier",
    "nav.prev": "← Précédent",
    "nav.next": "Suivant →",
    views: "vues",
    "coffee.message": "Cela vous a aidé ?",
    "coffee.button": "Offrez-moi un café",
  },
  vi: {
    "quiz.correct": "Chính xác!",
    "quiz.wrong": "Chưa đúng. Đáp án là",
    "playground.run": "▶ Chạy",
    "playground.reset": "Đặt lại",
    "progress.complete": "Đánh dấu hoàn thành",
    "progress.completed": "Đã hoàn thành",
    "comments.title": "Bình luận",
    "comments.placeholder": "Để lại bình luận...",
    "comments.login": "Đăng nhập GitHub để bình luận",
    "comments.post": "Đăng",
    "nav.prev": "← Trước",
    "nav.next": "Tiếp →",
    views: "lượt xem",
    "coffee.message": "Bài viết hữu ích?",
    "coffee.button": "Mua cho tôi ly cà phê",
  },
  zh: {
    "quiz.correct": "正确！",
    "quiz.wrong": "不太对。答案是",
    "playground.run": "▶ 运行",
    "playground.reset": "重置",
    "progress.complete": "标记完成",
    "progress.completed": "已完成",
    "comments.title": "评论",
    "comments.placeholder": "留下评论...",
    "comments.login": "使用 GitHub 登录以评论",
    "comments.post": "发布",
    "nav.prev": "← 上一章",
    "nav.next": "下一章 →",
    views: "次浏览",
    "coffee.message": "觉得有帮助？",
    "coffee.button": "请我喝杯咖啡",
  },
};

export function t(lang: string, key: string): string {
  return translations[lang]?.[key] || translations["en"][key] || key;
}
```

## Using Translations in Components

Pass `lang` through React Context so all components can access it:

```tsx
// lib/LangContext.tsx
"use client";

import { createContext, useContext } from "react";
import { t as translate } from "@/lib/i18n";

const LangContext = createContext("en");

export function LangProvider({ lang, children }: { lang: string; children: React.ReactNode }) {
  return <LangContext.Provider value={lang}>{children}</LangContext.Provider>;
}

export function useLang() {
  return useContext(LangContext);
}

export function useT() {
  const lang = useLang();
  return (key: string) => translate(lang, key);
}
```

Wrap your blog page:

```tsx
<LangProvider lang={lang}>
  <article>...</article>
</LangProvider>
```

Now in any component:

```tsx
function Quiz({ question, options, answer }: QuizProps) {
  const t = useT();
  // ...
  {
    revealed && <p>{isCorrect ? t("quiz.correct") : `${t("quiz.wrong")} ${correctLetter}.`}</p>;
  }
}
```

## Language Detection & Persistence

Remember the reader's choice:

```tsx
// app/components/LangDetector.tsx
"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

export function LangDetector() {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    // If on root /blog, redirect to preferred language
    if (pathname === "/blog" || pathname === "/blog/") {
      const saved = localStorage.getItem("lang");
      const browser = navigator.language.slice(0, 2);
      const lang = saved || (["fr", "vi", "zh"].includes(browser) ? browser : "en");
      router.replace(`/blog/${lang}`);
    }
  }, [pathname, router]);

  // Save language choice when navigating
  useEffect(() => {
    const lang = pathname.split("/")[2];
    if (["en", "fr", "vi", "zh"].includes(lang)) {
      localStorage.setItem("lang", lang);
    }
  }, [pathname]);

  return null;
}
```

## The Course Index Page

`app/blog/[lang]/page.tsx` — shows all courses in the selected language:

```tsx
import Link from "next/link";
import fs from "fs";
import path from "path";

interface Props {
  params: Promise<{ lang: string }>;
}

export async function generateStaticParams() {
  return [{ lang: "en" }, { lang: "fr" }, { lang: "vi" }, { lang: "zh" }];
}

export default async function CourseIndex({ params }: Props) {
  const { lang } = await params;
  const base = path.join(process.cwd(), "content", lang);

  const courses = fs.existsSync(base)
    ? fs
        .readdirSync(base, { withFileTypes: true })
        .filter((d) => d.isDirectory())
        .map((d) => {
          const chapters = fs
            .readdirSync(path.join(base, d.name))
            .filter((f) => f.endsWith(".md")).length;
          return { name: d.name, chapters };
        })
    : [];

  const titles: Record<string, string> = {
    en: "Courses",
    fr: "Cours",
    vi: "Khóa học",
    zh: "课程",
  };

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="mb-8 text-3xl font-bold">{titles[lang]}</h1>
      <div className="grid gap-4">
        {courses.map((course) => (
          <Link
            key={course.name}
            href={`/blog/${lang}/${course.name}`}
            className="block rounded-lg border p-5 transition hover:border-teal-400"
          >
            <h2 className="text-lg font-semibold">
              {course.name.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
            </h2>
            <p className="mt-1 text-sm text-gray-500">{course.chapters} chapters</p>
          </Link>
        ))}
      </div>
    </main>
  );
}
```

## Writing Multi-Language Content

### Strategy 1: Write in English first, translate later

```
1. Write content/en/python-basics/chapter-01-variables.md
2. Translate to content/fr/python-basics/chapter-01-variables.md
3. Translate to content/vi/python-basics/chapter-01-bien.md
4. Translate to content/zh/python-basics/chapter-01-变量.md
```

### Strategy 2: Use AI to bootstrap translations

```bash
# Example with a translation script (you review and edit after)
# This is a starting point, not a final product
python translate.py content/en/python-basics/ --to fr vi zh
```

Always review AI translations — especially for technical terms. "Variable" in Vietnamese is "biến" (correct), but "closure" might get mistranslated.

### Strategy 3: Code blocks stay the same

Code is universal. Only translate the prose:

````markdown
<!-- English -->

A variable stores a value. You create one with `let`:

````python
name = "Ada"
age = 36
```⁠

<!-- Vietnamese -->
Biến lưu trữ một giá trị. Bạn tạo biến với `let`:

```python
name = "Ada"
age = 36
```⁠
````
````

The code block is identical. Only the explanation changes.

## CJK Typography

Chinese and Vietnamese need different font handling:

```css
/* globals.css */
:lang(zh) {
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
  line-height: 1.8; /* CJK needs more line height */
}

:lang(vi) {
  font-family: "Segoe UI", "Roboto", sans-serif;
  /* Vietnamese uses Latin script with diacritics — standard fonts work */
}
```

Set the `lang` attribute on `<html>`:

```tsx
<html lang={lang} suppressHydrationWarning>
```

## SEO for Multi-Language

Add `hreflang` tags so Google knows about translations:

```tsx
// In generateMetadata:
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const [lang, series, chapter] = slug;

  return {
    title: `${chapter} — ${series}`,
    alternates: {
      languages: {
        en: `/blog/en/${series}/${chapter}`,
        fr: `/blog/fr/${series}/${chapter}`,
        vi: `/blog/vi/${series}/${chapter}`,
        zh: `/blog/zh/${series}/${chapter}`,
      },
    },
  };
}
```

Google will show the right language version to each user.

## The Complete Architecture

```
content/
  {lang}/
    {course}/
      {chapter}.md
         ↓
/blog/{lang}/{course}/{chapter}
         ↓
LangProvider wraps the page
         ↓
Components use useT() for UI strings
         ↓
Code blocks are language-agnostic
         ↓
LangSwitcher lets readers switch
         ↓
localStorage remembers preference
```

## Scaling: Adding a New Language

To add Japanese:

1. Create `content/ja/` folder
2. Add translations of your courses
3. Add `{ code: "ja", label: "日本語", flag: "🇯🇵" }` to `LANGS`
4. Add Japanese strings to `lib/i18n.ts`
5. `git push`

No code changes to components. No new routes. The system discovers languages from the folder structure.

---

## The Full Series — Final Summary

20 chapters. From empty folder to a multi-language, interactive, monetized learning platform:

| Part                   | What You Built                                     |
| ---------------------- | -------------------------------------------------- |
| **Build** (0–7)        | Static blog with quizzes, playgrounds, visualizers |
| **Polish** (8–11)      | Dark mode, mobile, performance                     |
| **Understand** (12–15) | JavaScript, React, Hooks, TypeScript               |
| **Backend** (16–19)    | Supabase: views, auth, progress, comments          |
| **Scale** (20–21)      | Monetization + 4 languages                         |

**Cost:** $0/month (GitHub Pages + Supabase free tier)
**Languages:** English, French, Vietnamese, Chinese (extensible)
**Content format:** Plain markdown files
**Deploy:** `git push`

You're not just a blogger. You're running a course platform. Ship it.
