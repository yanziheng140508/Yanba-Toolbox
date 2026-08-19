# -*- coding: utf-8 -*-
"""
工具箱 YBv1.2 - 完整独立 tkinter GUI 应用
作者: YB
仅使用 Python 标准库
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import json
import base64
import re
import os
import sys
import random
import string
import hashlib
import difflib
import time
import datetime
import py_compile
import uuid
import copy
from io import BytesIO

# =========================================================
#  全局主题配色
# =========================================================
DARK = {
    "BG": "#1A1A2E",
    "CARD": "#252538",
    "PRIMARY": "#7986CB",
    "SIDEBAR_BG": "#1A1A2E",
    "TEXT": "#E8E8F0",
    "MUTED": "#9E9EB8",
    "BORDER": "#3A3A52",
    "HOVER": "#2D2D44",
    "SELECTED": "#3A3A52",
    "SUCCESS": "#81C784",
    "WARNING": "#FFB74D",
    "ERROR": "#EF5350",
}

LIGHT = {
    "BG": "#F0F2F5",
    "CARD": "#FFFFFF",
    "PRIMARY": "#3F51B5",
    "SIDEBAR_BG": "#263238",
    "TEXT": "#212121",
    "MUTED": "#757575",
    "BORDER": "#E0E0E0",
    "HOVER": "#F5F5F5",
    "SELECTED": "#E8EAF6",
    "SUCCESS": "#66BB6A",
    "WARNING": "#FFA726",
    "ERROR": "#EF5350",
}

THEME = copy.deepcopy(DARK)
THEME_MODE = "dark"

def toggle_theme():
    global THEME, THEME_MODE
    if THEME_MODE == "dark":
        THEME.update(LIGHT)
        THEME_MODE = "light"
    else:
        THEME.update(DARK)
        THEME_MODE = "dark"

# =========================================================
#  数据目录
# =========================================================
def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(get_app_dir(), "yanba_data")
os.makedirs(DATA_DIR, exist_ok=True)

def load_json(name, default):
    path = os.path.join(DATA_DIR, name)
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(name, data):
    try:
        path = os.path.join(DATA_DIR, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存 {name} 失败: {e}")

# =========================================================
#  自定义控件
# =========================================================
class RoundedContainer(tk.Canvas):
    """圆角矩形容器，内部有 Frame"""
    def __init__(self, master, bg=None, radius=14, padx=0, pady=0, **kwargs):
        self._bg = bg if bg else THEME["CARD"]
        self._radius = radius
        self._padx = padx
        self._pady = pady
        super().__init__(master, bg=master["bg"] if hasattr(master, "__getitem__") else THEME["BG"],
                         highlightthickness=0, bd=0, **kwargs)
        self._rect_id = None
        self.inner = tk.Frame(self, bg=self._bg)
        self.bind("<Configure>", self._on_resize)
        self._after_id = None

    def _on_resize(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 2 or h < 2:
            return
        r = self._radius
        # 画圆角矩形
        self.create_oval(0, 0, 2*r, 2*r, fill=self._bg, outline="")
        self.create_oval(w-2*r, 0, w, 2*r, fill=self._bg, outline="")
        self.create_oval(0, h-2*r, 2*r, h, fill=self._bg, outline="")
        self.create_oval(w-2*r, h-2*r, w, h, fill=self._bg, outline="")
        self.create_rectangle(r, 0, w-r, h, fill=self._bg, outline="")
        self.create_rectangle(0, r, w, h-r, fill=self._bg, outline="")
        # 放置 inner frame
        self.create_window(self._padx, self._pady, anchor="nw", window=self.inner,
                           width=max(1, w - 2*self._padx), height=max(1, h - 2*self._pady))

    def set_bg(self, color):
        self._bg = color
        self.inner.configure(bg=color)
        self._on_resize()

class CircleAvatar(tk.Canvas):
    """圆形头像"""
    def __init__(self, master, text, bg=None, fg="white", size=36, **kwargs):
        self._text = text
        self._bg = bg if bg else THEME["PRIMARY"]
        self._fg = fg
        self._size = size
        super().__init__(master, width=size, height=size,
                         bg=master["bg"] if hasattr(master, "__getitem__") else THEME["BG"],
                         highlightthickness=0, bd=0, **kwargs)
        self.bind("<Configure>", lambda e: self._draw())
        self.after(10, self._draw)

    def _draw(self):
        self.delete("all")
        s = self._size
        self.create_oval(1, 1, s-1, s-1, fill=self._bg, outline="")
        self.create_text(s//2, s//2, text=self._text, fill=self._fg,
                         font=("Microsoft YaHei", int(s*0.38), "bold"))

    def set_text(self, text):
        self._text = text
        self._draw()

    def set_bg(self, color):
        self._bg = color
        self._draw()

class RoundedButton(tk.Canvas):
    """圆角按钮（椭圆+矩形方式）"""
    def __init__(self, master, text, command=None, bg=None, fg="white",
                 radius=10, width=120, height=36, font=None, **kwargs):
        self._text = text
        self._bg = bg if bg else THEME["PRIMARY"]
        self._fg = fg
        self._radius = radius
        self._btn_w = width
        self._btn_h = height
        self._command = command
        self._font = font or ("Microsoft YaHei", 10)
        super().__init__(master, width=width, height=height,
                         bg=master["bg"] if hasattr(master, "__getitem__") else THEME["BG"],
                         highlightthickness=0, bd=0, cursor="hand2", **kwargs)
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self._hover = False
        self.after(10, self._draw)

    def _lighter(self, color, pct=1.1):
        color = color.lstrip("#")
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = min(255, int(r*pct))
        g = min(255, int(g*pct))
        b = min(255, int(b*pct))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _darker(self, color, pct=0.9):
        color = color.lstrip("#")
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, int(r*pct))
        g = max(0, int(g*pct))
        b = max(0, int(b*pct))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self):
        self.delete("all")
        w = self._btn_w
        h = self._btn_h
        r = self._radius
        color = self._lighter(self._bg, 1.08) if self._hover else self._bg
        # 圆角
        self.create_oval(0, 0, 2*r, 2*r, fill=color, outline="")
        self.create_oval(w-2*r, 0, w, 2*r, fill=color, outline="")
        self.create_oval(0, h-2*r, 2*r, h, fill=color, outline="")
        self.create_oval(w-2*r, h-2*r, w, h, fill=color, outline="")
        self.create_rectangle(r, 0, w-r, h, fill=color, outline="")
        self.create_rectangle(0, r, w, h-r, fill=color, outline="")
        self.create_text(w//2, h//2, text=self._text, fill=self._fg, font=self._font)

    def _on_enter(self, e):
        self._hover = True
        self._draw()

    def _on_leave(self, e):
        self._hover = False
        self._draw()

    def _on_click(self, e):
        try:
            if self._command:
                self._command()
        except Exception as ex:
            messagebox.showerror("错误", f"操作失败: {ex}")

    def set_text(self, text):
        self._text = text
        self._draw()

    def set_bg(self, color):
        self._bg = color
        self._draw()

# =========================================================
#  工具页面基类
# =========================================================
class BasePage(tk.Frame):
    def __init__(self, master, app, title=""):
        super().__init__(master, bg=THEME["BG"])
        self.app = app
        self.title_text = title
        self._build()

    def _build(self):
        # 顶部标题条
        header = tk.Frame(self, bg=THEME["BG"])
        header.pack(fill="x", padx=20, pady=(12, 6))
        back = RoundedButton(header, "← 返回", command=self.app.go_home,
                             bg=THEME["CARD"], fg=THEME["TEXT"], width=90, height=32, radius=8)
        back.pack(side="left")
        tk.Label(header, text=self.title_text, fg=THEME["TEXT"], bg=THEME["BG"],
                 font=("Microsoft YaHei", 15, "bold")).pack(side="left", padx=12)
        # 内容容器：单独的 Frame，确保 build_content 能 fill/expand 且不被 header 遮挡
        self._content_wrap = tk.Frame(self, bg=THEME["BG"])
        self._content_wrap.pack(fill="both", expand=True)
        self.build_content()

    def build_content(self):
        pass

    def safe(self, func, *a, **k):
        try:
            return func(*a, **k)
        except Exception as e:
            messagebox.showerror("错误", f"操作失败: {e}")

# =========================================================
#  1. JSON 格式化
# =========================================================
class JsonPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app, "JSON格式化")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        # 按钮区
        bar = tk.Frame(wrap, bg=THEME["BG"])
        bar.pack(fill="x", pady=(0, 8))
        for t, cmd in [("美化", self._pretty), ("压缩", self._compress),
                       ("校验", self._validate), ("复制", self._copy), ("清除", self._clear)]:
            RoundedButton(bar, t, command=cmd, width=88, height=32, radius=8).pack(side="left", padx=4)
        # 文本区
        rc = RoundedContainer(wrap, radius=14, padx=12, pady=12)
        rc.pack(fill="both", expand=True)
        self.txt = tk.Text(rc.inner, bg=THEME["CARD"], fg=THEME["TEXT"],
                           insertbackground=THEME["TEXT"], bd=0, relief="flat",
                           font=("Consolas", 11), wrap="word")
        self.txt.pack(fill="both", expand=True)

    def _get(self):
        return self.txt.get("1.0", "end").strip()

    def _pretty(self):
        s = self._get()
        if not s:
            return
        try:
            obj = json.loads(s)
            self.txt.delete("1.0", "end")
            self.txt.insert("1.0", json.dumps(obj, ensure_ascii=False, indent=2))
        except Exception as e:
            messagebox.showerror("JSON 错误", str(e))

    def _compress(self):
        s = self._get()
        if not s:
            return
        try:
            obj = json.loads(s)
            self.txt.delete("1.0", "end")
            self.txt.insert("1.0", json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
        except Exception as e:
            messagebox.showerror("JSON 错误", str(e))

    def _validate(self):
        s = self._get()
        if not s:
            messagebox.showinfo("校验", "空内容")
            return
        try:
            json.loads(s)
            messagebox.showinfo("校验", "✅ 合法的 JSON")
        except Exception as e:
            messagebox.showerror("JSON 错误", str(e))

    def _copy(self):
        s = self._get()
        self.clipboard_clear()
        self.clipboard_append(s)
        messagebox.showinfo("复制", "已复制到剪贴板")

    def _clear(self):
        self.txt.delete("1.0", "end")

# =========================================================
#  2. Base64 编解码
# =========================================================
class Base64Page(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app, "Base64 编解码")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        cols = tk.Frame(wrap, bg=THEME["BG"])
        cols.pack(fill="both", expand=True)
        # 左列
        lcol = tk.Frame(cols, bg=THEME["BG"])
        lcol.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(lcol, text="原文", fg=THEME["TEXT"], bg=THEME["BG"],
                 font=("Microsoft YaHei", 10, "bold"), anchor="w").pack(fill="x", pady=(0,4))
        rc1 = RoundedContainer(lcol, radius=14, padx=10, pady=10)
        rc1.pack(fill="both", expand=True)
        self.t1 = tk.Text(rc1.inner, bg=THEME["CARD"], fg=THEME["TEXT"],
                          insertbackground=THEME["TEXT"], bd=0, font=("Consolas", 11), wrap="word")
        self.t1.pack(fill="both", expand=True)
        # 中间按钮
        btns = tk.Frame(cols, bg=THEME["BG"])
        btns.pack(side="left", fill="y", padx=4)
        tk.Frame(btns, bg=THEME["BG"], height=30).pack()
        RoundedButton(btns, "编码 →", command=self._encode, width=92, height=36, radius=8).pack(pady=6)
        RoundedButton(btns, "← 解码", command=self._decode, width=92, height=36, radius=8,
                      bg=THEME["CARD"], fg=THEME["TEXT"]).pack(pady=6)
        # 右列
        rcol = tk.Frame(cols, bg=THEME["BG"])
        rcol.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(rcol, text="Base64", fg=THEME["TEXT"], bg=THEME["BG"],
                 font=("Microsoft YaHei", 10, "bold"), anchor="w").pack(fill="x", pady=(0,4))
        rc2 = RoundedContainer(rcol, radius=14, padx=10, pady=10)
        rc2.pack(fill="both", expand=True)
        self.t2 = tk.Text(rc2.inner, bg=THEME["CARD"], fg=THEME["TEXT"],
                          insertbackground=THEME["TEXT"], bd=0, font=("Consolas", 11), wrap="word")
        self.t2.pack(fill="both", expand=True)

    def _encode(self):
        try:
            s = self.t1.get("1.0", "end").rstrip("\n")
            out = base64.b64encode(s.encode("utf-8")).decode("ascii")
            self.t2.delete("1.0", "end")
            self.t2.insert("1.0", out)
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _decode(self):
        try:
            s = self.t2.get("1.0", "end").strip()
            out = base64.b64decode(s.encode("ascii")).decode("utf-8")
            self.t1.delete("1.0", "end")
            self.t1.insert("1.0", out)
        except Exception as e:
            messagebox.showerror("错误", str(e))

# =========================================================
#  3. 密码生成器
# =========================================================
class PasswordPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app, "密码生成器")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        # 结果显示
        rc = RoundedContainer(wrap, radius=14, padx=16, pady=16)
        rc.pack(fill="x", pady=(0, 16))
        self.result = tk.StringVar(value="点击下方「生成密码」")
        tk.Label(rc.inner, textvariable=self.result, fg=THEME["PRIMARY"],
                 bg=THEME["CARD"], font=("Consolas", 16, "bold")).pack(side="left")
        RoundedButton(rc.inner, "复制", command=self._copy, width=80, height=32, radius=8).pack(side="right")
        # 选项
        card = RoundedContainer(wrap, radius=14, padx=16, pady=16)
        card.pack(fill="x")
        cfg = tk.Frame(card.inner, bg=THEME["CARD"])
        cfg.pack(fill="x")
        tk.Label(cfg, text="密码长度:", fg=THEME["TEXT"], bg=THEME["CARD"],
                 font=("Microsoft YaHei", 10)).grid(row=0, column=0, sticky="w")
        self.len_var = tk.IntVar(value=16)
        self.len_label = tk.Label(cfg, text="16", fg=THEME["PRIMARY"], bg=THEME["CARD"],
                                  font=("Consolas", 12, "bold"))
        self.len_label.grid(row=0, column=1, sticky="w", padx=8)
        scale = tk.Scale(cfg, from_=4, to=64, orient="horizontal", variable=self.len_var,
                         bg=THEME["CARD"], fg=THEME["TEXT"], troughcolor=THEME["HOVER"],
                         activebackground=THEME["PRIMARY"], highlightthickness=0,
                         command=lambda v: self.len_label.configure(text=str(int(float(v)))))
        scale.grid(row=0, column=2, sticky="we", padx=8)
        cfg.grid_columnconfigure(2, weight=1)
        self.lower = tk.BooleanVar(value=True)
        self.upper = tk.BooleanVar(value=True)
        self.num = tk.BooleanVar(value=True)
        self.sym = tk.BooleanVar(value=False)
        opts = [("包含小写 a-z", self.lower), ("包含大写 A-Z", self.upper),
                ("包含数字 0-9", self.num), ("包含符号 !@#$", self.sym)]
        for i, (t, v) in enumerate(opts):
            cb = tk.Checkbutton(cfg, text=t, variable=v, bg=THEME["CARD"], fg=THEME["TEXT"],
                                selectcolor=THEME["CARD"], activebackground=THEME["CARD"],
                                activeforeground=THEME["TEXT"], font=("Microsoft YaHei", 10))
            cb.grid(row=1+i//2, column=i%2, sticky="w", pady=6, padx=4)
        # 生成按钮
        btn_bar = tk.Frame(wrap, bg=THEME["BG"])
        btn_bar.pack(fill="x", pady=16)
        RoundedButton(btn_bar, "🎲 生成密码", command=self._gen, width=180, height=42, radius=10).pack(side="left")

    def _gen(self):
        pool = ""
        if self.lower.get(): pool += string.ascii_lowercase
        if self.upper.get(): pool += string.ascii_uppercase
        if self.num.get():   pool += string.digits
        if self.sym.get():   pool += "!@#$%^&*()-_=+[]{};:,.<>?"
        if not pool:
            messagebox.showwarning("提示", "请至少选择一种字符类型")
            return
        length = self.len_var.get()
        pwd = "".join(random.choice(pool) for _ in range(length))
        self.result.set(pwd)

    def _copy(self):
        pwd = self.result.get()
        if not pwd or pwd.startswith("点击"):
            return
        self.clipboard_clear()
        self.clipboard_append(pwd)
        messagebox.showinfo("复制", "密码已复制")

# =========================================================
#  4. 单位换算
# =========================================================
class UnitPage(BasePage):
    UNITS = {
        "长度": {
            "m": 1.0, "km": 1000.0, "cm": 0.01, "mm": 0.001,
            "mi": 1609.344, "yd": 0.9144, "ft": 0.3048, "in": 0.0254
        },
        "重量": {
            "kg": 1.0, "g": 0.001, "mg": 1e-6, "t": 1000.0,
            "lb": 0.45359237, "oz": 0.0283495
        },
    }

    def __init__(self, master, app):
        super().__init__(master, app, "单位换算")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        # Tabs
        card = RoundedContainer(wrap, radius=14, padx=16, pady=16)
        card.pack(fill="both", expand=True)
        nb_bar = tk.Frame(card.inner, bg=THEME["CARD"])
        nb_bar.pack(fill="x")
        self.tab_var = tk.StringVar(value="长度")
        self.tabs = {}
        for t in ["长度", "重量", "温度"]:
            btn = tk.Label(nb_bar, text=t, padx=16, pady=8, cursor="hand2",
                           font=("Microsoft YaHei", 10, "bold"))
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, tt=t: self._switch_tab(tt))
            self.tabs[t] = btn
        # 内容
        body = tk.Frame(card.inner, bg=THEME["CARD"])
        body.pack(fill="both", expand=True, pady=12)
        self.from_var = tk.StringVar()
        self.to_var = tk.StringVar()
        self.from_unit = tk.StringVar()
        self.to_unit = tk.StringVar()
        # 左输入
        left = tk.Frame(body, bg=THEME["CARD"])
        left.pack(side="left", fill="both", expand=True, padx=8)
        tk.Label(left, text="从", fg=THEME["MUTED"], bg=THEME["CARD"], anchor="w").pack(fill="x")
        e1_rc = RoundedContainer(left, bg=THEME["BG"], radius=10, padx=10, pady=4)
        e1_rc.pack(fill="x", pady=4)
        e1 = tk.Entry(e1_rc.inner, textvariable=self.from_var, bg=THEME["BG"],
                      fg=THEME["TEXT"], bd=0, font=("Consolas", 14), insertbackground=THEME["TEXT"])
        e1.pack(fill="x")
        self.cb_from = ttk.Combobox(left, textvariable=self.from_unit, state="readonly")
        self.cb_from.pack(fill="x", pady=8)
        self.cb_from.bind("<<ComboboxSelected>>", lambda e: self._conv_from())
        # 中间按钮
        mid = tk.Frame(body, bg=THEME["CARD"])
        mid.pack(side="left", fill="y", padx=8)
        tk.Frame(mid, bg=THEME["CARD"], height=30).pack()
        RoundedButton(mid, "→ 换算", command=self._conv_from, width=92, height=34, radius=8).pack(pady=6)
        RoundedButton(mid, "← 换算", command=self._conv_to, width=92, height=34, radius=8,
                      bg=THEME["BG"], fg=THEME["TEXT"]).pack(pady=6)
        # 右输入
        right = tk.Frame(body, bg=THEME["CARD"])
        right.pack(side="left", fill="both", expand=True, padx=8)
        tk.Label(right, text="到", fg=THEME["MUTED"], bg=THEME["CARD"], anchor="w").pack(fill="x")
        e2_rc = RoundedContainer(right, bg=THEME["BG"], radius=10, padx=10, pady=4)
        e2_rc.pack(fill="x", pady=4)
        e2 = tk.Entry(e2_rc.inner, textvariable=self.to_var, bg=THEME["BG"],
                      fg=THEME["TEXT"], bd=0, font=("Consolas", 14), insertbackground=THEME["TEXT"])
        e2.pack(fill="x")
        self.cb_to = ttk.Combobox(right, textvariable=self.to_unit, state="readonly")
        self.cb_to.pack(fill="x", pady=8)
        self.cb_to.bind("<<ComboboxSelected>>", lambda e: self._conv_from())
        # 设置初始 tab
        self._switch_tab("长度")

    def _switch_tab(self, name):
        self.tab_var.set(name)
        for t, b in self.tabs.items():
            if t == name:
                b.configure(bg=THEME["PRIMARY"], fg="white")
            else:
                b.configure(bg=THEME["HOVER"], fg=THEME["TEXT"])
        if name == "温度":
            units = ["°C", "°F", "K"]
        else:
            units = list(self.UNITS[name].keys())
        self.cb_from["values"] = units
        self.cb_to["values"] = units
        self.from_unit.set(units[0])
        self.to_unit.set(units[1] if len(units) > 1 else units[0])

    def _conv_from(self):
        try:
            v = float(self.from_var.get() or 0)
        except Exception:
            self.from_var.set("")
            return
        out = self._convert(v, self.tab_var.get(), self.from_unit.get(), self.to_unit.get())
        self.to_var.set(f"{out:.6g}")

    def _conv_to(self):
        try:
            v = float(self.to_var.get() or 0)
        except Exception:
            self.to_var.set("")
            return
        out = self._convert(v, self.tab_var.get(), self.to_unit.get(), self.from_unit.get())
        self.from_var.set(f"{out:.6g}")

    def _convert(self, v, kind, a, b):
        if kind == "温度":
            return self._conv_temp(v, a, b)
        tbl = self.UNITS[kind]
        base = v * tbl[a]
        return base / tbl[b]

    @staticmethod
    def _conv_temp(v, a, b):
        # 统一转成摄氏度
        if a == "°C": c = v
        elif a == "°F": c = (v - 32) * 5 / 9
        elif a == "K":  c = v - 273.15
        else: c = v
        if b == "°C": return c
        if b == "°F": return c * 9 / 5 + 32
        if b == "K":  return c + 273.15
        return c

# =========================================================
#  5. 颜色选择器
# =========================================================
class ColorPage(BasePage):
    def __init__(self, master, app):
        self.color_hex = "#6366F1"
        self.color_rgb = (99, 102, 241)
        super().__init__(master, app, "颜色选择器")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        # 颜色预览
        top = tk.Frame(wrap, bg=THEME["BG"])
        top.pack(fill="x", pady=(0, 16))
        self.preview = tk.Canvas(top, width=160, height=160, bg=THEME["BG"], highlightthickness=0)
        self.preview.pack(side="left", padx=(0, 24))
        self.preview.bind("<Configure>", lambda e: self._draw_preview())
        info = tk.Frame(top, bg=THEME["BG"])
        info.pack(side="left", fill="both", expand=True)
        self.hex_var = tk.StringVar(value=self.color_hex)
        self.rgb_var = tk.StringVar(value="rgb(99, 102, 241)")
        # HEX
        self._row(info, "HEX:", self.hex_var, self._copy_hex, 0)
        self._row(info, "RGB:", self.rgb_var, self._copy_rgb, 1)
        RoundedButton(info, "🎨 选择颜色", command=self._pick, width=150, height=38, radius=10).grid(row=2, column=0, sticky="w", pady=12)
        self.after(20, self._draw_preview)

    def _row(self, parent, label, var, cmd, r):
        tk.Label(parent, text=label, fg=THEME["TEXT"], bg=THEME["BG"],
                 font=("Microsoft YaHei", 10, "bold"), width=6, anchor="w").grid(row=r, column=0, sticky="w")
        rc = RoundedContainer(parent, bg=THEME["CARD"], radius=10, padx=10, pady=4)
        rc.grid(row=r, column=1, sticky="we", padx=6, pady=4)
        e = tk.Entry(rc.inner, textvariable=var, bg=THEME["CARD"], fg=THEME["TEXT"],
                     bd=0, font=("Consolas", 12), readonlybackground=THEME["CARD"], state="readonly")
        e.pack(fill="x")
        RoundedButton(parent, "复制", command=cmd, width=70, height=30, radius=8,
                      bg=THEME["CARD"], fg=THEME["TEXT"]).grid(row=r, column=2, padx=4)
        parent.grid_columnconfigure(1, weight=1)

    def _draw_preview(self):
        self.preview.delete("all")
        w, h = 160, 160
        r = 20
        c = self.color_hex
        self.preview.create_oval(0, 0, 2*r, 2*r, fill=c, outline="")
        self.preview.create_oval(w-2*r, 0, w, 2*r, fill=c, outline="")
        self.preview.create_oval(0, h-2*r, 2*r, h, fill=c, outline="")
        self.preview.create_oval(w-2*r, h-2*r, w, h, fill=c, outline="")
        self.preview.create_rectangle(r, 0, w-r, h, fill=c, outline="")
        self.preview.create_rectangle(0, r, w, h-r, fill=c, outline="")

    def _pick(self):
        try:
            rgb, hx = colorchooser.askcolor(color=self.color_hex, title="选择颜色")
            if rgb and hx:
                self.color_hex = hx
                self.color_rgb = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
                self.hex_var.set(hx)
                r, g, b = self.color_rgb
                self.rgb_var.set(f"rgb({r}, {g}, {b})")
                self._draw_preview()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _copy_hex(self):
        self.clipboard_clear(); self.clipboard_append(self.hex_var.get())
        messagebox.showinfo("复制", "HEX 已复制")

    def _copy_rgb(self):
        self.clipboard_clear(); self.clipboard_append(self.rgb_var.get())
        messagebox.showinfo("复制", "RGB 已复制")

# =========================================================
#  6. 随机决定器
# =========================================================
class DeciderPage(BasePage):
    def __init__(self, master, app):
        self.options = load_json("decider.json", ["选项A", "选项B", "选项C"])
        self.chits = load_json("chits.json", ["签1", "签2", "签3", "签4", "签5"])
        super().__init__(master, app, "随机决定器")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        # Tabs bar
        card = RoundedContainer(wrap, radius=14, padx=16, pady=16)
        card.pack(fill="both", expand=True)
        nb = tk.Frame(card.inner, bg=THEME["CARD"])
        nb.pack(fill="x")
        self.tab = tk.StringVar(value="自定义")
        self.btns = {}
        for t in ["自定义", "抽签", "抛硬币"]:
            b = tk.Label(nb, text=t, padx=16, pady=8, cursor="hand2",
                         font=("Microsoft YaHei", 10, "bold"))
            b.pack(side="left", padx=2)
            b.bind("<Button-1>", lambda e, tt=t: self._switch(tt))
            self.btns[t] = b
        self.body = tk.Frame(card.inner, bg=THEME["CARD"])
        self.body.pack(fill="both", expand=True, pady=10)
        self._switch("自定义")

    def _switch(self, name):
        self.tab.set(name)
        for t, b in self.btns.items():
            if t == name:
                b.configure(bg=THEME["PRIMARY"], fg="white")
            else:
                b.configure(bg=THEME["HOVER"], fg=THEME["TEXT"])
        for c in self.body.winfo_children():
            c.destroy()
        if name == "自定义":
            self._build_custom(self.body)
        elif name == "抽签":
            self._build_chits(self.body)
        else:
            self._build_coin(self.body)

    def _build_custom(self, parent):
        left = tk.Frame(parent, bg=THEME["CARD"])
        left.pack(side="left", fill="both", expand=True, padx=4)
        tk.Label(left, text="选项列表（每行一个）", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10, "bold"), anchor="w").pack(fill="x", pady=(0,4))
        rc = RoundedContainer(left, radius=10, padx=10, pady=8)
        rc.pack(fill="both", expand=True)
        self.txt_opt = tk.Text(rc.inner, bg=THEME["CARD"], fg=THEME["TEXT"],
                               insertbackground=THEME["TEXT"], bd=0,
                               font=("Microsoft YaHei", 11), height=12)
        self.txt_opt.pack(fill="both", expand=True)
        self.txt_opt.insert("1.0", "\n".join(self.options))
        # 右侧
        right = tk.Frame(parent, bg=THEME["CARD"])
        right.pack(side="left", fill="both", expand=True, padx=4)
        tk.Label(right, text="✨ 随机结果", bg=THEME["CARD"], fg=THEME["MUTED"],
                 font=("Microsoft YaHei", 10, "bold")).pack(pady=(0,8))
        self.res_custom = tk.Label(right, text="？", bg=THEME["CARD"], fg=THEME["PRIMARY"],
                                   font=("Microsoft YaHei", 28, "bold"), wraplength=320, justify="center")
        self.res_custom.pack(pady=16, fill="both", expand=True)
        btns = tk.Frame(right, bg=THEME["CARD"])
        btns.pack(fill="x", pady=8)
        RoundedButton(btns, "🎯 随机选择", command=self._do_custom,
                      width=140, height=40, radius=10).pack(side="left", padx=4)
        RoundedButton(btns, "保存选项", command=self._save_opts, bg=THEME["CARD"], fg=THEME["TEXT"],
                      width=100, height=40, radius=10).pack(side="left", padx=4)

    def _opts_list(self):
        return [x.strip() for x in self.txt_opt.get("1.0", "end").splitlines() if x.strip()]

    def _do_custom(self):
        opts = self._opts_list()
        if not opts:
            messagebox.showwarning("提示", "请输入选项")
            return
        def step(i=0):
            if i > 12:
                pick = random.choice(opts)
                self.res_custom.configure(text=pick)
                return
            self.res_custom.configure(text=random.choice(opts))
            self.after(40 + i*10, lambda: step(i+1))
        step()

    def _save_opts(self):
        self.options = self._opts_list()
        save_json("decider.json", self.options)
        messagebox.showinfo("保存", f"已保存 {len(self.options)} 个选项")

    def _build_chits(self, parent):
        left = tk.Frame(parent, bg=THEME["CARD"])
        left.pack(side="left", fill="both", expand=True, padx=4)
        tk.Label(left, text="签文列表（每行一个）", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10, "bold"), anchor="w").pack(fill="x", pady=(0,4))
        rc = RoundedContainer(left, radius=10, padx=10, pady=8)
        rc.pack(fill="both", expand=True)
        self.txt_chit = tk.Text(rc.inner, bg=THEME["CARD"], fg=THEME["TEXT"],
                                insertbackground=THEME["TEXT"], bd=0,
                                font=("Microsoft YaHei", 11), height=12)
        self.txt_chit.pack(fill="both", expand=True)
        self.txt_chit.insert("1.0", "\n".join(self.chits))
        right = tk.Frame(parent, bg=THEME["CARD"])
        right.pack(side="left", fill="both", expand=True, padx=4)
        tk.Label(right, text="🎋 抽签结果", bg=THEME["CARD"], fg=THEME["MUTED"],
                 font=("Microsoft YaHei", 10, "bold")).pack(pady=(0,8))
        self.res_chit = tk.Label(right, text="求一支签吧", bg=THEME["CARD"], fg=THEME["PRIMARY"],
                                 font=("Microsoft YaHei", 20, "bold"), wraplength=320, justify="center")
        self.res_chit.pack(pady=16, fill="both", expand=True)
        btns = tk.Frame(right, bg=THEME["CARD"])
        btns.pack(fill="x", pady=8)
        RoundedButton(btns, "🎋 抽签", command=self._do_chit, width=140, height=40, radius=10).pack(side="left", padx=4)
        RoundedButton(btns, "保存签文", command=self._save_chits, bg=THEME["CARD"], fg=THEME["TEXT"],
                      width=100, height=40, radius=10).pack(side="left", padx=4)

    def _chits_list(self):
        return [x.strip() for x in self.txt_chit.get("1.0", "end").splitlines() if x.strip()]

    def _do_chit(self):
        cs = self._chits_list()
        if not cs:
            messagebox.showwarning("提示", "请输入签文")
            return
        def step(i=0):
            if i > 14:
                self.res_chit.configure(text=random.choice(cs))
                return
            self.res_chit.configure(text=random.choice(cs))
            self.after(40 + i*8, lambda: step(i+1))
        step()

    def _save_chits(self):
        self.chits = self._chits_list()
        save_json("chits.json", self.chits)
        messagebox.showinfo("保存", f"已保存 {len(self.chits)} 个签文")

    def _build_coin(self, parent):
        tk.Label(parent, text="", bg=THEME["CARD"], height=2).pack()
        self.coin_canvas = tk.Canvas(parent, width=240, height=240, bg=THEME["CARD"], highlightthickness=0)
        self.coin_canvas.pack(pady=8)
        self.coin_canvas.bind("<Configure>", lambda e: self._draw_coin("?"))
        self.coin_res = tk.Label(parent, text="点击抛硬币", bg=THEME["CARD"], fg=THEME["TEXT"],
                                 font=("Microsoft YaHei", 14, "bold"))
        self.coin_res.pack(pady=8)
        RoundedButton(parent, "🪙 抛硬币", command=self._do_coin, width=160, height=42, radius=10).pack(pady=8)
        self.after(30, lambda: self._draw_coin("?"))

    def _draw_coin(self, side):
        c = self.coin_canvas
        c.delete("all")
        cx, cy = 120, 120
        cr = 100
        if side == "正":
            fill = "#FACC15"; text = "正"; tc = "#78350F"
        elif side == "反":
            fill = "#94A3B8"; text = "反"; tc = "#0F172A"
        else:
            fill = "#CBD5E1"; text = "?"; tc = "#334155"
        c.create_oval(cx-cr, cy-cr, cx+cr, cy+cr, fill=fill, outline="", width=0)
        c.create_oval(cx-cr+8, cy-cr+8, cx+cr-8, cy+cr-8, fill="", outline="#FFFFFF", width=2)
        c.create_text(cx, cy, text=text, fill=tc, font=("Microsoft YaHei", 64, "bold"))

    def _do_coin(self):
        sides = ["正", "反"]
        def step(i=0):
            if i > 10:
                s = random.choice(sides)
                self._draw_coin(s)
                self.coin_res.configure(text=f"结果: {s}面")
                return
            self._draw_coin(sides[i % 2])
            self.after(60 + i*10, lambda: step(i+1))
        step()

# =========================================================
#  7. 字数统计
# =========================================================
class WordCountPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app, "字数统计")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        # 输入
        rc = RoundedContainer(wrap, radius=14, padx=12, pady=12)
        rc.pack(fill="both", expand=True)
        self.txt = tk.Text(rc.inner, bg=THEME["CARD"], fg=THEME["TEXT"],
                           insertbackground=THEME["TEXT"], bd=0,
                           font=("Microsoft YaHei", 11), wrap="word", height=14)
        self.txt.pack(fill="both", expand=True)
        self.txt.bind("<KeyRelease>", lambda e: self._calc())
        # 统计
        card = RoundedContainer(wrap, radius=14, padx=16, pady=16)
        card.pack(fill="x", pady=(12,0))
        stats = tk.Frame(card.inner, bg=THEME["CARD"])
        stats.pack(fill="x")
        self.stats = {}
        keys = [("总字符", "chars"), ("中文字符", "cn"), ("英文单词", "words"), ("行数", "lines"),
                ("非空字符", "nospace"), ("数字", "nums")]
        for i, (name, key) in enumerate(keys):
            col, row = i % 3, i // 3
            cell = tk.Frame(stats, bg=THEME["BG"])
            cell.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            tk.Label(cell, text=name, fg=THEME["MUTED"], bg=THEME["BG"],
                     font=("Microsoft YaHei", 9)).pack(pady=(8,0))
            v = tk.Label(cell, text="0", fg=THEME["PRIMARY"], bg=THEME["BG"],
                         font=("Consolas", 18, "bold"))
            v.pack(pady=(0,8))
            self.stats[key] = v
            stats.grid_columnconfigure(col, weight=1)
        RoundedButton(card.inner, "立即统计", command=self._calc, width=120, height=34,
                      radius=8, bg=THEME["CARD"], fg=THEME["TEXT"]).pack(anchor="e", pady=(8,0))
        self._calc()

    def _calc(self):
        s = self.txt.get("1.0", "end").rstrip("\n")
        self.stats["chars"].configure(text=str(len(s)))
        cn = len(re.findall(r"[\u4e00-\u9fa5]", s))
        self.stats["cn"].configure(text=str(cn))
        words = len(re.findall(r"[A-Za-z_]+", s))
        self.stats["words"].configure(text=str(words))
        lines = len(s.splitlines()) if s else 0
        self.stats["lines"].configure(text=str(lines))
        nospace = len(re.sub(r"\s", "", s))
        self.stats["nospace"].configure(text=str(nospace))
        nums = len(re.findall(r"\d", s))
        self.stats["nums"].configure(text=str(nums))

# =========================================================
#  8. 文本对比
# =========================================================
class DiffPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app, "文本对比")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        cols = tk.Frame(wrap, bg=THEME["BG"])
        cols.pack(fill="both", expand=True)
        # 左
        lc = tk.Frame(cols, bg=THEME["BG"])
        lc.pack(side="left", fill="both", expand=True, padx=(0,6))
        tk.Label(lc, text="原文 A", anchor="w", fg=THEME["TEXT"], bg=THEME["BG"],
                 font=("Microsoft YaHei", 10, "bold")).pack(fill="x", pady=(0,4))
        r1 = RoundedContainer(lc, radius=12, padx=10, pady=10)
        r1.pack(fill="both", expand=True)
        self.t1 = tk.Text(r1.inner, bg=THEME["CARD"], fg=THEME["TEXT"],
                          insertbackground=THEME["TEXT"], bd=0, font=("Consolas", 11), wrap="word")
        self.t1.pack(fill="both", expand=True)
        # 右
        rc2 = tk.Frame(cols, bg=THEME["BG"])
        rc2.pack(side="left", fill="both", expand=True, padx=(6,0))
        tk.Label(rc2, text="原文 B", anchor="w", fg=THEME["TEXT"], bg=THEME["BG"],
                 font=("Microsoft YaHei", 10, "bold")).pack(fill="x", pady=(0,4))
        r2 = RoundedContainer(rc2, radius=12, padx=10, pady=10)
        r2.pack(fill="both", expand=True)
        self.t2 = tk.Text(r2.inner, bg=THEME["CARD"], fg=THEME["TEXT"],
                          insertbackground=THEME["TEXT"], bd=0, font=("Consolas", 11), wrap="word")
        self.t2.pack(fill="both", expand=True)
        # 按钮 + 结果
        bar = tk.Frame(wrap, bg=THEME["BG"])
        bar.pack(fill="x", pady=(10, 6))
        RoundedButton(bar, "🔍 对比文本", command=self._diff, width=140, height=36, radius=10).pack(side="left")
        self.ratio_label = tk.Label(bar, text="相似度: --", fg=THEME["MUTED"], bg=THEME["BG"],
                                    font=("Microsoft YaHei", 11, "bold"))
        self.ratio_label.pack(side="left", padx=20)
        out_rc = RoundedContainer(wrap, radius=12, padx=12, pady=12)
        out_rc.pack(fill="x")
        self.out = tk.Text(out_rc.inner, bg=THEME["CARD"], fg=THEME["TEXT"],
                           bd=0, font=("Consolas", 10), height=8, wrap="word")
        self.out.pack(fill="both")
        self.out.tag_configure("same", foreground=THEME["MUTED"])
        self.out.tag_configure("diff", foreground=THEME["ERROR"])
        self.out.tag_configure("add", foreground=THEME["SUCCESS"])
        self.out.configure(state="disabled")

    def _diff(self):
        a = self.t1.get("1.0", "end").splitlines()
        b = self.t2.get("1.0", "end").splitlines()
        sm = difflib.SequenceMatcher(None, a, b)
        ratio = sm.ratio() * 100
        self.ratio_label.configure(text=f"相似度: {ratio:.2f}%")
        self.out.configure(state="normal")
        self.out.delete("1.0", "end")
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for line in a[i1:i2]:
                    self.out.insert("end", f"  {line}\n", "same")
            elif tag == "replace":
                for line in a[i1:i2]:
                    self.out.insert("end", f"- {line}\n", "diff")
                for line in b[j1:j2]:
                    self.out.insert("end", f"+ {line}\n", "add")
            elif tag == "delete":
                for line in a[i1:i2]:
                    self.out.insert("end", f"- {line}\n", "diff")
            elif tag == "insert":
                for line in b[j1:j2]:
                    self.out.insert("end", f"+ {line}\n", "add")
        self.out.configure(state="disabled")

# =========================================================
#  9. Markdown 预览（简化版）
# =========================================================
class MarkdownPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app, "Markdown 预览")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        cols = tk.PanedWindow(wrap, orient="horizontal", bg=THEME["BG"],
                              sashwidth=4, sashrelief="flat", bd=0)
        cols.pack(fill="both", expand=True)
        # 左: 编辑器
        left = tk.Frame(cols, bg=THEME["BG"])
        cols.add(left, minsize=240)
        tk.Label(left, text="✏️  Markdown 编辑器", anchor="w", fg=THEME["TEXT"], bg=THEME["BG"],
                 font=("Microsoft YaHei", 10, "bold")).pack(fill="x", pady=(0,4))
        rc1 = RoundedContainer(left, radius=12, padx=10, pady=10)
        rc1.pack(fill="both", expand=True)
        self.txt = tk.Text(rc1.inner, bg=THEME["CARD"], fg=THEME["TEXT"],
                           insertbackground=THEME["TEXT"], bd=0,
                           font=("Consolas", 11), wrap="word")
        self.txt.pack(fill="both", expand=True)
        sample = """# 标题 H1
## 标题 H2
### 标题 H3
这是 **粗体** 与 *斜体* 文本。

`行内代码` 使用反引号。

    代码块第一行
    代码块第二行

- 列表项 A
- 列表项 B
- 列表项 C

> 引用块示例。
普通段落文字。
"""
        self.txt.insert("1.0", sample)
        self.txt.bind("<KeyRelease>", lambda e: self._render())
        # 右: 预览
        right = tk.Frame(cols, bg=THEME["BG"])
        cols.add(right, minsize=240)
        tk.Label(right, text="👁  预览", anchor="w", fg=THEME["TEXT"], bg=THEME["BG"],
                 font=("Microsoft YaHei", 10, "bold")).pack(fill="x", pady=(0,4))
        rc2 = RoundedContainer(right, radius=12, padx=12, pady=12)
        rc2.pack(fill="both", expand=True)
        self.out = tk.Text(rc2.inner, bg=THEME["CARD"], fg=THEME["TEXT"], bd=0,
                           font=("Microsoft YaHei", 11), wrap="word", spacing1=4)
        self.out.pack(fill="both", expand=True)
        self.out.configure(state="disabled")
        # 标签
        self.out.tag_configure("h1", font=("Microsoft YaHei", 20, "bold"),
                               foreground=THEME["PRIMARY"], spacing3=10)
        self.out.tag_configure("h2", font=("Microsoft YaHei", 18, "bold"),
                               foreground=THEME["PRIMARY"], spacing3=8)
        self.out.tag_configure("h3", font=("Microsoft YaHei", 14, "bold"),
                               foreground=THEME["TEXT"], spacing3=6)
        self.out.tag_configure("bold", font=("Microsoft YaHei", 11, "bold"))
        self.out.tag_configure("italic", font=("Microsoft YaHei", 11, "italic"))
        self.out.tag_configure("code", font=("Consolas", 11),
                               background=THEME["HOVER"], foreground=THEME["PRIMARY"])
        self.out.tag_configure("codeblock", font=("Consolas", 11),
                               background=THEME["BG"], foreground=THEME["SUCCESS"], lmargin1=14, lmargin2=14)
        self.out.tag_configure("quote", foreground=THEME["MUTED"],
                               lmargin1=12, lmargin2=12, font=("Microsoft YaHei", 11, "italic"))
        self.out.tag_configure("list", lmargin1=16, lmargin2=28)
        RoundedButton(wrap, "🔄 重新渲染", command=self._render, width=140, height=32,
                      radius=8, bg=THEME["CARD"], fg=THEME["TEXT"]).pack(anchor="e", pady=(8,0))
        self.after(60, self._render)

    def _inline(self, text, line_tags):
        # **粗体**
        def sub_bold(m):
            self.out.insert("end", m.group(1), line_tags + ["bold"])
            return ""
        # *斜体*
        def sub_ital(m):
            self.out.insert("end", m.group(1), line_tags + ["italic"])
            return ""
        # `code`
        def sub_code(m):
            self.out.insert("end", m.group(1), line_tags + ["code"])
            return ""
        # 处理顺序 code -> bold -> italic -> 剩余文字
        i = 0
        pattern = re.compile(r"`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*")
        while i < len(text):
            m = pattern.search(text, i)
            if not m:
                self.out.insert("end", text[i:], line_tags)
                break
            if m.start() > i:
                self.out.insert("end", text[i:m.start()], line_tags)
            if m.group(1):
                self.out.insert("end", m.group(1), line_tags + ["code"])
            elif m.group(2):
                self.out.insert("end", m.group(2), line_tags + ["bold"])
            elif m.group(3):
                self.out.insert("end", m.group(3), line_tags + ["italic"])
            i = m.end()

    def _render(self):
        self.out.configure(state="normal")
        self.out.delete("1.0", "end")
        lines = self.txt.get("1.0", "end").splitlines()
        in_codeblock = False
        for raw in lines:
            line = raw.rstrip()
            if line.startswith("    ") or line.startswith("\t"):
                # 代码块
                self.out.insert("end", (line if line.startswith("    ") else line[1:]) + "\n", ["codeblock"])
                in_codeblock = False
                continue
            if line.startswith("### "):
                self._inline(line[4:], ["h3"])
                self.out.insert("end", "\n")
            elif line.startswith("## "):
                self._inline(line[3:], ["h2"])
                self.out.insert("end", "\n")
            elif line.startswith("# "):
                self._inline(line[2:], ["h1"])
                self.out.insert("end", "\n")
            elif line.startswith("> "):
                self._inline(line[2:], ["quote"])
                self.out.insert("end", "\n")
            elif line.startswith("- ") or line.startswith("* "):
                self.out.insert("end", "• ", ["list"])
                self._inline(line[2:], ["list"])
                self.out.insert("end", "\n")
            elif re.match(r"\d+\. ", line):
                self._inline(line, ["list"])
                self.out.insert("end", "\n")
            elif not line:
                self.out.insert("end", "\n")
            else:
                self._inline(line, [])
                self.out.insert("end", "\n")
            in_codeblock = False
        self.out.configure(state="disabled")

# =========================================================
#  10. 正则测试
# =========================================================
class RegexPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app, "正则表达式测试")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        # 输入
        top = RoundedContainer(wrap, radius=14, padx=14, pady=12)
        top.pack(fill="x")
        tk.Label(top.inner, text="正则表达式 Pattern:", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10, "bold"), anchor="w").grid(row=0, column=0, sticky="w")
        pat_rc = RoundedContainer(top.inner, bg=THEME["BG"], radius=10, padx=10, pady=4)
        pat_rc.grid(row=0, column=1, sticky="we", padx=8, pady=4)
        self.pat = tk.Entry(pat_rc.inner, bg=THEME["BG"], fg=THEME["TEXT"],
                            insertbackground=THEME["TEXT"], bd=0, font=("Consolas", 12))
        self.pat.pack(fill="x")
        self.pat.insert(0, r"\d+")
        # Flags
        flag_row = tk.Frame(top.inner, bg=THEME["CARD"])
        flag_row.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6,0))
        self.flags = {}
        for name, val in [("忽略大小写 IGNORECASE", re.I), ("多行 MULTILINE", re.M),
                          ("点匹配所有 DOTALL", re.S), ("忽略空格 VERBOSE", re.X)]:
            v = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(flag_row, text=name, variable=v, bg=THEME["CARD"], fg=THEME["TEXT"],
                                selectcolor=THEME["CARD"], activebackground=THEME["CARD"],
                                activeforeground=THEME["TEXT"], font=("Microsoft YaHei", 9))
            cb.pack(side="left", padx=6)
            self.flags[name] = (v, val)
        top.inner.grid_columnconfigure(1, weight=1)
        # 文本区 + 结果
        mid = tk.Frame(wrap, bg=THEME["BG"])
        mid.pack(fill="both", expand=True, pady=(10,0))
        # 测试文本
        left = tk.Frame(mid, bg=THEME["BG"])
        left.pack(side="left", fill="both", expand=True, padx=(0,6))
        tk.Label(left, text="测试文本", anchor="w", fg=THEME["TEXT"], bg=THEME["BG"],
                 font=("Microsoft YaHei", 10, "bold")).pack(fill="x", pady=(0,4))
        r1 = RoundedContainer(left, radius=12, padx=10, pady=10)
        r1.pack(fill="both", expand=True)
        self.txt = tk.Text(r1.inner, bg=THEME["CARD"], fg=THEME["TEXT"],
                           insertbackground=THEME["TEXT"], bd=0,
                           font=("Consolas", 11), wrap="word")
        self.txt.pack(fill="both", expand=True)
        self.txt.insert("1.0", "订单号 A123 金额 456 元，电话 13812345678，日期 2026-08-19。")
        # 结果
        right = tk.Frame(mid, bg=THEME["BG"])
        right.pack(side="left", fill="both", expand=True, padx=(6,0))
        tk.Label(right, text="匹配结果", anchor="w", fg=THEME["TEXT"], bg=THEME["BG"],
                 font=("Microsoft YaHei", 10, "bold")).pack(fill="x", pady=(0,4))
        r2 = RoundedContainer(right, radius=12, padx=10, pady=10)
        r2.pack(fill="both", expand=True)
        self.out = tk.Text(r2.inner, bg=THEME["CARD"], fg=THEME["TEXT"],
                           bd=0, font=("Consolas", 11), wrap="word")
        self.out.pack(fill="both", expand=True)
        self.out.tag_configure("match", background=THEME["PRIMARY"], foreground="white")
        self.out.tag_configure("group", foreground=THEME["SUCCESS"])
        self.out.configure(state="disabled")
        # 按钮
        bar = tk.Frame(wrap, bg=THEME["BG"])
        bar.pack(fill="x", pady=8)
        RoundedButton(bar, "▶ 运行匹配", command=self._run, width=140, height=36, radius=10).pack(side="left", padx=4)
        self.count_lbl = tk.Label(bar, text="", bg=THEME["BG"], fg=THEME["MUTED"],
                                  font=("Microsoft YaHei", 10, "bold"))
        self.count_lbl.pack(side="left", padx=12)

    def _run(self):
        try:
            pat = self.pat.get()
            flag = 0
            for (v, val) in self.flags.values():
                if v.get():
                    flag |= val
            rx = re.compile(pat, flag)
            text = self.txt.get("1.0", "end")
            matches = list(rx.finditer(text))
            # 显示带高亮的文本
            self.out.configure(state="normal")
            self.out.delete("1.0", "end")
            last = 0
            for m in matches:
                self.out.insert("end", text[last:m.start()])
                self.out.insert("end", m.group(0), "match")
                last = m.end()
            self.out.insert("end", text[last:])
            # 详细
            if matches:
                self.out.insert("end", "\n\n--- 详情 ---\n", "group")
                for idx, m in enumerate(matches, 1):
                    self.out.insert("end", f"\n匹配 #{idx}: [{m.start()}:{m.end()}]\n", "group")
                    self.out.insert("end", f"  值: {m.group(0)!r}\n")
                    for gi, gv in enumerate(m.groups(), 1):
                        self.out.insert("end", f"  组 {gi}: {gv!r}\n")
            self.out.configure(state="disabled")
            self.count_lbl.configure(text=f"✅ 找到 {len(matches)} 个匹配")
        except re.error as e:
            messagebox.showerror("正则错误", str(e))
            self.count_lbl.configure(text="❌ 正则错误")
        except Exception as e:
            messagebox.showerror("错误", str(e))

# =========================================================
#  11. 番茄钟
# =========================================================
class PomodoroPage(BasePage):
    def __init__(self, master, app):
        self.total = 25 * 60
        self.remain = 25 * 60
        self.running = False
        self._job = None
        super().__init__(master, app, "番茄钟")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        card = RoundedContainer(wrap, radius=16, padx=24, pady=24)
        card.pack(fill="both", expand=True)
        # 模式选择
        modes = tk.Frame(card.inner, bg=THEME["CARD"])
        modes.pack(pady=(0, 16))
        self.mode_btns = {}
        for label, secs in [("🍅 专注 25 分", 25*60), ("☕ 短休息 5 分", 5*60), ("🌿 长休息 15 分", 15*60)]:
            b = RoundedButton(modes, label, command=lambda s=secs, l=label: self._set_mode(s, l),
                              width=150, height=36, radius=10, bg=THEME["BG"], fg=THEME["TEXT"])
            b.pack(side="left", padx=6)
            self.mode_btns[label] = b
        # 大圆倒计时
        self.canvas = tk.Canvas(card.inner, width=320, height=320, bg=THEME["CARD"], highlightthickness=0)
        self.canvas.pack(pady=8)
        self.canvas.bind("<Configure>", lambda e: self._draw())
        # 标签
        self.mode_label = tk.Label(card.inner, text="专注模式", bg=THEME["CARD"], fg=THEME["MUTED"],
                                   font=("Microsoft YaHei", 12, "bold"))
        self.mode_label.pack(pady=2)
        # 控制按钮
        ctrl = tk.Frame(card.inner, bg=THEME["CARD"])
        ctrl.pack(pady=16)
        self.btn_start = RoundedButton(ctrl, "▶ 开始", command=self._start, width=110, height=40, radius=10)
        self.btn_start.pack(side="left", padx=6)
        self.btn_pause = RoundedButton(ctrl, "⏸ 暂停", command=self._pause, width=110, height=40,
                                       radius=10, bg=THEME["WARNING"])
        self.btn_pause.pack(side="left", padx=6)
        RoundedButton(ctrl, "↺ 重置", command=self._reset, width=110, height=40, radius=10,
                      bg=THEME["CARD"], fg=THEME["TEXT"]).pack(side="left", padx=6)
        self._set_mode(25*60, "🍅 专注 25 分")
        self.after(30, self._draw)

    def _set_mode(self, secs, label):
        self.total = secs
        self.remain = secs
        self.running = False
        if self._job:
            self.after_cancel(self._job); self._job = None
        nice = label.replace("🍅 ", "").replace("☕ ", "").replace("🌿 ", "")
        self.mode_label.configure(text=nice)
        for k, b in self.mode_btns.items():
            if k == label:
                b.set_bg(THEME["PRIMARY"]); b._fg = "white"; b._draw()
            else:
                b.set_bg(THEME["BG"]); b._fg = THEME["TEXT"]; b._draw()
        self.btn_start.set_text("▶ 开始")
        self._draw()

    def _draw(self):
        c = self.canvas
        c.delete("all")
        cx, cy = 160, 160
        r = 130
        # 背景圆
        c.create_oval(cx-r, cy-r, cx+r, cy+r, fill=THEME["BG"], outline="")
        # 进度
        if self.total > 0:
            prog = 1 - self.remain / self.total
        else:
            prog = 0
        if prog > 0:
            # 画圆弧 (从 -90° 开始)
            extent = int(360 * prog)
            # 用多条线近似 arc
            import math
            points = []
            steps = 180
            for i in range(steps + 1):
                ang = math.radians(-90 + (extent * i / steps))
                points.append(cx + r * math.cos(ang))
                points.append(cy + r * math.sin(ang))
            if len(points) >= 4:
                for i in range(0, len(points)-2, 2):
                    c.create_line(points[i], points[i+1], points[i+2], points[i+3],
                                  fill=THEME["PRIMARY"], width=14, capstyle="round")
        # 内圈
        r2 = r - 24
        c.create_oval(cx-r2, cy-r2, cx+r2, cy+r2, fill=THEME["CARD"], outline="")
        # 时间文本
        m, s = divmod(max(0, self.remain), 60)
        c.create_text(cx, cy, text=f"{m:02d}:{s:02d}", fill=THEME["TEXT"],
                      font=("Consolas", 52, "bold"))

    def _start(self):
        if self.remain <= 0:
            return
        self.running = True
        self.btn_start.set_text("⏵ 运行中")
        self._tick()

    def _pause(self):
        self.running = False
        if self._job:
            self.after_cancel(self._job); self._job = None
        self.btn_start.set_text("▶ 继续")

    def _reset(self):
        self.running = False
        if self._job:
            self.after_cancel(self._job); self._job = None
        self.remain = self.total
        self.btn_start.set_text("▶ 开始")
        self._draw()

    def _tick(self):
        if not self.running:
            return
        self._draw()
        if self.remain <= 0:
            self.running = False
            self.btn_start.set_text("▶ 开始")
            try:
                messagebox.showinfo("番茄钟", "⏰ 时间到！")
                self.bell()
            except Exception:
                pass
            return
        self.remain -= 1
        self._job = self.after(1000, self._tick)

# =========================================================
#  12. 倒计时
# =========================================================
class CountdownPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app, "倒计时")
        self.total = 0
        self.remain = 0
        self.running = False
        self._job = None
        self._end_ts = None

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        card = RoundedContainer(wrap, radius=16, padx=24, pady=24)
        card.pack(fill="both", expand=True)
        # 输入 H M S
        inp = tk.Frame(card.inner, bg=THEME["CARD"])
        inp.pack(pady=(0, 16))
        self.h_var = tk.StringVar(value="0")
        self.m_var = tk.StringVar(value="5")
        self.s_var = tk.StringVar(value="0")
        for title, var in [("时", self.h_var), ("分", self.m_var), ("秒", self.s_var)]:
            cell = tk.Frame(inp, bg=THEME["CARD"])
            cell.pack(side="left", padx=8)
            tk.Label(cell, text=title, fg=THEME["MUTED"], bg=THEME["CARD"],
                     font=("Microsoft YaHei", 10)).pack()
            rc = RoundedContainer(cell, bg=THEME["BG"], radius=10, padx=8, pady=2)
            rc.pack(pady=4)
            sp = tk.Spinbox(rc.inner, from_=0, to=99, textvariable=var, width=5,
                            bg=THEME["BG"], fg=THEME["TEXT"], bd=0,
                            font=("Consolas", 18, "bold"), justify="center",
                            buttonbackground=THEME["HOVER"])
            sp.pack()
        # 显示
        self.canvas = tk.Canvas(card.inner, width=340, height=200, bg=THEME["CARD"], highlightthickness=0)
        self.canvas.pack(pady=4)
        self.canvas.bind("<Configure>", lambda e: self._draw())
        # 状态
        self.status = tk.Label(card.inner, text="⏱ 未开始", bg=THEME["CARD"], fg=THEME["MUTED"],
                               font=("Microsoft YaHei", 11, "bold"))
        self.status.pack(pady=4)
        # 按钮
        ctrl = tk.Frame(card.inner, bg=THEME["CARD"])
        ctrl.pack(pady=14)
        self.btn_start = RoundedButton(ctrl, "▶ 开始", command=self._start, width=110, height=40, radius=10)
        self.btn_start.pack(side="left", padx=6)
        RoundedButton(ctrl, "⏸ 暂停", command=self._pause, width=110, height=40, radius=10,
                      bg=THEME["WARNING"]).pack(side="left", padx=6)
        RoundedButton(ctrl, "↺ 重置", command=self._reset, width=110, height=40, radius=10,
                      bg=THEME["CARD"], fg=THEME["TEXT"]).pack(side="left", padx=6)
        self.after(30, self._draw)

    def _parse(self):
        try:
            h = int(float(self.h_var.get() or 0))
            m = int(float(self.m_var.get() or 0))
            s = int(float(self.s_var.get() or 0))
            return max(0, h*3600 + m*60 + s)
        except Exception:
            return 0

    def _draw(self):
        c = self.canvas
        c.delete("all")
        cw = c.winfo_width() or 340
        ch = c.winfo_height() or 200
        cx, cy = cw//2, ch//2
        h, rem = divmod(max(0, self.remain), 3600)
        m, s = divmod(rem, 60)
        txt = f"{h:02d}:{m:02d}:{s:02d}"
        # 画背景圆角
        c.create_rectangle(0, 0, cw, ch, fill=THEME["BG"], outline="")
        c.create_text(cx, cy, text=txt, fill=THEME["PRIMARY"],
                      font=("Consolas", 54, "bold"))

    def _start(self):
        if self.remain <= 0:
            self.remain = self._parse()
            self.total = self.remain
        if self.remain <= 0:
            messagebox.showwarning("提示", "请先设置时间")
            return
        self.running = True
        self._end_ts = time.time() + self.remain
        self.status.configure(text="⏳ 倒计时中...")
        self.btn_start.set_text("⏵ 运行中")
        self._tick()

    def _pause(self):
        self.running = False
        if self._job:
            self.after_cancel(self._job); self._job = None
        self.status.configure(text="⏸ 已暂停")
        self.btn_start.set_text("▶ 继续")

    def _reset(self):
        self.running = False
        if self._job:
            self.after_cancel(self._job); self._job = None
        self.remain = 0
        self._end_ts = None
        self.status.configure(text="⏱ 未开始")
        self.btn_start.set_text("▶ 开始")
        self._draw()

    def _tick(self):
        if not self.running:
            return
        if self._end_ts:
            self.remain = max(0, int(self._end_ts - time.time()))
        self._draw()
        if self.remain <= 0:
            self.running = False
            self.status.configure(text="⏰ 时间到！")
            self.btn_start.set_text("▶ 开始")
            try:
                messagebox.showinfo("倒计时", "⏰ 倒计时结束！")
                for _ in range(3): self.bell()
            except Exception:
                pass
            return
        self._job = self.after(1000, self._tick)

# =========================================================
#  13. 纪念日管理
# =========================================================
class AnniversaryPage(BasePage):
    def __init__(self, master, app):
        self.items = load_json("anniversaries.json", [])
        super().__init__(master, app, "纪念日管理")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        # 添加表单
        add_card = RoundedContainer(wrap, radius=14, padx=16, pady=14)
        add_card.pack(fill="x", pady=(0, 10))
        form = tk.Frame(add_card.inner, bg=THEME["CARD"])
        form.pack(fill="x")
        tk.Label(form, text="名称:", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.name_v = tk.StringVar()
        rc1 = RoundedContainer(form, bg=THEME["BG"], radius=8, padx=8, pady=2)
        rc1.grid(row=0, column=1, sticky="we", padx=6, pady=4)
        tk.Entry(rc1.inner, textvariable=self.name_v, bg=THEME["BG"], fg=THEME["TEXT"],
                 bd=0, font=("Microsoft YaHei", 10), insertbackground=THEME["TEXT"]).pack(fill="x")
        tk.Label(form, text="日期:", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10, "bold")).grid(row=0, column=2, sticky="w", padx=(8,0))
        today = datetime.date.today()
        self.date_v = tk.StringVar(value=today.strftime("%Y-%m-%d"))
        rc2 = RoundedContainer(form, bg=THEME["BG"], radius=8, padx=8, pady=2)
        rc2.grid(row=0, column=3, sticky="we", padx=6, pady=4)
        tk.Entry(rc2.inner, textvariable=self.date_v, bg=THEME["BG"], fg=THEME["TEXT"],
                 bd=0, font=("Consolas", 10), insertbackground=THEME["TEXT"]).pack(fill="x")
        RoundedButton(form, "➕ 添加", command=self._add, width=90, height=32,
                      radius=8).grid(row=0, column=4, padx=6)
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=1)
        # 列表
        list_card = RoundedContainer(wrap, radius=14, padx=6, pady=6)
        list_card.pack(fill="both", expand=True)
        # 表头
        head = tk.Frame(list_card.inner, bg=THEME["CARD"])
        head.pack(fill="x", padx=8, pady=(6,2))
        for t, w in [("名称", 20), ("日期", 12), ("天数", 8), ("说明", 22), ("操作", 10)]:
            tk.Label(head, text=t, fg=THEME["MUTED"], bg=THEME["CARD"],
                     font=("Microsoft YaHei", 9, "bold"), anchor="w",
                     width=w).pack(side="left", padx=4)
        # 可滚动列表
        scroll = tk.Frame(list_card.inner, bg=THEME["CARD"])
        scroll.pack(fill="both", expand=True, padx=8, pady=4)
        self.canvas_list = tk.Canvas(scroll, bg=THEME["CARD"], highlightthickness=0)
        self.canvas_list.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(scroll, orient="vertical", command=self.canvas_list.yview,
                          bg=THEME["CARD"], troughcolor=THEME["HOVER"],
                          activebackground=THEME["PRIMARY"])
        sb.pack(side="right", fill="y")
        self.canvas_list.configure(yscrollcommand=sb.set)
        self.list_frame = tk.Frame(self.canvas_list, bg=THEME["CARD"])
        self.canvas_list.create_window((0,0), window=self.list_frame, anchor="nw")
        self.list_frame.bind("<Configure>",
            lambda e: self.canvas_list.configure(scrollregion=self.canvas_list.bbox("all")))
        self._render_list()

    def _render_list(self):
        for c in self.list_frame.winfo_children():
            c.destroy()
        today = datetime.date.today()
        if not self.items:
            tk.Label(self.list_frame, text="暂无纪念日，快去添加一个吧~",
                     fg=THEME["MUTED"], bg=THEME["CARD"],
                     font=("Microsoft YaHei", 11), pady=30).pack()
        for idx, item in enumerate(self.items):
            try:
                d = datetime.datetime.strptime(item["date"], "%Y-%m-%d").date()
            except Exception:
                continue
            delta = (d - today).days
            if delta > 0:
                info = f"还有 {delta} 天"; tone = THEME["PRIMARY"]
            elif delta == 0:
                info = "就是今天！"; tone = THEME["SUCCESS"]
            else:
                info = f"已过去 {-delta} 天"; tone = THEME["WARNING"]
            bg = THEME["BG"] if idx % 2 == 0 else THEME["CARD"]
            row = tk.Frame(self.list_frame, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=item["name"], fg=THEME["TEXT"], bg=bg,
                     font=("Microsoft YaHei", 10), anchor="w", width=22).pack(side="left", padx=4, ipady=6)
            tk.Label(row, text=item["date"], fg=THEME["MUTED"], bg=bg,
                     font=("Consolas", 10), anchor="w", width=14).pack(side="left", padx=4)
            tk.Label(row, text=str(abs(delta)), fg=tone, bg=bg,
                     font=("Consolas", 12, "bold"), anchor="w", width=8).pack(side="left", padx=4)
            tk.Label(row, text=info, fg=tone, bg=bg,
                     font=("Microsoft YaHei", 10), anchor="w", width=24).pack(side="left", padx=4)
            del_btn = RoundedButton(row, "删除", command=lambda i=idx: self._delete(i),
                                    width=66, height=26, radius=6, bg=THEME["ERROR"])
            del_btn.pack(side="left", padx=4)

    def _add(self):
        name = self.name_v.get().strip()
        ds = self.date_v.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入名称"); return
        try:
            datetime.datetime.strptime(ds, "%Y-%m-%d")
        except Exception:
            messagebox.showwarning("提示", "日期格式应为 YYYY-MM-DD"); return
        self.items.append({"name": name, "date": ds})
        self.items.sort(key=lambda x: x["date"])
        save_json("anniversaries.json", self.items)
        self.name_v.set("")
        self._render_list()

    def _delete(self, idx):
        if not messagebox.askyesno("确认", "确定删除该纪念日？"):
            return
        del self.items[idx]
        save_json("anniversaries.json", self.items)
        self._render_list()

# =========================================================
#  14. 桌面便签
# =========================================================
class StickyNotePage(BasePage):
    def __init__(self, master, app):
        self.notes = load_json("notes.json", [])
        self.windows = {}
        super().__init__(master, app, "桌面便签")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        bar = tk.Frame(wrap, bg=THEME["BG"])
        bar.pack(fill="x", pady=(0, 10))
        RoundedButton(bar, "📝 新建便签", command=self._new, width=150, height=38, radius=10).pack(side="left")
        tk.Label(bar, text=f"共 {len(self.notes)} 个便签", fg=THEME["MUTED"], bg=THEME["BG"],
                 font=("Microsoft YaHei", 10)).pack(side="left", padx=16)
        RoundedButton(bar, "🗑 清空所有", command=self._clear_all, bg=THEME["ERROR"],
                      width=120, height=38, radius=10).pack(side="right")
        # 列表
        card = RoundedContainer(wrap, radius=14, padx=10, pady=10)
        card.pack(fill="both", expand=True)
        self.list_fr = tk.Frame(card.inner, bg=THEME["CARD"])
        self.list_fr.pack(fill="both", expand=True)
        self._render_list()

    def _render_list(self):
        for c in self.list_fr.winfo_children():
            c.destroy()
        if not self.notes:
            tk.Label(self.list_fr, text="还没有便签。点击上方「新建便签」开始记录吧！",
                     fg=THEME["MUTED"], bg=THEME["CARD"], font=("Microsoft YaHei", 11), pady=40).pack()
            return
        for i in range(0, len(self.notes), 3):
            row = tk.Frame(self.list_fr, bg=THEME["CARD"])
            row.pack(fill="x", pady=4)
            for j in range(3):
                if i + j >= len(self.notes):
                    break
                idx = i + j
                n = self.notes[idx]
                color = n.get("color", "#FEF3C7")
                preview = (n.get("content", "") or "(空便签)")[:40]
                cell = RoundedContainer(row, bg=color, radius=12, padx=12, pady=12)
                cell.pack(side="left", fill="both", expand=True, padx=6)
                cell.inner.configure(bg=color)
                tk.Label(cell.inner, text=preview, bg=color, fg="#1F2937",
                         font=("Microsoft YaHei", 10), wraplength=200,
                         anchor="nw", justify="left", height=4).pack(fill="x")
                btns = tk.Frame(cell.inner, bg=color)
                btns.pack(fill="x", pady=(6,0))
                tk.Button(btns, text="打开", relief="flat", bg="#F59E0B", fg="white",
                          cursor="hand2", font=("Microsoft YaHei", 9, "bold"),
                          command=lambda ii=idx: self._open(ii)).pack(side="left", padx=2)
                tk.Button(btns, text="删除", relief="flat", bg="#EF4444", fg="white",
                          cursor="hand2", font=("Microsoft YaHei", 9, "bold"),
                          command=lambda ii=idx: self._delete(ii)).pack(side="right", padx=2)

    def _save(self):
        save_json("notes.json", self.notes)

    def _new(self):
        colors = ["#FEF3C7", "#DBEAFE", "#FCE7F3", "#D1FAE5", "#E0E7FF", "#FED7AA"]
        color = random.choice(colors)
        note = {"id": str(uuid.uuid4()), "content": "", "color": color,
                "x": 300 + random.randint(-60, 60), "y": 200 + random.randint(-40, 40)}
        self.notes.append(note)
        self._save()
        self._open(len(self.notes) - 1)
        self._render_list()

    def _open(self, idx):
        if idx < 0 or idx >= len(self.notes):
            return
        note = self.notes[idx]
        nid = note["id"]
        if nid in self.windows and self.windows[nid].winfo_exists():
            self.windows[nid].lift(); return
        self.windows[nid] = self._make_window(idx, note)

    def _make_window(self, idx, note):
        win = tk.Toplevel(self)
        win.title("便签")
        win.geometry(f"280x300+{note.get('x',300)}+{note.get('y',200)}")
        win.configure(bg=note["color"])
        win.attributes("-topmost", True)
        # 标题条
        bar = tk.Frame(win, bg=note["color"], cursor="fleur")
        bar.pack(fill="x")
        tk.Label(bar, text="📝 便签", bg=note["color"], fg="#1F2937",
                 font=("Microsoft YaHei", 10, "bold")).pack(side="left", padx=8, pady=4)
        tk.Button(bar, text="×", relief="flat", bg=note["color"], fg="#1F2937",
                  cursor="hand2", bd=0, font=("Arial", 14, "bold"),
                  command=win.destroy).pack(side="right", padx=6)
        # 文本
        txt = tk.Text(win, bg=note["color"], fg="#1F2937", bd=0, relief="flat",
                      font=("Microsoft YaHei", 11), insertbackground="#1F2937")
        txt.pack(fill="both", expand=True, padx=8, pady=4)
        txt.insert("1.0", note.get("content", ""))
        # 保存
        def on_save(*a):
            try:
                self.notes[idx]["content"] = txt.get("1.0", "end").rstrip("\n")
                self._save()
            except Exception:
                pass
        txt.bind("<KeyRelease>", on_save)
        # 拖动
        data = {"x": 0, "y": 0}
        def on_press(e):
            data["x"] = e.x; data["y"] = e.y
        def on_drag(e):
            x = win.winfo_x() + (e.x - data["x"])
            y = win.winfo_y() + (e.y - data["y"])
            win.geometry(f"+{x}+{y}")
            try:
                self.notes[idx]["x"] = x
                self.notes[idx]["y"] = y
            except Exception:
                pass
        bar.bind("<Button-1>", on_press)
        bar.bind("<B1-Motion>", on_drag)
        win.protocol("WM_DELETE_WINDOW", lambda: (on_save(), self._render_list(), win.destroy()))
        return win

    def _delete(self, idx):
        if not messagebox.askyesno("确认", "删除这个便签？"): return
        nid = self.notes[idx].get("id")
        if nid and nid in self.windows:
            try: self.windows[nid].destroy()
            except Exception: pass
            del self.windows[nid]
        del self.notes[idx]
        self._save()
        self._render_list()

    def _clear_all(self):
        if not messagebox.askyesno("确认", "清空所有便签？此操作不可恢复！"): return
        for w in list(self.windows.values()):
            try: w.destroy()
            except Exception: pass
        self.windows.clear()
        self.notes.clear()
        self._save()
        self._render_list()

# =========================================================
#  15. 简易记账
# =========================================================
class LedgerPage(BasePage):
    def __init__(self, master, app):
        self.records = load_json("ledger.json", [])
        super().__init__(master, app, "简易记账")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        # 顶部统计
        top = tk.Frame(wrap, bg=THEME["BG"])
        top.pack(fill="x", pady=(0, 10))
        for title, key, color in [("总支出", "out", THEME["ERROR"]),
                                   ("总收入", "in", THEME["SUCCESS"]),
                                   ("结余", "net", THEME["PRIMARY"])]:
            c = RoundedContainer(top, radius=12, padx=14, pady=12)
            c.pack(side="left", fill="x", expand=True, padx=4)
            tk.Label(c.inner, text=title, bg=THEME["CARD"], fg=THEME["MUTED"],
                     font=("Microsoft YaHei", 9)).pack(anchor="w")
            self.stats_lbl = getattr(self, f"lbl_{key}", None)
            lbl = tk.Label(c.inner, text="¥0.00", bg=THEME["CARD"], fg=color,
                           font=("Consolas", 20, "bold"))
            lbl.pack(anchor="w", pady=(2,0))
            setattr(self, f"lbl_{key}", lbl)
        # 添加表单
        form_card = RoundedContainer(wrap, radius=12, padx=14, pady=12)
        form_card.pack(fill="x", pady=(0, 10))
        f = tk.Frame(form_card.inner, bg=THEME["CARD"])
        f.pack(fill="x")
        self.typ = tk.StringVar(value="支出")
        for t in ["支出", "收入"]:
            rb = tk.Radiobutton(f, text=t, value=t, variable=self.typ, bg=THEME["CARD"],
                                fg=THEME["TEXT"], selectcolor=THEME["CARD"],
                                activebackground=THEME["CARD"], font=("Microsoft YaHei", 10))
            rb.pack(side="left", padx=4)
        # 金额
        tk.Label(f, text="金额:", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10)).pack(side="left", padx=(12,2))
        rc1 = RoundedContainer(f, bg=THEME["BG"], radius=8, padx=8, pady=2)
        rc1.pack(side="left")
        self.amt = tk.StringVar()
        tk.Entry(rc1.inner, textvariable=self.amt, bg=THEME["BG"], fg=THEME["TEXT"],
                 bd=0, width=10, font=("Consolas", 11),
                 insertbackground=THEME["TEXT"]).pack()
        # 分类
        tk.Label(f, text="分类:", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10)).pack(side="left", padx=(12,2))
        self.cat_v = tk.StringVar(value="餐饮")
        self.cb = ttk.Combobox(f, textvariable=self.cat_v,
                               values=["餐饮", "交通", "购物", "娱乐", "住房", "医疗", "教育",
                                       "工资", "奖金", "红包", "其他"],
                               width=8, state="normal")
        self.cb.pack(side="left")
        # 日期
        tk.Label(f, text="日期:", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10)).pack(side="left", padx=(12,2))
        self.date_v = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        rc2 = RoundedContainer(f, bg=THEME["BG"], radius=8, padx=8, pady=2)
        rc2.pack(side="left")
        tk.Entry(rc2.inner, textvariable=self.date_v, bg=THEME["BG"], fg=THEME["TEXT"],
                 bd=0, width=12, font=("Consolas", 10),
                 insertbackground=THEME["TEXT"]).pack()
        # 备注
        tk.Label(f, text="备注:", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10)).pack(side="left", padx=(12,2))
        self.note_v = tk.StringVar()
        rc3 = RoundedContainer(f, bg=THEME["BG"], radius=8, padx=8, pady=2)
        rc3.pack(side="left", fill="x", expand=True)
        tk.Entry(rc3.inner, textvariable=self.note_v, bg=THEME["BG"], fg=THEME["TEXT"],
                 bd=0, font=("Microsoft YaHei", 10),
                 insertbackground=THEME["TEXT"]).pack(fill="x")
        RoundedButton(f, "➕ 记一笔", command=self._add, width=100, height=32,
                      radius=8).pack(side="left", padx=8)
        # 列表
        list_card = RoundedContainer(wrap, radius=12, padx=8, pady=8)
        list_card.pack(fill="both", expand=True)
        head = tk.Frame(list_card.inner, bg=THEME["CARD"])
        head.pack(fill="x", padx=6, pady=(2,4))
        for t, w in [("日期", 12), ("类型", 6), ("分类", 8), ("备注", 26), ("金额", 12), ("操作", 6)]:
            tk.Label(head, text=t, fg=THEME["MUTED"], bg=THEME["CARD"],
                     font=("Microsoft YaHei", 9, "bold"), anchor="w", width=w).pack(side="left", padx=2)
        scroll_fr = tk.Frame(list_card.inner, bg=THEME["CARD"])
        scroll_fr.pack(fill="both", expand=True, padx=6)
        self.cv = tk.Canvas(scroll_fr, bg=THEME["CARD"], highlightthickness=0)
        self.cv.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(scroll_fr, orient="vertical", command=self.cv.yview,
                          bg=THEME["CARD"], troughcolor=THEME["HOVER"],
                          activebackground=THEME["PRIMARY"])
        sb.pack(side="right", fill="y")
        self.cv.configure(yscrollcommand=sb.set)
        self.lf = tk.Frame(self.cv, bg=THEME["CARD"])
        self.cv.create_window((0,0), window=self.lf, anchor="nw")
        self.lf.bind("<Configure>", lambda e: self.cv.configure(scrollregion=self.cv.bbox("all")))
        self._recalc()
        self._render()

    def _recalc(self):
        total_in = sum(r["amount"] for r in self.records if r.get("type") == "收入")
        total_out = sum(r["amount"] for r in self.records if r.get("type") != "收入")
        self.lbl_in.configure(text=f"¥{total_in:.2f}")
        self.lbl_out.configure(text=f"¥{total_out:.2f}")
        self.lbl_net.configure(text=f"¥{total_in - total_out:.2f}")

    def _render(self):
        for c in self.lf.winfo_children():
            c.destroy()
        sorted_r = sorted(self.records, key=lambda r: r.get("date", ""), reverse=True)
        if not sorted_r:
            tk.Label(self.lf, text="暂无记录，快记一笔吧！",
                     fg=THEME["MUTED"], bg=THEME["CARD"], font=("Microsoft YaHei", 11), pady=30).pack()
        for idx, r in enumerate(sorted_r):
            bg = THEME["BG"] if idx % 2 == 0 else THEME["CARD"]
            row = tk.Frame(self.lf, bg=bg)
            row.pack(fill="x", pady=1)
            is_in = r.get("type") == "收入"
            amt_color = THEME["SUCCESS"] if is_in else THEME["ERROR"]
            sign = "+" if is_in else "-"
            tk.Label(row, text=r.get("date",""), width=12, anchor="w",
                     fg=THEME["TEXT"], bg=bg, font=("Consolas", 10)).pack(side="left", padx=2, ipady=6)
            tk.Label(row, text=r.get("type",""), width=6, anchor="w",
                     fg=THEME["TEXT"], bg=bg, font=("Microsoft YaHei", 10)).pack(side="left", padx=2)
            tk.Label(row, text=r.get("category",""), width=8, anchor="w",
                     fg=THEME["TEXT"], bg=bg, font=("Microsoft YaHei", 10)).pack(side="left", padx=2)
            tk.Label(row, text=r.get("note",""), width=26, anchor="w",
                     fg=THEME["MUTED"], bg=bg, font=("Microsoft YaHei", 10)).pack(side="left", padx=2)
            tk.Label(row, text=f"{sign}¥{r['amount']:.2f}", width=12, anchor="e",
                     fg=amt_color, bg=bg, font=("Consolas", 11, "bold")).pack(side="left", padx=2)
            # 原始 index
            orig_idx = self.records.index(r)
            del_btn = RoundedButton(row, "删", command=lambda i=orig_idx: self._del(i),
                                    width=44, height=24, radius=6, bg=THEME["ERROR"])
            del_btn.pack(side="left", padx=4)

    def _add(self):
        try:
            amt = float(self.amt.get())
        except Exception:
            messagebox.showwarning("提示", "请输入有效金额"); return
        try:
            datetime.datetime.strptime(self.date_v.get(), "%Y-%m-%d")
        except Exception:
            messagebox.showwarning("提示", "日期格式应为 YYYY-MM-DD"); return
        if amt <= 0:
            messagebox.showwarning("提示", "金额需大于 0"); return
        self.records.append({
            "type": self.typ.get(),
            "amount": amt,
            "category": self.cat_v.get(),
            "date": self.date_v.get(),
            "note": self.note_v.get().strip(),
        })
        save_json("ledger.json", self.records)
        self.amt.set("")
        self.note_v.set("")
        self._recalc()
        self._render()

    def _del(self, idx):
        if not messagebox.askyesno("确认", "删除这条记录？"): return
        del self.records[idx]
        save_json("ledger.json", self.records)
        self._recalc()
        self._render()

# =========================================================
#  16. 时光胶囊
# =========================================================
class CapsulePage(BasePage):
    def __init__(self, master, app):
        self.capsules = load_json("capsules.json", [])
        super().__init__(master, app, "时光胶囊")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        # 新建
        add_card = RoundedContainer(wrap, radius=14, padx=14, pady=12)
        add_card.pack(fill="x", pady=(0, 10))
        a = tk.Frame(add_card.inner, bg=THEME["CARD"])
        a.pack(fill="x")
        tk.Label(a, text="标题:", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.t_v = tk.StringVar()
        rc1 = RoundedContainer(a, bg=THEME["BG"], radius=8, padx=8, pady=2)
        rc1.grid(row=0, column=1, sticky="we", padx=6, pady=3)
        tk.Entry(rc1.inner, textvariable=self.t_v, bg=THEME["BG"], fg=THEME["TEXT"],
                 bd=0, font=("Microsoft YaHei", 10), insertbackground=THEME["TEXT"]).pack(fill="x")
        tk.Label(a, text="解锁日期:", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10, "bold")).grid(row=0, column=2, sticky="w", padx=(8,0))
        future = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        self.d_v = tk.StringVar(value=future)
        rc2 = RoundedContainer(a, bg=THEME["BG"], radius=8, padx=8, pady=2)
        rc2.grid(row=0, column=3, sticky="we", padx=6, pady=3)
        tk.Entry(rc2.inner, textvariable=self.d_v, bg=THEME["BG"], fg=THEME["TEXT"],
                 bd=0, font=("Consolas", 10), insertbackground=THEME["TEXT"]).pack(fill="x")
        RoundedButton(a, "🔒 封存胶囊", command=self._add, width=120, height=32,
                      radius=8).grid(row=0, column=4, padx=6)
        a.grid_columnconfigure(1, weight=1)
        a.grid_columnconfigure(3, weight=1)
        tk.Label(add_card.inner, text="内容:", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10, "bold"), anchor="w").pack(fill="x", pady=(6,2))
        rc3 = RoundedContainer(add_card.inner, bg=THEME["BG"], radius=10, padx=10, pady=8)
        rc3.pack(fill="x")
        self.txt = tk.Text(rc3.inner, bg=THEME["BG"], fg=THEME["TEXT"], bd=0,
                           height=4, font=("Microsoft YaHei", 11),
                           insertbackground=THEME["TEXT"], wrap="word")
        self.txt.pack(fill="x")
        # 列表
        self.list_wrap = tk.Frame(wrap, bg=THEME["BG"])
        self.list_wrap.pack(fill="both", expand=True)
        self._render_list()

    def _render_list(self):
        for c in self.list_wrap.winfo_children():
            c.destroy()
        card = RoundedContainer(self.list_wrap, radius=14, padx=12, pady=12)
        card.pack(fill="both", expand=True)
        if not self.capsules:
            tk.Label(card.inner, text="还没有胶囊，给未来的自己写一封信吧 💌",
                     fg=THEME["MUTED"], bg=THEME["CARD"], font=("Microsoft YaHei", 11), pady=30).pack()
            return
        sorted_c = sorted(self.capsules, key=lambda x: x.get("unlock_date", ""))
        today = datetime.date.today()
        for i, cap in enumerate(sorted_c):
            try:
                ud = datetime.datetime.strptime(cap["unlock_date"], "%Y-%m-%d").date()
            except Exception:
                continue
            unlocked = today >= ud
            tone = THEME["SUCCESS"] if unlocked else THEME["WARNING"]
            title_bg = THEME["BG"] if i % 2 == 0 else THEME["CARD"]
            row = tk.Frame(card.inner, bg=title_bg)
            row.pack(fill="x", pady=3)
            header = tk.Frame(row, bg=title_bg)
            header.pack(fill="x", padx=4, pady=4)
            icon = "🔓" if unlocked else "🔒"
            tk.Label(header, text=f"{icon} {cap.get('title','未命名')}", bg=title_bg,
                     fg=THEME["TEXT"], font=("Microsoft YaHei", 11, "bold"), anchor="w").pack(side="left")
            left = (ud - today).days
            status = "已解锁" if unlocked else f"还有 {left} 天解锁"
            tk.Label(header, text=status, bg=title_bg, fg=tone,
                     font=("Microsoft YaHei", 10, "bold")).pack(side="left", padx=12)
            tk.Label(header, text=f"解锁日: {cap['unlock_date']}", bg=title_bg, fg=THEME["MUTED"],
                     font=("Consolas", 10)).pack(side="left", padx=12)
            del_btn = RoundedButton(header, "删除", command=lambda cc=cap: self._del(cc),
                                    width=56, height=24, radius=6, bg=THEME["ERROR"])
            del_btn.pack(side="right", padx=4)
            # 内容
            content_fr = tk.Frame(row, bg=title_bg)
            content_fr.pack(fill="x", padx=8, pady=(0,6))
            if unlocked:
                rc = RoundedContainer(content_fr, bg=THEME["CARD"], radius=10, padx=10, pady=10)
                rc.pack(fill="x")
                t = tk.Text(rc.inner, bg=THEME["CARD"], fg=THEME["TEXT"], height=5, bd=0,
                            font=("Microsoft YaHei", 10), wrap="word")
                t.pack(fill="x")
                t.insert("1.0", cap.get("content", "") or "(空)")
                t.configure(state="disabled")
            else:
                tk.Label(content_fr, text="🔒 🔒 🔒 内容已封存，到达解锁日期后才能查看 🔒 🔒 🔒",
                         bg=title_bg, fg=THEME["MUTED"],
                         font=("Microsoft YaHei", 10, "bold"), pady=10).pack()

    def _add(self):
        t = self.t_v.get().strip()
        d = self.d_v.get().strip()
        content = self.txt.get("1.0", "end").rstrip("\n")
        if not t:
            messagebox.showwarning("提示", "请输入标题"); return
        try:
            ud = datetime.datetime.strptime(d, "%Y-%m-%d").date()
        except Exception:
            messagebox.showwarning("提示", "日期格式应为 YYYY-MM-DD"); return
        if not content.strip():
            if not messagebox.askyesno("提示", "内容为空，确定封存空胶囊？"):
                return
        self.capsules.append({"title": t, "unlock_date": d, "content": content,
                              "created": datetime.date.today().strftime("%Y-%m-%d")})
        save_json("capsules.json", self.capsules)
        self.t_v.set(""); self.txt.delete("1.0", "end")
        self._render_list()
        messagebox.showinfo("成功", f"✅ 胶囊已封存！将于 {d} 解锁")

    def _del(self, cap):
        if not messagebox.askyesno("确认", "删除这个胶囊？"): return
        if cap in self.capsules:
            self.capsules.remove(cap)
        save_json("capsules.json", self.capsules)
        self._render_list()

# =========================================================
#  17. 二维码生成 (艺术化像素图案, 基于哈希)
# =========================================================
class QRPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app, "二维码生成")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        top = tk.Frame(wrap, bg=THEME["BG"])
        top.pack(fill="x", pady=(0, 10))
        left = tk.Frame(top, bg=THEME["BG"])
        left.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tk.Label(left, text="输入文本", bg=THEME["BG"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 10, "bold"), anchor="w").pack(fill="x")
        rc1 = RoundedContainer(left, bg=THEME["CARD"], radius=12, padx=10, pady=8)
        rc1.pack(fill="x")
        self.txt = tk.Text(rc1.inner, bg=THEME["CARD"], fg=THEME["TEXT"], bd=0, height=4,
                           font=("Consolas", 11), insertbackground=THEME["TEXT"], wrap="word")
        self.txt.pack(fill="x")
        self.txt.insert("1.0", "https://www.example.com")
        right = tk.Frame(top, bg=THEME["BG"])
        right.pack(side="left", fill="y")
        tk.Frame(right, bg=THEME["BG"], height=14).pack()
        RoundedButton(right, "⬛ 生成像素码", command=self._gen, width=160, height=36, radius=10).pack(pady=4)
        RoundedButton(right, "💾 保存为 .txt 图案", command=self._save_txt, bg=THEME["CARD"],
                      fg=THEME["TEXT"], width=160, height=36, radius=10).pack(pady=4)
        # 显示
        disp_card = RoundedContainer(wrap, radius=16, padx=16, pady=16)
        disp_card.pack(fill="both", expand=True)
        center = tk.Frame(disp_card.inner, bg=THEME["CARD"])
        center.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(center, width=420, height=420, bg=THEME["CARD"], highlightthickness=0)
        self.canvas.pack(pady=8)
        self.canvas.bind("<Configure>", lambda e: self._draw())
        self.text_lbl = tk.Label(center, text="", bg=THEME["CARD"], fg=THEME["MUTED"],
                                 font=("Microsoft YaHei", 10), wraplength=420, justify="center")
        self.text_lbl.pack(pady=(0,8))
        self.last_pattern = None
        self.after(40, self._gen)

    def _gen(self):
        text = self.txt.get("1.0", "end").rstrip("\n").strip()
        if not text:
            messagebox.showwarning("提示", "请输入文本"); return
        self.text_lbl.configure(text=text)
        self.last_pattern = self._make_pattern(text, size=29)
        self.last_text = text
        self._draw()

    @staticmethod
    def _make_pattern(text, size=29):
        # 基于文本哈希 + LFSR 生成确定性像素图案
        seed_bytes = hashlib.sha256(text.encode("utf-8")).digest()
        pattern = [[0]*size for _ in range(size)]
        # 三个定位方块
        def place_finder(r, c):
            for i in range(7):
                for j in range(7):
                    on = False
                    if i in (0, 6) or j in (0, 6): on = True
                    elif 2 <= i <= 4 and 2 <= j <= 4: on = True
                    pattern[r+i][c+j] = 1 if on else 0
        place_finder(0, 0)
        place_finder(0, size-7)
        place_finder(size-7, 0)
        # 填充其余部分，排除 finder 周围 8 像素边框
        state = list(seed_bytes)  # 32 bytes
        def rand_bit():
            # LFSR 混合
            s = state
            new = (s[0] ^ (s[2] << 1) ^ (s[3] << 2) ^ s[-1]) & 0xFF
            for k in range(len(s)-1):
                s[k] = s[k+1]
            s[-1] = new
            return new & 1
        # 中间同步图案 (垂直)
        for i in range(8, size-8):
            pattern[i][6] = 1 if i % 2 == 0 else 0
            pattern[6][i] = 1 if i % 2 == 0 else 0
        # 右下角小对齐图案
        if size >= 25:
            ar, ac = size-9, size-9
            for i in range(5):
                for j in range(5):
                    on = False
                    if i in (0,4) or j in (0,4): on = True
                    elif i == 2 and j == 2: on = True
                    pattern[ar+i][ac+j] = 1 if on else 0
        # 数据区域填充
        for r in range(size):
            for c in range(size):
                # 跳过 finder
                if (r < 8 and c < 8) or (r < 8 and c >= size-8) or (r >= size-8 and c < 8):
                    continue
                if r == 6 or c == 6:  # 同步
                    continue
                if size-9 <= r < size-4 and size-9 <= c < size-4:  # 对齐图案
                    continue
                # mask 0: (r+c)%2 == 0 -> 翻转
                b = rand_bit()
                if (r + c) % 2 == 0:
                    b = 1 - b
                pattern[r][c] = b
        return pattern

    def _draw(self):
        c = self.canvas
        c.delete("all")
        if not self.last_pattern:
            return
        W = c.winfo_width() or 420
        H = c.winfo_height() or 420
        S = min(W, H)
        pat = self.last_pattern
        n = len(pat)
        pad = S * 0.05
        cell = (S - 2*pad) / n
        # 白底
        c.create_rectangle(0, 0, W, H, fill="white", outline="")
        # 静区
        c.create_rectangle(pad, pad, S-pad, S-pad, fill="white", outline="")
        for r in range(n):
            for col in range(n):
                if pat[r][col]:
                    x0 = pad + col * cell
                    y0 = pad + r * cell
                    c.create_rectangle(x0, y0, x0+cell, y0+cell, fill="#000000", outline="")

    def _save_txt(self):
        if not self.last_pattern:
            return
        fn = filedialog.asksaveasfilename(defaultextension=".txt",
                                          filetypes=[("文本文件", "*.txt")],
                                          title="保存图案")
        if not fn: return
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write(f"文本: {self.last_text}\n\n")
                for row in self.last_pattern:
                    f.write("".join("█" if x else "·" for x in row) + "\n")
            messagebox.showinfo("保存", f"已保存到: {fn}")
        except Exception as e:
            messagebox.showerror("错误", str(e))

# =========================================================
#  18. 主题切换 (独立页面, 同时顶部栏也有入口)
# =========================================================
class ThemePage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app, "主题切换")

    def build_content(self):
        wrap = tk.Frame(self, bg=THEME["BG"])
        wrap.pack(fill="both", expand=True, padx=24, pady=8)
        card = RoundedContainer(wrap, radius=16, padx=24, pady=24)
        card.pack(fill="both", expand=True)
        tk.Label(card.inner, text="🎨 显示主题", bg=THEME["CARD"], fg=THEME["TEXT"],
                 font=("Microsoft YaHei", 18, "bold")).pack(pady=(8,4), anchor="w")
        tk.Label(card.inner, text="选择你喜欢的界面风格，切换后立即生效。",
                 bg=THEME["CARD"], fg=THEME["MUTED"],
                 font=("Microsoft YaHei", 10)).pack(anchor="w", pady=(0, 20))
        btns = tk.Frame(card.inner, bg=THEME["CARD"])
        btns.pack(fill="x")
        dark_card = RoundedContainer(btns, bg="#1A1A1F", radius=14, padx=16, pady=16)
        dark_card.pack(side="left", fill="both", expand=True, padx=6)
        dark_card.inner.configure(bg="#1A1A1F")
        self._theme_preview(dark_card.inner, "#141418", "#272730", "#6366F1", "#E8E8F0")
        RoundedButton(dark_card.inner, "🌙 深色主题 (当前)" if THEME_MODE == "dark" else "🌙 深色主题",
                      command=lambda: self._apply("dark"), width=180, height=38, radius=10,
                      bg="#6366F1").pack(pady=(16,0))
        light_card = RoundedContainer(btns, bg="#F5F6FA", radius=14, padx=16, pady=16)
        light_card.pack(side="left", fill="both", expand=True, padx=6)
        light_card.inner.configure(bg="#F5F6FA")
        self._theme_preview(light_card.inner, "#EDEEF3", "#FFFFFF", "#6366F1", "#1A1A2E")
        RoundedButton(light_card.inner, "☀️ 浅色主题 (当前)" if THEME_MODE == "light" else "☀️ 浅色主题",
                      command=lambda: self._apply("light"), width=180, height=38, radius=10,
                      bg="#6366F1").pack(pady=(16,0))
        # 设置保存
        self.auto_var = tk.BooleanVar(value=True)
        tk.Checkbutton(card.inner, text="记住我的主题偏好（重启后保留）", variable=self.auto_var,
                       bg=THEME["CARD"], fg=THEME["TEXT"], selectcolor=THEME["CARD"],
                       activebackground=THEME["CARD"], font=("Microsoft YaHei", 10)).pack(anchor="w", pady=(24,6))

    def _theme_preview(self, parent, sb, cb, pb, tx):
        p = tk.Frame(parent, bg=cb, height=180)
        p.pack(fill="x")
        sb_fr = tk.Frame(p, bg=sb, width=60)
        sb_fr.pack(side="left", fill="y")
        tk.Frame(sb_fr, bg=pb, height=20, width=30).pack(pady=10, padx=10, anchor="w")
        for _ in range(4):
            tk.Frame(sb_fr, bg="#888888", height=14, width=40).pack(pady=4, padx=8, anchor="w")
        main = tk.Frame(p, bg=cb)
        main.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        tk.Frame(main, bg=pb, height=18).pack(fill="x", pady=(0,6))
        for _ in range(3):
            cell = tk.Frame(main, bg=sb, height=36)
            cell.pack(fill="x", pady=3)
            tk.Frame(cell, bg=pb, height=22, width=22).pack(side="left", padx=6, pady=7)
            info = tk.Frame(cell, bg=sb)
            info.pack(side="left", fill="both", expand=True, pady=6)
            tk.Frame(info, bg=tx, height=8).pack(fill="x", padx=4, pady=2)
            tk.Frame(info, bg=tx, height=6).pack(fill="x", padx=4, pady=1)

    def _apply(self, mode):
        global THEME_MODE
        if mode == THEME_MODE:
            return
        if mode == "dark":
            THEME_MODE = "light"  # 反向触发 toggle
        else:
            THEME_MODE = "dark"
        self.app.toggle_theme_from_ui()

# =========================================================
#  工具定义 & 注册
# =========================================================
TOOL_CATEGORIES = [
    ("★ 常用", [
        ("JSON格式化", "📋", "美化/压缩/校验 JSON", JsonPage),
        ("Base64编解码", "🔐", "文本与 Base64 互转", Base64Page),
        ("密码生成器", "🔑", "一键生成安全密码", PasswordPage),
        ("单位换算", "📏", "长度/重量/温度换算", UnitPage),
        ("颜色选择器", "🎨", "选颜色查看 HEX/RGB", ColorPage),
        ("随机决定器", "🎲", "自定义/抽签/抛硬币", DeciderPage),
    ]),
    ("T 文本", [
        ("字数统计", "📝", "统计字符/中文/单词/行数", WordCountPage),
        ("文本对比", "🔍", "找出文本差异", DiffPage),
        ("Markdown预览", "📑", "编写并预览 Markdown", MarkdownPage),
        ("正则测试", "🧪", "正则表达式在线测试", RegexPage),
    ]),
    ("⊙ 时间", [
        ("番茄钟", "🍅", "专注 25 分钟工作法", PomodoroPage),
        ("倒计时", "⏳", "自定义时分秒倒计时", CountdownPage),
        ("纪念日管理", "📅", "记录重要日期倒计时", AnniversaryPage),
    ]),
    ("⚙ 杂项", [
        ("桌面便签", "🗒", "悬浮便签自动保存", StickyNotePage),
        ("简易记账", "💰", "收支记录一目了然", LedgerPage),
        ("时光胶囊", "💌", "写给未来的自己", CapsulePage),
        ("二维码生成", "⬛", "艺术化像素二维码", QRPage),
    ]),
    ("⚒ 系统", [
        ("主题切换", "🎨", "深色/浅色主题选择", ThemePage),
    ]),
]

def all_tools():
    """展开为 (分类名, 工具tuple) 的列表"""
    out = []
    for cat_name, tools in TOOL_CATEGORIES:
        for t in tools:
            out.append((cat_name, t))
    return out

# =========================================================
#  内联图标 (小 PNG, base64)
# =========================================================
# 32x32 简单 YB 图标 PNG (手工生成的小图标)
_icon_b64 = (
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAA7EAAAOxAGVKw4bAAADRklE"
    "QVRYhe2XS2gTQRiFv7S0tLi3btwIlfAiHjyAC3jwAHjwADz4ABx5AA86Bc+8BIPANHDp37ty5c+fM"
    "fCcrLy/fmzGze+bMzJxrYkhRUFBQUxPjN9T6A7kqLi73s0Q2ePB5vsdl2QVBYFCi5/l8Hi4nJ9Pr9"
    "eL1eLpcr8P7+Ph0Oh5FIJJKbEAIBAKBQOBf7AEAwHQ6jUKh8Hg8Ho+Hw+HA4XAkEolwuVwYDAa5Xi4"
    "UCsHm81m83g8lUqFsNvtcLvdWq/X0Wg0JJKVSqVQKBQwGAwwGAy8XC4ikYhhGIa4XC5arZbJZBJqtfr"
    "4XQ6hmHw+/3Q6XQ4HA7xeDyKRCLFYrFIJpNMJrNwu91wu90wmUwcDgdhGIbhcDhAIpGgGAacTqcWi8V"
    "yuRwOh8VisRgMBpxO59i2bbvdboTDYLfbKZfL8Xg8hmHw+Xy81+uttVr1er34fD7KZjK9Xm+Vy+Twe"
    "uVwuGo0GHx8f5HI5JpOJxWLBbDZ7nkAhELfb7QSDQbFYLJpOJ4/E4URRFKSkpjh49ur+/v3t7ewX6"
    "/f3Nzs6+e/duhmGYlJQU9/X1/f39jY2Nbdu27ezZs7i4uMOHD/f09PS6rq7u2NhYVVXV0tLSVqu14cOH"
    "T6fTOHjw4JeXlzdu3Dh6vR4mk+E8Ho9EosG73R6KRqPRaDR6vV4qlYqenp65ubnT19f39fVVU1PTBw8e"
    "9PLy8vb2duXk5Nzd3X17e+vv7//w8PD4+PiQy+U4nU7JZDKfz9/ZWq8Xj8eztLR0a2trra2tZ2dnPz8/"
    "+fDhQ61Wy76+vh6Px9PS0nJycnJ+fr7Ozsy9duvTVV19zcnLq6+t7eHh4eXn529vbY2JiYm5u7oKCgnp6elpe"
    "Xl1dXV19fX2tra19f3/f395+QkDAsLGXXqlLq6uppOp+vq6pqdnZ2Ojs7d1NSkqqrq4eHh7e3t8/Pz39z"
    "c4Nq1a8+ePdutVovn80+n08ePH+/i4qKamhrT6fTs7OxcVFSkVCp1eXn58+fP2tra2tpaamvry8rK0t7ezs"
    "jIyM7O/vv3LlyuTkZLRaLReePXv26NGj+fn5n5+fW61Wg8Gwvb2d5/N5eXn5y8tLS0vL4cOHf/z48e3b"
    "t9/c3Mz4+PjExMQff/wRFBQU8/v27S5dunT//v1ffv2pqKioqqrK4XCIyMjIxYsX2djY1NTUNBqNvb29"
    "w8PDX19fSqVSFBoaWlNTk8DAQGdn5w8//OC4ceMmjUYCgUBgZGQkODjY2tpafHw8PT29sLAQVVVVU1PTf/Pm"
    "zcLCQp1OR2RkpJaWFr9fL51OBwKBQGhoaA7wDa2srS01Nvb6+rqqrC4sKBAJpaWmxWAyJRCLHjx/PwMDA1"
    "taWqqqqoKAgPT2doVDQarVqtfr8/Hzy8nIaDAYDAYjMzPz888/H4lEwp6enlZWVl9fX5XL5ypUryrNmz"
    "Q8ePH4+Pj0+c+n4fD4bFYxGAwkJ+f7+/vL41Gw7lz5/74448dHx9/+eWXXl5eSqfTzZs3Hxsby9Sp0"
    "+vp6bGxsY2Pj2traunTp0pUrV958883W1tZu3br1r7/+2tra+u9//7u0tDStVgszMzPz+++/j81Gw6FD"
    "h4ODg2bNnv3HjxsjISH744YdLly796aefPv300+3t7Tds2DBlZWX19PScnJzcvn37ixcvDh8+fPDgQcLhcJKSk"
    "hqNRh6Px3x8fFlZWUQQ4IEHHnB3d3/33Xesrq5u3bp1+/btw4cPP/300+PHj9+2bdvDhw8P"
    "ODjYsGHDhQsXHjhw4EGDBw4ciIiIOH/+fI/H43x9fU1PT//6669PTk4uX778rbfeKioqSk1N/eDAA"
    "x8bG/v3vf7e1tS0tLW3dunXOnDnzww8/fPDgweHh4Tt37hw+fPjo0aOnTp3aWlpmz579/fbb2dlZ"
    "eXl5Y8eOLVq06Je//v3JJ588ePAgOTk5AQMGfOONN86bN2/evHn8+PHj06dPDwkJW7Zs2bRp0+Li"
    "4oiIiIODg7/++mutVqtOp9OxY8cOHTp07ty5M2fOnDt37ty5c+fOnTt37ty5c+fOnTt37ty5"
    "c+fO//8P6FhH9T+L8xMAAAAASUVORK5CYII="
)

def _find_icon_file():
    """查找同目录下的 icon.ico 文件"""
    # 1. PyInstaller 单文件解包目录
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        p = os.path.join(meipass, "icon.ico")
        if os.path.isfile(p):
            return p
    # 2. 脚本/EXE 所在目录
    try:
        base = os.path.dirname(os.path.abspath(sys.argv[0]))
        p = os.path.join(base, "icon.ico")
        if os.path.isfile(p):
            return p
    except Exception:
        pass
    # 3. 当前工作目录
    try:
        p = os.path.join(os.getcwd(), "icon.ico")
        if os.path.isfile(p):
            return p
    except Exception:
        pass
    return None


def try_set_icon(root):
    """设置窗口图标：优先使用同目录下的 icon.ico"""
    # 1. 优先用同目录 icon.ico（最佳，原生 ico 多分辨率）
    ico = _find_icon_file()
    if ico:
        try:
            root.iconbitmap(default=ico)
            return
        except Exception:
            pass
    # 2. 回退：内嵌 base64 PNG
    try:
        data = base64.b64decode(_icon_b64)
        tmp = os.path.join(DATA_DIR, "icon_tmp.png")
        with open(tmp, "wb") as f:
            f.write(data)
        try:
            img = tk.PhotoImage(file=tmp)
            root.iconphoto(True, img)
            root._icon_keep = img  # 保留引用
        except Exception:
            pass
    except Exception:
        pass
    except Exception:
        pass

# =========================================================
#  主应用
# =========================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        s = load_json("settings.json", {})
        global THEME, THEME_MODE
        if s.get("theme") == "light":
            THEME.update(LIGHT)
            THEME_MODE = "light"
        else:
            THEME.update(DARK)
            THEME_MODE = "dark"
        self.title("闫巴工具箱 YBv1.2")
        self.geometry("680x720")
        self.minsize(560, 600)
        self.configure(bg=THEME["BG"])
        try_set_icon(self)
        self.current_page_frame = None
        self._cards_mode = True
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.report_callback_exception = self._on_exception

    def _on_exception(self, etype, value, tb):
        try:
            messagebox.showerror("应用错误", f"{etype.__name__}: {value}")
        except Exception:
            pass

    def _build_ui(self):
        for c in self.winfo_children():
            c.destroy()
        # 顶部栏：占位给主题按钮，不与内容重叠
        topbar = tk.Frame(self, bg=THEME["BG"], height=36)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)
        self.content_frame = tk.Frame(self, bg=THEME["BG"])
        self.content_frame.pack(fill="both", expand=True)
        self.go_home(initial=True)
        self._add_home_theme_btn(topbar)

    def go_home(self, initial=False):
        try:
            for c in self.content_frame.winfo_children():
                c.destroy()
            self.current_page_frame = None
            self._cards_mode = True
            self._render_home(self.content_frame)
            self.title("闫巴工具箱 YBv1.2")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _render_home(self, parent):
        # 标题
        tk.Label(parent, text="闫 巴 工 具 箱", font=("Microsoft YaHei", 20, "bold"),
                 bg=THEME["BG"], fg=THEME["PRIMARY"]).pack(pady=(18, 3))
        tk.Label(parent, text="— 便捷桌面小工具集 —",
                 font=("Microsoft YaHei", 11), bg=THEME["BG"], fg=THEME["MUTED"]).pack(pady=(0, 10))
        # 可滚动卡片列表
        scroll_wrap = tk.Frame(parent, bg=THEME["BG"])
        scroll_wrap.pack(fill="both", expand=True)
        cv = tk.Canvas(scroll_wrap, bg=THEME["BG"], highlightthickness=0, bd=0)
        sb = tk.Scrollbar(scroll_wrap, orient="vertical", command=cv.yview,
                          bg=THEME["BG"], troughcolor=THEME["HOVER"],
                          activebackground=THEME["PRIMARY"])
        inner = tk.Frame(cv, bg=THEME["BG"])
        inner_id = cv.create_window((0, 0), window=inner, anchor="n")
        inner.bind("<Configure>",
                   lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def _on_cv_config(e):
            # 同步 inner 宽度 = Canvas 可视宽度（减去滚动条宽度），让卡片填满
            try:
                w = cv.winfo_width()
                if w > 1:
                    cv.itemconfigure(inner_id, width=w - 12)
            except Exception:
                pass
        cv.bind("<Configure>", _on_cv_config)

        def on_wheel(e):
            cv.yview_scroll(int(-1 * (e.delta / 120)), "units")
        cv.bind_all("<MouseWheel>", on_wheel)
        self._home_cv = cv
        self._home_inner = inner
        # 遍历所有分类的所有工具，垂直卡片列表
        for cat_name, tools in TOOL_CATEGORIES:
            for tool in tools:
                self._make_home_card(inner, tool)

    def _make_home_card(self, parent, tool):
        name, icon, desc, page_cls = tool
        # 卡片宽度跟随父容器（inner）变化：用 fill="x" + 绑定 <Configure> 动态调整高度
        card = tk.Frame(parent, bg=THEME["CARD"], cursor="hand2", height=84)
        card.pack_propagate(False)
        card.pack(fill="x", padx=8, pady=5)
        lf = tk.Frame(card, bg=THEME["CARD"])
        lf.pack(side="left", padx=(16, 10), pady=8)
        tk.Label(lf, text=icon, font=("Segoe UI Emoji", 30), bg=THEME["CARD"]).pack()
        rf = tk.Frame(card, bg=THEME["CARD"])
        rf.pack(side="left", fill="x", expand=True, pady=8)
        tk.Label(rf, text=name, font=("Microsoft YaHei", 12, "bold"),
                 bg=THEME["CARD"], fg=THEME["TEXT"]).pack(anchor="w")
        tk.Label(rf, text=desc, font=("Microsoft YaHei", 10),
                 bg=THEME["CARD"], fg=THEME["MUTED"]).pack(anchor="w", pady=(3, 0))
        arrow = tk.Label(card, text="→", font=("Microsoft YaHei", 18),
                        bg=THEME["CARD"], fg=THEME["PRIMARY"])
        arrow.pack(side="right", padx=16)
        hover_bg = "#2D2D44" if THEME_MODE == "dark" else "#F5F5F5"
        normal_bg = THEME["CARD"]

        def enter(e, c=card, l=lf, r=rf, a=arrow):
            for w in [c, l, r, a] + list(l.winfo_children()) + list(r.winfo_children()):
                try: w.configure(bg=hover_bg)
                except Exception: pass
        def leave(e, c=card, l=lf, r=rf, a=arrow):
            for w in [c, l, r, a] + list(l.winfo_children()) + list(r.winfo_children()):
                try: w.configure(bg=normal_bg)
                except Exception: pass
        def click(e, _cls=page_cls, _name=name):
            try:
                self.open_tool(_cls, _name)
            except Exception as ex:
                messagebox.showerror("错误", str(ex))
        for w in [card, lf, rf, arrow] + list(lf.winfo_children()) + list(rf.winfo_children()):
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)
            w.bind("<Button-1>", click)

    def open_tool(self, page_cls, name):
        try:
            # 解绑主页的 MouseWheel，避免滚动事件影响功能页/被销毁控件
            try:
                self.unbind_all("<MouseWheel>")
            except Exception:
                pass
            for c in self.content_frame.winfo_children():
                c.destroy()
            self._cards_mode = False
            self.current_page_frame = page_cls(self.content_frame, self)
            self.current_page_frame.pack(fill="both", expand=True)
            self.title(f"{name} - 闫巴工具箱 YBv1.2")
        except Exception as e:
            import traceback
            messagebox.showerror("打开失败", f"{e}\n\n{traceback.format_exc()}")
            self.go_home()

    def open_tool(self, page_cls, name):
        try:
            for c in self.content_frame.winfo_children():
                c.destroy()
            self._cards_mode = False
            self.current_page_frame = page_cls(self.content_frame, self)
            self.current_page_frame.pack(fill="both", expand=True)
            self.title(f"{name} - 闫巴工具箱 YBv1.2")
        except Exception as e:
            messagebox.showerror("打开失败", str(e))
            self.go_home()

    def _add_home_theme_btn(self, topbar):
        icon = "☀" if THEME_MODE == "dark" else "☾"
        btn = tk.Label(topbar, text=icon, font=("Segoe UI", 14),
                      bg=THEME["BG"], fg=THEME["MUTED"],
                      cursor="hand2", padx=12, pady=6)
        btn.pack(side="right", padx=10, pady=2)
        btn.bind("<Button-1>", lambda e: self.toggle_theme_from_ui())
        btn.bind("<Enter>", lambda e: btn.config(fg=THEME["PRIMARY"]))
        btn.bind("<Leave>", lambda e: btn.config(fg=THEME["MUTED"]))
        self._home_theme_btn = btn

    def toggle_theme_from_ui(self):
        try:
            global THEME, THEME_MODE
            if THEME_MODE == "dark":
                THEME.update(LIGHT)
                THEME_MODE = "light"
            else:
                THEME.update(DARK)
                THEME_MODE = "dark"
            s = load_json("settings.json", {})
            s["theme"] = THEME_MODE
            save_json("settings.json", s)
            self.configure(bg=THEME["BG"])
            self._build_ui()
            self.title("闫巴工具箱 YBv1.2")
        except Exception as e:
            messagebox.showerror("主题切换失败", str(e))

    def _on_close(self):
        try:
            s = load_json("settings.json", {})
            s["theme"] = THEME_MODE
            save_json("settings.json", s)
        except Exception:
            pass
        self.destroy()


# =========================================================
#  启动
# =========================================================
def main():
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        try:
            messagebox.showerror("启动失败", str(e))
        except Exception:
            print(f"启动失败: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()
