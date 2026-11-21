// tests/dom_fake.js: a document stand-in whose getElementById returns recording elements (innerHTML, value,
// textContent, listeners), everything else stays an inert proxy. Used by the XSS and demo-mode tests.
"use strict";
const { inertDom } = require("./app_harness");

function makeElement() {
    const store = { innerHTML: "", textContent: "", value: "", listeners: {} };
    return new Proxy(inertDom(), {
        get(target, key) {
            if (key === "addEventListener") return (type, fn) => { store.listeners[type] = fn; };
            if (key === "__store") return store;
            if (key in store) return store[key];
            return target[key];
        },
        set(target, key, value) { store[key] = value; return true; },
    });
}

function makeDocument() {
    const elements = {};
    const base = inertDom();
    return {
        elements,
        document: new Proxy(base, {
            get(target, key) {
                if (key === "getElementById") return (id) => (elements[id] = elements[id] || makeElement());
                return target[key];
            },
            set() { return true; },
        }),
    };
}

module.exports = { makeDocument };
