import os
import random
import webbrowser
from urllib.parse import quote

import tkinter as tk

# ===== CONFIGURATION =====
BASE_FONT_SIZE = 24
SPAWN_COUNT = 2
INTERVAL = 2000
LANE_COUNT = 8
COLORS = [
    "red", "green", "blue", "orange", "purple", "pink", "yellow", "cyan",
    "magenta", "lime", "teal", "gold", "salmon", "violet", "brown", "coral",
    "turquoise", "indigo", "olive", "maroon"
]

# Depth factors for lanes (0.5 = far, 1.0 = near)
LANE_DEPTH = [0.5 + (i / (LANE_COUNT - 1)) * 0.5 for i in range(LANE_COUNT)]

# Mapping keys to JLPT files
JLPT_FILES = {
    "1": "JLPT-N5.txt",
    "2": "JLPT-N4.txt",
    "3": "JLPT-N3.txt",
    "4": "JLPT-N2.txt",
    "5": "JLPT-N1.txt"
}

def load_words(filename):
    """Load words from a text file, one per line. Returns an empty list if the file is not found."""
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def adjust_color(canvas, color, depth):
    """Adjust color brightness based on depth factor (0.5=far, 1=near)."""
    rgb = canvas.winfo_rgb(color)
    r, g, b = [v / 65535 for v in rgb]  # normalize 0-1
    r *= depth
    g *= depth
    b *= depth
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


class JLPTRain:
    """Tkinter app that scrolls JLPT vocabulary words across the screen in a
    depth-layered rain effect. Words are clickable and open Jisho.org for lookup.
    Press 1–5 to switch between JLPT levels N5–N1."""

    def __init__(self, root):
        self.root = root
        self.root.title("JLPT Rain")
        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.items = []

        # Load default words
        self.current_level = "JLPT-N5"
        self.words = load_words(self.current_level + ".txt")

        # Overlay showing current level (smaller, grey)
        self.overlay = self.canvas.create_text(
            10, 10, text=self.current_level, fill="grey", anchor="nw", font=("Helvetica", 10, "bold")
        )

        self.root.bind("<Key>", self.key_press)

        self.root.after(INTERVAL, self.spawn_word)
        self.animate()

    def key_press(self, event):
        key = event.char
        if key in JLPT_FILES:
            level = JLPT_FILES[key].replace(".txt", "")
            new_words = load_words(JLPT_FILES[key])
            if new_words:
                self.words = new_words
                self.current_level = level
                self.canvas.itemconfig(self.overlay, text=level)
            else:
                self.canvas.itemconfig(self.overlay, text=f"{level} (not found)")

    def get_jisho_url(self, word):
        return f"https://jisho.org/search/{quote(word)}"

    def get_jisho(self, event, word):
        webbrowser.open(self.get_jisho_url(word))

    def spawn_word(self):
        """Spawn a batch of words at the right edge of the canvas, each assigned
        a random lane, color, and speed. Reschedules itself every INTERVAL ms."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if height < 80:
            height = 200

        lane_height = height // LANE_COUNT

        for _ in range(SPAWN_COUNT):
            word = random.choice(self.words)
            lane = random.randint(0, LANE_COUNT - 1)
            y = lane * lane_height + lane_height // 2
            depth = LANE_DEPTH[lane]

            color = adjust_color(self.canvas, random.choice(COLORS), depth)
            speed = random.uniform(1, 3) * depth  # faster for closer lanes
            x_offset = random.randint(0, 50)

            item = self.canvas.create_text(
                width + x_offset, y,
                text=word, fill=color, font=("Helvetica", BASE_FONT_SIZE, "bold"), anchor="w"
            )

            self.items.append((item, speed))

            self.canvas.tag_bind(item, "<Button-1>", lambda e, w=word: self.get_jisho(e, w))

        self.root.after(INTERVAL, self.spawn_word)


    def animate(self):
        """Move all active words left by their speed each frame, and remove any
        that have scrolled off the left edge. Runs every 30ms."""
        to_remove = []
        for idx, (item, speed) in enumerate(self.items):
            self.canvas.move(item, -speed, 0)
            x, _ = self.canvas.coords(item)
            if x < -200:
                to_remove.append(idx)

        for idx in reversed(to_remove):
            self.canvas.delete(self.items[idx][0])
            del self.items[idx]

        self.root.after(30, self.animate)


if __name__ == "__main__":
    root = tk.Tk()
    app = JLPTRain(root)
    root.mainloop()

