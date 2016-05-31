import urwid


def keystroke(key):
    if key.lower() == "q":
        raise urwid.ExitMainLoop()


class QuestionBox(urwid.Filler):
    def keypress(self, size, key):
        if key != "enter":
            return super(QuestionBox, self).keypress(size, key)
        self.original_widget = urwid.Text(
            "Nice to meet you, {0}".format(edit.edit_text))

edit = urwid.Edit(u"Name: ")
fill = QuestionBox(edit)

loop = urwid.MainLoop(fill, unhandled_input=keystroke)
loop.run()
