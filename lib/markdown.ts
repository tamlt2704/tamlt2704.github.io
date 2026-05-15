import fs from "fs";
import path from "path";
import matter from "gray-matter";

const CONTENT_DIRS = ["acode", "bcode"];

export interface PostMeta {
    slug: string;
    title: string;
    series: string;
    chapter: number;
    prevSlug?: string;
    nextSlug?: string;
}

/**
 * Get all markdown files from acode/ and bcode/ directories.
 * Each folder is a series. Files are chapters ordered by filename.
 */
export function getAllSeries() {
    const series: { name: string; slug: string; chapters: number; dir: string }[] = [];

    for (const dir of CONTENT_DIRS) {
        const base = path.join(process.cwd(), dir);
        if (!fs.existsSync(base)) continue;

        const folders = fs.readdirSync(base, { withFileTypes: true })
            .filter((d) => d.isDirectory())
            .map((d) => d.name);

        for (const folder of folders) {
            const folderPath = path.join(base, folder);
            const files = fs.readdirSync(folderPath)
                .filter((f) => f.endsWith(".md") && f.startsWith("chapter-"));
            if (files.length > 0) {
                series.push({
                    name: folder,
                    slug: `${dir}/${folder}`,
                    chapters: files.length,
                    dir: folderPath,
                });
            }
        }
    }
    return series;
}

/**
 * Get a single markdown file's content and metadata.
 */
export function getChapter(seriesDir: string, filename: string) {
    const filePath = path.join(process.cwd(), seriesDir, filename);
    if (!fs.existsSync(filePath)) return null;

    const raw = fs.readFileSync(filePath, "utf-8");
    const { content, data } = matter(raw);
    return { content, meta: data };
}

/**
 * Get all chapters in a series folder, sorted by filename.
 */
export function getSeriesChapters(seriesDir: string) {
    const fullPath = path.join(process.cwd(), seriesDir);
    if (!fs.existsSync(fullPath)) return [];

    return fs.readdirSync(fullPath)
        .filter((f) => f.endsWith(".md") && f.startsWith("chapter-"))
        .sort();
}
