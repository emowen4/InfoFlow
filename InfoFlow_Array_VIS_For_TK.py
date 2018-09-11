import show_state_array
from InfoFlow import *
import tkinter as tk
from tkinter import font
from tkinter import N, S, W, E
from typing import List
import random
import time
from threading import Thread


class StateDisplay(tk.Frame):
    background = "black"
    foreground = "darkgray"
    textcolor = "white"
    highlightcolor = "white"
    default_font_name = "Helvetica"

    def __init__(self, parent, width, height):
        super().__init__(parent)
        self.root = parent
        self.width = width
        self.height = height
        # What our UI looks like
        # -------------------------------------
        # |        |     Round    |           |
        # |        |--------------|           |
        # |        |              |           |
        # | player |     Game     |    All    |
        # | stats  |     View     | Operators |
        # |        |              |           |
        # |-----------------------------------|
        # |           State Describe          |
        # -------------------------------------
        self.style(self.root, bg=StateDisplay.background)
        # Player Info
        self.frame_player_info = tk.LabelFrame(self.root, text=" Player Stats ", borderwidth=2, relief="groove", font=self.get_font("Chiller", 18, bold=True),
                                               bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.frame_player_info.grid(row=0, column=0, rowspan=2, columnspan=1, ipadx=4, ipady=4, padx=4, pady=4, sticky=N + S + W + E)
        self.label_energy = tk.Label(self.frame_player_info, text="Energy: ", font=self.get_font(StateDisplay.default_font_name, 12, bold=True),
                                     bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.label_energy.grid(row=0, column=0, sticky=W)
        self.canvas_energy = self.style(tk.Canvas(self.frame_player_info, width=100, height=20, bg=StateDisplay.background),
                                        hc=StateDisplay.highlightcolor, ht=1)
        self.canvas_energy.grid(row=0, column=1, sticky=W)
        color_energy = self.rgb2hex(46, 204, 113)
        self.rect_energy = self.canvas_energy.create_rectangle(0, 0, 100, 20, fill=color_energy, outline=color_energy)
        # self.text_energy = self.canvas_energy.create_text(25, 10, text="100", font=self.get_font("Helvetica", 12, bold=True))
        self.label_score = tk.Label(self.frame_player_info, text="Score: ", bg=StateDisplay.background, fg=StateDisplay.foreground, font=self.get_font(StateDisplay.default_font_name, 12, bold=True))
        self.label_score.grid(row=1, column=0, sticky=W)
        self.text_score = tk.Label(self.frame_player_info, font=self.get_font(StateDisplay.default_font_name, 12), bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.text_score.grid(row=1, column=1, sticky=W)
        self.label_finished = tk.Label(self.frame_player_info, text="Finished Challenges: ", font=self.get_font(StateDisplay.default_font_name, 12, bold=True),
                                       bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.label_finished.grid(row=2, column=0, sticky=W)
        self.text_finished = tk.Label(self.frame_player_info, font=self.get_font(StateDisplay.default_font_name, 12), bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.text_finished.grid(row=2, column=1, sticky=W)
        self.label_money = tk.Label(self.frame_player_info, text="Money/Debt: ", font=self.get_font(StateDisplay.default_font_name, 12, bold=True),
                                    bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.label_money.grid(row=3, column=0, sticky=W)
        self.text_money = tk.Label(self.frame_player_info, font=self.get_font(StateDisplay.default_font_name, 12), bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.text_money.grid(row=3, column=1, sticky=W)
        self.label_difficulty_level = tk.Label(self.frame_player_info, text="Difficulty Level: ", font=self.get_font(StateDisplay.default_font_name, 12, bold=True),
                                               bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.label_difficulty_level.grid(row=4, column=0, sticky=W)
        self.text_difficulty_level = tk.Label(self.frame_player_info, font=self.get_font(StateDisplay.default_font_name, 12), bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.text_difficulty_level.grid(row=4, column=1, sticky=W)
        self.label_accepted = tk.Label(self.frame_player_info, text="Has accepted challenge: ", font=self.get_font(StateDisplay.default_font_name, 12, bold=True),
                                       bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.label_accepted.grid(row=5, column=0, sticky=W)
        self.text_accepted = tk.Label(self.frame_player_info, font=self.get_font(StateDisplay.default_font_name, 12), bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.text_accepted.grid(row=5, column=1, sticky=W)
        # Game Frame
        self.label_round = tk.Label(self.root, text="\nRound Beginning", bg=StateDisplay.background, fg=StateDisplay.foreground, font=self.get_font("Algerian", 12))
        self.label_round.grid(row=0, column=1, padx=4, pady=4, sticky=N + S + W + E)
        self.frame_game = tk.LabelFrame(self.root, text=" Game View ", bg=StateDisplay.background, fg=StateDisplay.foreground, font=self.get_font("Chiller", 18, bold=True))
        self.frame_game.grid(row=1, column=1, ipadx=2, ipady=2, padx=8, pady=12)
        self.canvas_game = self.style(tk.Canvas(self.frame_game, width=600, height=400, bg=StateDisplay.background),
                                      hc="black", ht=0)
        self.canvas_game.grid(row=0, column=0)
        # Operators
        self.frame_operators = self.style(tk.LabelFrame(self.root, text=" Operators ", borderwidth=2, relief="groove", font=self.get_font("Chiller", 18, bold=True)),
                                          bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.frame_operators.grid(row=0, column=2, rowspan=2, columnspan=1, ipadx=4, ipady=4, padx=4, pady=4, sticky=N + S + W + E)
        self.list_operators = self.style(tk.Listbox(self.frame_operators, width=30, font=self.get_font(StateDisplay.default_font_name, 14), bg=StateDisplay.background, fg=StateDisplay.foreground),
                                         hc="black", ht=0, borderwidth=0, selectmode=tk.SINGLE, selectbackground="white", selectforeground="black")
        self.list_operators.grid(row=0, column=0, padx=4, pady=4)
        # Label for describing states
        self.frame_state_describe = tk.LabelFrame(self.root, text=" Current State Description ", borderwidth=2, relief="groove", font=self.get_font("Chiller", 18, bold=True),
                                                  bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.frame_state_describe.grid(row=2, column=0, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4, sticky=N + S + W + E)
        self.label_state_describe = tk.Label(self.frame_state_describe, font=self.get_font("Consolas", 12), bg=StateDisplay.background, fg=StateDisplay.foreground)
        self.label_state_describe.grid(row=0, column=0, sticky=N + S + W + E)
        # set grid auto expand
        self.grid_auto_expand(parent, 2, 2, row_weights=[0, 0, 1], col_weights=[0, 1, 0])
        self.grid_auto_expand(self.frame_player_info, 6, 2, row_weights=[0 for _ in range(6)], col_weights=[0, 0])

    loaded_fonts = {}

    @staticmethod
    def get_font(name: str, size: int, bold: bool = False, italic: bool = False, underline: bool = False, overstrike: bool = False, nocache=False) -> "font.Font":
        key = (name, size, bold, italic, underline, overstrike)
        if key in StateDisplay.loaded_fonts:
            return StateDisplay.loaded_fonts[key]
        f = font.Font(family=name, size=size, weight="bold" if bold else "normal", slant="italic" if italic else "roman", underline=str(underline).lower(), overstrike=str(overstrike).lower())
        if not nocache:
            StateDisplay.loaded_fonts[key] = f
        return f

    @staticmethod
    def rgb2hex(r, g, b):
        return "#%02x%02x%02x" % (r, g, b)

    @staticmethod
    def style(w, hc=None, ht=None, **options):
        w.configure(**options)
        if hc and ht:
            w.configure(highlightcolor=hc, highlightbackground=hc, highlightthickness=ht)
        elif hc:
            w.configure(highlightcolor=hc, highlightbackground=hc)
        elif ht:
            w.configure(highlightthickness=ht)
        return w

    @staticmethod
    def set_text(w: 'tk.Text', text: str):
        w.configure(state=tk.NORMAL)
        w.delete(1.0, tk.END)
        w.insert(tk.END, text)
        w.configure(state=tk.DISABLED)

    @staticmethod
    def grid_auto_expand(frame: 'tk.Frame', row: int, col: int, row_weights: 'List[int]' = None, col_weights: 'List[int]' = None) -> None:
        for i in range(row):
            tk.Grid.rowconfigure(frame, i, weight=row_weights[i] if row_weights else 1)
        for i in range(col):
            tk.Grid.columnconfigure(frame, i, weight=col_weights[i] if col_weights else 1)


def initialize_tk(width, height, title):
    root = tk.Tk()
    root.title(title)
    display = StateDisplay(root, width=width, height=height)
    root.minsize(1100, 590)
    show_state_array.STATE_WINDOW = display
    print("VIS initialization finished")


class StateRenderer:
    def init(self, display: 'StateDisplay'):
        pass

    def is_static_renderer(self):
        return True

    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        display.label_state_describe.configure(text=state.describe_state())
        # Draw player stats
        if state.player:
            display.canvas_energy.coords(display.rect_energy, 0, 0, state.player.energy, 20)
            # display.canvas_energy.itemconfigure(display.text_energy, text=f"{state.player.energy:3}", fill="white" if state.player.energy < 30 else "black")
            display.text_score.configure(text=f"{state.player.score}")
            display.text_finished.configure(text=f"{state.player.finished}")
            display.text_money.configure(text=f"${state.player.money}/${state.player.debt}")
            display.text_difficulty_level.configure(text=f"{state.player.difficulty_level}")
            display.text_accepted.configure(text=f"{'✔' if state.player.has_accepted_challenge() else '×'}")
        # Update round information
        display.label_round.configure(text=f"\nRound {state.round}")
        # Draw available operators
        global OPERATORS
        display.list_operators.delete(0, tk.END)
        if OPERATORS:
            ops = [(ind, op) for ind, op in enumerate(OPERATORS) if state.is_applicable_operator(op)]
            for ind, op in ops:
                display.list_operators.insert(tk.END, f"{ind:2}: {op.name}")

    def dynamic_render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        pass

    def is_static_post_renderer(self):
        return True

    def post_render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        pass

    def post_dynamic_render(self, display: 'StateDisplay', state: 'State', last_state: 'State') -> bool:
        # Return True if has more dynamic render; otherwise, return False
        return False

    @staticmethod
    def get_renderer(state_type) -> 'StateRenderer':
        if state_type in StateRenderer.all:
            return StateRenderer.all[state_type]()
        else:
            raise TypeError(state_type)


class GameStartStateRenderer(StateRenderer):
    class Rain:
        def __init__(self, content: List[str], x: int, y: int, speed: float, size: int, color: str):
            # self.text = "\n".join(content)
            self.text = "".join(content)
            self.x = x
            self.y = y
            self.speed = speed
            self.size = size
            self.color = color

        def is_disappeared(self):
            if self.speed > 0:
                return self.x > 650
            else:
                return self.x < -300

        @staticmethod
        def random() -> 'GameStartStateRenderer.Rain':
            x, speed = (random.randint(-800, -500), random.random() * 32 + 2) if random.randint(0, 1) is 0 else (600 + random.randint(500, 800), -(random.random() * 32 + 2))
            return GameStartStateRenderer.Rain(content=random.choices(population=["0", "1", "0", "1", "0", "1", "0", "1"], k=random.randint(6, 18)),
                                               # x=random.randint(-10, 590), y=random.randint(-500, -300), speed=random.random() * 32 + 2,
                                               x=x, y=random.randint(-10, 390), speed=speed,
                                               size=random.randint(4, 24), color=StateDisplay.textcolor)

    def init(self, display):
        self.rect_outer = display.canvas_game.create_rectangle(200, 150, 400, 250, width=4, fill=StateDisplay.textcolor)
        self.rect_inner = display.canvas_game.create_rectangle(204, 154, 396, 246, width=2, fill=StateDisplay.textcolor)
        self.font_title = StateDisplay.get_font("Gill Sans MT", 28, True, nocache=True)
        self.text_title = display.canvas_game.create_text(300, 200, text="Info Flow", fill="black", font=self.font_title)
        self.rains = [GameStartStateRenderer.Rain.random() for _ in range(40)]
        self.text_rains = []
        for r in self.rains:
            self.text_rains.append(display.canvas_game.create_text(r.x, r.y, anchor=tk.NW, font=StateDisplay.get_font("Consolas", r.size), text=r.text, fill=r.color))

    def is_static_renderer(self):
        return False

    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)

    def dynamic_render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        rains, text_rains = self.rains[:], self.text_rains[:]
        for i in range(len(rains)):
            r, t = rains[i], text_rains[i]
            r.x += r.speed
            if display:
                display.canvas_game.move(t, r.speed, 0)
            if r.is_disappeared() and r in rains:
                if display:
                    display.canvas_game.delete(t)
                rains.remove(r)
                text_rains.remove(t)
                nr = GameStartStateRenderer.Rain.random()
                rains.append(nr)
                text_rains.append(display.canvas_game.create_text(nr.x, nr.y, anchor=tk.NW, font=StateDisplay.get_font("Consolas", nr.size), text=nr.text, fill=nr.color))
        self.rains, self.text_rains = rains, text_rains

    def is_static_post_renderer(self):
        return False

    def post_render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        self.offset_outer = [0, 0, 0, 0]
        self.offset_inner = [0, 0, 0, 0]
        self.offset_size_title = 0

    def post_dynamic_render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        self.offset_outer = [i + 18 for i in self.offset_outer]
        self.offset_inner = [i + 18 for i in self.offset_inner]
        self.offset_size_title += 5
        self.font_title.configure(size=28 + self.offset_size_title)
        display.canvas_game.coords(self.rect_outer, 200 - self.offset_outer[0], 150 - self.offset_outer[1], 400 + self.offset_outer[2], 250 + self.offset_outer[3])
        display.canvas_game.coords(self.rect_inner, 204 - self.offset_outer[0], 154 - self.offset_outer[1], 396 + self.offset_outer[2], 246 + self.offset_outer[3])
        display.canvas_game.itemconfigure(self.text_title, font=self.font_title)
        return False if self.offset_size_title >= 60 else True


class ChallengeMenuStateRenderer(StateRenderer):
    def init(self, display):
        self.c_menus = [[i * 100 + 50, 100 + 50 * i, random.randint(0, 50), random.randint(0, 10), .5, .5] for i in range(4)]
        self.font = StateDisplay.get_font(StateDisplay.default_font_name, 16, italic=True)
        self.label_accept = display.canvas_game.create_text(self.c_menus[0][0], self.c_menus[0][1], anchor=W,
                                                            text=OperatorIds.CHALLENGE_ACCEPT.name, fill=StateDisplay.textcolor, font=self.font)
        self.label_decine = display.canvas_game.create_text(self.c_menus[1][0], self.c_menus[1][1], anchor=W,
                                                            text=OperatorIds.CHALLENGE_DECINE.name, fill=StateDisplay.textcolor, font=self.font)
        self.label_pay = display.canvas_game.create_text(self.c_menus[2][0], self.c_menus[2][1], anchor=W,
                                                         text=OperatorIds.PAY_DEBT.name, fill=StateDisplay.textcolor, font=self.font)
        self.label_finish_round = display.canvas_game.create_text(self.c_menus[3][0], self.c_menus[3][1], anchor=W,
                                                                  text=OperatorIds.FINISH_ROUND.name, fill=StateDisplay.textcolor, font=self.font)

    def is_static_renderer(self):
        return False

    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)

    def dynamic_render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        for t in self.c_menus:
            x, y, off_x, off_y, s_x, s_y = t
            t[0], t[1], t[2], t[3] = x + s_x, y + s_y, off_x + s_x, off_y + s_y
            if t[2] <= 0 or t[2] >= 50:
                t[4] = -t[4]
            if t[3] <= 0 or t[3] >= 10:
                t[5] = -t[5]
        display.canvas_game.coords(self.label_accept, self.c_menus[0][0], self.c_menus[0][1])
        display.canvas_game.coords(self.label_decine, self.c_menus[1][0], self.c_menus[1][1])
        display.canvas_game.coords(self.label_pay, self.c_menus[2][0], self.c_menus[2][1])
        display.canvas_game.coords(self.label_finish_round, self.c_menus[3][0], self.c_menus[3][1])

    def is_static_post_renderer(self):
        return False

    def post_render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        if last_state.selected_operator.id is OperatorIds.CHALLENGE_ACCEPT:
            self.pos_select = self.c_menus[0]
            self.text_select = self.label_accept
        elif last_state.selected_operator.id is OperatorIds.CHALLENGE_DECINE:
            self.pos_select = self.c_menus[1]
            self.text_select = self.label_decine
        elif last_state.selected_operator.id is OperatorIds.PAY_DEBT:
            self.pos_select = self.c_menus[2]
            self.text_select = self.label_pay
        elif last_state.selected_operator.id is OperatorIds.FINISH_ROUND:
            self.pos_select = self.c_menus[3]
            self.text_select = self.label_finish_round
        self.size_select = 16
        self.font_select = StateDisplay.get_font(StateDisplay.default_font_name, self.size_select, bold=True, italic=True, nocache=True)

    def post_dynamic_render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        if self.size_select < 22:
            display.canvas_game.itemconfigure(self.text_select, font=self.font_select)
            self.font_select.configure(size=self.size_select + 2)
            self.size_select += 2
            return True
        elif self.pos_select[0] < 650:
            display.canvas_game.coords(self.text_select, self.pos_select[0], self.pos_select[1])
            self.pos_select[0] += 30
            return True
        else:
            return False


class MessageDisplayStateRenderer(StateRenderer):
    def init(self, display):
        pass

    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)
        display.canvas_game.create_oval(50, 50, 100, 100, fill=StateDisplay.textcolor)
        display.canvas_game.create_oval(54, 54, 96, 96, fill="black")
        display.canvas_game.create_text(75, 75, text="i", fill=StateDisplay.textcolor, font=StateDisplay.get_font("Impact", 28, bold=True))
        display.canvas_game.create_text(120, 75, text=state.title, fill=StateDisplay.textcolor, font=StateDisplay.get_font(StateDisplay.default_font_name, 24, bold=True), anchor=tk.W, width=400)
        display.canvas_game.create_text(50, 120, text=state.info, fill=StateDisplay.textcolor, font=StateDisplay.get_font(StateDisplay.default_font_name, 14), anchor=tk.W, width=500)


class NewsSortingChallengeStateRenderer(StateRenderer):
    def init(self, display):
        pass

    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)
        display.canvas_game.create_text(300, 200, text=f"News: {state.player.current_challenge.to_sort[state.news_index]}", fill=StateDisplay.foreground,
                                        font=StateDisplay.get_font(StateDisplay.default_font_name, 20), width=550)


class MythBusterChallengeStateRenderer(StateRenderer):
    def init(self, display):
        pass

    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)
        display.canvas_game.create_text(300, 200, text=f"News: {state.player.current_challenge.myths[state.news_index]}", fill=StateDisplay.foreground,
                                        font=StateDisplay.get_font(StateDisplay.default_font_name, 20), width=550)


StateRenderer.all = {
    # TODO
    GameStartState: lambda: GameStartStateRenderer(),
    ChallengeMenuState: lambda: ChallengeMenuStateRenderer(),
    MessageDisplayState: lambda: MessageDisplayStateRenderer(),
    NewsSortingChallengeState: lambda: NewsSortingChallengeStateRenderer(),
    MythBusterChallengeState: lambda: MythBusterChallengeStateRenderer()
}


def initialize_vis():
    initialize_tk(width=1200, height=800, title="InfoFlow")


StateRenderer.last_state: 'State' = None
keep_render: bool = False
renderer: 'StateRenderer' = None
in_render_state = False


def render_state(state: 'State'):
    # print("In render_state, state is " + str(state))  # DEBUG ONLY
    global in_render_state
    while in_render_state:
        time.sleep(0.1)
    in_render_state = True
    global keep_render, renderer
    keep_render = False
    if StateRenderer.last_state and renderer:
        if show_state_array.STATE_WINDOW:
            renderer.post_render(show_state_array.STATE_WINDOW, state, StateRenderer.last_state)
            if not renderer.is_static_post_renderer():
                keep_post_render = True
                while show_state_array.STATE_WINDOW and keep_post_render:
                    keep_post_render = renderer.post_dynamic_render(show_state_array.STATE_WINDOW, state, StateRenderer.last_state)
                    show_state_array.STATE_WINDOW.root.update()
                    time.sleep(.05)

    show_state_array.STATE_WINDOW.canvas_game.delete(tk.ALL)

    def render():
        global in_render_state, renderer
        renderer = StateRenderer.get_renderer(type(state))
        renderer.init(show_state_array.STATE_WINDOW)
        in_render_state = False
        if show_state_array.STATE_WINDOW:
            renderer.render(show_state_array.STATE_WINDOW, state, StateRenderer.last_state)
            if not renderer.is_static_renderer():
                while show_state_array.STATE_WINDOW and keep_render:
                    renderer.dynamic_render(show_state_array.STATE_WINDOW, state, StateRenderer.last_state)
                    time.sleep(.05)

    keep_render = True
    t = Thread(target=lambda: render())
    t.setDaemon(True)
    t.start()
    # StateRenderer.get_renderer(type(state)).render(show_state_array.STATE_WINDOW, state, StateRenderer.last_state)
    StateRenderer.last_state = state
