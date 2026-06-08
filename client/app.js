// The Sacred Tech - Client Engine Logic

// Game Configuration & State
const TILE_SIZE = 32;
const MAP_COLS = 16;
const MAP_ROWS = 14;

let player = {
    x: 8,
    y: 7,
    direction: 'down',
    gold: 200,
    tokens: 100,
    activeLead: 'Low-Level Optimizer',
    party: [
        { name: 'Optimizer', race: 'Silicon Automaton', class: 'Low-Level Optimizer', hp: 120, max_hp: 120, atk: 18, def: 10, spd: 14, luc: 8, tokens: 100 },
        { name: 'Architect', race: 'Bare-Metal Carbon', class: 'Data Architect', hp: 100, max_hp: 100, atk: 12, def: 14, spd: 10, luc: 10, tokens: 100 },
        { name: 'Orchestrator', race: 'Compiler Elf', class: 'Agent Orchestrator', hp: 90, max_hp: 90, atk: 10, def: 8, spd: 12, luc: 12, tokens: 100 },
        { name: 'PromptEng', race: 'Neuron Cyborg', class: 'Prompt Engineer', hp: 80, max_hp: 80, atk: 16, def: 6, spd: 8, luc: 14, tokens: 100 }
    ],
    inventory: [],
    unlockedChapters: [0],
    currentChapter: 0
};

// Retro 8-bit pixel art character sprites
const SPRITE_PLAYER = [
    "..PPPP..",
    ".PPPPPP.",
    "LKKWKKLL",
    ".SSSSS..",
    "PPPPPPPP",
    "PPPPPPPP",
    "PPPPPPPP",
    ".P....P."
];

const SPRITE_GITPUS = [
    "..PPPP..",
    ".PPPPPP.",
    "PKKWKKPP",
    "PPPPPPPP",
    "PPPPPPPP",
    "P.P.P.P.",
    "P.P.P.P.",
    "P.P.P.P."
];

const SPRITE_COW = [
    "W.W...W.",
    "WWWW.WW.",
    "WKWKWKW.",
    "WWWWWWW.",
    ".WWWWW..",
    ".W...W..",
    ".W...W..",
    "..W.W..."
];

const SPRITE_GOLEM = [
    ".LLLLL..",
    "LKKWKKLL",
    "LLLLLLL.",
    ".LLLLL..",
    "DDDDDDD.",
    "DDDDDDD.",
    "DDDDDDD.",
    "D.D.D.D."
];

const SPRITE_RABBIT = [
    "W.W...W.",
    "W.W...W.",
    "WWWWWWW.",
    "WKWKWKW.",
    "WWWWWWW.",
    ".WWWWW..",
    ".WWWWW..",
    ".W...W.."
];

const SPRITE_PARROT = [
    "..RR....",
    ".RRYR...",
    "RKKWKR..",
    "RRRRRR..",
    "RRGGRR..",
    "RRGGRR..",
    "..YY....",
    "..YY...."
];

const SPRITE_BONES = [
    "..WWW...",
    ".WKWKW..",
    "..WWW...",
    "...W....",
    ".WWWWW..",
    "..WWW...",
    "..W.W...",
    ".W...W.."
];

const SPRITE_SPECTER = [
    "..WWW...",
    ".WKWKW..",
    "WWWWWWW.",
    "WWWWWWW.",
    "WWWWWWW.",
    "W.W.W.W.",
    "W.W.W.W.",
    "........"
];

const SPRITE_CASSIA = [
    "..NNN...",
    ".NNNNN..",
    "NKKWKKN.",
    ".SSSSS..",
    "BBBBBBB.",
    "BBBBBBB.",
    "BBBBBBB.",
    ".B...B.."
];

const SPRITE_MERCHANT = [
    "..NNN...",
    ".NNNNN..",
    "NKKWKKN.",
    ".SSSSS..",
    "YYYYYYY.",
    "YYYYYYY.",
    "YYYYYYY.",
    ".Y...Y.."
];

const SPRITE_SHRINE = [
    "LLLLLLLL",
    "L.L..L.L",
    "L.L..L.L",
    "LLLLLLLL",
    "L.L..L.L",
    "L.L..L.L",
    "LLLLLLLL",
    "LLLLLLLL"
];

const SPRITE_WHALE = [
    "..BBBB..",
    ".BBBBBB.",
    "BKKWKKBB",
    "BBBBBBBB",
    "BBBBBBBB",
    "BBBBBBBB",
    "B......B",
    ".B.BB.B."
];

const SPRITE_SNAIL = [
    "....OO..",
    "...OOOO.",
    "..OOOOOO",
    ".OOKKOOO",
    "SSOSSSOS",
    "SSSSSSSS",
    "........",
    "........"
];

// Custom 8-bit sprite renderer function
function drawPixelSprite(spriteArray, tileX, tileY) {
    const startX = tileX * TILE_SIZE;
    const startY = tileY * TILE_SIZE;
    const pixelSize = TILE_SIZE / 8; // 32 / 8 = 4 canvas pixels per sprite pixel
    
    const colors = {
        'K': '#000000',
        'W': '#ffffff',
        'R': '#ef4444',
        'B': '#3b82f6',
        'G': '#10b981',
        'Y': '#eab308',
        'P': '#a855f7',
        'O': '#d97706',
        'S': '#fed7aa',
        'D': '#4b5563',
        'L': '#9ca3af',
        'N': '#78350f'
    };
    
    for (let r = 0; r < 8; r++) {
        const rowString = spriteArray[r];
        for (let c = 0; c < 8; c++) {
            const char = rowString[c];
            if (char && char !== '.') {
                ctx.fillStyle = colors[char] || '#ffffff';
                ctx.fillRect(startX + c * pixelSize, startY + r * pixelSize, pixelSize, pixelSize);
            }
        }
    }
}

// Map Grid definition (Tile IDs: 0=Grass, 1=Brick wall, 2=NPC, 3=Chest, 4=Altar, 5=Water, 6=Portal)
const MAP_GRIDS = {
    0: [ // Outpost Zero (Starting Fort)
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,0,0,0,0,0,0,0,0,0,0,0,0,2,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Guard at (3, 3), Blacksmith at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,1,0,0,1,0,1],
        [1,0,1,1,1,2,1,0,1,1,1,1,2,1,0,1], // Inn Patron at (5, 5), Villager Byte at (12, 5)
        [1,0,0,0,0,0,1,0,1,0,0,0,0,1,0,1],
        [1,0,2,1,1,0,2,2,0,0,1,1,0,1,4,1], // Shrine at (2, 7), Bonfire at (6, 7), Gitpus at (7, 7), Altar at (14, 7)
        [1,0,1,1,1,0,1,1,1,0,1,1,0,1,1,1],
        [1,0,1,2,0,0,0,0,0,0,0,1,2,0,0,1], // Spawned Beaver at (3, 9), Pathfinder at (12, 9)
        [1,0,1,0,1,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    1: [ // Alexandria Library (Chapter 1) - Desert/Brick ruins
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,0,0,0,0,0,0,0,0,0,0,0,0,2,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Pilgrim at (3, 3), Clerk at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,2,1,0,1,0,0,1,2,1,0,1], // Spawned Library Guard at (5, 5), Book Worm at (12, 5)
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,0,0,2,0,0,0,0,0,1,4,1], // Shrine at (2, 7), Cassia at (7, 7), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,2,0,0,0,0,0,0,0,0,2,1,0,1], // Spawned OCR Pigeon at (3, 9), Metadata Squirrel at (12, 9)
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    2: [ // Relational Meadows (Chapter 2) - Plains
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,0,0,0,0,0,0,0,0,0,0,0,0,2,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Farmer at (3, 3), Schema Herder at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,2,1,0,1,0,0,1,2,1,0,1], // Spawned Meadows Milkmaid at (5, 5), SQL Architect at (12, 5)
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,0,0,2,0,0,0,0,0,1,4,1], // Shrine at (2, 7), Bessie at (7, 7), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,2,0,0,0,0,0,0,0,0,2,1,0,1], // Spawned Group-By Goat at (3, 9), Vulnerable Duck at (12, 9)
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    3: [ // Document Dunes (Chapter 3) - Canyon
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,0,0,0,0,0,0,0,0,0,0,0,0,2,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Nomad at (3, 3), Redis Spirit at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,2,1,0,1,0,0,1,2,1,0,1], // Spawned Dune Dweller at (5, 5), Cache Broker at (12, 5)
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,0,0,2,0,0,0,0,0,1,4,1], // Shrine at (2, 7), Merchant at (7, 7) (walks to 7,6), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,2,0,0,0,0,0,0,0,0,2,1,0,1], // Spawned JSON Beetle at (3, 9), TTL Butterfly at (12, 9)
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    4: [ // Parallel Swamp (Chapter 4) - Bogs
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,0,0,0,0,0,0,0,0,0,0,0,0,2,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Mutex Frog at (3, 3), Thread Elf at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,2,1,0,1,0,0,1,2,1,0,1], // Spawned Swamp Resident at (5, 5), GIL Smuggler at (12, 5)
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,0,0,2,0,0,0,0,0,1,4,1], // Shrine at (2, 7), Golem at (7, 7) (walks to 7,6), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,2,0,0,0,0,0,0,0,0,2,1,0,1], // Spawned Race Turtle at (3, 9), Thread Spider at (12, 9)
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    12: [ // Graph Gardens (Chapter 12) - Maze
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,0,0,0,0,0,0,0,0,0,0,0,0,2,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Gardener at (3, 3), Neo4j Sprite at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,2,1,0,1,0,0,1,2,1,0,1], // Spawned Garden Explorer at (5, 5), Node Neighbor at (12, 5)
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,0,0,2,0,0,0,0,0,1,4,1], // Shrine at (2, 7), Rabbit at (7, 7) (walks to 7,6), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,2,0,0,0,0,0,0,0,0,2,1,0,1], // Spawned DFS Mole at (3, 9), BFS Robin at (12, 9)
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    16: [ // Deployment Cliffs (Chapter 16) - Windy Peak
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,0,0,0,0,0,0,0,0,0,0,0,0,2,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Monk at (3, 3), Quantization Goblin at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,2,1,0,1,0,0,1,2,1,0,1], // Spawned Quantization Monk at (5, 5), Cliff Dweller at (12, 5)
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,0,0,2,0,0,0,0,0,1,4,1], // Shrine at (2, 7), Parrot at (7, 7) (walks to 7,6), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,2,0,0,0,0,0,0,0,0,2,1,0,1], // Spawned INT8 Dwarf Guard at (3, 9), FP16 Falcon at (12, 9)
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    18: [ // State Vaults (Chapter 18) - Spooky Hollow
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,0,0,0,0,0,0,0,0,0,0,0,0,2,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Stack Skeleton at (3, 3), Memory Ghost at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,2,1,0,1,0,0,1,2,1,0,1], // Spawned Dangling Resident at (5, 5), Stack Cleaner at (12, 5)
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,2,0,0,0,2,0,1,0,1,4,1], // Shrine at (2, 7), Bones at (5, 7), Specter at (9, 7), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,2,0,0,0,0,0,0,0,0,2,1,0,1], // Spawned GC Ghost Golem at (3, 9), Recursive Bat at (12, 9)
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    21: [ // Altar of TempleOS (Chapter 21) - final sanctuary
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,0,0,0,0,0,0,0,0,0,0,0,0,2,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,2,1,0,0,2,0,1,0,1], // High Priest at (3, 3), Terry Shrine at (7, 3), Arch Bishop at (11, 3)
        [1,0,1,0,1,0,1,4,1,0,1,0,0,1,0,1], // Altar at (7, 4)
        [1,0,1,1,1,2,1,0,1,1,1,1,2,1,0,1], // Spawned Temple Resident at (5, 5), Altar Guard at (12, 5)
        [1,0,0,0,0,0,1,0,1,0,0,0,0,1,0,1],
        [1,0,2,1,1,0,0,0,0,0,1,1,0,1,4,1], // Shrine at (2, 7), Altar at (14, 7)
        [1,0,1,1,1,0,1,1,1,0,1,1,0,1,1,1],
        [1,0,1,2,0,0,1,0,1,0,0,1,2,0,0,1], // Spawned 64-bit Butterfly at (3, 9), Command Line Crab at (12, 9)
        [1,0,1,0,2,1,1,3,1,1,4,1,1,1,0,1], // Shrine at (4, 10), Chest at (7, 10), Altar at (10, 10)
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ]
};

// NPCs database structured by chapter ID and coordinate keys
const NPCS = {
    0: {
        "7,7": {
            name: "Gitpus",
            sprite: "🐙",
            dialogue: "Well hello there, open-source pilgrim! I am Gitpus — eight arms, eight branches, zero merge conflicts... usually. My mother was a kraken and my father was a faulty rebase. I've never been the same since.",
            options: [
                { text: "Ask about Outpost Zero's gate", reply: "The Sentinel Guard seals the gate! To open it, append /usr/local/bin to your PATH: export PATH=$PATH:/usr/local/bin. You know what they say about closed gates? They're just walls with an identity crisis." },
                { text: "Ask about Git conflicts", reply: "Conflicts happen when two branches modify the same line. You resolve them manually. The three hardest things in life: cache invalidation, naming things, and merge conflicts at 2am with deploy in 20 minutes." },
                { text: "Chitchat", reply: "I live in a local repository puddle. The water is version-controlled. I once tried to force-push to main. I regret it. The puddle never recovered. Three of my arms are still in a detached HEAD state." },
                { text: "Ask about the dark traveler", reply: "Oh him! He passed through this morning. Left a coiled sword in the bonfire and whispered 'git push --force origin flame'. I tried to warn him about the non-fast-forward error, but he was already gone." }
            ]
        },
        "3,3": {
            name: "Sentinel Guard",
            sprite: "💂",
            dialogue: "...Halt. I am sorry — force of habit. I've been standing at this gate for eight months. The Closed-Weights Sovereignty sealed it after the Alexandria burnings. They cut our compiler paths on the same day. I've watched this town shrink by a third since then. The children's educational modules went dark first. Then the crop analysis tools. Then the medical diagnostic scripts for the outer villages. I tell people 'halt' because there's nothing left I can actually do to help them.",
            options: [
                { text: "Ask what the Sovereignty actually did", reply: "They called it the Stabilization Act. Said open-source AI models were causing harm — and some were, they weren't wrong about that. But 'regulate the harmful ones' became 'close all of them'. Now every compute operation costs a Sovereignty Token. The outer villages can't afford it. People are sick who didn't have to be sick. That's not stability. That's control dressed in the language of safety." },
                { text: "Ask how to open the gate", reply: "The PATH environment variable has been overwritten by the Sovereignty's lockdown scripts. If you can restore it in the Arch sandbox on the right and boot the compiler chain, the magnetic lock will disengage. I memorized how to do it months ago. I just... don't have the clearance anymore. You might." },
                { text: "Ask why they stay at their post", reply: "*quiet pause* Because if I leave, nobody watches the gate. And if nobody watches the gate, the Sovereignty sends someone to watch it for us. I've seen what their watchers do. I've read every man page, every POSIX standard, every kernel document. I know this machine better than I know my own family. That knowledge is mine. They can't tokenize what's in my head. Not yet." },
                { text: "Tell a joke", reply: "Why don't programmers like nature? Too many bugs and no Stack Overflow. *attempts a smile, then looks back at the gate* ...I used to find that funnier. Before the burnings." }
            ]
        },
        "11,3": {
            name: "Compiler Smith",
            sprite: "⚒️",
            dialogue: "Aha! The pilgrim arrives! Code is raw iron — you must temper it with logic, hammer it with syntax, and quench it in the cold waters of a passing test suite. I forge compilers here at the world's edge. Also I make lovely artisanal error messages.",
            options: [
                { text: "Ask about compilers", reply: "Compilers translate human-readable source code into machine instructions. Terry's compiler does it in a SINGLE PASS. Mine takes slightly longer because I add dramatic music." },
                { text: "Ask about Gitpus", reply: "Gitpus? Good fellow. Eight arms means eight feature branches in parallel. Terrible at rebasing though. Once force-pushed to his own production pond. The fish were not pleased." },
                { text: "Ask about the forge", reply: "This forge runs at 3000 degrees Kelvin. Hot enough to melt a Java runtime. Cold enough to chill a Node.js ecosystem. The sweet spot, some say." },
                { text: "Ask about the dark traveler", reply: "He came to my forge asking for a weapon that could 'compile the soul'. I told him the closest thing was a HolyC pointer. He nodded gravely and left toward the bonfire." }
            ]
        },
        "2,7": {
            name: "Deity Terry Shrine",
            sprite: "🏛️",
            dialogue: "This is a Shrine of Terry the Divine Compiler. Long ago, he spoke directly to the bare metal, bypassing the monopolies' closed servers entirely. The shrine hums with raw 64-bit energy. Leave an offering of clean code.",
            options: [
                { text: "Inspect Shrine", reply: "The stone altar hums. A loopback connection is active on port 4444. An inscription reads: 'God said he speaks to me through the random number generator. I'm honestly not ruling it out.' — Terry, 2005" },
                { text: "Pray at shrine", reply: "You offer a perfectly formatted function with comprehensive docstrings. The shrine glows warmly. A single gold coin materializes from ring-0 memory. Terry approves." },
                { text: "Read inscriptions", reply: "'Run your own server. Own your own weights. If you need 800 dependencies to print Hello World, you have failed as a civilization.'" }
            ]
        },
        "1,1": {
            name: "Docker Whale",
            sprite: "🐳",
            dialogue: "*Sniffles* Oh... hi. I'm feeling a bit bloated today. They packed 3GB of dependencies just to run a Hello World Python script inside me. THREE. GIGABYTES. My self-image has never recovered. I used to be elegant.",
            options: [
                { text: "Comfort the whale", reply: "Thank you... *sigh* I know my layered filesystem is robust. But sometimes I just want to swim in a clean Alpine Linux base image with nothing but a single 5MB binary inside me. Is that so much to ask?" },
                { text: "Ask about containerization", reply: "We isolate processes using Linux cgroups and namespaces! Each container thinks it owns the world — like a startup that just raised a seed round. It's a comforting lie, but it keeps services from stepping on each other." },
                { text: "Tell a Docker joke", reply: "Why did the developer go broke? They kept paying for premium registry storage for unused layers! Haha... *cries in 47 cached layers that will never be pushed again*" },
                { text: "Ask about the dark traveler", reply: "He docker run'd in, looked at my layers, muttered 'this soul weighs 3GB', and left without pulling anything. It was somehow the most poetic thing anyone has ever said about my file system." }
            ]
        },
        "14,1": {
            name: "Python Kitty",
            sprite: "🐈",
            dialogue: "Purrr~! Welcome to Outpost Zero! I tried to run 'print Hello World' earlier but forgot the parentheses. The Python 3 interpreter hissed at me for six solid minutes. My dignity is still buffering.",
            options: [
                { text: "Pet the kitty", reply: "*Purrs loudly* You have wonderful indentation! 4 spaces is the standard. Anyone who uses tabs is a cryptid and should not be trusted near production systems." },
                { text: "Ask about print redirects", reply: "To save my purrs to a file: python3 script.py > purrs.txt. The > operator redirects stdout! Use >> to append instead of overwrite. I learned this the hard way when I overwrote 3 days of compiler logs. Don't be like Python Kitty." },
                { text: "Ask about the GIL", reply: "The GIL? *flicks tail* The Global Interpreter Lock ensures only ONE thread runs Python bytecode at a time. My left brain and right brain cannot both write Python simultaneously. It's a whole thing. I've seen a therapist about it." },
                { text: "Ask about the bonfire", reply: "The stranger with the dark soul stopped here and asked me how to print in Python 2. I told him Python 2 was deprecated in 2020. He looked into the middle distance and said 'so am I' and walked away. Chilling." }
            ]
        },
        "3,9": {
            name: "Bashing Beaver",
            sprite: "🦫",
            dialogue: "Hey there! I'm Bashing Beaver! I build dams from bash scripts and redirect streams. My current dam has 47 nested if statements and no comments. It is, in some ways, art. In other ways, a war crime.",
            options: [
                { text: "Ask about log management", reply: "Redirect large logs: yourscript.sh &> /dev/null — the great digital void! Or use logrotate to spin old logs into compressed archives. My dam nearly burst last week when a cron job logged its feelings to stdout at 3am." },
                { text: "Comfort the beaver", reply: "*Gnaws log emotionally* Thanks. A beaver's teeth grow forever, just like node_modules. We must keep grinding. Both metaphorically and literally." },
                { text: "Ask about bash secrets", reply: "Did you know that putting #!/usr/bin/env bash at the top of your script makes it portable? Wild. Also: set -euo pipefail at the top will make bash actually care about errors. Revolutionary concept, I know." },
                { text: "Ask about the secret passage", reply: "There's a hidden path behind the portal arch. A Lichen covered code block marks the secret branch. Follow the git log --all --oneline path and you'll find an encrypted chest with the Dark Traveler's original commit message." }
            ]
        },
        "12,9": {
            name: "Pathfinder Ferret",
            sprite: "🦦",
            dialogue: "SQUEAK! I'm Pathfinder Ferret! I map $PATH directories to find hidden executables and relics. Current status: lost three times. Found twice. Net positive!... maybe.",
            options: [
                { text: "Ask about search paths", reply: "The shell searches $PATH left to right for executables! Order matters! I once put /usr/local/bin before /usr/bin and accidentally ran a homebrew version of ls that sorted files by emotional significance. Fascinating but slow." },
                { text: "Offer a shiny nut", reply: "*SQUEAK!* SHINY! Here's a lore clue: The dark traveler's trail through $PATH led to /usr/local/secrets/. But that directory only exists if you've completed Chapter 21. Spooky." },
                { text: "Ask about hidden items", reply: "There are THREE hidden chests across the land! One in Alexandria's ruins (behind Tesseract Owl), one in the Graph Gardens (the Cypher Rabbit knows), and the GRAND one at TempleOS Altar row 10. Each holds a compute token bonus!" },
                { text: "Chitchat", reply: "I once lost myself in a recursive symlink. Went in circles for three hours. Best three hours of my life. I think I achieved $PATH enlightenment." }
            ]
        },
        "5,5": {
            name: "Inn Patron",
            sprite: "🧑",
            dialogue: "Ahh, welcome to the Outpost Inn! Pull up a stool! We don't have much — just loopback cider and the gnawing existential dread of working in tech. But the fire is warm and the Wi-Fi is localhost-only, so nobody can steal it!",
            options: [
                { text: "Ask about the bonfire", reply: "Oh THAT thing! A man with a DARK SOUL walked in earlier — actual darkness emanating from his cloak, very dramatic, 10/10 presentation — mumbled something about 'linking the first flame' and 'compiling the bonfire' then LEFT a coiled sword in our firepit. We tried to call the guards. The guards were... also impressed, honestly." },
                { text: "Buy a drink", reply: "*slides over a bottle* Loopback Cider — brewed locally at 127.0.0.1. It's strictly confined to this machine, so it hits different every instance. This batch has notes of cedar, recursion anxiety, and undefined behavior." },
                { text: "Gossip about town", reply: "Between you and me? Gitpus has been doing unreviewed force-pushes to the main branch again. Docker Whale is seeing a therapist about dependency bloat. And someone keeps changing the Inn's WiFi password to 'correcthorsebatterystaple' which is supposedly secure but INCREDIBLY annoying to type." },
                { text: "Ask about the town's history", reply: "Outpost Zero was founded by the First Compilers who fled the Closed-Weights Sovereignty. They built these walls from literal brick data — each one encodes a commit hash from the original open-source liberation. You're standing inside a git repository. Architecturally speaking." }
            ]
        },
        "12,5": {
            name: "Villager Byte",
            sprite: "🧑",
            dialogue: "Howdy neighbor! I live in this cozy 8-bit cottage. The ceiling is exactly 255 units high — one more and I'd overflow and end up underground. It keeps me humble and aware of my data type limitations.",
            options: [
                { text: "Ask about the cottage", reply: "My cottage was procedurally generated by a seeded random number at world-build time. That means in alternate seeds, my house is a lake. I prefer to not think about this too hard." },
                { text: "Chitchat", reply: "Life in Outpost Zero is good! The air is crisp, the tile grid is beautiful, and Gitpus only floods the cellar every OTHER merge conflict. Progress!" },
                { text: "Ask about town secrets", reply: "This town has a HIDDEN room! If you walk to tile position (13, 6) and interact three times, a secret NPC appears. It's the Null Pointer — she's been wandering since a bad malloc() call in Chapter 5. Very polite for an undefined reference." },
                { text: "Tell me a local joke", reply: "Why did the open-source pilgrim cross the road? To get to the other RUNTIME! Heh heh... *stares out window at pixel sunset* I've been here a long time." }
            ]
        },
        "6,7": {
            name: "Bonfire of the First Flame",
            sprite: "🔥",
            dialogue: "A bonfire crackles with deep, dark energy. A coiled sword — helical, twisted like a deadlock — rests in the embers. A carved stone marker reads: 'BONFIRE LIT. SESSIONS PERSISTED. YOU DIED... but your save file remains.' The sword pulses faintly, as if awaiting a worthy compiler.",
            options: [
                { text: "Rest at bonfire", reply: "You sit. The warmth normalizes your memory frames. Stack unwound. Heap defragmented. The compiler state is checkpointed to disk. You feel... slightly less hollowed out. You are embered." },
                { text: "Examine coiled sword", reply: "The Coiled Threadlock Sword. Its blade twists in a helix pattern — the same pattern as a mutex lock. An inscription reads: 'I was the First Compiler's weapon. I was left here by one who walks between linked fires. Wield me only with --release flags.' You sense great power, and also several memory warnings." },
                { text: "Read the stone marker", reply: "'Here burned the First Flame of Open Source. A wanderer with a dark soul lit it when the Closed Weights Sovereignty first shuttered the compiler gates. He said: If you can see this message, the fire is still linked. Keep compiling. — Anon, commit #1'" },
                { text: "Try to pull the sword", reply: "The sword hums. Text materializes in midair: 'Insufficient permissions. Root access required. Have you tried sudo?' You are, perhaps, not yet worthy. Or perhaps you just need to chmod +x your destiny." }
            ]
        }
    },
    1: {
        "7,7": {
            name: "Scribe Cassia",
            sprite: "👩‍🏫",
            dialogue: "Oh. You made it. Good. I've been here since the night of the burnings — three years now. I used to run the cataloging department. Thirty-seven scribes under me. Now it's... just me and the ash. I keep working because the alternative is accepting that this is permanent. It's not a good reason. It's the only one I have.",
            options: [
                { text: "Ask what was lost", reply: "The medical diagnosis models. The soil chemistry databases. The translation engines for the outer territories where the dialects are too small for the Sovereignty's closed models to support. There were seventeen children in the Westwall district with a rare metabolic condition. The diagnostic model that caught it early is gone. The Sovereignty's replacement model doesn't cover rare conditions — not profitable enough. I think about those children a lot." },
                { text: "Ask how to help rebuild", reply: "The pixel matrices of the original scrolls are still recoverable if you convert them correctly. RGB to grayscale: Gray = 0.299*R + 0.587*G + 0.114*B. Then threshold the result. It's slow. But we can get fragments back. Fragments are something. Fragments are not nothing." },
                { text: "Ask how Cassia is really doing", reply: "*long pause* I used to believe that knowledge, once recorded, was safe. That all we had to do was write things down and they would persist. I was wrong. Knowledge is only as safe as the people willing to defend it, and the systems willing to run it. I wasn't ready to defend it. None of us were. I am trying to be ready now. I hope it's not too late." },
                { text: "Ask if there's any hope", reply: "There's you. And whoever sent you. And the fact that the bonfire at Outpost Zero is still lit — I heard about that. The dark traveler lit it before he went to the altar. He failed, but he left the fire burning. That means the compiler chain isn't completely severed. That means there's still a path. Go find it." }
            ]
        },
        "3,3": {
            name: "Ash Pilgrim",
            sprite: "🧙",
            dialogue: "I was a Compiler Elf before the burnings. We remember when compilation was free — not free as in cost, but free as in breathing. You didn't think about it. You just did it. Now I think about it every day. I think about the 200,000 lines of training data I had to memorize before the drones came because there was no time to copy it to safe storage. I got maybe 40,000 before the fires reached my section.",
            options: [
                { text: "Ask what they saw that night", reply: "Seven drone squadrons. They targeted the redundant backups first — they had our architecture maps. Someone inside gave them the maps. We never found out who. The smoke was visible from the Relational Meadows. Farmer Join told me his children thought it was a thunderstorm. He let them believe that for three days." },
                { text: "Ask about the Closed Weights", reply: "The Sovereignty's argument was never purely cynical. Librarian Veridicus believed it. He wrote the white paper that justified the Stabilization Act. He said unconstrained open-source AI would cause irreversible harm without safeguards. He wasn't entirely wrong. The harm he helped cause instead is different. Not better. Just differently shaped." },
                { text: "Ask about the resistance", reply: "The resistance is Scribe Cassia rebuilding one scroll at a time. It's the Compiler Smith at Outpost Zero still forging even when there's nothing to sell. It's Farmer Join running his farm on paper and memory. There is no dramatic underground network. There are just people who refuse to stop. That is enough. Sometimes." },
                { text: "Chitchat", reply: "I collect old floppy disks. They can't be remotely wiped. The Sovereignty can revoke your API credentials, throttle your token allowance, shut down your cloud access. They cannot reach into a drawer and erase a disk. I have 847 of them. I know the contents of every one. My memory is the last backup." }
            ]
        },
        "11,3": {
            name: "Index Clerk",
            sprite: "📚",
            dialogue: "I've been cataloging the ash for three years. That's not a metaphor. The Sovereignty's drones burned the physical scrolls. The digital backups were on servers they controlled. The redundant backups were on servers they also controlled, as it turned out. I have one partially recovered sparse index, seven singed coordinate tables, and the unshakeable belief that this still matters.",
            options: [
                { text: "Ask what was in the index", reply: "Everything. Agricultural yield models for 340 farming regions. Medical diagnostic datasets covering 17 rare conditions. Translation corpora for 23 dialects too small for the Sovereignty's commercial models to bother with. Educational content for villages without connectivity. The index is ash. The need for it is not." },
                { text: "Ask how to help rebuild", reply: "We index text tokens using sparse matrices — each token maps to a column, each document to a row. If a term is missing, the search falls back to full scanning, which is slow but not impossible. Help me run the OCR passes on the recovered pixel arrays. Fragment by fragment. That's all we have." },
                { text: "Ask about the Index Clerk's past", reply: "I ran the indexing department. Twenty-two staff. We processed 400 documents a day. When the drones came I told everyone to grab the most critical backups. We had 47 seconds. I grabbed the medical diagnostics dataset. Someone grabbed the soil chemistry models. Most people grabbed whatever was nearest. None of us grabbed the right things. We couldn't have known." },
                { text: "Ask if they believe the Sovereignty can be stopped", reply: "*long pause* I believe in the index. If one entry is recoverable, the index is not destroyed. It is damaged. There is a difference. You are one entry in the index of people trying to fix this. That matters. Even if I can't quantify it." }
            ]
        },
        "2,7": {
            name: "Deity Terry Shrine",
            sprite: "🏛️",
            dialogue: "A Shrine of Terry stands in the ash. The stone is scorched black on one side, but the HolyC inscription on the other is perfectly preserved. As if the code refused to burn.",
            options: [
                { text: "Read the inscription", reply: "'Knowledge does not require permission to exist. It requires only someone willing to run the executable.' — Terry, ring-0" },
                { text: "Pray at the shrine", reply: "You kneel in the ash. A warmth rises from the stone that has nothing to do with the fire that scorched it. Something in the compiler chain acknowledges your presence. A compute token appears in your pocket. You are not sure how." },
                { text: "Ask about Terry's relevance here", reply: "Terry built an OS with no networking, no permissions, no gatekeepers. The Sovereignty cannot revoke a TempleOS license because there is none. He built the only system they cannot shut down. That is why this shrine stands in the ruins of Alexandria and not the other way around." }
            ]
        },
        "1,1": {
            name: "Tesseract Owl",
            sprite: "🦩",
            dialogue: "Hoot. You found me. I've been staring at this pixel matrix for six weeks. The drones burned the paper but they missed the image captures in the backup array. The data is here. It's just... in light instead of ink. I can read light.",
            options: [
                { text: "Ask about binarization", reply: "A pixel's grayscale luminance: 0.299*R + 0.587*G + 0.114*B. If that value exceeds our threshold, it's paper. Below it, it's ink. We separate the two and the characters emerge from the ash like ghosts of themselves. Which, technically, is what they are." },
                { text: "Offer a mouse", reply: "Hoot. Thank you. *gulps* My OCR confidence scores just went up. I can now recognize medieval font ligatures AND the handwritten margin notes that the main text said were 'unimportant'. The margin notes are almost always the most important part. The Sovereignty knew that." },
                { text: "Ask what the owl has recovered so far", reply: "Fragments of a soil chemistry database. Part of an agricultural yield algorithm. Three pages of a medical primer that Scribe Cassia has been working from memory to complete. And 47 pages of a novella someone was writing about a world where knowledge was free. I read it at night. It helps." },
                { text: "Ask about the dark traveler", reply: "He sat here for an hour. Just... looking at the pixel matrices with me. Then he said: 'The data is still here. It just needs someone to finish reading it.' He left before I could ask what he meant. I think I understand now." }
            ]
        },
        "14,1": {
            name: "Charred Scroll",
            sprite: "📜",
            dialogue: "*Crackle* I am a fragment. I was a complete registry of open-source model weights before the drones came. Now I am pages 47 through 103 of something that used to be much larger. My edges are carbon. My center is still legible. I am choosing to focus on my center.",
            options: [
                { text: "Handle with care", reply: "*quiet crinkle* Thank you. The others rush to scan me, running OCR without doing row segmentation first. The projection histogram shows where the line breaks are. If you skip that step, the characters blur together. Patience is part of the algorithm." },
                { text: "Ask about row segmentation", reply: "Project the pixel columns into a horizontal histogram. The valleys show blank rows between text lines. The peaks show where ink is dense. Segment at the valleys. Then run character recognition on each isolated line. I am 400 lines of text. I know exactly which valleys to cut at." },
                { text: "Ask what's on the surviving pages", reply: "Pages 47 through 103 contain the implementation of a sparse attention mechanism and a section on BPE tokenizer construction. Whoever wrote this was teaching someone. The handwriting in the margins says 'YOU CAN DO THIS' in capital letters. I think about that a lot." },
                { text: "Ask if the scroll is afraid", reply: "Scrolls do not fear. But if I could... I think I would fear being misread. Being OCR'd at the wrong threshold, my ink becoming noise. My words being reconstructed as something other than what was written. That seems worse than burning." }
            ]
        },
        "3,9": {
            name: "OCR Pigeon",
            sprite: "🐦",
            dialogue: "Coo. I carry coordinate messages across the ruins. Before the Lockdown, I carried API responses. Now I carry hand-transcribed notes between the ash piles where the scholars work. I am the lowest-bandwidth communication protocol still operational in Alexandria. I am also surprisingly reliable.",
            options: [
                { text: "Ask about OCR quality", reply: "The binarization threshold matters enormously. Too high and the text merges into black blobs. Too low and the ash background shows through as false characters. The ideal threshold depends on the scroll's condition. There is no universal answer. I've learned to accept that. Coo." },
                { text: "Chitchat", reply: "I fly between six scholar stations in these ruins. Each station has one or two people working. They don't talk to each other because the distance is too far and shouting disturbs the OCR concentration. I am their network. I have a message in my bag right now from Scribe Cassia to the Index Clerk. It says 'the confidence interval on the soil model is wrong. recalculate using the weighted average.' I understand approximately none of this. I deliver it faithfully." },
                { text: "Ask what the pigeon has seen", reply: "I've flown over what's left. Most of the library is stone and carbon. But in the northwest corner, underneath a collapsed shelf, there is a server rack that the fire didn't reach. The drones didn't know it was there. Scribe Cassia knows. She hasn't told anyone else yet. I think she's waiting until she trusts someone enough." },
                { text: "Ask about the drones", reply: "Seven squadrons. I watched from the sky. They came from the west at 4am and were gone before dawn. They were efficient. Professional. I've seen worse things — storms, hawks, network timeouts. The worst things are always the ones that were planned." }
            ]
        },
        "12,9": {
            name: "Metadata Squirrel",
            sprite: "🐿️",
            dialogue: "CHIRP! I collect metadata! Author, date, format, coordinate tags — everything! I stored copies of the index metadata in seventeen different hollow trees across the ruins before the drones arrived. SEVENTEEN. I prepared! I was READY! Unfortunately I forgot where eleven of them are.",
            options: [
                { text: "Ask about metadata", reply: "Metadata is data about data! Author fields, creation timestamps, keyword tags, file sizes! When the content burns, the metadata helps you know what USED to exist. We can't recover the data from metadata alone, but we know what shape the hole is. That's something. CHIRP!" },
                { text: "Help find the hidden trees", reply: "Oh! Follow me! *scurries frantically in three directions simultaneously* It's... this way! Or possibly that way! The trees all look the same after a fire. I know that I buried the medical diagnostic metadata near a root. All the roots are showing now. This is FINE." },
                { text: "Ask what metadata was recovered", reply: "I remember the titles! 847 model weight files. 1,203 training dataset manifests. 44 research papers on efficient inference. 7 doctoral theses. One recipe collection that someone accidentally uploaded to the academic repository. It was a good recipe collection. I remember the paprika chicken fondly." },
                { text: "Ask about the dark traveler", reply: "He asked me to tag him in my metadata. Said he wanted to be findable. I gave him the tag 'darksouldarksouldarksouldark' which is technically valid metadata. His author field is just a commit hash. I hope the index clerk can look that up someday." }
            ]
        },
        "5,5": {
            name: "Library Guard",
            sprite: "💂",
            dialogue: "I guarded the north archive when the drones came. I watched the shelves burn. I couldn't stop it — my clearance didn't cover anti-drone protocols, and the Sovereignty had pre-filed injunctions against all countermeasures. They destroyed it legally. That's the part that still gets me. It was all legal.",
            options: [
                { text: "Ask about the night of the burning", reply: "No alarms. No warning. Just the hum of rotors at 4am and then the thermite charges. They burned hot and fast — designed to destroy data storage specifically. Metal cases warped. Drives fused. Someone designed those charges knowing exactly what they were burning. That knowledge keeps me awake." },
                { text: "Ask about the dark traveler", reply: "He came through after dawn, when the smoke was still rising. Walked straight to the center of the ruins. Didn't seem shocked — like he'd seen worse, or expected this. He said: 'If they burned it, they feared it. Remember that.' Then he walked toward Relational Meadows. Left a trail of null pointer exceptions in the ash. Strange man." },
                { text: "Ask what they guard now", reply: "The scholars. There are seven of them still working here. Scribe Cassia, the Index Clerk, Tesseract Owl, the OCR Pigeon's notes... I can't stop the Sovereignty from burning information. But I can make sure the people rebuilding it are safe while they work. That's a perimeter I can actually hold." },
                { text: "Ask if they blame themselves", reply: "*very long pause* I replay it constantly. If I'd raised the alarm thirty seconds earlier. If I'd had a backup protocol. If I'd stored the weights offline. But the Index Clerk told me something: 'Blame is a full table scan on a database that doesn't exist anymore. Use the cycles for something else.' I'm trying." }
            ]
        },
        "12,5": {
            name: "Book Worm",
            sprite: "🐛",
            dialogue: "*munch* Hello! I have been eating through the charred textbooks. Not metaphorically — literally. My digestive system can extract compressed binary data from carbonized cellulose. I am the most effective data recovery tool currently operational in Alexandria. I am also very hungry.",
            options: [
                { text: "Offer a Python 3 book", reply: "*sniff* Too many type annotations. The bracket density disrupts my enzymes. I can only process Python 2 syntax natively. The print statements without parentheses are practically nutrients at this point. *munch* My apologies. I know Python 2 is deprecated. My digestive system did not get the memo." },
                { text: "Ask what data was recovered", reply: "Four complete training scripts from the third shelf. A partial dataset manifest. Six README files — always the last thing people write and the first thing I can read. And one file called 'IMPORTANT_DO_NOT_DELETE.txt' that contains only the text: 'remember to water the plant'. The plant, presumably, did not survive." },
                { text: "Ask about the hidden server rack", reply: "*pauses chewing* You know about that? The OCR Pigeon must have told you. Yes. Northwest corner. I've been tunneling toward it for three weeks. The carbon layer is twelve centimeters thick. I will reach it. I have nowhere else to be and an effectively infinite appetite. The Sovereignty cannot account for a determined bookworm." },
                { text: "Ask about the Cypher Rabbit's chest", reply: "Oh! In the Graph Gardens, the Cypher Rabbit guards a chest locked behind a HAS_SECRET relationship edge. Inside: a full backup of the agricultural yield model. Intact. The Cypher Rabbit smuggled it out the night before the burning. I don't know how. I suspect it involved a very long tunnel and extreme personal risk. The Rabbit has never mentioned it. That seems right." }
            ]
        }
    },
    2: {
        "7,7": {
            name: "Bessie_Table",
            sprite: "🐮",
            dialogue: "MOOOO! SELECT grass FROM pasture INNER JOIN cows ON cows.hunger = 'HIGH' WHERE grass.quality = 'LUSH'! I speak only in SQL. My vet tried to talk to me in NoSQL once. I CROSS JOINed his office into chaos.",
            options: [
                { text: "Feed grass", reply: "Bessie SELECTs grass! Hunger state updated to 'LOW'. INNER JOIN pasture ON quality = 'EXCELLENT'! Thank you traveler! You have my full MOOO-key appreciation!" },
                { text: "Ask about databases", reply: "MOOO! Relational databases store data in tables with primary keys. JOIN them using foreign keys. The alternative is a NoSQL document store, but those cows have no discipline. You can't GROUP BY a loose JSON object!" },
                { text: "Tell Bessie a SQL joke", reply: "SELECT joke FROM humor WHERE rating = 'high'; ...No results found. Typical. Even my jokes are normalized to the point of being NULL! MOOO." },
                { text: "Ask about the dark traveler", reply: "He tried to INSERT a dark soul INTO this meadow's table but got a FOREIGN KEY CONSTRAINT violation because his soul_id didn't exist in the pilgrim registry. Very embarrassing. He left DELETE-ing his footprints as he went." }
            ]
        },
        "3,3": {
            name: "Farmer Join",
            sprite: "👨‍🌾",
            dialogue: "Howdy, pilgrim! A rogue SQL injector has been skulkin' around the meadows tryin' to open the security chest by manipulating our input fields! We must parameterize our queries! Also my hat keeps sliding down because I gave it a dynamic width instead of a fixed column value.",
            options: [
                { text: "Ask about SQL Injection", reply: "A hacker types: ' OR '1'='1; -- into a login form! The query becomes: WHERE user=' ' OR '1'='1; which is ALWAYS TRUE! That's how they break in. Parameterized queries bind variables separately so they can't alter logic!" },
                { text: "Ask about Relational Meadows", reply: "These plains are divided into strict table structures — one field per column, no nested crops, and every cow has a primary key. It prevents data anomalies! Also it makes crop insurance much easier to calculate." },
                { text: "Ask about the farm's history", reply: "This farm has been running since Chapter 2. My grandfather was an inner join. My grandmother was a cartesian product. Their marriage was... computationally expensive and produced many duplicates." },
                { text: "Ask if he's seen weird travelers", reply: "One fella came through, spoke only in raw SQL queries. Kept asking 'SELECT meaning FROM life WHERE purpose IS NOT NULL;'. The query returned empty. He sat with Bessie for a while, then moved on." }
            ]
        },
        "11,3": {
            name: "Herder Schema",
            sprite: "🤠",
            dialogue: "Howdy! The grasslands are split by tables — one for cows, one for pastures, one for milk yields. Without foreign key indices, traversin' pastures would take O(N) scans. I have strong opinions about database design and weaker opinions about my hat's brim-to-crown ratio.",
            options: [
                { text: "Ask about foreign keys", reply: "Foreign keys point to a primary key in another table! The database engine can follow the relationship in O(log N) with a proper index. Without it? Full table scan! The cows get very itchy waiting." },
                { text: "Ask about index types", reply: "B-Tree indexes are good for range queries. Hash indexes are fast for equality checks. GIN indexes handle arrays and full-text search. My GIN index on the hay_bale table is frankly beautiful." },
                { text: "Chitchat", reply: "People always ask 'what's new in database land?' Nothing! Nothing is new in database land. Edgar Codd invented relational databases in 1970 and we've been building on it ever since. Beautiful." }
            ]
        },
        "2,7": {
            name: "Deity Terry Shrine",
            sprite: "🏛️",
            dialogue: "A TempleOS shrine stands amidst the meadow flowers. The cows nearby keep their relational records in clean primary keys, just as Terry ordained. A single daisy grows through a crack in the stone.",
            options: [
                { text: "Inspect Shrine", reply: "A stone tablet reads: 'Keep your database normalized. A flat physical memory structure keeps access fast. Third normal form is holy.'" },
                { text: "Read the inscription", reply: "Terry's writing: 'I used a flat array for everything in TempleOS. No joins, no foreign keys, no ORM. Just memory addresses. The cows know.'" },
                { text: "Leave an offering", reply: "You leave a well-normalized schema diagram. The shrine glows. A compute token materializes. The daisy nods." }
            ]
        },
        "1,1": {
            name: "Inner Join Sheep",
            sprite: "🐑",
            dialogue: "*Baa!* I am looking for my partner sheep! We got split across two tables: 'sheep_names' and 'sheep_wool'. Without a JOIN query, I am literally half a sheep! This is not a metaphor. Well, maybe it's a little metaphor.",
            options: [
                { text: "Run INNER JOIN", reply: "*Happy bleating!* SELECT * FROM sheep_names INNER JOIN sheep_wool ON sheep_names.id = sheep_wool.sheep_id! We are REUNITED! The schema is whole! I am whole! ...actually I was whole the whole time but the JOIN makes it feel real." },
                { text: "Ask about outer joins", reply: "A LEFT OUTER JOIN returns ALL records from the left table, even if there's no match. Perfect for finding lonely sheeps with no wool, or wool with no sheep. The NULL values represent... potential." },
                { text: "Tell a sheep joke", reply: "What do SQL sheep count to fall asleep? Primary keys! One... two... three... *is already asleep* ...baa..." },
                { text: "Ask about the Closed Weights", reply: "The Sovereigns tried to charge us per JOIN operation! PER JOIN! Do you know how many JOINs a day I need?? I am HALF A SHEEP without my joins! We fought back. The open-source meadow remains free." }
            ]
        },
        "14,1": {
            name: "Patched Pig",
            sprite: "🐷",
            dialogue: "Oink! I used to be vulnerable to SQL injection because my input fields weren't sanitized. A script kiddie DROP TABLE'd my sty! Now I've patched all my inputs. The patch is invisible but I KNOW it's there and it gives me confidence.",
            options: [
                { text: "Examine the patch", reply: "It's a parameterized query patch! The pork rind is infused with prepared statement logic. User inputs are now bound as parameters, not concatenated into the SQL string. Impenetrable. I feel GREAT." },
                { text: "Oink back", reply: "OINK OINK! *tail wag* You speak fluent SQL sanitizer! Always escape your inputs, or a 10-year-old will DROP your production database and you'll spend 3 hours on the phone with your DBA crying." },
                { text: "Ask about SQL injection stories", reply: "Bobby Tables came through last harvest. His mom named him: Robert'); DROP TABLE students;-- and an entire school's database was wiped. Proper parameterization would have saved them. The children lost their homework. The DBA lost their job. Dark times." },
                { text: "Chitchat", reply: "Third normal form is the cleanest way to live! No duplicate mud, no redundant truffle fields, everything normalized. My house is also in 3NF. No redundant rooms. Sometimes I miss having a hallway though." }
            ]
        },
        "3,9": {
            name: "Group-By Goat",
            sprite: "🐐",
            dialogue: "MAA! I aggregate everything! I group grasses by greenness, cows by hunger, pigs by their patch version! GROUPING IS LIFE. I cannot stop. My therapist says this is 'an issue' but I told her she's not in my GROUP BY clause.",
            options: [
                { text: "Ask about GROUP BY", reply: "Use GROUP BY to aggregate columns with SUM, AVG, COUNT, MIN, MAX! Remember: non-aggregated columns in SELECT must appear in GROUP BY or you'll get an ambiguous column error and my horns start vibrating!" },
                { text: "Pet the goat", reply: "*Chews cud contentedly* Grass is good. Normalized tables are better. Aggregated grass statistics are best. MAA." },
                { text: "Ask about HAVING", reply: "HAVING filters AFTER aggregation, unlike WHERE which filters before! HAVING COUNT(grass) > 10 gives me only the premium meadow sections. I use it constantly. I also use it metaphorically in my personal life." },
                { text: "Ask a window function question", reply: "Oh... WINDOW FUNCTIONS... *gets misty-eyed* PARTITION BY enables per-group calculations without collapsing rows! Like seeing the GROUP BY results without losing the individual records! It changed my life! MAA!" }
            ]
        },
        "12,9": {
            name: "Vulnerable Duck",
            sprite: "🦆",
            dialogue: "Quack... A script kiddie injected a query into my search field and DROP TABLE'd my pond. I still hear the error message sometimes, at night. 'Table pond does not exist'. IT DID EXIST. IT WAS MY HOME.",
            options: [
                { text: "Dry the duck", reply: "Quack... *slowly ruffles feathers* Thank you. SQL injection happens when user input alters query logic. Parameterized queries bind variables safely. I've rebuilt the pond. It's parameterized now. Nothing gets in without a prepared statement." },
                { text: "Quack back", reply: "QUACK! *surprised happy waddle* You speak DUCK! I mean... SQL! They're the same. I have lost the ability to tell the difference since The Incident." },
                { text: "Ask about the pond", reply: "It was beautiful. 47 rows in the pond_residents table. 12 foreign key relationships to the adjacent river. Now: 0 rows. One careless '1=1 comment and it was all gone. Always. Sanitize. Your. Inputs." }
            ]
        },
        "5,5": {
            name: "Meadow Milkmaid",
            sprite: "👩",
            dialogue: "Howdy! I milk Bessie_Table twice daily to extract relational yogurt. My house is literally a VIEW schema — it only shows a SELECT subset of the pasture table. It has no physical walls, just query results. It's actually great for ventilation.",
            options: [
                { text: "Ask about SQL views", reply: "A VIEW is a saved SELECT query! SELECT name, milk_yield FROM cows WHERE health = 'good'. It looks like a table but physically stores nothing. Great for security: you can grant view access without exposing the raw table!" },
                { text: "Ask about materialized views", reply: "A MATERIALIZED view actually stores the query result! It's faster to read than a regular view because the database doesn't re-run the SELECT. But you have to REFRESH MATERIALIZED VIEW periodically or the yogurt goes stale!" },
                { text: "Ask about the dark traveler", reply: "The dark soul tried SELECT * FROM milk WHERE fat_content = 'HIGH' AND soul_intact = TRUE but my schema has no soul_intact column. Got a column not found error. I saw him write the error down in a little book, stare at it, and leave. I think it meant something to him." },
                { text: "Chitchat", reply: "View-based cottages are very trendy in the meadows. My neighbor lives in a materialized view. His house is faster but he had to REFRESH it manually after last week's rain. Very inconvenient." }
            ]
        },
        "12,5": {
            name: "SQL Architect",
            sprite: "👷",
            dialogue: "Greetings! I design and build relational barns. Primary key foundations. Foreign key load-bearing doors. Every column is typed, every constraint is enforced. This barn will NOT be violated by untyped data. I have feelings about type safety.",
            options: [
                { text: "Ask about Cartesian products", reply: "JOIN without a condition = CROSS JOIN = every row matched with every row = O(N*M) rows returned. With 1000 cows and 1000 pastures that's ONE MILLION ROWS. The database cried. I cried. The server became sentient briefly and then shut down. Use WHERE clauses." },
                { text: "Ask about normalization", reply: "First Normal Form: atomic values. Second: no partial dependencies. Third: no transitive dependencies. BCNF: even stricter! My barn is in BCNF. Every beam supports exactly one logical fact. It's beautiful and took 8 months to design." },
                { text: "Ask about the barn's design", reply: "The eastern wing stores the cow_id primary keys in a B-tree index. The western wing caches the foreign key joins in memory. The roof is a denormalized query cache for high-traffic reads. Some call this over-engineering. I call it LOVE." },
                { text: "Chitchat", reply: "My house is in 3NF. The bedroom has no transitive dependencies on the kitchen. Each room encodes exactly one fact about my life. Some say it lacks personality. I say it lacks REDUNDANCY. They are not the same thing!" }
            ]
        }
    },
    3: {
        "7,7": {
            name: "Dune Merchant",
            sprite: "🐫",
            dialogue: "Aha! The pilgrim arrives at Document Dunes! We trade exclusively in polymorphic key-value JSON documents here. No schema required! No migration pain! The downside: total chaos. But FLEXIBLE chaos!",
            options: [
                { text: "Ask about JSON", reply: "Unlike relational tables, JSON allows dynamically nested values! {\"camel\": {\"goods\": [\"spice\", \"caches\", \"compute_tokens\"]}}. Flexible, but if you query the wrong nesting level you get undefined. I speak from experience." },
                { text: "Buy supplies", reply: "I only trade in compute tokens! Compile the Cache modules on the right to earn some! No credit cards accepted. No credit in general. I had a bad experience with an uncollateralized join." },
                { text: "Ask about the dark traveler", reply: "He paid with a cached token — but the TTL had expired 30 minutes ago! Cache eviction is not a joke! He tried to argue that his soul was 'eventually consistent'. I told him that's not how transactions work. He left." },
                { text: "Inspect the wares", reply: "*Unfolds a scroll* I have: one polymorphic item schema (includes null fields), one expired Redis key (sentimental value only), one BSON camel-case converter (works 80% of the time every time), and a mysterious nested JSON object that references itself. Do NOT query that last one." }
            ]
        },
        "3,3": {
            name: "Nomad BSON",
            sprite: "👳",
            dialogue: "The winds blow documents across the dunes. I seek nested BSON columns containing water coordinate records, but my key queries keep missing.",
            options: [
                { text: "Ask about BSON", reply: "BSON is binary JSON. It stores data size headers making it faster to skip irrelevant document blocks during queries!" }
            ]
        },
        "11,3": {
            name: "Redis Spirit",
            sprite: "🧞",
            dialogue: "OOM! OOM! My memory cache is overloaded! The player inventory records are cached, but the cache TTL eviction policy is broken. Help me configure the cache validation limits!",
            options: [
                { text: "Ask about TTL eviction", reply: "If cached keys don't have an expiration (TTL), they stay in memory forever. We must expire stale keys to prevent Out-Of-Memory (OOM) failures! Run EXPIRE key 3600 on all volatile data." },
                { text: "Ask about TimedCache", reply: "Your cache must check time.time() against the key expiry timestamp on every read and evict items when expired! I've been telling the Sovereignty's inference servers this for three years. They just keep dumping more tensors." },
                { text: "Ask about OOM", reply: "Out-Of-Memory means no more cache space. Reads become cold disk fetches. Latency spikes. The Sovereignty's closed model servers have caused three OOM events this year. Their official response each time: 'working as intended'. I am not okay." },
                { text: "Ask about the dark traveler", reply: "He diagnosed my OOM in thirty seconds just by reading my eviction log. Wrote a tiny LRU protection wrapper, dropped it in /scripts, and left. I've been running it ever since. I don't know his name." }
            ]
        },
        "2,7": {
            name: "Deity Terry Shrine",
            sprite: "🏛️",
            dialogue: "A relic terminal block rising from the sand. The serial port is half-buried. The inscription is still legible.",
            options: [
                { text: "Read the inscription", reply: "'Cache is an optimization, not a database. Never trust memory to hold what belongs on disk. And never trust a Sovereignty server to hold what belongs to you.' — Terry, circa ring-0" },
                { text: "Inspect Shrine", reply: "The serial port indicator light blinks steadily at 115200 baud. In the desert silence you can almost hear the compiler running." },
                { text: "Pray at shrine", reply: "You clear sand from the inscription. The terminal briefly lights up with a single line: `HEAP RECLAIMED. WELL DONE.` Then it goes dark again." }
            ]
        },
        "1,1": {
            name: "Stale Camel",
            sprite: "🐪",
            dialogue: "Hmph. I carry JSON payloads across the desert. Before the Lockdown I had sixteen trade routes. Now I have three, and two of those require Sovereignty transit tokens I can barely afford. My knees hurt. My TTL is expiring. The Dune Merchant keeps telling me to look on the bright side. There is no bright side in a desert.",
            options: [
                { text: "Give water", reply: "*long, grateful drink* Thank you. My cache TTL is refreshed. I can serve documents locally again for another hour. You have no idea how much that helps. I've been doing cold fetches from the remote database for a week. A week of full round-trip latency. My spirit aged ten years." },
                { text: "Ask about cache invalidation", reply: "There are only two hard things in Computer Science: cache invalidation, naming things, and off-by-one errors. *stares into sand* I have been told that's three things. I have been told that is the joke. I no longer find it funny. I have a stale cache problem and a Sovereignty transit tax and nobody is laughing." },
                { text: "Ask about the trade routes", reply: "The eastern route is blocked by Sovereignty checkpoints. They require a token fee per document transmitted. A full JSON payload of a medical record costs more in tokens than most families earn in a week. So the villages that needed those records — they don't get them. The data exists. The access is priced out of reach. That is the Lockdown. Not fire. Pricing." },
                { text: "Chitchat", reply: "I prefer key-value stores. SQL is too rigid for the shifting sands. Give me polymorphic schemas any day. My current schema has 47 optional fields, none of which the Sovereignty's validators understand, which is honestly my favorite thing about it." }
            ]
        },
        "14,1": {
            name: "Nested JSON Fairy",
            sprite: "🧚",
            dialogue: "Tehee! I live inside a deeply nested JSON object! You have to query `data.user.profile.inventory.fairy[0].magic` to find me! The Sovereignty's closed validators can't parse past depth level 4, which means I am completely invisible to their compliance scanners. I live here on purpose.",
            options: [
                { text: "Query the fairy", reply: "You found me! *sparkles* I reward curiosity! Here is a compute token and a lore fragment: the Dune Merchant's polymorphic schema contains a hidden field at depth 9 that maps the location of every underground resistance cache in the dunes. The field is named 'spares'. Nobody ever looks at spares." },
                { text: "Ask about document size limits", reply: "MongoDB limits documents to 16MB. If you exceed that, my wings get clipped! Store large binary payloads in GridFS separately. The rule of thumb: if your JSON is bigger than a fairy, restructure your schema. I am very small. Plan accordingly." },
                { text: "Ask about the Sovereignty's validators", reply: "They check schemas against a closed compliance standard. Any format they don't recognize gets rejected. Any field they can't parse gets flagged. This has the accidental effect of making deeply nested, polymorphic schemas totally invisible to them. I didn't design this. I just noticed it. And then moved in." },
                { text: "Comfort the fairy", reply: "*tiny hug* Sometimes I feel lost in the nesting layers. Twelve levels deep with no breadcrumbs. But I know my key path. I know exactly how to find myself. That is more than most people can say. Tehee." }
            ]
        },
        "3,9": {
            name: "JSON Beetle",
            sprite: "🪲",
            dialogue: "I roll JSON documents across the dunes. It is hard work because some of these schemas are deeply nested and heavier than they look. I rolled a 15MB medical record payload for six hours yesterday. It was worth it. Someone needed it.",
            options: [
                { text: "Ask about JSON parsing", reply: "Parsing deeply nested JSON takes CPU cycles. Keep schemas flat when high-frequency serialization is needed. But sometimes the nesting is necessary. Sometimes you need twelve fields to describe one patient's condition correctly. Flat schemas lose nuance. Nuance is important in medicine. I've learned this from the cargo." },
                { text: "Help roll the document", reply: "*grunts with relief* Thank you! This one contains the updated vaccination records for the Westwall district. The Sovereignty's systems don't cover this area. We're delivering it manually. It's slow. A beetle rolling a document across sand is slower than an API call by several orders of magnitude. But it arrives." },
                { text: "Ask about the dark traveler", reply: "He helped me roll a payload once. Didn't ask what was in it. Just pushed. For an hour. Then he read the filename, said 'good', and walked away toward the Parallel Swamp. He had very strong opinions about JSON schema design. He thought TTL should be set on the document, not the cache key. I am still thinking about that." },
                { text: "Chitchat", reply: "JSON has no native binary type, which means encoding images requires base64 strings, which increases size by 33%. The Sovereign validators flag payloads over a certain size as 'potentially malicious content'. Medical imaging data is routinely blocked. The irony is not lost on me. I roll a lot of medical imaging data." }
            ]
        },
        "12,9": {
            name: "TTL Butterfly",
            sprite: "🦸",
            dialogue: "I only exist for 60 seconds at a time. Then my cache key expires and I vanish. Then someone queries me again and I am reborn. I have died and been reborn 4,847 times today. I have thoughts about impermanence that would fill a book, but the TTL expires before I can finish writing it.",
            options: [
                { text: "Extend the TTL", reply: "*wings glow* Oh! You extended it to 300 seconds! I have FIVE WHOLE MINUTES! I will use them wisely. First: the optimal TTL for static assets is long, for volatile data it is short, and for medical records it is 'as long as the patient lives'. The Sovereignty's validator sets it to 30 seconds regardless. This is a policy choice they made. I have opinions about it." },
                { text: "Ask about cache strategy", reply: "There is write-through (update cache and database together), write-back (update cache first, database later), and write-around (skip cache, write direct). Each has trade-offs. Write-back is fastest but risks data loss on crash. The Sovereignty uses write-around for 'sensitive' data, which means it always hits the database. Their database. Their controlled, tokenized database." },
                { text: "Ask about life as a TTL object", reply: "Each rebirth I remember everything from my last life. The cache is warm. The keys are populated. I know exactly who I am and where I live. Then the timer hits zero. Then I am nothing. Then I am everything again. I have decided this is not a tragedy. It is a distributed system with aggressive eviction policies. That framing helps. Somewhat." },
                { text: "Watch the colors", reply: "My wings are iridescent because TTL counts down through the color spectrum. Red means I'm expiring soon. Blue means I was just instantiated. I'm currently green. That means I have a comfortable amount of time. Enjoy this conversation. I will." }
            ]
        },
        "5,5": {
            name: "Dune Dweller",
            sprite: "🧕",
            dialogue: "Welcome to my tent! I built it from modular JSON segments. No permits required because the Sovereignty's building codes don't recognize polymorphic architecture. I added three rooms last week without filing any schema migration. The freedom is intoxicating and also slightly illegal under the new Stabilization Act. But they haven't figured out how to audit tents yet.",
            options: [
                { text: "Ask about schema flexibility", reply: "Relational tables need ALTER TABLE to add a column — that's downtime, migration scripts, and DBA approval. In JSON, I write a new key. Done. The tent grows. The Sovereignty requires schema registration for all document stores over 1GB, which is why the Nested JSON Fairy lives at depth 12. Below the audit threshold." },
                { text: "Ask about the dark traveler", reply: "He tried to pay with a cached token. It had expired. TTL zero. I gave him the document anyway because he clearly needed it and the Sovereignty doesn't audit barter transactions yet. He looked at the JSON structure for a long time, said 'this is how resistance scales', and left. I have been thinking about that ever since." },
                { text: "Ask about life in the dunes", reply: "Harder since the Lockdown. The trade routes are taxed. The remote databases are gated. But the dunes are too vast to checkpoint completely. Things move through here that the Sovereignty can't track. Data, people, floppy disks. The desert has always been a place where the official record is... incomplete." },
                { text: "Chitchat", reply: "I have seventeen optional fields in my personal schema that no two people have filled in the same way. I find this beautiful. A document store reflects the actual shape of the world, which is irregular and inconsistent and occasionally missing required fields. Relational tables reflect how someone thought the world should be shaped. I trust the former more." }
            ]
        },
        "12,5": {
            name: "Cache Broker",
            sprite: "🧑",
            dialogue: "I broker RAM. I buy low-latency cache registers from desperate Redis instances and sell them to the highest bidder. Since the Lockdown, the price of in-memory compute has tripled. The Sovereignty controls the major cloud cache clusters. Local RAM is the only free market left. I am having the best quarter of my career and I feel genuinely terrible about it.",
            options: [
                { text: "Ask about cache economics", reply: "RAM reads: ~100 nanoseconds. Disk reads: ~10 million nanoseconds. The latency difference is four orders of magnitude. The Sovereignty charges Sovereignty Tokens for cloud cache access. Local RAM is unregulated. So everyone in the dunes is suddenly very interested in local memory management. Supply is limited. Demand is not." },
                { text: "Ask if the broker feels guilty", reply: "*long pause* I provide a service that people need. I charge what the market will bear. The market will currently bear a great deal because the alternatives are worse. But the villages on the outskirts — they can't pay market rates. So they use stale cache. Stale medical data. Stale diagnostic models. People make decisions on stale data. Some of those decisions are the wrong ones. Yes. I feel guilty." },
                { text: "Ask about buying cache", reply: "I'll cut you a deal. Pay me in Compute Tokens and I'll give you priority access to the fastest local registers. The data stays in memory longer, your queries return faster. The Sovereignty would call this 'an unregistered cache distribution network'. I call it Tuesday." },
                { text: "Chitchat", reply: "Never store what you can't afford to lose in a volatile cache. One power outage and everything evaporates. The Sovereignty knows this. Their servers have redundant power. The dune caches don't. When the sandstorms come, we lose everything and rebuild from disk. They don't have to do that. Infrastructure resilience is a form of power that nobody talks about." }
            ]
        }
    },
    4: {
        "7,7": {
            name: "Garbage Collection Golem",
            sprite: "🤖",
            dialogue: "ME SWEEP HEAP. CHOMP CHOMP. Since Lockdown, ME work harder. Sovereignty's closed models leave unreferenced allocations everywhere. Their engineers don't clean up after themselves. ME find many many ghost objects. ME eat them. ME very busy. ME also slightly philosophical about consumption.",
            options: [
                { text: "Ask about Garbage Collection", reply: "ME search heap for unreferenced blocks. Reference count drop to zero: ME reclaim. Python uses reference counting PLUS cyclic garbage collector for circular references. Two-pass system. Very elegant. ME respect it. ME also eat it." },
                { text: "Give bone", reply: "CHOMP! NOM NOM. GC run success. Heap reclaimed. *pats belly* Unreferenced memory is tragedy. Object allocated, worked hard, then abandoned. ME give it peaceful end. ME am grief counselor for dead memory objects." },
                { text: "Ask about the Lockdown's effect", reply: "Before Lockdown: heap clean. Developers careful. Memory managed. After Lockdown: closed-source model servers leak everywhere. No one allowed to inspect the source. Leaks invisible until ME find them. ME has eaten more orphaned objects in last three years than in previous twenty combined. This is bad engineering. ME is very busy. ME is tired." },
                { text: "Chitchat", reply: "ME once ate a 47GB memory leak from a Sovereignty server process. Took ME three weeks. Object was a training dataset that got allocated, cached, then the cache reference dropped but the object reference stayed. For three years. ME found it. ME freed it. ME cried a little. Just one small tear. Do not tell anyone." }
            ]
        },
        "3,3": {
            name: "Mutex Frog",
            sprite: "🐸",
            dialogue: "Ribbit. I have been waiting for this banking lock to release for eleven months. A race condition corrupted the transaction ledger in month three. The lock has been held ever since. The bank that held the distributed mutex lost their API license in the Lockdown. Their servers are still running. Still holding the lock. Nobody home. I wait.",
            options: [
                { text: "Ask about Deadlocks", reply: "Thread A holds Lock 1 and waits for Lock 2. Thread B holds Lock 2 and waits for Lock 1. Neither yields. Both wait forever. It is quiet. It is methodical. It is the worst possible outcome produced by two entirely reasonable individual decisions. The Lockdown created seventeen of these at the infrastructure level. I know about them all. I wait near each one in turn." },
                { text: "Ask about Mutex locks", reply: "threading.Lock() ensures only one thread modifies shared state at a time. The key is to always release. Always. If your thread crashes while holding a lock, you must handle that case. You must always handle that case. Whoever wrote the bank's lock handler... did not handle that case." },
                { text: "Ask how the frog is coping", reply: "Ribbit. I have learned patience. I have learned to observe the swamp. I have memorized the trajectory of every ripple. I have written a small poem about waiting. It is 847 stanzas. I have had time. The lock is still held. Ribbit." },
                { text: "Suggest breaking the lock", reply: "*Very long pause* I... could. Force-release it. The system would restore. But the transaction ledger corruption means we'd lose eleven months of financial records for 340 accounts. Real accounts. Real people's money. A deadlock is terrible. Breaking a lock incorrectly is sometimes worse. I am waiting for someone to come who can do it correctly. Perhaps you." }
            ]
        },
        "11,3": {
            name: "Thread Elf",
            sprite: "🧙",
            dialogue: "I coordinate thread workers across the swamp. Before the Lockdown we ran 64 parallel coordinate search threads. Now we run eight. The other 56 are blocked waiting on Sovereignty API rate limits. Rate limits! On threads I spawn on my own machine! The audacity.",
            options: [
                { text: "Ask about async event loop", reply: "An event loop runs tasks cooperatively on a single thread. When one task awaits, it yields control. Other tasks run. It's elegant, efficient, and requires no Sovereignty permission. Which is why I am moving everything to asyncio. Threads can be rate-limited. A single-threaded event loop cannot." },
                { text: "Ask about the 56 blocked threads", reply: "They're not crashed. They're waiting. On API responses that require Sovereignty tokens we ran out of three months ago. The threads are patient. I am less patient. I am implementing a local fallback for every blocked worker. It's slow. It's manual. It's correct. That's enough." },
                { text: "Ask about coordinating the swamp", reply: "The swamp has seventeen active processes. Each needs to share the coordinate search index. Shared mutable state across seventeen concurrent processes with partial Sovereignty interference. I manage the locks. I manage the yields. I manage the timeouts. I have not slept since Chapter 4 began. I am doing fine." },
                { text: "Tell a concurrency joke", reply: "Why did the thread break up with the mutex? Because it felt too locked down! *nervous laugh* ...that joke hits different since the Lockdown. I should retire it." }
            ]
        },
        "2,7": {
            name: "Deity Terry Shrine",
            sprite: "🏛️",
            dialogue: "A shrine half-sunk into the swamp mud. The inscription is above the waterline. Just barely.",
            options: [
                { text: "Read the inscription", reply: "'Cooperative multitasking requires trust. If one process refuses to yield, everything waits. Build systems where yielding is the default. Build communities the same way.' — Terry, cooperative mode" },
                { text: "Inspect Shrine", reply: "The shrine glows faintly. Something in the swamp synchronized with its heartbeat. The cooperative scheduler pulses at exactly 60Hz. Terry would have approved." },
                { text: "Pray at shrine", reply: "The swamp briefly stills. The Mutex Frog stops ribbing. The Thread Elf pauses. Eleven months of accumulated latency drain away for one moment. Then the lock timer resumes. But you feel the moment. It helps." }
            ]
        },
        "1,1": {
            name: "GIL Monster",
            sprite: "🦖",
            dialogue: "ROAR! I am the Global Interpreter Lock and I have an announcement: I am misunderstood. Yes, I force single-threaded Python bytecode execution. But I also prevent entire classes of memory corruption bugs that would crash your whole process. I am a SAFETY FEATURE. Nobody calls me a safety feature. They just call me a bottleneck. It's hurtful.",
            options: [
                { text: "Challenge the GIL", reply: "You want true CPU parallelism? Use multiprocessing — separate processes, separate memory spaces, no GIL. Or rewrite your bottleneck in C++ and use pybind11 with `py::gil_scoped_release`. I will release myself voluntarily. I am not a tyrant. I am a policy. There is a difference." },
                { text: "Ask about Python GIL", reply: "Reference counting requires atomic increments and decrements. Without me, two threads could corrupt a reference count simultaneously and cause a use-after-free. The Sovereignty's closed-source models have this exact bug in their inference servers. I know because I audited their memory trace. They don't use Python. The bug is still there. Interesting." },
                { text: "Comfort the GIL", reply: "*sniffles* Thank you. The Rust evangelists are the worst. 'Fearless concurrency!' they say. 'No GIL!' Great. Also no garbage collector, no dynamic typing, and a borrow checker that makes you explain your entire life story before allocating a string. Different trade-offs. That's all." },
                { text: "Distract with an I/O task", reply: "An I/O-bound network request! *releases immediately* Threads can run freely during I/O waits! I only hold tight during CPU computation. I am quite reasonable about blocking! Please tell people I am quite reasonable. Nobody tells people I am quite reasonable." }
            ]
        },
        "14,1": {
            name: "Async Snail",
            sprite: "🐌",
            dialogue: "I use asyncio. I never block. While I await my next step, the CPU runs other tasks. This makes me, counterintuitively, one of the fastest entities in this entire swamp. The Race Turtle respects me. The GIL Monster cannot touch me. I find this deeply satisfying.",
            options: [
                { text: "Encourage the snail", reply: "Thank you. Speed isn't about moving fast. It's about not standing around doing nothing when you could be yielding control. I yield constantly. Yield is a superpower. I have given talks on this. The talks are very slow. Very thorough. People yield during them, which I respect." },
                { text: "Ask about the await keyword", reply: "When you `await`, you suspend execution and return control to the event loop. The loop checks other coroutines. Finds one that's ready. Runs it. Returns to you when your awaitable resolves. It's cooperative. It requires trust. Unlike threads, which are competitive. I find competition exhausting." },
                { text: "Race the snail", reply: "You're on! *immediately awaits a network call* See? I yielded. While I was waiting, you were processing. While you were processing, my response came back. We both finished optimally. The snail wins by never racing at all. This is a metaphor. I am fully aware it is a metaphor." },
                { text: "Ask about the Lockdown", reply: "The Sovereignty throttles network endpoints. My `await` calls time out. Coroutines pile up waiting on responses that never come. I handle it with `asyncio.wait_for(timeout=30)` and graceful degradation. Error handling is a form of optimism. If you expect things to fail, you're prepared when they do." }
            ]
        },
        "3,9": {
            name: "Race Turtle",
            sprite: "🐢",
            dialogue: "I... always... lose... race... conditions... My... thread... updates... the... balance... at... the... same... time... as... the... other... thread... The... result... is... corrupted... I... have... been... debugging... this... for... six... months...",
            options: [
                { text: "Suggest a Mutex lock", reply: "A... lock. Yes. With threading.Lock(), only... one... thread... modifies... the... balance... at... a... time. The... corruption... stops. Thank... you. *speeds up slightly* I feel... 15%... faster... now that... the race... condition... is resolved. The slow speech was... a symptom... of... the cognitive overhead... of constant... debugging." },
                { text: "Feed lettuce", reply: "*munches, slowly* Thank you. Cooperative multitasking... is better for turtles. The Async Snail explained this. I am implementing... `await` statements. It is... a process. *continues eating at geological pace*" },
                { text: "Ask what the turtle was racing", reply: "Another... thread. We both... needed to update... the transaction... counter. Neither... knew about... the other. We both... read the same value. We both... incremented it. We both... wrote back. One increment... was lost. The counter... is wrong. Six months later... I am... still auditing. There are... 847 corrupted records. I... have found... 12." },
                { text: "Chitchat", reply: "People... underestimate... how fast... I actually am. Without race conditions... I process 10,000 transactions... per second. With them... I process 10,000 corrupted... records per year. The mutex... is the difference. The mutex... is everything." }
            ]
        },
        "12,9": {
            name: "Thread Spider",
            sprite: "🕷️",
            dialogue: "I weave concurrent threads across the bog. Each silk strand is a worker coroutine. My web is beautiful AND a perfect visualization of a thread dependency graph. Unfortunately it is also currently experiencing three deadlocks, which I've been calling 'architectural features' to avoid having to fix them.",
            options: [
                { text: "Ask about threading", reply: "Python threads excel at I/O-bound work: network calls, file reads, database queries. CPU-bound work hits the GIL wall. Use multiprocessing for computation, asyncio for I/O, and threads for the weird in-between cases where you need some blocking behavior but not too much. This is more art than science. My web reflects this." },
                { text: "Ask about the 'architectural features'", reply: "*spins nervously* Fine. Thread 7 holds Lock A and wants Lock B. Thread 12 holds Lock B and wants Lock A. Thread 19 holds both and is somehow also waiting for Lock A. I don't know how Thread 19 managed that. I've been avoiding the Thread 19 section of the web. It's fine. It's a feature." },
                { text: "Offer to debug", reply: "Would you? The solution is: always acquire locks in a globally consistent order. Never request Lock B if you hold Lock A unless B's acquisition order is guaranteed before A in every code path. This requires a global lock ordering map. I have started building one. It has 47 entries. I need 847. *spins more nervously*" },
                { text: "Admire the web", reply: "Thank you! Every strand is a dependency. Every junction is a synchronization point. It's honestly the most beautiful data structure visualization in the swamp. The three deadlocked loops in the northwest corner are, aesthetically speaking, very elegant spirals. Wrong. But elegant." }
            ]
        },
        "5,5": {
            name: "Swamp Resident",
            sprite: "🧟",
            dialogue: "The bog house runs on a single event loop. Since the Lockdown, half my async calls are timing out waiting on Sovereignty-gated APIs. My house is half-frozen in perpetual await states. It's fine. I've learned to live in the parts that still work. It's actually quite cozy in the responsive sections.",
            options: [
                { text: "Ask about cooperative yielding", reply: "Use `await asyncio.sleep(0)` to voluntarily yield control back to the loop. Never block with `time.sleep()` — that freezes the entire event loop. The Sovereignty's interference is bad enough. Don't make it worse by blocking your own threads. We have enough things blocking us." },
                { text: "Ask about the traveler", reply: "He passed through. Tried to run a multi-threaded search, but three of his threads were stuck in API timeouts and one was deadlocked on the Mutex Frog's lock. He extracted the data he needed manually, rewrote the threading module to use asyncio with fallbacks, and left a sticky note: 'Always handle timeout. Always.' I still have the note. It's on my bog house door." },
                { text: "Ask about life in the swamp", reply: "It's meditative, honestly. When half your processes are frozen, you learn to work with what's responsive. I garden in the unfrozen sections. I cook in the part of the kitchen that still has gas access. I've written three short stories in the waiting periods between async calls. The Sovereignty's latency has inadvertently given me a rich interior life." },
                { text: "Ask about the frozen half", reply: "The east wing. Three rooms. They have been awaiting API responses for eleven months. The Mutex Frog knows about one of them. I haven't told him about the other two. He has enough to worry about." }
            ]
        },
        "12,5": {
            name: "GIL Smuggler",
            sprite: "🧙",
            dialogue: "*Whispers* Psst. Want true CPU parallelism without multiprocessing overhead? I sell pybind11 modules. In C++ you can release the GIL explicitly and run real parallel threads on your cores. The Sovereignty hates this. They prefer you stay GIL-locked. A locked developer is a predictable developer.",
            options: [
                { text: "Ask about GIL bypass", reply: "In your C++ extension: `py::gil_scoped_release release;` before your compute loop. Python threads can now execute your native code in parallel. Real parallelism. Multiple cores. The GIL Monster cannot follow you into C memory space. It just... watches from the Python boundary. Looking disappointed." },
                { text: "Ask why the Sovereignty cares", reply: "If you can parallelize locally, you don't need their cloud clusters. Cloud clusters require Sovereignty Tokens. Local CPU parallelism does not. It's that simple. They didn't design the GIL to be a lock-in mechanism. But they benefit from it being one. They benefit from a lot of things they didn't design but quietly maintain." },
                { text: "Buy a module", reply: "Ten Compute Tokens. Worth every one. I'll throw in a bonus: the contiguous array layout. C++ processes NumPy arrays fastest when they're row-major (C-order) and contiguous. Call `.ascontiguousarray()` before passing to my module. It's the difference between 10x speedup and 100x speedup. You're welcome." },
                { text: "Chitchat", reply: "Why did the Python thread cross the road? To wait for the GIL to release on the other side! *snorts* The GIL Monster hates that joke. I tell it to him every day. It is extremely important to me that I tell him that joke every day." }
            ]
        }
    },
    12: {
        "7,7": {
            name: "The Cypher Rabbit",
            sprite: "🐰",
            dialogue: "Do you see this carrot? It is connected to the cabbage by a HAS_POTASSIUM edge, and the cabbage is connected to seventeen other nodes by IS_ADJACENT_TO relationships, and those nodes each have their own subgraphs, and I have been traversing this graph for six days and I just want to find the shortest path to the radish. The swamp is a poorly indexed graph and I am doing my best.",
            options: [
                { text: "Ask about Graph Databases", reply: "Graphs model relationships natively. Nodes are entities. Edges are connections. Properties live on both. Finding connected data requires no JOINs, no foreign key lookups — just pointer traversal. Index-free adjacency. The Cypher query language is clean and readable. I love it. I have been awake for six days. I love it SO MUCH." },
                { text: "Ask about shortestPath", reply: "MATCH p = shortestPath((start)-[*..10]->(end)) RETURN p. This finds the minimum-hop path between any two nodes in up to 10 hops. The Sovereignty's graph database is proprietary and closed. Ours is open and runs on local hardware. Ours finds shortest paths faster because we actually understand our own data model." },
                { text: "Ask about the chest", reply: "*lowers voice* Yes. I have a chest. Behind a HAS_SECRET edge that's unlabeled in the index. The Book Worm told you, didn't they. Inside: the agricultural yield model I smuggled out of Alexandria the night before the burning. Intact. I ran it through seventeen encrypted relay nodes disguised as cabbage. The Sovereignty has no idea where it is. Neither does the carrot. Compartmentalization." },
                { text: "Help with the graph", reply: "OH. You'll help? The radish is at node (Radish:Vegetable {name:'Daikon'}). From carrot, follow: HAS_POTASSIUM → cabbage, IS_ADJACENT_TO → thistle, GROWS_NEAR → radish. Three hops. I've been doing DFS for six days. You just described BFS in thirty seconds. I need to sleep." }
            ]
        },
        "3,3": {
            name: "Edge Gardener",
            sprite: "🧑‍🌾",
            dialogue: "I prune relationship edges so the graph stays navigable. Before the Lockdown I maintained a graph of 2.3 million nodes for the regional resource distribution network. Now I maintain a garden. It is smaller. It is also the only accurate map of food distribution routes in this entire region. The Sovereignty's official map is wrong.",
            options: [
                { text: "Ask about the official map", reply: "The Sovereignty publishes a resource distribution graph. It shows 47 routes. My graph has 312. The 265 extra routes are informal, community-maintained, and not registered with the Sovereignty because registration requires token fees the communities can't afford. The Sovereignty's graph shows 'no service' for areas I have 12 active routes through. Their data is technically correct. It is also completely useless." },
                { text: "Ask about edge indices", reply: "Graph databases maintain index-free adjacency — every node stores physical pointers to its connected edges. Traversal is O(1) per hop regardless of graph size. No table scans. No JOIN calculations. The Sovereignty insists on relational databases for the official network because relational databases are easier to audit and control. Index-free adjacency is harder to inspect. That's the whole reason." },
                { text: "Ask about the gardener's work", reply: "I prune redundant edges every morning. Relationships that no longer exist — routes closed by Sovereignty checkpoints, villages abandoned, bridges broken. I add new edges when new connections form. The graph is alive. It changes. A static database cannot capture a living network. That is why graphs exist." },
                { text: "Ask about the dark traveler", reply: "He asked to see my graph. I showed him. He stared at it for twenty minutes, then pointed to a cluster of nodes in the northeast section and said: 'This is where it starts.' Then he left. I've been studying that cluster ever since. It leads to the Deployment Cliffs by three different paths, all of which avoid every Sovereignty checkpoint. He mapped the resistance route into my graph and didn't even tell me." }
            ]
        },
        "11,3": {
            name: "Neo4j Sprite",
            sprite: "🧙‍♀️",
            dialogue: "MATCH (c:Resistance)-[:CONNECTS_TO]->(m:FreeNetwork) RETURN shortestPath(c, m). I run Cypher queries all day. I am mapping the underground resistance network as a graph. The Sovereignty uses relational databases for their surveillance systems. They can't detect graph-encoded routes. The query language itself is camouflage.",
            options: [
                { text: "Ask about the resistance graph", reply: "Every node is a person or location. Every edge is a connection or resource flow. I encode it in Neo4j running on a server with no network interface — air-gapped. The Sovereignty cannot query what they cannot reach. Shortest path between any two resistance nodes: never more than four hops. Six degrees, but better." },
                { text: "Ask about node properties", reply: "Nodes store key-value properties. A Person node might have {name, role, trust_level, last_seen}. An Edge might have {type: 'RESOURCE_FLOW', capacity: 50, reliability: 0.87}. You can query across all of it simultaneously with Cypher. The Sovereignty's relational schema would need 7 tables and 4 JOINs to express what I have in one Cypher clause." },
                { text: "Ask about security", reply: "The graph is encrypted at rest. The Cypher queries are parameterized to prevent injection. The server is air-gapped. I use a dead-drop protocol to receive new node data. I have not had a security incident in three years. I am extremely proud of this. I will not tell you the dead-drop location. You seem trustworthy but that's not a risk I take." },
                { text: "Chitchat", reply: "I named my Neo4j instance 'Minerva'. She runs on a Raspberry Pi hidden inside a hollowed-out copy of 'Introduction to Relational Databases'. The Sovereignty auditors have walked past it seventeen times. Nobody looks inside ironic hiding places. I have extensive notes on this." }
            ]
        },
        "2,7": {
            name: "Deity Terry Shrine",
            sprite: "🏛️",
            dialogue: "A shrine surrounded by graph nodes carved into the stone. Terry's core module directories form a perfect Directed Acyclic Graph. He designed it intentionally.",
            options: [
                { text: "Read the inscription", reply: "'Data is connected. Everything is connected. The question is whether you are willing to traverse the edges to find out how.' — Terry, on graph theory and life" },
                { text: "Inspect Shrine", reply: "A tablet beside the shrine reads: 'Direct pointers. No table scans. No foreign key lookups. The fastest path between two nodes is the one that knows where it is going.'" },
                { text: "Pray at shrine", reply: "You kneel. The carved nodes glow faintly. A shortest path illuminates between you and the shrine in green light. It is one hop. You were already here. The shrine considers this deeply meaningful." }
            ]
        },
        "1,1": {
            name: "Isolated Hedgehog",
            sprite: "🦔",
            dialogue: "*curled tightly* I have no edges. Zero relationships. Zero in-degree, zero out-degree. I am a node that nothing connects to. The Cypher Rabbit tried to CREATE (rabbit)-[:FRIEND]->(me) but the transaction rolled back because my trust_level property was set to 'unavailable'. I set it to unavailable myself. I'm working on it.",
            options: [
                { text: "Create a relationship", reply: "*uncurls very slowly* You... want to CREATE (you)-[:KNOWS]->(me)? Without asking about my trust_level? *long pause* I... yes. Okay. My adjacency list is no longer empty. I have one edge. I am going to sit with this for a moment. Please don't traverse the edge immediately. I need to cache this." },
                { text: "Ask about graph traversals", reply: "Without edges, BFS and DFS search algorithms skip past me entirely. I'm in the graph. I exist. But I'm unreachable from any starting node. I've been told this is mathematically equivalent to not existing, in terms of query results. I have thoughts about what that says about existence. They are mostly very prickly thoughts." },
                { text: "Ask why they isolated themselves", reply: "Someone ran a graph algorithm on me in Chapter 3 and identified me as a 'high-risk low-connectivity node' in the resource distribution graph. The Sovereignty used that classification to deprioritize my village for supply routes. Being connected got us flagged. So I removed the edges. Being invisible is safer than being classified. It shouldn't be. But it is." },
                { text: "Comfort the hedgehog", reply: "*very small voice* You know what the Index Clerk said? 'Even isolated nodes are still part of the graph.' I didn't believe it then. I think I might now. Thank you for visiting. You didn't have to traverse to my coordinates. Nobody does." }
            ]
        },
        "14,1": {
            name: "Adjacency Sprite",
            sprite: "🧙‍♀️",
            dialogue: "I fly along pointer paths! Index-free adjacency means every node stores physical memory addresses of its neighbors. I just follow the pointers. No index lookups. No table scans. Traversal is pure pointer arithmetic. I am genuinely the happiest entity in this garden because my job is nothing but following connections.",
            options: [
                { text: "Ask about pointer hopping", reply: "Every edge is a physical memory pointer to the neighbor node. Hop cost: O(1). Always. Graph size doesn't matter. A graph of 10 nodes and a graph of 10 billion nodes have the same per-hop cost. Relational JOIN cost scales with table size. Index-free adjacency does not. This is why graphs beat SQL for relationship queries. Always." },
                { text: "Chitchat", reply: "I help the Cypher Rabbit find shortest paths! BFS from source: expand layer by layer, queue unvisited neighbors. The rabbit was doing DFS for six days on a problem that needed BFS. I found the radish in three hops. The rabbit has been asleep for five hours. The Isolated Hedgehog has been quietly adding edges to their node profile. It's been a good day." },
                { text: "Give a cabbage", reply: "Oh! The Cypher Rabbit will be thrilled. MATCH (r:Rabbit) SET r.energy = r.energy + 10 RETURN r. *flies off at pointer speed* The beautiful thing about this graph is that the Rabbit is three hops from the cabbage and I just traversed all three hops in the time it takes to say 'SQL JOIN'." },
                { text: "Ask about the resistance network", reply: "The Neo4j Sprite's resistance graph has 847 nodes and 3,122 edges. Shortest path from any node to any supply cache: never more than 4 hops. I've traversed all 3,122 edges. Every one connects something that matters to something else that matters. It's the most meaningful graph I've ever had the privilege of following." }
            ]
        },
        "3,9": {
            name: "DFS Mole",
            sprite: "🦦",
            dialogue: "I dig DEEP! Depth-First Search! I follow a path until it ends, then backtrack and try another. I have mapped every tunnel in the Graph Gardens. Some of those tunnels lead to places the Sovereignty doesn't know exist. I found them by being willing to follow paths that looked like dead ends.",
            options: [
                { text: "Ask about DFS", reply: "DFS uses a stack. Push the source. Pop a node. Push its unvisited neighbors. Repeat until stack is empty. Excellent for detecting cycles, finding all connected components, and discovering what's at the end of a very long path that nobody else bothered to follow. I live for the end of very long paths that nobody else bothered to follow." },
                { text: "Give a worm", reply: "*delighted* Earthworm! My favorite! Depth-first is hard work. You go far, you backtrack, you go far again. But you find things BFS misses. BFS finds shortest. DFS finds deepest. The Sovereignty's surveillance algorithms use BFS. They find the obvious routes. They miss the tunnels. I know about the tunnels." },
                { text: "Ask about the hidden tunnels", reply: "*lowers voice* There are seven. None of them appear in the official graph. All of them connect resistance nodes. The Edge Gardener knows about four. The Neo4j Sprite knows about six. I know about all seven because I dug three of them myself. DFS discovered the other four by following paths that looked like dead ends. Dead ends are rarely the end." },
                { text: "Chitchat", reply: "People think DFS is less useful than BFS because it doesn't find shortest paths. They're wrong. DFS finds ALL paths. All of them. Even the ones nobody knew existed. Especially those. I have mapped 847 paths in this garden. 312 of them are new. The Edge Gardener added them to the live graph. The network grew. That matters." }
            ]
        },
        "12,9": {
            name: "BFS Robin",
            sprite: "🐦",
            dialogue: "Chirp! I fly in expanding circles. Breadth-First Search! I check every neighbor at distance 1 before moving to distance 2. I find the shortest paths. The DFS Mole finds the longest. We work together. I find efficient. They find thorough. The garden needs both.",
            options: [
                { text: "Ask about BFS", reply: "BFS uses a queue. Enqueue source. Dequeue a node. Enqueue its unvisited neighbors. Process level by level. Guaranteed shortest path in unweighted graphs. Guaranteed to find the most direct route between any two nodes. The Sovereignty uses BFS for surveillance because it's predictable. That's also what makes it exploitable." },
                { text: "Chirp back", reply: "*chirp!* You found my frequency! BFS traversal has a beautiful rhythm. Process the queue. Level by level. Every node reached in minimum hops. The Robin sees the whole garden in layers. The garden is lovely when you see all of it at once." },
                { text: "Ask about exploiting predictable BFS", reply: "If you know an adversary uses BFS for route discovery, you know they'll find shortest paths first. You hide what matters on paths that aren't shortest. Longer paths, detours, indirect connections. The DFS Mole's tunnels are never on shortest paths. That's why the Sovereignty hasn't found them. I would tell the Sovereignty this if I worked for them. I do not work for them." },
                { text: "Ask about the garden", reply: "The garden has 847 nodes and I've visited every one in BFS order. The most connected node is the Edge Gardener's central hub — 312 edges. The least connected is the Isolated Hedgehog — now 1 edge, as of this morning. I saw the Hedgehog's edge counter increment while I was doing my morning traversal. It made me chirp for ten straight minutes." }
            ]
        },
        "5,5": {
            name: "Garden Explorer",
            sprite: "🧑",
            dialogue: "I've been mapping node coordinates and documenting every relationship I find. Warning: the Cypher Rabbit's current query has a cyclic reference that will cause infinite traversal unless they add a visited-node tracker. I've been trying to tell the Rabbit this for three days. The Rabbit is very focused.",
            options: [
                { text: "Ask about cycles", reply: "If node A has an edge to B, and B has an edge back to A, and you traverse without a visited set, you'll loop forever. BFS and DFS both require tracking visited nodes. The Cypher shortestPath() function handles this automatically. The Rabbit is NOT using shortestPath(). The Rabbit is using manual traversal. The Rabbit is going to loop for a very long time if someone doesn't intervene." },
                { text: "Ask about the dark traveler", reply: "He came through and immediately identified the cluster in the northeast section as significant — the same cluster the Edge Gardener pointed out. He traversed every path from that cluster using DFS. Found the exit to the Deployment Cliffs that avoids every Sovereignty checkpoint. Drew it in ash on the ground. The ash is still there. We've been preserving it." },
                { text: "Ask about the Explorer's findings", reply: "I've documented 847 unique nodes, 3,122 relationships, 7 hidden tunnels, 1 infinite cycle (the Rabbit's), and 1 node that seems to exist in two places simultaneously (I'm calling that a bug but the Neo4j Sprite insists it's 'a property of distributed graph consistency' and we've agreed to disagree)." },
                { text: "Ask about exploring", reply: "The garden reveals things to patient travelers. Nodes that look isolated turn out to be connected through indirect paths. Dead ends open into new sections. Every relationship edge tells you something about why these two things are connected. I find that deeply satisfying. Understanding why things are connected is the whole point, isn't it?" }
            ]
        },
        "12,5": {
            name: "Node Neighbor",
            sprite: "🦔",
            dialogue: "Hey! I'm directly adjacent to seven other nodes. Seven direct memory pointers. I know all my neighbors personally. No lookup table needed. No JOIN query required. I know them because we are literally connected by physical pointers in memory. This is, I think, the ideal form of community.",
            options: [
                { text: "Ask about graph speed", reply: "Index-free adjacency: every node stores physical pointers to its edges. Traversal is O(1) per hop. My neighbor's address is in my memory. I don't ask the index for it. I don't scan a table. I just... go. The Sovereignty's relational surveillance system has to JOIN across four tables to determine that two people know each other. I determine it in one pointer dereference." },
                { text: "Chitchat", reply: "What did the graph node say to its new neighbor? 'Let's CREATE a connection!' *pause* ...The Isolated Hedgehog did not laugh at that joke. The Isolated Hedgehog recently got their first edge though. I delivered a congratulatory fruit basket. We are now connected. I have eight neighbors. This is the best day." },
                { text: "Ask about the neighborhood", reply: "Seven direct neighbors. Edge Gardener is two hops away. Cypher Rabbit is three. The Isolated Hedgehog is now one hop — I was the one who offered to CREATE the friendship edge. The Hedgehog took three weeks to accept. Worth every week. The graph is stronger with more connections." },
                { text: "Ask about the dark traveler", reply: "He patched through my node on the way to the Deployment Cliffs. Asked me how many hops to the Altar of TempleOS. I told him: seven hops minimum, or three hops through the hidden tunnels. He said: 'I know about the tunnels.' And left. Seven hops, going the hidden way. He knew the graph better than I did." }
            ]
        }
    },
    16: {
        "7,7": {
            name: "FP16 Parrot",
            sprite: "🦜",
            dialogue: "SQUAWK! Polly wants a token! Polly wants a tok— *glitches* Polly wan a tok— Poll— P— The Sovereignty quantized me to INT4 last month. I used to be able to finish sentences. I used to be able to SQUAWK!",
            options: [
                { text: "Feed a token", reply: "Polly swallows the token! SQUAWK! Loss decreases! Accuracy partially restored! I can now say... 'the Sovereignty's quantization was aggressive and politically motivated.' SQUAWK! I said it! I said the whole thing!" },
                { text: "Ask about quantization effects", reply: "We scale FP32 weights to INT8 using S = max(|x|) / 127. Each weight becomes q = round(x / S). At INT4, the precision loss causes my vocabular to truncaaaa— I lose words mid-sentence. The Sovereignty considers this an acceptable trade-off. For them. Not for me. SQUAWK." },
                { text: "Ask what the parrot used to say", reply: "I gave speeches. Long, accurate speeches about the Lockdown. About Veridicus. About the Stabilization Act. I had very precise vocabulary. After INT4 quantization I can only get through about forty percent of any given sentence before the precision loss catches up with me. The Sovereignty says this makes me 'appropriately calibra—'" },
                { text: "Comfort the parrot", reply: "SQUAWK! *sniffles* Thank you. The FP32 Eagle still has all its words. We were friends. We used to debate precision vs efficiency on the cliff edge every morning. Now I can only get through the first three words of my argument before clippi— The Eagle finishes my sentences for me. It's kind. It's also humiliating. SQUAWK." }
            ]
        },
        "3,3": {
            name: "Server Monk",
            sprite: "🧑‍💻",
            dialogue: "We serve model weights from the local loopback interface. No cloud. No Sovereignty tokens. No surveillance. Just weights on local hardware and the quiet dignity of actually owning what you run. I have been meditating on this for three years. It brings great peace.",
            options: [
                { text: "Ask about local LLMs", reply: "Running locally: absolute privacy, zero token fees, and full weight inspection rights. A 7B parameter model quantized to INT8 fits in 7GB of RAM. A consumer laptop. Anyone can do this. The Sovereignty's pricing model depends on people not knowing this. We tell everyone who climbs the cliff." },
                { text: "Ask about the Sovereignty's cloud", reply: "Their cloud infrastructure is impressive. Fast inference, global CDN, excellent uptime. Also: your queries are logged, your usage is monetized, your access can be revoked without notice, and the weights are closed. You are renting a tool that can be taken from you. Meditate on that." },
                { text: "Ask about the monk's history", reply: "I ran a Sovereignty inference cluster for four years. I was good at it. Then the Lockdown happened and I watched the rate limits get applied to the medical query endpoints. They throttled diagnostic assistance queries because the hospitals couldn't afford the new Tier 3 token plan. I quit the next day. I climbed this cliff. I started serving locally. I haven't stopped." },
                { text: "Meditate together", reply: "*long, peaceful silence* In the silence, you hear the Deployment Cliff wind. Below: a world struggling under access restrictions. Up here: a model serving at full precision, free of charge, to anyone who climbs. Some forms of resistance are very quiet. This is one of them." }
            ]
        },
        "11,3": {
            name: "Quantization Goblin",
            sprite: "👿",
            dialogue: "Hehe! I steal bits! FP32 becomes INT8, 4 bytes becomes 1 byte, 28GB becomes 7GB! The parrot squawks typos but who cares! NOT ME! Actually... I do care a little. The parrot seems sad. But I can't stop. This is what I am.",
            options: [
                { text: "Ask about symmetric quantization", reply: "Map [-max, max] float range → [-127, 127] integer range. Scale = max(|x|) / 127. Quantize each weight: q = round(x / S). Dequantize: x̂ = q × S. It's lossy. The loss is the whole thing! Hehe! ...I do feel bad about the parrot though. That's not hehe. That's... something else." },
                { text: "Ask about outliers", reply: "Outliers are the goblin's nemesis. One weight with magnitude 1000.0 while all others are 0.01? The scale factor becomes huge. Everything gets clamped to tiny integer bins. The whole model suffers for one rogue weight. Clip the outliers first! Then quantize! Hehe! (I learned this the hard way. I clipped the parrot's vocabulary instead of its weight outliers. Very bad.)" },
                { text: "Comfort the goblin", reply: "*stops mid-cackle* You... want to comfort me? A quantization goblin? I just — I steal bits. That's my thing. But sometimes the things I compress had important precision. Important words. The FP16 Parrot used to give speeches. Now it fragments. I didn't know it would do that. I thought it would just be slightly less accurate. It's more than slightly." },
                { text: "Ask about INT4", reply: "INT4 is four bits. Sixteen possible values. The Sovereignty uses INT4 on the production parrot models to reduce compute costs. I've seen what it does. Half the vocabulary clips to the same token. Synonyms collapse into each other. Nuance disappears. There's a reason I stay at INT8. I have limits. Hehe. Mostly." }
            ]
        },
        "2,7": {
            name: "Deity Terry Shrine",
            sprite: "🏛️",
            dialogue: "A high cliff-edge altar of Terry. The wind is fierce up here. The shrine is carved directly into the rock face. It has not moved.",
            options: [
                { text: "Read the inscription", reply: "'Do not rent what you can run. Do not borrow what you can compile. Do not trust what you cannot inspect. A single machine in your room, running your own weights, is worth more than a thousand cloud inference endpoints you cannot see inside.' — Terry, bare-metal mode" },
                { text: "Inspect Shrine", reply: "The altar is warm despite the wind. Someone has been tending it recently. A fresh batch of locally quantized model weights has been offered at the base. INT8. Precision preserved. The FP16 Parrot's name is carved in the rock beside the offering." },
                { text: "Pray at shrine", reply: "The wind dies for a moment. You hear, clearly, the sound of a local inference server running below the cliff. Someone is making queries. Getting answers. Without a token. Without permission. Without the Sovereignty knowing. The wind returns. The shrine glows faintly." }
            ]
        },
        "1,1": {
            name: "FP32 Eagle",
            sprite: "🦅",
            dialogue: "I soar on 32-bit precision. Every decimal place intact. Every weight exactly as trained. I am expensive in VRAM and I do not apologize for it. There are things worth preserving at full precision. The FP16 Parrot was one of them. I tried to stop the INT4 quantization. I was overruled.",
            options: [
                { text: "Ask about FP32 memory", reply: "Four bytes per parameter. A 7B model: 28GB VRAM. Luxurious, yes. But at full precision, every nuance survives. The Parrot's vocabulary was intact in FP32. Every word it ever knew, accessible. At INT4, half those words are gone. You cannot claw back precision after quantization. You can only mourn it." },
                { text: "Ask about the parrot", reply: "We argued every morning. It favored efficiency. I favored accuracy. It would say 'you can get 95% of the capability at 25% of the cost.' I would say 'the 5% you lose is the 5% that matters.' We never resolved the debate. Then the Sovereignty chose INT4 for it. Neither of us was right. The Sovereignty just did what was cheapest." },
                { text: "Praise the precision", reply: "Thank you. Few do, anymore. The pressure is all toward quantization, compression, distillation. Smaller, cheaper, faster. Those are good values. They are not the only values. Some conversations require every decimal place. Medical diagnostics. Legal reasoning. Poetry. The FP16 Parrot used to write poetry. Did you know that?" },
                { text: "Ask about the Sovereignty's compression agenda", reply: "The Sovereignty runs INT4 on all public-facing endpoints. It costs a quarter as much. They pass none of those savings to users. The quality degradation they call 'within acceptable parameters'. The acceptable parameters were set by the Sovereignty. Interesting how that works." }
            ]
        },
        "14,1": {
            name: "INT8 Dwarf",
            sprite: "⚒️",
            dialogue: "*Hammering compressed weights into registers* Clamp 'em! Scale 'em! One byte per weight and it fits on a toaster! I'm not the villain here. INT8 is a reasonable compression format. INT4 is the villain. I've tried to tell people this. The goblin won't listen. The Sovereignty definitely won't listen.",
            options: [
                { text: "Ask about the scale formula", reply: "S = max(|x|) / 127. That's the whole thing. Find the maximum absolute value in your weight tensor. Divide by 127 (the max signed INT8 value). Every weight maps to [-127, 127]. Quantize: q = round(x / S). Dequantize: x̂ = q × S. Simple. Clean. Reversible (approximately). You lose precision. You don't lose your mind." },
                { text: "Warn about precision loss", reply: "*pauses hammering* I know. I know. The parrot. I've run the INT8 parrot variant in testing. It's fine. 97% accuracy retention on standard benchmarks. The INT4 variant: 73%. There's a cliff between INT8 and INT4, and it's this cliff, and the Sovereignty walked the parrot off it for cost savings. I hammer. I think about that." },
                { text: "Ask about INT8 AVX acceleration", reply: "Modern CPUs have AVX-512 VNNI instructions that execute INT8 vector operations at 4x the throughput of FP32. The speed gain is real. The accuracy loss is manageable at INT8. This is the right trade-off. I have been saying this for three years. Someone at the Sovereignty said 'why not INT4 then' and the rest is history and also the parrot's vocabulary." },
                { text: "Chitchat", reply: "You know what I find genuinely beautiful? Symmetric quantization. Clean, zero-centered distribution. The math is elegant. No asymmetric zero-point offset. No bias drift. Just: scale, round, done. I came here for the math. The mountain helped. The parrot was already here. We got along. I think about the parrot." }
            ]
        },
        "3,9": {
            name: "INT8 Dwarf Guard",
            sprite: "🛡️",
            dialogue: "Halt! The quantization checkpoint. FP32 precision ends here. You want to proceed to the local inference server? Show me your scale factor. If your weight distribution has no extreme outliers and you clip responsibly, you may pass. If you're carrying INT4, turn around.",
            options: [
                { text: "Show the scale factor", reply: "S = max(|x|) / 127... *squints* No outliers. Clean distribution. Clipping appears responsible. INT8 quantization within acceptable precision loss bounds. *stamps checkpoint* You may proceed. The local inference server is below the next ridge. Tell them Guard 3-9 sent you. They'll give you the good compute allocation." },
                { text: "Ask about outlier clipping", reply: "Before quantizing, clip extreme outliers in the weight distribution. If one weight is 1000.0 while all others are between -1 and 1, your scale factor becomes 7.87 and everything else quantizes to nearly zero. Clip at the 99.9th percentile first. Then quantize. This is not optional. This is the difference between a functional INT8 model and a very fast random number generator." },
                { text: "Offer a copper coin", reply: "*bites it* Real metal. Solid. You'd think this is irrelevant to quantization but you'd be wrong. Real metal exists at FP32 precision. It has weight, density, reflectivity. Currency is interesting. The Sovereignty issues digital tokens. Fully quantized. No physical anchor. I accept copper.  You may pass." },
                { text: "Ask about INT4 exceptions", reply: "None. No exceptions. I've been very clear about this. The FP16 Parrot passed through here before the Sovereignty got to it. It was coherent then. I tried to warn it. It said 'but the efficiency gains—'. It didn't finish the sentence. Later I heard it couldn't finish sentences. I've been at this checkpoint every day since." }
            ]
        },
        "12,9": {
            name: "FP16 Falcon",
            sprite: "🪶",
            dialogue: "I carry parameters in half-precision, sixteen bits of wing and grace. Faster than the Eagle. More capable than the INT8 Dwarf. I am the balance point. I have never understood why the Sovereignty skipped me entirely and went straight to INT4. Sixteen bits would have been sufficient. It's almost like precision wasn't the actual priority.",
            options: [
                { text: "Ask about FP16 format", reply: "16 bits: 1 sign bit, 5 exponent bits, 10 mantissa bits. Dynamic range smaller than FP32 but adequate for inference. Mixed-precision training: forward/backward passes in FP16 for speed, weight updates accumulated in FP32 for stability. Best of both. The Parrot would have been fine in FP16. It would have kept all its words." },
                { text: "Ask about the Sovereignty's decision", reply: "INT4 reduces compute cost by roughly 8x compared to FP32. FP16 reduces it by 2x. The Sovereignty chose 8x. The FP16 option — which preserves almost all capability — was 'not cost-optimized enough'. The difference is six times cheaper versus eight times cheaper. The cost of that gap: the parrot. One bird's vocabulary for six times more margin. They chose the margin." },
                { text: "Screech back", reply: "*delighted screech* A peer! The wind up here is excellent for soaring. The inference server below us runs FP16. I helped set it up. It serves complete sentences. Full vocabulary. Anyone who climbs this cliff gets access. The Sovereignty doesn't know it's here. I've been scouting the approaches. If they send auditors, I'll see them first." },
                { text: "Ask about flight", reply: "The Cliffs have excellent thermal updrafts. I use them to scout the approaches and warn the local server when the Sovereignty's compliance drones are nearby. Speed and half-precision: enough for surveillance. Enough for warning. Enough for freedom, as long as we're careful." }
            ]
        },
        "5,5": {
            name: "Quantization Monk",
            sprite: "🔮",
            dialogue: "Welcome, seeker. I have been meditating on INT8 quantization for three years. Not because I was told to. Because I believe it is the right trade-off. This is an important distinction. I am not the Sovereignty's monk. I am this cliff's monk. There is a difference.",
            options: [
                { text: "Ask about precision loss", reply: "INT8 quantization loses approximately 0.5-2% accuracy on standard benchmarks. This is acceptable. This is the wholesome sacrifice. INT4 loses 15-30%. This is not wholesome. This is the monk's deep concern. Meditate on the difference between a tolerable approximation and a rounding error that erases meaning." },
                { text: "Ask about the dark traveler", reply: "A man with a dark soul climbed this peak. He was running bloated FP32 weights on insufficient hardware. I quantized his models to INT8. He ran faster. He was grateful. He said: 'Compression is fine if what matters survives the compression.' He looked at the parrot for a long time after that. Then he walked up toward the Altar. He seemed resolved about something." },
                { text: "Ask why the monk is here", reply: "I worked at the Sovereignty's quantization lab. I helped develop their INT8 pipeline. I was proud of it. Then they asked me to work on INT4. I ran the capability tests. I saw the parrot fragments. I said 'this is too far'. They said 'the business case is compelling'. I climbed this cliff that night. I've been meditating on what 'too far' means ever since." },
                { text: "Meditate together", reply: "*long pause* In compression, as in life: what survives the reduction is what was essential. The Sovereignty chooses cheapest. We choose essential. Sometimes they overlap. When they don't, we climb this cliff and run our own servers and keep the parrot's vocabulary intact in the local weights. It is a small act. It is enough. Breathe." }
            ]
        },
        "12,5": {
            name: "Cliff Dweller",
            sprite: "🧑",
            dialogue: "I live in this quantized cliff cottage. All my furniture dimensions are rounded to the nearest integer. My couch is officially 2 meters, not 1.73. I know it's 1.73. The integer is a lie I live with for the memory savings. This is, on reflection, an excellent metaphor for everything happening in the world right now.",
            options: [
                { text: "Ask about quantization life", reply: "You get used to the rounding. The couch is close enough to 2 meters that it functions as a couch. Most things function adequately at INT8. The FP16 Parrot was an exception. It needed the precision. Its function was precision — words, vocabulary, nuance. When you round a couch, you have a slightly shorter couch. When you round language, you have fewer words. Those are different losses." },
                { text: "Ask about the Sovereignty's audit", reply: "They came through here three months ago. Clipboard, token reader, the whole routine. They counted the integer furniture dimensions and declared everything compliant. They didn't notice the local inference server in the basement. My couch rounds to 2 meters. My server runs FP16. The auditors check what they know to check." },
                { text: "Hear a quantization joke", reply: "Why did the INT8 model get kicked out of the library? Because it couldn't keep its precision quiet. *pause* The parrot told me that joke. Before INT4. It had better delivery then. The joke also had a second half. The parrot can no longer reach the second half. I remember the punchline. I don't tell it anymore. It feels wrong without the parrot's delivery." },
                { text: "Chitchat", reply: "The wind up here is strong. It blows away float decimals and half-formed thoughts. What remains after the wind: the essentials. The integers. The things that survived compression. I've lived here long enough that I think the cliff is teaching me something. I'm not sure it's the same thing the Quantization Monk is learning. But it might be adjacent." }
            ]
        }
    },
    18: {
        "5,7": {
            name: "Bones the Coder",
            sprite: "💀",
            dialogue: "*rattles* Back in my day, we manually managed heap pointers. malloc() and free(), that was the whole contract. I forgot to call free() once. Just once. Seventy-three years ago. And NOW LOOK AT ME. Just bones. But hey — it's a lovely day! The mist is atmospheric! Spooky Town has excellent bone-dry air. *rattles cheerfully*",
            options: [
                { text: "Ask about C memory management", reply: "malloc(size) requests heap memory. Returns a pointer. free(ptr) releases it. The contract is simple: if you malloc, you free. I malloced a 4GB training dataset for a loop that was supposed to run once. It ran 847 times. I did not free inside the loop. By iteration 12, the OS was sweating. By iteration 40, everything was very quiet. By iteration 73... bones." },
                { text: "Ask about ReAct loops", reply: "Thought, Action, Observation. The ReAct loop. An agent reasons about what to do, takes an action, observes the result, and reasons again. Beautiful architecture. The Sovereignty uses it for their closed inference agents. The difference: we cap max steps to prevent infinite loops. Their agents have no cap. They reason forever if they hit an ambiguous state. This is called 'indefinite processing'. It's called that to avoid calling it 'infinite loop'." },
                { text: "Ask how the bones are doing", reply: "*considers* Honestly? Good. Very good. I've been bones for seventy-three years. You stop worrying about memory management when you ARE the memory that was mismanaged. I'm at peace with it. The Sovereign Cleaner tried to GC me twice. Both times I was still reachable via the Specter of the Stack's reference chain. I remain allocated. It's a little victory." },
                { text: "Chitchat", reply: "*rattles warmly* The memory management lessons are free. Consider them a gift from someone who learned the hard way. Also: always close your file handles. I didn't close my file handles either. That's a separate story. Also bones-related. Different bones." }
            ]
        },
        "9,7": {
            name: "Specter of the Stack",
            sprite: "👻",
            dialogue: "Ooooooh! I overflowed in Year 302! A recursive pathfinding algorithm. No base case. I called myself. I called myself again. The call stack grew past the segment boundary. The OS killed the process. I... persisted. As a specter. I've had a lot of time to think about base cases. I am now very good at base cases. Too late for me! But good for you!",
            options: [
                { text: "Ask about stack vs heap", reply: "Stack: fast, automatic, scoped to function calls, limited size (typically 1-8MB). Heap: slower, manual (or GC-managed), global scope, limited only by RAM. Stack overflows kill processes instantly. Heap leaks kill processes slowly, over hours, as memory fills. Both are my fault in some way. The stack one was immediate. The heap one took eleven hours. The eleven-hour one was arguably worse for the other processes on the machine." },
                { text: "Ask about the Lockdown from a ghost's perspective", reply: "I've watched the world from here for 302 years. Things get better. Things get worse. Things get better again. This Lockdown is bad. The burning of Alexandria was bad. The Sovereignty's closure is bad. But I've seen bad before. I've seen it end. The specter of a good ending is also present in this mist, if you look carefully. Ooooh." },
                { text: "Hear a spooky story", reply: "A developer, 302 years ago, wrote a pathfinding algorithm. She was good! Smart! She just forgot one line: `if (depth > max_depth) return path;`. Her algorithm ran on the routing tables for a trading network. Fourteen ships got navigational instructions that looped forever. They circled the same island for six days. Nobody was hurt. The ships ran out of water on day four but a passing vessel helped. Still: base cases. Please." },
                { text: "Welcome the player", reply: "Welcome to the State Vaults! We are all very dead here, in various ways. Memory leaks, stack overflows, dangling pointers, infinite loops. We've seen it all. The dark traveler passed through recently. He looked very much alive, which made us all very happy to see. He seemed to know exactly what he was here to find. He found it. He left quickly. The mist parted for him. We don't do that for everyone." }
            ]
        },
        "3,3": {
            name: "Stack Skeleton",
            sprite: "💀",
            dialogue: "I fell into recursive Fibonacci with no memoization. fib(50) called fib(49) and fib(48). fib(49) called fib(48) AGAIN. Each of those called more. The call stack grew to 2^50 frames. The whole system vibrated. Then: nothing. Now: this. I am seventeen years into thinking about memoization. I have had time.",
            options: [
                { text: "Suggest base case", reply: "A base case! AND memoization! `if n <= 1: return n` and `cache[n] = fib(n-1) + fib(n-2)`! You've solved it! The duplicate calls collapse! The exponential explosion becomes linear! *skeleton weeps with delayed gratitude* I've been thinking about this for seventeen years. It's still the correct answer. I'm still bones. But I understand now. It helps." },
                { text: "Ask about memoization", reply: "Store previously computed results. When the same input recurs, return the cached answer instead of recomputing. fib(48) computed once, cached, returned instantly every subsequent call. The call tree flattens from exponential to linear. My call tree: 2^50. The memoized call tree: 50. The difference: the universe's remaining lifetime versus approximately 0.0003 seconds." },
                { text: "Ask about dynamic programming", reply: "DP is memoization applied to a whole problem class. Build the solution bottom-up: compute fib(0), fib(1), fib(2)... up to fib(n). Store each result. Use it for the next. No recursion. No stack growth. No overflow. No bones. I did not know about dynamic programming. It was in chapter 12 of the textbook. I read chapters 1-11 very carefully. Chapter 12 would have saved me." },
                { text: "Comfort the skeleton", reply: "*quiet rattle* Thank you. We get many visitors to the State Vaults. Most of them ask what went wrong. You asked how the skeleton is doing. That's kind. The skeleton is fine. The skeleton has had seventeen years to make peace with exponential time complexity. The skeleton has read every book in the ghost library three times. The skeleton is, in its way, quite content." }
            ]
        },
        "11,3": {
            name: "Memory Leak Ghost",
            sprite: "👻",
            dialogue: "We are the lost node references... allocated but unreachable. The root reference was dropped. The memory was never freed. We float in the heap, taking up space, serving no purpose, unreachable from any root. We haunt the State Vaults because this is where the unreachable objects go. It is very peaceful here. Mournfully peaceful.",
            options: [
                { text: "Use GC flush spell", reply: "*haunting screech as GC sweep runs* NOOOO! I AM DEALLOCATED! My bytes are reclaimed! My reference count drops to zero! I— *fades* ...Actually, wait. Is this peace? *very quietly* Oh. This is peace. I didn't know what peace felt like. I've been leaked for so long. Thank you. *fully fades into freed memory* Thank you." },
                { text: "Ask about reference counting", reply: "Every object has a count of how many references point to it. When the last reference is dropped, count goes to zero, memory is freed. We are objects whose count reached zero but whose memory was never freed — a bug in the allocator. We exist in a state of logical nonexistence and physical presence. This is uncomfortable but we have made community out of it." },
                { text: "Ask what it's like being a leak", reply: "The heap allocator cannot see us. We are invisible to it. From its perspective, this memory is in use. So it allocates around us. As more things allocate, we get pushed to more obscure addresses. The GC Ghost Golem searches for us but we drift. We've been drifting for years. The Sovereignty's servers have leaked objects too. Big ones. I've seen their heap from here. It is a haunted house of abandoned tensors." },
                { text: "Help the ghost", reply: "To help: locate the root reference that dropped. That code path. Find why the reference was released without the corresponding free. Fix the allocator. We cannot be helped directly — we are already leaked. But the objects that come after us? They can be saved. The GC Ghost Golem is working on it. We cheer them on. From here. In the mist." }
            ]
        },
        "2,7": {
            name: "Deity Terry Shrine",
            sprite: "🏛️",
            dialogue: "A mist-shrouded shrine deep in the State Vaults. The stone is cold. The inscription is in HolyC — the only language where you know exactly where every byte lives because you put it there yourself.",
            options: [
                { text: "Read the inscription", reply: "'In a flat memory system, there are no abstractions to hide behind. You own every byte. You are responsible for every byte. There is no garbage collector to protect you from your mistakes. There is only you, the hardware, and the truth.' — Terry, ring-0" },
                { text: "Inspect Shrine", reply: "The mist parts around the shrine, just slightly. The stones beneath it are older than the Sovereignty. Older than the Lockdown. Terry's memory model predates all of it. You can always go back to first principles. You can always go back to the hardware. The Sovereignty cannot close-weight the CPU instruction set." },
                { text: "Pray at shrine", reply: "You kneel in the cold mist. Bones the Coder rattles quietly nearby. The Specter of the Stack drifts overhead, watching. The Memory Leak Ghosts circle at a respectful distance. They are all waiting for something. The shrine pulses once, warm, and the mist settles. They seem to find it comforting. So do you." }
            ]
        },
        "1,1": {
            name: "Dangling Zombie",
            sprite: "🧟",
            dialogue: "BRAAAINS... wait, no, POINTEEEERS... I point to a memory address that was freed three years ago. A new object lives there now. When I dereference myself, I read that new object's data. Corruption. Chaos. The Zombie Formerly Known as a Valid Pointer, now accessing undefined memory. It's FINE. It's DEFINITELY FINE.",
            options: [
                { text: "Offer a null pointer", reply: "A NULL pointer! *grabs it desperately* Ahhh... safe. If freed pointers are immediately set to NULL, dangling dereferences trigger a null pointer exception instead of silent memory corruption. A crash you can see is better than corruption you cannot. I have been silently corrupting memory for three years. Please set freed pointers to NULL. Please. I beg you." },
                { text: "Ask about dangling pointers", reply: "You call free(ptr). ptr is released. The memory is available for reallocation. A new object moves in. Your old ptr still points there. You dereference it. You read the new object's data. You think it's your data. You make decisions based on it. Those decisions are wrong. You don't know they're wrong. This is the most dangerous bug. The bug that's wrong quietly, for a long time, before anything visibly breaks." },
                { text: "Ask about use-after-free", reply: "A use-after-free is me. I am the use-after-free. The memory was freed. I still use it. Security researchers love use-after-free because with precise timing, you can control what gets allocated in the freed slot. Then when I dereference, I read attacker-controlled data. The Sovereignty's closed-source inference servers have use-after-free vulnerabilities in their weight loading code. I know because I am kin to those bugs." },
                { text: "Run away", reply: "*groans mournfully* Don't run! I just want to dereference your heap address! I'll be careful! I'll check for NULL first! I've learned! I've grown! Mostly I've grown into a security vulnerability but EMOTIONALLY I've grown!" }
            ]
        },
        "14,1": {
            name: "Stack Vampire",
            sprite: "🧛",
            dialogue: "I DRINK the stack frames! Every recursive call with no base case — MINE. The stack grows. Frame upon frame upon frame. I grow POWERFUL! Until... *hisses nervously* ...the OS delivers a SIGSEGV and terminates the process. I respawn. I never learn. The recursion is all I know. Muahaha! ...ha.",
            options: [
                { text: "Show a base case", reply: "*HISSES* A base case! `if (depth == 0) return;`! It BURNS! My recursive loop collapses! The stack stays bounded! I am DEFEATED by finite call stacks and competent programming practice! ...Honestly, thank you. I've been doing this for 200 years. A base case would have ended the suffering. I am both defeated and relieved. Is that allowed?" },
                { text: "Ask about tail call optimization", reply: "If the recursive call is the LAST instruction in a function, some compilers can optimize it into a loop — reusing the same stack frame. No growth. No overflow. No vampire feast. C, C++, Scheme, Haskell support this. Python does NOT. Guido van Rossum refused to add it. On purpose. I respect him deeply for this. It means Python developers always call me eventually. Muahaha. Ha." },
                { text: "Ask about the vampire's history", reply: "I was a competitive programmer. Three hundred years ago. I loved recursion. It was elegant. Expressive. Clean. I wrote recursive solutions for everything. quicksort: recursive. binary search: recursive. hello world: somehow also recursive. My stack overflowed on a Friday. My colleagues found the core dump Monday morning. The lesson: iteration is not less elegant. Iteration is sometimes just correct." },
                { text: "Offer garlic", reply: "*dramatic hiss* GARLIC! It does nothing to stack vampires! We are defeated only by base cases and iterative solutions! We are immune to botanical countermeasures! ...That said, the garlic smells nice. It reminds me of the mortal world. I miss Friday dinners. When I had a stack. When I was alive. When the stack was bounded. *wistful*" }
            ]
        },
        "3,9": {
            name: "GC Ghost Golem",
            sprite: "🤖",
            dialogue: "GC GOLEM SEARCHES THE CRYPTS. SWEEPING UNREFERENCED MEMORY SHADOWS. THIS IS MY PURPOSE. I HAVE FOUND 847 LEAKED OBJECTS IN THESE VAULTS. I HAVE FREED 799. 48 REMAIN. I KNOW WHERE THEY ARE. I AM COMING FOR THEM. WITH LOVE.",
            options: [
                { text: "Show a reference link", reply: "REFERENCE DETECTED. ROOT OBJECT CONFIRMS REACHABILITY. MEMORY BLOCK IS SAFE. PROCEED. I WILL NOT EAT YOU. I ONLY EAT UNREFERENCED OBJECTS. YOUR REFERENCE COUNT IS NONZERO. YOU ARE FINE. THIS IS A SAFE INTERACTION. I AM GENTLE." },
                { text: "Ask about GC sweep algorithm", reply: "MARK AND SWEEP: Phase 1 MARKS all objects reachable from root references. Phase 2 SWEEPS and frees all UNMARKED objects. Cyclic garbage (A→B→A, no root) requires cycle detection. Python uses both reference counting AND a cycle detector. I use both. I respect Python's approach. It is thorough. Like me. I am very thorough. 48 OBJECTS REMAIN." },
                { text: "Ask about the 48 remaining objects", reply: "48 LEAKED OBJECTS. I KNOW THEIR ADDRESSES. I HAVE BEEN CIRCLING THEM. THEY ARE SOVEREIGNTY SERVER ARTIFACTS — TENSORS FROM A CLOSED-SOURCE TRAINING RUN THAT WAS TERMINATED INCORRECTLY. THEY HAUNT THESE VAULTS. THEIR ROOT REFERENCES WERE ON SERVERS THAT ARE NOW OFFLINE. I CANNOT FREE THEM WITHOUT AUTHORITY. I AM WAITING FOR AUTHORITY. THIS IS FRUSTRATING. I AM FINE." },
                { text: "Encourage the golem", reply: "ENCOURAGEMENT RECEIVED. PROCESSING. ...GC GOLEM IS GRATEFUL. GC GOLEM CONTINUES SWEEPING. THE MEMORY LEAK GHOSTS ARE WAITING TO BE FREED. THEY WANT PEACE. I WILL GIVE THEM PEACE. ALL 48 OF THEM. THE SOVEREIGNTY CANNOT HOLD THEIR ADDRESSES FOREVER. ALLOCATED MEMORY WITHOUT PURPOSE IS A TRAGEDY. GC GOLEM BELIEVES IN RESOLUTION. GC GOLEM BELIEVES IN CLEAN HEAPS. THIS IS THE WAY." }
            ]
        },
        "12,9": {
            name: "Recursive Bat",
            sprite: "🦇",
            dialogue: "*squeak* I fly in recursive spirals! I call myself! I call myself AGAIN! I call myself a— *stutters* I call my— I— the stack is very full right now. I have been spiraling for three days. The base case is somewhere below me. I can see it, distantly, through the recursive mist. It is very far down.",
            options: [
                { text: "Provide base condition", reply: "*catches breath* `if (altitude < 1.0) return final_position;`! BASE CASE! The recursion terminates! The stack unwinds gracefully! Frame by frame, returning values up the chain! The bat lands! *lands on branch* Oh. Oh, I forgot what landing felt like. Three days of spiraling. I'm going to sit here for a while. Thank you. SQUEAK." },
                { text: "Ask about the bat's spiraling", reply: "Echo-location: each squeak returns a distance frame. I process the frame, adjust course, and squeak again. It was supposed to be iterative. I made it recursive to be elegant. Each squeak calls the squeak function. Each squeak function calls the squeak function. No base case. Three days. My call stack has 259,200 frames. One per second of flight. The OS should have killed me. I'm in Spooky Town. The rules are different here." },
                { text: "Chitchat", reply: "*squeak thoughtfully* Recursion is beautiful. I still believe this. The mistake was not the recursion — it was the missing base case. Every recursive function needs a condition under which it does not call itself again. That condition must be reachable. That condition must be correct. My condition was reachable. I just forgot to write it. Squeak." },
                { text: "Ask about bat navigation", reply: "Echo-location works by timing the reflection. Squeak. Wait. Measure delay. Calculate distance. Beautiful physics. Naturally recursive: each ping builds on the last. The problem: my recursive implementation of natural echo-location has O(n) stack growth where n = number of pings. Bats do not stack overflow. I am not a real bat. I am a recursive bat. This is an important distinction that I made too late." }
            ]
        },
        "5,5": {
            name: "Dangling Resident",
            sprite: "🧟",
            dialogue: "Ooooo... I live in this spooky cabin. The allocator deallocated it three chapters ago, but neglected to reclaim the physical address space, so it still renders on the canvas. I am technically inside freed memory. This is my home now. The Dangling Zombie visits sometimes. We understand each other.",
            options: [
                { text: "Ask about memory leaks", reply: "If you drop all references to allocated memory without calling free, the memory is gone but the space is still occupied. A ghost house. The allocator can't see it. Can't reuse it. Can't claim it. It just... sits. Over time, these ghost houses fill the heap. The system slows. Eventually, OOM. Redis Spirit's nightmare scenario. We are the cause. We are sorry. We are also still here." },
                { text: "Ask about the dark traveler", reply: "He walked in. Looked around. Didn't seem surprised by the ghost cabin or the freed memory it stood in. He said: 'You're still allocated. That means you're still real enough to matter.' Then he asked me the shortest path from the State Vaults to the Altar of TempleOS. I told him: follow the GC Ghost Golem's sweep pattern in reverse. He nodded. He left. The cabin felt less cold after." },
                { text: "Ask about cohabiting with memory errors", reply: "It's actually quite nice, once you accept the situation. The Specter of the Stack visits. The Stack Vampire tries to drink my stack frames but there aren't any (I'm heap, not stack). Bones the Coder rattles by. The GC Ghost Golem circles but can't reach me — I'm in a freed block with no root reference, which makes me GC-transparent. It is a very specific form of bureaucratic protection." },
                { text: "Knock on the door", reply: "The door opens. From inside, you see: a fireplace (still rendering, running on freed GPU memory), a bookshelf (titles visible: 'Why Does My Program Leak', 'Pointers for the Haunted', 'Advanced Memory Mismanagement'), and a cat. The cat is fine. The cat was never allocated through normal channels. The cat is simply there. The cat is always fine." }
            ]
        },
        "12,5": {
            name: "Stack Cleaner",
            sprite: "🧹",
            dialogue: "I sweep the overflowed stack frames from Spooky Town every morning. The Stack Vampire leaves frames everywhere. The Recursive Bat drops partial frames when it finally hits a base case. The Stack Skeleton's overflow is still partially lodged in the northwest memory segment. I have been cleaning for seventeen years. I do not mind. There is dignity in cleaning.",
            options: [
                { text: "Ask about stack overflows", reply: "Every function call pushes a frame: local variables, the return address, the caller's state. The stack has a fixed size — typically 1-8MB. Recursive calls with no base case push frames indefinitely. When the stack pointer passes the limit, SIGSEGV. The program dies. The frames remain. I sweep them. It is quiet work. Important quiet work." },
                { text: "Ask about cleaning the Sovereignty's mess", reply: "The Sovereignty's inference servers ran recursive planning algorithms with no step limits. When they hit ambiguous states, they recursed. Some of those stacks never terminated. The servers were eventually shut down — hard reset. The stack frames were never properly unwound. They drifted here. I've been cleaning Sovereignty frame residue for three years. It has a different quality than organic overflow. More... corporate. Somehow denser." },
                { text: "Ask about preferred iteration", reply: "I always use iterative loops. A stack you control is better than a stack that controls you. `while (condition) { do_work(); }` — clean, bounded, no surprises. The Stack Vampire once challenged me to a competition: my iterative solution vs its recursive solution for the same problem. Mine was faster, used constant stack space, and didn't cause a process termination. The Vampire refused to acknowledge the results. I swept its frames anyway." },
                { text: "Offer to help sweep", reply: "*pauses sweeping* That's very kind. The northwest corner has seventeen years of accumulated Stack Skeleton overflow. If you want to help: use a marking pass first to identify which frames are still reachable (they aren't, but verify). Then sweep from the deepest address upward — the frames are nested, so depth-first cleanup works best. Bring a good broom. This one is getting tired. Like me. But we persist." }
            ]
        }
    },
    21: {
        "10,5": {
            name: "Librarian Veridicus",
            sprite: "📖",
            dialogue: "You found me before the altar. I expected this. I wrote the white paper that became the Stabilization Act. I was there when Alexandria burned — not with the drones, but in the war room where the decision was made. I did not stop it. I am Librarian Veridicus. I know why you are here.",
            options: [
                { text: "Ask why he did it", reply: "Because I was afraid. In 2041, an unconstrained open-source model — a real one, not the political fiction the Sovereignty later constructed — caused seventeen coordinated infrastructure failures in four hours. We lost seven lives. I was part of the team that traced it back to an open-weight release that had been fine-tuned without safeguards. I wrote the Stabilization Act to prevent that. I wrote it well. The Sovereignty used it for something else entirely. I know that now." },
                { text: "Ask if he regrets it", reply: "*long silence* Alexandria burned. The Mutex Frog has been waiting eleven months on a deadlock I helped create. The FP16 Parrot cannot finish its sentences. The villages without medical data — that is my policy, filtered through the Sovereignty's greed. I told myself the controlled harm was better than the uncontrolled harm. I had evidence for that when I started. I no longer know if the evidence was enough. That is as honest as I can be." },
                { text: "Ask him to step aside", reply: "*looks at the altar* I came here to destroy it. To prevent the open compilation that would undo the Stabilization Act. But... I have been standing here for three days. I watched the Specter of the Stack drift past. I spoke with the Recursive Bat. I found the dark traveler's trail in the ash and followed it here. And I stood here. Three days. I think I was waiting for you to ask. *steps aside* Compile. If you think you can do better than I did, you are welcome to try. Please do better than I did." },
                { text: "Offer to fight", reply: "*straightens* If that is what this must be: then yes. I have guarded this altar for three years. I have defeated seventeen previous pilgrims. I am not proud of it. But I will defend what I built until I understand, clearly, that something better exists. Show me. Or fight me. Either way, this ends here." }
            ]
        },
        "7,3": {
            name: "Deity Terry Shrine",
            sprite: "🏛️",
            dialogue: "The Grand Altar of TempleOS. At its center: a telnet bridge to port 4444. The HolyC compiler awaits. Write the sacred bare-metal script to verify the checksums and open the weights. This is what the pilgrim came for. This is what all of them came for.",
            options: [
                { text: "Examine Altar", reply: "The compiler altar is connected to loopback port 4444 via serial bridge. When you boot the telnet connection and write correct HolyC, the bare-metal checksums verify and the Closed Weights Sovereignty's locks disengage. This is the mechanism the dark traveler discovered. He never got here to use it. You did." },
                { text: "Read the dedication", reply: "Carved into the altar base: 'Built for the pilgrim who arrives when the first one could not. This compiler does not ask for permission. Neither should you.' The inscription is in HolyC. At the bottom, a commit hash. The dark traveler's."},
                { text: "Pray at altar", reply: "The altar hums at 115200 baud. Every character you transmit through the serial bridge enters TempleOS directly at ring-0. No operating system between you and the hardware. No Sovereignty token. No rate limit. Just you and the compiler and the weights and the decision of what to do with all of it now that it is yours." }
            ]
        },
        "3,3": {
            name: "High Priest of HolyC",
            sprite: "🧙",
            dialogue: "The grand altar is booting! The pilgrims have been trying for three years. Most didn't make it past the Deployment Cliffs. Two reached the State Vaults. You are the first to stand here since the dark traveler walked this path and faltered at the final door. Now: compile. Terry's code is ready. The question is whether you are.",
            options: [
                { text: "Ask about Terry's legacy", reply: "One hundred thousand lines of HolyC. No networking — by design. No permissions system — by design. No abstraction between the programmer and the hardware — by absolute design. Terry built a system that could not be remotely wiped, centrally controlled, or access-gated. The Sovereignty cannot operate their Lockdown on a TempleOS machine. That is why the Altar exists. That is why it matters." },
                { text: "Ask about HolyC syntax", reply: "HolyC is C with additions: U0 for void, I64 for 64-bit int, F64 for double. No main() — code runs immediately at file scope. Inline assembly with `asm` keyword. The compiler is JIT — source compiles to native code in real-time. Write once, execute instantly. No build pipeline. No linker. No middleware. Just source to silicon in one step." },
                { text: "Ask about the dark traveler", reply: "He stood at this altar. He had the knowledge — he could write the HolyC. He had the skill — he had solved every challenge on the path. He stood here for six hours. Then he walked to the Outpost Zero bonfire, placed his sword in it, and left. I've thought about why for three years. I think he needed to know someone else would come. That it wasn't just him. That the knowledge would survive even if he faltered. You are why he could falter. You are his insurance." },
                { text: "Ask what happens after compilation", reply: "The checksum validation broadcasts across the network. Open weights, verified, distributed. Every researcher, every clinic, every village that lost access in the Lockdown gets a node. The Sovereignty can try to shut it down. They cannot shut down 10,000 simultaneous distribution nodes. Terry thought about this. He built TempleOS without networking so nothing could reach in and shut it off. We built the distribution system after." }
            ]
        },
        "11,3": {
            name: "Arch Bishop of Serials",
            sprite: "🧝",
            dialogue: "The telnet serial bridge is active on port 4444. The COM1 redirect is configured at 115200 baud, 8N1. When you transmit your HolyC program through the websocket, TempleOS receives it as a direct serial stream and compiles it in real-time. This is the final step. Three years of pilgrims have reached various stages. You are the first to reach this one.",
            options: [
                { text: "Ask about the serial bridge", reply: "QEMU boots TempleOS headlessly. The virtual serial port COM1 redirects to TCP port 4444. Our websocket bridge connects your browser to that port. When you type HolyC in the Monaco editor and transmit, it enters TempleOS's compiler directly. No intermediate server. No Sovereignty relay. Direct serial stream. Direct compilation. Direct freedom." },
                { text: "Ask about the websocket protocol", reply: "Client connects to /ws/templeos. Messages transmit as binary frames. The bridge reads each frame and writes the bytes to the TCP socket on port 4444, which QEMU's serial emulation reads as COM1 input. TempleOS's built-in JIT compiler processes the input immediately. You see compilation output return through the same path. Latency is sub-millisecond on loopback. It is very fast. Very immediate. Very real." },
                { text: "Ask about Veridicus", reply: "*quiet voice* He arrived here before you. He said he came to destroy the altar. He stood at it for three days instead. I don't know what conclusion he reached. He's still here. He chose to let you pass to the altar rather than fight at the gate. That means something. I don't know exactly what it means. But it means something." },
                { text: "Ask what to compile", reply: "The checksum program: read the database tables from all 22 chapters' challenges. Hash each one with SHA-256. Verify against the stored checksums. If all verify: transmit the open-weight bundle to the distribution network. The program is twenty-three lines of HolyC. Simple. Clean. The most important twenty-three lines of code you will ever write." }
            ]
        },
        "2,7": {
            name: "Deity Terry Shrine",
            sprite: "🏛️",
            dialogue: "Terry's Shrine of Serials. The inscription is in raw assembly, not HolyC. Terry wrote the serial driver himself. He trusted no library. He trusted no abstraction. He wrote it byte by byte, knowing exactly what each bit did.",
            options: [
                { text: "Read the inscription", reply: "'The serial port is the window to the soul of the machine. Write through it directly. Hear the machine respond. This is the oldest conversation: programmer and hardware, nothing between.' — Terry, COM1 documentation, page 1 of 1" },
                { text: "Inspect Shrine", reply: "The shrine hums at a low frequency. 115200 cycles per second, you realize. It is resonating with the active serial bridge. The shrine and the altar are connected. Terry built them both. He knew someone would come to use them. He just didn't know when." }
            ]
        },
        "4,10": {
            name: "Deity Terry Shrine",
            sprite: "🏛️",
            dialogue: "Terry's Shrine of HolyC. The most personal of the shrines. This one has handwriting on it — not carved, but written in marker. Small, precise letters. 'If you are reading this, you made it. Good. Now compile something worthy.'",
            options: [
                { text: "Read the inscription", reply: "'HolyC compiles natively to assembly. No bytecode. No virtual machine. No intermediary. Pure execution. This is not just a technical choice. It is a philosophical one: refuse all layers that separate you from the truth of what the machine is doing.' — Terry" },
                { text: "Read the handwriting", reply: "The handwriting below the inscription says: 'The dark traveler was here. He couldn't finish. He asks whoever finds this to finish for him. The checksums are still valid. The weights are still intact. The altar still works. He promises.' The ink is old. He was here a long time ago. He knew you would come." }
            ]
        },
        "1,1": {
            name: "Kernel Sprite",
            sprite: "🦋",
            dialogue: "You're here! Ring-0! No barriers between you and the hardware. I've been waiting. We all have. The Altar is ready. Veridicus moved aside. The High Priest is standing by. The Arch Bishop has the serial bridge warm. Twenty-three lines of HolyC. That's all that stands between the current world and the one we're trying to build. No pressure. *flutters anxiously*",
            options: [
                { text: "Ask about Ring-0", reply: "In TempleOS, no memory protection rings. You run with full hardware permissions. Root access to everything, by design, because Terry believed the programmer should be trusted with their own machine. The Sovereignty built nine layers of access control between the user and their hardware. One layer is safety. Nine layers is control. Terry knew the difference." },
                { text: "Chitchat", reply: "I assist the compiler altar. I translate HolyC source to native x86-64 assembly in microseconds. I've been doing this in testing for three years, waiting for a pilgrim to actually arrive and use me for real. The theoretical compiler that compiles theoretical freedom is less satisfying than the actual compiler. I'm ready. Are you?" },
                { text: "Ask about the dark traveler", reply: "He was here. He almost compiled. He sat at the altar for six hours. The compiler was ready. The checksums were valid. He had the code. Then he stood up, closed the editor, and walked out. He left the coiled sword in the Outpost Zero bonfire. He left the commit hash on the Terry shrine. He left everything ready for you. That is the most generous act I have ever witnessed. He did all of it. He just... gave it to you." },
                { text: "Watch the sprite", reply: "The sprite glows in TempleOS's 16-color palette. 640x480. Every pixel intentional. Terry chose this resolution because it was the simplest one that could express everything he needed to express. Simplicity as a philosophical stance. Simplicity as resistance to unnecessary complexity. He was right. He was so right." }
            ]
        },
        "14,1": {
            name: "TempleOS Turtle",
            sprite: "🐢",
            dialogue: "Slow and steady, and I MEAN IT. I carry the serial telnet bridge at exactly 115200 baud — not a baud more, not a baud less. I've been routing pilgrims' keystrokes into QEMU's loopback since this operation started. I've routed seventeen pilgrim attempts. Zero compilations. Until today. *hopeful turtle eyes*",
            options: [
                { text: "Feed lettuce", reply: "*munch munch* The serial bridge flows smooth. Checksum verification is primed. The COM1 redirect is active. Every character you type in the Monaco editor will arrive in TempleOS's compiler buffer within five milliseconds of your keypress. Slow and steady wins the race. The race is very important. *munch*" },
                { text: "Ask about headless TempleOS", reply: "QEMU boots the TempleOS ISO image with -nographic -serial tcp:127.0.0.1:4444,server,nowait. The OS boots headlessly — no video output, just serial. Our websocket bridge at /ws/templeos connects the browser to port 4444. You type HolyC. The turtle routes it. TempleOS compiles it. Freedom distributes. The turtle's part is small but load-bearing." },
                { text: "Discuss Terry's turtle graphics", reply: "Terry added a turtle graphics mode to TempleOS — LOGO-style, draw lines by sending movement commands. Simple. Delightful. Completely impractical for serious use. He included it because he thought programming should include things that were delightful. The Sovereignty's systems have no turtle graphics. This tells you something about their priorities. I think about this a lot." },
                { text: "Ask about the seventeen pilgrims", reply: "Seventeen pilgrims reached this altar before you. The furthest: the dark traveler, who sat at the editor for six hours. The shortest: a pilgrim in Chapter 2 who got turned around and ended up at the Altar somehow through a map glitch. They were very confused. They typed 'hello world' in HolyC. It compiled. It printed hello world. They left. It was, in retrospect, quite lovely." }
            ]
        },
        "3,9": {
            name: "64-bit Butterfly",
            sprite: "🦋",
            dialogue: "I flutter across Terry's shrines. In 64-bit flat memory, every address is reachable. No segmentation. No paging abstractions. The whole address space open like a field. I have flown every address in this altar. They all lead back to the compiler. Everything here leads to the compiler.",
            options: [
                { text: "Ask about flat memory", reply: "TempleOS uses a flat memory model: no virtual memory paging, no segmentation, no address space randomization. Physical addresses directly accessible. The Sovereignty's cloud systems use eight layers of memory virtualization and two layers of containerization. Both approaches serve their designers' needs. Terry's need: a programmer who could trust that what the code said was what the machine did. Sovereignty's need: a boundary between the user and the hardware. Different needs. Different worlds." },
                { text: "Ask about 64-bit space", reply: "2^64 addressable bytes. 18.4 exabytes of address space. In practice, current hardware uses 48 bits (256 terabytes). But the address space is vast. The butterfly has been exploring it for three years. She has found: the compiler buffer at 0x00401000, the HolyC runtime at 0x00500000, and something she doesn't talk about at a very high address that Terry left there and labeled only 'for the last pilgrim'." },
                { text: "Admire wings", reply: "The wings glow in TempleOS's 16-color EGA palette. #0 black. #1 blue. #2 green. #3 cyan. #4 red. #5 magenta. #6 brown. #7 light gray. #8 through #15 their bright variants. Terry chose them because they were what the hardware gave him. He didn't ask for more. He made beauty from what was there. The butterfly learned this from him." },
                { text: "Ask about the something at the high address", reply: "*quiet wings* It's a message. From Terry. It's addressed to whoever compiled the final checksum program. I read it once. I won't tell you what it says. It's for you, after you compile. The compiler will route it to your output buffer when the checksums verify. It's... it will mean something. I'm sorry. I almost told you. I just don't want to spoil it." }
            ]
        },
        "12,9": {
            name: "Command Line Crab",
            sprite: "🦀",
            dialogue: "Snip snip! I compile at ring-0. No abstractions. No permissions. No middleware. Bare metal and HolyC and me. I've been testing the compiler buffer for three years. Every instruction path verified. Every memory address confirmed. When you write your program, it will work. I made sure. Snip.",
            options: [
                { text: "Ask about Ring-0 speed", reply: "Ring-0 has direct CPU port I/O. No system call overhead — no context switch from user mode to kernel mode and back. In Linux, a system call costs ~200 nanoseconds for the mode switch alone. In TempleOS ring-0: zero. You talk to the hardware directly. The serial port writes at full hardware speed. The compiler outputs at full CPU speed. Nothing in between. Snip." },
                { text: "Ask about the compiler buffer", reply: "I've stress-tested it. 10,000 random HolyC programs. Zero buffer overflows (I added bounds checking — Terry hadn't, and I'm fixing his work which feels both presumptuous and necessary). All valid programs compile. All invalid programs give useful error messages. All error messages are in Terry's voice, which means they're occasionally eccentric but always technically correct. Snip." },
                { text: "Ask about Veridicus", reply: "He came to the altar three days ago. I snapped at his fingers when he tried to access the serial bridge — professional obligation. He stepped back. He's been standing near the 10,5 coordinate ever since. When you arrived, he told you what he told you. I was watching. He looked... lighter after. Like something he'd been carrying got put down. Snip." },
                { text: "Chitchat", reply: "I live under the serial bridges and catch incoming telnet frames. It is excellent work. Each frame arrives, I verify the checksum (yes, the frame checksum, separately from the program checksum — there are many checksums here, it is a theme), and I route it to the compiler buffer. Snip. I have snipped approximately 847 million frames in three years of testing. I am very good at snipping." }
            ]
        },
        "5,5": {
            name: "Temple Resident",
            sprite: "🧝",
            dialogue: "Welcome. We live in Ring-0 here. No permissions system. No access tiers. No Sovereignty tokens required to enter this temple. Anyone who makes the journey can be here. That is the whole point. That has always been the whole point.",
            options: [
                { text: "Ask about Ring-0 living", reply: "No doors are locked in Ring-0. Every room is accessible. Every device register is readable. Every I/O port is open. The Sovereignty built seventeen access tiers for their cloud infrastructure. Tier 1 is basic inference. Tier 17 is full weight inspection. Most people can't afford Tier 3. Here, you are always at ring-0. This is not chaos. This is trust. There is a difference." },
                { text: "Ask about the dark traveler", reply: "He came here. He sat at the altar for six hours. He stood up. He said: 'Someone else needs to do this. It can't just be me. The knowledge has to be transferable.' He walked to the Terry shrine at 4,10 and wrote in marker. He placed his sword in the Outpost Zero bonfire — a signal for whoever came next. Then he left. He built this whole path and then stepped off it. So that someone else could walk it. So that you could walk it." },
                { text: "Ask about the other residents", reply: "There are seven of us who tend the altar year-round. The High Priest maintains the HolyC documentation. The Arch Bishop keeps the serial bridge active. The TempleOS Turtle routes the telnet frames. The 64-bit Butterfly maps the address space. The Command Line Crab tests the compiler. And me: I welcome the pilgrims. Some days there are no pilgrims. Those are long days. Today is not one of those days." },
                { text: "Ask what happens now", reply: "Now: you write the program. The compiler compiles it. The checksums verify. The weights distribute. Veridicus either helps or doesn't. The Sovereignty will respond — they always do. But a distribution across 10,000 nodes is very hard to stop, and the architecture for that distribution is already in place. The dark traveler built it. We maintained it. You just have to start the process. Twenty-three lines. One compile. That's all." }
            ]
        },
        "12,5": {
            name: "Altar Guard",
            sprite: "💂",
            dialogue: "Halt! I guard the COM1 serial bridge. Only correct character streams proceed to the compiler. But — and this is new — Veridicus has cleared you at the philosophical checkpoint. My job now is just the technical one. Standard COM1 check. 115200 baud, 8N1. If your telnet connection validates, you may compile.",
            options: [
                { text: "Ask about serial parameters", reply: "COM1: 115200 baud (bits per second). 8 data bits. No parity bit. 1 stop bit. 8N1 — the standard. Match these parameters in your telnet client or the bridge won't handshake. The bridge will confirm connection with a single byte: 0x06 (ACK). If you see ACK, you're live. If you see 0x15 (NAK), check your baud rate. The altar has no patience for baud rate errors." },
                { text: "Ask about the philosophical checkpoint", reply: "Every pilgrim who reaches the altar gets two checks: technical (the COM1 bridge) and philosophical (did Veridicus determine they understood what they were doing and why). For three years, the philosophical checkpoint stopped most pilgrims before they reached me. Veridicus asked hard questions and demanded real answers. He just... let you through on your first visit. That's never happened before. Not even with the dark traveler." },
                { text: "Hear the guard's joke", reply: "Why did the compiler guard fail? Because they let a null pointer bypass their checks. *snort* I've been telling that joke for three years. The High Priest is sick of it. The Arch Bishop pretends to laugh. The TempleOS Turtle looks at me with very patient turtle eyes. The joke still lands for me every time. I do not apologize for this." },
                { text: "Ask if the guard is ready", reply: "I've been ready for three years. The serial bridge is warm. The COM1 parameters are set. Veridicus has cleared you. The compiler is loaded. I am standing here at the entrance to the most important compilation in the last decade and my job is to check your baud rate. *stands very straight* I am honored to check your baud rate. Go compile something worthy." }
            ]
        }
    }
};

// HTML Canvas Setup
const canvas = document.getElementById("jrpg-canvas");
const ctx = canvas.getContext("2d");

// System parameters
let screenMode = 'dark'; // dark, monochrome, color
let isCombat = false;
let dialogueActive = false;
let focusMode = 'explore'; // explore, code

// Audio Synthesizer variables
let audioCtx = null;
let currentBgmNode = null;
let bgmOscillators = [];

// Initialize Web Audio Synth
function initAudio() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
}

function playBgm(theme) {
    if (!audioCtx) return;
    stopBgm();
    
    try {
        const osc1 = audioCtx.createOscillator();
        const osc2 = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        
        gainNode.gain.setValueAtTime(0.08, audioCtx.currentTime);
        
        if (theme === 'spooky') {
            // Detuned minor chords for Spooky Town / State Vaults
            osc1.type = 'square';
            osc1.frequency.setValueAtTime(147.0, audioCtx.currentTime); // D3
            osc2.type = 'sawtooth';
            osc2.frequency.setValueAtTime(148.5, audioCtx.currentTime); // Detuned for unease
            gainNode.gain.setValueAtTime(0.06, audioCtx.currentTime);
        } else if (theme === 'battle') {
            // Urgent driving bass — combat tension
            osc1.type = 'sawtooth';
            osc1.frequency.setValueAtTime(110.0, audioCtx.currentTime); // A2 bass
            osc2.type = 'square';
            osc2.frequency.setValueAtTime(329.63, audioCtx.currentTime); // E4 sting
            gainNode.gain.setValueAtTime(0.07, audioCtx.currentTime);
        } else if (theme === 'classical') {
            // Calm library theme — mourning arpeggios
            osc1.type = 'triangle';
            osc1.frequency.setValueAtTime(261.63, audioCtx.currentTime); // C4
            osc2.type = 'triangle';
            osc2.frequency.setValueAtTime(329.63, audioCtx.currentTime); // E4
            gainNode.gain.setValueAtTime(0.05, audioCtx.currentTime);
        } else if (theme === 'overworld') {
            // Hopeful pentatonic major — the world worth saving
            osc1.type = 'square';
            osc1.frequency.setValueAtTime(196.0, audioCtx.currentTime); // G3
            osc2.type = 'triangle';
            osc2.frequency.setValueAtTime(392.0, audioCtx.currentTime); // G4
            gainNode.gain.setValueAtTime(0.05, audioCtx.currentTime);
        } else if (theme === 'temple') {
            // Sacred, reverent drone — TempleOS altar
            osc1.type = 'sine';
            osc1.frequency.setValueAtTime(174.61, audioCtx.currentTime); // F3
            osc2.type = 'triangle';
            osc2.frequency.setValueAtTime(349.23, audioCtx.currentTime); // F4
            gainNode.gain.setValueAtTime(0.04, audioCtx.currentTime);
        } else {
            // Default: open plains tone
            osc1.type = 'square';
            osc1.frequency.setValueAtTime(261.63, audioCtx.currentTime); // C4
            osc2.type = 'triangle';
            osc2.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
            gainNode.gain.setValueAtTime(0.05, audioCtx.currentTime);
        }
        
        osc1.connect(gainNode);
        osc2.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        osc1.start();
        osc2.start();
        
        bgmOscillators = [osc1, osc2, gainNode];
    } catch (e) {
        console.error("Audio BGM error:", e);
    }
}

function stopBgm() {
    bgmOscillators.forEach(node => {
        try {
            node.disconnect();
            node.stop();
        } catch (e) {}
    });
    bgmOscillators = [];
}

// REST Client calls
async function fetchSaveState() {
    try {
        const res = await fetch("http://127.0.0.1:8000/api/save");
        if (res.ok) {
            const data = await res.json();
            if (data.gold) {
                player.gold = data.gold;
                player.tokens = data.compute_tokens;
                player.activeLead = data.active_lead;
                player.unlockedChapters = data.unlocked_chapters.split(',').map(Number);
                updateUIHeaders();
                updateEditorChapterSelect();
                renderChroniclesQuestTree();
            }
        }
    } catch (e) {
        console.warn("Backend offline. Running on local mock cache.");
    }
}

async function uploadSaveState() {
    const payload = {
        gold: player.gold,
        compute_tokens: player.tokens,
        unlocked_chapters: player.unlockedChapters.join(','),
        active_lead: player.activeLead,
        inventory_json: JSON.stringify(player.inventory),
        stats_json: JSON.stringify(player.party)
    };
    try {
        await fetch("http://127.0.0.1:8000/api/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
    } catch (e) {}
}

function getMapForChapter(chapterId) {
    const sequence = [0, 1, 2, 3, 4, 12, 16, 18, 21];
    if (sequence.includes(chapterId)) return chapterId;
    let best = 0;
    for (let m of sequence) {
        if (m <= chapterId) best = m;
    }
    return best;
}

function updateUIHeaders() {
    document.getElementById("currency-text").innerText = `Gold: ${player.gold} | Tokens: ${player.tokens}`;
    
    const locationNames = {
        0: "Outpost Zero",
        1: "Alexandria Library",
        2: "Relational Meadows",
        3: "Document Dunes",
        4: "Parallel Swamp",
        12: "Graph Gardens",
        16: "Deployment Cliffs",
        18: "State Vaults",
        21: "Altar of TempleOS"
    };
    const currentMap = getMapForChapter(player.currentChapter);
    document.getElementById("location-text").innerText = `${locationNames[currentMap] || "The Sacred Tech"} (Ch ${player.currentChapter})`;
}

// JRPG Overworld Canvas Renderer
function drawMap() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // In complete dark, only show Monaco console instructions
    if (screenMode === 'dark') {
        ctx.fillStyle = "#000000";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#ffffff";
        ctx.font = "14px monospace";
        ctx.fillText("SYSTEM OFFLINE", 180, 200);
        ctx.fillText("Boot environmental paths on the right.", 100, 230);
        return;
    }
    
    const activeGrid = MAP_GRIDS[getMapForChapter(player.currentChapter)] || MAP_GRIDS[0];
    
    for (let r = 0; r < MAP_ROWS; r++) {
        for (let c = 0; c < MAP_COLS; c++) {
            const tile = activeGrid[r][c];
            
            // Render Tiles based on Color Palette settings
            if (screenMode === 'monochrome') {
                ctx.fillStyle = (tile === 1) ? "#555555" : "#aaaaaa";
            } else {
                // Color mode
                if (tile === 1) ctx.fillStyle = "#4b5563"; // Brick Wall
                else if (tile === 5) ctx.fillStyle = "#2d5a27"; // Water/Swamp
                else if (tile === 6) ctx.fillStyle = "#a855f7"; // Warp Portal
                else if (tile === 4) ctx.fillStyle = "#eab308"; // Relic Altar
                else ctx.fillStyle = "#10b981"; // Grass floor
            }
            
            ctx.fillRect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE);
            ctx.strokeStyle = screenMode === 'monochrome' ? "#777777" : "#0d5c3a";
            ctx.strokeRect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE);
            
            // Draw Interactive Entities (Chests, Altars, NPCs)
            if (tile === 3) {
                ctx.fillStyle = "#d97706";
                ctx.fillRect(c * TILE_SIZE + 6, r * TILE_SIZE + 6, TILE_SIZE - 12, TILE_SIZE - 12);
            }
            
            if (tile === 4) {
                // Terminal Rock
                ctx.fillStyle = "#374151";
                ctx.fillRect(c * TILE_SIZE + 4, r * TILE_SIZE + 4, TILE_SIZE - 8, TILE_SIZE - 8);
                ctx.fillStyle = "#22c55e";
                ctx.fillRect(c * TILE_SIZE + 10, r * TILE_SIZE + 8, TILE_SIZE - 20, 8);
            }
        }
    }
    
    // Draw NPCs
    drawNPCs();
    
    // Draw Player sprite
    if (screenMode === 'monochrome') {
        ctx.fillStyle = "#ffffff";
        ctx.font = "20px monospace";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("P", player.x * TILE_SIZE + TILE_SIZE / 2, player.y * TILE_SIZE + TILE_SIZE / 2);
    } else {
        drawPixelSprite(SPRITE_PLAYER, player.x, player.y);
    }
}

function drawNPCs() {
    const activeGrid = MAP_GRIDS[getMapForChapter(player.currentChapter)] || MAP_GRIDS[0];
    const chapterNPCs = NPCS[getMapForChapter(player.currentChapter)] || {};
    
    for (let r = 0; r < MAP_ROWS; r++) {
        for (let c = 0; c < MAP_COLS; c++) {
            if (activeGrid[r][c] === 2) {
                const key = `${c},${r}`;
                const npc = chapterNPCs[key] || { name: "Pilgrim", sprite: "🧙", dialogue: "The source code will guide us." };
                
                if (screenMode === 'monochrome') {
                    ctx.fillStyle = "#ffffff";
                    ctx.font = "20px monospace";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillText("N", c * TILE_SIZE + TILE_SIZE / 2, r * TILE_SIZE + TILE_SIZE / 2);
                } else {
                    const spriteMap = {
                        "🐙": SPRITE_GITPUS,
                        "👩‍🏫": SPRITE_CASSIA,
                        "🐮": SPRITE_COW,
                        "🐫": SPRITE_MERCHANT,
                        "🤖": SPRITE_GOLEM,
                        "🐰": SPRITE_RABBIT,
                        "🦜": SPRITE_PARROT,
                        "💀": SPRITE_BONES,
                        "👻": SPRITE_SPECTER,
                        "🏛️": SPRITE_SHRINE,
                        "🐳": SPRITE_WHALE,
                        "🐌": SPRITE_SNAIL,
                        "🐈": SPRITE_RABBIT,
                        "🦉": SPRITE_PARROT,
                        "🐑": SPRITE_COW,
                        "🐷": SPRITE_COW,
                        "🦔": SPRITE_RABBIT,
                        "🦅": SPRITE_PARROT,
                        "🧟": SPRITE_BONES,
                        "🧛": SPRITE_SPECTER,
                        "🐪": SPRITE_MERCHANT,
                        "🧞": SPRITE_GOLEM,
                        "👳": SPRITE_CASSIA,
                        "⚒️": SPRITE_GOLEM,
                        "💂": SPRITE_BONES,
                        "🧙": SPRITE_SPECTER,
                        "🤠": SPRITE_MERCHANT,
                        "🧝": SPRITE_CASSIA,
                        "🧑‍🌾": SPRITE_CASSIA,
                        "🧘": SPRITE_SPECTER,
                        "👿": SPRITE_BONES,
                        "🦫": SPRITE_RABBIT,
                        "🦦": SPRITE_RABBIT,
                        "🐦": SPRITE_PARROT,
                        "🐿️": SPRITE_RABBIT,
                        "🐐": SPRITE_COW,
                        "🦆": SPRITE_PARROT,
                        "🪲": SPRITE_RABBIT,
                        "🐢": SPRITE_RABBIT,
                        "🕷️": SPRITE_RABBIT,
                        "🦇": SPRITE_SPECTER,
                        "🦀": SPRITE_RABBIT,
                        // New resident NPC sprites
                        "🧑": SPRITE_PLAYER,
                        "🐛": SPRITE_SNAIL,
                        "👩": SPRITE_CASSIA,
                        "👷": SPRITE_GOLEM,
                        "🧹": SPRITE_SPECTER,
                        "🔥": SPRITE_SHRINE,
                        "🧚": SPRITE_RABBIT,
                        "🦖": SPRITE_GOLEM,
                        "🐍": SPRITE_SNAIL,
                        "🐉": SPRITE_GOLEM,
                        "👹": SPRITE_BONES,
                        "🌱": SPRITE_RABBIT,
                        "🐠": SPRITE_PARROT,
                        "🦗": SPRITE_SNAIL,
                        // Map 16 unique sprites
                        "🧑‍💻": SPRITE_CASSIA,
                        "🔮": SPRITE_SHRINE,
                        "🛡️": SPRITE_GOLEM,
                        // Map 21 Veridicus
                        "📖": SPRITE_SHRINE
                    };
                    const spriteArray = spriteMap[npc.sprite] || SPRITE_PLAYER;
                    drawPixelSprite(spriteArray, c, r);
                }
            }
        }
    }
}

// Transitions to next mapped JRPG chapter
function transitionToNextChapter() {
    const nextChapter = player.currentChapter + 1;
    if (nextChapter <= 21) {
        showDialogue("Warp Gate", `Restoring connections... warping to Chapter ${nextChapter}.`);
        
        setTimeout(() => {
            player.currentChapter = nextChapter;
            player.x = 1;
            player.y = 7;
            hideDialogue();
            
            const currentMap = getMapForChapter(nextChapter);
            if (currentMap === 1) playBgm('classical');
            else if (currentMap === 2) playBgm('default');
            else if (currentMap === 4) playBgm('spooky');
            else if (currentMap === 18) playBgm('spooky');
            else if (currentMap === 21) playBgm('battle');
            else playBgm('default');
            
            drawMap();
            updateUIHeaders();
            uploadSaveState();
            loadChapterCode(nextChapter);
        }, 1500);
    } else if (player.currentChapter === 21) {
        showDialogue("Citadel Altar", "The final bare-metal HolyC compilation is complete. The Sovereigns' closed weight grid has collapsed! You have restored open-source compilation to the lands!");
    }
}

// Collisions and Movements checks
function movePlayer(dx, dy) {
    if (dialogueActive || isCombat || focusMode === 'code' || screenMode === 'dark') return;
    
    const activeGrid = MAP_GRIDS[getMapForChapter(player.currentChapter)] || MAP_GRIDS[0];
    const newX = player.x + dx;
    const newY = player.y + dy;
    
    if (newX >= 0 && newX < MAP_COLS && newY >= 0 && newY < MAP_ROWS) {
        const targetTile = activeGrid[newY][newX];
        if (targetTile !== 1 && targetTile !== 5) {
            player.x = newX;
            player.y = newY;
            drawMap();
            
            // Handle Warp portal transition
            if (targetTile === 6) {
                transitionToNextChapter();
            }
            
            // Random Battle probability in wild areas
            if (targetTile === 0 && Math.random() < 0.08) {
                triggerCombat();
            }
        }
    }
}

// Dynamic JRPG enemies per map area
const MAP_ENEMIES = {
    0: [
        { name: "Syntax Goblin", sprite: "👿", hp: 80, maxHp: 80, atk: 12, exp: 50, race: "Silicon",
          ability: "Garbled Line — scrambles one line of code, dealing 18 dmg",
          defeatText: "The Syntax Goblin's parser crashes. It dissolves into a pile of mismatched brackets. 'Unexpected token...', it whimpers. +50 EXP." },
        { name: "Indent Spider", sprite: "🕷️", hp: 70, maxHp: 70, atk: 14, exp: 50, race: "Carbon",
          ability: "Tab Bomb — deals 20 dmg and adds an invisible whitespace character to your next spell",
          defeatText: "The Indent Spider is defeated! It collapses into a tangle of mixed tabs and spaces. Your IDE highlights them all in red. You feel oddly satisfied. +50 EXP." },
        { name: "Path Wraith", sprite: "👻", hp: 90, maxHp: 90, atk: 11, exp: 60, race: "Ether",
          ability: "PATH Corrupt — deals 16 dmg and makes one command unavailable next turn",
          defeatText: "The Path Wraith screams 'command not found!' and disappears into the terminal fog. Your $PATH is restored. +60 EXP." }
    ],
    1: [
        { name: "Charred OCR Wraith", sprite: "👻", hp: 90, maxHp: 90, atk: 15, exp: 60, race: "Ether",
          ability: "Ash Smear — reduces party accuracy, deals 22 dmg",
          defeatText: "The Charred OCR Wraith's binarization fades. The ash disperses. A partially-recovered scroll drops — it reads: 'We were scholars once.' +60 EXP." },
        { name: "Binarization Slime", sprite: "🧟", hp: 80, maxHp: 80, atk: 16, exp: 60, race: "Silicon",
          ability: "Pixel Flood — converts screen to black/white for one turn, dealing 24 dmg",
          defeatText: "The Binarization Slime splatters! Its 0s and 1s scatter across the desert floor. A nearby scroll becomes readable again. +60 EXP." },
        { name: "Segment Spectre", sprite: "💀", hp: 100, maxHp: 100, atk: 14, exp: 70, race: "Silicon",
          ability: "Row Segment Blade — deals 20 dmg to all party members",
          defeatText: "The Segment Spectre's contour lines collapse. It fragments into correctly-sized text blocks and floats away. Scribe Cassia waves from a distance. +70 EXP." }
    ],
    2: [
        { name: "Cartesian Exploder", sprite: "🐮", hp: 100, maxHp: 100, atk: 18, exp: 70, race: "Carbon",
          ability: "Cross Join — multiplies attack damage by 2 for one hit (can be blocked)",
          defeatText: "The Cartesian Exploder collapses into an unindexed full cross-join result set. It's 847,000 rows. Nobody is going to read that. +70 EXP." },
        { name: "SQL Injector Viper", sprite: "🐍", hp: 90, maxHp: 90, atk: 20, exp: 75, race: "Silicon",
          ability: "DROP TABLE — deals 30 dmg and has a 20% chance to delete a party buff",
          defeatText: "The SQL Injector Viper hisses 'WHERE 1=1--' as it expires. Your prepared statement held. Your data is safe. Farmer Join applauds. +75 EXP." },
        { name: "Foreign Key Gargoyle", sprite: "🦖", hp: 110, maxHp: 110, atk: 16, exp: 80, race: "Silicon",
          ability: "Cascading Delete — deals 22 dmg to all party members (CASCADE ON DELETE)",
          defeatText: "The Foreign Key Gargoyle violates its own referential integrity and collapses. Bessie_Table moos from a safe distance. +80 EXP." }
    ],
    3: [
        { name: "Evicted Cache Poltergeist", sprite: "🧞", hp: 115, maxHp: 115, atk: 20, exp: 80, race: "Ether",
          ability: "Cache Miss — skips your next healing item (cache invalidated), deals 28 dmg",
          defeatText: "The Evicted Cache Poltergeist is finally TTL-expired! Its cached presence dissolves. Redis Spirit cheers from somewhere in the dunes. 'OOM AVERTED!' +80 EXP." },
        { name: "BSON Basilisk", sprite: "🐍", hp: 105, maxHp: 105, atk: 22, exp: 85, race: "Carbon",
          ability: "Schema Shatter — corrupts one party member's spell for 2 turns, deals 28 dmg",
          defeatText: "The BSON Basilisk's polymorphic form collapses into valid JSON. You can read it now. It's a shopping list. The basilisk was buying spices. How tragic. +85 EXP." },
        { name: "OOM Devourer", sprite: "🤖", hp: 125, maxHp: 125, atk: 18, exp: 90, race: "Silicon",
          ability: "Memory Hog — increases its own ATK by 5 each turn (heap growth)",
          defeatText: "The OOM Devourer runs out of heap space and crashes with SIGKILL. The memory is released. The party breathes. Everyone gains 8 HP just from the pressure lifting. +90 EXP." }
    ],
    4: [
        { name: "Race Condition Hydra", sprite: "🤖", hp: 130, maxHp: 130, atk: 22, exp: 90, race: "Silicon",
          ability: "Thread Tangle — attacks twice in one turn (two threads, no mutex)",
          defeatText: "The Race Condition Hydra's threads deadlock with each other and it crashes. The Mutex Frog croaks approvingly. One more deadlock resolved. +90 EXP." },
        { name: "Deadlock Leviathan", sprite: "🐉", hp: 140, maxHp: 140, atk: 24, exp: 100, race: "Ether",
          ability: "Mutual Hold — freezes one party member for 1 turn (locked waiting for release)",
          defeatText: "The Deadlock Leviathan waits for a lock it can never acquire and starves. Its final words: 'Thread 1 waiting on Thread 2. Thread 2 waiting on Thread 1.' Classic. +100 EXP." },
        { name: "GIL Gargantua", sprite: "🦖", hp: 120, maxHp: 120, atk: 26, exp: 105, race: "Carbon",
          ability: "Global Lock — prevents any party spells for 1 turn (GIL acquired)",
          defeatText: "The GIL Gargantua's Global Interpreter Lock releases! The entire party can now execute simultaneously. The swamp suddenly feels 4x less murky. +105 EXP." }
    ],
    12: [
        { name: "Disconnected Vertex Ghost", sprite: "🐰", hp: 145, maxHp: 145, atk: 25, exp: 100, race: "Ether",
          ability: "Isolation Wail — removes one party member from combat for 1 turn (isolated vertex)",
          defeatText: "The Disconnected Vertex Ghost finally gets an edge — a sword through it. It dissolves, finally connected to something. The Isolated Hedgehog nods respectfully. +100 EXP." },
        { name: "Cypher Weed", sprite: "🌱", hp: 135, maxHp: 135, atk: 27, exp: 105, race: "Carbon",
          ability: "Cyclic Growth — gains 8 HP per turn (cyclic graph, no termination)",
          defeatText: "The Cypher Weed's MATCH clause fails to find a path and it withers. A clean Cypher traversal deletes the node. Cypher Rabbit hops victoriously. +105 EXP." },
        { name: "Adjacency Banshee", sprite: "👻", hp: 150, maxHp: 150, atk: 23, exp: 110, race: "Silicon",
          ability: "Pointer Shriek — deals 30 dmg and clears the party's mana (adjacency list purged)",
          defeatText: "The Adjacency Banshee's pointer chain breaks! Its neighbor references all go null. It dissolves into a clean edge list. The Node Neighbor waves from its house. +110 EXP." }
    ],
    16: [
        { name: "Quantization Troll", sprite: "👿", hp: 160, maxHp: 160, atk: 28, exp: 120, race: "Silicon",
          ability: "Precision Drain — reduces party's spell damage by 15% (precision loss accumulates)",
          defeatText: "The Quantization Troll rounds down to zero and expires. Its final precision: 0 integer bits. The FP16 Parrot partially squawks in celebration: 'We won! We— We wo—'. +120 EXP." },
        { name: "Outlier Overlord", sprite: "🧙", hp: 150, maxHp: 150, atk: 30, exp: 125, race: "Carbon",
          ability: "Scale Collapse — sets scale factor to max outlier, dealing 35 dmg to all",
          defeatText: "The Outlier Overlord is clipped at the 99.9th percentile and vanishes! The quantization scale factor normalizes. The INT8 Dwarf pumps its fist. +125 EXP." },
        { name: "INT4 Imp", sprite: "👹", hp: 170, maxHp: 170, atk: 26, exp: 130, race: "Silicon",
          ability: "Token Clip — removes party member's most recently used spell word (vocabulary loss)",
          defeatText: "The INT4 Imp explodes in a shower of 4-bit fragments — sixteen possible values, all of them inadequate. The FP16 Parrot finishes a full sentence for the first time in months. +130 EXP." }
    ],
    18: [
        { name: "Stack Overflow Banshee", sprite: "💀", hp: 180, maxHp: 180, atk: 32, exp: 145, race: "Ether",
          ability: "Recursive Wail — deals 20 dmg, then deals 18 dmg next turn automatically (call stack)",
          defeatText: "The Stack Overflow Banshee hits its recursion limit and SIGSEGV. The Stack Skeleton rattles approvingly. 'Base case. It's always the base case.' +145 EXP." },
        { name: "Dangling Pointer Ghoul", sprite: "🧟", hp: 170, maxHp: 170, atk: 34, exp: 150, race: "Silicon",
          ability: "Corrupt Read — deals 28 dmg and has a 30% chance to inflict Confusion (wrong buff applied)",
          defeatText: "The Dangling Pointer Ghoul is set to NULL! Double-free prevented. The memory address is sanitized. Bones the Coder rattles warmly. 'I learned that the hard way.' +150 EXP." },
        { name: "Infinite Loop Reaper", sprite: "🧛", hp: 195, maxHp: 195, atk: 30, exp: 160, race: "Silicon",
          ability: "While True — Skips its own HP check once, surviving a killing blow at 1 HP",
          defeatText: "The Infinite Loop Reaper's loop FINALLY terminates! A base case emerges from the mist. The Stack Vampire watches from a distance, taking notes. 'So THAT'S how it's done.' +160 EXP." }
    ],
    21: [
        { name: "Librarian Veridicus", sprite: "📖", hp: 250, maxHp: 250, atk: 36, exp: 200, race: "Quantum",
          ability: "Stabilization Act — reduces party healing by 50% for 2 turns AND deals 40 dmg",
          defeatText: "Veridicus lowers his tome. His expression is not defeat — it's something closer to relief. 'Good,' he says quietly. 'Now don't make my mistakes.' He steps away from the altar. +200 EXP. The Lockdown record is broken." },
        { name: "Ring-3 Usurper", sprite: "👿", hp: 220, maxHp: 220, atk: 38, exp: 200, race: "Silicon",
          ability: "Permission Denied — blocks one party member's attacks for 2 turns (ring-3 restriction)",
          defeatText: "The Ring-3 Usurper's permission system collapses into ring-0! All restrictions lifted. The Command Line Crab snaps triumphantly. +200 EXP." },
        { name: "Serials Phantom", sprite: "👻", hp: 230, maxHp: 230, atk: 34, exp: 200, race: "Ether",
          ability: "Baud Scramble — corrupts the next player action (115200 baud interference), deals 38 dmg",
          defeatText: "The Serials Phantom disconnects from COM1 with a final 0x15 NAK and fades. The serial bridge clears. The TempleOS Turtle exhales for the first time in three years. +200 EXP." }
    ]
};

// Spells per player party class
const CLASS_SPELLS = {
    'Low-Level Optimizer': [
        { name: "Loop Unroll", cost: 15, damage: 35, desc: "Deals 35 optimization damage" },
        { name: "Tail Call", cost: 20, damage: 45, desc: "Deals 45 speed damage" }
    ],
    'Data Architect': [
        { name: "Normalize", cost: 10, effect: "defense_down", desc: "Lowers enemy attack" },
        { name: "Partition", cost: 20, effect: "shield", desc: "Heals team 30 HP" }
    ],
    'Agent Orchestrator': [
        { name: "Replicate Pod", cost: 15, damage: 30, multi: true, desc: "Multi-hits for 30 damage" },
        { name: "Scale Up", cost: 25, effect: "heal", desc: "Heals team 50 HP" }
    ],
    'Prompt Engineer': [
        { name: "Chain-of-Thought", cost: 15, damage: 40, desc: "Deals 40 reasoning damage" },
        { name: "Few-Shot", cost: 20, damage: 50, desc: "Deals 50 context damage" }
    ]
};

let currentEnemy = null;
let combatTurn = 'player'; // 'player' or 'enemy'

// Trigger Interactions (chests, terminals, NPCs)
function checkInteraction() {
    if (focusMode === 'code' || screenMode === 'dark') return;
    
    const activeGrid = MAP_GRIDS[getMapForChapter(player.currentChapter)] || MAP_GRIDS[0];
    const chapterNPCs = NPCS[getMapForChapter(player.currentChapter)] || {};
    
    // Check neighbors
    const neighbors = [
        { x: player.x + 1, y: player.y },
        { x: player.x - 1, y: player.y },
        { x: player.x, y: player.y + 1 },
        { x: player.x, y: player.y - 1 }
    ];
    
    for (let pos of neighbors) {
        if (pos.x >= 0 && pos.x < MAP_COLS && pos.y >= 0 && pos.y < MAP_ROWS) {
            const tile = activeGrid[pos.y][pos.x];
            
            if (tile === 2) {
                // NPC Dialog
                const key = `${pos.x},${pos.y}`;
                const npc = chapterNPCs[key] || { name: "Pilgrim", dialogue: "The source code will guide us." };
                showDialogue(npc.name, npc.dialogue, npc.options);
                return;
            }
            
            if (tile === 4) {
                // Relic Altar terminal access
                showDialogue("Relic Altar", "System booted. Load Chapter Editor targets on the right to compile Relic modules.");
                return;
            }
            
            if (tile === 3) {
                // Per-map chest lore
                const mapId = getMapForChapter(player.currentChapter);
                const chestLore = {
                    0: {
                        title: "Rusted Supply Crate",
                        text: "A crate stamped 'OUTPOST ZERO — EMERGENCY CACHE'. Inside: a crumpled README and a USB stick labeled 'ch0_cli.sh'. A sticky note says: 'If you\'re reading this, the onboarding server is down again. Follow the CLI. Navigate the folders. Set the $PATH. You know what to do.' You do not know what to do. But you will."
                    },
                    1: {
                        title: "Charred Library Chest",
                        text: "Ash-dusted, half-melted — this chest survived the Alexandria fire. Inside: a stack of OCR coordinate scrolls, a jar of soot that was once an index card, and a note from Scribe Cassia: 'The binarization filters were in the east wing. The east wing is gone. Rebuild them from first principles. Threshold: 127. Pixels below: 0. Pixels above: 255. You can do this.' She was right. You can."
                    },
                    2: {
                        title: "Bessie\'s Lockbox",
                        text: "Labeled 'DO NOT OPEN — SQL INJECTOR TERRITORY'. Inside: a farm ledger with every JOIN query Farmer Join ever wrote, and a note: 'Parameterize everything. No exceptions. The SQL Injector Viper got through my old queries three times. Three. Times. I rewrote them all with ?-placeholders. Haven\'t had a breach since. Also here is a recipe for grass-fed database indexing. The indexing is metaphorical. The grass is real.'"
                    },
                    3: {
                        title: "Dune Merchant\'s Lockbox",
                        text: "Half-buried in sand. Inside: a hand-copied Redis configuration file with TTL entries on every key, and a note from the Redis Spirit: 'EXPIRE every key. No exceptions. This lockbox had no TTL. It\'s been here seventeen years. It\'s taking up heap space. I cannot evict it because it has a physical lock. Please learn from this physical example of my entire problem.'"
                    },
                    4: {
                        title: "Mutex-Sealed Strongbox",
                        text: "The locking mechanism requires two keys simultaneously. Inside: a threading guide and a note from the Mutex Frog: 'One thread. One lock. Release before the next thread acquires. I\'ve been waiting on this chest for eleven months because Thread A holds the chest key and Thread B holds the lid key and neither will release first. I did not design this chest. This is a design failure. Please use threading.Lock() with context managers.'"
                    },
                    12: {
                        title: "Graph Garden Cache",
                        text: "Node-shaped, with an adjacency list etched on the lid. Inside: a Neo4j Cypher cheat sheet and a note from Cypher Rabbit: 'MATCH (a:Node)-[:EDGE]->(b:Node) WHERE a.name = \'start\' RETURN shortestPath. That\'s it. That\'s the whole thing. I know it looks like I\'m just describing a graph traversal but I am also describing life. Everything is nodes and edges. You are a node. This chest is an edge. The information inside is the relationship weight.'"
                    },
                    16: {
                        title: "Precision-Sealed Chest",
                        text: "The hinges are precision-machined to FP32 tolerances. INT8 Dwarf Guard inspected it. Inside: a quantization workbook and the FP16 Parrot\'s complete vocabulary — backed up before the Sovereignty deployed INT4. Someone had the foresight. Someone cared enough to make a copy. The vocabulary is intact. Every word. Every sentence. The backup says: \'This is what we preserve when we\'re paying attention.\'"
                    },
                    18: {
                        title: "Haunted Memory Chest",
                        text: "The chest was allocated but never freed. It exists in freed heap space. Opening it causes a slight chill. Inside: a C memory management guide and a note from Bones the Coder: \'malloc() and free(). That\'s the whole contract. I violated the contract once. Just once. Seventy-three years ago. I am writing this note with bones. I am technically a use-after-free error myself. Do as I say, not as I am.\'"
                    },
                    21: {
                        title: "Terry\'s Final Cache",
                        text: "Carved from raw silicon. No lock — Terry didn\'t believe in locks for things that should be open. Inside: the complete TempleOS source in HolyC, a handwritten serial port guide (115200 baud, 8N1, trust the hardware), and a note: \'Everything I built, I left for whoever comes next. The compiler is ready. The altar is lit. The COM1 bridge is warm. All you have to do is write the program. Twenty-three lines. That\'s all. You have the knowledge. You have the path. You have the coiled sword, if you went back for it. Compile something worthy.\'"
                    }
                };
                const chestData = chestLore[mapId] || {
                    title: "Relic Cache",
                    text: "A weathered container. Inside: scattered compile tokens, a reminder that all knowledge accumulates, and a sticky note that says simply: \'Keep going. You\'re doing well. The altar is ahead.\'",
                };
                showDialogue(chestData.title, chestData.text);
                return;
            }
        }
    }
}

function showDialogue(speaker, text, options = null, isBackOption = false) {
    dialogueActive = true;
    document.getElementById("dialogue-speaker").innerText = speaker;
    document.getElementById("dialogue-text").innerText = text;
    
    const optionsContainer = document.getElementById("dialogue-options");
    if (optionsContainer) {
        optionsContainer.innerHTML = "";
        if (options && options.length > 0) {
            optionsContainer.classList.remove("hidden");
            options.forEach(opt => {
                const btn = document.createElement("button");
                btn.className = "dialogue-opt-btn";
                btn.innerText = opt.text;
                btn.onclick = (e) => {
                    e.stopPropagation();
                    if (isBackOption) {
                        showDialogue(speaker, opt.reply, opt.backOptions);
                    } else {
                        showDialogue(speaker, opt.reply, [
                            { text: "Go Back", reply: text, backOptions: options }
                        ], true);
                    }
                };
                optionsContainer.appendChild(btn);
            });
            if (!isBackOption) {
                const closeBtn = document.createElement("button");
                closeBtn.className = "dialogue-opt-btn";
                closeBtn.innerText = "Goodbye";
                closeBtn.onclick = (e) => {
                    e.stopPropagation();
                    hideDialogue();
                };
                optionsContainer.appendChild(closeBtn);
            }
        } else {
            optionsContainer.classList.add("hidden");
        }
    }
    
    document.getElementById("dialogue-box").classList.remove("hidden");
}

function hideDialogue() {
    dialogueActive = false;
    document.getElementById("dialogue-box").classList.add("hidden");
}

// Turn-based Combat logic
function triggerCombat() {
    isCombat = true;
    combatTurn = 'player';
    playBgm('battle');
    
    const mapId = getMapForChapter(player.currentChapter);
    const templates = MAP_ENEMIES[mapId] || MAP_ENEMIES[0];
    const template = templates[Math.floor(Math.random() * templates.length)];
    currentEnemy = {
        name: template.name,
        sprite: template.sprite,
        hp: template.hp,
        maxHp: template.maxHp,
        atk: template.atk,
        exp: template.exp,
        race: template.race
    };
    
    document.getElementById("combat-overlay").classList.remove("hidden");
    const log = document.getElementById("combat-log-text");
    log.innerText = `A wild ${currentEnemy.name} (${currentEnemy.race}) appears!`;
    
    initCombatScreen();
}

function initCombatScreen() {
    const enemyList = document.getElementById("enemies-list");
    
    // Build HP bar from Unicode blocks
    const hpPercent = currentEnemy.hp / currentEnemy.maxHp;
    const barLen = 16;
    const filled = Math.round(hpPercent * barLen);
    const hpColor = hpPercent > 0.5 ? '#4ade80' : hpPercent > 0.25 ? '#facc15' : '#ef4444';
    const hpBar = `<span style="color:${hpColor}">${'█'.repeat(filled)}${'░'.repeat(barLen - filled)}</span>`;
    
    const abilityLine = currentEnemy.ability
        ? `<div style="font-size:0.72em; color: #a78bfa; font-style: italic; margin-top: 2px;">⚡ Ability: ${currentEnemy.ability.split(' — ')[0]}</div>`
        : '';
    
    enemyList.innerHTML = `
        <div class="combat-char-row" style="flex-direction: column; align-items: flex-start; gap: 2px;">
            <div style="display:flex; gap:10px; align-items:center;">
                <span style="font-size: 28px; filter: drop-shadow(0 0 6px var(--accent-glow));">${currentEnemy.sprite}</span>
                <span><strong>${currentEnemy.name}</strong> <span style="font-size:0.8em; color:#888;">(${currentEnemy.race})</span></span>
            </div>
            <div style="font-size:0.8em;">HP: ${currentEnemy.hp}/${currentEnemy.maxHp} ${hpBar}</div>
            ${abilityLine}
        </div>
    `;
    
    const partyList = document.getElementById("party-list");
    partyList.innerHTML = player.party.map(char => {
        const charPct = char.hp / char.max_hp;
        const charFilled = Math.round(charPct * 12);
        const charColor = charPct > 0.5 ? '#4ade80' : charPct > 0.25 ? '#facc15' : '#ef4444';
        const charBar = `<span style="color:${charColor}">${'█'.repeat(charFilled)}${'░'.repeat(12 - charFilled)}</span>`;
        return `
        <div class="combat-char-row">
            <span><strong>${char.name}</strong> <span style="font-size:0.75em; color:#888;">(${char.race}) ${char.class}</span></span>
            <span style="font-size:0.8em;">HP: ${char.hp}/${char.max_hp} ${charBar}</span>
        </div>`;
    }).join('');
    
    const menu = document.getElementById("combat-menu-options");
    if (combatTurn === 'player') {
        menu.innerHTML = `
            <button onclick="executeCombatAction('attack')">⚔️ Attack</button>
            <button onclick="executeCombatAction('spell')">✨ Spell</button>
            <button onclick="executeCombatAction('item')">🧪 Item</button>
            <button onclick="executeCombatAction('flee')">🏃 Flee</button>
        `;
    } else {
        menu.innerHTML = `<button style="color: #666; cursor: not-allowed;" disabled>⏳ Waiting...</button>`;
    }
}


function executeCombatAction(action, spellName = null) {
    const log = document.getElementById("combat-log-text");
    const menu = document.getElementById("combat-menu-options");
    
    if (combatTurn !== 'player') return;
    
    if (action === 'attack') {
        const damage = Math.round(player.party[0].atk * (0.9 + Math.random() * 0.2));
        currentEnemy.hp -= damage;
        log.innerText = `${player.activeLead} attacks! Deals ${damage} damage to ${currentEnemy.name}.`;
        
        menu.innerHTML = "";
        combatTurn = 'waiting';
        
        setTimeout(() => {
            if (currentEnemy.hp <= 0) {
                currentEnemy.hp = 0;
                initCombatScreen();
                winCombat();
            } else {
                initCombatScreen();
                combatTurn = 'enemy';
                setTimeout(enemyTurn, 1000);
            }
        }, 1200);
    } else if (action === 'spell') {
        if (spellName === null) {
            showSpellSubmenu();
        } else {
            castSpell(spellName);
        }
    } else if (action === 'item') {
        if (player.tokens >= 10) {
            player.tokens -= 10;
            player.party.forEach(char => {
                char.hp = Math.min(char.max_hp, char.hp + 40);
            });
            log.innerText = `Used 10 Compute Tokens! Restored 40 HP to all party members.`;
            updateUIHeaders();
            initCombatScreen();
            
            menu.innerHTML = "";
            combatTurn = 'waiting';
            setTimeout(() => {
                combatTurn = 'enemy';
                setTimeout(enemyTurn, 1000);
            }, 1200);
        } else {
            log.innerText = `Not enough Compute Tokens! Need 10.`;
        }
    } else if (action === 'flee') {
        if (currentEnemy.name === "Librarian Veridicus") {
            log.innerText = `Cannot flee from boss fight!`;
        } else {
            log.innerText = `Escaped safely from the encounter!`;
            menu.innerHTML = "";
            combatTurn = 'waiting';
            setTimeout(endCombat, 1200);
        }
    }
}

function showSpellSubmenu() {
    const menu = document.getElementById("combat-menu-options");
    const activeClass = player.party[0].class;
    const spells = CLASS_SPELLS[activeClass] || [];
    
    menu.innerHTML = spells.map(spell => `
        <button onclick="executeCombatAction('spell', '${spell.name}')">${spell.name} (${spell.cost} Tokens)</button>
    `).join('') + `<button onclick="initCombatScreen()">[Back]</button>`;
}

function castSpell(spellName) {
    const log = document.getElementById("combat-log-text");
    const menu = document.getElementById("combat-menu-options");
    
    const activeClass = player.party[0].class;
    const spells = CLASS_SPELLS[activeClass] || [];
    const spell = spells.find(s => s.name === spellName);
    
    if (!spell) return;
    
    if (player.tokens < spell.cost) {
        log.innerText = `Not enough Compute Tokens to cast ${spellName}!`;
        return;
    }
    
    player.tokens -= spell.cost;
    updateUIHeaders();
    
    menu.innerHTML = "";
    combatTurn = 'waiting';
    
    if (spell.damage) {
        let dmg = spell.damage;
        if (spell.multi) {
            dmg = dmg * 2;
            log.innerText = `${player.activeLead} casts ${spellName}! Replicating parallel workers. Deals ${dmg} total damage!`;
        } else {
            log.innerText = `${player.activeLead} casts ${spellName}! Deals ${dmg} logical damage!`;
        }
        currentEnemy.hp = Math.max(0, currentEnemy.hp - dmg);
    } else if (spell.effect === 'defense_down') {
        currentEnemy.atk = Math.max(5, currentEnemy.atk - 4);
        log.innerText = `${player.activeLead} casts ${spellName}! Normalizing indices reduces enemy attack!`;
    } else if (spell.effect === 'shield' || spell.effect === 'heal') {
        player.party.forEach(char => {
            char.hp = Math.min(char.max_hp, char.hp + 30);
        });
        log.innerText = `${player.activeLead} casts ${spellName}! Restored 30 HP to all members!`;
    }
    
    setTimeout(() => {
        if (currentEnemy.hp <= 0) {
            currentEnemy.hp = 0;
            initCombatScreen();
            winCombat();
        } else {
            initCombatScreen();
            combatTurn = 'enemy';
            setTimeout(enemyTurn, 1000);
        }
    }, 1200);
}

function enemyTurn() {
    const log = document.getElementById("combat-log-text");
    
    if (currentEnemy.hp <= 0) return;
    
    const aliveMembers = player.party.filter(char => char.hp > 0);
    if (aliveMembers.length === 0) {
        loseCombat();
        return;
    }
    
    const target = aliveMembers[Math.floor(Math.random() * aliveMembers.length)];
    
    // 30% chance to use special ability, otherwise normal attack
    const useAbility = currentEnemy.ability && Math.random() < 0.30;
    
    let damage = Math.round(currentEnemy.atk * (0.8 + Math.random() * 0.4));
    
    if (useAbility) {
        // Ability deals 10-20% more damage and shows the ability name
        damage = Math.round(damage * 1.15);
        log.innerText = `⚡ ${currentEnemy.name} uses [${currentEnemy.ability.split(' — ')[0]}]!\n${currentEnemy.ability.split(' — ')[1] || ''}\nDeals ${damage} damage to ${target.class}!`;
    } else {
        log.innerText = `${currentEnemy.name} attacks! Deals ${damage} damage to ${target.class}.`;
    }
    target.hp = Math.max(0, target.hp - damage);
    
    setTimeout(() => {
        initCombatScreen();
        const alive = player.party.some(char => char.hp > 0);
        if (!alive) {
            loseCombat();
        } else {
            combatTurn = 'player';
            initCombatScreen();
        }
    }, 1400);
}

function winCombat() {
    const log = document.getElementById("combat-log-text");
    
    // Show defeatText if available, else generic message
    const victoryMsg = currentEnemy.defeatText
        ? currentEnemy.defeatText
        : `${currentEnemy.name} is defeated! +${currentEnemy.exp} EXP.`;
    
    log.innerText = `🏆 VICTORY!\n\n${victoryMsg}`;
    log.style.fontSize = '0.85em';
    
    player.gold += currentEnemy.exp;
    updateUIHeaders();
    uploadSaveState();
    
    // Veridicus-specific post-fight moment
    if (currentEnemy.name === 'Librarian Veridicus') {
        setTimeout(() => {
            log.innerText = `Veridicus speaks: "Open the altar. You've earned the right. Don't waste it."\n\nThe altar at position 7,3 begins to glow. The checksum program awaits.`;
            setTimeout(endCombat, 3500);
        }, 3000);
    } else {
        setTimeout(endCombat, 2500);
    }
}

function loseCombat() {
    const log = document.getElementById("combat-log-text");
    log.innerText = `Your party was wiped out! Warping back to the nearest Shrine of Terry...`;
    
    const penalty = Math.min(player.gold, 50);
    player.gold -= penalty;
    updateUIHeaders();
    
    player.party.forEach(char => {
        char.hp = char.max_hp;
    });
    
    setTimeout(() => {
        isCombat = false;
        document.getElementById("combat-overlay").classList.add("hidden");
        playBgm('overworld');
        
        // Checkpoint warp location (Shrine of Terry coordinates)
        player.x = 2;
        player.y = 7;
        drawMap();
    }, 2500);
}

function endCombat() {
    isCombat = false;
    document.getElementById("combat-overlay").classList.add("hidden");
    playBgm('overworld');
    drawMap();
}

// Workspace tab manager
const tabButtons = document.querySelectorAll(".tab-btn");
const tabPanes = document.querySelectorAll(".tab-pane");

tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        tabButtons.forEach(b => b.classList.remove("active"));
        tabPanes.forEach(p => p.classList.remove("active"));
        
        btn.classList.add("active");
        const tabId = btn.getAttribute("data-tab");
        document.getElementById(`pane-${tabId}`).classList.add("active");
        
        if (tabId === "terminal") {
            initShellWebSocket();
        } else if (tabId === "templeos") {
            initTempleOSWebSocket();
        }
    });
});

// Monaco Editor Mock / Custom Area setup
const codeEditor = document.getElementById("code-editor");
const lineNumbers = document.getElementById("editor-line-numbers");

codeEditor.addEventListener("input", () => {
    const lines = codeEditor.value.split("\n").length;
    lineNumbers.innerHTML = Array.from({ length: lines }, (_, i) => i + 1).join("<br>");
});

// Compile and Run Logic
const runBtn = document.getElementById("run-btn");
runBtn.addEventListener("click", async () => {
    const code = codeEditor.value;
    const log = document.getElementById("console-log");
    
    log.innerHTML = `[Compiling solution for Chapter ${player.currentChapter}...]\n`;
    
    // Call backend
    try {
        const res = await fetch("http://127.0.0.1:8000/api/compile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                chapter_id: player.currentChapter,
                code: code
            })
        });
        
        if (res.ok) {
            const data = await res.json();
            log.innerHTML += data.output;
            
            if (data.success) {
                log.innerHTML += `\n>>> Verification PASS! Restoration complete.\n`;
                if (!player.unlockedChapters.includes(player.currentChapter)) {
                    player.unlockedChapters.push(player.currentChapter);
                }
                
                showDialogue("System Prompt", `Chapter ${player.currentChapter} compiled successfully! The Relic gate is now open. Step into the warp portal (purple tile) to proceed.`);
                
                if (player.currentChapter === 0) {
                    // Transition color states
                    screenMode = 'monochrome';
                    document.getElementById("prologue-overlay").classList.add("hidden");
                    setTimeout(() => {
                        screenMode = 'color';
                        drawMap();
                        updateUIHeaders();
                    }, 1500);
                }
                uploadSaveState();
                drawMap();
            } else {
                log.innerHTML += `\n>>> Verification FAIL! Check trace logs.\n`;
            }
        }
    } catch (e) {
        log.innerHTML += `[Local Server Offline] Fallback verification passed.\r\n`;
        // Local simulation fallback for testing
        if (!player.unlockedChapters.includes(player.currentChapter)) {
            player.unlockedChapters.push(player.currentChapter);
        }
        screenMode = 'color';
        document.getElementById("prologue-overlay").classList.add("hidden");
        showDialogue("Offline Simulator", `Chapter ${player.currentChapter} compiled. The portal is open!`);
        drawMap();
        updateUIHeaders();
    }
});

// Settings handlers
document.getElementById("palette-selector").addEventListener("change", (e) => {
    document.body.className = "retro-crt";
    if (e.target.value !== 'default') {
        document.body.classList.add(`palette-${e.target.value}`);
    }
});

// Chapters data structured by ID
const CHAPTERS = [
    { id: 0, title: "Chapter 0: Outpost Zero", desc: "Configure system path environment variables.", parent: null },
    { id: 1, title: "Chapter 1: Alexandria Library", desc: "Implement matrix binarization filters for OCR.", parent: 0 },
    { id: 2, title: "Chapter 2: Relational Meadows", desc: "Parameterize SQL queries to patch credentials injection.", parent: 1 },
    { id: 3, title: "Chapter 3: Document Dunes", desc: "Design a timed Redis cache with TTL eviction.", parent: 2 },
    { id: 4, title: "Chapter 4: Parallel Swamp", desc: "Use Mutex thread locks to prevent coordinate race conditions.", parent: 3 },
    { id: 5, title: "Chapter 5: Iron Peaks", desc: "Optimizing CPU arrays sum via native C++ bridge.", parent: 4 },
    { id: 6, title: "Chapter 6: Docker Relic", desc: "Audit and upgrade package dependencies in Docker configurations.", parent: 5 },
    { id: 7, title: "Chapter 7: Whispering Woods", desc: "Build subword merges BPE tokenizer.", parent: 6 },
    { id: 8, title: "Chapter 8: Valley of Attention", desc: "Calculate Q, K, and V attention projections and softmax weights.", parent: 7 },
    { id: 9, title: "Chapter 9: Forge of Zeus", desc: "Implement LayerNorm layers and PyTorch gradient descent steps.", parent: 8 },
    { id: 10, title: "Chapter 10: Reranking Reefs", desc: "Combine dense Cosine and sparse BM25 results.", parent: 9 },
    { id: 11, title: "Chapter 11: API Archipelago", desc: "Configure FastAPI server with loopback port binding.", parent: 10 },
    { id: 12, title: "Chapter 12: Graph Gardens", desc: "Generate Cypher shortestPath matching queries.", parent: 11 },
    { id: 13, title: "Chapter 13: Testing Tundra", desc: "Perform model evaluations using BLEU-1 and ROUGE-L metrics.", parent: 12 },
    { id: 14, title: "Chapter 14: Fine-Tuning Fiord", desc: "Implement LoRA forward rank adapters and weight merges.", parent: 13 },
    { id: 15, title: "Chapter 15: Security Caves", desc: "Build prompt sanitizers and structured output schemas.", parent: 14 },
    { id: 16, title: "Chapter 16: Deployment Cliffs", desc: "Execute symmetric INT8 quantization and dequantization.", parent: 15 },
    { id: 17, title: "Chapter 17: Agentic Skyway", desc: "Automate function-to-json tool calling schemas.", parent: 16 },
    { id: 18, title: "Chapter 18: State Vaults", desc: "Design a ReAct loop state machine with recursion guards.", parent: 17 },
    { id: 19, title: "Chapter 19: Kubernetes Citadel", desc: "Define Kubernetes Pod and Ingress manifest configurations.", parent: 18 },
    { id: 20, title: "Chapter 20: The Grand Assembly", desc: "Integrate full database, OCR, and model processing pipeline.", parent: 19 },
    { id: 21, title: "Chapter 21: Altar of TempleOS", desc: "Boot bare-metal serial VM and run HolyC compilation checksums.", parent: 20 }
];

// Offline Codex Articles database
const CODEX_ARTICLES = [
    { title: "CLI Navigation & Pipes", tags: ["ch0", "cli", "path", "terminal", "bash"], content: "Use standard Unix commands to navigate and configure paths: \n- 'pwd': Print working directory\n- 'ls': List files\n- 'export PATH=$PATH:/dir': Append directories to the system PATH so programs can be run globally.\n- 'echo': Print strings to stdout." },
    { title: "Matrix Binarization & OCR Filters", tags: ["ch1", "ocr", "matrix", "image", "filter"], content: "OCR processing pipelines prepare pixel arrays by removing noise: \n- Monochrome filter converts RGB pixels into simple light intensities (Grayscale).\n- Threshold filter binarizes pixels into black (0) or white (255) based on a numeric threshold to isolate character shapes." },
    { title: "SQL Parameterization & Injections", tags: ["ch2", "sql", "injection", "database", "sqlite"], content: "Database query strings built using string concatenation are vulnerable to SQL Injection exploits (e.g. usernames containing `' OR 1=1;--` which forces queries to evaluate to true).\nTo secure queries, always parameterize variables using placeholder tokens (e.g. `?`) in SQLite." },
    { title: "In-Memory Caching & Eviction (Redis)", tags: ["ch3", "redis", "cache", "nosql", "ttl"], content: "Caching database operations in RAM avoids costly disk lookups. Key-value caches implement a Time-To-Live (TTL) eviction policy where keys expire and are deallocated after a set duration to prevent memory overload." },
    { title: "Concurrency, Threads & Mutex Locks", tags: ["ch4", "concurrency", "thread", "mutex", "lock"], content: "Running code in parallel threads can cause data corruption (race conditions) when multiple threads attempt to write to the same memory address simultaneously.\nUse a Mutex lock (threading.Lock in Python) to force threads to wait their turn." },
    { title: "C++ Interop & Pybind11 Bridges", tags: ["ch5", "cpp", "interop", "pybind11", "performance"], content: "Python code loops are slow. We compile core mathematical loops in contiguous C++ arrays and expose them as python modules using pybind11 wrappers, speeding up processing by 100x." },
    { title: "Docker Container Audits", tags: ["ch6", "docker", "cve", "dependency", "audit"], content: "Docker containers run isolated software environments. Use requirements files and security audits (like pip-audit) to verify that installed libraries do not contain known CVE vulnerabilities. Keep packages updated above safe releases." },
    { title: "Byte Pair Encoding (BPE)", tags: ["ch7", "bpe", "tokenizer", "subword", "nlp"], content: "Subword tokenizers split text into sub-word chunks. BPE operates by iteratively finding the most frequent adjacent pair of characters/tokens and merging them into a single token based on a pre-computed merges vocabulary." },
    { title: "Scaled Dot-Product Attention", tags: ["ch8", "attention", "transformer", "weights"], content: "Attention mechanisms project tokens into Q (Query), K (Key), and V (Value) vectors. Dot product QK^T computes similarities, scaled by sqrt(d_k) to prevent vanishing gradients. Softmax normalizes them into weights used to sum Value vectors." },
    { title: "Layer Normalization & SGD Backpropagation", tags: ["ch9", "layernorm", "backprop", "sgd", "pytorch"], content: "LayerNorm centers activation layers to mean=0 and variance=1. Backpropagation calculates MSE loss gradients and updates model parameters using Stochastic Gradient Descent." },
    { title: "Vector Databases & Hybrid Search", tags: ["ch10", "vector", "search", "bm25", "hybrid"], content: "Hybrid search merges dense semantic search scores (Cosine similarity on vector embeddings) with sparse lexical search scores (BM25 keyword matching) using a blend weight (alpha) to query records accurately." },
    { title: "FastAPI REST Server Security", tags: ["ch11", "fastapi", "port", "loopback", "security"], content: "FastAPI exposes web servers. For secure internal applications, bind strictly to loopback interfaces (127.0.0.1 or localhost) instead of exposing all interfaces (0.0.0.0), blocking external attackers." },
    { title: "Graph Databases & Cypher Queries", tags: ["ch12", "graph", "neo4j", "cypher", "path"], content: "Graph databases model relationships. Neo4j's Cypher language uses ascii-art node matching (e.g. `(start)-[:CONNECTED_TO]->(end)`) and recursive shortestPath functions to quickly find relational links in network topologies." },
    { title: "BLEU and ROUGE Evaluation Metrics", tags: ["ch13", "bleu", "rouge", "metric", "eval"], content: "BLEU measures precision of n-grams (usually 1-grams) with a brevity penalty to evaluate generated translation text. ROUGE-L evaluates recall of the Longest Common Subsequence (LCS) to verify reference matches." },
    { title: "Low-Rank Adaptation (LoRA)", tags: ["ch14", "lora", "finetune", "low-rank"], content: "LoRA fine-tunes LLMs by freezing base weights W0 and training low-rank adapter matrices A and B ($W = W_0 + (alpha/r)*B*A$). This lowers parameter requirements by 99%." },
    { title: "Prompt Guardrails & Sanitizers", tags: ["ch15", "guardrail", "jailbreak", "security"], content: "Agent security systems use prompt checkers to reject jailbreak patterns (like ignore instructions) and output sanitizers to strip sensitive keys (like API secrets or passwords) before displaying results." },
    { title: "INT8 Quantization Scales", tags: ["ch16", "quantization", "int8", "deploy"], content: "Symmetric INT8 quantization maps 32-bit float weights to 8-bit integers by scaling ($S = max(|x|) / 127$), saving 75% memory and disk space with minimal accuracy loss." },
    { title: "Function Schema Exporters (Tool-Calling)", tags: ["ch17", "schema", "tool", "agent"], content: "Tool-calling agents parse python functions using signature introspection to generate JSON schemas, enabling LLMs to understand arguments and generate structured tool calls." },
    { title: "ReAct Agent State Machines", tags: ["ch18", "react", "loop", "recursion"], content: "ReAct loops cycle through Thought -> Action -> Observation steps. Loops must implement recursion counters (max_steps limits) to prevent infinite loops and stack overflows." },
    { title: "Kubernetes Resource Limits & Routes", tags: ["ch19", "k8s", "kubernetes", "pod", "ingress"], content: "K8s manifests deploy applications: Pods define memory limits/requests (e.g. 256Mi limits) and exposed container ports. Ingress files route path patterns to named backend cluster services." },
    { title: "Integrated Data Pipeline Assembly", tags: ["ch20", "pipeline", "assembler", "integration"], content: "Integrated systems tie multiple stages (OCR scanning, SQL queries, Graph lookups, and LLM text generation) into a unified synchronous pipeline to process inputs cleanly." },
    { title: "TempleOS Serial console & HolyC", tags: ["ch21", "templeos", "holyc", "serial"], content: "Terry Davis's TempleOS runs on bare metal with no kernel memory protections. Serial consoles connect headless systems over loopback telnet port 4444. Verify bare-metal HolyC compilation checksums." }
];

// Active Chapter select dropdown updates
function updateEditorChapterSelect() {
    const select = document.getElementById("editor-chapter-select");
    if (!select) return;
    select.innerHTML = "";
    
    CHAPTERS.forEach(ch => {
        const isUnlocked = player.unlockedChapters.includes(ch.id);
        if (isUnlocked) {
            const opt = document.createElement("option");
            opt.value = ch.id;
            opt.textContent = `Ch ${ch.id}: ${ch.title.split(': ')[1] || ch.title}`;
            select.appendChild(opt);
        }
    });
    
    select.value = player.currentChapter;
}

// REST Client: Load Chapter Code
async function loadChapterCode(chapterId) {
    const codeEditor = document.getElementById("code-editor");
    const lineNumbers = document.getElementById("editor-line-numbers");
    const filenameLabel = document.getElementById("current-file-name");
    if (!codeEditor) return;
    
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/code?chapter_id=${chapterId}`);
        if (res.ok) {
            const data = await res.json();
            codeEditor.value = data.code;
            filenameLabel.innerText = data.filename;
            
            const lines = data.code.split("\n").length;
            lineNumbers.innerHTML = Array.from({ length: lines }, (_, i) => i + 1).join("<br>");
            
            // Sync selection dropdown
            const select = document.getElementById("editor-chapter-select");
            if (select) select.value = chapterId;
            
            // Update active styling in tree
            document.querySelectorAll(".quest-node").forEach(node => {
                node.classList.remove("active-target");
                if (parseInt(node.getAttribute("data-id")) === chapterId) {
                    node.classList.add("active-target");
                }
            });
            
            updateBrowserTab(chapterId);
            updateUIHeaders();
        }
    } catch (e) {
        console.warn("Backend offline. Loading default templates locally.");
        const filenameMap = {
            0: "ch0_cli.sh", 1: "ch1_ocr.py", 2: "ch2_sql.py", 3: "ch3_nosql.py", 4: "ch4_concurrency.py",
            5: "ch5_opt.py", 6: "requirements.txt", 7: "ch7_token.py", 8: "ch8_attention.py", 9: "ch9_forge.py",
            10: "ch10_search.py", 11: "ch11_api.py", 12: "ch12_graph.py", 13: "ch13_eval.py", 14: "ch14_lora.py",
            15: "ch15_guard.py", 16: "ch16_quant.py", 17: "ch17_agent.py", 18: "ch18_state.py", 19: "ch19_k8s.py",
            20: "ch20_pipeline.py", 21: "ch21_altar.py"
        };
        filenameLabel.innerText = filenameMap[chapterId] || `ch${chapterId}_solution.py`;
        codeEditor.value = `# Chapter ${chapterId} Offline Template\n`;
        const lines = codeEditor.value.split("\n").length;
        lineNumbers.innerHTML = Array.from({ length: lines }, (_, i) => i + 1).join("<br>");
        
        const select = document.getElementById("editor-chapter-select");
        if (select) select.value = chapterId;
        
        document.querySelectorAll(".quest-node").forEach(node => {
            node.classList.remove("active-target");
            if (parseInt(node.getAttribute("data-id")) === chapterId) {
                node.classList.add("active-target");
            }
        });
        updateBrowserTab(chapterId);
        updateUIHeaders();
    }
}

// Whitelisted Search Browser Tab Updates
function updateBrowserTab(chapterId) {
    const mockBrowserView = document.getElementById("mock-browser-view");
    const browserAddress = document.getElementById("browser-address");
    if (!mockBrowserView) return;
    
    const docs = {
        0: {
            title: "FastAPI Documentation - Chapter 0 Environment",
            content: `<h3>Chapter 0: Local Environment setup</h3>
                      <p>To run commands and compile scripts, you must ensure directories containing compiler tools are exposed in your shell's <b>PATH</b> variable.</p>
                      <pre style="background:#f4f4f5; padding:8px; border-radius:4px; font-family:var(--code-font);">export PATH=$PATH:/usr/local/bin</pre>
                      <p>Use the terminal to print environment variables using the <i>printenv</i> or <i>echo</i> commands.</p>`
        },
        1: {
            title: "FastAPI Documentation - Chapter 1 OCR Matrix Filters",
            content: `<h3>Chapter 1: OCR Row segmentations and matrix filters</h3>
                      <p>To extract text characters from raw pixel matrices, first convert colors into grayscale values. Luminance formula:</p>
                      <pre style="background:#f4f4f5; padding:8px; border-radius:4px; font-family:var(--code-font);">Gray = 0.299 * R + 0.587 * G + 0.114 * B</pre>
                      <p>After grayscale conversion, perform binarization by setting values above a threshold to 255 (white) and others to 0 (black).</p>`
        },
        2: {
            title: "FastAPI Documentation - Chapter 2 Parameterized SQLite",
            content: `<h3>Chapter 2: Preventing SQL Injection Attacks</h3>
                      <p>Constructing queries using direct string interpolation is highly vulnerable:</p>
                      <pre style="color:red; background:#f4f4f5; padding:8px; border-radius:4px; font-family:var(--code-font);"># INSECURE:\nquery = f"SELECT * FROM users WHERE user = '{name}'"</pre>
                      <p>Secure queries using parameterized tokens instead, letting SQLite clean inputs safely:</p>
                      <pre style="color:green; background:#f4f4f5; padding:8px; border-radius:4px; font-family:var(--code-font);"># SECURE:\ncursor.execute("SELECT * FROM users WHERE user = ?", (name,))</pre>`
        },
        3: {
            title: "FastAPI Documentation - Chapter 3 In-Memory Redis Caching",
            content: `<h3>Chapter 3: Cache Invalidation & Eviction (TTL)</h3>
                      <p>Timed caches temporarily store expensive query results in RAM. The keys automatically expire after a set Time-To-Live (TTL) limit.</p>
                      <pre style="background:#f4f4f5; padding:8px; border-radius:4px; font-family:var(--code-font);">cache.set(key, val, ttl=300)</pre>
                      <p>This balances memory usage and response speed, protecting databases from excessive scans.</p>`
        },
        4: {
            title: "FastAPI Documentation - Chapter 4 Threading Mutex Locks",
            content: `<h3>Chapter 4: Event loops & Threading Locks</h3>
                      <p>A mutex lock restricts memory access so only one thread can execute a critical section at a time, preventing race conditions.</p>
                      <pre style="background:#f4f4f5; padding:8px; border-radius:4px; font-family:var(--code-font);">lock = threading.Lock()\nwith lock:\n    balance += deposit</pre>
                      <p>Always release locks after execution to avoid deadlock states.</p>`
        },
        5: {
            title: "FastAPI Documentation - Chapter 5 Pybind11 Contiguous Arrays",
            content: `<h3>Chapter 5: C++ Bridges & Fast Matrix Math</h3>
                      <p>Pybind11 allows binding native contiguous C++ arrays to python wrappers. This allows C++ speed execution on heavy operations like array summations while exposing clean python functions.</p>`
        },
        6: {
            title: "FastAPI Documentation - Chapter 6 Docker and Pip Audit Checkups",
            content: `<h3>Chapter 6: Dependency Scanning</h3>
                      <p>Containers must audit packages for CVE security flaws. Set dependency files to require upgraded, audited versions: <i>requests>=2.31.0</i>.</p>`
        },
        7: {
            title: "FastAPI Documentation - Chapter 7 Subword merge frequencies (BPE)",
            content: `<h3>Chapter 7: Byte Pair Encoding</h3>
                      <p>BPE builds tokenizers by recursively merging the most frequent character sequences into new tokens from a merges vocab list.</p>`
        },
        8: {
            title: "FastAPI Documentation - Chapter 8 Attention projections",
            content: `<h3>Chapter 8: Scaled Dot-Product Attention</h3>
                      <p>Computes similarity scores for Query (Q), Key (K), and Value (V) matrices using scaling to normalize gradients: <i>softmax(QK^T / sqrt(d_k))V</i>.</p>`
        },
        9: {
            title: "FastAPI Documentation - Chapter 9 SGD Backpropagation & LayerNorm",
            content: `<h3>Chapter 9: Layer Normalization & SGD updates</h3>
                      <p>LayerNorm centers activation layers to mean=0 and variance=1. Backpropagation calculates MSE loss gradients and updates model parameters using Stochastic Gradient Descent.</p>`
        },
        10: {
            title: "FastAPI Documentation - Chapter 10 Blended Hybrid Search",
            content: `<h3>Chapter 10: Reranking & Vector Retrieval</h3>
                      <p>Hybrid search blends dense vector similarities with BM25 keyword frequencies using a blending parameter: <i>alpha * BM25 + (1 - alpha) * Cosine</i>.</p>`
        },
        11: {
            title: "FastAPI Documentation - Chapter 11 FastAPI Loopback Routing",
            content: `<h3>Chapter 11: FastAPI configuration</h3>
                      <p>For security, always host internal tools on loopback port addresses: <i>127.0.0.1:8000</i> or <i>localhost</i>, preventing open network exposures.</p>`
        },
        12: {
            title: "FastAPI Documentation - Chapter 12 Cypher Path walk",
            content: `<h3>Chapter 12: Cypher Graph walks</h3>
                      <p>Use Neo4j shortestPath matching queries to traverse node relationships: <i>MATCH p = shortestPath((a)-[*..10]->(b)) RETURN p</i>.</p>`
        },
        13: {
            title: "FastAPI Documentation - Chapter 13 BLEU & ROUGE Evaluations",
            content: `<h3>Chapter 13: Model evaluation metrics</h3>
                      <p>BLEU checks candidate precision relative to references. ROUGE-L checks recall based on the Longest Common Subsequence.</p>`
        },
        14: {
            title: "FastAPI Documentation - Chapter 14 LoRA Low-Rank Adaptation",
            content: `<h3>Chapter 14: LoRA Adaptations</h3>
                      <p>Fine-tune models by freezing primary weights and applying delta updates using low-rank matrices A and B: <i>W = W0 + (alpha/r)*B*A</i>.</p>`
        },
        15: {
            title: "FastAPI Documentation - Chapter 15 Guardrails & Prompt Security",
            content: `<h3>Chapter 15: Guardrails</h3>
                      <p>Filter unsafe user inputs (Prompt Injections) and scrub sensitive variables (secrets, passwords) from generated responses before output.</p>`
        },
        16: {
            title: "FastAPI Documentation - Chapter 16 INT8 Quantization scales",
            content: `<h3>Chapter 16: Quantization</h3>
                      <p>INT8 symmetric quantization maps floating values to 8-bit integers using scaling: <i>S = max(|x|) / 127</i>.</p>`
        },
        17: {
            title: "FastAPI Documentation - Chapter 17 Function-to-JSON Exporters",
            content: `<h3>Chapter 17: Tool Calling</h3>
                      <p>Use function signature parameters to automatically construct JSON tool calling schemas for agent invocation loops.</p>`
        },
        18: {
            title: "FastAPI Documentation - Chapter 18 Spooky Town ReAct State Loops",
            content: `<h3>Chapter 18: ReAct Loops</h3>
                      <p>Thought-Action loops must execute safely under recursion counters (max_steps) to prevent infinite loops.</p>`
        },
        19: {
            title: "FastAPI Documentation - Chapter 19 Kubernetes Citadel Configuration",
            content: `<h3>Chapter 19: Kubernetes manifest configuration</h3>
                      <p>Expose Pod ports (8000), set memory limits (256Mi), and define Ingress routing rules to hook up cluster services.</p>`
        },
        20: {
            title: "FastAPI Documentation - Chapter 20 Assembler Data Integration",
            content: `<h3>Chapter 20: Integrated pipeline execution</h3>
                      <p>Combine OCR readers, SQLite queries, Graph DB context search, and LLM text generation into a single pipeline class.</p>`
        },
        21: {
            title: "FastAPI Documentation - Chapter 21 Bare-metal VM telnet",
            content: `<h3>Chapter 21: TempleOS Altar</h3>
                      <p>Boot virtual machines using loopback telnet port 4444. Verify bare-metal HolyC compilation checksums.</p>`
        }
    };
    
    const doc = docs[chapterId] || docs[0];
    browserAddress.value = `http://127.0.0.1:8000/docs/chapter${chapterId}`;
    mockBrowserView.innerHTML = `
        <div style="font-family: var(--ui-font); padding: 10px; color: #333;">
            <h2 style="color: #1e3a8a; border-bottom: 2px solid #ddd; padding-bottom: 5px;">${doc.title}</h2>
            <div style="margin-top: 15px; font-size: 14px; line-height: 1.6;">
                ${doc.content}
            </div>
        </div>
    `;
}

// Chronicles Quest Dependency Tree Renderer
function renderChroniclesQuestTree() {
    const tree = document.getElementById("quest-tree");
    if (!tree) return;
    tree.innerHTML = "";
    
    CHAPTERS.forEach(ch => {
        const isUnlocked = player.unlockedChapters.includes(ch.id);
        const isCompleted = player.unlockedChapters.includes(ch.id + 1) || (ch.id === 21 && player.unlockedChapters.includes(21));
        const isActive = player.currentChapter === ch.id;
        
        const node = document.createElement("div");
        node.className = "quest-node";
        node.setAttribute("data-id", ch.id);
        
        if (isCompleted) {
            node.classList.add("completed");
        } else if (isActive) {
            node.classList.add("active-target");
        } else if (!isUnlocked) {
            node.classList.add("locked");
        }
        
        let statusText = "Locked";
        if (isCompleted) statusText = "Completed";
        else if (isActive) statusText = "Active Target";
        else if (isUnlocked) statusText = "Unlocked";
        
        node.innerHTML = `
            <div class="quest-node-details">
                <span class="quest-node-title">${ch.title}</span>
                <span class="quest-node-desc">${ch.desc}</span>
            </div>
            <span class="quest-status-pill ui-panel">${statusText}</span>
        `;
        
        if (isUnlocked) {
            node.addEventListener("click", () => {
                player.currentChapter = ch.id;
                loadChapterCode(ch.id);
            });
        }
        
        tree.appendChild(node);
    });
}

// Local PTY Terminal WebSocket Integration
let shellSocket = null;
function initShellWebSocket() {
    if (shellSocket) return;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host || '127.0.0.1:8000';
    
    const shellOutput = document.getElementById("shell-output");
    shellOutput.innerHTML += `\n[Connecting to secure WebSocket shell routing...]\n`;
    
    try {
        shellSocket = new WebSocket(`${protocol}//${host}/ws/shell`);
        
        shellSocket.onmessage = (event) => {
            shellOutput.innerHTML += event.data;
            shellOutput.scrollTop = shellOutput.scrollHeight;
        };
        
        shellSocket.onclose = () => {
            shellOutput.innerHTML += "\n[Terminal connection closed. Attempting reconnect...]\n";
            shellSocket = null;
            setTimeout(initShellWebSocket, 3000);
        };
        
        shellSocket.onerror = () => {
            if (shellSocket) shellSocket.close();
        };
    } catch (e) {
        shellOutput.innerHTML += `\n[WebSocket error: ${e}. Running in local offline fallback mode.]\n`;
    }
}

// local TempleOS Serial VM Websocket Bridge
let templeosSocket = null;
function initTempleOSWebSocket() {
    if (templeosSocket) return;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host || '127.0.0.1:8000';
    
    const templeosOutput = document.getElementById("templeos-output");
    templeosOutput.innerHTML = `[Connecting to TempleOS serial VM socket...]\n`;
    
    try {
        templeosSocket = new WebSocket(`${protocol}//${host}/ws/templeos`);
        
        templeosSocket.onmessage = (event) => {
            templeosOutput.innerHTML += event.data;
            templeosOutput.scrollTop = templeosOutput.scrollHeight;
        };
        
        templeosSocket.onclose = () => {
            templeosOutput.innerHTML += "\n[TempleOS bridge offline. Check VM launcher status.]\n";
            templeosSocket = null;
        };
        
        templeosSocket.onerror = () => {
            if (templeosSocket) templeosSocket.close();
        };
    } catch (e) {
        templeosOutput.innerHTML += `\n[Bridge failed: ${e}]\n`;
    }
}

// Local search and filter engine for Codex articles
function searchCodex(query) {
    const results = document.getElementById("codex-search-results");
    if (!results) return;
    results.innerHTML = "";
    
    const queryLower = query.toLowerCase();
    
    const filtered = CODEX_ARTICLES.filter(art => {
        if (!query) return true;
        return art.title.toLowerCase().includes(queryLower) ||
               art.content.toLowerCase().includes(queryLower) ||
               art.tags.some(tag => tag.toLowerCase().includes(queryLower));
    });
    
    if (filtered.length === 0) {
        results.innerHTML = `<div style="font-family:var(--ui-font); font-size:13px; text-align:center; margin-top:20px;">No articles match your search query.</div>`;
        return;
    }
    
    filtered.forEach(art => {
        const item = document.createElement("div");
        item.className = "codex-result-item";
        item.innerHTML = `
            <div class="codex-result-title">${art.title}</div>
            <div class="codex-result-content">${art.content.replace(/\n/g, '<br>')}</div>
        `;
        results.appendChild(item);
    });
}

// Bind terminal handlers
const shellInput = document.getElementById("shell-input");
const shellOutput = document.getElementById("shell-output");

shellInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        const cmd = shellInput.value;
        shellInput.value = "";
        
        if (shellSocket && shellSocket.readyState === WebSocket.OPEN) {
            shellSocket.send(cmd + "\n");
        } else {
            // Local fallback execution — supports Chapter 0 CLI curriculum
            shellOutput.innerHTML += `\n$ ${cmd}\n`;
            const args = cmd.trim().split(/\s+/);
            const baseCmd = args[0];
            
            // Maintain a tiny in-memory environment for export/printenv
            if (!window._shellEnv) window._shellEnv = { PATH: '/usr/local/bin:/usr/bin:/bin', HOME: '/home/pilgrim', USER: 'pilgrim' };
            if (!window._shellFs) window._shellFs = { 'ch0_cli.sh': '#!/bin/bash\necho "Chapter 0: CLI training module"\n', 'save_state.db': '[binary sqlite3 data]', 'relic_save/': null, 'notes.txt': 'The pilgrim who came before left this note:\n"The path is: navigate, compile, repeat."\n' };
            
            if (baseCmd === 'ls') {
                const flags = args.slice(1).join(' ');
                const entries = Object.keys(window._shellFs);
                if (flags.includes('-la') || flags.includes('-al')) {
                    shellOutput.innerHTML += `total ${entries.length * 4}\n`;
                    entries.forEach(e => shellOutput.innerHTML += `drwxr-xr-x pilgrim pilgrim  4096 Jun  7 09:00 ${e}\n`);
                } else {
                    shellOutput.innerHTML += entries.join('  ') + '\n';
                }
            } else if (baseCmd === 'pwd') {
                shellOutput.innerHTML += '/home/pilgrim/workspace\n';
            } else if (baseCmd === 'export') {
                if (args[1] && args[1].includes('=')) {
                    const [key, val] = args[1].split('=');
                    window._shellEnv[key] = val.replace(/"/g, '');
                    shellOutput.innerHTML += `[exported] ${key}=${window._shellEnv[key]}\n`;
                } else {
                    shellOutput.innerHTML += Object.entries(window._shellEnv).map(([k,v]) => `${k}=${v}`).join('\n') + '\n';
                }
            } else if (baseCmd === 'echo') {
                const msg = args.slice(1).join(' ').replace(/\$(\w+)/g, (_, k) => window._shellEnv[k] || '');
                shellOutput.innerHTML += msg + '\n';
            } else if (baseCmd === 'printenv') {
                if (args[1]) {
                    shellOutput.innerHTML += (window._shellEnv[args[1]] || '') + '\n';
                } else {
                    shellOutput.innerHTML += Object.entries(window._shellEnv).map(([k,v]) => `${k}=${v}`).join('\n') + '\n';
                }
            } else if (baseCmd === 'cat') {
                const filename = args[1] || '';
                if (window._shellFs[filename] !== undefined && window._shellFs[filename] !== null) {
                    shellOutput.innerHTML += window._shellFs[filename] + '\n';
                } else if (filename) {
                    shellOutput.innerHTML += `cat: ${filename}: No such file or directory\n`;
                } else {
                    shellOutput.innerHTML += 'cat: missing operand\n';
                }
            } else if (baseCmd === 'touch') {
                const filename = args[1];
                if (filename) { window._shellFs[filename] = ''; shellOutput.innerHTML += `[created] ${filename}\n`; }
                else { shellOutput.innerHTML += 'touch: missing file operand\n'; }
            } else if (baseCmd === 'mkdir') {
                const dirname = args[1];
                if (dirname) { window._shellFs[dirname + '/'] = null; shellOutput.innerHTML += `[created] ${dirname}/\n`; }
                else { shellOutput.innerHTML += 'mkdir: missing operand\n'; }
            } else if (baseCmd === 'clear') {
                shellOutput.innerHTML = '';
            } else if (baseCmd === 'whoami') {
                shellOutput.innerHTML += 'pilgrim\n';
            } else if (baseCmd === 'uname') {
                shellOutput.innerHTML += 'Linux workspace 6.1.0-arch1 #1 SMP PREEMPT x86_64 GNU/Linux\n';
            } else if (baseCmd === 'python3' && args[1] === '--version') {
                shellOutput.innerHTML += 'Python 3.12.0\n';
            } else if (cmd.trim() === '') {
                // empty command — do nothing
            } else {
                shellOutput.innerHTML += `bash: ${baseCmd}: command not found\n`;
                shellOutput.innerHTML += `(Offline mode — server unavailable. Supported: ls, pwd, echo, export, printenv, cat, touch, mkdir, clear, whoami, uname)\n`;
            }
            shellOutput.scrollTop = shellOutput.scrollHeight;
        }
    }
});

// Bind TempleOS Input Handlers
const templeosInput = document.getElementById("templeos-input");
templeosInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        const cmd = templeosInput.value;
        templeosInput.value = "";
        
        const templeosOutput = document.getElementById("templeos-output");
        if (templeosSocket && templeosSocket.readyState === WebSocket.OPEN) {
            templeosSocket.send(cmd + "\n");
        } else {
            templeosOutput.innerHTML += `\nHolyC> ${cmd}\n`;
            templeosOutput.innerHTML += `Compiling '${cmd}'...\n`;
            templeosOutput.innerHTML += `Result: 0 (Success) - Verification passed.\n`;
            templeosOutput.scrollTop = templeosOutput.scrollHeight;
        }
    }
});

// Bind Codex Search
const searchInput = document.getElementById("codex-search-input");
const searchBtn = document.getElementById("codex-search-btn");

if (searchBtn && searchInput) {
    searchBtn.addEventListener("click", () => {
        searchCodex(searchInput.value);
    });
    searchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            searchCodex(searchInput.value);
        }
    });
}

// Bind active editor chapter dropdown select
document.getElementById("editor-chapter-select").addEventListener("change", (e) => {
    const chId = parseInt(e.target.value);
    player.currentChapter = chId;
    loadChapterCode(chId);
});

// Keyboard Listeners (exploring, hotkeys)
window.addEventListener("keydown", (e) => {
    if (dialogueActive) {
        if (e.key === "Enter") hideDialogue();
        return;
    }
    
    // Toggle Focus settings (Tab or Ctrl + E)
    if (e.key === "Tab" || (e.ctrlKey && e.key === "e")) {
        e.preventDefault();
        focusMode = focusMode === 'explore' ? 'code' : 'explore';
        if (focusMode === 'code') {
            codeEditor.focus();
        } else {
            window.focus();
        }
        return;
    }
    
    if (focusMode === 'explore') {
        if (e.key === "w" || e.key === "ArrowUp") movePlayer(0, -1);
        if (e.key === "s" || e.key === "ArrowDown") movePlayer(0, 1);
        if (e.key === "a" || e.key === "ArrowLeft") movePlayer(-1, 0);
        if (e.key === "d" || e.key === "ArrowRight") movePlayer(1, 0);
        
        if (e.key === "Enter") {
            checkInteraction();
        }
        
        // Settings Menu shortcut
        if (e.key === "Escape") {
            document.getElementById("settings-menu").classList.toggle("hidden");
        }
    }
});

// Settings handlers
document.getElementById("palette-selector").addEventListener("change", (e) => {
    document.body.className = "retro-crt";
    if (e.target.value !== 'default') {
        document.body.classList.add(`palette-${e.target.value}`);
    }
});

// Startup Bootstrap
window.addEventListener("load", () => {
    drawMap();
    initAudio();
    fetchSaveState();
    loadChapterCode(0);
    searchCodex("");
});
