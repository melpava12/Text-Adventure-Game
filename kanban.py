#!/usr/bin/env python3
"""Terminal Kanban board - works on Windows, Mac, and Linux."""
import curses
import json
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path

DATA_FILE = Path.home() / ".kanban_data.json"
COLUMNS = ["Todo", "In Progress", "Done"]
COL_WIDTH = 30


@dataclass
class Card:
    title: str
    col: int = 0
    created: str = field(default_factory=lambda: date.today().isoformat())
    id: int = 0


@dataclass
class Board:
    cards: list = field(default_factory=list)
    next_id: int = 1

    def add(self, title: str, col: int = 0) -> Card:
        card = Card(title=title, col=col, id=self.next_id)
        self.next_id += 1
        self.cards.append(card)
        return card

    def delete(self, card_id: int):
        self.cards = [c for c in self.cards if c.id != card_id]

    def move(self, card_id: int, direction: int):
        for card in self.cards:
            if card.id == card_id:
                card.col = max(0, min(len(COLUMNS) - 1, card.col + direction))
                break

    def col_cards(self, col: int) -> list:
        return [c for c in self.cards if c.col == col]

    def save(self):
        data = {"next_id": self.next_id, "cards": [asdict(c) for c in self.cards]}
        DATA_FILE.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls) -> "Board":
        if not DATA_FILE.exists():
            return cls()
        try:
            data = json.loads(DATA_FILE.read_text())
            board = cls(next_id=data.get("next_id", 1))
            board.cards = [Card(**c) for c in data.get("cards", [])]
            return board
        except Exception:
            return cls()


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN,    -1)  # header
    curses.init_pair(2, curses.COLOR_BLUE,    -1)  # todo col
    curses.init_pair(3, curses.COLOR_YELLOW,  -1)  # in progress col
    curses.init_pair(4, curses.COLOR_GREEN,   -1)  # done col
    curses.init_pair(5, curses.COLOR_BLACK,   curses.COLOR_CYAN)   # selected card
    curses.init_pair(6, curses.COLOR_WHITE,   -1)  # normal card
    curses.init_pair(7, curses.COLOR_RED,     -1)  # status/warning


def prompt_input(stdscr, prompt: str) -> str:
    """Show an input box at the bottom of the screen."""
    height, width = stdscr.getmaxyx()
    stdscr.addstr(height - 3, 2, prompt, curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(height - 2, 2, "> ", curses.color_pair(6))
    stdscr.clrtoeol()
    stdscr.refresh()

    curses.echo()
    curses.curs_set(1)
    try:
        raw = stdscr.getstr(height - 2, 4, width - 6)
        return raw.decode("utf-8", errors="ignore").strip()
    finally:
        curses.noecho()
        curses.curs_set(0)


def render(stdscr, board: Board, cursor_col: int, cursor_row: int, status: str = ""):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    col_colors = [
        curses.color_pair(2),
        curses.color_pair(3),
        curses.color_pair(4),
    ]

    # Title
    title = " KANBAN BOARD "
    stdscr.addstr(0, 2, title, curses.color_pair(1) | curses.A_BOLD)

    # Column headers
    for ci, name in enumerate(COLUMNS):
        x = 2 + ci * (COL_WIDTH + 2)
        count = len(board.col_cards(ci))
        label = f" {name} ({count}) ".center(COL_WIDTH)
        attr = col_colors[ci] | curses.A_BOLD
        if ci == cursor_col:
            attr |= curses.A_UNDERLINE
        stdscr.addstr(2, x, label, attr)

    # Divider
    stdscr.addstr(3, 2, "─" * (COL_WIDTH * 3 + 4), curses.color_pair(6) | curses.A_DIM)

    # Cards
    col_cards = [board.col_cards(i) for i in range(len(COLUMNS))]
    max_rows = max((len(col) for col in col_cards), default=0)
    max_display = height - 8

    for row in range(min(max_rows, max_display)):
        for ci in range(len(COLUMNS)):
            cards = col_cards[ci]
            x = 2 + ci * (COL_WIDTH + 2)
            y = 4 + row

            if row < len(cards):
                card = cards[row]
                title_text = card.title
                if len(title_text) > COL_WIDTH - 4:
                    title_text = title_text[:COL_WIDTH - 5] + "~"

                is_cursor = ci == cursor_col and row == cursor_row
                if is_cursor:
                    label = f" > {title_text:<{COL_WIDTH - 3}}"
                    stdscr.addstr(y, x, label[:COL_WIDTH], curses.color_pair(5) | curses.A_BOLD)
                else:
                    label = f"   {title_text:<{COL_WIDTH - 3}}"
                    stdscr.addstr(y, x, label[:COL_WIDTH], curses.color_pair(6))
            else:
                stdscr.addstr(4 + row, x, " " * COL_WIDTH)

    # Divider above controls
    stdscr.addstr(height - 4, 2, "─" * (COL_WIDTH * 3 + 4), curses.color_pair(6) | curses.A_DIM)

    # Controls
    controls = "  n:new   ←→:move card   ↑↓:select   Tab:switch col   d:delete   q:quit"
    stdscr.addstr(height - 3, 2, controls[:width - 4], curses.color_pair(1))

    # Status
    if status:
        stdscr.addstr(height - 2, 2, status[:width - 4], curses.color_pair(7))

    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    curses.noecho()
    stdscr.keypad(True)
    init_colors()

    board = Board.load()
    cursor_col = 0
    cursor_row = 0
    status = ""

    def clamp():
        nonlocal cursor_row
        cards = board.col_cards(cursor_col)
        cursor_row = max(0, min(cursor_row, len(cards) - 1)) if cards else 0

    while True:
        clamp()
        render(stdscr, board, cursor_col, cursor_row, status)
        status = ""
        key = stdscr.getch()

        if key == ord("q"):
            board.save()
            break

        elif key == ord("n"):
            title = prompt_input(stdscr, "New card title (Enter to confirm):")
            if title:
                board.add(title, col=cursor_col)
                cursor_row = len(board.col_cards(cursor_col)) - 1
                board.save()
                status = f"Added: {title}"

        elif key in (curses.KEY_UP, ord("k")):
            cursor_row = max(0, cursor_row - 1)

        elif key in (curses.KEY_DOWN, ord("j")):
            cursor_row += 1

        elif key in (curses.KEY_RIGHT, ord("l")):
            cards = board.col_cards(cursor_col)
            if cards and cursor_col < len(COLUMNS) - 1:
                board.move(cards[cursor_row].id, 1)
                cursor_col += 1
                board.save()

        elif key in (curses.KEY_LEFT, ord("h")):
            cards = board.col_cards(cursor_col)
            if cards and cursor_col > 0:
                board.move(cards[cursor_row].id, -1)
                cursor_col -= 1
                board.save()

        elif key == ord("\t"):
            cursor_col = (cursor_col + 1) % len(COLUMNS)

        elif key == ord("d"):
            cards = board.col_cards(cursor_col)
            if cards:
                card = cards[cursor_row]
                board.delete(card.id)
                board.save()
                status = f"Deleted: {card.title}"


if __name__ == "__main__":
    try:
        import curses
        curses.wrapper(main)
    except ModuleNotFoundError:
        print("Missing dependency. Run:  pip install windows-curses")
        print("Then try again.")
