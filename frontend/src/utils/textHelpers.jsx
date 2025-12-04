export function toTitleCase(str) {
  if (!str) return "";

  const smallWords = new Set([
    "and", "or", "the", "a", "an", "but", "nor",
    "at", "by", "for", "from", "in", "into",
    "on", "onto", "with", "up", "of", "to"
  ]);

  const words = str.toLowerCase().split(" ");

  return words
    .map((word, index) => {
      // Always capitalize the first & last word
      if (index === 0 || index === words.length - 1) {
        return word.charAt(0).toUpperCase() + word.slice(1);
      }

      // Keep small words lowercase
      if (smallWords.has(word)) {
        return word;
      }

      // Capitalize regular words
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join(" ");
}
