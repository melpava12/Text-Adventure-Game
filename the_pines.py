# -*- coding: utf-8 -*-
import tkinter as tk
import random
import threading
import math
import wave
import struct
import tempfile

# ─── Colours ──────────────────────────────────────────────────────────────────

BG          = '#0d0608'
TEXT_COL    = '#e8ddd0'
CHOICE_BG   = '#2a1520'
CHOICE_HOV  = '#3d2030'
BTN_TEXT    = '#f0e6d3'
ACCENT      = '#8b4a4a'
GOLD        = '#c4956a'
DIM         = '#8b6a5a'
INPUT_BG    = '#1a0c10'

# ─── Sound ────────────────────────────────────────────────────────────────────

KNOCK_WAV = None
CREAK_WAV = None


def _write_wav(samples, sr):
    f = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    with wave.open(f.name, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(struct.pack(f'<{len(samples)}h', *samples))
    return f.name


def _gen_knock():
    sr = 44100
    samples = []
    for i in range(int(sr * 0.18)):
        t = i / sr
        v = int(32767 * math.exp(-t * 28) * abs(math.sin(2 * math.pi * 110 * t)))
        samples.append(v)
    return _write_wav(samples, sr)


def _gen_creak():
    sr = 44100
    dur = 1.8
    samples = []
    for i in range(int(sr * dur)):
        t = i / sr
        freq = 180 + 220 * math.sin(math.pi * t / dur) + 30 * math.sin(7 * math.pi * t)
        noise = random.uniform(-0.25, 0.25)
        v = int(13000 * (1 - t / dur * 0.5) * (math.sin(2 * math.pi * freq * t) + noise))
        samples.append(max(-32767, min(32767, v)))
    return _write_wav(samples, sr)


def init_sounds():
    global KNOCK_WAV, CREAK_WAV
    KNOCK_WAV = _gen_knock()
    CREAK_WAV = _gen_creak()


def play_sound(path):
    try:
        import winsound
        threading.Thread(
            target=lambda: winsound.PlaySound(path, winsound.SND_FILENAME),
            daemon=True
        ).start()
    except Exception:
        pass


# ─── Game ─────────────────────────────────────────────────────────────────────

class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("The Pines: A Haunted Getaway")
        self.root.configure(bg=BG)
        self.root.geometry('880x700')
        self.root.resizable(False, False)

        self.player_name = ''
        self.path = None
        self._skip = False
        self._typing = False
        self._history_visible = False
        self._history_win = None

        self._build_ui()
        init_sounds()

        self.root.after(400, self.scene_title)
        self.root.mainloop()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Use grid so the bottom bar has a guaranteed fixed height
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Row 0 — header
        header = tk.Frame(self.root, bg='#1a0810', pady=10)
        header.grid(row=0, column=0, sticky='ew')

        tk.Label(header, text='THE PINES', bg='#1a0810', fg=GOLD,
                 font=('Georgia', 20, 'bold')).pack()
        tk.Label(header, text='A Haunted Getaway', bg='#1a0810', fg=DIM,
                 font=('Georgia', 10, 'italic')).pack()

        self._history_btn = tk.Button(
            header, text='📋  History', bg='#2a1520', fg=DIM,
            font=('Georgia', 9), relief='flat', bd=0, padx=10, pady=3,
            cursor='hand2', activebackground=CHOICE_HOV, activeforeground=BTN_TEXT,
            command=self._toggle_history
        )
        self._history_btn.place(relx=1.0, rely=0.5, anchor='e', x=-12)

        # Row 1 — scrollable text area (expands)
        self.text_frame = tk.Frame(self.root, bg=BG, padx=44, pady=18)
        self.text_frame.grid(row=1, column=0, sticky='nsew')
        self.text_frame.grid_rowconfigure(0, weight=1)
        self.text_frame.grid_columnconfigure(0, weight=1)

        self.text_widget = tk.Text(
            self.text_frame, bg=BG, fg=TEXT_COL,
            font=('Georgia', 12), wrap='word',
            relief='flat', bd=0, cursor='arrow',
            state='disabled', spacing1=3, spacing3=3
        )
        self.text_widget.grid(row=0, column=0, sticky='nsew')
        self.text_widget.bind('<Button-1>', self._skip_type)
        self.root.bind('<space>', self._skip_type)

        # Row 2 — thin separator
        tk.Frame(self.root, bg=ACCENT, height=2).grid(row=2, column=0, sticky='ew')

        # Row 3 — bottom action bar (sizes to content)
        self.bottom = tk.Frame(self.root, bg='#1e0f14', padx=44, pady=10)
        self.bottom.grid(row=3, column=0, sticky='ew')

    def _skip_type(self, _=None):
        self._skip = True

    # ── History panel ─────────────────────────────────────────────────────────

    def _toggle_history(self):
        if self._history_visible and self._history_win:
            self._history_win.withdraw()
            self._history_visible = False
            self._history_btn.config(fg=DIM)
        else:
            if self._history_win is None:
                self._build_history_window()
            self._history_win.deiconify()
            self._history_visible = True
            self._history_btn.config(fg=GOLD)

    def _build_history_window(self):
        win = tk.Toplevel(self.root)
        win.title('History')
        win.geometry('320x500')
        win.configure(bg='#110a0d')
        win.resizable(True, True)
        # Position it to the right of the main window
        self.root.update_idletasks()
        x = self.root.winfo_x() + self.root.winfo_width() + 8
        y = self.root.winfo_y()
        win.geometry(f'+{x}+{y}')
        win.protocol('WM_DELETE_WINDOW', self._toggle_history)

        tk.Label(win, text='Run History', bg='#110a0d', fg=GOLD,
                 font=('Georgia', 12, 'bold'), pady=8).pack(fill='x')
        tk.Frame(win, bg=ACCENT, height=1).pack(fill='x', padx=12)

        frame = tk.Frame(win, bg='#110a0d')
        frame.pack(fill='both', expand=True, padx=8, pady=8)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')

        self._history_text = tk.Text(
            frame, bg='#110a0d', fg=TEXT_COL,
            font=('Georgia', 10), wrap='word',
            relief='flat', bd=0, state='disabled',
            spacing1=2, spacing3=4,
            yscrollcommand=scrollbar.set
        )
        self._history_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self._history_text.yview)

        # Tags for styling
        self._history_text.tag_config('scene',    foreground=GOLD,
                                       font=('Georgia', 10, 'bold'))
        self._history_text.tag_config('dialogue', foreground=TEXT_COL,
                                       font=('Georgia', 10))
        self._history_text.tag_config('choice',   foreground='#c49a9a',
                                       font=('Georgia', 10, 'italic'))
        self._history_text.tag_config('input',    foreground='#9ac4c4',
                                       font=('Georgia', 10, 'italic'))
        self._history_text.tag_config('divider',  foreground='#3d2030')

        self._history_win = win

    def log(self, text, kind='dialogue'):
        """Add an entry to the history panel. kind: 'scene', 'dialogue', 'choice', 'input'"""
        if self._history_win is None:
            self._build_history_window()
            self._history_win.withdraw()

        self._history_text.config(state='normal')
        if kind == 'scene':
            self._history_text.insert('end', f'\n── {text} ──\n', 'scene')
        elif kind == 'choice':
            self._history_text.insert('end', f'  ▶ {text}\n', 'choice')
        elif kind == 'input':
            self._history_text.insert('end', f'  ✎ {text}\n', 'input')
        else:
            self._history_text.insert('end', text, 'dialogue')
        self._history_text.config(state='disabled')
        self._history_text.see('end')

    # ── Text helpers ──────────────────────────────────────────────────────────

    def clear(self):
        self.text_widget.config(state='normal')
        self.text_widget.delete('1.0', 'end')
        self.text_widget.config(state='disabled')
        self._clear_bottom()

    def _clear_bottom(self):
        for w in self.bottom.winfo_children():
            w.destroy()

    def type_text(self, text, callback=None, speed=16):
        self._skip = False
        self._typing = True
        self._clear_bottom()
        self.log(text, 'dialogue')
        self.text_widget.config(state='normal')
        chars = list(text)

        def _done():
            self.text_widget.config(state='disabled')
            self._typing = False
            if callback:
                self.show_continue(callback)

        def _tick(idx=0):
            if self._skip:
                self.text_widget.insert('end', ''.join(chars[idx:]))
                self.text_widget.see('end')
                _done()
                return
            if idx < len(chars):
                self.text_widget.insert('end', chars[idx])
                self.text_widget.see('end')
                ch = chars[idx]
                delay = 55 if ch in '.!?\n' else (1 if ch == ' ' else speed)
                self.root.after(delay, lambda: _tick(idx + 1))
            else:
                _done()

        _tick()

    def append_text(self, text, callback=None, speed=16):
        self.type_text(text, callback, speed)

    # ── Choices & input ───────────────────────────────────────────────────────

    def show_continue(self, callback, label='Continue  ▶'):
        """Show a single centred Continue button — used between scenes."""
        self._clear_bottom()
        btn = tk.Button(
            self.bottom, text=label, bg=ACCENT, fg=BTN_TEXT,
            font=('Georgia', 11, 'italic'), relief='flat', bd=0,
            padx=20, pady=7, cursor='hand2',
            activebackground=CHOICE_HOV, activeforeground=BTN_TEXT,
            command=callback
        )
        btn.pack(pady=2)

    def show_choices(self, choices):
        self._clear_bottom()
        for label, cb in choices:
            btn = tk.Button(
                self.bottom, text=label, bg=CHOICE_BG, fg=BTN_TEXT,
                font=('Georgia', 11), relief='flat', bd=0,
                padx=14, pady=7, cursor='hand2',
                anchor='w', wraplength=760, justify='left',
                activebackground=CHOICE_HOV, activeforeground=BTN_TEXT,
                command=cb
            )
            btn.pack(fill='x', pady=2)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=CHOICE_HOV))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=CHOICE_BG))

    def get_input(self, prompt, callback):
        self._clear_bottom()
        row = tk.Frame(self.bottom, bg='#110a0d')
        row.pack(fill='x')

        tk.Label(row, text=prompt, bg='#110a0d', fg=GOLD,
                 font=('Georgia', 12, 'italic')).pack(side='left', padx=(0, 10))

        entry = tk.Entry(row, bg=INPUT_BG, fg=TEXT_COL,
                         insertbackground=GOLD,
                         font=('Georgia', 12), relief='groove', bd=3, width=36)
        entry.pack(side='left', fill='x', expand=True)

        def submit(_=None):
            val = entry.get().strip()
            if val:
                self._clear_bottom()
                callback(val)

        entry.bind('<Return>', submit)
        tk.Button(row, text='→', bg=ACCENT, fg=BTN_TEXT,
                  font=('Georgia', 13), relief='flat', bd=0,
                  padx=10, cursor='hand2', command=submit
                  ).pack(side='left', padx=(6, 0))
        entry.focus_set()

    # ── Knock mini-game ───────────────────────────────────────────────────────

    def knock_minigame(self, callback):
        self._clear_bottom()
        self.root.update_idletasks()

        w = self.text_frame.winfo_width()
        h = self.text_frame.winfo_height()

        canvas = tk.Canvas(self.text_frame, bg=BG, width=w, height=h,
                           relief='flat', bd=0, highlightthickness=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)

        canvas.create_text(w // 2, 36, text='Something knocks back.',
                           fill=TEXT_COL, font=('Georgia', 14, 'italic'))
        canvas.create_text(w // 2, 62, text='Click each light to answer.',
                           fill=DIM, font=('Georgia', 10))

        # Place 5 non-overlapping dots
        margin = 70
        positions = []
        attempts = 0
        while len(positions) < 5 and attempts < 500:
            attempts += 1
            x = random.randint(margin, w - margin)
            y = random.randint(100, h - 60)
            if all(math.hypot(x - px, y - py) > 90 for px, py in positions):
                positions.append((x, y))

        remaining = [len(positions)]

        def make_dot(x, y):
            r = 16
            glow = canvas.create_oval(x - r - 5, y - r - 5, x + r + 5, y + r + 5,
                                      outline='#5a2535', width=1)
            dot  = canvas.create_oval(x - r, y - r, x + r, y + r,
                                      fill='#3d2030', outline=GOLD, width=2)

            def on_click(_):
                canvas.itemconfig(dot, fill=GOLD)
                canvas.itemconfig(glow, outline=TEXT_COL)
                play_sound(KNOCK_WAV)
                canvas.tag_unbind(dot,  '<Button-1>')
                canvas.tag_unbind(glow, '<Button-1>')
                canvas.tag_unbind(dot,  '<Enter>')
                canvas.tag_unbind(dot,  '<Leave>')
                self.root.after(220, lambda: canvas.itemconfig(dot, fill='#1a0810'))
                self.root.after(220, lambda: canvas.itemconfig(glow, outline=''))
                remaining[0] -= 1
                if remaining[0] == 0:
                    self.root.after(700, lambda: (canvas.destroy(), callback()))

            canvas.tag_bind(dot,  '<Button-1>', on_click)
            canvas.tag_bind(glow, '<Button-1>', on_click)
            canvas.tag_bind(dot,  '<Enter>',
                            lambda e: canvas.itemconfig(dot, fill='#5a2535'))
            canvas.tag_bind(dot,  '<Leave>',
                            lambda e: canvas.itemconfig(dot, fill='#3d2030'))

        for x, y in positions:
            make_dot(x, y)

    # =========================================================================
    # SCENES
    # =========================================================================

    # ── Title screen ──────────────────────────────────────────────────────────

    def scene_title(self):
        self.clear()
        self.type_text(
            "ABOUT THIS GAME\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "The Pines: A Haunted Getaway is a horror comedy text adventure.\n\n"
            "You've booked a suspiciously cheap weekend at The Pines Bed & Breakfast. "
            "Upon arrival you discover the staff are monsters — but they're desperately "
            "trying to get a good review on HauntBnB because they're three months behind "
            "on the mortgage.\n\n"
            "The horror is real. The danger is real. The monsters just really, really "
            "need that five-star rating.\n\n"
            "Your choices shape the story across three distinct paths, each leading to "
            "one of three possible endings. How you treat the staff — and how curious "
            "you let yourself get — determines everything.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "THE CAST\n\n"
            "VICTOR  —  Your host. A 400-year-old vampire in a burgundy waistcoat who "
            "has never successfully made small talk and refuses to stop trying. "
            "Deeply dramatic. Surprisingly soft underneath. Bought The Pines in 1987 "
            "because he had never, in four centuries, had somewhere that was his.\n\n"
            "GRETA  —  The chef. A werewolf with an encyclopaedic knowledge of French "
            "cuisine and a habit of shedding when stressed. Makes a Wellington that will "
            "rearrange your priorities. Has been at The Pines since 1993 and considers "
            "it her kitchen in every meaningful sense.\n\n"
            "DOT  —  The housekeeper. A ghost who has haunted The Pines since the 1940s "
            "and effectively came with the building. Cares enormously about hospital "
            "corners. Will glow brighter when complimented. The emotional backbone of "
            "the entire operation, whether she admits it or not.\n\n"
            "BARRY  —  Maintains the pool. Arrived from the creek in 2001 and never "
            "left. Seven feet tall, green-scaled, and intensely private. Enjoys tide "
            "pool documentaries and quiet rooms. More is going on with Barry than "
            "anyone has fully investigated.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
            callback=self.scene_intro
        )

    # ── Intro ─────────────────────────────────────────────────────────────────

    def scene_intro(self):
        self.clear()
        self.type_text(
            "It's Friday evening.\n\n"
            "You booked The Pines Bed & Breakfast three weeks ago after finding it "
            "on HauntBnB for $12 a night. The reviews were... sparse. One simply "
            "read: 'I left.' Another: 'The eggs were good (3 stars).'\n\n"
            "You told yourself it was a deal. You told yourself it would be an adventure.\n\n"
            "You are now parked in front of a Victorian mansion that is definitely "
            "leaning slightly to the left, and a fog has rolled in that seems "
            "personally interested in you.\n\n"
            "Your phone has one bar. Your gas tank is empty. The lights inside are on.\n\n"
            "You grab your overnight bag.\n\n",
            callback=self._ask_name
        )

    def _ask_name(self):
        self.get_input("Who are you, traveller?", self._set_name)

    def _set_name(self, name):
        self.player_name = name.strip().title()
        self.log(f'Name entered: {self.player_name}', 'input')
        self.append_text(
            f"\nAh, {self.player_name}. What a perfectly normal name for a perfectly "
            "normal person about to have a perfectly normal weekend.\n",
            callback=self.scene_act1
        )

    # ── Act 1 — Victor's Welcome ──────────────────────────────────────────────

    def scene_act1(self):
        self.clear()
        self.type_text(
            "THE FRONT DOOR\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "The front door swings open before you knock.\n\n"
            "Standing in the doorway is a very tall, very pale man in a burgundy "
            "waistcoat. He has slicked-back hair, a widow's peak that could cut "
            "glass, and is holding a candelabra despite there being perfectly "
            "functional electric lights behind him.\n\n"
            "He stares at you for a long moment.\n\n"
            "\"You... CAME,\" he breathes, like you've fulfilled an ancient prophecy.\n\n"
            "A beat of silence.\n\n"
            "\"I am Victor. I will be your host this evening.\" He gestures grandly "
            "at the interior. A moth flies out of his sleeve. He does not acknowledge it.\n\n"
            "What do you do?\n",
            callback=lambda: self.show_choices([
                ('[A]  Gesture grandly back and say "Wonderful to be here, Victor."',
                 self._act1_a),
                ('[B]  Ask if the WiFi password is somewhere on the confirmation email.',
                 self._act1_b),
                ('[C]  Say "Actually I think I left my straightener on" and back toward your car.',
                 self._act1_c),
            ])
        )

    def _act1_a(self):
        self.path = 'friendly'
        self.log('Act 1 — Victor\'s Welcome', 'scene')
        self.log('Gestured grandly back at Victor', 'choice')
        self.clear()
        self.type_text(
            "Victor blinks. Then, slowly, a smile spreads across his face. "
            "It shows slightly too many teeth.\n\n"
            "\"A guest with SPIRIT,\" he says approvingly. \"Excellent. Come. "
            "Your room awaits. I had Dot prepare it. Mostly.\"\n\n"
            "You follow him inside. The chandelier flickers. Somewhere deeper in "
            "the house, something crashes, followed by a whispered \"I'm FINE.\"\n\n"
            "Victor does not break stride.\n\n"
            "You decide you like it here.\n",
            callback=self.scene_act2_friendly
        )

    def _act1_b(self):
        self.path = 'skeptic'
        self.log('Act 1 — Victor\'s Welcome', 'scene')
        self.log('Asked about the WiFi', 'choice')
        self.clear()
        self.type_text(
            "Victor's eye twitches.\n\n"
            "\"The... WiFi,\" he repeats.\n\n"
            "\"Yes. The wireless internet. For my phone.\"\n\n"
            "He stares at you with the expression of a man encountering a word "
            "in a language he has never heard.\n\n"
            "\"Wire... less.\"\n\n"
            "\"It's how phones connect to the internet without a cable.\"\n\n"
            "\"Phones have cables?\"\n\n"
            "\"They used to. Now they don't. That's the point.\"\n\n"
            "Victor looks at your phone. Then back at you. His brow furrows with "
            "the deep consternation of someone who has been alive for 400 years "
            "and finds the 21st century personally offensive.\n\n"
            "\"So the internet,\" he says slowly, \"travels. Through the air.\"\n\n"
            "\"Yes.\"\n\n"
            "\"Like a bat.\"\n\n"
            "\"...Sure.\"\n\n"
            "\"And your small rectangle needs to catch it.\"\n\n"
            "\"Essentially.\"\n\n"
            "A very long pause.\n\n"
            "\"I will ask Greta,\" he says finally, with great dignity. \"She handles "
            "the router.\" He says 'router' the way someone says a word they have "
            "only ever seen written down.\n\n"
            "He steps aside to let you in. As you pass him you notice he doesn't "
            "cast a reflection in the hallway mirror. You file this away.\n\n"
            "Something to look into later.\n",
            callback=self.scene_act2_skeptic
        )

    def _act1_c(self):
        self.log('Act 1 — Victor\'s Welcome', 'scene')
        self.log('Claimed to have left the straightener on', 'choice')
        self.clear()
        self.type_text(
            "\"Actually I think I left my straightener on,\" you say, "
            "already stepping back.\n\n"
            "Victor glances at your hair with the unselfconscious frankness of "
            "someone who has not had to observe social niceties for several centuries.\n\n"
            "\"You have a buzz cut,\" he says.\n\n"
            "A pause.\n\n"
            "\"...It's my travel straightener.\"\n\n"
            "\"For what?\"\n\n",
            callback=self._act1_c_input
        )

    def _act1_c_input(self):
        self.get_input(f"{self.player_name}, what exactly are you straightening?",
                       self._act1_c_response)

    def _act1_c_response(self, answer):
        self.log(f'Straightener answer: "{answer}"', 'input')
        self.append_text(
            f"\nYou: \"{answer}\"\n\n"
            "Victor considers this for a very long moment.\n\n"
            "\"Interesting,\" he says.\n\n"
            "Another pause.\n\n"
            "\"The fog,\" he continues, as though the exchange never happened, "
            "\"is quite thick tonight. And the road closures —\"\n\n"
            "You look at the fog. The fog looks back.\n\n"
            "\"Alternatively,\" Victor says, \"I could show you to your room. "
            "Greta has made soup.\"\n\n"
            "Your stomach growls.\n\n"
            "\"...What kind of soup?\"\n\n"
            "\"Tomato. From scratch.\"\n\n"
            "You pick up your bag.\n",
            callback=lambda: self.show_choices([
                ('[A]  Fine. Just for tonight.', self._act1_c_stay),
                ("[B]  I'll take my chances with the fog.", self._act1_c_fog),
            ])
        )

    def _act1_c_fog(self):
        self.log('Tried to walk into the fog (the fog won)', 'choice')
        self.clear()
        self.type_text(
            "You walk into the fog.\n\n"
            "The fog is very thick.\n\n"
            "You walk in a circle for forty minutes and end up back at The Pines.\n\n"
            "Victor is still standing in the doorway. He hands you a bowl of soup "
            "without a word.\n\n"
            "You go inside.\n\n"
            "(The fog wins. It always wins.)\n",
            callback=self._act1_c_stay
        )

    def _act1_c_stay(self):
        self.path = 'escape'
        self.log('Accepted soup and went inside', 'choice')
        self.scene_act2_escape()

    # ── Act 2 ─────────────────────────────────────────────────────────────────

    def scene_act2_friendly(self):
        self.clear()
        self.type_text(
            "THE WISTERIA SUITE\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Victor shows you to Room 4. It smells like lavender and very faintly "
            "like a basement.\n\n"
            "There's a handwritten welcome card on the pillow:\n\n"
            "   \"Dear Guest, Welcome to The Pines. Turndown service is at 9pm.\n"
            "   Please do not open the door at the end of the hall.\n"
            "   Breakfast is at 8am. Eggs are excellent.\n"
            "   Warmly, The Staff\"\n\n"
            "A small ghost — translucent, about 5'2\", wearing a housekeeper's apron — "
            "phases through the wall, spots you, and screams.\n\n"
            "Then you scream.\n\n"
            "Then she composes herself and smooths her apron.\n\n"
            "\"Sorry, sorry. I'm Dot. I do the rooms. You're not supposed to be up "
            "here yet, I haven't done the mints.\" She looks genuinely distressed "
            "about the mints.\n\n"
            "What do you say?\n",
            callback=lambda: self.show_choices([
                ('[A]  "No worries, Dot. The room looks great."', self._f_a2_a),
                ('[B]  "...Are you a ghost?"',                    self._f_a2_b),
            ])
        )

    def _f_a2_a(self):
        self.log('Act 2 — The Wisteria Suite', 'scene')
        self.log('"No worries, Dot. The room looks great."', 'choice')
        self.clear()
        self.type_text(
            "Dot lights up — literally, she glows a little brighter.\n\n"
            "\"Oh! That's — thank you. I've been working on the hospital corners. "
            "Victor says they don't matter but they DO matter.\"\n\n"
            "She produces two foil-wrapped chocolates from her apron pocket and "
            "places them on the pillow with great ceremony.\n\n"
            "\"Dinner's in an hour. Greta's made her famous Wellington. Fair warning — "
            "she sheds a little when she's stressed. Just... don't mention it.\"\n\n"
            "She phases back through the wall. You hear her muffled voice:\n\n"
            "\"THEY SAID THE ROOM LOOKED GREAT, GRETA. I TOLD YOU THE CORNERS MATTERED.\"\n\n"
            "You feel weirdly at home.\n",
            callback=self.scene_act3
        )

    def _f_a2_b(self):
        self.log('Act 2 — The Wisteria Suite', 'scene')
        self.log('"...Are you a ghost?"', 'choice')
        self.clear()
        self.type_text(
            "Dot pauses.\n\n"
            "\"I prefer 'post-living,'\" she says with great dignity. \"But yes.\"\n\n"
            "She straightens her apron. \"I'm not going to rattle chains or moan or "
            "any of that. Victor tried it in 2003 and we got a very bad review.\" "
            "She shudders. \"Never again.\"\n\n"
            "\"So you're all... monsters?\"\n\n"
            "\"We prefer 'alternative lifeform hospitality staff.' But also yes.\" "
            "She gives you a look. \"Are you going to be a problem?\"\n",
            callback=lambda: self.show_choices([
                ('[A]  "Absolutely not. This is fine."',             self._f_a2_a),
                ('[B]  "I need to understand what\'s happening here."', self._shift_to_skeptic),
            ])
        )

    def _shift_to_skeptic(self):
        self.path = 'skeptic'
        self.log('"I need to understand what\'s happening here." → shifted to Skeptic path', 'choice')
        self.scene_act3()

    def scene_act2_skeptic(self):
        self.clear()
        self.type_text(
            "THE WISTERIA SUITE — NIGHT\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Your room is Room 4. You do a lap. Normal bed. Normal lamp. Window that "
            "overlooks a garden where something large is digging a hole at 9pm, "
            "which is less normal.\n\n"
            "The welcome card says not to open the door at the end of the hall.\n\n"
            "You open your notes app:\n"
            "  - Victor: no reflection\n"
            "  - Digging in garden: unknown\n"
            "  - Door at end of hall: suspicious\n"
            "  - Eggs: reportedly good\n\n"
            "A small translucent woman phases through your wall, sees you, screams, "
            "you both scream, and she introduces herself as Dot the housekeeper.\n\n"
            "\"Are you a ghost?\" you ask.\n\n"
            "\"I prefer post-living,\" she says. \"Are you going to be a problem?\"\n\n"
            "\"What's behind the door at the end of the hall?\"\n\n"
            "Dot's expression goes carefully neutral. \"Storage.\"\n\n"
            "\"What kind of storage?\"\n\n"
            "\"The... stored kind.\"\n\n"
            "What do you do?\n",
            callback=lambda: self.show_choices([
                ('[A]  Drop it for now. Go down to dinner and observe.',
                 self._s_a2_dinner),
                ('[B]  Wait for Dot to leave and immediately go check the door.',
                 self._s_a2_door),
            ])
        )

    def _s_a2_dinner(self):
        self.log('Act 2 — The Wisteria Suite (Skeptic)', 'scene')
        self.log('Dropped it for now. Went to dinner to observe.', 'choice')
        self.clear()
        self.type_text(
            "Smart. Gather more data first.\n\n"
            "You head downstairs. The dining room is candlelit — electric candles, "
            "you notice. Victor's compromise with modernity.\n\n"
            "Greta emerges from the kitchen. She's broad-shouldered, enthusiastic, "
            "and wearing a chef's hat over ears that are slightly too pointed to be human. "
            "She sets down a Beef Wellington with the reverence of someone presenting "
            "a sacred artifact.\n\n"
            "\"I made the pastry from scratch,\" she says. \"I want you to know that.\" "
            "She is making direct, intense eye contact.\n\n"
            "\"It looks incredible,\" you say.\n\n"
            "Greta exhales with her whole body. \"OKAY. Good. Great. Eat. Please.\"\n\n"
            "The food is genuinely exceptional. You're making notes between bites.\n",
            callback=self.scene_act3
        )

    def _s_a2_door(self):
        self.log('Act 2 — The Wisteria Suite (Skeptic)', 'scene')
        self.log('Immediately went to check the door at the end of the hall.', 'choice')
        self.clear()
        self.type_text(
            "The second Dot phases back through the wall you're in the hallway.\n\n"
            "The door at the end of the hall is old wood, slightly warped, with a "
            "brass handle shaped like a crescent moon.\n\n"
            "You try it. Locked.\n\n"
            "You pull out your library card and wiggle it in the gap —\n\n"
            "The door swings open.\n\n"
            "Inside is a small room, wallpapered in faded roses, containing:\n"
            "  - A mini fridge\n"
            "  - A beanbag chair\n"
            "  - A lava lamp\n"
            "  - Barry\n\n"
            "Barry is roughly seven feet tall, green-scaled, and currently watching "
            "a nature documentary on a small TV with the volume very low. "
            "He looks at you. You look at him.\n\n"
            "\"...This is my room,\" Barry says quietly.\n\n"
            "\"The card said storage.\"\n\n"
            "\"I asked them to put that. I'm private.\"\n\n"
            "An extremely long pause.\n\n"
            "\"Your documentary looks interesting,\" you try.\n\n"
            "Barry's expression shifts slightly. \"It's about tide pools.\"\n",
            callback=lambda: self.show_choices([
                ('[A]  Sit down. Watch the tide pool documentary with Barry.',
                 self._s_barry_doc),
                ('[B]  Apologize and back out of the room.',
                 self._s_a2_dinner),
            ])
        )

    def _s_barry_doc(self):
        self.log('Sat down and watched tide pool documentary with Barry.', 'choice')
        self.clear()
        self.type_text(
            "You sit on the floor — there's only one beanbag — and watch seventeen "
            "minutes of tide pool documentary in companionable silence.\n\n"
            "At one point a crab does something remarkable and you both lean "
            "forward slightly.\n\n"
            "\"That's a decorator crab,\" Barry says. \"They camouflage themselves "
            "with whatever's around. Shells, seaweed, debris.\"\n\n"
            "\"Smart,\" you say.\n\n"
            "\"Very,\" Barry agrees.\n\n"
            "Eventually Dot floats through the wall to tell you dinner's ready, "
            "with the air of someone who has seen stranger things and moved on.\n",
            callback=self.scene_act3
        )

    def scene_act2_escape(self):
        self.clear()
        self.type_text(
            "THE WISTERIA SUITE — ESCAPE PLAN\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Your room is fine. Normal, even. You've already scoped two exit routes — "
            "window to the porch roof, or straight back down the stairs if you're fast.\n\n"
            "A ghost comes through the wall, you both scream, she introduces herself as Dot.\n\n"
            "\"I'm going to be very upfront with you,\" you say. \"I'm planning to leave "
            "in the middle of the night.\"\n\n"
            "Dot stares at you.\n\n"
            "\"...Did you want me to pack you a snack for the road?\"\n\n"
            "\"Would you?\"\n\n"
            "\"We have leftover scones.\"\n\n"
            "You feel this is going better than expected.\n\n"
            "\"Why don't you just let me go?\" you ask. \"If I leave, no scene, "
            "everyone's happy.\"\n\n"
            "Dot sits on the edge of your bed — through it, technically. She sighs.\n\n"
            "\"Victor would never admit it,\" she says, \"but we really need a good review. "
            "The mortgage is — it's not great. And if you leave in the middle of the night "
            "that's a one-star automatic on HauntBnB.\" She looks at you with enormous "
            "sad eyes. \"Just stay through breakfast? The eggs are genuinely excellent.\"\n\n"
            "What do you do?\n",
            callback=lambda: self.show_choices([
                ("[A]  Fine. Breakfast. Then I'm gone.", self._e_a2_stay),
                ("[B]  I feel bad but I'm still leaving tonight.", self._e_a2_leave),
            ])
        )

    def _e_a2_leave(self):
        self.log('Act 2 — Escape Plan', 'scene')
        self.log('Decided to leave in the middle of the night.', 'choice')
        self.clear()
        self.type_text(
            "At 2am you ease your door open, tiptoe down the stairs —\n\n"
            "— and step directly onto Barry, who is asleep in the hallway.\n\n"
            "Barry wakes up. You flee. Barry, to his credit, doesn't chase you — "
            "he's not really a chaser. But in your panic you grab your bag and "
            "Victor's prized pocket watch off the hallway table, which you will not "
            "discover until you're already in your car with the engine running.\n",
            callback=self.ending_check_out_early
        )

    def _e_a2_stay(self):
        self.log('Act 2 — Escape Plan', 'scene')
        self.log('Agreed to stay through breakfast.', 'choice')
        self.scene_act3()

    # ── Act 3 — The Incident (convergence) ────────────────────────────────────

    def scene_act3(self):
        self.log('Act 3 — The Incident', 'scene')
        self.clear()
        self.type_text(
            "THE DINING ROOM — THE INCIDENT\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Dinner is going well. Or it was.\n\n"
            "Greta has just brought out dessert — a chocolate lava cake she is "
            "clearly very proud of — when there is a loud CRASH from the kitchen, "
            "followed by a series of smaller crashes, and then silence.\n\n"
            "Greta disappears through the kitchen door.\n\n"
            "Victor straightens in his chair. Dot flickers nervously.\n\n"
            "Greta reappears. Her chef's hat is askew. There is flour on her face. "
            "Her ears are now fully, unmistakably wolf ears.\n\n"
            "\"Everything is fine,\" she says.\n\n"
            "\"What happened?\" you ask.\n\n"
            "\"Barry dropped the flan. But it's fine. I have backup flan.\"\n\n"
            "Barry's enormous head appears in the kitchen doorway. He looks at you.\n\n"
            "Victor is watching you very carefully.\n\n"
            "This is the moment. The whole staff is holding their breath.\n",
            callback=self._act3_choices
        )

    def _act3_choices(self):
        if self.path == 'friendly':
            self.show_choices([
                ('[A]  "Is there enough backup flan for everyone? Barry should come sit with us."',
                 self.scene_act4_friendly),
            ])
        elif self.path == 'skeptic':
            self.show_choices([
                ('[A]  "Okay I have about fifteen questions but they can wait. Is the flan okay?"',
                 self.scene_act4_skeptic),
            ])
        else:
            self.show_choices([
                ('[A]  "...Do you want help cleaning up?"',
                 self.scene_act4_escape),
            ])

    # ── Act 4 ─────────────────────────────────────────────────────────────────

    def scene_act4_friendly(self):
        self.log('"Barry should come sit with us."', 'choice')
        self.log('Act 4 — The Staff Open Up', 'scene')
        self.clear()
        self.type_text(
            "Barry comes and sits at the table. He has to angle slightly sideways "
            "to fit. Dot hovers nearby. Victor pours wine — his glass appears to "
            "have something other than wine in it and no one comments.\n\n"
            "They're all watching you with this cautious, hopeful energy.\n\n"
            "\"So,\" you say. \"How long have you all been running this place?\"\n\n"
            "And they start talking.\n\n"
            "Victor bought The Pines in 1987. Greta joined in 1993. Dot has been here "
            "since the 1940s and sort of came with the building. Barry wandered up from "
            "the creek in 2001 and never left.\n\n"
            "\"The reviews used to be good,\" Dot says wistfully. \"In the 90s. Before "
            "everything went online and everyone started taking photos.\"\n\n"
            "\"Victor kept flying dramatically at people,\" Greta says.\n\n"
            "\"It was ATMOSPHERIC,\" Victor says.\n\n"
            "\"A man fainted. Twice.\"\n\n"
            "\"He came BACK, didn't he? Second visit.\"\n\n"
            "You are genuinely charmed. But you also notice: the heating keeps going "
            "out, one of the porch rails is rotting, and Victor's HauntBnB app shows "
            "2.1 stars. The most recent review reads simply: \"vibes off.\"\n\n"
            "You have an idea.\n",
            callback=lambda: self.show_choices([
                ('[A]  Offer to help them stage a better HauntBnB listing.',
                 self.ending_five_stars),
                ('[B]  Offer to spend tomorrow helping fix the place up.',
                 self.ending_five_stars),
            ])
        )

    def scene_act4_skeptic(self):
        self.log('"I have fifteen questions. Is the flan okay?"', 'choice')
        self.log('Act 4 — Confronting Victor', 'scene')
        self.clear()
        self.type_text(
            "Greta exhales. Barry retreats slightly but doesn't disappear.\n\n"
            "\"Victor,\" you say, setting down your fork. \"I'm going to be honest. "
            "I've been taking notes all evening. I know you don't have a reflection. "
            "I know Greta is a werewolf. I know Dot is a ghost. I have reasonable "
            "theories about Barry.\"\n\n"
            "A silence.\n\n"
            "\"I'm not going to do anything with this information. I'm just — "
            "I need to know what's behind the wallpaper in Room 7.\"\n\n"
            "\"How did you know about Room 7?\" Dot whispers.\n\n"
            "\"The wallpaper pattern is slightly different and there's a cold spot.\"\n\n"
            "Victor and Greta exchange a look.\n\n"
            "\"They're good,\" Greta says.\n\n"
            "\"They're a liability,\" Victor says.\n\n"
            "He turns to you. His expression is unreadable.\n\n"
            "\"And why,\" he says carefully, \"should I tell you that?\"\n\n",
            callback=self._s_victor_input
        )

    def _s_victor_input(self):
        self.get_input("What do you say to Victor?", self._s_victor_respond)

    def _s_victor_respond(self, answer):
        self.log(f'Said to Victor: "{answer}"', 'input')
        self.append_text(
            f"\nYou: \"{answer}\"\n\n",
            callback=lambda: self._s_victor_react(answer.lower())
        )

    def _s_victor_react(self, answer_lower):
        kind = ['promise', 'trust', 'curious', 'interesting', 'no harm', 'mean well',
                "won't tell", 'safe', 'please', 'fascinated', 'understand',
                'appreciate', 'honest', 'respect', 'just want']
        opens_up = any(w in answer_lower for w in kind)

        if opens_up:
            self.type_text(
                "Victor is quiet for a moment. Then, slowly, he sets down his glass.\n\n"
                "\"...Fair enough,\" he says. Which, from Victor, is practically "
                "a standing ovation.\n\n"
                "\"Room 7 contains a door that should not be opened.\"\n\n"
                "\"What's behind it?\"\n\n"
                "\"We don't know. It was here when I bought the house. The wallpaper "
                "was Dot's idea. We have all agreed not to think about it too hard.\"\n\n"
                "You write this down.\n\n"
                "\"And you've just... lived with a mysterious door for 35 years.\"\n\n"
                "\"It hasn't bothered us,\" Victor says defensively. "
                "\"It only rattles on the equinox.\"\n\n"
                "\"It's rattling right now,\" Dot says quietly.\n\n"
                "Everyone looks at the ceiling.\n\n"
                "It is rattling right now.\n",
                callback=self.scene_room7
            )
        else:
            self.type_text(
                "Victor straightens in his chair.\n\n"
                "\"I don't think so,\" he says simply.\n\n"
                "You hold eye contact. He does not blink. You remember, distantly, "
                "that he probably doesn't have to.\n\n"
                "You back down. For now.\n\n"
                "─  ─  ─\n\n"
                "At 3am you are in the hallway outside Room 7 with your phone "
                "flashlight and your library card.\n\n"
                "The door takes thirty seconds. Inside is another door — old, old wood, "
                "with no handle.\n\n"
                "You put your hand on it. It's warm.\n\n"
                "Something knocks from the other side. Three times. Polite, almost.\n",
                callback=self.scene_knock_minigame
            )

    def scene_act4_escape(self):
        self.log('"Do you want help cleaning up?"', 'choice')
        self.log('Act 4 — Kitchen Scene', 'scene')
        self.clear()
        self.type_text(
            "You help Greta clean up the kitchen. Barry washes dishes with surprising "
            "delicacy for someone with hands the size of dinner plates.\n\n"
            "\"You're still planning to leave,\" Greta says. Not accusing. Just observing.\n\n"
            "\"In the morning. After breakfast. I promised Dot.\"\n\n"
            "Greta nods. She hands you a dish towel.\n\n"
            "\"Can I ask you something?\" you say.\n\n"
            "\"Sure.\"\n\n"
            "\"Why do you all stay? You could go anywhere.\"\n\n"
            "Greta is quiet for a moment, scrubbing a pot.\n\n"
            "\"Victor bought this place because he wanted somewhere that was his,\" "
            "she says finally. \"He's been alive for 400 years and he'd never had a home. "
            "Just... somewhere that was his.\" She shrugs, a big wolfy shrug. "
            "\"And then it sort of became ours.\"\n\n"
            "Barry makes a small sound that might be agreement.\n\n"
            "You feel the scones in your future, and your car keys in your pocket, "
            "and something uncomfortable happening in your chest.\n",
            callback=lambda: self.show_choices([
                ('[A]  "Do you actually want me to leave? Or do you want a good review?"',
                 self._e_a4_stay),
                ('[B]  Finish the dishes quietly. Stick to the plan.',
                 self.ending_check_out_early),
            ])
        )

    def _e_a4_stay(self):
        self.path = 'friendly'
        self.log('"Do you actually want me to leave?" → stayed for the weekend', 'choice')
        self.clear()
        self.type_text(
            "Greta stops scrubbing. Barry sets down a dish.\n\n"
            "\"Both,\" Greta says honestly. \"But mostly — we just wanted someone "
            "to have a nice time here. For once.\"\n\n"
            "She sounds tired in a way that has nothing to do with the dishes.\n\n"
            "You look around the kitchen. At Greta's meticulously organized spice rack. "
            "At Barry carefully drying a wine glass with a tea towel three sizes too "
            "small for his hands. At Dot's handwritten cleaning schedule on the wall, "
            "every box ticked.\n\n"
            "They're really trying.\n\n"
            "\"Okay,\" you say. \"I'll stay through the weekend.\"\n\n"
            "Greta looks up.\n\n"
            "\"I might have some ideas for the listing,\" you add. \"If you want.\"\n\n"
            "Barry puts the wine glass down very carefully and makes a small sound.\n\n"
            "\"That's a yes,\" Greta translates.\n\n"
            "(Victor is suspicious of your change of heart for approximately one hour. "
            "Then Dot tells him to be grateful and he is.)\n",
            callback=self.ending_five_stars
        )

    # ── Room 7 ────────────────────────────────────────────────────────────────

    def scene_room7(self):
        self.log('Act 4 — Room 7, 3am', 'scene')
        self.clear()
        self.type_text(
            "ROOM 7 — 3AM\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "You stand outside the wallpapered door.\n\n"
            "You put your hand on it. It's warm.\n\n"
            "Something knocks from the other side. Three times. Polite, almost.\n\n"
            "You stand there for a long moment.\n",
            callback=lambda: self.show_choices([
                ('[A]  Knock back.',
                 self.scene_knock_minigame),
                ('[B]  Close Room 7 and go back to bed. Some things are better unknown.',
                 self._room7_retreat),
            ])
        )

    def _room7_retreat(self):
        self.log('Chose not to knock... then knocked anyway at 5am.', 'choice')
        self.clear()
        self.type_text(
            "You close the door.\n\n"
            "You go back to bed.\n\n"
            "You lie there staring at the ceiling for two hours.\n\n"
            "At 5am you get up, go back to Room 7, and knock anyway.\n\n"
            "Some things are better unknown. You know this.\n\n"
            "You knock anyway.\n",
            callback=self.scene_knock_minigame
        )

    # ── Knock mini-game scene ─────────────────────────────────────────────────

    def scene_knock_minigame(self):
        self.log('Knocked back on the door.', 'choice')
        self.clear()
        self.type_text(
            "You raise your fist.\n\nKnock back.\n",
            callback=lambda: self.knock_minigame(self._after_knocks)
        )

    def _after_knocks(self):
        play_sound(CREAK_WAV)
        self.type_text(
            "\nSilence.\n\n"
            "Then, from the other side of the door — five knocks back.\n\n"
            "Measured. Deliberate. Exactly matching your rhythm.\n\n"
            "The door swings open.\n",
            callback=self.scene_barry_room
        )

    def scene_barry_room(self):
        self.clear()
        self.type_text(
            "BARRY'S QUIET ROOM\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Barry is standing in the doorway, fist still raised mid-knock.\n\n"
            "You stare at him.\n\n"
            "He stares at you.\n\n"
            "\"...That was you,\" you say.\n\n"
            "\"That was me,\" he confirms.\n\n"
            "\"This whole time. You've been behind the door.\"\n\n"
            "\"I like the quiet room,\" he says. \"No one bothers me here. "
            "Victor thinks it's mysterious so he keeps everyone away.\" "
            "A pause. \"It works very well.\"\n\n"
            "You look past him into the warm wood-paneled room — the fireplace, "
            "the armchairs, the impossible window overlooking a garden that "
            "doesn't exist.\n\n"
            "\"Barry,\" you say slowly. \"Is this room the reason guests never come back?\"\n\n"
            "Barry is quiet for a moment.\n\n"
            "\"Some of them stay too long,\" he says carefully. \"The room is... "
            "comfortable. Some people sit down and don't want to leave.\"\n\n"
            "You look at the armchairs. They do look very comfortable.\n\n"
            "\"But you'd tell me if I was in danger,\" you say.\n\n"
            "Barry considers this with great seriousness.\n\n"
            "\"I would,\" he says. \"I don't like when people get hurt. "
            "I just like tide pools and quiet rooms.\"\n\n"
            "He steps aside.\n\n"
            "\"You can come in,\" he says. \"I'll make sure you can leave.\"\n\n"
            "You sit down in one of the armchairs.\n\n"
            "You look out the impossible window.\n",
            callback=self.ending_permanent_guest
        )

    # =========================================================================
    # ENDINGS
    # =========================================================================

    def ending_five_stars(self):
        self.log('ENDING: Five Stars ⭐⭐⭐⭐⭐', 'scene')
        self.clear()
        self.type_text(
            "ENDING 1: FIVE STARS\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "You spend Saturday helping.\n\n"
            "Greta teaches you her Wellington recipe. You help Victor practice a "
            "welcome that doesn't make guests feel like they've fulfilled a prophecy.\n\n"
            "\"Try 'lovely to meet you' instead of 'you CAME.'\"\n\n"
            "\"But you DID come —\"\n\n"
            "\"Victor.\"\n\n"
            "\"...Lovely to meet you.\"\n\n"
            "Dot nearly cries, which means she glows bright enough to read by.\n\n"
            "Barry re-stains the porch rail. You take photos — good ones, with natural "
            "light that make the house look like a charming eccentric getaway.\n\n"
            "Sunday morning arrives. Your bag is packed. The eggs were, as promised, "
            "genuinely excellent.\n\n"
            "Victor sees you to the door, trying very hard not to be dramatic about it "
            "and only partially succeeding.\n\n"
            "\"You'll write the review,\" he says. Not quite a question.\n\n"
            "\"Already typed it in the car,\" you say.\n\n"
            "─  ─  ─\n\n"
            f"{self.player_name}'s HauntBnB Review — The Pines  ★★★★★\n\n"
            "\"Genuinely the best weekend I've had in years. The food alone is worth "
            "the trip — ask Greta about the Wellington. The staff are attentive, "
            "deeply earnest, and occasionally luminous. Victor is a lot, but in the "
            "best way. Bring an open mind and don't worry about the door in Room 7.\n\n"
            "Would absolutely return.\"\n\n"
            "─  ─  ─\n\n"
            "Victor reads it on his phone in the driveway.\n\n"
            "\"I am not 'a lot.'\"\n\n"
            "\"Victor.\"\n\n"
            f"\"...Thank you, {self.player_name}.\"\n\n"
            "You drive away. Three hours later your phone buzzes.\n\n"
            "The Pines now has a 4.8 rating.\n\n"
            "Victor has texted you a single bat emoji.\n\n"
            "You text back a house emoji.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "         THE END — \"Five Stars\"\n\n"
            "  You didn't just survive the weekend.\n"
            "           You saved the inn.\n"
            "      Not bad for $12 a night.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
            callback=lambda: self._show_ending_summary(1, 'Five Stars', 'Friendly')
        )

    def ending_check_out_early(self):
        self.log('ENDING: Check Out Early 🏃', 'scene')
        self.clear()
        self.type_text(
            "ENDING 2: CHECK OUT EARLY\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "You are three miles down the road when you reach into your jacket "
            "and your hand closes around something cool and metallic.\n\n"
            "A pocket watch.\n\n"
            "Gold. Antique. Engraved on the back with a V in an ornate script.\n\n"
            "\"Oh no,\" you say.\n\n"
            "Your rearview mirror shows the road behind you.\n\n"
            "Then it shows Victor.\n\n"
            "Victor is running. In his waistcoat. At a genuinely impressive speed. "
            "Greta is beside him on all fours, which explains the speed. "
            "Dot is somehow ahead of both of them despite not technically having legs. "
            "Barry is bringing up the rear with the focused energy of someone who "
            "does not run often but, when he does, is committed.\n\n"
            "You hit the gas.\n\n"
            "What follows is the single most chaotic fifteen minutes of your life: "
            "three miles of winding road, one wrong turn into a pumpkin patch, "
            "a brief détente at a 24-hour diner where everyone orders coffee and "
            "stares at each other, and a negotiation conducted in whispers while "
            "a trucker at the counter tries very hard to pretend he's not hearing "
            "any of it.\n\n"
            "You give back the watch.\n\n"
            "Victor holds it to his chest and exhales for approximately eight seconds.\n\n"
            "\"It was my mother's,\" he says.\n\n"
            "\"I didn't mean to take it.\"\n\n"
            "\"I know.\" A pause. \"...Your driving is very aggressive.\"\n\n"
            "\"You were CHASING me.\"\n\n"
            "\"We were RETRIEVING the watch.\"\n\n"
            "Greta is eating an entire plate of pancakes. She points at you with her fork. "
            "\"You're a fast driver,\" she says, with what sounds like genuine admiration.\n\n"
            "An hour later you are back on the road. For real this time, "
            "with Victor's blessing and a bag of scones for the drive.\n\n"
            "─  ─  ─\n\n"
            f"{self.player_name}'s HauntBnB Review — The Pines  ★★★\n\n"
            "\"Chaotic. Unprecedented. The staff chased my car.\n"
            "But the scones were incredible and I think we're friends now?\n"
            "Do not steal the pocket watch.\"\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "       THE END — \"Check Out Early\"\n\n"
            "  You escaped. Technically. With new friends\n"
            "           and a very good story.\n"
            "     The road is yours. Drive safe.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
            callback=lambda: self._show_ending_summary(2, 'Check Out Early', 'Escape')
        )

    def ending_permanent_guest(self):
        self.log('ENDING: Permanent Guest 👻', 'scene')
        self.clear()
        self.type_text(
            "ENDING 3: PERMANENT GUEST\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Some time passes. It's hard to say how much.\n\n"
            "When you stand up and reach for the wall, your hand goes through it.\n\n"
            "You look down at yourself.\n\n"
            "\"Huh,\" you say.\n\n"
            "You walk through the wall. You are in the hallway of The Pines, "
            "outside Room 7. The wallpaper is back. The door is sealed.\n\n"
            "Dot is standing at the end of the hall. She stares at you. "
            "Then she puts her face in her hands.\n\n"
            "\"VICTOR,\" she calls downstairs. \"WE HAVE ANOTHER ONE.\"\n\n"
            "Victor appears at the bottom of the stairs, looks up at you, "
            "and sighs the sigh of a man who has had this happen before.\n\n"
            "\"Well,\" he says. \"You'll need an apron.\"\n\n"
            "─  ─  ─\n\n"
            f"You've been at The Pines for three weeks now. You handle the morning "
            "shift with Dot. You have mastered the hospital corners. "
            "Barry lent you a tide pool documentary.\n\n"
            "Your notes app still works, somehow:\n"
            "  - Victor: no reflection, soft underneath\n"
            "  - Greta: best chef you've ever met, sheds in autumn\n"
            "  - Dot: right about the corners\n"
            "  - Barry: quiet, good taste in documentaries\n"
            "  - Me: post-living, apparently\n"
            "  - The door in Room 7: do NOT knock back\n\n"
            "You update the HauntBnB listing:\n\n"
            "\"Cozy Victorian B&B with exceptional food and a uniquely dedicated staff. "
            "The Wisteria Suite has lovely corners. Guests are encouraged to avoid "
            "Room 7. We cannot stress this enough.\"\n\n"
            "The Pines gets three bookings that week.\n\n"
            "Victor doesn't know whether to be grateful or suspicious.\n\n"
            "Dot says: both.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "      THE END — \"Permanent Guest\"\n\n"
            "   You came for a weekend.\n"
            "   You found something that felt like home.\n"
            "   (Technically you are now part of the building.\n"
            "    But still.)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
            callback=lambda: self._show_ending_summary(3, 'Permanent Guest', 'Skeptic')
        )

    # ── Play again ────────────────────────────────────────────────────────────

    def _show_ending_summary(self, number, title, path):
        summary = (
            f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  Ending {number} of 3 — {path} Path\n"
            f"  \"{title}\"\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        self.log(f'You achieved Ending {number}/3 — {path} Path: "{title}"', 'scene')
        self.text_widget.config(state='normal')
        self.text_widget.insert('end', summary)
        self.text_widget.see('end')
        self.text_widget.config(state='disabled')
        self._play_again()

    def _play_again(self):
        self.show_choices([
            ('Play again', self._restart),
            ('Quit',       self.root.destroy),
        ])

    def _restart(self):
        self.player_name = ''
        self.path = None
        if self._history_win:
            self._history_text.config(state='normal')
            self._history_text.delete('1.0', 'end')
            self._history_text.config(state='disabled')
        self.log('── New Run ──────────────────', 'scene')
        self.scene_intro()


if __name__ == '__main__':
    Game()
