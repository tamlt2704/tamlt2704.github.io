import fs from "fs";
import path from "path";

const CONTENT_DIR = "content";

export function getAllSeries() {
  const base = path.join(process.cwd(), CONTENT_DIR);

  if (!fs.existsSync(base)) {
    return [];
  }

  return fs
    .readdirSync(base, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => ({
      name: d.name,
      slug: d.name,
      chapters: fs
        .readdirSync(path.join(base, d.name))
        .filter((f) => f.endsWith(".md"))
        .sort(),
    }));
}

export function getChapterContent(series: string, file: string) {
  const filePath = path.join(process.cwd(), CONTENT_DIR, series, file);
  if (!fs.existsSync(filePath)) return null;
  return fs.readFileSync(filePath, "utf-8"); // Read the entire file as text
}

/**
 * Get the list of chapter filenames in a series, sorted.
 * Used for prev/next navigation.
 */
export function getSeriesChapters(series: string) {
  const dir = path.join(process.cwd(), CONTENT_DIR, series);
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".md"))
    .sort();
}
