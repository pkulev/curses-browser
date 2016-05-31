import urwid


def question():
    return urwid.Pile([urwid.Edit(("--> "))])


def answer(message):
    return urwid.Text(("I say", u"{0}: {1}".format("Most", message)))


def on_exit_clicked(button):
    raise urwid.ExitMainLoop()


class ChatListBox(urwid.ListBox):
    def __init__(self):
        body = urwid.SimpleFocusListWalker([question()])
        super(ChatListBox, self).__init__(body)

    def keypress(self, size, key):
        key = super(ChatListBox, self).keypress(size, key)
        if key != "enter":
            return key

        message = self.focus[0].edit_text

        self.focus.contents[1:] = [(answer(message), self.focus.options())]
        pos = self.focus_position

        self.body.insert(pos + 1, question())
        self.focus_position = pos + 1

palette = [
    ("I say", "default,bold", "default", "bold"),
]

b_exit = urwid.Button(u"Exit", on_exit_clicked)
top = urwid.Frame(ChatListBox(),
                  header=urwid.Text("Blabla"),
                  footer=b_exit)

loop = urwid.MainLoop(top, palette)
loop.run()
