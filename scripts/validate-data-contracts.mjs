#!/usr/bin/env node

import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const ROOT = process.cwd();
const DATA_DIR = path.join(ROOT, "data");
const errors = [];
const warnings = [];
const docs = new Map();

function rel(p) {
  return path.relative(ROOT, p).replaceAll(path.sep, "/");
}

function taskOf(doc) {
  return doc?.task_id ?? doc?.task ?? "unscoped";
}

function issue(bucket, file, record, message) {
  bucket.push({ file, record: record || "-", task: taskOf(docs.get(file)), message });
}

function fail(file, record, message) {
  issue(errors, file, record, message);
}

function warn(file, record, message) {
  issue(warnings, file, record, message);
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function uniqueStrings(file, record, values, label) {
  const seen = new Set();
  for (const [i, value] of asArray(values).entries()) {
    if (typeof value !== "string" || !value.trim()) {
      fail(file, `${record}[${i}]`, `${label} must contain non-empty strings`);
      continue;
    }
    if (seen.has(value)) fail(file, `${record}[${i}]`, `duplicate ${label} value: ${value}`);
    seen.add(value);
  }
  return seen;
}

function parseTrailingInteger(value, prefix) {
  if (typeof value !== "string" || !value.startsWith(prefix)) return null;
  const n = Number(value.slice(prefix.length));
  return Number.isInteger(n) ? n : null;
}

function inRange(n, start, end) {
  return Number.isInteger(n) && n >= start && n <= end;
}

function normalizedAlias(value) {
  return String(value).normalize("NFKC").trim().toLocaleLowerCase("en").replace(/\s+/g, " ");
}

async function discoverJson(dir) {
  const out = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...await discoverJson(full));
    else if (entry.isFile() && entry.name.endsWith(".json")) out.push(full);
  }
  return out.sort();
}

async function loadAllJson() {
  let files;
  try {
    files = await discoverJson(DATA_DIR);
  } catch (error) {
    console.error(`ERROR data/: cannot enumerate JSON files: ${error.message}`);
    process.exit(1);
  }

  for (const full of files) {
    const file = rel(full);
    try {
      const text = await readFile(full, "utf8");
      docs.set(file, JSON.parse(text));
    } catch (error) {
      errors.push({ file, record: "-", task: "parse", message: `invalid JSON: ${error.message}` });
    }
  }

  if (!docs.size) errors.push({ file: "data/", record: "-", task: "parse", message: "no JSON datasets found" });
}

function requireDoc(file) {
  const doc = docs.get(file);
  if (!doc) fail(file, "-", "required dataset missing or unparsable");
  return doc;
}

function validateSourcePointer(ownerFile, record, pointer) {
  if (typeof pointer !== "string" || !pointer) {
    fail(ownerFile, record, "source dataset pointer must be a non-empty string");
    return;
  }
  if (!docs.has(pointer)) fail(ownerFile, record, `source dataset does not exist or is unparsable: ${pointer}`);
}

function validateCoreZubaida() {
  const indexFile = "data/zubaida-index.json";
  const excludedFile = "data/zubaida-nonsource.json";
  const index = requireDoc(indexFile);
  const excluded = requireDoc(excludedFile);
  if (!index || !excluded) return null;

  if (!isObject(index.audit)) fail(indexFile, "audit", "audit must be an object");
  const indexIds = uniqueStrings(indexFile, "ids", index.ids, "message id");
  if (!Array.isArray(index.ids)) fail(indexFile, "ids", "ids must be an array");

  const senderMessages = index.audit?.sender_messages;
  const sourceBearing = index.audit?.source_bearing_transmissions;
  if (!Number.isInteger(senderMessages) || senderMessages < 0) fail(indexFile, "audit.sender_messages", "must be a non-negative integer");
  if (!Number.isInteger(sourceBearing) || sourceBearing < 0) fail(indexFile, "audit.source_bearing_transmissions", "must be a non-negative integer");
  if (Number.isInteger(senderMessages) && indexIds.size !== senderMessages) {
    fail(indexFile, "ids", `unique id count ${indexIds.size} != audit.sender_messages ${senderMessages}`);
  }

  if (!Array.isArray(excluded.ids)) fail(excludedFile, "ids", "ids must be an array");
  const excludedIds = new Set();
  for (const [i, row] of asArray(excluded.ids).entries()) {
    if (!isObject(row) || typeof row.id !== "string" || !row.id) {
      fail(excludedFile, `ids[${i}]`, "each exclusion must have a non-empty id");
      continue;
    }
    if (excludedIds.has(row.id)) fail(excludedFile, `ids[${i}]`, `duplicate excluded id: ${row.id}`);
    excludedIds.add(row.id);
    if (!indexIds.has(row.id)) fail(excludedFile, `ids[${i}]`, `excluded id is absent from zubaida-index: ${row.id}`);
    if (typeof row.classification !== "string" || !row.classification.trim()) {
      fail(excludedFile, `ids[${i}]`, "excluded message requires a classification");
    }
  }

  const sourceIds = new Set([...indexIds].filter((id) => !excludedIds.has(id)));
  if (Number.isInteger(sourceBearing) && sourceIds.size !== sourceBearing) {
    fail(indexFile, "audit.source_bearing_transmissions", `derived source-bearing count ${sourceIds.size} != declared ${sourceBearing}`);
  }

  return { indexIds, excludedIds, sourceIds, sourceBearing };
}

const canonicalRelationships = new Set([
  "defines", "expands", "applies", "corrects", "supersedes", "example-of",
  "prerequisite-for", "contrasts-with", "related-to", "explicit-possessor", "example-subject"
]);

function validateZubaidaCrossrefs(base) {
  const file = "data/zubaida-crossrefs.json";
  const doc = docs.get(file);
  if (!doc) return;

  if (doc.task !== "ZUB-002") warn(file, "task", `unexpected task marker: ${doc.task ?? "(missing)"}`);
  const concepts = uniqueStrings(file, "concepts", doc.concepts, "concept");
  if (!Array.isArray(doc.coverage) || doc.coverage.length < 7 || doc.coverage.some((n) => !Number.isInteger(n) || n < 0)) {
    fail(file, "coverage", "coverage must contain at least seven non-negative integers");
  }

  if (!isObject(doc.rel)) fail(file, "rel", "relationship-code map must be an object");
  const relCodes = new Map();
  for (const [code, relationship] of Object.entries(doc.rel ?? {})) {
    if (!/^[A-Za-z0-9]+$/.test(code)) fail(file, `rel.${code}`, "relationship code must be alphanumeric");
    if (!canonicalRelationships.has(relationship)) fail(file, `rel.${code}`, `unsupported relationship: ${relationship}`);
    relCodes.set(code, relationship);
  }

  const edgeRows = typeof doc.edges === "string" && doc.edges ? doc.edges.split(";").filter(Boolean) : [];
  const sourcePositions = new Set();
  for (const [i, row] of edgeRows.entries()) {
    const fields = row.split(".");
    if (fields.length !== 6) {
      fail(file, `edges[${i}]`, `encoded edge must have 6 dot-delimited fields, got ${fields.length}`);
      continue;
    }
    const [source36, concept36, relCode, paragraph36, start36, end36] = fields;
    const source = Number.parseInt(source36, 36);
    const concept = Number.parseInt(concept36, 36);
    const paragraph = Number.parseInt(paragraph36, 36);
    const start = Number.parseInt(start36, 36);
    const end = Number.parseInt(end36, 36);
    if (![source, concept, paragraph, start, end].every(Number.isInteger)) {
      fail(file, `edges[${i}]`, "base36 numeric edge fields must decode to integers");
      continue;
    }
    if (base && !inRange(source, 0, base.sourceIds.size - 1)) fail(file, `edges[${i}]`, `source position ${source} outside source corpus`);
    if (!inRange(concept, 0, concepts.size - 1)) fail(file, `edges[${i}]`, `concept index ${concept} outside concepts array`);
    if (!relCodes.has(relCode)) fail(file, `edges[${i}]`, `unknown relationship code: ${relCode}`);
    if (paragraph < 0 || start < 0 || end < start) fail(file, `edges[${i}]`, "paragraph/start/end locator is invalid");
    sourcePositions.add(source);
  }

  if (Array.isArray(doc.coverage)) {
    if (base && doc.coverage[0] !== base.sourceIds.size) fail(file, "coverage[0]", `target source count ${doc.coverage[0]} != ${base.sourceIds.size}`);
    if (doc.coverage[4] !== edgeRows.length) fail(file, "coverage[4]", `declared edge count ${doc.coverage[4]} != encoded rows ${edgeRows.length}`);
    if (doc.coverage[5] !== concepts.size) fail(file, "coverage[5]", `declared concept count ${doc.coverage[5]} != unique concepts ${concepts.size}`);
    if (doc.coverage[3] > doc.coverage[0]) fail(file, "coverage", "reviewed/covered source count cannot exceed target");
    if (doc.coverage[3] && sourcePositions.size > doc.coverage[3]) fail(file, "coverage[3]", "edge source coverage exceeds declared reviewed source count");
  }
}

function validateZubaidaCharacterLinks(base) {
  const file = "data/zubaida-character-links.json";
  const doc = docs.get(file);
  if (!doc) return;

  for (const key of ["reviewed", "expected", "remaining"]) {
    if (!Number.isInteger(doc[key]) || doc[key] < 0) fail(file, key, `${key} must be a non-negative integer`);
  }
  if ([doc.reviewed, doc.expected, doc.remaining].every(Number.isInteger) && doc.reviewed + doc.remaining !== doc.expected) {
    fail(file, "coverage", `reviewed ${doc.reviewed} + remaining ${doc.remaining} != expected ${doc.expected}`);
  }
  if (base && Number.isInteger(doc.expected) && doc.expected !== base.sourceIds.size) {
    fail(file, "expected", `expected ${doc.expected} != source-bearing corpus ${base.sourceIds.size}`);
  }
  if (doc.status === "partial" && doc.remaining === 0) warn(file, "status", "status is partial but remaining is zero");
  if (["complete", "finished"].includes(doc.status) && doc.remaining !== 0) fail(file, "status", `status ${doc.status} requires remaining=0`);

  if (!isObject(doc.entity)) fail(file, "entity", "entity registry must be an object");
  const aliasOwners = new Map();
  for (const [key, entity] of Object.entries(doc.entity ?? {})) {
    if (!/^[a-z0-9][a-z0-9-]*$/.test(key)) fail(file, `entity.${key}`, "entity key must be lowercase stable-id syntax");
    if (!isObject(entity) || typeof entity.n !== "string" || !entity.n.trim()) fail(file, `entity.${key}`, "entity requires non-empty n/name");
    if (!isObject(entity) || typeof entity.k !== "string" || !entity.k.trim()) fail(file, `entity.${key}`, "entity requires non-empty k/kind");
    const aliases = [entity?.n, ...asArray(entity?.a)].filter((x) => typeof x === "string" && x.trim());
    for (const alias of aliases) {
      const norm = normalizedAlias(alias);
      if (!aliasOwners.has(norm)) aliasOwners.set(norm, new Set());
      aliasOwners.get(norm).add(key);
    }
  }
  for (const [alias, owners] of aliasOwners) {
    if (owners.size > 1) warn(file, `alias:${alias}`, `duplicate normalized alias maps to multiple entities: ${[...owners].join(", ")}`);
  }

  if (!isObject(doc.tx)) fail(file, "tx", "transmission map must be an object");
  const txEntries = Object.entries(doc.tx ?? {});
  if (Number.isInteger(doc.reviewed) && txEntries.length !== doc.reviewed) {
    fail(file, "reviewed", `reviewed ${doc.reviewed} != transmission records ${txEntries.length}`);
  }
  for (const [txId, tx] of txEntries) {
    if (base && !base.sourceIds.has(txId)) fail(file, `tx.${txId}`, "transmission id is not source-bearing");
    if (!isObject(tx)) {
      fail(file, `tx.${txId}`, "transmission record must be an object");
      continue;
    }
    if (tx.sha !== undefined && (typeof tx.sha !== "string" || !/^[0-9a-f]{40}$/i.test(tx.sha))) {
      fail(file, `tx.${txId}.sha`, "sha must be a 40-character hex Git object id");
    }
    for (const [i, entityKey] of asArray(tx.e).entries()) {
      if (typeof entityKey !== "string" || !doc.entity?.[entityKey]) {
        fail(file, `tx.${txId}.e[${i}]`, `unknown entity target: ${String(entityKey)}`);
      }
    }
  }
}

function validateDivineCore() {
  const file = "data/divine.json";
  const doc = requireDoc(file);
  if (!doc) return null;
  if (!Array.isArray(doc.sections)) {
    fail(file, "sections", "sections must be an array");
    return null;
  }

  const ids = new Set();
  const numbered = new Set();
  for (const [i, section] of doc.sections.entries()) {
    if (!isObject(section) || typeof section.id !== "string" || !section.id) {
      fail(file, `sections[${i}]`, "section requires non-empty id");
      continue;
    }
    if (ids.has(section.id)) fail(file, `sections[${i}]`, `duplicate section id: ${section.id}`);
    ids.add(section.id);
    const n = parseTrailingInteger(section.id, "divine-");
    if (n !== null) numbered.add(n);
    if (section.parent_id !== null && section.parent_id !== undefined && typeof section.parent_id !== "string") {
      fail(file, `sections[${i}].parent_id`, "parent_id must be string or null");
    }
  }

  for (const section of doc.sections) {
    if (section?.parent_id && !ids.has(section.parent_id)) fail(file, section.id, `orphan parent_id: ${section.parent_id}`);
    for (const child of asArray(section?.children)) if (!ids.has(child)) fail(file, section.id, `orphan child id: ${child}`);
  }

  if (numbered.size !== 317) fail(file, "sections", `expected 317 numbered Divine sections, found ${numbered.size}`);
  for (let n = 1; n <= 317; n++) if (!numbered.has(n)) fail(file, `divine-${n}`, "missing numbered Divine section");

  return { ids, numbered };
}

function validateDivineExpansions(divine) {
  for (const [file, doc] of docs) {
    if (!/^data\/divine-explanations-\d{3}-\d{3}\.json$/.test(file)) continue;
    const source = doc.source;
    if (!isObject(source)) fail(file, "source", "source contract must be an object");
    else {
      validateSourcePointer(file, "source.dataset", source.dataset);
      if (source.immutable !== true) fail(file, "source.immutable", "source dataset must be marked immutable=true");
    }

    const coverage = doc.coverage;
    if (!isObject(coverage)) fail(file, "coverage", "coverage must be an object");
    const target = coverage?.target_sections;
    const completed = coverage?.completed_sections;
    if (!Number.isInteger(target) || target <= 0) fail(file, "coverage.target_sections", "must be a positive integer");
    if (!Number.isInteger(completed) || completed < 0) fail(file, "coverage.completed_sections", "must be a non-negative integer");
    if (Number.isInteger(target) && Number.isInteger(completed) && completed > target) fail(file, "coverage", "completed_sections exceeds target_sections");

    if (!Array.isArray(doc.sections)) fail(file, "sections", "sections must be an array");
    if (Number.isInteger(completed) && asArray(doc.sections).length !== completed) {
      fail(file, "coverage.completed_sections", `declared ${completed} != section records ${asArray(doc.sections).length}`);
    }
    const status = coverage?.status ?? doc.status;
    if (["complete", "finished"].includes(status) && completed !== target) fail(file, "coverage.status", `${status} requires completed_sections == target_sections`);

    let ownedStart = null;
    let ownedEnd = null;
    if (Array.isArray(source?.source_id_range) && source.source_id_range.length === 2) {
      ownedStart = parseTrailingInteger(source.source_id_range[0], "divine-");
      ownedEnd = parseTrailingInteger(source.source_id_range[1], "divine-");
      if (!Number.isInteger(ownedStart) || !Number.isInteger(ownedEnd) || ownedStart > ownedEnd) {
        fail(file, "source.source_id_range", "invalid Divine source id range");
      }
      if (Number.isInteger(target) && Number.isInteger(ownedStart) && Number.isInteger(ownedEnd) && ownedEnd - ownedStart + 1 !== target) {
        fail(file, "coverage.target_sections", "target_sections does not match owned source_id_range width");
      }
    }

    const vocab = new Set(asArray(doc.relationship_vocabulary));
    for (const relName of vocab) if (!canonicalRelationships.has(relName)) warn(file, "relationship_vocabulary", `non-global relationship vocabulary value: ${relName}`);

    const seen = new Set();
    for (const [i, section] of asArray(doc.sections).entries()) {
      const record = section?.section_id || `sections[${i}]`;
      if (!isObject(section) || typeof section.section_id !== "string") {
        fail(file, record, "section entry requires section_id");
        continue;
      }
      if (seen.has(section.section_id)) fail(file, record, `duplicate section_id: ${section.section_id}`);
      seen.add(section.section_id);
      if (divine && !divine.ids.has(section.section_id)) fail(file, record, "section_id does not exist in data/divine.json");
      const n = parseTrailingInteger(section.section_id, "divine-");
      if (Number.isInteger(ownedStart) && Number.isInteger(ownedEnd) && !inRange(n, ownedStart, ownedEnd)) fail(file, record, "section_id lies outside owned batch range");
      if (Number.isInteger(section.source_order) && Number.isInteger(n) && section.source_order !== n) fail(file, record, `source_order ${section.source_order} != id order ${n}`);

      for (const [j, targetId] of [...asArray(section.prerequisites), ...asArray(section.related_sections)].entries()) {
        if (typeof targetId !== "string" || (divine && !divine.ids.has(targetId))) fail(file, `${record}.link[${j}]`, `invalid Divine section locator: ${String(targetId)}`);
      }
      for (const [j, link] of asArray(section.concept_links).entries()) {
        if (!isObject(link) || typeof link.label !== "string" || !link.label.trim()) fail(file, `${record}.concept_links[${j}]`, "concept link requires label");
        if (!isObject(link) || typeof link.relationship !== "string" || (vocab.size && !vocab.has(link.relationship))) {
          fail(file, `${record}.concept_links[${j}]`, `relationship is absent from relationship_vocabulary: ${link?.relationship}`);
        }
        if (isObject(link?.target)) {
          if (link.target.dataset) validateSourcePointer(file, `${record}.concept_links[${j}].target.dataset`, link.target.dataset);
          if (link.target.section_id && divine && !divine.ids.has(link.target.section_id)) fail(file, `${record}.concept_links[${j}]`, `target section does not exist: ${link.target.section_id}`);
        }
      }
      for (const [j, link] of asArray(section.character_links).entries()) {
        if (!isObject(link) || typeof link.label !== "string" || !link.label.trim()) fail(file, `${record}.character_links[${j}]`, "character link requires label");
        if (link?.relationship && vocab.size && !vocab.has(link.relationship)) fail(file, `${record}.character_links[${j}]`, `relationship is absent from relationship_vocabulary: ${link.relationship}`);
      }
    }
  }
}

function validateHglCore() {
  const pagesFile = "data/hgl-pages.json";
  const tocFile = "data/hgl-toc.json";
  const pages = requireDoc(pagesFile);
  const toc = requireDoc(tocFile);
  const pageNumbers = new Set();
  const tocIds = new Set();

  if (pages) {
    if (!Array.isArray(pages.pages)) fail(pagesFile, "pages", "pages must be an array");
    for (const [i, row] of asArray(pages.pages).entries()) {
      if (!Number.isInteger(row?.page)) fail(pagesFile, `pages[${i}]`, "page number must be an integer");
      else if (pageNumbers.has(row.page)) fail(pagesFile, `pages[${i}]`, `duplicate page number: ${row.page}`);
      else pageNumbers.add(row.page);
    }
    if (pageNumbers.size !== 293) fail(pagesFile, "pages", `expected 293 HGL pages, found ${pageNumbers.size}`);
    for (let n = 1; n <= 293; n++) if (!pageNumbers.has(n)) fail(pagesFile, `page:${n}`, "missing HGL page");
  }

  if (toc) {
    if (!Array.isArray(toc.toc)) fail(tocFile, "toc", "toc must be an array");
    for (const [i, row] of asArray(toc.toc).entries()) {
      if (typeof row?.id !== "string" || !row.id) fail(tocFile, `toc[${i}]`, "TOC node requires id");
      else if (tocIds.has(row.id)) fail(tocFile, `toc[${i}]`, `duplicate TOC id: ${row.id}`);
      else tocIds.add(row.id);
      if (!Number.isInteger(row?.page) || !inRange(row.page, 1, 293)) fail(tocFile, `toc[${i}]`, `invalid HGL page locator: ${row?.page}`);
    }
    if (tocIds.size !== 1037) fail(tocFile, "toc", `expected 1037 HGL TOC nodes, found ${tocIds.size}`);
  }
  return { pageNumbers, tocIds };
}

function normalizeHglPart(part) {
  const n = part?.major_part_number ?? part?.n;
  const id = part?.source_part_id ?? part?.id;
  let start;
  let end;
  if (isObject(part?.source_page_range)) {
    start = part.source_page_range.start;
    end = part.source_page_range.end;
  } else if (Array.isArray(part?.pages)) {
    [start, end] = part.pages;
  }
  return { n, id, start, end };
}

function hglCrosslinkTarget(item) {
  if (typeof item === "string") return item;
  if (isObject(item) && typeof item.target === "string") return item.target;
  return null;
}

function validateHglExpansions() {
  for (const [file, doc] of docs) {
    if (!/^data\/hgl-explanations-parts-\d{3}-\d{3}\.json$/.test(file)) continue;

    const rawRange = doc.owned_major_part_range;
    const range = Array.isArray(rawRange)
      ? { start: rawRange[0], end: rawRange[1] }
      : rawRange;
    if (!isObject(range) || !inRange(range.start, 1, 95) || !inRange(range.end, 1, 95) || range.start > range.end) {
      fail(file, "owned_major_part_range", "must be a valid inclusive range within major parts 1..95");
    }
    const width = Number.isInteger(range?.start) && Number.isInteger(range?.end) ? range.end - range.start + 1 : null;

    const source = doc.source_contract;
    if (!isObject(source)) fail(file, "source_contract", "source_contract must be an object");
    else {
      const tocPointer = source.toc_source ?? source.toc;
      const pagePointer = source.page_source ?? source.pages;
      const pageCount = source.source_page_count ?? source.source_pages;
      const immutable = source.source_is_immutable ?? source.source_immutable;
      const explanationOnly = source.explanation_layer_only ?? source.explanations_separate;
      validateSourcePointer(file, "source_contract.toc", tocPointer);
      validateSourcePointer(file, "source_contract.pages", pagePointer);
      if (pageCount !== 293) fail(file, "source_contract.source_pages", `expected 293, got ${pageCount}`);
      if (immutable !== true || explanationOnly !== true) fail(file, "source_contract", "source must be immutable and explanations must be separate");
    }

    const coverage = doc.coverage;
    if (!isObject(coverage)) fail(file, "coverage", "coverage must be an object");
    const completed = asArray(coverage?.completed_major_parts ?? coverage?.completed);
    const remaining = asArray(coverage?.remaining_major_parts ?? coverage?.remaining);
    const declaredCompletedCount = coverage?.completed_major_part_count ?? coverage?.count;
    const declaredOwnedCount = coverage?.owned_major_part_count ?? coverage?.owned;
    if (declaredCompletedCount !== completed.length) fail(file, "coverage.completed_count", "does not match completed list length");
    if (width !== null && declaredOwnedCount !== width) fail(file, "coverage.owned_count", `does not match range width ${width}`);
    const completedSet = new Set(completed);
    const remainingSet = new Set(remaining);
    if (completedSet.size !== completed.length) fail(file, "coverage.completed", "contains duplicates");
    if (remainingSet.size !== remaining.length) fail(file, "coverage.remaining", "contains duplicates");
    for (const n of completedSet) if (!inRange(n, range.start, range.end)) fail(file, "coverage.completed", `part ${n} outside owned range`);
    for (const n of remainingSet) if (!inRange(n, range.start, range.end)) fail(file, "coverage.remaining", `part ${n} outside owned range`);
    for (const n of completedSet) if (remainingSet.has(n)) fail(file, "coverage", `part ${n} appears in both completed and remaining`);
    if (width !== null && completedSet.size + remainingSet.size !== width) fail(file, "coverage", "completed + remaining does not cover owned range exactly");
    if (["complete", "finished", "complete_pending_verification"].includes(doc.status) && remainingSet.size !== 0) fail(file, "status", `${doc.status} requires zero remaining parts`);

    const parts = asArray(doc.parts);
    if (parts.length !== completedSet.size) fail(file, "parts", `part record count ${parts.length} != completed coverage ${completedSet.size}`);
    const seenN = new Set();
    const seenIds = new Set();
    for (const [i, part] of parts.entries()) {
      const { n, id, start, end } = normalizeHglPart(part);
      const record = id || `parts[${i}]`;
      if (!Number.isInteger(n) || !inRange(n, range.start, range.end)) fail(file, record, `major-part number ${n} outside owned range`);
      if (seenN.has(n)) fail(file, record, `duplicate major-part number: ${n}`);
      seenN.add(n);
      if (!completedSet.has(n)) fail(file, record, `part ${n} is not listed in completed coverage`);
      if (typeof id !== "string" || !/^hgl-part-\d+$/.test(id)) fail(file, record, `invalid source part id: ${String(id)}`);
      else {
        if (seenIds.has(id)) fail(file, record, `duplicate source part id: ${id}`);
        seenIds.add(id);
        const idN = parseTrailingInteger(id, "hgl-part-");
        if (Number.isInteger(n) && idN !== n - 1) fail(file, record, `source part id ${id} does not match major-part number ${n}`);
      }
      if (!Number.isInteger(start) || !Number.isInteger(end) || !inRange(start, 1, 293) || !inRange(end, 1, 293) || start > end) {
        fail(file, record, `invalid HGL source-page range: ${start}..${end}`);
      }

      const rawLinks = Array.isArray(part?.crosslinks)
        ? part.crosslinks
        : (part?.crosslink ? [part.crosslink] : []);
      for (const [j, link] of rawLinks.entries()) {
        const target = hglCrosslinkTarget(link);
        if (!target || !/^hgl-part-\d+$/.test(target)) fail(file, `${record}.crosslinks[${j}]`, `invalid HGL part target: ${String(target)}`);
        else {
          const targetN = parseTrailingInteger(target, "hgl-part-");
          if (!inRange(targetN, 0, 94)) fail(file, `${record}.crosslinks[${j}]`, `HGL part target outside 0..94: ${target}`);
        }
      }
    }
  }
}

function validateGenericStableIdsAndProvenance() {
  for (const [file, doc] of docs) {
    if ((file.includes("explanations-") || file.includes("crossrefs") || file.includes("character-links")) && !(doc?.task || doc?.task_id)) {
      fail(file, "-", "generated dataset is missing task/task_id provenance");
    }

    for (const [key, value] of Object.entries(isObject(doc) ? doc : {})) {
      if (!Array.isArray(value) || !value.length || !value.every(isObject) || !value.some((x) => Object.hasOwn(x, "id"))) continue;
      const seen = new Set();
      for (const [i, row] of value.entries()) {
        if (row.id === undefined) continue;
        if (typeof row.id !== "string" || !row.id.trim()) fail(file, `${key}[${i}].id`, "stable id must be a non-empty string");
        else if (seen.has(row.id)) fail(file, `${key}[${i}].id`, `duplicate stable id: ${row.id}`);
        else seen.add(row.id);
      }
    }
  }
}

function printDiagnostics() {
  for (const entry of warnings) {
    console.warn(`::warning file=${entry.file}::${entry.task} ${entry.record} — ${entry.message}`);
  }
  for (const entry of errors) {
    console.error(`::error file=${entry.file}::${entry.task} ${entry.record} — ${entry.message}`);
  }
  console.log(`QA-006 data-contract validation: ${docs.size} JSON files; ${errors.length} error(s); ${warnings.length} warning(s).`);
}

await loadAllJson();
if (!errors.some((e) => e.task === "parse")) {
  const zubaida = validateCoreZubaida();
  validateZubaidaCrossrefs(zubaida);
  validateZubaidaCharacterLinks(zubaida);
  const divine = validateDivineCore();
  validateDivineExpansions(divine);
  validateHglCore();
  validateHglExpansions();
  validateGenericStableIdsAndProvenance();
}
printDiagnostics();
if (errors.length) process.exit(1);
