// Fix 4: validator output, terminal output and shell-echo text must be HTML-escaped before innerHTML.
// Run: node tests/test_innerhtml_escaping.js
"use strict";
const assert = require("assert");
const { loadApp } = require("./app_harness");
const { makeDocument } = require("./dom_fake");

const PAYLOAD = "<img src=x onerror=alert(1)>";
const { document, elements } = makeDocument();

class FakeWebSocket {
    constructor() { FakeWebSocket.last = this; this.readyState = 1; }
    send() {} close() {}
}
FakeWebSocket.OPEN = 1;

const { get } = loadApp({
    document,
    WebSocket: FakeWebSocket,
    fetch: (url) => {
        if (String(url).includes("/api/compile")) {
            return Promise.resolve({ ok: true, json: async () => ({ success: false, output: PAYLOAD }) });
        }
        if (String(url).includes("shell-token")) {
            return Promise.resolve({ ok: true, json: async () => ({ token: "T" }) });
        }
        return Promise.resolve({ ok: false, json: async () => ({}), text: async () => "" });
    },
});

function assertEscaped(html, where) {
    assert.ok(!/<img/i.test(html), where + ": raw <img reached innerHTML: " + html.slice(0, 120));
    assert.ok(html.includes("&lt;img"), where + ": escaped text missing");
}

(async () => {
    // 1. compile result
    await elements["run-btn"].__store.listeners.click();
    assertEscaped(elements["console-log"].__store.innerHTML, "console-log");

    // 2. real shell stream
    await get("initShellWebSocket")();
    FakeWebSocket.last.onmessage({ data: PAYLOAD });
    assertEscaped(elements["shell-output"].__store.innerHTML, "shell-output");

    // 3. escaping helper covers quotes
    const esc = get("escapeDiagnosticText");
    assert.strictEqual(esc(`<a href="x" b='y'>&`), "&lt;a href=&quot;x&quot; b=&#39;y&#39;&gt;&amp;");
    console.log("PASS test_innerhtml_escaping");
})().catch((e) => { console.error(e); process.exit(1); });
