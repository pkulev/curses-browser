"""Utilities for handling with test plans."""

import curses
import functools
import os
import sys
import time
import traceback
from pprint import pformat, pprint

from curses import A_NORMAL, A_BOLD

from dataframe import DataFrame

def execute(args, oargs):
    """Execute test plan using c2tests.

    :param plan: test plan to execute
    :type plan: file object

    :param fail_once: exit on first failed test
    :type fail_once: bool

    :param oargs: args to pass to c2tests
    :type oargs: list
    """
    testplan = args.file
    fail_once = args.fail_once
    testplan_data = parse_test_plan(testplan.file)

    print("FAIL_ONCE %s" % str(fail_once))
    print("OARGS %s" % str(oargs))
    testplan.close()


def parse_test_plan(filename, delim=":"):
    """
    Parse test plan by delimeter.

    Syntax (for colon):
    SuiteName1:CaseName1
    SuiteName1:CaseName2
    SuiteName2:*

    # Wildcard means 'execute all cases in suite'.
    # Blank line and comments are valid too.

    :param filename: file for parsing
    :type filename: str

    :param delim: delimeter
    :type delim: str

    :return: generator object that yields (str, str)
    """
    with open(filename, "r") as source:
        lines = [
            line.strip()
            for line in source.readlines()
            if line != "\n" and not line.startswith("#")]

    for line in lines:
        yield line.split(delim)


def to_string(entry):
    """Represent entry as string."""
    indents = ("", "    ")
    template = "{indent}{checked} {name}"
    return template.format(
        indent=indents[entry["indent"]],
        checked="[*]" if entry["checked"] else "[ ]",
        name=entry["case"] if entry["isCase"] else entry["suite"])


def shorten(text, width, placeholder="[...]", cut_placeholder=True):
    """Collapse and truncate the given text to fit in the given width.

    :param text: text for shortening
    :type text: str

    :param width: width of produced length
    :type width: int

    :param placeholder: end of line
    :type placeholder: str

    :return: collapsed and truncated text
    :rtype: str
    """
    if width < len(placeholder):
        if cut_placeholder:
            while width < len(placeholder):
                placeholder = placeholder[0 : len(placeholder) / 2] + \
                    placeholder[len(placeholder) / 2 + 1 :]
            return placeholder
        else:
            raise ValueError("placeholder too large for max width")

    if len(text) <= width:
        return text
    return text[0 : width - len(placeholder)] + placeholder


def init_curses():
    """Initialize curses.

    :return: curses.Window object
    """
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.nodelay(1)
    screen.keypad(1)
    curses.start_color()
    # Highlighted string color
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    # Error string color
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    screen.border(0)
    curses.curs_set(0)
    return screen


def deinit_curses(screen):
    """Deinitialize curses.

    :param screen: curses window
    :type screen: curses.Window
    """
    screen.nodelay(0)
    screen.keypad(0)
    curses.nocbreak()
    curses.curs_set(1)
    curses.endwin()


def key(keycode, keymap):
    def decorator(func):
        keymap[keycode] = func
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


class PlanMenu(object):
    """Data format:
    list of dicts:
    [{
        "suite": "SuiteName1",
        "case": "CaseName1",
        "check": True,
        "fold": True}]"""

    SLEEP_TIME = 0.03

    KEYMAP = dict()
    KEY_ESC = 27
    KEY_ENTER = ord("\n")
    KEY_SPACE = ord(" ")

    def __init__(self, data, filename):
        self._dframe = DataFrame(data)
        self._filename = filename

        self._screen = init_curses()

        # self._resize() will calculate variables below
        self._box = None
        self._max_y = None
        self._max_x = None
        self._resize()

        self._pos_y = 1
        self._running = False
        self._message = {
            "msg": "",
            "default_counter": 80,
            "counter": 80,
            "style": curses.color_pair(2) | A_BOLD}

    def _resize(self):
        """Handle terminal resizing."""
        scrsize = self._screen.getmaxyx()
        border = (scrsize[0] - 2, scrsize[1] - 2)
        self._box = curses.newwin(border[0], border[1], 1, 1)
        self._box.box()

        self._max_y = border[0] - 2
        self._max_x = border[1] - 2

        # Last string will be footer
        self._dframe.granulate(self._max_y - 1)
        self._pos_y = 1  # TODO: DataFrame.granulate sets all indexes to 0
        # TODO: make this clearer
        if self._max_x >= 4 and self._max_y >= 4:
            self._screen.border(0)
        else:
            self._screen.clear()

    def _notify(self, msg="", style=A_NORMAL):
        """Update message with notification.

        :param msg: message
        :type msg: str

        :param style: terminal string style
        :type style: int
        """
        if msg:
            self._message["msg"] = msg
            self._message["counter"] = self._message["default_counter"]
            self._message["style"] = style

    def _error(self, msg="ERR", style=None):
        """Update message with error.

        :param msg: message
        :type msg: str

        :param style: terminal string style
        :type style: int
        """
        style = style or (curses.color_pair(2) | A_BOLD)
        self._notify(msg, style)

    def _save_file(self, file_):
        """Save DataFrame's content to file.

        :param file_: file object for save
        :type file_: file
        """
        template = "{suite}:{case}"
        #filtered = itertools.takewhile(lambda x: x["checked"], self._dframe)
        try:
            for entry in self._dframe:
                if entry["checked"]:
                    file_.write(entry + "\n")
        except IOError:
            self._error("Can't save file")
        else:
            self._notify("Saved to %s" % self._filename)

    @key(curses.KEY_DOWN, KEYMAP)
    def move_down(self):
        """Move cursor line down."""
        if self._dframe.element_index < len(self._dframe) - 1:
            if self._pos_y > self._max_y - 2:
                self._pos_y = 1
            else:
                self._pos_y += 1
            self._dframe.move_next()

    @key(curses.KEY_UP, KEYMAP)
    def move_up(self):
        """Move cursor line up."""
        if self._dframe.frame_index > 0 and self._pos_y == 1:
            self._pos_y = self._max_y - 1
        elif self._pos_y > 1:
            self._pos_y -= 1
        self._dframe.move_prev()

    @key(KEY_ESC, KEYMAP)
    def exit(self):
        """Exit without saving."""
        self._error("Exitting...")
        self._running = False

    @key(curses.KEY_LEFT, KEYMAP)
    def move_left(self):
        """Previous page."""
        self._dframe.prev_frame()

    @key(curses.KEY_RIGHT, KEYMAP)
    def move_right(self):
        """Next page."""
        self._dframe.next_frame()
        if self._pos_y > len(self._dframe.frame):
            self._pos_y = len(self._dframe.frame)

    @key(KEY_ENTER, KEYMAP)
    @key(KEY_SPACE, KEYMAP)
    def toggle_check(self):
        """Toggle element's checkbox."""
        if len(self._dframe):
            entry = self._dframe.element
            entry["checked"] = not entry["checked"]
            self.move_down()

    @key(curses.KEY_RESIZE, KEYMAP)
    def resize(self):
        """Resize terminal."""
        self._resize()

    @key(curses.KEY_F5, KEYMAP)
    def save(self):
        """Save to file."""
        with open(self._filename, "w") as file_:
            self._save_file(file_)

    def events(self):
        """Handle key events."""
        key = self._screen.getch()
        action = self.KEYMAP.get(key)
        if action:
            action(self)

    def _update_content(self):
        """Update box's content."""
        if not len(self._dframe):
            self._box.addstr(2, 2, shorten("No data available", self._max_x))
            return

        for idy, entry in enumerate(self._dframe.frame, 1):
            if idy == self._pos_y:
                style = curses.color_pair(1)
            else:
                style = curses.A_NORMAL
            string = shorten(to_string(entry), self._max_x)
            self._box.addstr(idy, 2, string, style)


    def _update_footer(self):
        """Update box's footer."""

        def addstr(pos_y, pos_x, string, style=None):
            """Wrapper above curses.Window's method."""
            self._box.addstr(pos_y, pos_x, string, style or A_NORMAL)

        def update_message():
            """Update message dict."""
            if self._message["msg"]:
                if self._message["counter"] > 0:
                    self._message["counter"] -= 1
                else:
                    self._message["msg"] = ""
                    self._message["counter"] = self._message["default_counter"]

        left = "Save: F1  Exit: ESC  Nav: arrows  Toggle: enter"
        left_pos = (self._max_y, 2)

        center = "PAGE: [{0}/{1}]".format(
            self._dframe.frame_index + 1,
            self._dframe.frames_count())
        center_pos = (self._max_y, self._max_x // 2 - len(center) // 2)

        update_message()
        right = self._message["msg"]
        right_pos = (self._max_y, self._max_x - len(right) - 2)

        addstr(*left_pos, string=left)
        addstr(*center_pos, string=center)
        addstr(*right_pos, string=right, style=self._message["style"])

    def update(self):
        """Update state."""
        self._update_content()
        self._update_footer()

    def render(self):
        """Render content to screen."""
        self._screen.refresh()
        self._box.refresh()
        self._box.erase()
        # XXX: Resize handling. Need more to test to rewrite
        if self._max_x > 2 and self._max_y > 2:
            self._box.border(0)

    def loop(self):
        """Main loop."""
        if self._screen:
            self._running = True

        try:
            while self._running:
                self.events()
                self.update()
                self.render()
                time.sleep(self.SLEEP_TIME)
        except Exception:
            deinit_curses(self._screen)
            traceback.print_exc()
            pprint(vars(self))
            return os.EX_SOFTWARE

        deinit_curses(self._screen)
        return os.EX_OK


def main():
    import sys
    if len(sys.argv) != 1:
        sys.exit(0)

    testplan_data = [
        "testsuite{0}:testcase{1}".format(suite, case)
        for suite in range(10) for case in range(20)
    ]
    plan_menu = PlanMenu(testplan_data, "testfile.txt")
    plan_menu.loop()


if __name__ == "__main__":
    main()
