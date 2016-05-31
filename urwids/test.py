import urwid

def keystroke(key):
    key = key.lower()
    if key == "q":
        raise urwid.ExitMainLoop()
    elif key == "/":
        pass

palette = [
    ("banner", "black,bold", "dark gray", "", "#ffa", "#60d"),
    ("streak", "light red", "dark red", "", "g50", "#60a"),
    ("inside", "dark magenta", "dark magenta" ,"", "g38", "#808"),
    ("outside", "", "dark cyan", "", "g27", "#a06"),
    ("bg", "light magenta", "black", "", "g7", "#d06"),
    ("focus", "light gray", "dark blue", "standout"),
    ("header", "yellow", "dark blue", "", "", ""),
]

placeholder = urwid.SolidFill()
txt = urwid.Text(("banner", "I'm banner markup"), align="center")
txt_dec = urwid.AttrMap(txt, "banner")

header = urwid.AttrMap(urwid.Text("C2 Testplan Editor.", "center"), "header")
footer = urwid.AttrMap(urwid.Text("qQ to exit."), "focus")

view = urwid.Frame(
    urwid.AttrWrap(txt_dec, "banner"),
    header=header,
    footer=footer)

loop = urwid.MainLoop(view, palette, unhandled_input=keystroke)
loop.run()
