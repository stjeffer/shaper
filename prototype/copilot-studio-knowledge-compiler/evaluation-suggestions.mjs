export const EVALUATION_QUESTION_TARGET = 20;

const MAX_PASSAGE_CHARACTERS = 1000;
const MIN_PASSAGE_CHARACTERS = 20;

function sentencePassages(content) {
  const passages = [];
  content
    .split(/\n+/)
    .map((line) => line.replace(/^\s*(?:[-*+]|\d+[.)])\s+/, "").trim())
    .filter(Boolean)
    .forEach((line) => {
      const sentences = line.match(/[^.!?]+[.!?]+|[^.!?]+$/g) ?? [line];
      let pending = "";
      sentences.forEach((sentence) => {
        const value = sentence.trim();
        if (!value) return;
        pending = `${pending} ${value}`.trim();
        if (pending.length >= MIN_PASSAGE_CHARACTERS) {
          passages.push(pending.slice(0, MAX_PASSAGE_CHARACTERS));
          pending = "";
        }
      });
      if (pending) {
        if (
          passages.length &&
          passages.at(-1).length + pending.length + 1 <= MAX_PASSAGE_CHARACTERS
        ) {
          passages[passages.length - 1] = `${passages.at(-1)} ${pending}`;
        }
      }
    });
  return passages;
}

export function evaluationPassages(sourceText) {
  const passages = [];
  let heading = "";
  sourceText
    .split(/\n\s*\n/)
    .map((part) => part.trim())
    .filter(Boolean)
    .forEach((part) => {
      const headingMatch = part.match(/^#{1,6}\s+([^\n]+)(?:\n+([\s\S]+))?$/);
      let content = part;
      if (headingMatch) {
        heading = headingMatch[1].trim();
        content = (headingMatch[2] ?? "").trim();
        if (!content) return;
      }
      sentencePassages(content).forEach((text) => passages.push({ heading, text }));
    });
  const seen = new Set();
  return passages.filter((passage) => {
    const key = `${passage.heading}\n${passage.text}`.toLocaleLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export function evaluationKeywords(passage) {
  const excluded = new Set([
    "about",
    "after",
    "before",
    "from",
    "have",
    "must",
    "shall",
    "that",
    "their",
    "there",
    "these",
    "this",
    "with",
  ]);
  return [...new Set(passage.toLocaleLowerCase().match(/[a-z][a-z-]{3,}/g) ?? [])]
    .filter((word) => !excluded.has(word))
    .slice(0, 5);
}

function evaluationQuestion(documentTitle, passage) {
  const keywords = evaluationKeywords(passage.text);
  const fallback = passage.text.split(/\s+/).slice(0, 7).join(" ");
  const detail = keywords.slice(0, 3).join(", ") || fallback;
  const topic = passage.heading ? `${passage.heading}: ${detail}` : detail;
  return `What does ${documentTitle} say about ${topic}?`;
}

function evenlySelect(items, limit) {
  if (items.length <= limit) return items;
  return Array.from({ length: limit }, (_, index) => items[Math.floor((index * items.length) / limit)]);
}

export function suggestedEvaluations(proposal, documentValue, sourceText) {
  const seenQuestions = new Set();
  const candidates = evaluationPassages(sourceText)
    .map((passage) => ({
      passage,
      query: evaluationQuestion(documentValue.title, passage),
    }))
    .filter(({ query }) => {
      const key = query.toLocaleLowerCase();
      if (seenQuestions.has(key)) return false;
      seenQuestions.add(key);
      return true;
    });
  return evenlySelect(candidates, EVALUATION_QUESTION_TARGET).map(({ passage, query }, index) => ({
    id: `${proposal.recommendation_id}-evaluation-${index + 1}`,
    document_id: documentValue.document_id,
    source_version: documentValue.source_version,
    source_reference: `${documentValue.document_id}@${documentValue.source_version}`,
    query,
    ground_truth: passage.text,
    context: passage.text,
    keywords: evaluationKeywords(`${passage.heading} ${passage.text}`),
    foundry_evaluators: ["groundedness", "relevance", "completeness"],
    copilot_studio_methods: ["General quality", "Compare meaning", "Keyword match"],
    needs_sme_review: true,
  }));
}

export function selectEstateEvaluations(suggestions, limit = EVALUATION_QUESTION_TARGET) {
  const byDocument = new Map();
  suggestions.forEach((suggestion) => {
    const documentSuggestions = byDocument.get(suggestion.document_id) ?? [];
    documentSuggestions.push(suggestion);
    byDocument.set(suggestion.document_id, documentSuggestions);
  });
  const selected = [];
  let offset = 0;
  while (selected.length < limit) {
    let added = false;
    byDocument.forEach((documentSuggestions) => {
      if (selected.length >= limit || offset >= documentSuggestions.length) return;
      selected.push(documentSuggestions[offset]);
      added = true;
    });
    if (!added) break;
    offset += 1;
  }
  return selected;
}
