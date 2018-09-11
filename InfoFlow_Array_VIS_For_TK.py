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
    def __init__(self, parent, width, height):
        super().__init__(parent)
        self.root = parent
        self.width = width
        self.height = height
        # TODO
        # What our UI looks like
        # -------------------------------------
        # |        |              |           |
        # | player |     Game     |    All    |
        # | stats  |     View     | Operators |
        # |        |              |           |
        # |-----------------------------------|
        # |           State Describe          |
        # -------------------------------------
        background, foreground = "black", "darkgray"
        self.style(self.root, bg=background)
        # Player Info
        self.frame_player_info = self.style(tk.LabelFrame(self.root, text=" Player Stats ", borderwidth=2, relief="groove", font=self.get_font("Chiller", 18, bold=True)),
                                            bg=background, fg=foreground)
        self.frame_player_info.grid(row=0, column=0, rowspan=1, columnspan=1, ipadx=4, ipady=4, padx=4, pady=4, sticky=N + S + W + E)
        self.label_energy = self.style(tk.Label(self.frame_player_info, text="Energy: ", font=self.get_font("Helvetica", 12, bold=True)),
                                       bg=background, fg=foreground)
        self.label_energy.grid(row=0, column=0, sticky=W)
        self.canvas_energy = self.style(tk.Canvas(self.frame_player_info, width=100, height=20),
                                        bg=background, hc="white", ht=1)
        self.canvas_energy.grid(row=0, column=1, sticky=W)
        color_energy = self.rgb2hex(46, 204, 113)
        self.rect_energy = self.canvas_energy.create_rectangle(0, 0, 100, 20, fill=color_energy, outline=color_energy)
        # self.text_energy = self.canvas_energy.create_text(25, 10, text="100", font=self.get_font("Helvetica", 12, bold=True))
        self.label_score = self.style(tk.Label(self.frame_player_info, text="Score: "),
                                      bg=background, fg=foreground, font=self.get_font("Helvetica", 12, bold=True))
        self.label_score.grid(row=1, column=0, sticky=W)
        self.text_score = self.style(tk.Label(self.frame_player_info, font=self.get_font("Helvetica", 12)),
                                     bg=background, fg=foreground)
        self.text_score.grid(row=1, column=1, sticky=W)
        self.label_finished = self.style(tk.Label(self.frame_player_info, text="Finished Challenges: ", font=self.get_font("Helvetica", 12, bold=True)),
                                         bg=background, fg=foreground)
        self.label_finished.grid(row=2, column=0, sticky=W)
        self.text_finished = self.style(tk.Label(self.frame_player_info, font=self.get_font("Helvetica", 12)),
                                        bg=background, fg=foreground)
        self.text_finished.grid(row=2, column=1, sticky=W)
        self.label_money = self.style(tk.Label(self.frame_player_info, text="Money/Debt: ", font=self.get_font("Helvetica", 12, bold=True)),
                                      bg=background, fg=foreground)
        self.label_money.grid(row=3, column=0, sticky=W)
        self.text_money = self.style(tk.Label(self.frame_player_info, font=self.get_font("Helvetica", 12)),
                                     bg=background, fg=foreground)
        self.text_money.grid(row=3, column=1, sticky=W)
        self.label_difficulty_level = self.style(tk.Label(self.frame_player_info, text="Difficulty Level: ", font=self.get_font("Helvetica", 12, bold=True)),
                                                 bg=background, fg=foreground)
        self.label_difficulty_level.grid(row=4, column=0, sticky=W)
        self.text_difficulty_level = self.style(tk.Label(self.frame_player_info, font=self.get_font("Helvetica", 12)),
                                                bg=background, fg=foreground)
        self.text_difficulty_level.grid(row=4, column=1, sticky=W)
        self.label_accepted = self.style(tk.Label(self.frame_player_info, text="Has accepted challenge: ", font=self.get_font("Helvetica", 12, bold=True)),
                                         bg=background, fg=foreground)
        self.label_accepted.grid(row=5, column=0, sticky=W)
        self.text_accepted = self.style(tk.Label(self.frame_player_info, font=self.get_font("Helvetica", 12)),
                                        bg=background, fg=foreground)
        self.text_accepted.grid(row=5, column=1, sticky=W)
        # Game Frame
        self.frame_game = tk.LabelFrame(self.root, text=" Game View ", bg=background, fg=foreground, font=self.get_font("Chiller", 18, bold=True))
        self.frame_game.grid(row=0, column=1, ipadx=2, ipady=2, padx=8, pady=12)
        self.canvas_game = self.style(tk.Canvas(self.frame_game, width=600, height=400), bg=background, hc="black", ht=0)
        self.canvas_game.grid(row=0, column=0)
        # Operators
        self.frame_operators = self.style(tk.LabelFrame(self.root, text=" Operators ", borderwidth=2, relief="groove", font=self.get_font("Chiller", 18, bold=True)),
                                          bg=background, fg=foreground)
        self.frame_operators.grid(row=0, column=2, rowspan=1, columnspan=1, ipadx=4, ipady=4, padx=4, pady=4, sticky=N + S + W + E)
        self.list_operators = self.style(tk.Listbox(self.frame_operators, width=20, font=self.get_font("Helvetica", 12)),
                                         bg=background, fg=foreground, hc="black", ht=0, borderwidth=0,
                                         selectmode=tk.SINGLE, selectbackground="white", selectforeground="black")
        self.list_operators.grid(row=0, column=0, padx=4, pady=4)
        # Label for describing states
        self.frame_state_describe = self.style(tk.LabelFrame(self.root, text=" Current State Description ", borderwidth=2, relief="groove", font=self.get_font("Chiller", 18, bold=True)),
                                               bg=background, fg=foreground)
        self.frame_state_describe.grid(row=1, column=0, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4, sticky=N + S + W + E)
        self.label_state_describe = self.style(tk.Label(self.frame_state_describe, font=self.get_font("Consolas", 12)), bg=background, fg=foreground)
        self.label_state_describe.grid(row=0, column=0, sticky=N + S + W + E)
        # set grid auto expand
        self.grid_auto_expand(parent, 2, 2, row_weights=[1, 3], col_weights=[0, 1, 0])
        self.grid_auto_expand(self.frame_player_info, 6, 2, row_weights=[0 for _ in range(6)], col_weights=[0, 0])

    loaded_fonts = {}

    @staticmethod
    def get_font(name: str, size: int, bold: bool = False, italic: bool = False, underline: bool = False, overstrike: bool = False) -> "font.Font":
        key = (name, size, bold, italic, underline, overstrike)
        if key in StateDisplay.loaded_fonts:
            return StateDisplay.loaded_fonts[key]
        f = font.Font(family=name, size=size, weight="bold" if bold else "normal", slant="italic" if italic else "roman", underline=str(underline).lower(), overstrike=str(overstrike).lower())
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
    # display.pack(fill="both", expand=True)
    root.wm_minsize(1100, 760)
    show_state_array.STATE_WINDOW = display
    print("VIS initialization finished")


class StateRenderer:
    def init(self, display: 'StateDisplay'):
        pass

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
        # Draw available operators
        global OPERATORS
        display.list_operators.delete(0, tk.END)
        if OPERATORS:
            ops = [(ind, op) for ind, op in enumerate(OPERATORS) if state.is_applicable_operator(op)]
            for ind, op in ops:
                display.list_operators.insert(tk.END, f"{ind:2}: {op.name}")

    def is_static(self):
        return True

    def dynamic_render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        pass

    @staticmethod
    def get_renderer(state_type, display) -> 'StateRenderer':
        if state_type in StateRenderer.all:
            return StateRenderer.all[state_type](display)
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
                                               size=random.randint(4, 24), color="white")

    def init(self, display):
        self.rect_outer = display.canvas_game.create_rectangle(200, 150, 400, 250, width=4, fill="white")
        self.rect_inner = display.canvas_game.create_rectangle(204, 154, 396, 246, width=2, fill="white")
        self.text_title = display.canvas_game.create_text(300, 200, text="Info Flow", fill="black", font=StateDisplay.get_font("Gill Sans MT", 28, True))
        self.rains = [GameStartStateRenderer.Rain.random() for _ in range(40)]
        self.text_rains = []
        for r in self.rains:
            self.text_rains.append(display.canvas_game.create_text(r.x, r.y, anchor=tk.NW, font=StateDisplay.get_font("Consolas", r.size), text=r.text, fill=r.color))

    def is_static(self):
        return False

    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)

    def dynamic_render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        for i in range(len(self.rains[:])):
            r, t = self.rains[i], self.text_rains[i]
            r.x += r.speed
            if display:
                display.canvas_game.move(t, r.speed, 0)
            if r.is_disappeared():
                if display:
                    display.canvas_game.delete(t)
                self.rains.remove(r)
                self.text_rains.remove(t)
                nr = GameStartStateRenderer.Rain.random()
                self.rains.append(nr)
                self.text_rains.append(display.canvas_game.create_text(nr.x, nr.y, anchor=tk.NW, font=StateDisplay.get_font("Consolas", nr.size), text=nr.text, fill=nr.color))
        display.root.update()


class ChallengeMenuStateRenderer(StateRenderer):
    def init(self, display):
        pass

    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)
        # TODO
        pass


class MessageDisplayStateRenderer(StateRenderer):
    def init(self, display):
        pass

    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)
        # TODO
        pass


class NewsSortingChallengeStateRenderer(StateRenderer):
    def init(self, display):
        pass

    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)
        # TODO
        pass


StateRenderer.all = {
    # TODO
    GameStartState: lambda display: GameStartStateRenderer(),
    ChallengeMenuState: lambda display: ChallengeMenuStateRenderer(),
    MessageDisplayState: lambda display: MessageDisplayStateRenderer(),
    NewsSortingChallengeState: lambda display: NewsSortingChallengeStateRenderer()
}


def initialize_vis():
    initialize_tk(width=1200, height=800, title="InfoFlow")


StateRenderer.last_state: 'State' = None
keep_render = True


def render_state(state: 'State'):
    # print("In render_state, state is " + str(state))  # DEBUG ONLY
    global keep_render
    keep_render = False
    time.sleep(0.5)
    keep_render = True

    def render():
        renderer = StateRenderer.get_renderer(type(state), show_state_array.STATE_WINDOW)
        renderer.init(show_state_array.STATE_WINDOW)
        if show_state_array.STATE_WINDOW:
            renderer.render(show_state_array.STATE_WINDOW, state, StateRenderer.last_state)
        if not renderer.is_static():
            while show_state_array.STATE_WINDOW and keep_render:
                renderer.dynamic_render(show_state_array.STATE_WINDOW, state, StateRenderer.last_state)
                time.sleep(.05)

    show_state_array.STATE_WINDOW.canvas_game.delete("all")
    Thread(target=lambda: render()).start()
    # StateRenderer.get_renderer(type(state)).render(show_state_array.STATE_WINDOW, state, StateRenderer.last_state)
    StateRenderer.last_state = state
