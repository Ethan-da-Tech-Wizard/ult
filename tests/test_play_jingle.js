// tests/test_play_jingle.js
//
// Regression test for "playJingle is not defined": winCombat() and the compile-pass handler call
// playJingle(...) but commit 2607b58 deleted the function, so a ReferenceError aborted winCombat before gold,
// flags, saving and endCombat ran. Run: node tests/test_play_jingle.js
"use strict";

const assert = require("assert");
const { loadApp } = require("./app_harness");

/** Fake Web Audio context that counts oscillators started and records their frequencies. */
function makeFakeAudio() {
    const started = [];
    class FakeAudioContext {
        constructor() { this.currentTime = 0; this.destination = {}; }
        createOscillator() {
            const osc = {
                type: "", frequency: { setValueAtTime: (f) => { osc.freq = f; } },
                connect() {}, start: () => started.push(osc.freq), stop() {},
            };
            return osc;
        }
        createGain() {
            return { gain: { setValueAtTime() {}, exponentialRampToValueAtTime() {} }, connect() {} };
        }
    }
    return { FakeAudioContext, started };
}

const { FakeAudioContext, started } = makeFakeAudio();
const { get } = loadApp({ AudioContext: FakeAudioContext });

// Scenario 1: the function exists at all (this was the actual regression).
assert.strictEqual(typeof get("playJingle"), "function", "playJingle must be defined");
const playJingle = get("playJingle");

// Scenario 2: before the user gesture creates the AudioContext, it must be a silent no-op, not a throw.
assert.doesNotThrow(() => playJingle("victory"));
assert.strictEqual(started.length, 0, "no audio context yet -> no notes");

// Scenario 3: each jingle kind used by the callers plays its own number of notes.
get("initAudio")();
const expected = { victory: 4, levelup: 5, fanfare: 5 };
for (const [kind, count] of Object.entries(expected)) {
    started.length = 0;
    playJingle(kind);
    assert.strictEqual(started.length, count, `${kind} should play ${count} notes`);
}

// Scenario 4: an unknown kind falls back to the victory melody instead of throwing on undefined.forEach.
started.length = 0;
playJingle("no-such-jingle");
assert.strictEqual(started.length, 4);

// Scenario 5: the mute setting silences it.
get("gameSettings").muted = true;
started.length = 0;
playJingle("victory");
assert.strictEqual(started.length, 0, "muted -> silent");

console.log("PASS test_play_jingle");
