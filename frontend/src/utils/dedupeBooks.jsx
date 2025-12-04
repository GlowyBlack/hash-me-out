export function normalizeText(s) {
  if (!s) return "";
  return s
    .toLowerCase()
    .replace(/\./g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function normalizeTitleForWork(title) {
  if (!title) return "";

  return title
    .toLowerCase()
    .split(":", 1)[0]           
    .replace(/\(.*?\)/g, "")      
    .replace(/\s+/g, " ")
    .trim();
}

// Detect if book is series
const SERIES_PATTERNS = [
  /\bbook\s+\d+\b/,
  /\bbook\s+(one|two|three|four|five|six|seven|eight|nine|ten)\b/,
  /\bvolume\s+\d+\b/,
  /\bvol\.\s*\d+\b/,
  /\bpart\s+\d+\b/,
  /#\d+/,
  /\b(series|saga|chronicles)\b/,
];

export function isSeriesTitle(title) {
  if (!title) return false;
  const t = title.toLowerCase();
  return SERIES_PATTERNS.some((p) => p.test(t));
}

// Determine if two books are same work (NOT series)
export function isSameWork(a, b) {
  const t1 = normalizeTitleForWork(a.book_title);
  const t2 = normalizeTitleForWork(b.book_title);
  if (t1 !== t2) return false;

  if (isSeriesTitle(a.book_title) || isSeriesTitle(b.book_title)) return false;

  const a1 = normalizeText(a.author);
  const a2 = normalizeText(b.author);
  if (!a1 || !a2) return false;

  // last name match
  const ln1 = a1.split(" ").slice(-1)[0];
  const ln2 = a2.split(" ").slice(-1)[0];
  if (ln1 !== ln2) return false;

  // first initial match
  if (a1[0] !== a2[0]) return false;

  return true;
}

// Remove duplicates before showing
export function dedupeBooks(list) {
  const result = [];
  for (const book of list) {
    const exists = result.some((b) => isSameWork(b, book));
    if (!exists) result.push(book);
  }
  return result;
}
