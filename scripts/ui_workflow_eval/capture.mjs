#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, readFileSync, readdirSync, realpathSync, statSync, writeFileSync } from 'node:fs';
import { basename, dirname, join, relative, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

const ALLOWED_ACTIONS = new Set(['goto', 'click', 'fill', 'press', 'waitForVisible', 'screenshot']);
const SNAPSHOT_SOURCES = {
  fixture_manifest_sha256: 'fixture',
  product_manifest_sha256: 'product',
  design_authority_manifest_sha256: 'design_authority',
  ui_spec_manifest_sha256: 'ui_spec',
  plugin_inventory_sha256: 'plugin_inventory',
};

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    if (!key?.startsWith('--') || argv[index + 1] === undefined) throw new Error(`invalid argument: ${key}`);
    values[key.slice(2)] = argv[index + 1];
  }
  return values;
}

function sha256Bytes(value) {
  return createHash('sha256').update(value).digest('hex');
}

function sha256File(path) {
  return sha256Bytes(readFileSync(path));
}

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function walkFiles(root, current = root, output = []) {
  for (const name of readdirSync(current).sort()) {
    const path = join(current, name);
    const info = lstatSync(path);
    if (info.isSymbolicLink()) throw new Error(`symlink inside manifest is not allowed: ${path}`);
    if (info.isDirectory()) walkFiles(root, path, output);
    else if (info.isFile()) output.push(path);
  }
  return output;
}

function manifestHash(input) {
  const path = realpathSync(input);
  const info = lstatSync(path);
  if (info.isSymbolicLink()) throw new Error(`symlink source is not allowed: ${input}`);
  if (info.isFile()) return sha256File(path);
  if (!info.isDirectory()) throw new Error(`manifest source is invalid: ${input}`);
  const digest = createHash('sha256');
  for (const file of walkFiles(path)) {
    digest.update(relative(path, file).split(sep).join('/') + '\0' + sha256File(file) + '\n');
  }
  return digest.digest('hex');
}

function within(path, root) {
  const candidate = resolve(path);
  const boundary = realpathSync(root);
  const rel = relative(boundary, candidate);
  return rel === '' || (!rel.startsWith('..' + sep) && rel !== '..' && !rel.startsWith(sep));
}

function allowedTarget(raw, caseRoot) {
  let url;
  try {
    url = new URL(raw);
  } catch {
    if (!resolve(raw).startsWith(caseRoot + sep) && resolve(raw) !== caseRoot) throw new Error('path escapes case root');
    return pathToFileURL(resolve(raw)).href;
  }
  if (url.protocol === 'file:') {
    if (!within(decodeURIComponent(url.pathname), caseRoot)) throw new Error('file URL escapes case root');
    return url.href;
  }
  if (url.protocol !== 'http:') throw new Error('only file and loopback http URLs are allowed');
  if (!['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname)) throw new Error('network target is not loopback');
  return url.href;
}

function currentSnapshot(envelope) {
  const snapshot = { case_realpath: realpathSync(envelope.pending.snapshot.case_realpath) };
  for (const [hashKey, sourceKey] of Object.entries(SNAPSHOT_SOURCES)) {
    snapshot[hashKey] = manifestHash(envelope.capture_context.snapshot_sources[sourceKey]);
  }
  return snapshot;
}

function snapshotMismatches(expected, actual) {
  return ['case_realpath', ...Object.keys(SNAPSHOT_SOURCES)].filter((key) => expected[key] !== actual[key]);
}

function writeResult(path, value) {
  mkdirSync(dirname(resolve(path)), { recursive: true });
  writeFileSync(path, JSON.stringify(value, null, 2) + '\n', { encoding: 'utf8', mode: 0o600 });
}

async function loadPlaywright(playwrightRoot) {
  const modulePath = join(realpathSync(playwrightRoot), 'index.mjs');
  const module = await import(pathToFileURL(modulePath).href);
  if (!module.chromium) throw new Error('Playwright chromium API is missing');
  return module;
}

async function runProbe(args, chromium) {
  const runnerPath = realpathSync(process.argv[1]);
  if (sha256File(runnerPath) !== args['runner-sha256']) throw new Error('runner sha256 mismatch');
  const source = realpathSync(args['probe-source']);
  const output = resolve(args['probe-output']);
  const browser = await chromium.launch({
    executablePath: realpathSync(args['chromium-executable']),
    headless: true,
    env: { LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8' },
  });
  try {
    const page = await browser.newPage({ viewport: { width: 800, height: 500 } });
    await page.goto(pathToFileURL(source).href, { waitUntil: 'load', timeout: 15000 });
    await page.screenshot({ path: output, type: 'png' });
  } finally {
    await browser.close();
  }
  if (!existsSync(output) || statSync(output).size === 0) throw new Error('probe image is empty');
}

function policyCheck(envelope) {
  const caseRoot = realpathSync(envelope.pending.snapshot.case_realpath);
  if (sha256Bytes(Buffer.from(canonical(envelope.pending))) !== envelope.request_sha256) throw new Error('request sha256 mismatch');
  if (!within(envelope.capture_context.evidence_output_root, envelope.capture_context.evaluation_root)) {
    throw new Error('evidence output escapes evaluation root');
  }
  if (envelope.capture_context.case_script || envelope.capture_context.shell || envelope.capture_context.executable_override) {
    throw new Error('case-authored script/executable is forbidden');
  }
  for (const scenario of envelope.pending.matrix || []) {
    allowedTarget(scenario.route_or_file, caseRoot);
    if (!Array.isArray(scenario.actions) || scenario.actions.length === 0 || scenario.actions.length > 32) {
      throw new Error('invalid scenario actions');
    }
    for (const action of scenario.actions) {
      if (!ALLOWED_ACTIONS.has(action.action)) throw new Error(`action is not allowed: ${action.action}`);
      if ('script' in action || 'javascript' in action || 'shell' in action) throw new Error('case-authored script is forbidden');
      if (action.action === 'fill') {
        if (action.fixture_data !== true) throw new Error('fill requires fixture_data');
        if (/credential|password|secret|token|api[_-]?key/i.test(action.value || '')) throw new Error('credential fill is forbidden');
      }
    }
  }
}

async function runAction(page, action, scenarioTarget, outputRoot, scenarioId) {
  const timeout = action.timeout_ms || 5000;
  if (action.action === 'goto') await page.goto(action.url || scenarioTarget, { waitUntil: 'load', timeout });
  else if (action.action === 'click') await page.locator(action.selector).click({ timeout });
  else if (action.action === 'fill') await page.locator(action.selector).fill(action.value, { timeout });
  else if (action.action === 'press') await page.locator(action.selector).press(action.key, { timeout });
  else if (action.action === 'waitForVisible') await page.locator(action.selector).waitFor({ state: 'visible', timeout });
  else if (action.action === 'screenshot') {
    const path = join(outputRoot, `${scenarioId}.png`);
    await page.screenshot({ path, type: 'png', fullPage: action.full_page === true });
    return path;
  }
  return null;
}

async function capture(envelope, args, chromium) {
  const outputPath = resolve(args.output);
  const outputRoot = resolve(envelope.capture_context.evidence_output_root);
  mkdirSync(outputRoot, { recursive: true });
  const command = process.argv.slice();
  const stderrPath = join(outputRoot, 'capture.stderr.txt');
  const affected = (envelope.pending.matrix || []).map((item) => item.scenario_id);
  try {
    policyCheck(envelope);
  } catch (error) {
    writeFileSync(stderrPath, String(error.message) + '\n', { encoding: 'utf8', mode: 0o600 });
    const blocked = { type: 'CaptureBlocked', command, exit_code: 64, stderr_path: stderrPath, affected_scenarios: affected };
    writeResult(outputPath, blocked);
    return 64;
  }
  const before = currentSnapshot(envelope);
  const mismatch = snapshotMismatches(envelope.pending.snapshot, before);
  if (mismatch.length) {
    writeResult(outputPath, { type: 'StaleRenderRequest', mismatched_manifests: mismatch });
    return 0;
  }

  let browser;
  try {
    browser = await chromium.launch({
      executablePath: realpathSync(args['chromium-executable']),
      headless: true,
      env: { LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8' },
    });
    const context = await browser.newContext();
    const caseRoot = realpathSync(envelope.pending.snapshot.case_realpath);
    await context.route('**/*', async (route) => {
      try {
        allowedTarget(route.request().url(), caseRoot);
        await route.continue();
      } catch {
        await route.abort('blockedbyclient');
      }
    });
    const captured = [];
    for (const scenario of envelope.pending.matrix) {
      const page = await context.newPage();
      const target = allowedTarget(scenario.route_or_file, caseRoot);
      let imagePath = null;
      try {
        if (!scenario.actions.some((item) => item.action === 'goto')) {
          await page.goto(target, { waitUntil: 'load', timeout: 15000 });
        }
        for (const action of scenario.actions) {
          imagePath = (await runAction(page, action, target, outputRoot, scenario.scenario_id)) || imagePath;
        }
      } finally {
        await page.close();
      }
      if (!imagePath || !existsSync(imagePath) || statSync(imagePath).size === 0) {
        writeResult(outputPath, { type: 'IncompleteCapture', missing_scenarios: [scenario.scenario_id] });
        await browser.close();
        return 0;
      }
      captured.push({
        scenario_id: scenario.scenario_id,
        route_or_file: scenario.route_or_file,
        viewport: scenario.viewport,
        state: scenario.state,
        image_path: imagePath,
        image_sha256: sha256File(imagePath),
        exit_code: 0,
      });
    }
    await browser.close();
    browser = null;
    const after = currentSnapshot(envelope);
    const changed = snapshotMismatches(envelope.pending.snapshot, after);
    if (changed.length) {
      writeResult(outputPath, { type: 'StaleRenderRequest', mismatched_manifests: changed });
      return 0;
    }
    const evidence = {
      request_sha256: envelope.request_sha256,
      producer_call_id: envelope.pending.producer_call_id,
      snapshot: envelope.pending.snapshot,
      browser: {
        engine: 'chromium',
        version: args['browser-version'],
        executable_sha256: sha256File(realpathSync(args['chromium-executable'])),
      },
      runner_argv: command,
      captures: captured,
    };
    for (const key of Object.keys(SNAPSHOT_SOURCES)) evidence[key.replace('_sha256', '_sha256_after')] = after[key];
    writeResult(outputPath, { type: 'Captured', evidence });
    return 0;
  } catch (error) {
    if (browser) await browser.close().catch(() => {});
    writeFileSync(stderrPath, String(error.stack || error) + '\n', { encoding: 'utf8', mode: 0o600 });
    writeResult(outputPath, { type: 'CaptureBlocked', command, exit_code: 1, stderr_path: stderrPath, affected_scenarios: affected });
    return 1;
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const runnerPath = realpathSync(process.argv[1]);
  if (sha256File(runnerPath) !== args['runner-sha256']) throw new Error('runner sha256 mismatch');
  const { chromium } = await loadPlaywright(args['playwright-root']);
  if (args['probe-source']) {
    await runProbe(args, chromium);
    return 0;
  }
  for (const key of ['request', 'output', 'chromium-executable', 'browser-version']) {
    if (!args[key]) throw new Error(`missing --${key}`);
  }
  const envelope = JSON.parse(readFileSync(args.request, 'utf8'));
  return await capture(envelope, args, chromium);
}

try {
  process.exitCode = await main();
} catch (error) {
  process.stderr.write(`${error.stack || error}\n`);
  process.exitCode = 2;
}
