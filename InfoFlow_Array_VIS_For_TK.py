import show_state_array
from InfoFlow import *
import tkinter as tk
import tkinter.ttk as ttk
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
        self.style(self.root, bg="black")
        # Player Info
        self.frame_player_info = self.style(tk.LabelFrame(parent, text="Player Stats", borderwidth=2, relief="groove"),
                                            bg="black", fg="white")
        self.frame_player_info.grid(row=0, column=0, rowspan=2, columnspan=1, ipadx=4, ipady=4, padx=4, pady=4, sticky=N + S + W + E)
        self.label_energy = self.style(tk.Label(self.frame_player_info, text="Energy: "),
                                       bg="black", fg="white")
        self.label_energy.grid(row=0, column=0, sticky=E)
        self.canvas_energy = self.style(tk.Canvas(self.frame_player_info, width=100, height=20),
                                        bg="black", hc="white", ht=1)
        self.canvas_energy.grid(row=0, column=1, sticky=W)
        color_energy = self.rgb2hex(46, 204, 113)
        self.rect_energy = self.canvas_energy.create_rectangle(0, 0, 100, 20, fill=color_energy, outline=color_energy)
        self.label_score = self.style(tk.Label(self.frame_player_info, text="Score: "),
                                      bg="black", fg="white")
        self.label_score.grid(row=1, column=0, sticky=E)
        self.text_score = self.style(tk.Label(self.frame_player_info),
                                     bg="black", fg="white")
        self.text_score.grid(row=1, column=1, sticky=W)
        self.label_finished = self.style(tk.Label(self.frame_player_info, text="Finished Challenges: "),
                                         bg="black", fg="white")
        self.label_finished.grid(row=2, column=0, sticky=E)
        self.text_finished = self.style(tk.Label(self.frame_player_info),
                                        bg="black", fg="white")
        self.text_finished.grid(row=2, column=1, sticky=W)
        self.label_money = self.style(tk.Label(self.frame_player_info, text="Money/Debt: "),
                                      bg="black", fg="white")
        self.label_money.grid(row=3, column=0, sticky=E)
        self.text_money = self.style(tk.Label(self.frame_player_info),
                                     bg="black", fg="white")
        self.text_money.grid(row=3, column=1, sticky=W)
        self.label_level = self.style(tk.Label(self.frame_player_info, text="Difficulty Level: "),
                                      bg="black", fg="white")
        self.label_level.grid(row=4, column=0, sticky=E)
        self.text_level = self.style(tk.Label(self.frame_player_info),
                                     bg="black", fg="white")
        self.text_level.grid(row=4, column=1, sticky=W)
        self.label_accepted = self.style(tk.Label(self.frame_player_info, text="Has accepted challenge: "),
                                         bg="black", fg="white")
        self.label_accepted.grid(row=5, column=0, sticky=E)
        self.text_accepted = self.style(tk.Label(self.frame_player_info),
                                        bg="black", fg="white")
        self.text_accepted.grid(row=5, column=1, sticky=W)
        # Game Frame
        self.frame_first_level = tk.Frame(self)
        self.frame_first_level.grid(row=0, column=1, sticky=N + S + W + E)
        self.label_first_level = tk.Label(self.frame_first_level, text="First Level")  # DEBUG
        self.label_first_level.grid(row=0, column=0, sticky=W)
        self.frame_second_level = tk.Frame(self)
        self.frame_second_level.grid(row=1, column=1, sticky=N + S + W + E)
        self.label_second_level = tk.Label(self.frame_second_level, text="Second Level")  # DEBUG
        self.label_second_level.grid(row=0, column=0, sticky=W)
        # Label for describing states
        self.frame_state_describe = tk.LabelFrame(parent, text="Current State Description", borderwidth=2, relief="groove",
                                                  background="black", foreground="white")
        self.frame_state_describe.grid(row=2, column=0, columnspan=2, padx=4, pady=4, ipadx=4, ipady=4, sticky=N + S + W + E)
        self.label_state_describe = ttk.Label(self.frame_state_describe, background="black", foreground="white")
        self.label_state_describe.grid(row=0, column=0, sticky=N + S + W + E)
        # List of all operators
        # set grid auto expand
        self.grid_auto_expand(parent, 3, 2, row_weights=[0, 1, 0], col_weights=[0, 1])
        self.grid_auto_expand(self.frame_player_info, 6, 2, row_weights=[0 for _ in range(6)], col_weights=[0, 0])

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
        if fg:
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
        display.label_state_describe.configure(text=str(state))
        if state.player:
            display.canvas_energy.coords(display.rect_energy, 0, 0, state.player.energy, 20)

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
    initialize_tk(width=600, height=300, title="InfoFlow")


StateRenderer.last_state: 'State' = None


def render_state(state: 'State'):
    # print("In render_state, state is " + str(state))  # DEBUG ONLY
    StateRenderer.get_renderer(type(state)).render(show_state_array.STATE_WINDOW, state, StateRenderer.last_state)
    StateRenderer.last_state = state
