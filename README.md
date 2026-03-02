# Tetris Solver

Two AI approaches to the same problem: placing Tetris pieces optimally on a board. The **A\* search** version uses heuristic evaluation to find the best placement sequence, while the **Prolog backtracking** version explores all valid placements through constraint satisfaction. Same game, fundamentally different paradigms.

Built as a university project for the **Fundamentos de Sistemas Inteligentes (FSI)** course.

## Comparison

| | A* Search (Python) | Backtracking (Prolog) |
|---|---|---|
| **Algorithm** | A* with weighted heuristic | Depth-first backtracking |
| **Search type** | Informed (guided by cost function) | Uninformed (exhaustive exploration) |
| **Board** | 5 × 20 | 5 × 4 |
| **Piece types** | 7 (all standard Tetris pieces) | 4 (T, Square, L, L-inverted) |
| **Optimization** | Minimizes height + holes, maximizes cleared lines | Finds any valid placement via constraints |
| **Visualization** | Pygame window with animated piece drops | Console output of board state and solution |
| **Language** | Python | Visual Prolog |

## A* Search (Python)

The A* implementation treats Tetris as a search problem: each state is a board configuration, and each action is placing a piece at a specific position and rotation. The algorithm explores states ordered by `f(n) = g(n) + h(n)`, where the cost function balances multiple board quality metrics.

### Heuristic

The evaluation function combines four weighted factors:

| Factor | Weight | Goal |
|--------|--------|------|
| **Aggregate height** | 0.5 | Penalize tall stacks |
| **Holes** | 1.0 | Penalize gaps below filled cells |
| **Irregularity** | 0.5 | Penalize uneven column heights |
| **Cleared lines** | 10.0 | Reward completing full rows |

### How it works

1. Generate a random sequence of 50 pieces
2. Create the initial node with an empty board
3. For each state, generate all possible successors (every valid rotation × position for the current piece)
4. Evaluate each successor with `g(n)` (accumulated cost) + `h(n)` (heuristic estimate)
5. Expand the most promising node from the priority queue
6. Track visited states in a closed set to avoid redundant exploration
7. When all pieces are placed, reconstruct and animate the solution path

### Running it

```bash
cd python
pip install -r requirements.txt
python tetris.py
```

A Pygame window opens showing each piece falling to its A*-determined optimal position.

## Backtracking (Prolog)

The Prolog version models piece placement as a constraint satisfaction problem. Each piece type defines placement rules for every orientation and column, and Prolog's built-in backtracking explores all valid combinations until a solution is found.

### Board representation

The board is represented as `tab(Suelo, Tabla)`:

- **Suelo** (floor): A list of 5 column heights `[0,0,0,0,0]` tracking how high each column is filled
- **Tabla** (table): A list of 4 rows, each containing a row number and 5 cell values (0 = empty, 1 = filled)

```prolog
% Empty board
tab([0,0,0,0,0], [[4,0,0,0,0,0],
                   [3,0,0,0,0,0],
                   [2,0,0,0,0,0],
                   [1,0,0,0,0,0]])
```

### Piece placement

Each piece type has rules for every orientation (0-3) and valid column. The `mete/3` predicate handles placement by:

1. Checking column boundaries for the piece width
2. Reading current floor heights for affected columns
3. Verifying the piece fits without exceeding the board
4. Updating the board rows and floor heights
5. Cleaning any completed rows via `limpia_filas/4`

### Implemented pieces

| Type | Shape | Orientations |
|------|-------|-------------|
| 1 | T-shape | 4 (horizontal base, right extension, inverted, left extension) |
| 2 | Square | 1 (rotation-invariant) |
| 3 | L-shape | 4 (all rotations) |
| 4 | L-inverted | 4 (all rotations) |

### How it works

```prolog
% Solve: place pieces [T, Square, L, L] on an empty board
tetris() :-
    vacia(T),
    backtrack([1,2,3,3], T, [], Solution),
    write(Solution).
```

The `backtrack/4` predicate recursively:
1. Takes the next piece from the sequence
2. Tries all valid orientations and columns via `regla/5`
3. If placement succeeds, continues with the remaining pieces
4. If placement fails, Prolog automatically backtracks to try the next option

### Running it

Open `prolog/tetris.pro` in Visual Prolog 5.2 and run the `tetris` goal.

## Project structure

```
├── python/
│   ├── tetris.py            # A* solver with Pygame visualization
│   └── requirements.txt     # pygame==2.6.1
└── prolog/
    └── tetris.pro           # Backtracking solver in Visual Prolog
```

## Tech stack

| | |
|---|---|
| **Python** | A* search, heuristic evaluation, Pygame rendering |
| **Prolog** | Constraint-based backtracking, logic programming |
| **Pygame** | Board visualization and piece animation |
| **Visual Prolog 5.2** | Prolog development environment |

## Context

Built for the **Fundamentos de Sistemas Inteligentes (FSI)** course at Universidad de Salamanca, 2025. The project compares two search paradigms — informed heuristic search vs. uninformed exhaustive backtracking — applied to the same combinatorial problem.
