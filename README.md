# ChessMastery3D

**AAA-style 3D chess + “Edition 2” coaching.**
Hot-seat & AI, blitz clocks, promotion GUI, eval bar, themes, multilingual UI, PGN export. Built with **Ursina (Panda3D)** and **python-chess**. Optional **Stockfish** support if found on PATH.

[https://github.com/id01tsoftwaresgit/ChessMastery3D](https://github.com/id01tsoftwaresgit/ChessMastery3D)

---

## ✨ Why this exists

A beautiful, fast 3D chess experience that **teaches you to think like a champion**. The in-game coach highlights **center control, activity, initiative/tempo, and endgame triggers**, translating the *Chess Mastery – Edition 2* playbook into actionable tips while you play.

---

## 🚀 Features

* **AAA look & feel:** dynamic lighting, shadowed pieces, last-move glow, capture pop, themed boards.
* **Play modes:** Hot-seat PvP, PvAI (choose side), optional AIvAI.
* **Coach overlays:** center-control markers, quick tips on activity/initiative; endgame prompts.
* **Game systems:** legal moves, promotion selector, undo, board flip, blitz clocks.
* **Analysis:** lightweight eval bar (material+mobility+center+castling signals).
* **AI:** 3 built-in levels (randomish→greedy→minimax 2-ply).
  If **Stockfish** is installed, the engine is auto-used for stronger play.
* **Productivity:** **PGN export**, help overlay, save-ready UI.
* **Localization:** EN / ES / ID / RU / DE.
* **Theming:** 3 board themes (switch live).

---

## 🧩 Quick Start

### Requirements

* **Windows 10/11**, macOS, or Linux
* **Python 3.10+**
* A **hardware OpenGL** GPU driver (see Troubleshooting if you see “GDI Generic”)

### Install & Run

```bash
git clone https://github.com/your-org/ChessMastery3D.git
cd ChessMastery3D
pip install -r requirements.txt  # or: pip install ursina python-chess
python game/aaa_chess_3d_final.py
```

> **Tip:** If your file is named `chess.py`, rename it (e.g., `aaa_chess_3d_final.py`). A file called `chess.py` shadows the `python-chess` library.

### Optional: Stockfish

* Install Stockfish and ensure `stockfish` is on your **PATH**.
  The game will detect it and use it automatically for stronger AI (level 3+).

---

## 🎮 Controls

* **Left click:** select/move
* **Right click:** cancel selection
* **A:** toggle Coach
* **F1:** AI plays Black (on/off)
* **F2:** cycle AI level (1–3; uses Stockfish when available)
* **TAB:** flip board
* **Backspace:** undo last move
* **N:** new game
* **P:** export PGN (`game.pgn`)
* **+ / -:** add/remove 60s to both clocks
* **R:** reset clocks
* **1 / 2 / 3:** switch themes
* **L:** cycle UI language
* **H:** help overlay

---

## 🖼️ Project Structure

```
ChessMastery3D/
├─ game/
│  └─ aaa_chess_3d_final.py     # main single-file game (Ursina + python-chess)
├─ assets/                       # (optional) future meshes, fonts, sounds
├─ docs/                         # screenshots, store images
├─ requirements.txt
└─ LICENSE
```

**requirements.txt**

```
ursina>=8
python-chess>=1.999
```

---

## 🧪 Packaging (Windows Example)

Create a standalone EXE (PyInstaller):

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean ^
  --name ChessMastery3D ^
  --hidden-import ursina.shaders ^
  --collect-all ursina --collect-all panda3d --collect-all panda3d_gltf ^
  game/aaa_chess_3d_final.py
```

Output will be in `dist/ChessMastery3D`.

---

## 🛠️ Troubleshooting

**OpenGL “GDI Generic” error**
Your system is using software rendering. Fix:

1. Install/Update your **GPU driver** (NVIDIA/AMD/Intel).
2. On RDP/VM, enable hardware graphics for remote sessions.
3. As a fallback, use **Mesa software OpenGL** (drop `opengl32.dll`, `libglapi.dll`, `d3dcompiler_47.dll` next to `python.exe` or the game EXE).

**Module name conflict (`AttributeError: module 'chess' has no attribute 'Board'`)**
Rename any local `chess.py`; delete `__pycache__/`.

---

## 🧠 Design Notes (Coach)

* **Center control:** live overlay on d4/e4/d5/e5; tips nudge space/tempo decisions.
* **Activity & initiative:** warns when mobility/captures are low; encourages piece activation and file opening.
* **Endgame triggers:** when piece count drops, prompts king activation and passed-pawn play.
* **Eval bar:** fast heuristic that tracks material, mobility, center, and safety hints.

---

## 🗺️ Roadmap

* Online multiplayer (asyncio/WebSocket) + lobbies & ELO
* Replay viewer with arrows & engine lines
* Tactics/Drills: **Edition 2** mastery packs (center domination, initiative sprint, endgame labs)
* Cosmetics (piece sets, boards, camera rigs) and seasonal content
* Save/load, cloud sync
* Steam/Microsoft Store builds

---

## 💼 Monetization & Bundles

* **Free core** + optional **training DLC** aligned with the book.
* **Bundles:** eBook + game + drill packs for Amazon/Google Play Books/Microsoft Store.
* **Cosmetics:** premium piece sets and themes (non-pay-to-win).

---

## 🤝 Contributing

PRs welcome. Keep code clean, documented, and portable.
Please include before/after screenshots for visual/UI changes.

---

## ⚖️ License

**MIT** (recommended). Include Stockfish license when bundling the engine binary.

---

## 🙏 Credits

* **Ursina** (Panda3D)
* **python-chess**
* Optional **Stockfish** (UCI engine)

---


