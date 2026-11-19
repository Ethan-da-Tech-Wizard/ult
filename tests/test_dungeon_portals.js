// tests/test_dungeon_portals.js
//
// Regression test for "DUNGEON_PORTALS is not defined": handlePortalTransition() reads DUNGEON_PORTALS when
// the player steps on an overworld (map 2) portal or leaves a dungeon, but commit 2607b58 introduced those
// reads without any definition, so both branches threw ReferenceError. Run: node tests/test_dungeon_portals.js
"use strict";

const assert = require("assert");
const { loadApp } = require("./app_harness");

const { sandbox, get } = loadApp();

// Scenario 1: the table exists and covers every dungeon chapter (2..21; chapters 0/1 are cabin/Alexandria).
const portals = get("DUNGEON_PORTALS");
const MAP_GRIDS = get("MAP_GRIDS");
const ids = Object.keys(portals).map(Number).sort((a, b) => a - b);
assert.deepStrictEqual(ids, Array.from({ length: 20 }, (_, i) => i + 2));

// Scenario 2: every portal is a real portal tile (6) on the overworld grid, positions are unique, and the
// tile the player is pushed back onto (y + 1) is walkable grass.
const seen = new Set();
for (const id of ids) {
    const { x, y } = portals[id];
    assert.strictEqual(MAP_GRIDS[2][y][x], 6, `chapter ${id} portal tile at ${x},${y}`);
    assert.ok(!seen.has(`${x},${y}`), "duplicate portal position");
    seen.add(`${x},${y}`);
    assert.strictEqual(MAP_GRIDS[2][y + 1][x], 0, `tile below portal ${id} must be grass`);
}
assert.strictEqual(MAP_GRIDS[2][15][13], 6, "Alexandria return portal at (13,15)");

// Scenario 3: the whole set is reachable on foot from where Alexandria drops the player, (13,16).
const walk = (t) => t !== 1 && t !== 5;
const grid = MAP_GRIDS[2];
const queue = [[13, 16]];
const reached = new Set(["13,16"]);
while (queue.length) {
    const [cx, cy] = queue.shift();
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = cx + dx, ny = cy + dy, k = `${nx},${ny}`;
        if (ny < 0 || nx < 0 || ny >= grid.length || nx >= grid[0].length || reached.has(k)) continue;
        if (!walk(grid[ny][nx])) continue;
        reached.add(k);
        queue.push([nx, ny]);
    }
}
for (const id of ids) {
    const { x, y } = portals[id];
    assert.ok(reached.has(`${x},${y}`), `portal for chapter ${id} unreachable from the overworld entry`);
}

// Scenario 4: stepping on an unlocked portal enters that chapter's dungeon map (chapter N -> map N+1).
const player = get("player");
player.currentMapId = 2;
player.unlockedChapters = [0, 1, 2, 3];
get("handlePortalTransition")(portals[3].x, portals[3].y);
sandbox.__timers.forEach((t) => t.fn());
assert.strictEqual(player.currentMapId, 4);
assert.strictEqual(player.currentChapter, 3);

// Scenario 5: a locked chapter pushes the player back below the portal instead of entering.
player.currentMapId = 2;
player.unlockedChapters = [0, 1];
get("handlePortalTransition")(portals[9].x, portals[9].y);
assert.strictEqual(player.currentMapId, 2);
assert.deepStrictEqual([player.x, player.y], [portals[9].x, portals[9].y + 1]);

// Scenario 6: leaving a dungeon through its exit (7,11) lands just below that dungeon's overworld portal.
player.currentMapId = 4;
player.currentChapter = 3;
player.unlockedChapters = [0, 1, 2, 3, 4];
sandbox.__timers.length = 0;
get("handlePortalTransition")(7, 11);
sandbox.__timers.forEach((t) => t.fn());
assert.strictEqual(player.currentMapId, 2);
assert.deepStrictEqual([player.x, player.y], [portals[3].x, portals[3].y + 1]);

console.log("PASS test_dungeon_portals");
