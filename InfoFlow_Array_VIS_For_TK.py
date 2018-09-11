import show_state_array
from InfoFlow import *
import tkinter as tk
from tkinter import font
from tkinter import N, S, W, E
from typing import List


class StateDisplay(tk.Frame):
    def __init__(self, parent, width, height):
        super().__init__(parent)
        self.root = parent
        self.width = width
        self.height = height
        # TODO
        # What our UI looks like
        # -------------------------------------
        # |        |  1st Level   |           |
        # | player |--------------|           |
        # | stats  |     2nd      |   All     |
        # |        |    Level     | Operators |
        # |-----------------------|           |
        # |     State Describe    |           |
        # -------------------------------------
        background, foreground = "black", "darkgray"
        self.style(self.root, bg=background)
        # Player Info
        self.frame_player_info = self.style(tk.LabelFrame(self.root, text="Player Stats", borderwidth=2, relief="groove", font=self.get_font("Helvetica", 18, bold=True)),
                                            bg=background, fg=foreground)
        self.frame_player_info.grid(row=0, column=0, rowspan=2, columnspan=1, ipadx=4, ipady=4, padx=4, pady=4, sticky=N + S + W + E)
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
        self.frame_first_level = tk.Frame(self.root, background=background)
        self.frame_first_level.grid(row=0, column=1, ipadx=2, ipady=2, padx=2, pady=2, sticky=N + S + W + E)
        self.canvas_first_level = self.style(tk.Canvas(self.frame_first_level, width=600, height=100), bg=background)
        self.canvas_first_level.grid(row=0, column=0, sticky=N + S + W + E)
        self.frame_second_level = tk.Frame(self.root, background=background)
        self.frame_second_level.grid(row=1, column=1, ipadx=2, ipady=2, padx=2, pady=2, sticky=N + S + W + E)
        self.canvas_second_level = self.style(tk.Canvas(self.frame_second_level, width=600, height=300), bg=background)
        self.canvas_second_level.grid(row=0, column=0, sticky=N + S + W + E)
        # Label for describing states
        self.frame_state_describe = self.style(tk.LabelFrame(self.root, text="Current State Description", borderwidth=2, relief="groove", font=self.get_font("Helvetica", 18, bold=True)),
                                               bg=background, fg=foreground)
        self.frame_state_describe.grid(row=2, column=0, columnspan=2, padx=4, pady=4, ipadx=4, ipady=4, sticky=N + S + W + E)
        self.label_state_describe = self.style(tk.Label(self.frame_state_describe, font=self.get_font("Consolas", 12)), bg=background, fg=foreground)
        self.label_state_describe.grid(row=0, column=0, sticky=N + S + W + E)
        # List of all operators
        # set grid auto expand
        self.grid_auto_expand(parent, 3, 2, row_weights=[0, 1, 0], col_weights=[0, 1])
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
    def style(w, bg=None, fg=None, hc=None, ht=None, **options):
        w.configure(**options)
        if bg and fg:
            w.configure(background=bg, foreground=fg)
        elif bg:
            w.configure(background=bg)
        elif fg:
            w.configure(foreground=fg)
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
    show_state_array.STATE_WINDOW = display
    print("VIS initialization finished")


class StateRenderer:
    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        display.label_state_describe.configure(text=state.describe_state())
        if state.player:
            display.canvas_energy.coords(display.rect_energy, 0, 0, state.player.energy, 20)
            # display.canvas_energy.itemconfigure(display.text_energy, text=f"{state.player.energy:3}", fill="white" if state.player.energy < 30 else "black")
            display.text_score.configure(text=f"{state.player.score}")
            display.text_finished.configure(text=f"{state.player.finished}")
            display.text_money.configure(text=f"${state.player.money}/${state.player.debt}")
            display.text_difficulty_level.configure(text=f"{state.player.difficulty_level}")
            display.text_accepted.configure(text=f"{'✔' if state.player.has_accepted_challenge() else '×'}")

    @staticmethod
    def get_renderer(state_type) -> 'StateRenderer':
        if state_type in StateRenderer.all:
            return StateRenderer.all[state_type]
        else:
            raise TypeError(state_type)


class SecondLevelStateRenderer(StateRenderer):
    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        if last_state is not None:
            StateRenderer.get_renderer(type(last_state)).render(display, last_state, None)
        super().render(display, state, last_state)


class GameStartStateRenderer(StateRenderer):
    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)
        # TODO
        pass


class ChallengeMenuStateRenderer(StateRenderer):
    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)
        # TODO
        pass


class MessageDisplayStateRenderer(SecondLevelStateRenderer):
    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)
        # TODO
        pass


class NewsSortingChallengeStateRenderer(SecondLevelStateRenderer):
    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        super().render(display, state, last_state)
        # TODO
        pass


StateRenderer.all = {
    # TODO
    GameStartState: GameStartStateRenderer(),
    ChallengeMenuState: ChallengeMenuStateRenderer(),
    MessageDisplayState: MessageDisplayStateRenderer(),
    NewsSortingChallengeState: NewsSortingChallengeStateRenderer()
}


def initialize_vis():
    initialize_tk(width=1200, height=800, title="InfoFlow")


StateRenderer.last_state: 'State' = None


def render_state(state: 'State'):
    # print("In render_state, state is " + str(state))  # DEBUG ONLY
    StateRenderer.get_renderer(type(state)).render(show_state_array.STATE_WINDOW, state, StateRenderer.last_state)
    StateRenderer.last_state = state
