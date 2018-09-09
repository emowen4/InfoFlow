import show_state_array
from InfoFlow import *
import tkinter as tk


class StateDisplay(tk.Frame):
    def __init__(self, parent, width, height):
        super().__init__(parent)
        self.width = width
        self.height = height
        # TODO
        # self.panel_playerinfo = tk.Canvas(parent, width=self.width, height=50)
        # self.canvas = tk.Canvas(parent, width=self.width, height=self.height)
        # self.canvas.pack()
        # self.caption = tk.Label(self, text="caption goes here")
        # self.caption.pack(padx=20, pady=20)


def initialize_tk(width, height, title):
    root = tk.Tk()
    root.title(title)
    display = StateDisplay(root, width=width, height=height)
    display.pack(fill="both", expand=True)
    show_state_array.STATE_WINDOW = display
    print("VIS initialization finished")


class StateRenderer:
    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        raise NotImplementedError()

    @staticmethod
    def get_renderer(state_type) -> 'StateRenderer':
        if state_type in StateRenderer.all:
            return StateRenderer.all[state_type]
        else:
            raise TypeError()


class SecondLevelStateRenderer(StateRenderer):
    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        StateRenderer.get_renderer(type(last_state)).render(display, last_state, last_state.selected_operator)


class GameStartStateRenderer(StateRenderer):
    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
        # TODO
        pass


class ChallengeMenuStateRenderer(StateRenderer):
    def render(self, display: 'StateDisplay', state: 'State', last_state: 'State'):
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
    if type(state) in StateRenderer.all:
        renderer = StateRenderer.all[type(state)]
        renderer.render(show_state_array.STATE_WINDOW, state, StateRenderer.last_state)
        StateRenderer.last_state = state
