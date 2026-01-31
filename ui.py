# ui.py

import tkinter as tk
from tkinter import ttk
from constants import THEMES, UPDATE_INTERVAL, MAX_HISTORY


class SystemMonitorUI:
    def __init__(self, root, stats_manager, chart_manager):
        self.root = root
        self.stats_manager = stats_manager
        self.chart_manager = chart_manager
        self.theme = 'dark'
        self.labels = {}
        self.chart_frames = {}
        self.section_frames = {}
        self.animation_step = 0
        
        self.root.title("System Monitor")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        self.root.bind('<Configure>', self._on_window_resize)
        
        self._setup_ui()
        self._apply_theme()
        self._animate_intro()

    def _setup_ui(self):
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill='both', expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self._create_header()
        self._create_cpu_section()
        self._create_ram_section()
        self._create_disk_section()
        self._create_network_section()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_window_resize(self, event):
        pass

    def _create_header(self):
        header_frame = tk.Frame(self.scrollable_frame)
        header_frame.pack(fill='x', pady=(8, 12), padx=8)
        
        title_label = tk.Label(header_frame, text="System Monitor", font=('Arial', 16, 'bold'))
        title_label.pack(side='left')
        
        self.theme_button = tk.Button(header_frame, text="☀️ Light Mode", command=self._toggle_theme, 
                                       width=12, font=('Arial', 9), cursor='hand2',
                                       relief='raised', bd=1)
        self.theme_button.pack(side='right')
        self.labels['theme_button'] = self.theme_button
        
        self._setup_button_hover(self.theme_button)

    def _create_cpu_section(self):
        section_frame = self._create_section("CPU", 'cpu_section')
        
        self.labels['cpu_label'] = tk.Label(section_frame, text="CPU: 0.0%", font=('Arial', 10, 'bold'))
        self.labels['cpu_label'].pack(anchor='w', pady=(0, 8))
        
        chart_frame = tk.Frame(section_frame)
        chart_frame.pack(fill='both', expand=False, pady=(0, 8))
        chart_frame.configure(height=140)
        self.chart_frames['cpu'] = chart_frame
        
        self.chart_manager.create_cpu_chart(chart_frame, width=8, height=1.4)

    def _create_ram_section(self):
        section_frame = self._create_section("Memory (RAM)", 'ram_section')
        
        self.labels['ram_label'] = tk.Label(section_frame, text="RAM: 0.0 / 0.0 GB (0.0%)", 
                                            font=('Arial', 10, 'bold'))
        self.labels['ram_label'].pack(anchor='w', pady=(0, 8))
        
        chart_frame = tk.Frame(section_frame)
        chart_frame.pack(fill='both', expand=False, pady=(0, 8))
        chart_frame.configure(height=140)
        self.chart_frames['ram'] = chart_frame
        
        self.chart_manager.create_ram_chart(chart_frame, width=8, height=1.4)

    def _create_disk_section(self):
        section_frame = self._create_section("Disk", 'disk_section')
        
        self.labels['disk_label'] = tk.Label(section_frame, text="Disk: 0.0%", font=('Arial', 10, 'bold'))
        self.labels['disk_label'].pack(anchor='w')

    def _create_network_section(self):
        section_frame = self._create_section("Network", 'network_section')
        
        stats_frame = tk.Frame(section_frame)
        stats_frame.pack(fill='x', pady=(0, 8))
        
        self.labels['net_up_label'] = tk.Label(stats_frame, text="Upload: 0.00 KB/s", font=('Arial', 10, 'bold'))
        self.labels['net_up_label'].pack(anchor='w')
        
        self.labels['net_down_label'] = tk.Label(stats_frame, text="Download: 0.00 KB/s", font=('Arial', 10, 'bold'))
        self.labels['net_down_label'].pack(anchor='w')
        
        chart_frame = tk.Frame(section_frame)
        chart_frame.pack(fill='both', expand=False)
        chart_frame.configure(height=140)
        self.chart_frames['network'] = chart_frame
        
        self.chart_manager.create_network_chart(chart_frame, width=8, height=1.4)

    def _create_section(self, title, section_key):
        section_frame = tk.Frame(self.scrollable_frame, relief='raised', bd=1)
        section_frame.pack(fill='x', pady=(0, 12), padx=8)
        self.section_frames[section_key] = section_frame
        
        section_title = tk.Label(section_frame, text=title, font=('Arial', 11, 'bold'))
        section_title.pack(anchor='w', pady=(8, 8), padx=8)
        
        content_frame = tk.Frame(section_frame)
        content_frame.pack(fill='x', padx=8, pady=(0, 8))
        
        return content_frame

    def update_display(self):
        self.stats_manager.update(MAX_HISTORY)
        
        cpu_percent = self.stats_manager.get_cpu_percent()
        self.labels['cpu_label'].config(text=f"CPU: {cpu_percent:.1f}%")
        self.chart_manager.update_cpu_chart(self.stats_manager.cpu_history)
        
        used_gb, total_gb, ram_percent = self.stats_manager.get_ram_info()
        self.labels['ram_label'].config(text=f"RAM: {used_gb:.2f} / {total_gb:.2f} GB ({ram_percent:.1f}%)")
        self.chart_manager.update_ram_chart(self.stats_manager.ram_history)
        
        disk_percent = self.stats_manager.get_disk_info()
        self.labels['disk_label'].config(text=f"Disk: {disk_percent:.1f}%")
        
        upload_kb, download_kb = self.stats_manager.get_network_speeds()
        upload_str = self.stats_manager.format_network_speed(upload_kb)
        download_str = self.stats_manager.format_network_speed(download_kb)
        self.labels['net_up_label'].config(text=f"Upload: {upload_str}")
        self.labels['net_down_label'].config(text=f"Download: {download_str}")
        self.chart_manager.update_network_chart(self.stats_manager.net_up_history, 
                                                self.stats_manager.net_down_history)

    def _toggle_theme(self):
        self.theme = 'light' if self.theme == 'dark' else 'dark'
        self.chart_manager.set_theme(self.theme)
        self._apply_theme()
        self.update_display()

    def _apply_theme(self):
        theme_colors = THEMES[self.theme]
        
        self.root.config(bg=theme_colors['bg'])
        self.canvas.config(bg=theme_colors['bg'])
        self.scrollable_frame.config(bg=theme_colors['bg'])
        
        for section_key, frame in self.section_frames.items():
            self._apply_section_theme(frame, theme_colors)
        
        for label_key, label in self.labels.items():
            if isinstance(label, tk.Label):
                label.config(bg=theme_colors['bg'], fg=theme_colors['fg'])
            elif isinstance(label, tk.Button):
                label.config(bg=theme_colors['accent'], fg=theme_colors['fg'], activebackground=theme_colors['border'])
        
        button_text = "🌙 Dark Mode" if self.theme == 'light' else "☀️ Light Mode"
        self.labels['theme_button'].config(text=button_text)

    def _apply_section_theme(self, frame, theme_colors):
        frame.config(bg=theme_colors['section_bg'], borderwidth=1)
        for child in frame.winfo_children():
            if isinstance(child, tk.Label):
                child.config(bg=theme_colors['section_bg'], fg=theme_colors['fg'])
            elif isinstance(child, tk.Frame):
                self._apply_frame_theme(child, theme_colors)

    def _apply_frame_theme(self, frame, theme_colors):
        frame.config(bg=theme_colors['section_bg'])
        for child in frame.winfo_children():
            if isinstance(child, tk.Label):
                child.config(bg=theme_colors['section_bg'], fg=theme_colors['fg'])
            elif isinstance(child, tk.Frame):
                self._apply_frame_theme(child, theme_colors)

    def _animate_intro(self):
        self.animation_step = 0
        self._animate_sections()

    def _animate_sections(self):
        if self.animation_step < len(self.section_frames):
            section_key = list(self.section_frames.keys())[self.animation_step]
            frame = self.section_frames[section_key]
            frame.pack_configure(pady=(0, 12))
            self.animation_step += 1
            self.root.after(50, self._animate_sections)

    def _setup_button_hover(self, button):
        def on_enter(event):
            theme_colors = THEMES[self.theme]
            button.config(bg=theme_colors['accent_hover'])
        
        def on_leave(event):
            theme_colors = THEMES[self.theme]
            button.config(bg=theme_colors['accent'])
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
