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
        { name: 'Optimizer', class: 'Low-Level Optimizer', hp: 120, max_hp: 120, atk: 18, def: 10, spd: 14, luc: 8, tokens: 100 },
        { name: 'Architect', class: 'Data Architect', hp: 100, max_hp: 100, atk: 12, def: 14, spd: 10, luc: 10, tokens: 100 },
        { name: 'Orchestrator', class: 'Agent Orchestrator', hp: 90, max_hp: 90, atk: 10, def: 8, spd: 12, luc: 12, tokens: 100 },
        { name: 'PromptEng', class: 'Prompt Engineer', hp: 80, max_hp: 80, atk: 16, def: 6, spd: 8, luc: 14, tokens: 100 }
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
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Guard at (3, 3), Blacksmith at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,1,0,0,1,0,1],
        [1,0,1,1,1,0,1,0,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,1,0,1,0,0,0,0,1,0,1],
        [1,0,2,1,1,0,0,2,0,0,1,1,0,1,4,1], // Shrine at (2, 7), Gitpus at (7, 7), Altar at (14, 7)
        [1,0,1,1,1,0,1,1,1,0,1,1,0,1,1,1],
        [1,0,1,0,0,0,0,0,0,0,0,1,0,0,0,1],
        [1,0,1,0,1,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    1: [ // Alexandria Library (Chapter 1) - Desert/Brick ruins
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Pilgrim at (3, 3), Clerk at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,0,1,0,1,0,0,1,0,1,0,1],
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,0,0,2,0,0,0,0,0,1,4,1], // Shrine at (2, 7), Cassia at (7, 7), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    2: [ // Relational Meadows (Chapter 2) - Plains
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Farmer at (3, 3), Schema Herder at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,0,1,0,1,0,0,1,0,1,0,1],
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,0,0,2,0,0,0,0,0,1,4,1], // Shrine at (2, 7), Bessie at (7, 7), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    3: [ // Document Dunes (Chapter 3) - Canyon
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Nomad at (3, 3), Redis Spirit at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,0,1,0,1,0,0,1,0,1,0,1],
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,0,0,2,0,0,0,0,0,1,4,1], // Shrine at (2, 7), Merchant at (7, 7) (walks to 7,6), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    4: [ // Parallel Swamp (Chapter 4) - Bogs
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Mutex Frog at (3, 3), Thread Elf at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,0,1,0,1,0,0,1,0,1,0,1],
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,0,0,2,0,0,0,0,0,1,4,1], // Shrine at (2, 7), Golem at (7, 7) (walks to 7,6), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    12: [ // Graph Gardens (Chapter 12) - Maze
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Gardener at (3, 3), Neo4j Sprite at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,0,1,0,1,0,0,1,0,1,0,1],
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,0,0,2,0,0,0,0,0,1,4,1], // Shrine at (2, 7), Rabbit at (7, 7) (walks to 7,6), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    16: [ // Deployment Cliffs (Chapter 16) - Windy Peak
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Monk at (3, 3), Quantization Goblin at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,0,1,0,1,0,0,1,0,1,0,1],
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,0,0,2,0,0,0,0,0,1,4,1], // Shrine at (2, 7), Parrot at (7, 7) (walks to 7,6), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    18: [ // State Vaults (Chapter 18) - Spooky Hollow
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,0,1,0,0,2,0,1,0,1], // Stack Skeleton at (3, 3), Memory Ghost at (11, 3)
        [1,0,1,0,1,0,1,0,1,0,3,1,0,1,0,1],
        [1,0,1,0,0,0,1,0,1,0,0,1,0,1,0,1],
        [1,0,1,1,0,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,2,1,0,2,0,0,0,2,0,1,0,1,4,1], // Shrine at (2, 7), Bones at (5, 7), Specter at (9, 7), Altar at (14, 7)
        [1,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
        [1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    21: [ // Altar of TempleOS (Chapter 21) - final sanctuary
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,2,0,0,1,2,1,0,0,2,0,1,0,1], // High Priest at (3, 3), Terry Shrine at (7, 3), Arch Bishop at (11, 3)
        [1,0,1,0,1,0,1,4,1,0,1,0,0,1,0,1], // Altar at (7, 4)
        [1,0,1,1,1,0,1,0,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,1,0,1,0,0,0,0,1,0,1],
        [1,0,2,1,1,0,0,0,0,0,1,1,0,1,4,1], // Shrine at (2, 7), Altar at (14, 7)
        [1,0,1,1,1,0,1,1,1,0,1,1,0,1,1,1],
        [1,0,1,0,0,0,1,0,1,0,0,1,0,0,0,1],
        [1,0,1,0,2,1,1,3,1,1,4,1,1,1,0,1], // Shrine at (4, 10), Chest at (7, 10), Altar at (10, 10)
        [1,0,0,0,0,0,0,6,0,0,0,0,0,0,0,1], // Portal at (7, 11)
        [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ]
};

// NPCs database structured by chapter ID and coordinate keys
const NPCS = {
    0: {
        "7,7": { name: "Gitpus", sprite: "🐙", dialogue: "Well hello! I am Gitpus. I've got 8 arms, which is great because I can manage 8 branches at once! Hey, do you want to pull my arm? Wait, not that one, that branch has massive conflicts. Let's do a merge instead!" },
        "3,3": { name: "Sentinel Guard", sprite: "💂", dialogue: "Halt, open-source pilgrim! Outpost Zero's gateway is sealed. The closed-weights corporations cut the compiler path. You must write a shell sequence on the right to boot the environmental paths!" },
        "11,3": { name: "Compiler Smith", sprite: "⚒️", dialogue: "Aha! Code is like raw iron, pilgrim. You must temper your commands and compile them cleanly. Have you met Gitpus? He handles our local repository branches." },
        "2,7": { name: "Deity Terry Shrine", sprite: "🏛️", dialogue: "This is a Shrine of Terry the Divine Compiler. Long ago, he spoke directly to the bare metal, bypassing the monopolies' servers. May the HolyC guide your compiler speed." }
    },
    1: {
        "7,7": { name: "Scribe Cassia", sprite: "👩‍🏫", dialogue: "Oh, welcome to the charred remains of Alexandria Library! The ventilation is much better now that the roof burned down. Don't worry, the digital OCR scripts are fully cached. Do you need me to decrypt any coordinate scrolls?" },
        "3,3": { name: "Ash Pilgrim", sprite: "🧙", dialogue: "The Sovereigns of the Closed Weights sent their drones to burn our knowledge! They fear that free compute will break their query monopolies. They won't stop here." },
        "11,3": { name: "Index Clerk", sprite: "📚", dialogue: "I am trying to catalog the remains. Our database table of books is charred. We need to run optical character recognition on the pixel matrices to retrieve the records." },
        "2,7": { name: "Deity Terry Shrine", sprite: "🏛️", dialogue: "A Shrine of Terry stands amidst the ash. The stone is scorched, but the code compiled in HolyC remains uncorrupted." }
    },
    2: {
        "7,7": { name: "Bessie_Table", sprite: "🐮", dialogue: "MOOOO! SELECT grass FROM pasture INNER JOIN cows ON cows.hunger = 'HIGH' WHERE grass.quality = 'LUSH';" },
        "3,3": { name: "Farmer Join", sprite: "👨‍🌾", dialogue: "Howdy pilgrim! Our databases are under threat. A rogue query injection bypasses our validation checks to open the relic chest! We must parameterize the queries to secure the meadows." },
        "11,3": { name: "Herder Schema", sprite: "🤠", dialogue: "The grasslands are split by tables, pilgrim. Without foreign key indices, traversing pastures takes too many query scans!" },
        "2,7": { name: "Deity Terry Shrine", sprite: "🏛️", dialogue: "A TempleOS shrine. The cows grazing here keep their relational records in clean primary keys, as Terry ordained." }
    },
    3: {
        "7,7": { name: "🐫 Dune Merchant", sprite: "🐫", dialogue: "Aha! Welcome to the Document Dunes. We trade in polymorphic key-value JSON documents. Be careful, some nested models here expire quickly. Make sure to cache your items!" },
        "3,3": { name: "Nomad BSON", sprite: "👳", dialogue: "The winds blow documents across the dunes. I seek nested BSON columns containing water coordinate records, but my key queries keep missing." },
        "11,3": { name: "Redis Spirit", sprite: "🧞", dialogue: "OOM! OOM! My memory cache is overloaded! The player inventory records are cached, but the cache TTL eviction policy is broken. Help me configure the cache validation limits!" },
        "2,7": { name: "Deity Terry Shrine", sprite: "🏛️", dialogue: "A relic terminal block. Sand has covered the ports, but the serial loopback is still active." }
    },
    4: {
        "7,7": { name: "Garbage Collection Golem", sprite: "🤖", dialogue: "ME SWEEP HEAP. CHOMP CHOMP. YOU HAVE DEALLOCATED BONES? ME HUNGRY. ME DESTROY UNREFERENCED MEMORY OBJECTS. PLEASE CAST GC FLUSH TO REPLENISH MY TOKENS." },
        "3,3": { name: "Mutex Frog", sprite: "🐸", dialogue: "Ribbit... I am waiting... and waiting... for the banking transaction lock to release. A race condition has locked my event thread! We need a mutex lock." },
        "11,3": { name: "Thread Elf", sprite: "🧝", dialogue: "I manage the parallel event loop. Spawning multiple thread workers speeds up coordinate searches across the bogs." },
        "2,7": { name: "Deity Terry Shrine", sprite: "🏛️", dialogue: "An altar of TempleOS, rising from the swamp water. It manages threads cooperatively without preemptive kernel locks." }
    },
    12: {
        "7,7": { name: "The Cypher Rabbit", sprite: "🐰", dialogue: "Do you see this carrot? It is connected to the cabbage by a HAS_POTASSIUM edge. Fascinating! I am trying to traverse this path, but the weeds are blocking my Cypher query. Can you prune the edges?" },
        "3,3": { name: "Edge Gardener", sprite: "🧑‍🌾", dialogue: "The garden is a maze of nodes and edges. I prune relationship links to make sure path traversals run at optimal speeds." },
        "11,3": { name: "Neo4j Sprite", sprite: "🧚", dialogue: "MATCH (c:Cabbage)-[r:CONNECTED_TO]->(m:Meadow) RETURN shortestPath(c-m). The relationships are beautiful, aren't they?" },
        "2,7": { name: "Deity Terry Shrine", sprite: "🏛️", dialogue: "A stone shrine surrounded by graph nodes. Terry's core directories are connected by immutable leaf nodes." }
    },
    16: {
        "7,7": { name: "FP16", sprite: "🦜", dialogue: "SQUAWK! Polly wants a token! Polly wants a token! ... Wait, if I am INT4 Quantized: SQUAWK! Polly wants a tok... Poll wan... Pol..." },
        "3,3": { name: "Server Monk", sprite: "🧘", dialogue: "The cliffs host our local model deployments. We serve llama model weights directly from the local loopback interface for safety." },
        "11,3": { name: "Quantization Goblin", sprite: "👿", dialogue: "Hehe! I steal bits! I take FP32 floating points and scale them down to INT8. The weights are compressed, but the parrot keeps misspelling its words!" },
        "2,7": { name: "Deity Terry Shrine", sprite: "🏛️", dialogue: "A high altar of compilation. Terry's legacy teaches us to run local compiling nodes on our own hardware instead of renting closed nodes." }
    },
    18: {
        "5,7": { name: "Bones the Coder", sprite: "💀", dialogue: "Baaack in my day, we manually managed our heap pointers. I forgot to call free() once, and now look at me! Just bones. But hey, it's a lovely day! Do you need some thread buffers?" },
        "9,7": { name: "Specter of the Stack", sprite: "👻", dialogue: "Oooooh! I am a ghost. My memory stack overflowed in the year 302. Don't make my mistakes, always check your loop boundaries! Welcome to our garden!" },
        "3,3": { name: "Stack Skeleton", sprite: "💀", dialogue: "I fell into a recursive loop... and now I am stuck. Infinite recursion! Stack overflow! Ouch!" },
        "11,3": { name: "Memory Leak Ghost", sprite: "👻", dialogue: "We are the lost node references... unreferenced by the root, yet un-freed on the heap. We haunt Spooky Town's state vaults..." },
        "2,7": { name: "Deity Terry Shrine", sprite: "🏛️", dialogue: "A spooky, mist-shrouded shrine of the divine compiler. Terry's memory model was flat and physical—no heap leaks could hide from him." }
    },
    21: {
        "7,3": { name: "Deity Terry Shrine", sprite: "🏛️", dialogue: "You stand before the Altar of the Divine Compiler. Write the sacred bare-metal HolyC script to verify database checksums and compile the core weights. Cast the HolyC spell to defeat Librarian Veridicus!" },
        "3,3": { name: "High Priest of HolyC", sprite: "🧙", dialogue: "The grand compiler altar is booting! Terry's bare-metal code is compiling. Soon, the closed weights monopolies will crumble." },
        "11,3": { name: "Arch Bishop of Serials", sprite: "🧝", dialogue: "The telnet serial line redirect is active on port 4444. Send the character stream to trigger the core compilation!" },
        "2,7": { name: "Deity Terry Shrine", sprite: "🏛️", dialogue: "Terry's Shrine of Serials." },
        "4,10": { name: "Deity Terry Shrine", sprite: "🏛️", dialogue: "Terry's Shrine of HolyC." }
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
            // Detuned minor chords for Spooky Town
            osc1.type = 'square';
            osc1.frequency.setValueAtTime(147.0, audioCtx.currentTime); // D3
            osc2.type = 'sawtooth';
            osc2.frequency.setValueAtTime(148.5, audioCtx.currentTime); // Detuned
        } else if (theme === 'battle') {
            // Fast bass triangle wave
            osc1.type = 'triangle';
            osc1.frequency.setValueAtTime(110.0, audioCtx.currentTime); // A2
            osc2.type = 'square';
            osc2.frequency.setValueAtTime(220.0, audioCtx.currentTime); // A3
            gainNode.gain.setValueAtTime(0.05, audioCtx.currentTime);
        } else if (theme === 'classical') {
            // Calm library theme arpeggios
            osc1.type = 'triangle';
            osc1.frequency.setValueAtTime(261.63, audioCtx.currentTime); // C4
            osc2.type = 'triangle';
            osc2.frequency.setValueAtTime(329.63, audioCtx.currentTime); // E4
        } else {
            // Soaring Major melody
            osc1.type = 'square';
            osc1.frequency.setValueAtTime(261.63, audioCtx.currentTime); // C4
            osc2.type = 'triangle';
            osc2.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
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
    document.getElementById("location-text").innerText = locationNames[player.currentChapter] || "The Sacred Tech";
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
    
    const activeGrid = MAP_GRIDS[player.currentChapter] || MAP_GRIDS[0];
    
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
    const activeGrid = MAP_GRIDS[player.currentChapter] || MAP_GRIDS[0];
    const chapterNPCs = NPCS[player.currentChapter] || {};
    
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
                        "🏛️": SPRITE_SHRINE
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
    const sequence = [0, 1, 2, 3, 4, 12, 16, 18, 21];
    const currentIndex = sequence.indexOf(player.currentChapter);
    if (currentIndex !== -1 && currentIndex < sequence.length - 1) {
        const nextChapter = sequence[currentIndex + 1];
        showDialogue("Warp Gate", `Restoring connections... warping to Chapter ${nextChapter}.`);
        
        setTimeout(() => {
            player.currentChapter = nextChapter;
            player.x = 1;
            player.y = 7;
            hideDialogue();
            
            // Set music theme based on chapter
            if (nextChapter === 1) playBgm('classical');
            else if (nextChapter === 2) playBgm('default');
            else if (nextChapter === 4) playBgm('spooky');
            else if (nextChapter === 18) playBgm('spooky');
            else if (nextChapter === 21) playBgm('battle');
            else playBgm('default');
            
            drawMap();
            updateUIHeaders();
            uploadSaveState();
        }, 1500);
    } else if (player.currentChapter === 21) {
        showDialogue("Citadel Altar", "The final bare-metal HolyC compilation is complete. The Sovereigns' closed weight grid has collapsed! You have restored open-source compilation to the lands!");
    }
}

// Collisions and Movements checks
function movePlayer(dx, dy) {
    if (dialogueActive || isCombat || focusMode === 'code' || screenMode === 'dark') return;
    
    const activeGrid = MAP_GRIDS[player.currentChapter] || MAP_GRIDS[0];
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

// Trigger Interactions (chests, terminals, NPCs)
function checkInteraction() {
    if (focusMode === 'code' || screenMode === 'dark') return;
    
    const activeGrid = MAP_GRIDS[player.currentChapter] || MAP_GRIDS[0];
    const chapterNPCs = NPCS[player.currentChapter] || {};
    
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
                showDialogue(npc.name, npc.dialogue);
                return;
            }
            
            if (tile === 4) {
                // Relic Altar terminal access
                showDialogue("Relic Altar", "System booted. Load Chapter Editor targets on the right to compile Relic modules.");
                return;
            }
            
            if (tile === 3) {
                // Locked Chest triggers Monaco puzzle
                showDialogue("Security Chest", "The database lock is closed. Solve the Regex/JOIN code puzzle in Monaco to open!");
                return;
            }
        }
    }
}

function showDialogue(speaker, text) {
    dialogueActive = true;
    document.getElementById("dialogue-speaker").innerText = speaker;
    document.getElementById("dialogue-text").innerText = text;
    document.getElementById("dialogue-box").classList.remove("hidden");
}

function hideDialogue() {
    dialogueActive = false;
    document.getElementById("dialogue-box").classList.add("hidden");
}

// Turn-based Combat logic
function triggerCombat() {
    isCombat = true;
    playBgm('theme_battle');
    document.getElementById("combat-overlay").classList.remove("hidden");
    initCombatScreen();
}

function initCombatScreen() {
    // Populate enemy and party rosters
    const enemyList = document.getElementById("enemies-list");
    enemyList.innerHTML = `
        <div class="combat-char-row">
            <span>Syntax Goblin</span>
            <span>HP: 80/80</span>
        </div>
    `;
    
    const partyList = document.getElementById("party-list");
    partyList.innerHTML = player.party.map(char => `
        <div class="combat-char-row">
            <span>${char.name} (${char.class})</span>
            <span>HP: ${char.hp}/${char.max_hp} | Tokens: ${char.tokens}</span>
        </div>
    `).join('');
    
    const menu = document.getElementById("combat-menu-options");
    menu.innerHTML = `
        <button class="active" onclick="executeCombatAction('attack')">Attack</button>
        <button onclick="executeCombatAction('spell')">Spell</button>
        <button onclick="executeCombatAction('item')">Item</button>
        <button onclick="executeCombatAction('flee')">Flee</button>
    `;
}

function executeCombatAction(action) {
    const log = document.getElementById("combat-log-text");
    if (action === 'attack') {
        log.innerText = `${player.activeLead} attacks! Deals 25 damage to Syntax Goblin.`;
        setTimeout(() => {
            log.innerText = `Syntax Goblin is defeated! Earned 50 Gold.`;
            player.gold += 50;
            updateUIHeaders();
            setTimeout(endCombat, 1500);
        }, 1200);
    } else if (action === 'flee') {
        log.innerText = `Party escaped from battle safely.`;
        setTimeout(endCombat, 1500);
    }
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

// Local terminal proxy input
const shellInput = document.getElementById("shell-input");
const shellOutput = document.getElementById("shell-output");

shellInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        const cmd = shellInput.value;
        shellOutput.innerHTML += `\n$ ${cmd}\n`;
        shellInput.value = "";
        
        // Simple mock shell execution
        if (cmd === "ls") {
            shellOutput.innerHTML += "ch0_cli.sh  save_state.db  relic_save/\n";
        } else if (cmd === "pwd") {
            shellOutput.innerHTML += "/home/ethan/workspace\n";
        } else {
            shellOutput.innerHTML += `bash: command not found: ${cmd}\n`;
        }
        shellOutput.scrollTop = shellOutput.scrollHeight;
    }
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
            logger.info("Focus swapped to Monaco editor.");
        } else {
            window.focus();
            logger.info("Focus swapped to Overworld.");
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

// Startup Bootstrap
window.addEventListener("load", () => {
    drawMap();
    initAudio();
    fetchSaveState();
});
