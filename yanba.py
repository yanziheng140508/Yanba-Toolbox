# -*- coding: utf-8 -*-
"""
闫巴工具箱 YBv1.0 — 现代动画版
纯本地运行 · 全局异常保护 · JSON持久化 · 平滑交互动画
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import json
import os
import sys
import random
import datetime
import traceback


class Theme:
    BG = '#F0F2F5'
    CARD = '#FFFFFF'
    PRIMARY = '#3F51B5'
    PRIMARY_DARK = '#303F9F'
    ACCENT = '#FF7043'
    SUCCESS = '#66BB6A'
    WARNING = '#FFA726'
    DANGER = '#EF5350'
    TEXT = '#212121'
    TEXT_SECONDARY = '#757575'
    TEXT_MUTED = '#BDBDBD'
    BORDER = '#E0E0E0'

    NAV_BG = '#263238'
    NAV_BACK_FG = '#ECEFF1'
    NAV_BACK_HOVER_FG = '#4FC3F7'
    NAV_BACK_HOVER_BG = '#1E272C'
    NAV_TITLE_FG = '#FFFFFF'

    FONT_TITLE = ('Microsoft YaHei', 22, 'bold')
    FONT_HEADER = ('Microsoft YaHei', 16, 'bold')
    FONT_BODY = ('Microsoft YaHei', 11)
    FONT_BODY_BOLD = ('Microsoft YaHei', 11, 'bold')
    FONT_SMALL = ('Microsoft YaHei', 9)
    FONT_NUM = ('Consolas', 42, 'bold')
    FONT_BTN = ('Microsoft YaHei', 11, 'bold')

    DARK = {
        'BG': '#1A1A2E',
        'CARD': '#252538',
        'PRIMARY': '#7986CB',
        'PRIMARY_DARK': '#5C6BC0',
        'ACCENT': '#FF8A65',
        'SUCCESS': '#81C784',
        'WARNING': '#FFB74D',
        'DANGER': '#EF5350',
        'TEXT': '#E8E8F0',
        'TEXT_SECONDARY': '#9E9EB8',
        'TEXT_MUTED': '#5C5C78',
        'BORDER': '#3A3A52',
        'NAV_BG': '#1A1A2E',
        'NAV_BACK_FG': '#B0B0C8',
        'NAV_BACK_HOVER_FG': '#64B5F6',
        'NAV_BACK_HOVER_BG': '#252538',
        'NAV_TITLE_FG': '#E8E8F0',
        'NOTE_DEFAULT': '#3D3D5C',
    }

    @classmethod
    def set_dark(cls):
        cls.BG = cls.DARK['BG']
        cls.CARD = cls.DARK['CARD']
        cls.PRIMARY = cls.DARK['PRIMARY']
        cls.PRIMARY_DARK = cls.DARK['PRIMARY_DARK']
        cls.ACCENT = cls.DARK['ACCENT']
        cls.SUCCESS = cls.DARK['SUCCESS']
        cls.WARNING = cls.DARK['WARNING']
        cls.DANGER = cls.DARK['DANGER']
        cls.TEXT = cls.DARK['TEXT']
        cls.TEXT_SECONDARY = cls.DARK['TEXT_SECONDARY']
        cls.TEXT_MUTED = cls.DARK['TEXT_MUTED']
        cls.BORDER = cls.DARK['BORDER']
        cls.NAV_BG = cls.DARK['NAV_BG']
        cls.NAV_BACK_FG = cls.DARK['NAV_BACK_FG']
        cls.NAV_BACK_HOVER_FG = cls.DARK['NAV_BACK_HOVER_FG']
        cls.NAV_BACK_HOVER_BG = cls.DARK['NAV_BACK_HOVER_BG']
        cls.NAV_TITLE_FG = cls.DARK['NAV_TITLE_FG']

    @classmethod
    def set_light(cls):
        cls.BG = '#F0F2F5'
        cls.CARD = '#FFFFFF'
        cls.PRIMARY = '#3F51B5'
        cls.PRIMARY_DARK = '#303F9F'
        cls.ACCENT = '#FF7043'
        cls.SUCCESS = '#66BB6A'
        cls.WARNING = '#FFA726'
        cls.DANGER = '#EF5350'
        cls.TEXT = '#212121'
        cls.TEXT_SECONDARY = '#757575'
        cls.TEXT_MUTED = '#BDBDBD'
        cls.BORDER = '#E0E0E0'
        cls.NAV_BG = '#263238'
        cls.NAV_BACK_FG = '#ECEFF1'
        cls.NAV_BACK_HOVER_FG = '#4FC3F7'
        cls.NAV_BACK_HOVER_BG = '#1E272C'
        cls.NAV_TITLE_FG = '#FFFFFF'


class AnimationEngine:
    @staticmethod
    def fade_in(widget, duration=400, callback=None):
        try:
            widget.update_idletasks()
            w = widget.winfo_width() or 400
            h = widget.winfo_height() or 400
            cx = widget.winfo_rootx() + w // 2
            cy = widget.winfo_rooty() + h // 2
            overlay = tk.Toplevel(widget)
            overlay.overrideredirect(True)
            overlay.attributes('-topmost', True)
            overlay.configure(bg=Theme.BG)
            overlay.geometry(f'{w}x{h}+{cx - w // 2}+{cy - h // 2}')
            overlay.lower()
            steps = 12
            alpha = [0.0]

            def _step():
                alpha[0] += 1.0 / steps
                if alpha[0] >= 1.0:
                    overlay.destroy()
                    if callback:
                        callback()
                    return
                try:
                    overlay.attributes('-alpha', min(alpha[0], 1.0))
                    widget.after(duration // steps, _step)
                except Exception:
                    overlay.destroy()
                    if callback:
                        callback()
            overlay.attributes('-alpha', 0.0)
            widget.after(1, _step)
        except Exception:
            if callback:
                callback()

    @staticmethod
    def animate_popup(window, duration=250):
        try:
            window.update_idletasks()
            w = window.winfo_width()
            h = window.winfo_height()
            x = window.winfo_x()
            y = window.winfo_y()
            cx, cy = x + w // 2, y + h // 2
            steps = 10
            scale = [0.3]

            def _step():
                scale[0] += (1.0 - scale[0]) * 0.25
                s = scale[0]
                cw, ch = int(w * s), int(h * s)
                window.geometry(f'{cw}x{ch}+{cx - cw // 2}+{cy - ch // 2}')
                if s < 0.98:
                    window.after(duration // steps, _step)
                else:
                    window.geometry(f'{w}x{h}+{x}+{y}')
            window.geometry(f'{int(w * 0.3)}x{int(h * 0.3)}+'
                            f'{cx - int(w * 0.3) // 2}+{cy - int(h * 0.3) // 2}')
            window.after(10, _step)
        except Exception:
            pass

    @staticmethod
    def roll_number(label, from_text, to_text, duration=300):
        try:
            steps = 6
            cur = [0]

            def _step():
                cur[0] += 1
                if cur[0] >= steps:
                    label.config(text=to_text)
                    return
                chars = []
                for fc, tc in zip(from_text, to_text):
                    chars.append(fc if fc == tc else random.choice('0123456789:'))
                label.config(text=''.join(chars))
                label.after(duration // steps, _step)
            label.config(text=from_text)
            label.after(20, _step)
        except Exception:
            label.config(text=to_text)

    @staticmethod
    def glow_label(label, color, times=3):
        try:
            orig = label.cget('fg')
            cnt = [0]

            def _blink():
                cnt[0] += 1
                if cnt[0] >= times * 2:
                    label.config(fg=orig)
                    return
                label.config(fg='#FFFFFF' if cnt[0] % 2 == 0 else color)
                label.after(150, _blink)
            _blink()
        except Exception:
            pass

    @staticmethod
    def bounce_widget(widget, times=2, amplitude=8):
        try:
            if widget.place_info():
                orig_y = float(widget.place_info().get('y', 0))
            else:
                orig_y = widget.winfo_y()
            f = [0]
            d = [1]

            def _step():
                f[0] += 1
                if d[0] == 1:
                    off = -amplitude * (1 - f[0] / (times * 4))
                    if f[0] >= times * 2:
                        d[0] = -1
                        f[0] = 0
                else:
                    off = amplitude * (f[0] / (times * 4))
                    if f[0] >= times * 2:
                        if widget.place_info():
                            widget.place(y=orig_y)
                        return
                if widget.place_info():
                    widget.place(y=orig_y + off)
                widget.after(25, _step)
            _step()
        except Exception:
            pass


class DataManager:
    APP_DIR = None

    @classmethod
    def init_app_dir(cls):
        try:
            if getattr(sys, 'frozen', False):
                base = os.path.dirname(sys.executable)
            else:
                base = os.path.dirname(os.path.abspath(__file__))
            cls.APP_DIR = os.path.join(base, 'yanba_data')
            os.makedirs(cls.APP_DIR, exist_ok=True)
        except Exception:
            cls.APP_DIR = os.path.join(os.path.expanduser('~'), '.yanba_data')
            os.makedirs(cls.APP_DIR, exist_ok=True)

    @classmethod
    def _file(cls, name):
        if cls.APP_DIR is None:
            cls.init_app_dir()
        return os.path.join(cls.APP_DIR, name)

    @classmethod
    def load(cls, name, default=None):
        if default is None:
            default = {}
        try:
            fp = cls._file(name)
            if os.path.exists(fp):
                with open(fp, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return default

    @classmethod
    def save(cls, name, data):
        try:
            fp = cls._file(name)
            with open(fp, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False


class RoundedButton(tk.Canvas):
    def __init__(self, master, text='', command=None, bg=Theme.PRIMARY,
                 fg='white', width=120, height=40, radius=18, **kwargs):
        super().__init__(master, width=width, height=height,
                         highlightthickness=0, bg=master['bg'], **kwargs)
        self._text = text
        self._command = command
        self._bg = bg
        self._fg = fg
        self._width = width
        self._height = height
        self._radius = radius
        self._hover = False
        self._draw(bg)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)

    def _draw(self, color):
        self.delete('all')
        r, w, h = self._radius, self._width, self._height
        self.create_oval(0, 0, 2*r, 2*r, fill=color, outline='')
        self.create_oval(w-2*r, 0, w, 2*r, fill=color, outline='')
        self.create_oval(0, h-2*r, 2*r, h, fill=color, outline='')
        self.create_oval(w-2*r, h-2*r, w, h, fill=color, outline='')
        self.create_rectangle(r, 0, w-r, h, fill=color, outline='')
        self.create_rectangle(0, r, w, h-r, fill=color, outline='')
        self.create_text(w//2, h//2, text=self._text,
                         fill=self._fg, font=Theme.FONT_BTN)

    def _on_enter(self, event):
        self._hover = True
        self._anim(self._bg, self._lighten(self._bg))

    def _on_leave(self, event):
        self._hover = False
        self._anim(self._lighten(self._bg), self._bg)

    def _anim(self, c1, c2):
        steps, s = 8, [0]
        def _step():
            s[0] += 1
            t = s[0] / steps
            self._draw(self._mix(c1, c2, t))
            if s[0] < steps and self._hover:
                self.after(10, _step)
        _step()

    def _on_click(self, event):
        if self._command:
            self._command()

    @staticmethod
    def _lighten(c):
        try:
            r = min(255, int(c[1:3], 16) + 25)
            g = min(255, int(c[3:5], 16) + 25)
            b = min(255, int(c[5:7], 16) + 25)
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            return c

    @staticmethod
    def _mix(c1, c2, t):
        try:
            r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
            r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            return c2


class RoundedFrame(tk.Canvas):
    def __init__(self, master, bg=None, radius=18, **kwargs):
        self._bg = bg or Theme.CARD
        self._radius = radius
        self._items = []
        super().__init__(master, bg=self._bg, highlightthickness=0, bd=0, **kwargs)
        self.bind('<Configure>', self._on_resize)
        self._draw()

    def _draw(self):
        self.delete('all')
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            self.after(50, self._draw)
            return
        r = self._radius
        self.create_oval(0, 0, 2*r, 2*r, fill=self._bg, outline='')
        self.create_oval(w-2*r, 0, w, 2*r, fill=self._bg, outline='')
        self.create_oval(0, h-2*r, 2*r, h, fill=self._bg, outline='')
        self.create_oval(w-2*r, h-2*r, w, h, fill=self._bg, outline='')
        self.create_rectangle(r, 0, w-r, h, fill=self._bg, outline='')
        self.create_rectangle(0, r, w, h-r, fill=self._bg, outline='')

    def _on_resize(self, event):
        self._draw()

    def set_bg(self, color):
        self._bg = color
        self._draw()


class RoundedEntry(tk.Frame):
    def __init__(self, master, bg=None, fg=None, radius=15, **kwargs):
        self._bg = bg or Theme.CARD
        self._radius = radius
        self._canvas = tk.Canvas(master, bg=master['bg'], highlightthickness=0, bd=0)
        self._canvas.pack(side='left', fill='both', expand=True)
        self._canvas.bind('<Configure>', self._on_resize)
        self._entry = tk.Entry(self._canvas, bg=self._bg, fg=fg or Theme.TEXT,
                               bd=0, highlightthickness=0, insertbackground=Theme.TEXT,
                               font=Theme.FONT_BODY, **kwargs)
        self._entry.place(relx=0.5, rely=0.5, anchor='center')
        self._draw()

    def _draw(self):
        self._canvas.delete('all')
        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()
        if w < 10 or h < 10:
            self._canvas.after(50, self._draw)
            return
        r = self._radius
        self._canvas.create_oval(0, 0, 2*r, 2*r, fill=self._bg, outline='')
        self._canvas.create_oval(w-2*r, 0, w, 2*r, fill=self._bg, outline='')
        self._canvas.create_oval(0, h-2*r, 2*r, h, fill=self._bg, outline='')
        self._canvas.create_oval(w-2*r, h-2*r, w, h, fill=self._bg, outline='')
        self._canvas.create_rectangle(r, 0, w-r, h, fill=self._bg, outline='')
        self._canvas.create_rectangle(0, r, w, h-r, fill=self._bg, outline='')
        self._entry.place_configure(width=w-14, height=h-6)

    def _on_resize(self, event):
        self._draw()

    def get(self):
        return self._entry.get()

    def set(self, text):
        self._entry.delete(0, 'end')
        self._entry.insert(0, text)

    def config(self, **kwargs):
        if 'bg' in kwargs:
            self._bg = kwargs['bg']
            self._entry.configure(bg=self._bg)
            self._canvas.configure(bg=self._bg)
            self._draw()

    def bind(self, *args, **kwargs):
        return self._entry.bind(*args, **kwargs)


class DeciderPage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=Theme.BG, **kwargs)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        tk.Label(self, text="🎲 随机决定器", font=Theme.FONT_HEADER,
                 bg=Theme.BG, fg=Theme.TEXT).pack(pady=(10, 5))
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=15, pady=5)
        for cls_fn, title in [
            (self._build_custom, '  自定义选项  '),
            (self._build_lots, '  抽签  '),
            (self._build_coin, '  抛硬币  '),
        ]:
            tab = tk.Frame(nb, bg=Theme.CARD)
            nb.add(tab, text=title)
            cls_fn(tab)

    def _build_custom(self, parent):
        tk.Label(parent, text="选项列表", font=Theme.FONT_BODY,
                 bg=Theme.CARD, fg=Theme.TEXT_SECONDARY).pack(anchor='w', padx=15, pady=(12, 3))

        scroll_wrap = tk.Frame(parent, bg=Theme.CARD)
        scroll_wrap.pack(fill='both', expand=True, padx=15, pady=(0, 5))
        canvas = tk.Canvas(scroll_wrap, bg=Theme.CARD, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(scroll_wrap, orient='vertical', command=canvas.yview)
        self.custom_inner = tk.Frame(canvas, bg=Theme.CARD)
        self.custom_inner.bind('<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.custom_inner, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self._custom_canvas = canvas
        self.option_entries = []

        add_frame = tk.Frame(parent, bg=Theme.CARD)
        add_frame.pack(fill='x', padx=15, pady=(2, 0))
        add_lbl = tk.Label(add_frame, text="➕ 添加选项",
                 font=Theme.FONT_SMALL, bg=Theme.CARD, fg=Theme.TEXT_MUTED,
                 cursor='hand2')
        add_lbl.pack(side='left')
        add_lbl.bind('<Button-1>', lambda e: self._add_option_row(''))
        for _ in range(3):
            self._add_option_row('')

        brow = tk.Frame(parent, bg=Theme.CARD)
        brow.pack(pady=6)
        RoundedButton(brow, text="💾 保存", command=self._save_options,
                       bg=Theme.SUCCESS, width=90, height=32).pack(side='left', padx=5)
        RoundedButton(brow, text="🎯 随机选一个", command=self._pick_one,
                       bg=Theme.ACCENT, width=120, height=32).pack(side='left', padx=5)
        RoundedButton(brow, text="🎲 随机选N个", command=self._pick_n,
                       bg=Theme.PRIMARY, width=120, height=32).pack(side='left', padx=5)
        rc = tk.Frame(parent, bg='#FFF8E1')
        rc.pack(fill='x', padx=15, pady=(5, 12))
        tk.Label(rc, text="结果", font=Theme.FONT_SMALL, bg='#FFF8E1',
                 fg=Theme.TEXT_SECONDARY).pack(anchor='w', padx=12, pady=(8, 0))
        self.custom_result = tk.Label(rc, text="点击按钮开始",
                                       font=('Microsoft YaHei', 14, 'bold'),
                                       bg='#FFF8E1', fg=Theme.ACCENT,
                                       wraplength=320, justify='left')
        self.custom_result.pack(pady=(2, 10), padx=12, anchor='w')

    def _add_option_row(self, text=''):
        row = tk.Frame(self.custom_inner, bg=Theme.CARD)
        row.pack(fill='x', padx=5, pady=2)
        idx_label = tk.Label(row, text=f'{len(self.option_entries)+1}.',
                             font=Theme.FONT_SMALL, bg=Theme.CARD,
                             fg=Theme.TEXT_MUTED, width=3)
        idx_label.pack(side='left')
        entry = tk.Entry(row, font=Theme.FONT_BODY, bd=0,
                         highlightthickness=1, highlightbackground=Theme.BORDER,
                         highlightcolor=Theme.PRIMARY)
        entry.insert(0, text)
        entry.pack(side='left', fill='x', expand=True, padx=(2, 5))
        del_btn = tk.Label(row, text='✕', font=Theme.FONT_SMALL, bg=Theme.CARD,
                           fg=Theme.DANGER, cursor='hand2')
        del_btn.pack(side='right', padx=(2, 5))
        del_btn.bind('<Button-1>', lambda e, r=row, en=entry: self._remove_option_row(r, en))
        self.option_entries.append(entry)

    def _remove_option_row(self, row, entry):
        try:
            row.destroy()
            if entry in self.option_entries:
                self.option_entries.remove(entry)
            for i, w in enumerate(self.custom_inner.winfo_children()):
                for child in w.winfo_children():
                    try:
                        if '.' in str(child.cget('text')):
                            child.config(text=f'{i+1}.')
                    except Exception:
                        pass
        except Exception:
            pass

    def _get_options_text(self):
        return '\n'.join(e.get().strip() for e in self.option_entries if e.winfo_exists() and e.get().strip())

    def _build_lots(self, parent):
        tk.Label(parent, text="签文列表", font=Theme.FONT_BODY,
                 bg=Theme.CARD, fg=Theme.TEXT_SECONDARY).pack(anchor='w', padx=15, pady=(12, 3))

        scroll_wrap = tk.Frame(parent, bg=Theme.CARD)
        scroll_wrap.pack(fill='both', expand=True, padx=15, pady=(0, 5))
        canvas = tk.Canvas(scroll_wrap, bg=Theme.CARD, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(scroll_wrap, orient='vertical', command=canvas.yview)
        self.lots_inner = tk.Frame(canvas, bg=Theme.CARD)
        self.lots_inner.bind('<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.lots_inner, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self._lots_canvas = canvas
        self.lot_entries = []

        add_frame = tk.Frame(parent, bg=Theme.CARD)
        add_frame.pack(fill='x', padx=15, pady=(2, 0))
        add_lbl = tk.Label(add_frame, text="➕ 添加签文",
                 font=Theme.FONT_SMALL, bg=Theme.CARD, fg=Theme.TEXT_MUTED,
                 cursor='hand2')
        add_lbl.pack(side='left')
        add_lbl.bind('<Button-1>', lambda e: self._add_lot_row(''))
        for lot in ['大吉', '中吉', '小吉', '吉', '末吉', '凶', '大凶']:
            self._add_lot_row(lot)

        brow = tk.Frame(parent, bg=Theme.CARD)
        brow.pack(pady=6)
        RoundedButton(brow, text="💾 保存签文", command=self._save_lots,
                       bg=Theme.SUCCESS, width=110, height=32).pack(side='left', padx=5)
        RoundedButton(brow, text="🎋 抽签", command=self._draw_lot_anim,
                       bg='#E91E63', width=110, height=34).pack(side='left', padx=5)
        rc = tk.Frame(parent, bg='#FCE4EC')
        rc.pack(fill='x', padx=15, pady=(5, 12))
        self.lot_result = tk.Label(rc, text="心诚则灵",
                                    font=('Microsoft YaHei', 14, 'bold'),
                                    bg='#FCE4EC', fg='#880E4F',
                                    wraplength=320, justify='center')
        self.lot_result.pack(pady=12, padx=15)

    def _add_lot_row(self, text=''):
        row = tk.Frame(self.lots_inner, bg=Theme.CARD)
        row.pack(fill='x', padx=5, pady=2)
        idx_label = tk.Label(row, text=f'{len(self.lot_entries)+1}.',
                             font=Theme.FONT_SMALL, bg=Theme.CARD,
                             fg=Theme.TEXT_MUTED, width=3)
        idx_label.pack(side='left')
        entry = tk.Entry(row, font=Theme.FONT_BODY, bd=0,
                         highlightthickness=1, highlightbackground=Theme.BORDER,
                         highlightcolor=Theme.PRIMARY)
        entry.insert(0, text)
        entry.pack(side='left', fill='x', expand=True, padx=(2, 5))
        del_btn = tk.Label(row, text='✕', font=Theme.FONT_SMALL, bg=Theme.CARD,
                           fg=Theme.DANGER, cursor='hand2')
        del_btn.pack(side='right', padx=(2, 5))
        del_btn.bind('<Button-1>', lambda e, r=row, en=entry: self._remove_lot_row(r, en))
        self.lot_entries.append(entry)

    def _remove_lot_row(self, row, entry):
        try:
            row.destroy()
            if entry in self.lot_entries:
                self.lot_entries.remove(entry)
            for i, w in enumerate(self.lots_inner.winfo_children()):
                for child in w.winfo_children():
                    try:
                        if '.' in str(child.cget('text')):
                            child.config(text=f'{i+1}.')
                    except Exception:
                        pass
        except Exception:
            pass

    def _get_lots_text(self):
        return '\n'.join(e.get().strip() for e in self.lot_entries if e.winfo_exists() and e.get().strip())

    def _build_coin(self, parent):
        c = tk.Frame(parent, bg=Theme.CARD)
        c.pack(expand=True, fill='both')

        self.coin_canvas = tk.Canvas(c, width=220, height=150,
                                      bg=Theme.CARD, highlightthickness=0)
        self.coin_canvas.pack(pady=(15, 5))
        self._draw_coin_canvas('idle')

        self.coin_label = tk.Label(c, text="点击按钮抛硬币",
                                    font=('Microsoft YaHei', 18, 'bold'),
                                    bg=Theme.CARD, fg=Theme.TEXT_MUTED)
        self.coin_label.pack(pady=5)
        RoundedButton(c, text="🪙 抛 硬 币", command=self._flip_coin_anim,
                       bg=Theme.WARNING, fg='#333',
                       width=150, height=42).pack(pady=12)
        self.coin_stats = tk.Label(c, text="正面: 0 次  |  反面: 0 次",
                                    font=Theme.FONT_SMALL, bg=Theme.CARD,
                                    fg=Theme.TEXT_MUTED)
        self.coin_stats.pack()
        self.coin_count = {'heads': 0, 'tails': 0}

    def _draw_coin_canvas(self, state):
        self.coin_canvas.delete('all')
        cx, cy = 110, 75
        r_outer = 55
        r_inner = 48
        if state == 'idle':
            # 3D coin appearance with rim and shine
            self.coin_canvas.create_oval(cx - r_outer, cy - r_outer,
                                          cx + r_outer, cy + r_outer,
                                          fill='#B8860B', outline='#8B6914', width=2)
            self.coin_canvas.create_oval(cx - r_inner, cy - r_inner,
                                          cx + r_inner, cy + r_inner,
                                          fill='#FFD700', outline='#DAA520', width=2)
            # Inner circle decoration
            self.coin_canvas.create_oval(cx - 35, cy - 35, cx + 35, cy + 35,
                                          outline='#DAA520', width=1)
            # Shine highlight
            self.coin_canvas.create_arc(cx - 40, cy - 42, cx + 40, cy + 20,
                                         start=200, extent=100,
                                         style='arc', outline='#FFFFFF', width=2)
            self.coin_canvas.create_text(cx, cy + 2, text="正 反",
                                           font=('Microsoft YaHei', 16, 'bold'),
                                           fill='#8B6914')
        elif state == 'flip1':
            # Side view - thin ellipse
            self.coin_canvas.create_oval(cx - r_outer * 0.25, cy - r_outer,
                                          cx + r_outer * 0.25, cy + r_outer,
                                          fill='#DAA520', outline='#8B6914', width=2)
            self.coin_canvas.create_text(cx, cy, text="!",
                                           font=('Arial', 24, 'bold'),
                                           fill='#5D4E37')
        elif state == 'flip2':
            # Almost edge-on
            self.coin_canvas.create_oval(cx - r_outer * 0.08, cy - r_outer,
                                          cx + r_outer * 0.08, cy + r_outer,
                                          fill='#B8860B', outline='#8B6914', width=2)
        elif state == 'heads':
            # Heads - 正面 with "正" character
            self.coin_canvas.create_oval(cx - r_outer, cy - r_outer,
                                          cx + r_outer, cy + r_outer,
                                          fill='#B8860B', outline='#8B6914', width=2)
            self.coin_canvas.create_oval(cx - r_inner, cy - r_inner,
                                          cx + r_inner, cy + r_inner,
                                          fill='#FFA726', outline='#E65100', width=2)
            # Decorative ring
            self.coin_canvas.create_oval(cx - 40, cy - 40, cx + 40, cy + 40,
                                          outline='#E65100', width=1)
            # Character 正
            self.coin_canvas.create_text(cx, cy - 5, text="正",
                                           font=('Microsoft YaHei', 30, 'bold'),
                                           fill='#BF360C')
            self.coin_canvas.create_text(cx, cy + 28, text="HEADS",
                                           font=('Arial', 9, 'bold'),
                                           fill='#BF360C')
            # Small decorative dots
            for dx, dy in [(-30, -25), (30, -25), (-30, 25), (30, 25)]:
                self.coin_canvas.create_oval(cx+dx-2, cy+dy-2, cx+dx+2, cy+dy+2,
                                              fill='#E65100', outline='')
        elif state == 'tails':
            # Tails - 反面 with "反" character
            self.coin_canvas.create_oval(cx - r_outer, cy - r_outer,
                                          cx + r_outer, cy + r_outer,
                                          fill='#5C6BC0', outline='#283593', width=2)
            self.coin_canvas.create_oval(cx - r_inner, cy - r_inner,
                                          cx + r_inner, cy + r_inner,
                                          fill='#42A5F5', outline='#0D47A1', width=2)
            # Decorative ring
            self.coin_canvas.create_oval(cx - 40, cy - 40, cx + 40, cy + 40,
                                          outline='#0D47A1', width=1)
            # Character 反
            self.coin_canvas.create_text(cx, cy - 5, text="反",
                                           font=('Microsoft YaHei', 30, 'bold'),
                                           fill='#0D47A1')
            self.coin_canvas.create_text(cx, cy + 28, text="TAILS",
                                           font=('Arial', 9, 'bold'),
                                           fill='#0D47A1')
            # Small decorative dots
            for dx, dy in [(-30, -25), (30, -25), (-30, 25), (30, 25)]:
                self.coin_canvas.create_oval(cx+dx-2, cy+dy-2, cx+dx+2, cy+dy+2,
                                              fill='#0D47A1', outline='')

    def _load_data(self):
        try:
            data = DataManager.load('decider.json', {})
            options = data.get('options', '')
            lots = data.get('lots', '')
            self.coin_count = data.get('coin_stats', {'heads': 0, 'tails': 0})
            self._update_stats()
            if options.strip():
                for w in self.custom_inner.winfo_children():
                    w.destroy()
                self.option_entries = []
                for line in options.split('\n'):
                    self._add_option_row(line.strip())
            if lots.strip():
                for w in self.lots_inner.winfo_children():
                    w.destroy()
                self.lot_entries = []
                for line in lots.split('\n'):
                    self._add_lot_row(line.strip())
        except Exception:
            pass

    def _save_options(self):
        try:
            data = DataManager.load('decider.json', {})
            data['options'] = self._get_options_text()
            data['lots'] = self._get_lots_text()
            data['coin_stats'] = self.coin_count
            DataManager.save('decider.json', data)
            self.custom_result.config(text="✅ 已保存", fg=Theme.SUCCESS)
            AnimationEngine.glow_label(self.custom_result, Theme.SUCCESS)
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _pick_one(self):
        try:
            opts = [o.strip() for o in self._get_options_text().split('\n') if o.strip()]
            if not opts:
                self.custom_result.config(text="⚠️ 请先输入选项", fg=Theme.WARNING)
                AnimationEngine.glow_label(self.custom_result, Theme.WARNING)
                return
            choice = random.choice(opts)
            self._animate_result(f"🎯 {choice}")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _pick_n(self):
        try:
            opts = [o.strip() for o in self._get_options_text().split('\n') if o.strip()]
            if len(opts) < 2:
                self.custom_result.config(text="⚠️ 至少需要2个选项", fg=Theme.WARNING)
                AnimationEngine.glow_label(self.custom_result, Theme.WARNING)
                return
            n = simpledialog.askinteger("随机多选",
                                         f"共 {len(opts)} 项，选几个？",
                                         minvalue=1, maxvalue=len(opts))
            if n is None:
                return
            picked = random.sample(opts, n)
            self._animate_result("🎯 选中:\n" + "  ".join(picked))
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _animate_result(self, text):
        self.custom_result.config(text="✨ ...", fg=Theme.PRIMARY)
        self.update()
        def _show():
            self.custom_result.config(text=text, fg=Theme.ACCENT)
            AnimationEngine.glow_label(self.custom_result, Theme.ACCENT)
        self.after(250, _show)

    def _save_lots(self):
        try:
            data = DataManager.load('decider.json', {})
            data['options'] = self._get_options_text()
            data['lots'] = self._get_lots_text()
            data['coin_stats'] = self.coin_count
            DataManager.save('decider.json', data)
            self.lot_result.config(text="✅ 签文已保存", fg=Theme.SUCCESS)
            AnimationEngine.glow_label(self.lot_result, Theme.SUCCESS)
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _draw_lot_anim(self):
        try:
            lots = [l.strip() for l in self._get_lots_text().split('\n') if l.strip()]
            if not lots:
                self.lot_result.config(text="⚠️ 请先输入签文", fg=Theme.WARNING)
                AnimationEngine.glow_label(self.lot_result, Theme.WARNING)
                return
            self.lot_result.config(text="摇签中... 🍀", fg=Theme.PRIMARY)
            self.update()
            frames = ["🍀", "🎋", "✨", "🌟", "🍀", "🎋"]
            idx = [0]
            def _shake():
                idx[0] += 1
                if idx[0] >= len(frames):
                    result = random.choice(lots)
                    self.lot_result.config(text=f"🎋 {result}", fg='#880E4F')
                    AnimationEngine.glow_label(self.lot_result, '#E91E63')
                    self._show_lot_popup(result)
                    return
                self.lot_result.config(text=frames[idx[0] - 1], fg='#F57C00')
                self.after(100, _shake)
            self.after(300, _shake)
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _show_lot_popup(self, result):
        try:
            popup = tk.Toplevel(self)
            popup.title("抽签结果")
            popup.geometry("320x200")
            popup.configure(bg='#FCE4EC')
            popup.transient(self.winfo_toplevel())
            popup.grab_set()
            tk.Label(popup, text="🎋", font=('Segoe UI Emoji', 48),
                     bg='#FCE4EC').pack(pady=(15, 0))
            tk.Label(popup, text=result, font=('Microsoft YaHei', 16, 'bold'),
                     bg='#FCE4EC', fg='#880E4F', wraplength=280).pack(pady=10, padx=20)
            RoundedButton(popup, text="好的", command=popup.destroy,
                           bg='#E91E63', width=100, height=32).pack(pady=8)
            popup.update_idletasks()
            AnimationEngine.animate_popup(popup, duration=300)
        except Exception:
            pass

    def _flip_coin_anim(self):
        try:
            self.coin_label.config(text="翻转中...", fg=Theme.PRIMARY)
            self.update()
            frames = ['flip1', 'flip2', 'flip1', 'flip2', 'flip1']
            idx = [0]

            def _flip():
                idx[0] += 1
                if idx[0] >= len(frames):
                    result = random.choice(['heads', 'tails'])
                    if result == 'heads':
                        self.coin_count['heads'] += 1
                        self._draw_coin_canvas('heads')
                        self.coin_label.config(text="🌟 正 面 🌟", fg='#FF6F00')
                    else:
                        self.coin_count['tails'] += 1
                        self._draw_coin_canvas('tails')
                        self.coin_label.config(text="🌙 反 面 🌙", fg='#1565C0')
                    self._update_stats()
                    data = DataManager.load('decider.json', {})
                    data['coin_stats'] = self.coin_count
                    DataManager.save('decider.json', data)
                    c = '#FF6F00' if result == 'heads' else '#1565C0'
                    AnimationEngine.glow_label(self.coin_label, c)
                    return
                self._draw_coin_canvas(frames[idx[0] - 1])
                self.after(80, _flip)
            self.after(200, _flip)
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _update_stats(self):
        h = self.coin_count.get('heads', 0)
        t = self.coin_count.get('tails', 0)
        self.coin_stats.config(text=f"正面: {h} 次  |  反面: {t} 次")

class AccountingPage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=Theme.BG, **kwargs)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="💰 简易记账", font=Theme.FONT_HEADER,
                 bg=Theme.BG, fg=Theme.TEXT).pack(pady=(10, 5))
        tk.Label(self, text="收支记录 / 极简流水", font=Theme.FONT_SMALL,
                 bg=Theme.BG, fg=Theme.TEXT_SECONDARY).pack()

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=15, pady=5)

        t1 = tk.Frame(nb, bg=Theme.CARD)
        nb.add(t1, text='  记一笔  ')
        self._build_add_entry(t1)

        t2 = tk.Frame(nb, bg=Theme.CARD)
        nb.add(t2, text='  流水表  ')
        self._build_transaction_list(t2)

        self._refresh_summary()

    def _build_add_entry(self, parent):
        form = tk.Frame(parent, bg=Theme.CARD)
        form.pack(fill='x', padx=15, pady=15)

        row1 = tk.Frame(form, bg=Theme.CARD)
        row1.pack(fill='x', pady=5)
        tk.Label(row1, text="类型:", font=Theme.FONT_BODY, bg=Theme.CARD,
                 fg=Theme.TEXT_SECONDARY, width=8).pack(side='left')
        self.type_var = tk.StringVar(value='expense')
        type_frame = tk.Frame(row1, bg=Theme.CARD)
        type_frame.pack(side='left', fill='x', expand=True)
        tk.Radiobutton(type_frame, text="支出", variable=self.type_var, value='expense',
                        font=Theme.FONT_BODY, bg=Theme.CARD, fg=Theme.DANGER,
                        selectcolor=Theme.CARD, activebackground=Theme.CARD).pack(side='left', padx=5)
        tk.Radiobutton(type_frame, text="收入", variable=self.type_var, value='income',
                        font=Theme.FONT_BODY, bg=Theme.CARD, fg=Theme.SUCCESS,
                        selectcolor=Theme.CARD, activebackground=Theme.CARD).pack(side='left', padx=5)

        row2 = tk.Frame(form, bg=Theme.CARD)
        row2.pack(fill='x', pady=5)
        tk.Label(row2, text="分类:", font=Theme.FONT_BODY, bg=Theme.CARD,
                 fg=Theme.TEXT_SECONDARY, width=8).pack(side='left')
        self.category_var = tk.StringVar(value='餐饮')
        categories = ['餐饮', '交通', '购物', '娱乐', '医疗', '工资', '奖金', '其他']
        ttk.Combobox(row2, textvariable=self.category_var, values=categories,
                      font=Theme.FONT_BODY, state='readonly',
                      width=15).pack(side='left', fill='x', expand=True)

        row3 = tk.Frame(form, bg=Theme.CARD)
        row3.pack(fill='x', pady=5)
        tk.Label(row3, text="金额:", font=Theme.FONT_BODY, bg=Theme.CARD,
                 fg=Theme.TEXT_SECONDARY, width=8).pack(side='left')
        self.amount_var = tk.StringVar()
        tk.Entry(row3, textvariable=self.amount_var, font=Theme.FONT_BODY,
                  width=15, bd=0, highlightthickness=1,
                  highlightbackground=Theme.BORDER,
                  highlightcolor=Theme.PRIMARY).pack(side='left', fill='x', expand=True)

        row4 = tk.Frame(form, bg=Theme.CARD)
        row4.pack(fill='x', pady=5)
        tk.Label(row4, text="日期:", font=Theme.FONT_BODY, bg=Theme.CARD,
                 fg=Theme.TEXT_SECONDARY, width=8).pack(side='left')
        today = datetime.date.today().strftime('%Y-%m-%d')
        self.date_var = tk.StringVar(value=today)
        tk.Entry(row4, textvariable=self.date_var, font=Theme.FONT_BODY,
                  width=15, bd=0, highlightthickness=1,
                  highlightbackground=Theme.BORDER,
                  highlightcolor=Theme.PRIMARY).pack(side='left', fill='x', expand=True)

        row5 = tk.Frame(form, bg=Theme.CARD)
        row5.pack(fill='x', pady=5)
        tk.Label(row5, text="备注:", font=Theme.FONT_BODY, bg=Theme.CARD,
                 fg=Theme.TEXT_SECONDARY, width=8).pack(side='left')
        self.note_var = tk.StringVar()
        tk.Entry(row5, textvariable=self.note_var, font=Theme.FONT_BODY,
                  width=15, bd=0, highlightthickness=1,
                  highlightbackground=Theme.BORDER,
                  highlightcolor=Theme.PRIMARY).pack(side='left', fill='x', expand=True)

        btn_frame = tk.Frame(form, bg=Theme.CARD)
        btn_frame.pack(pady=10)
        RoundedButton(btn_frame, text="💾 保存记录", command=self._add_entry,
                       bg=Theme.PRIMARY, width=130, height=36).pack(side='left', padx=5)
        RoundedButton(btn_frame, text="清空", command=self._clear_form,
                       bg=Theme.TEXT_MUTED, width=80, height=36).pack(side='left', padx=5)

        self.add_status = tk.Label(form, text="", font=Theme.FONT_SMALL,
                                    bg=Theme.CARD, fg=Theme.SUCCESS)
        self.add_status.pack(pady=3)

    def _build_transaction_list(self, parent):
        style = ttk.Style()
        style.configure('Acc.Treeview', background=Theme.CARD, foreground=Theme.TEXT,
                        fieldbackground=Theme.CARD, font=Theme.FONT_BODY, rowheight=26)
        style.configure('Acc.Treeview.Heading', font=Theme.FONT_BODY_BOLD,
                        background=Theme.PRIMARY, foreground='white')

        lf = tk.Frame(parent, bg=Theme.CARD)
        lf.pack(fill='both', expand=True, padx=15, pady=10)

        cols = ('date', 'type', 'category', 'amount', 'note')
        self.tree = ttk.Treeview(lf, columns=cols, show='headings',
                                  height=12, style='Acc.Treeview')
        for col, txt, w in [('date', '日期', 100), ('type', '类型', 60),
                             ('category', '分类', 80), ('amount', '金额', 80),
                             ('note', '备注', 160)]:
            self.tree.heading(col, text=txt)
            anchor = 'center' if col != 'note' else 'w'
            self.tree.column(col, width=w, anchor=anchor)

        vsb = ttk.Scrollbar(lf, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        bf = tk.Frame(parent, bg=Theme.CARD)
        bf.pack(fill='x', padx=15, pady=5)
        RoundedButton(bf, text="🗑️ 删除选中", command=self._delete_selected,
                       bg=Theme.DANGER, width=110, height=30).pack(side='left', padx=5)
        RoundedButton(bf, text="🔄 刷新", command=self._refresh_list,
                       bg=Theme.PRIMARY, width=80, height=30).pack(side='left', padx=5)

        self.summary_frame = tk.Frame(parent, bg=Theme.CARD)
        self.summary_frame.pack(fill='x', padx=15, pady=10)

    def _add_entry(self):
        try:
            amount_str = self.amount_var.get().strip()
            if not amount_str:
                messagebox.showwarning("提示", "请输入金额！")
                return
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("提示", "金额必须大于0！")
                return
            date_str = self.date_var.get().strip()
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的金额和日期！")
            return
        except Exception as e:
            messagebox.showerror("错误", str(e))
            return

        try:
            data = DataManager.load('accounting.json', {})
            entries = data.get('entries', [])
            entry = {
                'type': self.type_var.get(),
                'category': self.category_var.get(),
                'amount': amount,
                'date': date_str,
                'note': self.note_var.get().strip()
            }
            entries.append(entry)
            data['entries'] = entries
            DataManager.save('accounting.json', data)
            self.add_status.config(text="✅ 已保存", fg=Theme.SUCCESS)
            AnimationEngine.glow_label(self.add_status, Theme.SUCCESS)
            self._clear_form()
            self._refresh_list()
            self._refresh_summary()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _clear_form(self):
        self.amount_var.set('')
        self.note_var.set('')
        self.type_var.set('expense')
        self.category_var.set('餐饮')
        self.date_var.set(datetime.date.today().strftime('%Y-%m-%d'))

    def _load_entries(self):
        data = DataManager.load('accounting.json', {})
        return data.get('entries', [])

    def _refresh_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        entries = self._load_entries()
        for e in reversed(entries):
            type_text = '收入' if e.get('type') == 'income' else '支出'
            amount = e.get('amount', 0)
            if e.get('type') == 'income':
                amount_text = f'+{amount:.2f}'
            else:
                amount_text = f'-{amount:.2f}'
            self.tree.insert('', 'end', values=(
                e.get('date', ''), type_text, e.get('category', ''),
                amount_text, e.get('note', '')))

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请先选择要删除的记录！")
            return
        if not messagebox.askyesno("确认", f"确定要删除 {len(sel)} 条记录吗？"):
            return
        try:
            data = DataManager.load('accounting.json', {})
            entries = data.get('entries', [])
            for s in sel:
                vals = self.tree.item(s, 'values')
                date_sel, type_sel, cat_sel, amt_sel = vals[0], vals[1], vals[2], vals[3]
                for i, e in enumerate(entries):
                    if (e.get('date') == date_sel and
                        ('收入' if e.get('type') == 'income' else '支出') == type_sel and
                        e.get('category') == cat_sel and
                        f"{float(amt_sel.replace('+', '').replace('-', '')):.2f}" == f"{e.get('amount'):.2f}"):
                        del entries[i]
                        break
            data['entries'] = entries
            DataManager.save('accounting.json', data)
            self._refresh_list()
            self._refresh_summary()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _refresh_summary(self):
        try:
            for w in self.summary_frame.winfo_children():
                w.destroy()
            entries = self._load_entries()
            total_income = sum(e.get('amount', 0) for e in entries if e.get('type') == 'income')
            total_expense = sum(e.get('amount', 0) for e in entries if e.get('type') == 'expense')
            balance = total_income - total_expense

            tk.Label(self.summary_frame, text="📊 统计", font=Theme.FONT_BODY_BOLD,
                     bg=Theme.CARD, fg=Theme.TEXT).pack(anchor='w', padx=10, pady=(8, 3))

            stats_row = tk.Frame(self.summary_frame, bg=Theme.CARD)
            stats_row.pack(fill='x', padx=10, pady=3)

            tk.Label(stats_row, text=f"总收入: ¥{total_income:.2f}",
                     font=Theme.FONT_BODY, bg=Theme.CARD,
                     fg=Theme.SUCCESS).pack(side='left', padx=10)
            tk.Label(stats_row, text=f"总支出: ¥{total_expense:.2f}",
                     font=Theme.FONT_BODY, bg=Theme.CARD,
                     fg=Theme.DANGER).pack(side='left', padx=10)
            bal_color = Theme.SUCCESS if balance >= 0 else Theme.DANGER
            tk.Label(stats_row, text=f"结余: ¥{balance:.2f}",
                     font=Theme.FONT_BODY_BOLD, bg=Theme.CARD,
                     fg=bal_color).pack(side='left', padx=10)

            tk.Label(self.summary_frame, text=f"共 {len(entries)} 条记录",
                     font=Theme.FONT_SMALL, bg=Theme.CARD,
                     fg=Theme.TEXT_MUTED).pack(anchor='w', padx=10, pady=(3, 8))
        except Exception:
            pass



class StickyNoteWindow(tk.Toplevel):
    def __init__(self, master, note_id=0, text="", color='#FFF9C4', name=""):
        super().__init__(master)
        self.note_id = note_id
        self.save_job = None
        self._drag_x = 0
        self._drag_y = 0
        self._name = name or f"便签 #{note_id + 1}"
        self._main_app = master.winfo_toplevel()
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.configure(bg=color, highlightbackground='#BDBDBD', highlightthickness=1)

        title_bar = tk.Frame(self, bg=color, height=30)
        title_bar.pack(fill='x', side='top')
        title_bar.pack_propagate(False)

        self.name_label = tk.Label(title_bar, text=self._name, bg=color,
                                    font=('Microsoft YaHei', 9, 'bold'),
                                    anchor='w', cursor='hand2')
        self.name_label.pack(side='left', padx=5)
        self.name_label.bind('<Double-Button-1>', lambda e: self._rename())

        close_btn = tk.Label(title_bar, text="✕", bg=color, fg='#D32F2F',
                               font=('Segoe UI', 10, 'bold'), cursor='hand2')
        close_btn.pack(side='right', padx=3)
        close_btn.bind('<Button-1>', lambda e: self._close())
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg='#B71C1C'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg='#D32F2F'))

        color_btn = tk.Label(title_bar, text="🎨", bg=color,
                               font=('Segoe UI', 10), cursor='hand2')
        color_btn.pack(side='right', padx=3)
        color_btn.bind('<Button-1>', lambda e: self._change_color())

        title_bar.bind('<Button-1>', self._start_drag)
        title_bar.bind('<B1-Motion>', self._on_drag)
        self.name_label.bind('<Button-1>', self._start_drag)
        self.name_label.bind('<B1-Motion>', self._on_drag)

        self.text_widget = tk.Text(self, bg=color, fg=Theme.TEXT,
                                    font=Theme.FONT_BODY, wrap='word', bd=0,
                                    highlightthickness=0, padx=8, pady=5, height=6)
        self.text_widget.pack(fill='both', expand=True)
        self.text_widget.insert('1.0', text)
        self.text_widget.bind('<KeyRelease>', self._on_change)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="修改名称", command=self._rename)
        self.menu.add_command(label="置顶/取消置顶", command=self._toggle_top)
        self.menu.add_command(label="新建便签", command=self._new_note)
        self.menu.add_command(label="关闭", command=self._close)
        self.text_widget.bind('<Button-3>', self._show_menu)

        try:
            data = DataManager.load('notes.json', {})
            notes = data.get('notes', [])
            if note_id < len(notes):
                self.geometry(notes[note_id].get('geometry', '180x150+100+100'))
            else:
                self.geometry('180x150+100+100')
        except Exception:
            self.geometry('180x150+100+100')
        try:
            self.update_idletasks()
            AnimationEngine.animate_popup(self, duration=250)
        except Exception:
            pass

    def _rename(self):
        try:
            new_name = simpledialog.askstring("修改便签名称",
                                               "请输入便签名称：",
                                               initialvalue=self._name,
                                               parent=self._main_app)
            if new_name and new_name.strip():
                self._name = new_name.strip()
                self.name_label.config(text=self._name)
                self._save()
        except Exception:
            pass

    def _start_drag(self, e):
        self._drag_x, self._drag_y = e.x_root - self.winfo_x(), e.y_root - self.winfo_y()

    def _on_drag(self, e):
        self.geometry(f'+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}')

    def _on_change(self, e=None):
        if self.save_job:
            self.after_cancel(self.save_job)
        self.save_job = self.after(500, self._save)

    def _save(self):
        self.save_job = None
        try:
            data = DataManager.load('notes.json', {})
            notes = data.get('notes', [])
            text = self.text_widget.get('1.0', 'end-1c')
            geom = self.geometry()
            color = self.cget('bg')
            while len(notes) <= self.note_id:
                notes.append({'text': '', 'geometry': '180x150+100+100',
                              'color': '#FFF9C4', 'name': ''})
            notes[self.note_id] = {
                'text': text, 'geometry': geom,
                'color': color, 'name': self._name}
            data['notes'] = notes
            DataManager.save('notes.json', data)
        except Exception:
            pass

    def _close(self):
        try:
            self._save()
            data = DataManager.load('notes.json', {})
            notes = data.get('notes', [])
            if self.note_id < len(notes):
                notes[self.note_id]['closed'] = True
                data['notes'] = notes
                DataManager.save('notes.json', data)
        except Exception:
            pass
        try:
            self.attributes('-topmost', False)
            self.overrideredirect(False)
        except Exception:
            pass
        self.destroy()

    def _toggle_top(self):
        try:
            self.attributes('-topmost', not self.attributes('-topmost'))
        except Exception:
            pass

    def _new_note(self):
        try:
            self._main_app.add_note()
        except Exception:
            pass

    def _change_color(self):
        try:
            c = colorchooser.askcolor(title="选择便签颜色",
                                        color=self.cget('bg'),
                                        parent=self._main_app)
            if c and c[1]:
                new_color = c[1]
                self.configure(bg=new_color)
                try:
                    title_bar = self.winfo_children()[0]
                    title_bar.configure(bg=new_color)
                    for ch in title_bar.winfo_children():
                        try:
                            ch.configure(bg=new_color)
                        except Exception:
                            pass
                except Exception:
                    pass
                self.text_widget.configure(bg=new_color)
                self._save()
        except Exception:
            pass

    def _show_menu(self, e):
        try:
            self.menu.tk_popup(e.x_root, e.y_root)
        except Exception:
            pass

class TimeCapsulePage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=Theme.BG, **kwargs)
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        tk.Label(self, text="⏳ 时光胶囊", font=Theme.FONT_HEADER,
                 bg=Theme.BG, fg=Theme.TEXT).pack(pady=(10, 5))
        tk.Label(self, text="写下文字 / 定时解锁", font=Theme.FONT_SMALL,
                 bg=Theme.BG, fg=Theme.TEXT_SECONDARY).pack()

        main_frame = tk.Frame(self, bg=Theme.BG)
        main_frame.pack(fill='both', expand=True, padx=15, pady=5)

        left_frame = tk.Frame(main_frame, bg=Theme.CARD)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 8))

        tk.Label(left_frame, text="✍️ 写一封给未来的信", font=Theme.FONT_BODY_BOLD,
                 bg=Theme.CARD, fg=Theme.TEXT).pack(anchor='w', padx=12, pady=(10, 5))

        self.capsule_text = tk.Text(left_frame, font=Theme.FONT_BODY, height=10,
                                     bd=0, highlightthickness=1,
                                     highlightbackground=Theme.BORDER,
                                     highlightcolor=Theme.PRIMARY, wrap='word')
        self.capsule_text.pack(fill='both', expand=True, padx=12)

        date_frame = tk.Frame(left_frame, bg=Theme.CARD)
        date_frame.pack(fill='x', padx=12, pady=8)
        tk.Label(date_frame, text="解锁日期:", font=Theme.FONT_BODY,
                 bg=Theme.CARD, fg=Theme.TEXT_SECONDARY).pack(side='left', padx=(0, 5))
        self.unlock_date_var = tk.StringVar()
        tk.Entry(date_frame, textvariable=self.unlock_date_var, font=Theme.FONT_BODY,
                  width=12, bd=0, highlightthickness=1,
                  highlightbackground=Theme.BORDER,
                  highlightcolor=Theme.PRIMARY).pack(side='left', padx=5)
        tk.Label(date_frame, text="(格式: YYYY-MM-DD)", font=Theme.FONT_SMALL,
                 bg=Theme.CARD, fg=Theme.TEXT_MUTED).pack(side='left', padx=5)

        btn_frame = tk.Frame(left_frame, bg=Theme.CARD)
        btn_frame.pack(pady=8)
        RoundedButton(btn_frame, text="📦 封存胶囊", command=self._seal_capsule,
                       bg=Theme.PRIMARY, width=130, height=36).pack(side='left', padx=5)
        RoundedButton(btn_frame, text="清空", command=self._clear_text,
                       bg=Theme.TEXT_MUTED, width=80, height=36).pack(side='left', padx=5)

        self.capsule_status = tk.Label(left_frame, text="", font=Theme.FONT_SMALL,
                                        bg=Theme.CARD, fg=Theme.SUCCESS)
        self.capsule_status.pack(pady=3)

        right_frame = tk.Frame(main_frame, bg=Theme.CARD)
        right_frame.pack(side='right', fill='both', expand=True, padx=(8, 0))

        tk.Label(right_frame, text="📋 我的胶囊", font=Theme.FONT_BODY_BOLD,
                 bg=Theme.CARD, fg=Theme.TEXT).pack(anchor='w', padx=12, pady=(10, 5))

        list_container = tk.Frame(right_frame, bg=Theme.CARD)
        list_container.pack(fill='both', expand=True, padx=12)

        self.capsule_canvas = tk.Canvas(list_container, bg=Theme.CARD,
                                        bd=0, highlightthickness=0)
        self.capsule_scrollbar = ttk.Scrollbar(list_container, orient='vertical',
                                                command=self.capsule_canvas.yview)
        self.capsule_inner = tk.Frame(self.capsule_canvas, bg=Theme.CARD)

        self.capsule_inner.bind('<Configure>',
                                  lambda e: self.capsule_canvas.configure(
                                      scrollregion=self.capsule_canvas.bbox('all')))
        self.capsule_canvas.create_window((0, 0), window=self.capsule_inner, anchor='nw')
        self.capsule_canvas.configure(yscrollcommand=self.capsule_scrollbar.set)

        self.capsule_canvas.pack(side='left', fill='both', expand=True)
        self.capsule_scrollbar.pack(side='right', fill='y')

    def _seal_capsule(self):
        text = self.capsule_text.get('1.0', 'end-1c').strip()
        if not text:
            messagebox.showwarning("提示", "请写下胶囊内容！")
            return
        date_str = self.unlock_date_var.get().strip()
        if not date_str:
            messagebox.showwarning("提示", "请设置解锁日期！")
            return
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("提示", "日期格式错误！请使用 YYYY-MM-DD")
            return

        try:
            data = DataManager.load('capsules.json', {})
            capsules = data.get('capsules', [])
            capsule = {
                'text': text,
                'unlock_date': date_str,
                'seal_date': datetime.date.today().strftime('%Y-%m-%d'),
                'unlocked': False
            }
            capsules.append(capsule)
            data['capsules'] = capsules
            DataManager.save('capsules.json', data)
            self.capsule_status.config(text="✅ 胶囊已封存！", fg=Theme.SUCCESS)
            AnimationEngine.glow_label(self.capsule_status, Theme.SUCCESS)
            self._clear_text()
            self._refresh_list()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _clear_text(self):
        self.capsule_text.delete('1.0', 'end')
        self.unlock_date_var.set('')

    def _load_capsules(self):
        data = DataManager.load('capsules.json', {})
        return data.get('capsules', [])

    def _refresh_list(self):
        for w in self.capsule_inner.winfo_children():
            w.destroy()
        capsules = self._load_capsules()
        if not capsules:
            tk.Label(self.capsule_inner, text="暂无胶囊，写下你的第一个时光胶囊吧 ✨",
                     font=Theme.FONT_BODY, bg=Theme.CARD,
                     fg=Theme.TEXT_MUTED).pack(pady=20)
            return

        today = datetime.date.today()
        for i, cap in enumerate(reversed(capsules)):
            unlock_date = cap.get('unlock_date', '')
            unlocked = cap.get('unlocked', False)
            try:
                ud = datetime.datetime.strptime(unlock_date, '%Y-%m-%d').date()
                if not unlocked and ud <= today:
                    cap['unlocked'] = True
                    unlocked = True
                    data = DataManager.load('capsules.json', {})
                    caps = data.get('capsules', [])
                    idx = len(caps) - 1 - i
                    if 0 <= idx < len(caps):
                        caps[idx]['unlocked'] = True
                        data['capsules'] = caps
                        DataManager.save('capsules.json', data)
            except Exception:
                pass

            cap_frame = tk.Frame(self.capsule_inner, bg=Theme.CARD)
            cap_frame.pack(fill='x', pady=5, padx=5)

            header = tk.Frame(cap_frame, bg=Theme.CARD)
            header.pack(fill='x', padx=10, pady=8)

            status_text = "🔓 已解锁" if unlocked else "🔒 已封存"
            status_color = Theme.SUCCESS if unlocked else Theme.WARNING
            tk.Label(header, text=status_text, font=Theme.FONT_BODY_BOLD,
                     bg=Theme.CARD, fg=status_color).pack(side='left')

            tk.Label(header, text=f"解锁日期: {unlock_date}", font=Theme.FONT_SMALL,
                     bg=Theme.CARD, fg=Theme.TEXT_SECONDARY).pack(side='right')

            tk.Label(header, text=f"封存于 {cap.get('seal_date', '')}",
                     font=Theme.FONT_SMALL, bg=Theme.CARD,
                     fg=Theme.TEXT_MUTED).pack(side='right', padx=10)

            if unlocked:
                content_frame = tk.Frame(cap_frame, bg='#F3E5F5')
                content_frame.pack(fill='x', padx=10, pady=(0, 8))
                tk.Label(content_frame, text=cap.get('text', ''),
                         font=Theme.FONT_BODY, bg='#F3E5F5', fg=Theme.TEXT,
                         wraplength=250, justify='left',
                         anchor='w').pack(padx=10, pady=8, anchor='w')
            else:
                tk.Label(cap_frame, text="🔒 内容将在解锁日期后可见...",
                         font=Theme.FONT_SMALL, bg=Theme.CARD,
                         fg=Theme.TEXT_MUTED).pack(pady=(0, 8))

            del_btn = tk.Label(cap_frame, text="🗑️ 删除", font=Theme.FONT_SMALL,
                                bg=Theme.CARD, fg=Theme.DANGER, cursor='hand2')
            del_btn.pack(anchor='e', padx=10, pady=(0, 5))
            del_btn.bind('<Button-1>', lambda e, idx=len(capsules)-1-i: self._delete_capsule(idx))

    def _delete_capsule(self, idx):
        if not messagebox.askyesno("确认", "确定要删除这个胶囊吗？"):
            return
        try:
            data = DataManager.load('capsules.json', {})
            capsules = data.get('capsules', [])
            if 0 <= idx < len(capsules):
                del capsules[idx]
                data['capsules'] = capsules
                DataManager.save('capsules.json', data)
                self._refresh_list()
        except Exception as e:
            messagebox.showerror("错误", str(e))



class NotePage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=Theme.BG, **kwargs)
        self.active_notes = {}
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="📝 桌面便签", font=Theme.FONT_HEADER,
                 bg=Theme.BG, fg=Theme.TEXT).pack(pady=(10, 5))
        tk.Label(self, text="置顶窗口 · 自由拖动 · 自动保存",
                 font=Theme.FONT_SMALL, bg=Theme.BG,
                 fg=Theme.TEXT_SECONDARY).pack()
        bf = tk.Frame(self, bg=Theme.BG)
        bf.pack(pady=12)
        RoundedButton(bf, text="＋ 新建便签", command=self.add_note,
                       bg=Theme.WARNING, fg='#333',
                       width=120, height=38).pack(side='left', padx=6)
        RoundedButton(bf, text="打开所有便签", command=self.open_all,
                       bg=Theme.PRIMARY, width=130, height=38).pack(side='left', padx=6)
        RoundedButton(bf, text="清除所有数据", command=self.clear_all,
                       bg=Theme.DANGER, width=130, height=38).pack(side='left', padx=6)
        info = tk.Frame(self, bg=Theme.CARD)
        info.pack(fill='both', expand=True, padx=15, pady=8)
        tk.Label(info, text="💡 使用说明", font=Theme.FONT_BODY_BOLD,
                 bg=Theme.CARD, fg=Theme.TEXT).pack(anchor='w', padx=15, pady=(10, 5))
        for tip in [
            "• 便签窗口始终置顶，可自由拖动",
            "• 内容修改后自动保存（延迟 500ms）",
            "• 点击 🎨 更换便签颜色",
            "• 右键文本区：置顶 / 新建 / 关闭",
            "• 点击 ✕ 关闭当前便签",
        ]:
            tk.Label(info, text=tip, font=Theme.FONT_BODY,
                     bg=Theme.CARD, fg=Theme.TEXT_SECONDARY,
                     anchor='w').pack(anchor='w', padx=25, pady=2)

    def add_note(self):
        try:
            data = DataManager.load('notes.json', {})
            notes = data.get('notes', [])
            closed = [i for i, n in enumerate(notes) if n.get('closed', False)]
            if closed:
                nid = closed[0]
                notes[nid] = {'text': '', 'geometry': '180x150+100+100',
                              'color': '#FFF9C4', 'closed': False, 'name': ''}
            else:
                nid = len(notes)
                notes.append({'text': '', 'geometry': '180x150+100+100',
                              'color': '#FFF9C4', 'closed': False, 'name': ''})
            data['notes'] = notes
            DataManager.save('notes.json', data)
            nd = notes[nid]
            note = StickyNoteWindow(self.winfo_toplevel(), note_id=nid,
                                     text=nd.get('text', ''),
                                     color=nd.get('color', '#FFF9C4'),
                                     name=nd.get('name', ''))
            self.active_notes[nid] = note
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def open_all(self):
        try:
            data = DataManager.load('notes.json', {})
            for i, nd in enumerate(data.get('notes', [])):
                if not nd.get('closed', False) and i not in self.active_notes:
                    note = StickyNoteWindow(self.winfo_toplevel(), note_id=i,
                                             text=nd.get('text', ''),
                                             color=nd.get('color', '#FFF9C4'),
                                             name=nd.get('name', ''))
                    self.active_notes[i] = note
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def clear_all(self):
        if not messagebox.askyesno("确认", "确定要清除所有便签数据吗？"):
            return
        try:
            for n in self.active_notes.values():
                try:
                    n.destroy()
                except Exception:
                    pass
            self.active_notes.clear()
            DataManager.save('notes.json', {'notes': []})
        except Exception as e:
            messagebox.showerror("错误", str(e))


class TimerPage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=Theme.BG, **kwargs)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="⏱️ 计时工具", font=Theme.FONT_HEADER,
                 bg=Theme.BG, fg=Theme.TEXT).pack(pady=(10, 5))
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=15, pady=5)
        t1 = tk.Frame(nb, bg=Theme.CARD)
        nb.add(t1, text='  番茄钟  ')
        self._build_pomodoro(t1)
        t2 = tk.Frame(nb, bg=Theme.CARD)
        nb.add(t2, text='  自定义倒计时  ')
        self._build_countdown(t2)

    def _build_pomodoro(self, parent):
        self.pomo_seconds = 25 * 60
        self.pomo_remaining = self.pomo_seconds
        self.pomo_running = False
        self.pomo_mode = 'work'
        self.pomo_round = 0
        tk.Label(parent, text="🍅 番茄工作法", font=Theme.FONT_BODY_BOLD,
                 bg=Theme.CARD, fg=Theme.TEXT).pack(pady=(12, 3))
        self.pomo_mode_label = tk.Label(parent, text="工作时间", font=Theme.FONT_BODY,
                                        bg=Theme.CARD, fg=Theme.DANGER)
        self.pomo_mode_label.pack()
        self.pomo_display = tk.Label(parent, text="25:00", font=Theme.FONT_NUM,
                                      bg=Theme.CARD, fg=Theme.DANGER)
        self.pomo_display.pack(pady=10)
        self.pomo_progress = ttk.Progressbar(parent, length=280, maximum=100)
        self.pomo_progress.pack(pady=3)
        self.pomo_round_label = tk.Label(parent, text="第 0 轮", font=Theme.FONT_SMALL,
                                          bg=Theme.CARD, fg=Theme.TEXT_MUTED)
        self.pomo_round_label.pack()
        bf = tk.Frame(parent, bg=Theme.CARD)
        bf.pack(pady=10)
        self.pomo_start_btn = RoundedButton(bf, text="开始", command=self._pomo_toggle,
                                              bg=Theme.SUCCESS, width=90, height=34)
        self.pomo_start_btn.pack(side='left', padx=4)
        RoundedButton(bf, text="重置", command=self._pomo_reset,
                       bg=Theme.TEXT_MUTED, width=80, height=34).pack(side='left', padx=4)
        RoundedButton(bf, text="跳过", command=self._pomo_skip,
                       bg=Theme.WARNING, fg='#333',
                       width=80, height=34).pack(side='left', padx=4)
        sf = tk.LabelFrame(parent, text="时间设置(分钟)", font=Theme.FONT_SMALL,
                            bg=Theme.CARD, fg=Theme.TEXT_SECONDARY, padx=10, pady=5,
                            bd=0, relief='flat')
        sf.pack(pady=8)
        row = tk.Frame(sf, bg=Theme.CARD)
        row.pack()
        for i, (lbl, key, default) in enumerate([
            ('工作', 'work', 25), ('短休', 'short', 5),
            ('长休', 'long', 15), ('长休间隔', 'interval', 4)]):
            tk.Label(row, text=lbl, font=Theme.FONT_SMALL,
                     bg=Theme.CARD).grid(row=0, column=i*2, padx=2, pady=2)
            var = tk.StringVar()
            tk.Entry(row, textvariable=var, width=4, font=Theme.FONT_SMALL,
                       justify='center', bd=0, highlightthickness=1,
                       highlightbackground=Theme.BORDER,
                       highlightcolor=Theme.PRIMARY).grid(row=0, column=i*2+1, padx=2, pady=2)
            setattr(self, f'pomo_{key}_var', var)
            var.set(str(default))
        RoundedButton(sf, text="应用设置", command=self._pomo_apply,
                       bg=Theme.PRIMARY, width=100, height=28).pack(pady=5)

    def _pomo_apply(self):
        try:
            data = DataManager.load('timer.json', {})
            data['pomodoro'] = {
                'work': int(self.pomo_work_var.get()) * 60,
                'short': int(self.pomo_short_var.get()) * 60,
                'long': int(self.pomo_long_var.get()) * 60,
                'interval': int(self.pomo_interval_var.get())}
            DataManager.save('timer.json', data)
            self.pomo_mode_label.config(text="✅ 设置已应用", fg=Theme.SUCCESS)
            AnimationEngine.glow_label(self.pomo_mode_label, Theme.SUCCESS)
        except ValueError:
            messagebox.showwarning("提示", "请输入有效数字！")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _pomo_toggle(self):
        if self.pomo_running:
            self.pomo_running = False
            self.pomo_start_btn._text = "开始"
            self.pomo_start_btn._draw(Theme.SUCCESS)
        else:
            self.pomo_running = True
            self.pomo_start_btn._text = "暂停"
            self.pomo_start_btn._draw(Theme.WARNING)
            self._pomo_tick()

    def _pomo_tick(self):
        if not self.pomo_running:
            return
        try:
            self.pomo_remaining -= 1
            m, s = divmod(max(0, self.pomo_remaining), 60)
            text = f"{m:02d}:{s:02d}"
            cur = self.pomo_display.cget('text')
            if cur != text:
                AnimationEngine.roll_number(self.pomo_display, cur, text, duration=180)
            self.pomo_display.config(text=text)
            w = int(self.pomo_work_var.get()) * 60
            sh = int(self.pomo_short_var.get()) * 60
            lo = int(self.pomo_long_var.get()) * 60
            t = {'work': w, 'short': sh, 'long': lo}.get(self.pomo_mode, w)
            self.pomo_progress['value'] = ((t - self.pomo_remaining) / t) * 100 if t > 0 else 0
            if self.pomo_remaining <= 0:
                self._pomo_finish()
                return
            self.after(1000, self._pomo_tick)
        except Exception:
            self.pomo_running = False

    def _pomo_finish(self):
        self.pomo_running = False
        self.pomo_start_btn._text = "开始"
        self.pomo_start_btn._draw(Theme.SUCCESS)
        if self.pomo_mode == 'work':
            self.pomo_round += 1
            self.pomo_round_label.config(text=f"第 {self.pomo_round} 轮")
            interval = int(self.pomo_interval_var.get())
            if self.pomo_round % interval == 0:
                self.pomo_mode = 'long'
                self.pomo_seconds = int(self.pomo_long_var.get()) * 60
                self.pomo_mode_label.config(text="长休息", fg='#1565C0')
                self._show_popup("🍅 工作完成！",
                                  f"进入长休息\n({int(self.pomo_long_var.get())}分钟)")
            else:
                self.pomo_mode = 'short'
                self.pomo_seconds = int(self.pomo_short_var.get()) * 60
                self.pomo_mode_label.config(text="短休息", fg='#2E7D32')
                self._show_popup("🍅 工作完成！",
                                  f"进入短休息\n({int(self.pomo_short_var.get())}分钟)")
        else:
            self.pomo_mode = 'work'
            self.pomo_seconds = int(self.pomo_work_var.get()) * 60
            self.pomo_mode_label.config(text="工作时间", fg=Theme.DANGER)
            self._show_popup("⏰ 休息结束！", "开始工作吧 💪")
        self.pomo_remaining = self.pomo_seconds
        m, s = divmod(self.pomo_remaining, 60)
        self.pomo_display.config(text=f"{m:02d}:{s:02d}")

    def _pomo_reset(self):
        self.pomo_running = False
        self.pomo_start_btn._text = "开始"
        self.pomo_start_btn._draw(Theme.SUCCESS)
        self.pomo_mode = 'work'
        self.pomo_seconds = int(self.pomo_work_var.get()) * 60
        self.pomo_remaining = self.pomo_seconds
        self.pomo_mode_label.config(text="工作时间", fg=Theme.DANGER)
        self.pomo_round = 0
        self.pomo_round_label.config(text="第 0 轮")
        m, s = divmod(self.pomo_remaining, 60)
        self.pomo_display.config(text=f"{m:02d}:{s:02d}")
        self.pomo_progress['value'] = 0

    def _pomo_skip(self):
        if self.pomo_running:
            self.pomo_remaining = 1
            self._pomo_tick()
        else:
            self._pomo_finish()

    def _build_countdown(self, parent):
        self.cd_seconds = 0
        self.cd_remaining = 0
        self.cd_running = False
        tk.Label(parent, text="⏳ 自定义倒计时", font=Theme.FONT_BODY_BOLD,
                 bg=Theme.CARD, fg=Theme.TEXT).pack(pady=(12, 3))
        tf = tk.Frame(parent, bg=Theme.CARD)
        tf.pack(pady=8)
        for lbl, key, default in [("时:", 'h', 0), ("分:", 'm', 10), ("秒:", 's', 0)]:
            tk.Label(tf, text=lbl, font=Theme.FONT_BODY, bg=Theme.CARD).pack(side='left', padx=2)
            var = tk.StringVar(value=str(default))
            setattr(self, f'cd_{key}_var', var)
            tk.Entry(tf, textvariable=var, width=5, font=('Consolas', 14, 'bold'),
                       justify='center', bd=0, highlightthickness=1,
                       highlightbackground=Theme.BORDER,
                       highlightcolor=Theme.PRIMARY).pack(side='left', padx=2)
        self.cd_display = tk.Label(parent, text="00:10:00", font=Theme.FONT_NUM,
                                    bg=Theme.CARD, fg=Theme.PRIMARY)
        self.cd_display.pack(pady=8)
        pf = tk.Frame(parent, bg=Theme.CARD)
        pf.pack(pady=3)
        tk.Label(pf, text="快速设置:", font=Theme.FONT_SMALL, bg=Theme.CARD,
                 fg=Theme.TEXT_SECONDARY).pack(side='left', padx=5)
        for lbl, h, m, s in [("5分钟",0,5,0),("10分钟",0,10,0),("30分钟",0,30,0),("1小时",1,0,0)]:
            RoundedButton(pf, text=lbl, command=lambda h=h, m=m, s=s: self._cd_preset(h,m,s),
                            bg='#E3F2FD', fg='#1565C0',
                            width=72, height=26, radius=8).pack(side='left', padx=3)
        bf = tk.Frame(parent, bg=Theme.CARD)
        bf.pack(pady=10)
        self.cd_start_btn = RoundedButton(bf, text="开始倒计时", command=self._cd_toggle,
                                             bg=Theme.SUCCESS, width=120, height=34)
        self.cd_start_btn.pack(side='left', padx=5)
        RoundedButton(bf, text="重置", command=self._cd_reset,
                       bg=Theme.TEXT_MUTED, width=80, height=34).pack(side='left', padx=5)

    def _cd_preset(self, h, m, s):
        self.cd_h_var.set(str(h))
        self.cd_m_var.set(str(m))
        self.cd_s_var.set(str(s))
        self._cd_reset()

    def _cd_toggle(self):
        if self.cd_running:
            self.cd_running = False
            self.cd_start_btn._text = "继续"
            self.cd_start_btn._draw(Theme.SUCCESS)
        else:
            if self.cd_remaining == 0:
                try:
                    self.cd_seconds = int(self.cd_h_var.get()) * 3600 + \
                                      int(self.cd_m_var.get()) * 60 + int(self.cd_s_var.get())
                    if self.cd_seconds <= 0:
                        messagebox.showwarning("提示", "请设置大于0的时间！")
                        return
                    self.cd_remaining = self.cd_seconds
                except ValueError:
                    messagebox.showwarning("提示", "请输入有效数字！")
                    return
            self.cd_running = True
            self.cd_start_btn._text = "暂停"
            self.cd_start_btn._draw(Theme.WARNING)
            self._cd_tick()

    def _cd_tick(self):
        if not self.cd_running:
            return
        try:
            self.cd_remaining -= 1
            t = max(0, self.cd_remaining)
            h, rem = divmod(t, 3600)
            m, s = divmod(rem, 60)
            text = f"{h:02d}:{m:02d}:{s:02d}"
            cur = self.cd_display.cget('text')
            if cur != text:
                AnimationEngine.roll_number(self.cd_display, cur, text, duration=200)
            self.cd_display.config(text=text)
            if self.cd_remaining <= 0:
                self._cd_finish()
                return
            self.after(1000, self._cd_tick)
        except Exception:
            self.cd_running = False

    def _cd_finish(self):
        self.cd_running = False
        self.cd_start_btn._text = "开始倒计时"
        self.cd_start_btn._draw(Theme.SUCCESS)
        self.cd_display.config(text="时间到!", fg=Theme.DANGER)
        AnimationEngine.glow_label(self.cd_display, Theme.DANGER)
        self._show_popup("⏰ 时间到！", "倒计时结束")

    def _cd_reset(self):
        self.cd_running = False
        self.cd_start_btn._text = "开始倒计时"
        self.cd_start_btn._draw(Theme.SUCCESS)
        try:
            self.cd_seconds = int(self.cd_h_var.get()) * 3600 + \
                              int(self.cd_m_var.get()) * 60 + int(self.cd_s_var.get())
            self.cd_remaining = self.cd_seconds
            t = max(0, self.cd_remaining)
            h, rem = divmod(t, 3600)
            m, s = divmod(rem, 60)
            self.cd_display.config(text=f"{h:02d}:{m:02d}:{s:02d}", fg=Theme.PRIMARY)
        except ValueError:
            self.cd_remaining = 0
            self.cd_display.config(text="00:00:00", fg=Theme.PRIMARY)

    def _show_popup(self, title, msg):
        try:
            popup = tk.Toplevel(self)
            popup.title(title)
            popup.geometry("300x180")
            popup.configure(bg='#FFEBEE')
            popup.attributes('-topmost', True)
            popup.transient(self.winfo_toplevel())
            popup.grab_set()
            tk.Label(popup, text="⏰", font=('Segoe UI Emoji', 40),
                     bg='#FFEBEE').pack(pady=(12, 0))
            tk.Label(popup, text=title, font=('Microsoft YaHei', 14, 'bold'),
                     bg='#FFEBEE', fg='#C62828').pack(pady=5)
            tk.Label(popup, text=msg, font=Theme.FONT_BODY,
                     bg='#FFEBEE', fg=Theme.TEXT_SECONDARY).pack()
            RoundedButton(popup, text="知道了", command=popup.destroy,
                           bg=Theme.SUCCESS, width=100, height=32).pack(pady=10)
            popup.update_idletasks()
            AnimationEngine.animate_popup(popup, duration=280)
            try:
                popup.bell()
            except Exception:
                pass
        except Exception:
            messagebox.showinfo("⏰", title)


class AnniversaryPage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=Theme.BG, **kwargs)
        self.items = []
        self._build_ui()
        self._load()

    def _build_ui(self):
        tk.Label(self, text="📅 纪念日管理", font=Theme.FONT_HEADER,
                 bg=Theme.BG, fg=Theme.TEXT).pack(pady=(10, 5))
        af = tk.Frame(self, bg=Theme.CARD)
        af.pack(fill='x', padx=15, pady=5)
        for i, (lbl, key) in enumerate([
            ('名称', 'name'), ('日期(YYYY-MM-DD)', 'date'), ('类型', 'type')]):
            tk.Label(af, text=lbl, font=Theme.FONT_BODY, bg=Theme.CARD,
                     fg=Theme.TEXT_SECONDARY).grid(row=0, column=i*2, padx=5, pady=8, sticky='e')
        self.name_var = tk.StringVar()
        tk.Entry(af, textvariable=self.name_var, width=12,
                   font=Theme.FONT_BODY, bd=0, highlightthickness=1,
                   highlightbackground=Theme.BORDER,
                   highlightcolor=Theme.PRIMARY).grid(row=0, column=1, padx=3, pady=8)
        self.date_var = tk.StringVar()
        tk.Entry(af, textvariable=self.date_var, width=12,
                   font=Theme.FONT_BODY, bd=0, highlightthickness=1,
                   highlightbackground=Theme.BORDER,
                   highlightcolor=Theme.PRIMARY).grid(row=0, column=3, padx=3, pady=8)
        self.type_var = tk.StringVar(value='每年重复')
        ttk.Combobox(af, textvariable=self.type_var,
                       values=['每年重复', '仅一次', '每周重复'],
                       width=10, state='readonly',
                       font=Theme.FONT_BODY).grid(row=0, column=5, padx=3, pady=8)
        RoundedButton(af, text="＋ 添加", command=self._add,
                       bg=Theme.PRIMARY, width=90, height=30).grid(row=0, column=6, padx=10, pady=8)
        st = ttk.Style()
        st.configure('Anniv.Treeview', background=Theme.CARD, foreground=Theme.TEXT,
                      fieldbackground=Theme.CARD, font=Theme.FONT_BODY, rowheight=28)
        st.configure('Anniv.Treeview.Heading', font=Theme.FONT_BODY_BOLD,
                      background=Theme.PRIMARY, foreground='white')
        lf = tk.Frame(self, bg=Theme.BG)
        lf.pack(fill='both', expand=True, padx=15, pady=5)
        cols = ('name', 'date', 'type', 'days')
        self.tree = ttk.Treeview(lf, columns=cols, show='headings',
                                  height=10, style='Anniv.Treeview')
        for col, txt, w in [('name','名称',140),('date','日期',110),
                             ('type','类型',90),('days','剩余/已过',140)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor='center' if col != 'name' else 'w')
        vsb = ttk.Scrollbar(lf, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        self.tree.bind('<Double-1>', self._on_double)
        bf = tk.Frame(self, bg=Theme.BG)
        bf.pack(fill='x', padx=15, pady=3)
        RoundedButton(bf, text="🗑️ 删除选中", command=self._delete,
                       bg=Theme.DANGER, width=110, height=30).pack(side='left', padx=5)
        RoundedButton(bf, text="🔄 刷新", command=self._refresh,
                       bg=Theme.PRIMARY, width=80, height=30).pack(side='left', padx=5)
        self.stats = tk.Label(self, text="", font=Theme.FONT_SMALL,
                               bg=Theme.BG, fg=Theme.TEXT_SECONDARY)
        self.stats.pack(pady=3)

    def _load(self):
        try:
            self.items = DataManager.load('anniversaries.json', {}).get('items', [])
            self._refresh()
        except Exception:
            self.items = []

    def _add(self):
        try:
            name = self.name_var.get().strip()
            date_str = self.date_var.get().strip()
            a_type = self.type_var.get()
            if not name:
                messagebox.showwarning("提示", "请输入名称！")
                return
            if not date_str:
                messagebox.showwarning("提示", "请输入日期！")
                return
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            self.items.append({'name': name, 'date': date_str, 'type': a_type})
            DataManager.save('anniversaries.json', {'items': self.items})
            self.name_var.set('')
            self.date_var.set('')
            self._refresh()
        except ValueError:
            messagebox.showerror("错误", "日期格式错误！请使用 YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _days_text(self, item):
        try:
            today = datetime.date.today()
            date = datetime.datetime.strptime(item['date'], '%Y-%m-%d').date()
            t = item.get('type', '每年重复')
            if t == '仅一次':
                d = (date - today).days
                return f"还有 {d} 天" if d >= 0 else f"已过 {-d} 天"
            elif t == '每周重复':
                d = (date - today).days % 7
                return "就在今天!" if d == 0 else f"还有 {d} 天"
            else:
                nd = date.replace(year=today.year)
                if nd < today:
                    nd = date.replace(year=today.year + 1)
                d = (nd - today).days
                return "就在今天! 🎉" if d == 0 else f"还有 {d} 天"
        except Exception:
            return "计算错误"

    def _sort_key(self, item):
        try:
            today = datetime.date.today()
            date = datetime.datetime.strptime(item['date'], '%Y-%m-%d').date()
            t = item.get('type', '每年重复')
            if t == '仅一次':
                return abs((date - today).days)
            elif t == '每周重复':
                return (date - today).days % 7
            else:
                nd = date.replace(year=today.year)
                if nd < today:
                    nd = date.replace(year=today.year + 1)
                return (nd - today).days
        except Exception:
            return 999999

    def _refresh(self):
        try:
            for i in self.tree.get_children():
                self.tree.delete(i)
            for item in sorted(self.items, key=self._sort_key):
                self.tree.insert('', 'end', values=(
                    item['name'], item['date'], item.get('type', '每年重复'),
                    self._days_text(item)))
            self.stats.config(
                text=f"共 {len(self.items)} 个纪念日  |  "
                     f"今日: {datetime.date.today().strftime('%Y-%m-%d')}")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请先选择要删除的项！")
            return
        if not messagebox.askyesno("确认", f"确定要删除 {len(sel)} 个纪念日吗？"):
            return
        try:
            to_del = []
            for s in sel:
                v = self.tree.item(s, 'values')
                for i, item in enumerate(self.items):
                    if item['name'] == v[0] and item['date'] == v[1]:
                        to_del.append(i)
                        break
            for i in sorted(to_del, reverse=True):
                del self.items[i]
            DataManager.save('anniversaries.json', {'items': self.items})
            self._refresh()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _on_double(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0], 'values')
        d = self._days_text({'name': v[0], 'date': v[1], 'type': v[2]})
        try:
            popup = tk.Toplevel(self)
            popup.title("纪念日详情")
            popup.geometry("300x160")
            popup.configure(bg='#E8EAF6')
            popup.transient(self.winfo_toplevel())
            popup.grab_set()
            tk.Label(popup, text="📅", font=('Segoe UI Emoji', 36),
                     bg='#E8EAF6').pack(pady=(12, 0))
            tk.Label(popup, text=v[0], font=('Microsoft YaHei', 14, 'bold'),
                     bg='#E8EAF6', fg=Theme.PRIMARY).pack(pady=3)
            tk.Label(popup, text=f"日期: {v[1]}  |  类型: {v[2]}",
                     font=Theme.FONT_SMALL, bg='#E8EAF6',
                     fg=Theme.TEXT_SECONDARY).pack()
            tk.Label(popup, text=d, font=('Microsoft YaHei', 12, 'bold'),
                     bg='#E8EAF6', fg=Theme.ACCENT).pack(pady=5)
            RoundedButton(popup, text="关闭", command=popup.destroy,
                           bg=Theme.PRIMARY, width=90, height=28).pack(pady=5)
            popup.update_idletasks()
            AnimationEngine.animate_popup(popup, duration=280)
        except Exception:
            pass


class YanbaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("闫巴工具箱 YBv1.0")
        self.geometry("540x620")
        self.minsize(500, 560)
        DataManager.init_app_dir()
        self._set_window_icon()
        self._theme = DataManager.load('settings.json', {}).get('theme', 'light')
        if self._theme == 'dark':
            Theme.set_dark()
        self.configure(bg=Theme.BG)
        self._configure_notebook_style()
        self.current_page = None
        self.pages = {}
        self._nav_bar = None
        self._theme_btn = None
        self._home_theme_widgets = []
        self._build_home()
        self._show_page('home')
        self._add_theme_btn_home()
        self.after(2000, self._check_capsules)


    def _set_window_icon(self):
        try:
            if getattr(sys, 'frozen', False):
                base = os.path.dirname(sys.executable)
            else:
                base = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base, 'icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                return
        except Exception:
            pass
        try:
            import base64 as _b64
            _ICON_B64 = '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'
            try:
                self._icon_img = tk.PhotoImage(data=_b64.b64decode(_ICON_B64))
                self.iconphoto(True, self._icon_img)
            except Exception:
                pass
        except Exception:
            pass

    def _configure_notebook_style(self):
        try:
            st = ttk.Style()
            st.theme_use('clam')
            st.configure('TNotebook', background=Theme.BG, borderwidth=0)
            st.configure('TNotebook.Tab', padding=[16, 8], font=Theme.FONT_BODY_BOLD,
                        background=Theme.CARD, foreground=Theme.TEXT)
            st.map('TNotebook.Tab', background=[('selected', Theme.PRIMARY)],
                   foreground=[('selected', 'white')])
        except Exception:
            pass

    def _toggle_theme(self):
        try:
            if self._theme == 'light':
                self._theme = 'dark'
                Theme.set_dark()
            else:
                self._theme = 'light'
                Theme.set_light()
            DataManager.save('settings.json', {'theme': self._theme})
            self._apply_theme()
        except Exception:
            pass

    def _apply_theme(self):
        try:
            self.configure(bg=Theme.BG)
            self._configure_notebook_style()
            for w in getattr(self, '_home_theme_widgets', []):
                try:
                    icon = "☀" if self._theme == 'dark' else "☾"
                    w.config(text=icon, bg=Theme.BG, fg=Theme.TEXT_SECONDARY)
                except Exception:
                    pass
            for key in list(self.pages.keys()):
                try:
                    old = self.pages[key]
                    old.destroy()
                except Exception:
                    pass
                self.pages[key] = None
            self.pages = {}
            saved_page = self.current_page
            self.home_frame.destroy()
            self._build_home()
            if saved_page and saved_page != 'home':
                self._show_page(saved_page)
            else:
                self._show_page('home')
                self._add_theme_btn_home()
        except Exception:
            pass

    def _build_home(self):
        self.home_frame = tk.Frame(self, bg=Theme.BG)
        tk.Label(self.home_frame, text="闫 巴 工 具 箱", font=Theme.FONT_TITLE,
                 bg=Theme.BG, fg=Theme.PRIMARY).pack(pady=(30, 5))
        tk.Label(self.home_frame, text="— 便捷桌面小工具集 —",
                 font=Theme.FONT_BODY, bg=Theme.BG, fg=Theme.TEXT_SECONDARY).pack(pady=(0, 20))

        tools = [
            ("🎲", "随机决定器", "自定义选项 / 抽签 / 抛硬币", Theme.ACCENT, 'decider'),
            ("📝", "桌面便签", "置顶窗口 / 自动保存", Theme.WARNING, 'notes'),
            ("⏱️", "计时工具", "番茄钟 / 自定义倒计时", Theme.PRIMARY, 'timer'),
            ("📅", "纪念日管理", "录入日期 / 剩余天数", '#E91E63', 'anniversary'),
            ("💰", "简易记账", "收支记录 / 极简流水", '#4CAF50', 'accounting'),
            ("⏳", "时光胶囊", "写下文字 / 定时解锁", '#9C27B0', 'capsule'),
        ]
        for emoji, name, desc, color, key in tools:
            card = tk.Frame(self.home_frame, bg=Theme.CARD, cursor='hand2')
            card.pack(fill='x', padx=35, pady=7)
            lf = tk.Frame(card, bg=Theme.CARD)
            lf.pack(side='left', padx=15, pady=10)
            tk.Label(lf, text=emoji, font=('Segoe UI Emoji', 30),
                     bg=Theme.CARD).pack()
            rf = tk.Frame(card, bg=Theme.CARD)
            rf.pack(side='left', fill='x', expand=True, pady=10)
            tk.Label(rf, text=name, font=Theme.FONT_BODY_BOLD,
                     bg=Theme.CARD, fg=Theme.TEXT).pack(anchor='w')
            tk.Label(rf, text=desc, font=Theme.FONT_SMALL,
                     bg=Theme.CARD, fg=Theme.TEXT_MUTED).pack(anchor='w')
            arrow = tk.Label(card, text="→", font=('Microsoft YaHei', 16),
                               bg=Theme.CARD, fg=color)
            arrow.pack(side='right', padx=15)
            for w in [card, lf, rf, arrow] + list(lf.winfo_children()) + list(rf.winfo_children()):
                w.bind('<Button-1>', lambda e, k=key: self._show_page(k))
                w.bind('<Enter>', lambda e, c=card: c.configure(bg='#E8EAF6' if self._theme == 'dark' else '#F5F5F5'))
                w.bind('<Leave>', lambda e, c=card: c.configure(bg=Theme.CARD))

        # 今日纪念日
        try:
            today_items = self._get_today_items()
            if today_items:
                tip = tk.Frame(self.home_frame, bg='#FFEBEE')
                tip.pack(fill='x', padx=35, pady=(15, 10))
                tk.Label(tip, text="📅 今日提醒", font=Theme.FONT_BODY_BOLD,
                         bg='#FFEBEE', fg='#C62828').pack(anchor='w', padx=15, pady=(8, 2))
                for item in today_items[:3]:
                    tk.Label(tip, text=f"  • {item['name']} ({item['date']})",
                             font=Theme.FONT_SMALL, bg='#FFEBEE',
                             fg=Theme.TEXT_SECONDARY, anchor='w').pack(anchor='w', padx=20)
                tk.Label(tip, text=f"共 {len(today_items)} 个纪念日临近",
                         font=Theme.FONT_SMALL, bg='#FFEBEE',
                         fg='#C62828').pack(anchor='w', padx=15, pady=(3, 8))
        except Exception:
            pass

    def _get_today_items(self):
        items = DataManager.load('anniversaries.json', {}).get('items', [])
        today = datetime.date.today()
        result = []
        for item in items:
            try:
                date = datetime.datetime.strptime(item['date'], '%Y-%m-%d').date()
                d = item.get('type', '每年重复')
                if d == '仅一次':
                    diff = (date - today).days
                    if 0 <= diff <= 3:
                        result.append(item)
                elif d == '每周重复':
                    diff = (date - today).days % 7
                    if diff <= 1:
                        result.append(item)
                else:
                    nd = date.replace(year=today.year)
                    if nd < today:
                        nd = date.replace(year=today.year + 1)
                    diff = (nd - today).days
                    if 0 <= diff <= 7:
                        result.append(item)
            except Exception:
                pass
        return result

    def _show_page(self, key):
        try:
            # Destroy previous nav bar if exists
            if hasattr(self, '_nav_bar') and self._nav_bar:
                try:
                    self._nav_bar.destroy()
                except Exception:
                    pass
                self._nav_bar = None

            if self.current_page and self.current_page != 'home':
                p = self.pages.get(self.current_page)
                if p:
                    p.pack_forget()
            if key == 'home':
                self.title("闫巴工具箱 YBv1.0")
                self.home_frame.pack(fill='both', expand=True)
                self.current_page = 'home'
                self._add_theme_btn_home()
                return
            self.home_frame.pack_forget()
            if key not in self.pages:
                cls = {'decider': DeciderPage, 'notes': NotePage,
                        'timer': TimerPage, 'anniversary': AnniversaryPage,
                        'accounting': AccountingPage, 'capsule': TimeCapsulePage}.get(key)
                if cls:
                    self.pages[key] = cls(self)
            page = self.pages[key]
            page.pack(fill='both', expand=True, pady=(32, 0))
            self._nav_bar = tk.Frame(self, bg=Theme.BG, height=32)
            self._nav_bar.place(x=0, y=0, relwidth=1, height=32)
            nav_border = tk.Frame(self._nav_bar, bg=Theme.TEXT_MUTED, height=1)
            nav_border.pack(side='bottom', fill='x')

            back = RoundedButton(self._nav_bar, text="<", command=lambda: self._show_page('home'),
                              width=36, height=28, radius=14, bg=Theme.BG,
                              fg=Theme.TEXT)
            back.place(x=2, y=2, width=36, height=28)

            titles = {'decider': '随机决定器', 'notes': '桌面便签',
                       'timer': '计时工具', 'anniversary': '纪念日管理',
                       'accounting': '简易记账', 'capsule': '时光胶囊'}
            tk.Label(self._nav_bar, text=titles.get(key, ''), font=Theme.FONT_BODY_BOLD,
                     bg=Theme.BG, fg=Theme.TEXT).place(relx=0.5, rely=0.4, anchor='center')

            theme_icon = "☀" if self._theme == 'dark' else "☾"
            self._theme_btn = tk.Label(self._nav_bar, text=theme_icon,
                                         font=('Segoe UI', 14),
                                         bg=Theme.BG, fg=Theme.TEXT_SECONDARY,
                                         cursor='hand2', padx=8)
            self._theme_btn.place(relx=1.0, y=0, anchor='ne', height=31)
            self._theme_btn.bind('<Button-1>', lambda e: self._toggle_theme())
            self._theme_btn.bind('<Enter>', lambda e: self._theme_btn.config(
                fg=Theme.PRIMARY))
            self._theme_btn.bind('<Leave>', lambda e: self._theme_btn.config(
                fg=Theme.TEXT_SECONDARY))

            self.current_page = key
            try:
                AnimationEngine.fade_in(page, duration=300)
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("错误", f"页面加载失败: {e}")

    def _add_theme_btn_home(self):
        for w in getattr(self, '_home_theme_widgets', []):
            try:
                w.destroy()
            except Exception:
                pass
        self._home_theme_widgets = []
        icon = "☀" if self._theme == 'dark' else "☾"
        btn = tk.Label(self, text=icon, font=('Segoe UI', 14),
                          bg=Theme.BG, fg=Theme.TEXT_SECONDARY,
                          cursor='hand2', padx=10, pady=5)
        btn.place(relx=1.0, y=0, anchor='ne')
        btn.bind('<Button-1>', lambda e: self._toggle_theme())
        btn.bind('<Enter>', lambda e: btn.config(fg=Theme.PRIMARY))
        btn.bind('<Leave>', lambda e: btn.config(fg=Theme.TEXT_SECONDARY))
        self._home_theme_widgets.append(btn)

    def add_note(self):
        if 'notes' in self.pages:
            self.pages['notes'].add_note()


    def _check_capsules(self):
        try:
            data = DataManager.load('capsules.json', {})
            capsules = data.get('capsules', [])
            today = datetime.date.today()
            due = []
            for i, cap in enumerate(capsules):
                if not cap.get('unlocked', False):
                    try:
                        ud = datetime.datetime.strptime(cap.get('unlock_date', ''), '%Y-%m-%d').date()
                        if ud <= today:
                            due.append((i, cap))
                    except Exception:
                        pass
            if due:
                for idx, cap in due:
                    cap['unlocked'] = True
                    capsules[idx] = cap
                data['capsules'] = capsules
                DataManager.save('capsules.json', data)
                self._show_capsule_popup(due)
        except Exception:
            pass

    def _show_capsule_popup(self, due_capsules):
        try:
            popup = tk.Toplevel(self)
            popup.title("🔓 时光胶囊解锁")
            popup.configure(bg='#F3E5F5')
            popup.transient(self)
            popup.grab_set()
            popup.geometry("380x300")

            tk.Label(popup, text="⏳", font=('Segoe UI Emoji', 36),
                     bg='#F3E5F5').pack(pady=(15, 0))
            tk.Label(popup, text="时光胶囊已解锁！", font=('Microsoft YaHei', 14, 'bold'),
                     bg='#F3E5F5', fg=Theme.PRIMARY).pack(pady=5)

            container = tk.Frame(popup, bg='#F3E5F5')
            container.pack(fill='both', expand=True, padx=15, pady=5)

            canvas = tk.Canvas(container, bg='#F3E5F5', bd=0, highlightthickness=0)
            sb = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
            inner = tk.Frame(canvas, bg='#F3E5F5')
            inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            canvas.create_window((0, 0), window=inner, anchor='nw')
            canvas.configure(yscrollcommand=sb.set)
            canvas.pack(side='left', fill='both', expand=True)
            sb.pack(side='right', fill='y')

            for i, cap in due_capsules:
                tk.Label(inner, text=f"解锁日期: {cap.get('unlock_date', '')}",
                         font=Theme.FONT_SMALL, bg='#F3E5F5',
                         fg=Theme.TEXT_SECONDARY).pack(anchor='w', pady=(5, 2))
                tk.Label(inner, text=cap.get('text', ''), font=Theme.FONT_BODY,
                         bg='#F3E5F5', fg=Theme.TEXT, wraplength=320,
                         justify='left').pack(anchor='w', pady=(0, 8))

            RoundedButton(popup, text="好的", command=popup.destroy,
                          bg=Theme.PRIMARY, width=100, height=32).pack(pady=10)
            popup.update_idletasks()
            AnimationEngine.animate_popup(popup, duration=300)
        except Exception:
            messagebox.showinfo("时光胶囊", "有时光胶囊已解锁！")


def global_exception(exc_type, exc_value, exc_tb):
    try:
        log_dir = DataManager.APP_DIR or os.path.join(os.path.expanduser('~'), '.yanba_data')
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, 'error.log'), 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n时间: {datetime.datetime.now()}\n")
            f.write(f"异常: {exc_type.__name__}: {exc_value}\n")
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    except Exception:
        pass
    try:
        messagebox.showerror("程序异常", f"程序遇到错误，但不会退出：\n\n{exc_value}")
    except Exception:
        pass


def main():
    sys.excepthook = global_exception
    app = YanbaApp()

    def on_closing():
        try:
            r = messagebox.askyesnocancel("退出确认",
                "是否要退出闫巴工具箱？\n\n是: 退出  |  否: 最小化  |  取消: 返回")
            if r is True:
                app.destroy()
            elif r is False:
                app.iconify()
        except Exception:
            app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()


if __name__ == '__main__':
    main()
