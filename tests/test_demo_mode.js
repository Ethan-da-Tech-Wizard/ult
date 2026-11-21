// Fix 7: when the server is unreachable the editor's old "offline simulator" auto-passed the chapter, paid
// rewards and saved. It must now be a clearly labelled DEMO that changes no progress and writes no save.
// Also: a non-OK server answer (for example the 503 "sandbox unavailable") must be shown, not swallowed.
// Run: node tests/test_demo_mode.js
"use strict";
const assert = require("assert");
const { loadApp } = require("./app_harness");
const { makeDocument } = require("./dom_fake");

async function scenario(fetchImpl) {
    const { document, elements } = makeDocument();
    const calls = [];
    const { get } = loadApp({
        document,
        fetch: (url, opts) => { calls.push({ url: String(url), method: (opts && opts.method) || "GET" }); return fetchImpl(url, opts); },
    });
    const player = get("player");
    const before = { unlocked: JSON.stringify(player.unlockedChapters), gold: player.gold, tokens: player.tokens };
    calls.length = 0;
    await elements["run-btn"].__store.listeners.click();
    return { player, before, calls, log: elements["console-log"].__store.innerHTML };
}

(async () => {
    // A: server offline (fetch rejects)
    const a = await scenario(() => Promise.reject(new Error("offline")));
    assert.ok(/DEMO/.test(a.log), "log must say DEMO: " + a.log);
    assert.strictEqual(JSON.stringify(a.player.unlockedChapters), a.before.unlocked, "no chapter unlocked");
    assert.strictEqual(a.player.gold, a.before.gold, "no gold");
    assert.strictEqual(a.player.tokens, a.before.tokens, "no tokens");
    assert.ok(!a.calls.some((c) => c.url.includes("/api/save") && c.method === "POST"), "no save POST");
    assert.ok(!/Verification PASS|Fallback verification passed/.test(a.log), "must not claim a pass");

    // B: server answers 503 with an explanation
    const b = await scenario(() => Promise.resolve({ ok: false, status: 503, json: async () => ({ detail: "Code sandbox unavailable: <b>x</b>" }) }));
    assert.ok(b.log.includes("Code sandbox unavailable"), "503 detail shown: " + b.log);
    assert.ok(!b.log.includes("<b>x</b>"), "503 detail escaped");
    assert.strictEqual(JSON.stringify(b.player.unlockedChapters), b.before.unlocked);
    console.log("PASS test_demo_mode");
})().catch((e) => { console.error(e); process.exit(1); });
