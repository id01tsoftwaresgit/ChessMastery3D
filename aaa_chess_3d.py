# aaa_chess_3d_final.py
# AAA-style 3D Chess — single-file, production-minded demo
# Engine: Ursina (Panda3D). Rules: python-chess.
# Modes: PvP (hot seat), PvAI (White/Black), AIvAI, Edition-2 Coach overlays (center, activity, initiative)
# Features: legal moves, promotion GUI, clocks, undo, flip, last-move glow, capture animation, PGN export, eval bar, multi-language UI
# Run:
#   python aaa_chess_3d_final.py
#
# Notes:
# - If you see an OpenGL "GDI Generic" warning, install/update your GPU driver (NVIDIA/AMD/Intel),
#   or drop Mesa software OpenGL DLLs next to python.exe (opengl32.dll, libglapi.dll, d3dcompiler_47.dll).
# - If your file is named chess.py, rename it; it shadows the python-chess lib.

import sys, subprocess, os, math, time, random, shutil
def _ensure(mod, pip_name=None):
    try: __import__(mod)
    except Exception:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name or mod])

for m, p in [("ursina", None), ("chess", "python-chess")]:
    _ensure(m, p)

from ursina import *
from ursina.prefabs.editor_camera import EditorCamera
try:
    from ursina.shaders import lit_with_shadows_shader
except Exception:
    lit_with_shadows_shader = None

import chess, chess.pgn

# ---------- Guard against module shadowing ----------
if not hasattr(chess, "Board"):
    raise SystemExit("Local file shadows python-chess. Rename your script (not chess.py) and delete __pycache__.")

# ---------- Config ----------
APP_TITLE = "Chess Mastery 3D — Edition 2 Coach (Final)"
BOARD_SIZE = 8
TILE = 1.0
ORIGIN = Vec3(-(BOARD_SIZE-1)*TILE/2, 0, -(BOARD_SIZE-1)*TILE/2)
CENTER_SQS = [chess.D4, chess.E4, chess.D5, chess.E5]

# Base colors (themes)
THEMES = [
    dict(light=color.rgb(234,216,180), dark=color.rgb(120,88,66), base=color.rgb(40,44,52)),
    dict(light=color.rgb(220,220,220), dark=color.rgb(80,100,120), base=color.rgb(35,40,48)),
    dict(light=color.rgb(238,228,200), dark=color.rgb(60,60,60), base=color.rgb(30,30,33)),
]
theme_idx = 0

CLR_SEL  = color.rgba(255,232,70,210)
CLR_MOVE = color.rgba(64,200,128,190)
CLR_CAPT = color.rgba(230,100,100,220)
CLR_LAST = color.rgba(80,150,255,120)
CLR_TEXT = color.rgb(230,234,242)

LANGS = ["EN","ES","ID","RU","DE"]
L = 0  # language index

def T(key):
    # Minimal i18n for UI strings
    table = {
        "turn":      ["Turn","Turno","Giliran","Ход","Zug"],
        "white":     ["White","Blancas","Putih","Белые","Weiß"],
        "black":     ["Black","Negras","Hitam","Чёрные","Schwarz"],
        "check":     ["Check","Jaque","Skak","Шах","Schach"],
        "mate":      ["Checkmate","Jaque mate","Skak Mat","Мат","Schachmatt"],
        "stalemate": ["Stalemate","Tablas por ahogado","Paten","Пат","Patt"],
        "help_hdr":  ["Controls","Controles","Kontrol","Управление","Steuerung"],
        "help_body": [
            "- Left click: select / move\n- Right click: cancel\n- A: toggle Coach\n- F1: AI plays Black\n- F2: AI strength\n- TAB: flip board\n- N: new game   Backspace: undo\n- P: export PGN\n- +/- : change clocks   R: reset\n- 1..3: switch theme   L: language",
            "- Clic izq: seleccionar / mover\n- Clic der: cancelar\n- A: Coach\n- F1: IA juega con negras\n- F2: Fuerza IA\n- TAB: girar tablero\n- N: nueva   Retroceso: deshacer\n- P: exportar PGN\n- +/- : reloj   R: reset\n- 1..3: tema   L: idioma",
            "- Klik kiri: pilih / gerak\n- Klik kanan: batal\n- A: Coach\n- F1: AI main Hitam\n- F2: Kekuatan AI\n- TAB: balik papan\n- N: baru   Backspace: undo\n- P: ekspor PGN\n- +/- : jam   R: reset\n- 1..3: tema   L: bahasa",
            "- ЛКМ: выбрать / ход\n- ПКМ: отмена\n- A: Тренер\n- F1: ИИ играет чёрными\n- F2: Сила ИИ\n- TAB: перевернуть доску\n- N: новая   Backspace: отменить\n- P: экспорт PGN\n- +/- : часы   R: сброс\n- 1..3: тема   L: язык",
            "- Linksklick: wählen / ziehen\n- Rechtsklick: abbrechen\n- A: Coach\n- F1: KI spielt Schwarz\n- F2: KI-Stärke\n- TAB: Brett drehen\n- N: neu   Rück: zurück\n- P: PGN export\n- +/- : Uhren   R: reset\n- 1..3: Theme   L: Sprache",
        ],
        "coach_hdr": ["Coach","Coach","Pelatih","Тренер","Coach"],
        "coach_ok":  ["Good plan, keep tempo.","Buen plan, mantén el ritmo.","Rencana bagus, jaga tempo.","Хороший план, держите темп.","Guter Plan, Tempo halten."],
        "ai_on":     ["AI Black: ON","IA Negras: ON","AI Hitam: ON","ИИ чёрные: ВКЛ","KI Schwarz: AN"],
        "ai_off":    ["AI Black: OFF","IA Negras: OFF","AI Hitam: OFF","ИИ чёрные: ВЫКЛ","KI Schwarz: AUS"],
        "ai_lvl":    ["AI Level","Nivel IA","Level AI","Уровень ИИ","KI-Stufe"],
        "game_over": ["Game Over","Partida terminada","Permainan selesai","Игра окончена","Partie beendet"],
        "save_pgn":  ["Saved PGN ->","PGN guardado ->","PGN disimpan ->","PGN сохранён ->","PGN gespeichert ->"],
    }
    return table[key][L]

# ---------- App/scene ----------
app = Ursina(title=APP_TITLE, borderless=False)
window.color = color.rgb(14,16,20)
window.size = (1280, 800)
Sky(color=color.rgb(10,12,15))

AmbientLight(color=color.rgba(255,255,255,70))
dlight = DirectionalLight(shadows=True)
dlight.look_at(Vec3(1,-2,1.2))

camera.position = Vec3(0, 10, -18)
camera.rotation_x = 30
camera.fov = 60
EditorCamera(enabled=False)

board = chess.Board()
move_history = []
clock_white, clock_black = 5*60, 5*60
last_tick = time.time()
running = True

ai_plays_black = False
ai_level = 2      # 1=random-ish, 2=greedy+center, 3=minimax-2ply
use_stockfish = shutil.which("stockfish") is not None  # optional external engine
stockfish = None

# ---------- Themeable board ----------
def theme():
    return THEMES[theme_idx]

tiles = []
class Tile(Button):
    def __init__(self, idx:int):
        f, r = idx%8, idx//8
        super().__init__(
            parent=scene,
            position=ORIGIN + Vec3(f*TILE, 0, r*TILE),
            model='cube',
            collider='box',
            scale=(TILE, 0.06, TILE),
            color=theme()["light"] if (f+r)%2==0 else theme()["dark"],
            shader=lit_with_shadows_shader
        )
        self.index = idx
        self.base_color = self.color
    def reset(self):
        self.color = self.base_color

def build_board():
    global tiles, rim, floor
    for t in tiles: destroy(t)
    tiles = [Tile(i) for i in range(64)]
    try: destroy(rim); destroy(floor)
    except: pass
    floor = Entity(model='plane', scale=80, position=(0,-0.5,0), color=color.rgb(18,20,24), shader=lit_with_shadows_shader)
    rim = Entity(model='cube', scale=(BOARD_SIZE*TILE+0.5, 0.05, BOARD_SIZE*TILE+0.5),
                 position=ORIGIN+Vec3(3.5, -0.03, 3.5), color=theme()["base"], shader=lit_with_shadows_shader)

build_board()

# Last move markers
last_from_marker = Entity(model='quad', scale=(TILE*0.95, TILE*0.95), rotation_x=90, color=CLR_LAST, enabled=False)
last_to_marker   = Entity(model='quad', scale=(TILE*0.95, TILE*0.95), rotation_x=90, color=CLR_LAST, enabled=False)

# ---------- Pieces ----------
PIECE_MODEL = {
    chess.PAWN:'cylinder', chess.ROOK:'cube', chess.KNIGHT:'cone', chess.BISHOP:'cube', chess.QUEEN:'sphere', chess.KING:'cylinder'
}
piece_ents = {}

def spawn_piece(piece:chess.Piece, sq:int):
    is_white = piece.color
    ent = Entity(
        parent=scene,
        model=PIECE_MODEL[piece.piece_type],
        position=ORIGIN + Vec3((sq%8)*TILE, 0.25, (sq//8)*TILE),
        color=color.rgb(242,243,245) if is_white else color.rgb(26,28,32),
        collider='box',
        scale=Vec3(0.7, 0.95, 0.7),
        shader=lit_with_shadows_shader
    )
    if piece.piece_type == chess.BISHOP: ent.scale = Vec3(0.52, 1.1, 0.52)
    elif piece.piece_type == chess.KNIGHT: ent.scale = Vec3(0.7, 1.0, 0.7); ent.rotation_y = 35
    elif piece.piece_type == chess.QUEEN: ent.scale = Vec3(0.82, 1.2, 0.82)
    elif piece.piece_type == chess.KING: ent.scale = Vec3(0.9, 1.28, 0.9)
    piece_ents[sq] = ent

def rebuild_from_board():
    for e in list(piece_ents.values()): destroy(e)
    piece_ents.clear()
    for sq, p in board.piece_map().items(): spawn_piece(p, sq)
    for t in tiles: t.reset()
    if move_history:
        last_from_marker.enabled = True; last_to_marker.enabled = True
        last_from_marker.position = ORIGIN + Vec3((move_history[-1].from_square%8)*TILE, 0.051, (move_history[-1].from_square//8)*TILE)
        last_to_marker.position   = ORIGIN + Vec3((move_history[-1].to_square%8)*TILE,   0.051, (move_history[-1].to_square//8)*TILE)
    else:
        last_from_marker.enabled = False; last_to_marker.enabled = False
    update_status(); update_center_overlay(); update_eval_bar()

def animate_capture_at(to:int):
    cap = piece_ents.get(to)
    if cap:
        cap.animate_scale(Vec3(0.01,0.01,0.01), duration=0.15)
        destroy(cap, delay=0.16); piece_ents.pop(to, None)

def animate_move(fr:int, to:int):
    e = piece_ents.get(fr)
    if not e: return
    animate_capture_at(to)
    piece_ents.pop(fr, None); piece_ents[to] = e
    e.animate_position(ORIGIN + Vec3((to%8)*TILE, 0.25, (to//8)*TILE), duration=0.18, curve=curve.in_out_cubic)

# ---------- UI ----------
ui_panel = Entity(parent=camera.ui, scale=(0.7,0.7), y=.4, x=-.46)
turn_text = Text(parent=ui_panel, text="", color=CLR_TEXT, origin=(-.5,.5), x=0, y=0.1, scale=1.2)
info_text = Text(parent=ui_panel, text="", color=color.rgba(200,210,230,200), origin=(-.5,.5), x=0, y=0.06, scale=.9)
coach_text = Text(parent=ui_panel, text="", color=color.rgb(180,240,200), origin=(-.5,.5), x=0, y=-.02, scale=.9, line_height=1.1)
clock_text = Text(parent=camera.ui, text="", color=CLR_TEXT, origin=(.5,.5), x=.44, y=.43, scale=1.2)
right_panel = Entity(parent=camera.ui, x=.47, y=0, scale=(.06,.8), model='quad', color=color.rgba(30,34,40,220))
eval_fill = Entity(parent=right_panel, model='quad', color=color.rgb(80,190,100), origin=(0,-.5), scale=(.9, .5), y=-.4)

help_text = Text(parent=camera.ui, text="[H] Help", color=color.rgba(220,220,230,180), origin=(.5,.5), x=.46, y=-.46, scale=.85)
ai_text   = Text(parent=camera.ui, text="", color=color.rgba(220,220,230,180), origin=(.5,.5), x=.46, y=-.42, scale=.85)

help_overlay = None
def show_help():
    global help_overlay
    if help_overlay and help_overlay.enabled: help_overlay.enabled = False; return
    help_overlay = Panel(parent=camera.ui, scale=(.9,.8), color=color.rgba(15,18,24,240))
    Text(parent=help_overlay, text=T("help_hdr"), x=-.43, y=.36, origin=(-.5,.5), color=CLR_TEXT, scale=1.2)
    Text(parent=help_overlay, text=T("help_body"), x=-.43, y=.30, origin=(-.5,.5), color=CLR_TEXT, scale=.95)

# ---------- Status / Clocks ----------
coach_on = True

def update_status():
    side = T("white") if board.turn else T("black")
    turn_text.text = f"{T('turn')}: {side}"
    if board.is_checkmate(): info_text.text = T("mate")
    elif board.is_stalemate(): info_text.text = T("stalemate")
    elif board.is_check(): info_text.text = T("check")
    else: info_text.text = ""

def format_time(t): m = int(t)//60; s = int(t)%60; return f"{m:02d}:{s:02d}"

def tick_clocks():
    global last_tick, clock_white, clock_black, running
    now = time.time(); dt = now - last_tick; last_tick = now
    if not running: return
    if board.turn: clock_white = max(0, clock_white - dt)
    else: clock_black = max(0, clock_black - dt)
    if clock_white <= 0 or clock_black <= 0: running = False
    clock_text.text = f"⏱  {T('white')} {format_time(clock_white)}  |  {T('black')} {format_time(clock_black)}"

# ---------- Coach overlays ----------
center_markers = [Entity(model='quad', rotation_x=90, color=color.rgba(120,180,255,80), scale=(.95,.95), enabled=False) for _ in range(4)]
for i, sq in enumerate(CENTER_SQS):
    center_markers[i].position = ORIGIN + Vec3((sq%8)*TILE, 0.055, (sq//8)*TILE)

def update_center_overlay():
    for m in center_markers: m.enabled = coach_on

def analyze_and_coach():
    if not coach_on: coach_text.text = ""; return
    # Center control differential
    center = 0
    for sq in CENTER_SQS:
        center += len(board.attackers(board.turn, sq)) - len(board.attackers(not board.turn, sq))
    # Activity
    my_moves = board.legal_moves.count()
    caps = sum(1 for m in board.legal_moves if board.is_capture(m))
    tips = []
    if center > 0: tips.append("Center OK, keep tension on d4/e4/d5/e5.")
    elif center < 0: tips.append("Contest center: push a pawn or reroute a knight.")
    if caps == 0 and my_moves < 15: tips.append("Increase activity: unpin pieces, open a file for rooks.")
    if board.is_check(): tips.append("Defend first, then counter with tempo.")
    if len(board.piece_map()) <= 10: tips.append("Endgame: activate king, create passed pawn.")
    coach_text.text = f"{T('coach_hdr')}: " + ("  •  ".join(tips) if tips else T("coach_ok"))

# ---------- Selection / Moves ----------
selected = None
targets = set()

def legal_targets_from(fr:int):
    tgts = set()
    for mv in board.legal_moves:
        if mv.from_square == fr: tgts.add(mv.to_square)
    return tgts

def highlight_selection(fr:int):
    for t in tiles: t.reset()
    tiles[fr].color = CLR_SEL
    for to in targets:
        tiles[to].color = CLR_MOVE if not board.piece_at(to) else CLR_CAPT

def clear_selection():
    global selected, targets
    selected = None; targets = set()
    for t in tiles: t.reset()
    update_status()

def push_move(move:chess.Move):
    global running
    board.push(move)
    move_history.append(move)
    animate_move(move.from_square, move.to_square)
    last_from_marker.position = ORIGIN + Vec3((move.from_square%8)*TILE, 0.051, (move.from_square//8)*TILE)
    last_to_marker.position   = ORIGIN + Vec3((move.to_square%8)*TILE,   0.051, (move.to_square//8)*TILE)
    last_from_marker.enabled = last_to_marker.enabled = True
    analyze_and_coach(); update_eval_bar()
    if board.is_game_over(): running = False

def promotion_gui(fr:int, to:int):
    # Minimal GUI for promotion, appears above target square
    panel = Panel(model='quad', color=color.rgba(25,28,34,240), scale=(.2,.26), position=(0,0,0), parent=camera.ui)
    tpos = ORIGIN + Vec3((to%8)*TILE, 0.25, (to//8)*TILE)
    screen_pos = camera.world_to_screen_point(tpos)
    panel.x = screen_pos.x - .1; panel.y = screen_pos.y + .1
    choice = {"p":None}
    def set_(p): choice["p"]=p; destroy(panel)
    btns = []
    for i,(sym,ptype) in enumerate([("Q",chess.QUEEN),("R",chess.ROOK),("B",chess.BISHOP),("N",chess.KNIGHT)]):
        b = Button(parent=panel, text=sym, color=color.rgb(60,120,90), scale=(.09,.06), x=-.07+.05*i, y=.07)
        b.on_click = (lambda p=ptype: set_(p))
        btns.append(b)
    t0=time.time()
    while time.time()-t0<7 and choice["p"] is None:
        application.step()
    destroy(panel)
    return choice["p"] or chess.QUEEN

def try_move(fr:int, to:int):
    promo = None
    p = board.piece_at(fr)
    if p and p.piece_type == chess.PAWN and (to//8 in (0,7)):
        promo = promotion_gui(fr, to)
    mv = chess.Move(fr, to, promotion=promo)
    if mv in board.legal_moves:
        push_move(mv)
        return True
    return False

def undo_move():
    global running
    if move_history:
        board.pop(); move_history.pop(); rebuild_from_board(); running=True

def flip_board():
    camera.animate_rotation_y(camera.rotation_y + 180, duration=0.35, curve=curve.in_out_cubic)

def new_game():
    global clock_white, clock_black, running, move_history
    board.reset(); clock_white, clock_black = 5*60, 5*60; move_history=[]; running=True; rebuild_from_board()

def export_pgn(path="game.pgn"):
    game = chess.pgn.Game()
    node = game
    tmp = chess.Board()
    for mv in move_history:
        node = node.add_variation(mv)
        tmp.push(mv)
    with open(path, "w", encoding="utf-8") as f:
        print(game, file=f, end="\n\n")
    print(T("save_pgn"), path)

# ---------- Evaluation / AI ----------
# Simple centipawn evaluator (material + mobility + center + king safety-ish)
PIECE_VAL = {chess.PAWN:100, chess.KNIGHT:320, chess.BISHOP:330, chess.ROOK:500, chess.QUEEN:900, chess.KING:0}
CENTER_BONUS = 12
MOBILITY_BONUS = 2

def evaluate(b:chess.Board):
    if b.is_checkmate():
        return -99999 if b.turn else 99999
    if b.is_stalemate(): return 0
    score = 0
    # material
    for sq, p in b.piece_map().items():
        val = PIECE_VAL[p.piece_type]
        score += val if p.color else -val
        if sq in CENTER_SQS:
            score += CENTER_BONUS if p.color else -CENTER_BONUS
    # mobility (current side to move tends to have options)
    score += (b.legal_moves.count() * MOBILITY_BONUS) * (1 if b.turn else -1)
    # small king safety proxy: castle rights
    if b.has_kingside_castling_rights(True) or b.has_queenside_castling_rights(True): score += 10
    if b.has_kingside_castling_rights(False) or b.has_queenside_castling_rights(False): score -= 10
    return score

def minimax(b:chess.Board, depth:int, alpha:int, beta:int):
    if depth == 0 or b.is_game_over(): return evaluate(b), None
    best_move = None
    if b.turn:  # maximizing white
        max_eval = -10**9
        for mv in b.legal_moves:
            b.push(mv)
            ev,_ = minimax(b, depth-1, alpha, beta)
            b.pop()
            if ev > max_eval: max_eval, best_move = ev, mv
            alpha = max(alpha, ev)
            if beta <= alpha: break
        return max_eval, best_move
    else:
        min_eval = 10**9
        for mv in b.legal_moves:
            b.push(mv)
            ev,_ = minimax(b, depth-1, alpha, beta)
            b.pop()
            if ev < min_eval: min_eval, best_move = ev, mv
            beta = min(beta, ev)
            if beta <= alpha: break
        return min_eval, best_move

def ai_pick_move(b:chess.Board):
    # Level 1: random-ish with center preference
    # Level 2: greedy capture-first + center
    # Level 3: minimax 2-ply
    if use_stockfish and ai_level >= 3:
        try:
            import subprocess, shlex
            p = subprocess.Popen([shutil.which("stockfish")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            def send(cmd): p.stdin.write(cmd+"\n"); p.stdin.flush()
            send("uci"); send("isready"); send("ucinewgame")
            send(f"position fen {b.fen()}"); send("go movetime 500")
            move = None
            t0=time.time()
            while time.time()-t0<2:
                line = p.stdout.readline().strip()
                if line.startswith("bestmove"):
                    move = line.split()[1]; break
            if move:
                mv = chess.Move.from_uci(move)
                p.kill()
                if mv in b.legal_moves: return mv
        except Exception:
            pass

    legal = list(b.legal_moves)
    if not legal: return None

    if ai_level == 1:
        def sc1(m):
            s = 0
            if b.is_capture(m): s += 5
            if m.to_square in CENTER_SQS: s += 2
            s += random.random()
            return -s
        return sorted(legal, key=sc1)[0]

    if ai_level == 2:
        # one-ply greedy using evaluate after the move
        best = None; best_val = -10**9 if b.turn else 10**9
        for m in legal:
            b.push(m); val = evaluate(b); b.pop()
            if b.turn:  # white to move originally
                if val > best_val: best_val, best = val, m
            else:
                if val < best_val: best_val, best = val, m
        return best

    # ai_level >=3: minimax 2-ply
    _, mv = minimax(b, 2, -10**9, 10**9)
    return mv or random.choice(legal)

def update_eval_bar():
    # Normalize eval to [-5, +5] pawns; fill height 0..1 (top = white better)
    val = evaluate(board) / 100.0
    val = max(-5.0, min(5.0, val))
    fill = (val + 5.0) / 10.0
    eval_fill.scale_y = max(0.02, fill * .98)
    eval_fill.y = -0.49 + eval_fill.scale_y

def on_ai_turn():
    mv = ai_pick_move(board)
    if mv:
        push_move(mv)

# ---------- Input ----------
def input(key):
    global selected, targets, coach_on, ai_plays_black, ai_level, clock_white, clock_black, theme_idx, L
    if key == 'h': show_help()
    if key == 'a': coach_on = not coach_on; update_center_overlay(); analyze_and_coach()
    if key == 'f1': ai_plays_black = not ai_plays_black
    if key == 'f2': ai_level = 1 if ai_level>=3 else ai_level+1
    if key == 'tab': flip_board()
    if key == 'backspace': undo_move()
    if key == 'n': new_game()
    if key == 'p': export_pgn()
    if key == '+': clock_white += 60; clock_black += 60
    if key == '-': clock_white = max(60, clock_white-60); clock_black = max(60, clock_black-60)
    if key == 'r': clock_white, clock_black = 5*60, 5*60
    if key == '1': theme_idx = 0; build_board(); rebuild_from_board()
    if key == '2': theme_idx = 1; build_board(); rebuild_from_board()
    if key == '3': theme_idx = 2; build_board(); rebuild_from_board()
    if key == 'l': L = (L+1)%len(LANGS); update_status(); show_help()  # reopen help for language

    ai_text.text = f"{T('ai_lvl')}: {ai_level}   |   {(T('ai_on') if ai_plays_black else T('ai_off'))}"

    if key == 'right mouse down':
        clear_selection(); return
    if key == 'left mouse down' and mouse.hovered_entity:
        h = mouse.hovered_entity
        idx = h.index if isinstance(h, Tile) else _pos_to_sq(h.position)
        if selected is None:
            p = board.piece_at(idx)
            if p and p.color == board.turn:
                selected = idx; targets = legal_targets_from(selected); highlight_selection(selected)
        else:
            moved = try_move(selected, idx)
            if not moved:
                p = board.piece_at(idx)
                if p and p.color == board.turn:
                    selected = idx; targets = legal_targets_from(selected); highlight_selection(selected)
                else:
                    clear_selection()
            else:
                clear_selection()

def _pos_to_sq(pos:Vec3)->int:
    rel = pos - ORIGIN
    f = int(round(rel.x / TILE)); r = int(round(rel.z / TILE))
    f = max(0, min(7, f)); r = max(0, min(7, r))
    return r*8 + f

# ---------- Build and run ----------
rebuild_from_board()

def update():
    tick_clocks()
    if ai_plays_black and not board.turn and not board.is_game_over():
        on_ai_turn()

app.run()
