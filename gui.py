import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font, filedialog
import threading
import webbrowser
import os
import requests
from chaoxing_crawler import ChaoxingImageCrawler
import json
from datetime import datetime
from auto_cookie import get_cookie_auto


class ChaoxingCrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CYFORKK - 学习通图片爬取工具")
        self.root.geometry("900x820")
        self.root.minsize(800, 700)
        
        # 窗口居中
        self.center_window()

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        images_path = os.path.join(desktop_path, "images")

        if not os.path.exists(images_path):
            os.makedirs(images_path, exist_ok=True)

        self.default_save_dir = images_path

        self.cookie_modified = False
        self.crawl_mode = "course"  # 默认爬取课程图片

        self.setup_styles()
        self.create_widgets()
        self.load_saved_data()

        self.cookie_text.bind("<KeyRelease>", self.on_cookie_change)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_styles(self):
        self.colors = {
            "bg": "#f8fafc",
            "primary": "#3b82f6",
            "primary_hover": "#2563eb",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "text": "#1f2937",
            "text_light": "#6b7280",
            "border": "#e5e7eb",
            "white": "#ffffff",
            "header_bg": "#667eea",
            "header_fg": "#ffffff",
            "log_bg": "#0f172a",
            "log_fg": "#e2e8f0",
            "card_shadow": "#00000010",
        }

        self.root.configure(bg=self.colors["bg"])

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.colors["bg"])
        style.configure(
            "TLabel",
            background=self.colors["bg"],
            foreground=self.colors["text"],
            font=("Microsoft YaHei UI", 9),
        )
        style.configure(
            "Header.TLabel",
            font=("Microsoft YaHei UI", 12, "bold"),
            foreground=self.colors["primary"],
        )

        style.configure(
            "TEntry",
            fieldbackground=self.colors["white"],
            bordercolor=self.colors["border"],
            lightcolor=self.colors["border"],
            darkcolor=self.colors["border"],
            font=("Microsoft YaHei UI", 9),
            padding=8,
        )

        style.configure(
            "TButton",
            font=("Microsoft YaHei UI", 10, "bold"),
            padding=(15, 8),
            borderwidth=0,
            focuscolor="none",
        )
        style.map("TButton", background=[("active", self.colors["primary_hover"])])

        style.configure(
            "Primary.TButton",
            background=self.colors["primary"],
            foreground=self.colors["white"],
        )
        style.map(
            "Primary.TButton",
            background=[
                ("active", self.colors["primary_hover"]),
                ("pressed", self.colors["primary_hover"]),
            ],
        )

        style.configure(
            "Success.TButton",
            background=self.colors["success"],
            foreground=self.colors["white"],
        )
        style.map(
            "Success.TButton",
            background=[("active", "#45a049"), ("pressed", "#45a049")],
        )

        style.configure(
            "Warning.TButton",
            background=self.colors["warning"],
            foreground=self.colors["white"],
        )
        style.map(
            "Warning.TButton",
            background=[("active", "#f57c00"), ("pressed", "#f57c00")],
        )

        style.configure(
            "TLabelframe",
            background=self.colors["bg"],
            bordercolor=self.colors["border"],
        )
        style.configure(
            "TLabelframe.Label",
            background=self.colors["bg"],
            foreground=self.colors["primary"],
            font=("Microsoft YaHei UI", 10, "bold"),
        )

        style.configure("Horizontal.TScale", background=self.colors["bg"])

    def create_widgets(self):
        # 渐变头部
        header_frame = tk.Frame(self.root, bg="#667eea", height=70)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        # 添加阴影效果
        shadow_frame = tk.Frame(self.root, bg="#d1d5db", height=3)
        shadow_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="🚀 CYFORKK",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg="#667eea",
            fg=self.colors["header_fg"],
        )
        title_label.pack(side=tk.LEFT, padx=25, pady=20)

        subtitle_label = tk.Label(
            header_frame,
            text="学习通图片爬取工具 v1.0 ✨",
            font=("Microsoft YaHei UI", 10),
            bg="#667eea",
            fg="#e0e7ff",
        )
        subtitle_label.pack(side=tk.LEFT, padx=10, pady=22)

        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        input_frame = tk.Frame(main_container, bg=self.colors["bg"])
        input_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        log_frame = tk.Frame(main_container, bg=self.colors["bg"])
        log_frame.grid(row=1, column=0, sticky="nsew")

        self.create_url_section(input_frame)
        self.create_cookie_section(input_frame)
        self.create_directory_section(input_frame)
        self.create_action_buttons(input_frame)

        self.create_log_section(log_frame)

        input_frame.update()
        required_height = input_frame.winfo_reqheight()
        main_container.grid_rowconfigure(0, minsize=required_height)

    def create_section_frame(self, parent, title):
        # 卡片容器
        card_container = tk.Frame(parent, bg=self.colors["bg"])
        card_container.pack(fill=tk.X, pady=(0, 15))
        
        # 卡片阴影
        shadow = tk.Frame(card_container, bg="#d1d5db", height=2)
        shadow.pack(fill=tk.X, padx=2)
        
        # 主卡片
        frame = tk.Frame(card_container, bg=self.colors["white"], padx=20, pady=16)
        frame.pack(fill=tk.X)

        # 标题带图标
        title_frame = tk.Frame(frame, bg=self.colors["white"])
        title_frame.pack(fill=tk.X, pady=(0, 12))
        
        label = tk.Label(
            title_frame,
            text=f"📌 {title}",
            font=("Microsoft YaHei UI", 11, "bold"),
            bg=self.colors["white"],
            fg=self.colors["primary"],
            anchor="w",
        )
        label.pack(side=tk.LEFT)
        
        # 装饰线
        line = tk.Frame(title_frame, bg=self.colors["primary"], height=2)
        line.pack(fill=tk.X, pady=(8, 0))

        return frame

    def create_url_section(self, parent):
        section = self.create_section_frame(parent, "课程链接")

        self.url_entry = tk.Entry(
            section,
            font=("Microsoft YaHei UI", 10),
            bg="#f9fafb",
            fg=self.colors["text"],
            relief="flat",
            borderwidth=0,
            highlightthickness=2,
            highlightcolor=self.colors["primary"],
            highlightbackground=self.colors["border"],
            insertbackground=self.colors["primary"],
        )
        self.url_entry.pack(fill=tk.X, ipady=8)
        self.url_entry.insert(0, "")

    def create_cookie_section(self, parent):
        section = self.create_section_frame(parent, "Cookie")

        top_frame = tk.Frame(section, bg=self.colors["white"])
        top_frame.pack(fill=tk.X)

        header_frame = tk.Frame(top_frame, bg=self.colors["white"])
        header_frame.pack(fill=tk.X, pady=(0, 5))

        self.cookie_status_label = tk.Label(
            header_frame,
            text="📦 Cookie状态: 未保存",
            font=("Microsoft YaHei UI", 8),
            bg=self.colors["white"],
            fg=self.colors["text_light"],
        )
        self.cookie_status_label.pack(side=tk.LEFT)

        cookie_text_frame = tk.Frame(top_frame, bg=self.colors["white"])
        cookie_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.cookie_text = scrolledtext.ScrolledText(
            cookie_text_frame,
            height=6,
            font=("Consolas", 10),
            bg="#f9fafb",
            fg=self.colors["text"],
            relief="flat",
            borderwidth=0,
            wrap=tk.WORD,
            insertbackground=self.colors["primary"],
            selectbackground=self.colors["primary"],
            selectforeground="white",
        )
        self.cookie_text.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(top_frame, bg=self.colors["white"])
        btn_frame.pack(side=tk.RIGHT, padx=(10, 0))

        auto_btn = tk.Button(
            btn_frame,
            text="🤖\n自动",
            command=self.auto_get_cookie,
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=self.colors["success"],
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=12,
            activebackground="#059669",
        )
        auto_btn.pack(fill=tk.X, pady=(0, 5))

        clear_btn = tk.Button(
            btn_frame,
            text="🗑️\n清空",
            command=self.clear_cookie,
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=self.colors["error"],
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=12,
            activebackground="#dc2626",
        )
        clear_btn.pack(fill=tk.X)

    def create_directory_section(self, parent):
        section = self.create_section_frame(parent, "下载目录")

        dir_frame = tk.Frame(section, bg=self.colors["white"])
        dir_frame.pack(fill=tk.X)

        self.save_dir_entry = tk.Entry(
            dir_frame,
            font=("Microsoft YaHei UI", 9),
            bg="#fafafa",
            fg=self.colors["text"],
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=self.colors["primary"],
            highlightbackground=self.colors["border"],
        )
        self.save_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.save_dir_entry.insert(0, os.path.abspath(self.default_save_dir))

        browse_btn = tk.Button(
            dir_frame,
            text="📂 浏览",
            command=self.browse_directory,
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=self.colors["primary"],
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=18,
        )
        browse_btn.pack(side=tk.LEFT, padx=(10, 0))

    def create_action_buttons(self, parent):
        button_frame = tk.Frame(parent, bg=self.colors["bg"])
        button_frame.pack(fill=tk.X, pady=(8, 9))

        # 左侧按钮组
        left_frame = tk.Frame(button_frame, bg=self.colors["bg"])
        left_frame.pack(side=tk.LEFT)

        # 爬取模式选择
        mode_frame = tk.Frame(left_frame, bg=self.colors["bg"])
        mode_frame.pack(side=tk.LEFT, padx=(0, 10))

        self.mode_var = tk.StringVar(value="course")
        
        course_radio = tk.Radiobutton(
            mode_frame,
            text="📚 课程图片",
            variable=self.mode_var,
            value="course",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            cursor="hand2",
        )
        course_radio.pack(side=tk.LEFT, padx=(0, 5))

        homework_radio = tk.Radiobutton(
            mode_frame,
            text="📝 作业图片",
            variable=self.mode_var,
            value="homework",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            cursor="hand2",
        )
        homework_radio.pack(side=tk.LEFT)

        self.crawl_btn = tk.Button(
            left_frame,
            text="🚀 开始爬取",
            command=self.start_crawl,
            font=("Microsoft YaHei UI", 10, "bold"),
            bg=self.colors["primary"],
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=28,
            pady=9,
        )
        self.crawl_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.clear_btn = tk.Button(
            left_frame,
            text="🗑️ 清空日志",
            command=self.clear_log,
            font=("Microsoft YaHei UI", 9),
            bg="#757575",
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=9,
        )
        self.clear_btn.pack(side=tk.LEFT)

        save_btn = tk.Button(
            button_frame,
            text="💾 保存设置",
            command=self.save_settings,
            font=("Microsoft YaHei UI", 9),
            bg=self.colors["success"],
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=9,
        )
        save_btn.pack(side=tk.RIGHT)

    def create_log_section(self, parent):
        section_frame = tk.Frame(parent, bg=self.colors["white"], padx=16, pady=11)
        section_frame.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(section_frame, bg=self.colors["white"])
        header.pack(fill=tk.X, pady=(0, 7))

        tk.Label(
            header,
            text="📋 爬取日志",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=self.colors["white"],
            fg=self.colors["primary"],
            anchor="w",
        ).pack(side=tk.LEFT)

        self.log_text = scrolledtext.ScrolledText(
            section_frame,
            font=("Consolas", 9),
            bg=self.colors["log_bg"],
            fg=self.colors["log_fg"],
            relief="solid",
            borderwidth=1,
            wrap=tk.WORD,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.log_text.tag_config("INFO", foreground="#b0b0b0", font=("Consolas", 9))
        self.log_text.tag_config(
            "SUCCESS", foreground="#81C784", font=("Consolas", 9, "bold")
        )
        self.log_text.tag_config("WARNING", foreground="#FFB74D", font=("Consolas", 9))
        self.log_text.tag_config(
            "ERROR", foreground="#e57373", font=("Consolas", 9, "bold")
        )
        self.log_text.tag_config("DEBUG", foreground="#64B5F6", font=("Consolas", 9))

    def show_cookie_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("如何获取Cookie")
        help_window.geometry("650x600")
        help_window.configure(bg=self.colors["bg"])
        help_window.transient(self.root)
        help_window.grab_set()
        
        # 帮助窗口居中
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (650 // 2)
        y = (help_window.winfo_screenheight() // 2) - (600 // 2)
        help_window.geometry(f"650x600+{x}+{y}")

        header = tk.Frame(help_window, bg=self.colors["header_bg"], height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📖 如何获取Cookie",
            font=("Microsoft YaHei UI", 14, "bold"),
            bg=self.colors["header_bg"],
            fg="white",
        ).pack(pady=15)

        content_frame = tk.Frame(help_window, bg=self.colors["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        help_text = scrolledtext.ScrolledText(
            content_frame,
            width=70,
            height=25,
            wrap=tk.WORD,
            font=("Microsoft YaHei UI", 10),
            bg=self.colors["white"],
            fg=self.colors["text"],
            relief="solid",
            borderwidth=1,
        )
        help_text.pack(fill=tk.BOTH, expand=True)

        help_content = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 方法一：Chrome浏览器（推荐）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 打开Chrome浏览器，登录学习通网站
2. 进入你想要爬取的课程页面
3. 按F12打开开发者工具，或右键点击页面选择"检查"
4. 点击顶部的"Network"（网络）标签
5. 刷新页面（按F5）
6. 在左侧列表中点击任意一个请求
7. 在右侧找到"Request Headers"（请求头）区域
8. 找到"Cookie:"后面的内容
9. 复制整个Cookie值（包括等号和分号）
10. 将Cookie粘贴到本工具的Cookie输入框中


📌 方法二：Chrome浏览器（快捷方式）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 登录学习通并进入课程页面
2. 按F12打开开发者工具
3. 点击"Console"（控制台）标签
4. 在控制台输入：document.cookie
5. 按回车键，复制输出的内容


📌 方法三：Edge浏览器
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 打开Edge浏览器，登录学习通
2. 进入你想要爬取的课程页面
3. 按F12打开开发者工具
4. 点击顶部的"Network"（网络）标签
5. 刷新页面（按F5）
6. 点击左侧任意一个请求
7. 在右侧找到"Request Headers"（请求头）
8. 找到"Cookie:"后面的内容
9. 复制整个Cookie值


⚠️ 重要注意事项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Cookie包含您的个人信息，请勿泄露给他人
• Cookie可能会过期，如无法爬取请重新获取
• 请合理使用本工具，不要频繁爬取
• 避免给服务器造成过大压力
• 请遵守网站的使用条款和规定

        """

        help_text.insert(tk.END, help_content)
        help_text.config(state="disabled")

        btn_frame = tk.Frame(help_window, bg=self.colors["bg"])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Button(
            btn_frame,
            text="🌐 打开学习通",
            command=self.open_chaoxing,
            font=("Microsoft YaHei UI", 10, "bold"),
            bg=self.colors["primary"],
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            btn_frame,
            text="✖ 关闭",
            command=help_window.destroy,
            font=("Microsoft YaHei UI", 10),
            bg="#616161",
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
        ).pack(side=tk.LEFT)

    def open_chaoxing(self):
        webbrowser.open("https://i.mooc.chaoxing.com/space/")

    def browse_directory(self):
        current_dir = self.save_dir_entry.get().strip()
        if not current_dir:
            current_dir = os.path.abspath(self.default_save_dir)

        directory = filedialog.askdirectory(
            title="选择下载目录", initialdir=current_dir
        )
        if directory:
            self.save_dir_entry.delete(0, tk.END)
            self.save_dir_entry.insert(0, os.path.abspath(directory))

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")

        prefix = f"[{timestamp}] [{level}]"

        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, prefix + " ", level)
        self.log_text.insert(tk.END, message + "\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def save_settings(self):
        save_dir = self.save_dir_entry.get().strip()
        if save_dir:
            save_dir = os.path.abspath(save_dir)
        else:
            save_dir = os.path.abspath(self.default_save_dir)

        settings = {
            "url": self.url_entry.get().strip(),
            "save_dir": save_dir,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        cookie_str = self.cookie_text.get(1.0, tk.END).strip()
        if cookie_str:
            if self.save_cookie(cookie_str):
                self.log(f"✅ Cookie已保存", "SUCCESS")
                self.cookie_modified = False
            else:
                self.log(f"❌ 保存Cookie失败", "ERROR")

        try:
            with open("gui_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.log(f"✅ 设置已保存", "SUCCESS")
            self.log(f"📁 保存目录: {save_dir}", "INFO")
        except Exception as e:
            self.log(f"❌ 保存设置失败: {e}", "ERROR")

        self.update_cookie_status()

    def save_cookie(self, cookie_str):
        cookie_file = os.path.join(os.path.dirname(__file__), "saved_cookie.json")
        try:
            with open(cookie_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "cookie": cookie_str,
                        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            return True
        except Exception as e:
            return False

    def load_cookie(self):
        cookie_file = os.path.join(os.path.dirname(__file__), "saved_cookie.json")
        try:
            if os.path.exists(cookie_file):
                with open(cookie_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("cookie", ""), data.get("saved_at", "")
            return "", ""
        except Exception as e:
            return "", ""

    def auto_get_cookie(self):
        """自动获取Cookie"""
        result = messagebox.askyesno(
            "自动获取Cookie",
            "即将打开浏览器，请在浏览器中登录学习通。\n\n登录成功后，程序将自动获取Cookie。\n\n是否继续？"
        )
        
        if not result:
            return
        
        self.log("🤖 启动自动获取Cookie...", "INFO")
        
        def get_cookie_thread():
            try:
                cookie = get_cookie_auto(
                    callback=lambda msg: self.root.after(0, lambda: self.log(msg, "INFO")),
                    keep_browser_open=True  # 保持浏览器打开
                )
                
                if cookie:
                    self.root.after(0, lambda: self.cookie_text.delete(1.0, tk.END))
                    self.root.after(0, lambda: self.cookie_text.insert(1.0, cookie))
                    self.root.after(0, lambda: self.log("✅ Cookie获取成功！", "SUCCESS"))
                    
                    # 自动保存新Cookie
                    if self.save_cookie(cookie):
                        self.root.after(0, lambda: self.log("✅ Cookie已自动保存", "SUCCESS"))
                        self.cookie_modified = False
                    else:
                        self.cookie_modified = True
                    
                    self.root.after(0, self.update_cookie_status)
                else:
                    self.root.after(0, lambda: self.log("❌ Cookie获取失败", "ERROR"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"❌ 获取Cookie出错: {str(e)}", "ERROR"))
        
        thread = threading.Thread(target=get_cookie_thread)
        thread.daemon = False
        thread.start()

    def clear_cookie(self):
        self.cookie_text.delete(1.0, tk.END)
        self.cookie_modified = True
        self.log("🗑️ Cookie已清空", "WARNING")
        self.update_cookie_status()

    def on_cookie_change(self, event=None):
        self.cookie_modified = True
        self.update_cookie_status()

    def update_cookie_status(self):
        cookie_str = self.cookie_text.get(1.0, tk.END).strip()
        if not cookie_str:
            self.cookie_status_label.config(text="📦 Cookie状态: 空", fg="#9E9E9E")
        elif self.cookie_modified:
            self.cookie_status_label.config(text="📦 Cookie状态: 未保存", fg="#FF9800")
        else:
            _, saved_at = self.load_cookie()
            if saved_at and cookie_str == self.load_cookie()[0]:
                self.cookie_status_label.config(
                    text=f"✅ Cookie已保存 ({saved_at})", fg="#4CAF50"
                )
            else:
                self.cookie_status_label.config(
                    text="📦 Cookie状态: 未保存", fg="#FF9800"
                )

    def on_closing(self):
        if self.cookie_modified:
            cookie_str = self.cookie_text.get(1.0, tk.END).strip()
            if cookie_str:
                self.save_cookie(cookie_str)

        self.root.destroy()

    def load_saved_data(self):
        loaded_cookie = False

        try:
            cookie, saved_at = self.load_cookie()
            if cookie:
                self.cookie_text.delete(1.0, tk.END)
                self.cookie_text.insert(1.0, cookie)
                self.log(f"✅ 已加载保存的Cookie (保存于: {saved_at})", "SUCCESS")
                loaded_cookie = True
        except Exception as e:
            pass

        try:
            if not os.path.exists("gui_settings.json"):
                self.save_dir_entry.delete(0, tk.END)
                self.save_dir_entry.insert(0, self.default_save_dir)
                self.log(
                    f"📁 默认保存目录: {os.path.abspath(self.default_save_dir)}", "INFO"
                )
                self.update_cookie_status()
                return

            with open("gui_settings.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("url"):
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, data["url"])

            if data.get("save_dir"):
                saved_dir = data["save_dir"]
                self.save_dir_entry.delete(0, tk.END)
                self.save_dir_entry.insert(0, os.path.abspath(saved_dir))
            else:
                self.save_dir_entry.delete(0, tk.END)
                self.save_dir_entry.insert(0, os.path.abspath(self.default_save_dir))

            if not loaded_cookie:
                self.log("✅ 已加载上次保存的设置", "INFO")
        except Exception as e:
            self.save_dir_entry.delete(0, tk.END)
            self.save_dir_entry.insert(0, os.path.abspath(self.default_save_dir))

        self.update_cookie_status()

    def parse_cookie(self, cookie_str):
        cookies = {}
        pairs = cookie_str.split(";")
        for pair in pairs:
            pair = pair.strip()
            if "=" in pair:
                key, value = pair.split("=", 1)
                cookies[key.strip()] = value.strip()
        return cookies

    def validate_cookie(self, cookies):
        try:
            test_url = "https://mooc1.chaoxing.com/mooc-ans/mycourse/studentstudy"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            session = requests.Session()
            session.cookies.update(cookies)

            response = session.get(
                test_url, headers=headers, timeout=10, allow_redirects=False
            )

            if response.status_code == 200 or response.status_code == 302:
                return True
            elif "登录" in response.text or "login" in response.text.lower():
                return False
            else:
                return True
        except Exception:
            return False

    def start_crawl(self):
        url = self.url_entry.get().strip()
        cookie_str = self.cookie_text.get(1.0, tk.END).strip()
        save_dir = self.save_dir_entry.get().strip()
        crawl_mode = self.mode_var.get()

        if not url:
            if cookie_str:
                result = messagebox.askyesno(
                    "未检测到课程链接",
                    "未检测到课程链接！\n\n是否打开带Cookie的学习通浏览器？"
                )
                if result:
                    self.open_browser_with_cookie(cookie_str)
            else:
                messagebox.showwarning("提示", "请输入课程链接！")
            return

        if not cookie_str:
            result = messagebox.askyesno(
                "未检测到Cookie",
                "未检测到Cookie！\n\n是否自动打开浏览器获取Cookie？"
            )
            if result:
                self.auto_get_cookie()
            return

        if not save_dir:
            messagebox.showwarning("提示", "请输入下载目录！")
            return

        self.crawl_btn.config(state="disabled", bg="#9E9E9E")
        self.crawl_btn.config(text="⏳ 验证Cookie...")

        save_dir_abs = os.path.abspath(save_dir)

        mode_text = "课程图片" if crawl_mode == "course" else "作业图片"
        self.log("=" * 70, "INFO")
        self.log(f"🚀 开始爬取任务 - {mode_text}", "INFO")
        self.log(f"📚 课程链接: {url[:80]}...", "INFO")
        self.log(f"📁 保存目录: {save_dir_abs}", "INFO")
        self.log("=" * 70, "INFO")
        self.log("🔍 正在验证Cookie有效性...", "INFO")

        def validate_and_crawl():
            nonlocal cookie_str  # 声明使用外层变量
            try:
                cookies = self.parse_cookie(cookie_str)

                if not self.validate_cookie(cookies):
                    self.root.after(0, lambda: self.on_cookie_invalid())
                    return

                if self.cookie_modified and cookie_str:
                    self.save_cookie(cookie_str)
                    self.cookie_modified = False
                    self.root.after(0, self.update_cookie_status)

                self.root.after(0, lambda: self.crawl_btn.config(text="⏳ 爬取中..."))
                self.root.after(0, lambda: self.log("✅ Cookie验证通过", "SUCCESS"))

                crawler = ChaoxingImageCrawler(cookies)
                crawler.log_callback = self.log
                
                if crawl_mode == "course":
                    success = crawler.crawl_images(url, save_dir)
                else:
                    success = crawler.crawl_homework_images(url, save_dir)

                if success:
                    self.log("=" * 70, "SUCCESS")
                    self.log("✅ 爬取任务完成！", "SUCCESS")
                    self.log("=" * 70, "SUCCESS")
                    
                    # 爬取完成后打开带Cookie的浏览器
                    self.root.after(0, lambda: self.open_browser_with_cookie(cookie_str))
                else:
                    self.log("=" * 70, "ERROR")
                    self.log("❌ 爬取任务失败", "ERROR")
                    self.log("=" * 70, "ERROR")
            except Exception as e:
                self.log("=" * 70, "ERROR")
                self.log(f"❌ 爬取出错: {str(e)}", "ERROR")
                self.log("=" * 70, "ERROR")
            finally:
                self.root.after(
                    0,
                    lambda: self.crawl_btn.config(
                        state="normal", bg=self.colors["primary"]
                    ),
                )
                self.root.after(0, lambda: self.crawl_btn.config(text="🚀 开始爬取"))

        thread = threading.Thread(target=validate_and_crawl, daemon=True)
        thread.start()

    def open_browser_with_cookie(self, cookie_str):
        """打开带Cookie的浏览器"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            import time
            
            self.log("🌐 正在打开浏览器...", "INFO")
            
            chrome_options = Options()
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.maximize_window()
            
            # 先访问学习通任意页面建立域
            driver.get("https://www.chaoxing.com")
            time.sleep(1)
            
            # 添加Cookie
            cookies = self.parse_cookie(cookie_str)
            for name, value in cookies.items():
                try:
                    driver.add_cookie({
                        'name': name, 
                        'value': value, 
                        'domain': '.chaoxing.com',
                        'path': '/'
                    })
                except Exception as e:
                    pass
            
            # 跳转到学习通个人空间
            driver.get("https://i.mooc.chaoxing.com/space/")
            
            self.log("✅ 浏览器已打开，您可以继续操作", "SUCCESS")
        except Exception as e:
            self.log(f"❌ 打开浏览器失败: {str(e)}", "ERROR")
    
    def on_cookie_invalid(self):
        self.crawl_btn.config(state="normal", bg=self.colors["primary"])
        self.crawl_btn.config(text="🚀 开始爬取")
        self.log("=" * 70, "ERROR")
        self.log("❌ Cookie已失效或错误", "ERROR")
        self.log("=" * 70, "ERROR")

        result = messagebox.askyesno(
            "Cookie失效",
            "检测到Cookie已失效或错误！\n\n是否需要重新获取Cookie？\n\n点击'是'查看获取帮助，点击'否'继续尝试爬取",
        )

        if result:
            self.show_cookie_help()


def main():
    root = tk.Tk()
    app = ChaoxingCrawlerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
