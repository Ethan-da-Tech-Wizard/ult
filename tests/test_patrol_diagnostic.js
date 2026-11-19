// tests/test_patrol_diagnostic.js
//
// Regression test for the patrol diagnostic reading the retired `patrol.to` field: NPC_PATROLS entries use
// `route` arrays, so every patrol was reported as "out of bounds" and the Diagnostics tab was all noise.
// Run: node tests/test_patrol_diagnostic.js
"use strict";

const assert = require("assert");
const { loadApp } = require("./app_harness");

const { get } = loadApp();
const NPC_PATROLS = get("NPC_PATROLS");
const check = get("checkPatrolRoutes");

// Scenario 1: with the shipped data there must be no "out of bounds" finding (that was the bug: one per
// patrol, ~120 of them).
let items = [];
check(items);
const oob = items.filter((i) => i.title.includes("out of bounds"));
assert.strictEqual(oob.length, 0, `patrol routes wrongly reported out of bounds: ${oob.length}`);
console.log(`shipped data: ${items.length} finding(s), 0 out-of-bounds`);

// Scenario 2: a route with a point outside the map is still caught (the check was not simply disabled).
NPC_PATROLS[0]["7,7"].route = [[7, 7], [999, 7]];
items = [];
check(items);
assert.ok(items.some((i) => i.severity === "critical" && i.title.includes("Map 0 patrol target out of bounds")));

// Scenario 3: a legacy entry that only has `to` is still understood (matches getPatrolPosition's fallback).
delete NPC_PATROLS[0]["7,7"].route;
NPC_PATROLS[0]["7,7"].to = [-1, 7];
items = [];
check(items);
assert.ok(items.some((i) => i.title.includes("Map 0 patrol target out of bounds")), "legacy `to` is validated");

console.log("PASS test_patrol_diagnostic");
