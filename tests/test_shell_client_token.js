// tests/test_shell_client_token.js
//
// Pins the browser side of the /ws/shell access control: initShellWebSocket() must fetch the per-run token
// from /api/shell-token and send it as the FIRST frame after the socket opens, and must not reconnect after
// the server refuses with close code 1008. Run: node tests/test_shell_client_token.js
"use strict";

const assert = require("assert");
const { loadApp } = require("./app_harness");

const sockets = [];
/** Fake browser WebSocket that records what the client sends and lets the test trigger events. */
class FakeWebSocket {
    constructor(url) { this.url = url; this.sent = []; this.readyState = 0; sockets.push(this); }
    send(data) { this.sent.push(data); }
    close() {}
}
FakeWebSocket.OPEN = 1;

const fetchCalls = [];
const overrides = {
    WebSocket: FakeWebSocket,
    fetch: (url, opts) => {
        fetchCalls.push(url);
        if (url === "/api/shell-token") {
            return Promise.resolve({ ok: true, json: async () => ({ token: "TEST-TOKEN" }) });
        }
        return Promise.resolve({ ok: false, json: async () => ({}), text: async () => "" });
    },
};
const { sandbox, get } = loadApp(overrides);

(async () => {
    sandbox.__timers.length = 0;
    await get("initShellWebSocket")();

    // Scenario 1: the token is requested from the server before any socket is opened.
    assert.ok(fetchCalls.includes("/api/shell-token"), "token must be fetched");
    assert.strictEqual(sockets.length, 1);
    assert.ok(sockets[0].url.endsWith("/ws/shell"));
    assert.ok(!sockets[0].url.includes("TEST-TOKEN"), "token must not be put in the URL");

    // Scenario 2: on open, the very first frame is the token.
    sockets[0].onopen();
    assert.deepStrictEqual(sockets[0].sent, ["TEST-TOKEN"]);

    // Scenario 3: a second call while connected does not open a second shell.
    await get("initShellWebSocket")();
    assert.strictEqual(sockets.length, 1);

    // Scenario 4: a policy close (1008) does not schedule a reconnect...
    sandbox.__timers.length = 0;
    sockets[0].onclose({ code: 1008 });
    assert.strictEqual(sandbox.__timers.length, 0, "1008 must not auto-reconnect");

    // Scenario 5: ...but an ordinary drop (1006) still does, after 3 s.
    await get("initShellWebSocket")();
    assert.strictEqual(sockets.length, 2);
    sandbox.__timers.length = 0;
    sockets[1].onclose({ code: 1006 });
    assert.strictEqual(sandbox.__timers.length, 1);
    assert.strictEqual(sandbox.__timers[0].ms, 3000);

    console.log("PASS test_shell_client_token");
})().catch((e) => { console.error(e); process.exit(1); });
