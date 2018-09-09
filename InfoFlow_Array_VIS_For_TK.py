from show_state_array import initialize_tk, state_array, state_display, STATE_WINDOW, test

from tkinter import font

myFont = None

WIDTH = 1200
HEIGHT = 100
TITLE = 'InfoFlow'


def initialize_vis():
    initialize_tk(WIDTH, HEIGHT, TITLE)

def render_state(s):
    # Note that font creation is only allowed after the Tk root has been
    # defined.  So we check here if the font creation is still needed,
    # and we do it (the first time this method is called).
    global myFont
    if not myFont:
        myFont = font.Font(family="Times", size=18, weight="bold")
    print("In render_state, state is " + str(s))
    # Create the default array of colors
    tan = (200, 190, 128)
    blue = (100, 100, 255)
    brown = (100, 80, 0)
    pink = (194, 152, 143)
    yellow = (227,207,87)
    purple = (51,0,111)
    gold = (232,211,162)

    row = [purple] * 4 + [gold] * 2 + [purple] * 4
    the_color_array = [row[:],row[:]]
    # Now create the default array of string labels.
    row = ['' for i in range(12)]
    the_string_array = [row[:],row[:]]

    # Adjust colors and strings to match the state.


    caption = "Current state of the game. Textual version: " + str(s)
    the_state_array = state_array(color_array=the_color_array,
                                  string_array=the_string_array,
                                  text_font=myFont,
                                  caption=caption)
    # print("the_state_array is: "+str(the_state_array))
    the_state_array.show()




