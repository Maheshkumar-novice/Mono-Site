# Tic Tac Toe — How It Works

A configurable Tic Tac Toe game built with pure HTML, CSS, and JavaScript. No frameworks, no build tools, no dependencies — just one file.

## Table of Contents

- [Features](#features)
- [How the Board Works](#how-the-board-works)
- [How Win Detection Works](#how-win-detection-works)
- [How the AI Works](#how-the-ai-works)
  - [Small Boards: Minimax](#small-boards-minimax)
  - [Large Boards: Heuristic](#large-boards-heuristic)
- [How the UI Works](#how-the-ui-works)
- [Key Concepts for Beginners](#key-concepts-for-beginners)

---

## Features

- **Configurable board**: 3×3 up to 7×7
- **Win length scales with board size**: 3×3 needs 3 in a row, 5×5 needs 5, etc.
- **Two modes**: Play against AI or another person
- **Choose your side**: Play as X (first move) or O (second move)
- **Score tracking**: Wins and draws tracked across games
- **Responsive design**: Works on desktop and mobile

---

## How the Board Works

The board is stored as a **flat array** (1D), not a 2D grid. A 3×3 board looks like:

```
Index:  0 | 1 | 2
        3 | 4 | 5
        6 | 7 | 8
```

To convert between flat index and row/column:

```javascript
row = Math.floor(index / size)    // index 5 on 3×3 → row 1
col = index % size                // index 5 on 3×3 → col 2
index = row * size + col          // row 1, col 2 → index 5
```

Each cell is either `''` (empty), `'X'`, or `'O'`.

**Why a flat array?** Simpler to iterate, easier to check if the board is full (`board.every(c => c)`), and works the same regardless of board size.

---

## How Win Detection Works

To win, a player needs N consecutive marks in a line, where N = board size.

We check **4 directions** from every cell:

```
→  Horizontal    (dr=0, dc=1)
↓  Vertical      (dr=1, dc=0)
↘  Diagonal      (dr=1, dc=1)
↙  Anti-diagonal (dr=1, dc=-1)
```

For each cell (r, c) and each direction, we look ahead N steps:

```javascript
for (let k = 0; k < winLen; k++) {
    const nr = r + dr * k;   // next row
    const nc = c + dc * k;   // next col
    // Check if in bounds and belongs to the player
}
```

If all N cells in a line belong to the same player, they win. We return the winning cell indices so the UI can highlight them.

**Time complexity**: O(size² × 4 × winLen) per check — fast enough even for 7×7.

---

## How the AI Works

### Small Boards: Minimax

For 3×3 and 4×4 boards, we use the **Minimax algorithm** — the same algorithm used in chess engines (at a simpler scale).

#### The Idea

Minimax assumes both players play **optimally**. It builds a tree of all possible future moves and picks the one that leads to the best guaranteed outcome.

```
Current board (AI's turn)
├── AI plays cell 0 → score?
│   ├── Opponent plays cell 1 → score?
│   │   ├── AI plays cell 2 → ...
│   │   └── AI plays cell 3 → ...
│   └── Opponent plays cell 2 → score?
├── AI plays cell 1 → score?
└── AI plays cell 4 → score?
```

#### Scoring

- AI wins → `+100 - depth` (winning sooner is better)
- Opponent wins → `depth - 100` (losing later is less bad)
- Draw or depth limit → `0`

```javascript
if (checkWin(aiPlayer)) return 100 - depth;   // AI won
if (checkWin(opponent)) return depth - 100;    // Opponent won
if (board full || depth >= maxDepth) return 0; // Draw
```

#### Maximizing and Minimizing

- **AI's turn (maximizing)**: Pick the move with the **highest** score
- **Opponent's turn (minimizing)**: Pick the move with the **lowest** score

This back-and-forth is why it's called "minimax".

#### Alpha-Beta Pruning

Without optimization, minimax checks every possible game state. For 3×3, that's up to 9! = 362,880 states. **Alpha-beta pruning** skips branches that can't possibly affect the result:

```javascript
alpha = Math.max(alpha, best);  // Best score AI can guarantee
beta = Math.min(beta, best);    // Best score opponent can guarantee
if (beta <= alpha) break;       // No need to check further
```

This typically cuts the search space by 50-90%.

#### Depth Limit

For 4×4, the full tree is too large (16! states). We limit search depth to 6 levels and return 0 (neutral) for positions we can't fully evaluate. This makes the AI fast but not perfect on 4×4.

### Large Boards: Heuristic

For 5×5 and above, minimax is too slow even with pruning. We use a **heuristic** (rule-based) approach instead:

#### Priority Order

1. **Win**: If AI can win in one move, take it
2. **Block**: If opponent can win in one move, block it
3. **Score positions**: Rate each empty cell by how useful it is

#### Position Scoring

For each empty cell, we look at every possible winning line that passes through it:

```javascript
for (each direction) {
    for (each possible line of winLen through this cell) {
        count friendly pieces and empty spaces
        if no opponent pieces block this line:
            score += friendly² + 1
    }
}
```

**Why friendly²?** Having 3 in a line is much more valuable than 3 scattered pieces:
- 1 in a line → 1² + 1 = 2 points
- 2 in a line → 2² + 1 = 5 points
- 3 in a line → 3² + 1 = 10 points

We also slightly prefer **center positions** since they have more winning lines passing through them.

---

## How the UI Works

### CSS Grid for the Board

The board uses CSS Grid, which makes any N×N layout trivial:

```javascript
boardEl.style.gridTemplateColumns = `repeat(${size}, ${cellSize}px)`;
```

Cell sizes are computed dynamically based on screen width:

```javascript
const maxBoard = Math.min(window.innerWidth - 48, 400);
const cellSize = Math.floor((maxBoard - (size + 1) * 4) / size);
```

### State Management

All game state lives in simple variables:

```javascript
let board = [];       // Array of '' | 'X' | 'O'
let turn = 'X';       // Whose turn
let gameOver = false;  // Is the game finished
let scores = { X: 0, O: 0, draw: 0 };
```

No classes, no state management library — just variables and functions. When settings change, `init()` resets everything.

### AI Timing

The AI move has a 200ms delay (`setTimeout(aiMove, 200)`) so it doesn't feel instant. Without this, the AI response is so fast it feels like nothing happened.

---

## Key Concepts for Beginners

If you're learning programming, this project touches several important concepts:

| Concept | Where It's Used |
|---|---|
| **Arrays** | Board storage, win checking |
| **2D ↔ 1D mapping** | `row * size + col` conversion |
| **Recursion** | Minimax tree search |
| **Backtracking** | Try a move, evaluate, undo it |
| **Greedy algorithms** | Heuristic picks the best-looking move |
| **Alpha-beta pruning** | Optimization technique for tree search |
| **Event handling** | Click listeners on cells and buttons |
| **CSS Grid** | Dynamic N×N layouts |
| **State machines** | Game states (playing, won, draw) |
| **DOM manipulation** | Creating cells, updating text, adding classes |

### Want to Extend This?

Some ideas to try:

- **Undo button**: Store move history in an array, pop the last move
- **Difficulty levels**: Limit minimax depth or make the heuristic intentionally weaker
- **Animations**: Animate X/O appearing using CSS transitions
- **Sound effects**: Play audio on move and win using the Web Audio API
- **Online multiplayer**: Use WebSockets to share moves between two browsers
