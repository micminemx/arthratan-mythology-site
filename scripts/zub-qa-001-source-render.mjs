#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright';

const root = process.cwd();
const base = (process.env.ZUB_QA_BASE_URL || 'https://arthratanmythology.com/').replace(/\/+$/, '') + '/';
const reportPath = process.env.ZUB_QA_REPORT || 'zub-qa-001-source-render-report.json';
const expectedSha = process.env.GITHUB_SHA || process.env.EXPECTED_SHA || null;

const readJson = (rel) => JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'));
const normalize = (text) => String(text ?? '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');

function firstMismatch(expected, actual) {
  const a = normalize(expected).split('\n');
  const b = normalize(actual).split('\n');
  const max = Math.max(a.length, b.length);
  for (let i = 0; i < max; i++) {
    if (a[i] !== b[i]) {
      const from = Math.max(0, i - 2);
      const to = Math.min(max, i + 3);
      return {
        line: i + 1,
        expected_lines: a.slice(from, to),
        actual_lines: b.slice(from, to),
        expected_line_count: a.length,
        actual_line_count: b.length,
      };
    }
  }
  return null;
}

function sourceIds() {
  const index = readJson('data/zubaida-index.json');
  const non = readJson('data/zubaida-nonsource.json');
  const rows = non.non_source_records || non.ids || [];
  const excluded = new Set(rows.map((row) => row.id));
  const ids = (index.ids || []).filter((id) => !excluded.has(id));
  return { index, rows, ids };
}

async function fetchLiveSource(id) {
  const url = `${base}sources/zubaida/${encodeURIComponent(id)}.txt?zubqa=${Date.now()}`;
  const response = await fetch(url, { cache: 'no-store', redirect: 'follow' });
  const text = response.ok ? await response.text() : '';
  return { url, status: response.status, ok: response.ok, text };
}

async function main() {
  const { index, rows: nonSourceRows, ids } = sourceIds();
  const report = {
    task: 'ZUB-QA-001',
    generated_at: new Date().toISOString(),
    expected_sha: expectedSha,
    base_url: base,
    corpus: {
      sender_messages: index?.audit?.sender_messages,
      expected_source_bearing: index?.audit?.source_bearing_transmissions,
      derived_source_bearing: ids.length,
      non_source_records: nonSourceRows.length,
    },
    checks: {},
    raw_source_failures: [],
    render_failures: [],
    browser_errors: [],
  };

  if (ids.length !== 118) {
    report.checks.derived_118_source_ids = false;
    report.fatal = `Derived ${ids.length} source-bearing IDs instead of 118.`;
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
    process.exit(1);
  }
  report.checks.derived_118_source_ids = true;

  const expected = new Map();
  for (const id of ids) {
    const rel = `sources/zubaida/${id}.txt`;
    const file = path.join(root, rel);
    if (!fs.existsSync(file)) {
      report.raw_source_failures.push({ id, stage: 'local', reason: 'missing preserved source file', rel });
      continue;
    }
    const text = fs.readFileSync(file, 'utf8');
    if (!text.trim()) report.raw_source_failures.push({ id, stage: 'local', reason: 'empty preserved source file', rel });
    expected.set(id, text);
  }
  report.checks.local_118_source_files_present = expected.size === 118 && report.raw_source_failures.length === 0;

  let cursor = 0;
  const workers = Array.from({ length: 8 }, async () => {
    while (true) {
      const i = cursor++;
      if (i >= ids.length) return;
      const id = ids[i];
      const local = expected.get(id);
      if (local === undefined) continue;
      try {
        const live = await fetchLiveSource(id);
        const mismatch = live.ok ? firstMismatch(local, live.text) : null;
        if (!live.ok || mismatch) {
          report.raw_source_failures.push({
            id,
            stage: 'live-raw-source',
            status: live.status,
            reason: live.ok ? 'live raw source differs from preserved candidate' : 'live raw source request failed',
            mismatch,
          });
        }
      } catch (error) {
        report.raw_source_failures.push({ id, stage: 'live-raw-source', reason: String(error) });
      }
    }
  });
  await Promise.all(workers);
  report.checks.live_raw_sources_118_of_118 = report.raw_source_failures.length === 0;

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1365, height: 900 } });
  page.on('pageerror', (error) => report.browser_errors.push(`pageerror: ${String(error)}`));
  page.on('console', (message) => {
    if (message.type() === 'error') report.browser_errors.push(`console: ${message.text()}`);
  });

  for (let i = 0; i < ids.length; i++) {
    const id = ids[i];
    const local = expected.get(id);
    if (local === undefined) continue;
    const route = `${base}?zubqa=${encodeURIComponent(expectedSha || 'run')}-${i}#transmission:${id}`;
    try {
      const response = await page.goto(route, { waitUntil: 'domcontentloaded', timeout: 45000 });
      if (!response?.ok()) {
        report.render_failures.push({ id, route, stage: 'navigation', status: response?.status() ?? null, reason: 'page response not OK' });
        continue;
      }
      await page.waitForSelector('.tx-source', { state: 'visible', timeout: 20000 });
      const rendered = await page.locator('.tx-source').textContent();
      const mismatch = firstMismatch(local, rendered);
      if (mismatch) {
        report.render_failures.push({ id, route, stage: 'render', reason: 'rendered source differs from preserved source', mismatch });
      }
    } catch (error) {
      report.render_failures.push({ id, route, stage: 'render', reason: String(error) });
    }
  }

  await browser.close();
  report.checks.rendered_source_panels_118_of_118 = report.render_failures.length === 0;
  report.checks.no_uncaught_browser_errors = report.browser_errors.length === 0;
  report.counts = {
    source_ids: ids.length,
    local_sources: expected.size,
    raw_source_failures: report.raw_source_failures.length,
    render_failures: report.render_failures.length,
    browser_errors: report.browser_errors.length,
    render_passes: ids.length - report.render_failures.length,
  };
  report.complete = Object.values(report.checks).every(Boolean);

  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
  console.log(`ZUB-QA-001: ${report.counts.render_passes}/${ids.length} rendered source panels match preserved source; raw failures=${report.raw_source_failures.length}; browser errors=${report.browser_errors.length}.`);
  if (!report.complete) process.exit(1);
}

main().catch((error) => {
  const fatal = {
    task: 'ZUB-QA-001',
    generated_at: new Date().toISOString(),
    expected_sha: expectedSha,
    base_url: base,
    complete: false,
    fatal: String(error?.stack || error),
  };
  fs.writeFileSync(reportPath, JSON.stringify(fatal, null, 2) + '\n');
  console.error(error);
  process.exit(1);
});
