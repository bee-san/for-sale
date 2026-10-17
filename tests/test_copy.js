const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function page(clipboard) {
  const field = { value: 'First line\nSecond line & quoted "text"', focused: false, selected: false,
    focus() { this.focused = true; }, select() { this.selected = true; },
    setSelectionRange() { this.selected = true; } };
  const status = { textContent: '' };
  let handler;
  const button = { textContent: 'Copy description', dataset: { copyTarget: 'description-test' },
    closest(selector) { return selector === '[data-copy-target]' ? this : null; } };
  const document = {
    getElementById(id) { return id === 'copy-status' ? status : id === 'description-test' ? field : null; },
    addEventListener(name, callback) { if (name === 'click') handler = callback; },
  };
  const source = path.join(__dirname, '..', 'assets/js/vinted-copy.js');
  assert.ok(fs.existsSync(source), 'Copy buttons have no implementation');
  vm.runInNewContext(fs.readFileSync(source, 'utf8'), {
    document, navigator: { clipboard }, setTimeout() {}, console,
  });
  return { field, status, button, async click() { await handler({ target: button }); } };
}

test('copy writes the exact plain field, including newlines', async () => {
  let copied;
  const state = page({ async writeText(value) { copied = value; } });
  await state.click();
  assert.equal(copied, state.field.value);
  assert.match(state.status.textContent, /copied/i);
});

test('clipboard denial selects the field and explains manual copying', async () => {
  const state = page({ async writeText() { throw new Error('Permission denied'); } });
  await state.click();
  assert.equal(state.field.focused, true);
  assert.equal(state.field.selected, true);
  assert.match(state.status.textContent, /copy manually/i);
  assert.notEqual(state.button.textContent, 'Copied');
});

test('missing Clipboard API still provides a usable manual fallback', async () => {
  const state = page(undefined);
  await state.click();
  assert.equal(state.field.selected, true);
  assert.match(state.status.textContent, /copy manually/i);
});
