import assert from "node:assert/strict";
import test from "node:test";

import {
  EVALUATION_QUESTION_TARGET,
  selectEstateEvaluations,
  suggestedEvaluations,
} from "../prototype/copilot-studio-knowledge-compiler/evaluation-suggestions.mjs";

function documentValue(documentId) {
  return {
    document_id: documentId,
    source_version: `${documentId}-version`,
    title: `${documentId} policy`,
  };
}

function proposal(documentId) {
  return { recommendation_id: `${documentId}-recommendation` };
}

function sourceWithRules(count) {
  return Array.from(
    { length: count },
    (_, index) =>
      `## Rule ${index + 1}\n\nEmployees must complete requirement ${index + 1} before approval.`,
  ).join("\n\n");
}

test("generates up to 20 distinct grounded questions for one document", () => {
  const source = sourceWithRules(30);
  const suggestions = suggestedEvaluations(proposal("document-1"), documentValue("document-1"), source);

  assert.equal(suggestions.length, EVALUATION_QUESTION_TARGET);
  assert.equal(new Set(suggestions.map(({ query }) => query)).size, EVALUATION_QUESTION_TARGET);
  suggestions.forEach((suggestion) => {
    assert.ok(source.includes(suggestion.ground_truth));
    assert.equal(suggestion.ground_truth, suggestion.context);
  });
});

test("returns fewer questions rather than padding sparse knowledge", () => {
  const suggestions = suggestedEvaluations(
    proposal("document-1"),
    documentValue("document-1"),
    sourceWithRules(3),
  );

  assert.equal(suggestions.length, 3);
});

test("does not generate questions from non-substantive source fragments", () => {
  const suggestions = suggestedEvaluations(
    proposal("document-1"),
    documentValue("document-1"),
    "## Status\n\nActive.\n\n## Owner\n\nJane Smith.",
  );

  assert.deepEqual(suggestions, []);
});

test("balances a 20-question estate set across documents", () => {
  const first = suggestedEvaluations(
    proposal("document-1"),
    documentValue("document-1"),
    sourceWithRules(30),
  );
  const second = suggestedEvaluations(
    proposal("document-2"),
    documentValue("document-2"),
    sourceWithRules(30),
  );
  const selected = selectEstateEvaluations([...first, ...second]);

  assert.equal(selected.length, EVALUATION_QUESTION_TARGET);
  assert.equal(selected.filter(({ document_id }) => document_id === "document-1").length, 10);
  assert.equal(selected.filter(({ document_id }) => document_id === "document-2").length, 10);
});
