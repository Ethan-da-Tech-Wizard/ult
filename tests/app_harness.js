// tests/app_harness.js
//
// Purpose: loads the whole browser script client/app.js inside a Node `vm` sandbox so regression tests can
// call its real functions (playJingle, handlePortalTransition, the patrol diagnostic...) instead of testing
// a copy of them.
//
// How it fits: required by tests/test_*.js in this folder. Run any test with `node tests/test_<name>.js`;
// each exits non-zero on failure. Not part of CI (CI only syntax-checks app.js) but cheap enough to run by
// hand before pushing.
//
// Design decisions:
//  - The DOM is replaced by a permissive Proxy: any property read returns another callable proxy, so the
//    script's start-up code (getElementById(...).addEventListener(...), canvas.getContext(...)...) runs
//    without a browser. Tests that need real behaviour install their own stubs on `sandbox` first.
//  - app.js declares everything with top-level const/let/function, which live in the script scope and are not
//    properties of the sandbox global. The loader therefore appends a tiny accessor `__get(name)` that
//    evaluates an identifier inside that scope, which is how tests read or call internal symbols.
// Known limit: timers are stubbed to never fire, so setTimeout-based transitions must be driven by tests
// capturing the callback (see `sandbox.__timers`).

"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const APP_PATH = path.join(__dirname, "..", "client", "app.js");

/**
 * Builds a Proxy that behaves like "any DOM object": callable, constructible, and every property is another
 * such proxy. Prevents ReferenceError/TypeError during app.js start-up without emulating a browser.
 *
 * @returns {Proxy} an inert stand-in for DOM nodes, canvas contexts and similar objects.
 */
function inertDom() {
    const target = function () {};
    return new Proxy(target, {
        // Symbol.toPrimitive returns "" so template literals / string concatenation on a proxy never throw.
        // `then` is undefined so `await proxy` does not wait forever treating it as a thenable.
        get: (t, key) => {
            if (key === Symbol.toPrimitive) return () => "";
            if (key === "then") return undefined;
            return inertDom();
        },
        apply: () => inertDom(),
        construct: () => inertDom(),
        set: () => true,
    });
}

/**
 * Loads client/app.js into a fresh sandbox and returns helpers to reach its internal symbols.
 *
 * @param {object} [overrides] extra globals (for example a fake AudioContext) installed BEFORE app.js runs.
 * @returns {{sandbox: object, get: function(string): *}} `get("playJingle")` evaluates that identifier in the
 *   script scope; `sandbox.__timers` collects the callbacks passed to setTimeout (never auto-fired).
 */
function loadApp(overrides) {
    const timers = [];
    const sandbox = {
        console,
        // Timers are recorded, not run: app.js schedules map transitions and reconnects that would otherwise
        // fire after the test ended or touch state the test is asserting on.
        setTimeout: (fn, ms) => { timers.push({ fn, ms }); return timers.length; },
        setInterval: () => 0,
        clearTimeout: () => {},
        clearInterval: () => {},
        requestAnimationFrame: () => 0,
        // Server calls fail fast so offline-fallback branches run deterministically.
        fetch: () => Promise.resolve({ ok: false, json: async () => ({}), text: async () => "" }),
        localStorage: { getItem: () => null, setItem() {}, removeItem() {} },
        navigator: {},
        location: { protocol: "http:", host: "127.0.0.1:8000", search: "" },
        addEventListener() {},
        __timers: timers,
        ...overrides,
    };
    sandbox.window = sandbox;
    sandbox.document = inertDom();
    vm.createContext(sandbox);
    const source = fs.readFileSync(APP_PATH, "utf8");
    // The accessor lives in the same script so its eval sees the file's top-level const/let bindings.
    vm.runInContext(source + "\n;this.__get = (name) => eval(name);", sandbox, { filename: "client/app.js" });
    return { sandbox, get: sandbox.__get };
}

module.exports = { loadApp, inertDom };
