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
        self.label_animations = {}
        
        self.root.title("System Monitor")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        self._setup_ui()
        self._apply_theme()
        self._animate_intro()

    def _setup_ui(self):
        # Create main container with two columns (no scroll)
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True, padx=12, pady=12)
        
        # Left column
        self.left_column = tk.Frame(self.main_container)
        self.left_column.pack(side='left', fill='both', expand=True, padx=(0, 8))
        
        # Right column
        self.right_column = tk.Frame(self.main_container)
        self.right_column.pack(side='right', fill='both', expand=True, padx=(8, 0))
        
        # Create sections in left column
        self._create_section_in_container("CPU", 'cpu_section', self.left_column, has_chart=True)
        self._create_section_in_container("GPU", 'gpu_section', self.left_column, has_chart=True)
        
        # Create sections in right column
        self._create_section_in_container("Memory (RAM)", 'ram_section', self.right_column, has_chart=True)
        self._create_section_in_container("Network", 'network_section', self.right_column, has_chart=True)
        
        # Create disk section (full width at bottom)
        self.disk_container = tk.Frame(self.root)
        self.disk_container.pack(fill='x', padx=12, pady=(0, 12))
        self._create_section_in_container("Disk", 'disk_section', self.disk_container, has_chart=False)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _create_header(self):
        pass

    def _create_section_in_container(self, title, section_key, parent, has_chart=True):
        section_frame = tk.Frame(parent, relief='raised', bd=1)
        section_frame.pack(fill='x', pady=(0, 10))
        self.section_frames[section_key] = section_frame
        
        section_title = tk.Label(section_frame, text=title, font=('Arial', 11, 'bold'))
        section_title.pack(anchor='w', pady=(6, 6), padx=6)
        
        content_frame = tk.Frame(section_frame)
        content_frame.pack(fill='x', padx=6, pady=(0, 6))
        
        if section_key == 'cpu_section':
            self.labels['cpu_label'] = tk.Label(content_frame, text="CPU: 0.0%", font=('Arial', 10, 'bold'))
            self.labels['cpu_label'].pack(anchor='w', pady=(6, 4))
            self.label_animations['cpu_label'] = {'current': '0.0', 'target': '0.0'}
            if has_chart:
                chart_frame = tk.Frame(content_frame)
                chart_frame.pack(fill='both', expand=False, pady=(0, 0))
                chart_frame.configure(height=80)
                self.chart_frames['cpu'] = chart_frame
                self.chart_manager.create_cpu_chart(chart_frame, width=3.5, height=0.85)
        
        elif section_key == 'ram_section':
            self.labels['ram_label'] = tk.Label(content_frame, text="RAM: 0.0 / 0.0 GB (0.0%)", 
                                                font=('Arial', 10, 'bold'))
            self.labels['ram_label'].pack(anchor='w', pady=(0, 4))
            self.label_animations['ram_label'] = {'current': '0.0', 'target': '0.0'}
            if has_chart:
                chart_frame = tk.Frame(content_frame)
                chart_frame.pack(fill='both', expand=False, pady=(0, 0))
                chart_frame.configure(height=80)
                self.chart_frames['ram'] = chart_frame
                self.chart_manager.create_ram_chart(chart_frame, width=3.5, height=0.85)
        
        elif section_key == 'gpu_section':
            self.labels['gpu_label'] = tk.Label(content_frame, text="GPU: 0.0% / No GPU", font=('Arial', 10, 'bold'))
            self.labels['gpu_label'].pack(anchor='w', pady=(0, 4))
            self.label_animations['gpu_label'] = {'current': '0.0', 'target': '0.0'}
            if has_chart:
                chart_frame = tk.Frame(content_frame)
                chart_frame.pack(fill='both', expand=False, pady=(0, 0))
                chart_frame.configure(height=80)
                self.chart_frames['gpu'] = chart_frame
                self.chart_manager.create_gpu_chart(chart_frame, width=3.5, height=0.85)
        
        elif section_key == 'disk_section':
            self.labels['disk_label'] = tk.Label(content_frame, text="Disk: 0.0%", font=('Arial', 10, 'bold'))
            self.labels['disk_label'].pack(anchor='w')
            self.label_animations['disk_label'] = {'current': '0.0', 'target': '0.0'}
        
        elif section_key == 'network_section':
            stats_frame = tk.Frame(content_frame)
            stats_frame.pack(fill='x', pady=(0, 4))
            self.labels['net_up_label'] = tk.Label(stats_frame, text="Upload: 0.00 KB/s", font=('Arial', 10, 'bold'))
            self.labels['net_up_label'].pack(anchor='w')
            self.labels['net_down_label'] = tk.Label(stats_frame, text="Download: 0.00 KB/s", font=('Arial', 10, 'bold'))
            self.labels['net_down_label'].pack(anchor='w')
            if has_chart:
                chart_frame = tk.Frame(content_frame)
                chart_frame.pack(fill='both', expand=False, pady=(0, 0))
                chart_frame.configure(height=80)
                self.chart_frames['network'] = chart_frame
                self.chart_manager.create_network_chart(chart_frame, width=3.5, height=0.85)

    def _create_cpu_section(self):
        pass

    def _create_ram_section(self):
        pass

    def _create_gpu_section(self):
        pass

    def _create_network_section(self):
        pass

    def _create_disk_section(self):
        pass

    def _create_section(self, title, section_key):
        pass

    def update_display(self):
        self.stats_manager.update(MAX_HISTORY)
        
        cpu_percent = self.stats_manager.get_cpu_percent()
        self.labels['cpu_label'].config(text=f"CPU: {cpu_percent:.1f}%")
        self.chart_manager.update_cpu_chart(self.stats_manager.cpu_history)
        
        used_gb, total_gb, ram_percent = self.stats_manager.get_ram_info()
        self.labels['ram_label'].config(text=f"RAM: {used_gb:.2f} / {total_gb:.2f} GB ({ram_percent:.1f}%)")
        self.chart_manager.update_ram_chart(self.stats_manager.ram_history)
        
        gpu_percent, gpu_name = self.stats_manager.get_gpu_info()
        self.labels['gpu_label'].config(text=f"GPU: {gpu_percent:.1f}% / {gpu_name}")
        self.chart_manager.update_gpu_chart(self.stats_manager.gpu_history)
        
        disk_percent = self.stats_manager.get_disk_info()
        self.labels['disk_label'].config(text=f"Disk: {disk_percent:.1f}%")
        
        upload_kb, download_kb = self.stats_manager.get_network_speeds()
        upload_str = self.stats_manager.format_network_speed(upload_kb)
        download_str = self.stats_manager.format_network_speed(download_kb)
        self.labels['net_up_label'].config(text=f"Upload: {upload_str}")
        self.labels['net_down_label'].config(text=f"Download: {download_str}")
        self.chart_manager.update_network_chart(self.stats_manager.net_up_history, 
                                                self.stats_manager.net_down_history)

    def _apply_theme(self):
        theme_colors = THEMES[self.theme]
        
        self.root.config(bg=theme_colors['bg'])
        self.main_container.config(bg=theme_colors['bg'])
        self.left_column.config(bg=theme_colors['bg'])
        self.right_column.config(bg=theme_colors['bg'])
        self.disk_container.config(bg=theme_colors['bg'])
        
        for section_key, frame in self.section_frames.items():
            self._apply_section_theme(frame, theme_colors)
        
        for label_key, label in self.labels.items():
            if isinstance(label, tk.Label):
                label.config(bg=theme_colors['section_bg'], fg=theme_colors['fg'])

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
            frame.pack_configure(pady=(0, 10))
            self.animation_step += 1
            self.root.after(30, self._animate_sections)  # Faster animation

    def _animate_label(self, label_key, new_value):
        if label_key not in self.label_animations:
            self.labels[label_key].config(text=new_value)
            return
        
        self.label_animations[label_key]['target'] = new_value
        self._update_label_animation(label_key)

    def _update_label_animation(self, label_key):
        self.labels[label_key].config(text=self.label_animations[label_key]['target'])
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
