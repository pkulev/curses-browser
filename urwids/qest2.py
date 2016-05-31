import urwid

palette = [
    ("I say", "default,bold", "default", "bold"),
]

def keystroke(key):
    if key.lower() == "q":
        raise urwid.ExitMainLoop()

edit = urwid.Edit(("I say", "What's your name?\n"))
reply = urwid.Text(u"")
button = urwid.Button(u"Exit")
div = urwid.Divider()
pile = urwid.Pile([edit, div, reply, div, button])
top = urwid.Filler(pile, valign="top")

def on_edit_change(edit, new_edit_text):
    reply.set_text(("I say", "Nice to meet you, {0}".format(new_edit_text)))

def on_exit_clicked(button):
    raise urwid.ExitMainLoop()

urwid.connect_signal(edit, "change", on_edit_change)
urwid.connect_signal(button, "click", on_exit_clicked)

loop = urwid.MainLoop(top, palette)
loop.run()
