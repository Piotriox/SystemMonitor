# ui.py

import tkinter as tk
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
        self.canvas = None
        self.scrollbar = None

        self.root.title("System Monitor")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        self._setup_ui()
        self._apply_theme()
        self._animate_intro()

    def _setup_ui(self):
        # Create scrollable area using Canvas + Scrollbar
        self.canvas = tk.Canvas(self.root, borderwidth=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Main container inside the scrollable canvas (single vertical column)
        self.main_container = tk.Frame(self.canvas, bd=0)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_container, anchor="nw")

        # Padding inside the scrollable content
        self.main_container.configure(padx=12, pady=12)

        # Update scrollregion when content size changes
        self.main_container.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse wheel scrolling (Windows / Linux)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel)
        self.root.bind_all("<Button-5>", self._on_mousewheel)

        # Create sections from top to bottom as individual cards
        self._create_section_in_container("CPU", 'cpu_section', self.main_container, has_chart=True)
        self._create_section_in_container("Memory (RAM)", 'ram_section', self.main_container, has_chart=True)
        self._create_section_in_container("Integrated GPU", 'gpu_integrated_section', self.main_container, has_chart=False)
        self._create_section_in_container("Primary GPU", 'gpu_primary_section', self.main_container, has_chart=True)
        self._create_section_in_container("Network", 'network_section', self.main_container, has_chart=True)
        self._create_section_in_container("Disk", 'disk_section', self.main_container, has_chart=False)

    def _create_section_in_container(self, title, section_key, parent, has_chart=True):
        section_frame = tk.Frame(parent, relief='flat', bd=0)
        section_frame.pack(fill='x', pady=(0, 10))
        self.section_frames[section_key] = section_frame

        section_title = tk.Label(section_frame, text=title, font=('Inter', 11, 'bold'))
        section_title.pack(anchor='w', pady=(8, 4), padx=10)

        content_frame = tk.Frame(section_frame, bd=0)
        content_frame.pack(fill='x', padx=10, pady=(0, 10))

        if section_key == 'cpu_section':
            self.labels['cpu_label'] = tk.Label(content_frame, text="CPU: 0.0%", font=('Inter', 10, 'bold'))
            self.labels['cpu_label'].pack(anchor='w', pady=(6, 2))
            self.labels['cpu_model_label'] = tk.Label(
                content_frame,
                text="CPU Model: Detecting...",
                font=('Inter', 9)
            )
            self.labels['cpu_model_label'].pack(anchor='w', pady=(0, 4))
            if has_chart:
                chart_frame = tk.Frame(content_frame, bd=0)
                chart_frame.pack(fill='both', expand=False, pady=(0, 0))
                chart_frame.configure(height=80)
                self.chart_frames['cpu'] = chart_frame
                self.chart_manager.create_cpu_chart(chart_frame, width=3.5, height=0.85)
        
        elif section_key == 'ram_section':
            self.labels['ram_label'] = tk.Label(
                content_frame,
                text="RAM: 0.0 / 0.0 GB (0.0%)",
                font=('Inter', 10, 'bold')
            )
            self.labels['ram_label'].pack(anchor='w', pady=(0, 2))
            self.labels['ram_info_label'] = tk.Label(
                content_frame,
                text="RAM Info: Detecting...",
                font=('Inter', 9)
            )
            self.labels['ram_info_label'].pack(anchor='w', pady=(0, 4))
            if has_chart:
                chart_frame = tk.Frame(content_frame, bd=0)
                chart_frame.pack(fill='both', expand=False, pady=(0, 0))
                chart_frame.configure(height=80)
                self.chart_frames['ram'] = chart_frame
                self.chart_manager.create_ram_chart(chart_frame, width=3.5, height=0.85)
        
        elif section_key == 'gpu_integrated_section':
            self.labels['gpu_integrated_label'] = tk.Label(
                content_frame,
                text="Integrated GPU: 0.0% / No GPU",
                font=('Inter', 10, 'bold')
            )
            self.labels['gpu_integrated_label'].pack(anchor='w', pady=(0, 2))
            self.labels['gpu_integrated_name_label'] = tk.Label(
                content_frame,
                text="Integrated GPU Name: Detecting...",
                font=('Inter', 9)
            )
            self.labels['gpu_integrated_name_label'].pack(anchor='w', pady=(0, 4))
        
        elif section_key == 'gpu_primary_section':
            self.labels['gpu_primary_label'] = tk.Label(
                content_frame,
                text="Primary GPU: 0.0% / No GPU",
                font=('Inter', 10, 'bold')
            )
            self.labels['gpu_primary_label'].pack(anchor='w', pady=(0, 2))
            self.labels['gpu_primary_name_label'] = tk.Label(
                content_frame,
                text="Primary GPU Name: Detecting...",
                font=('Inter', 9)
            )
            self.labels['gpu_primary_name_label'].pack(anchor='w', pady=(0, 4))
            if has_chart:
                chart_frame = tk.Frame(content_frame, bd=0)
                chart_frame.pack(fill='both', expand=False, pady=(0, 0))
                chart_frame.configure(height=80)
                self.chart_frames['gpu_primary'] = chart_frame
                self.chart_manager.create_gpu_chart(chart_frame, width=3.5, height=0.85)
        
        elif section_key == 'disk_section':
            self.labels['disk_label'] = tk.Label(content_frame, text="Disk: 0.0%", font=('Inter', 10, 'bold'))
            self.labels['disk_label'].pack(anchor='w', pady=(0, 2))
            self.labels['disk_info_label'] = tk.Label(
                content_frame,
                text="Disk Info: Detecting...",
                font=('Inter', 9)
            )
            self.labels['disk_info_label'].pack(anchor='w')
        
        elif section_key == 'network_section':
            stats_frame = tk.Frame(content_frame, bd=0)
            stats_frame.pack(fill='x', pady=(0, 4))
            self.labels['net_up_label'] = tk.Label(stats_frame, text="Upload: 0.00 KB/s", font=('Inter', 10, 'bold'))
            self.labels['net_up_label'].pack(anchor='w')
            self.labels['net_down_label'] = tk.Label(stats_frame, text="Download: 0.00 KB/s", font=('Inter', 10, 'bold'))
            self.labels['net_down_label'].pack(anchor='w')
            if has_chart:
                chart_frame = tk.Frame(content_frame, bd=0)
                chart_frame.pack(fill='both', expand=False, pady=(0, 0))
                chart_frame.configure(height=80)
                self.chart_frames['network'] = chart_frame
                self.chart_manager.create_network_chart(chart_frame, width=3.5, height=0.85)

    def update_display(self):
        self.stats_manager.update(MAX_HISTORY)
        
        cpu_percent = self.stats_manager.get_cpu_percent()
        self.labels['cpu_label'].config(text=f"CPU: {cpu_percent:.1f}%")
        cpu_model = self.stats_manager.get_cpu_model()
        if 'cpu_model_label' in self.labels:
            self.labels['cpu_model_label'].config(text=f"CPU Model: {cpu_model}")
        self.chart_manager.update_cpu_chart(self.stats_manager.cpu_history)
        
        used_gb, total_gb, ram_percent = self.stats_manager.get_ram_info()
        self.labels['ram_label'].config(text=f"RAM: {used_gb:.2f} / {total_gb:.2f} GB ({ram_percent:.1f}%)")
        ram_type, ram_model = self.stats_manager.get_ram_hardware_info()
        if 'ram_info_label' in self.labels:
            self.labels['ram_info_label'].config(text=f"RAM Info: {ram_type} - {ram_model}")
        self.chart_manager.update_ram_chart(self.stats_manager.ram_history)
        
        integrated_load, integrated_name, primary_load, primary_name = self.stats_manager.get_dual_gpu_info()
        if 'gpu_integrated_label' in self.labels:
            self.labels['gpu_integrated_label'].config(
                text=f"Integrated GPU: {integrated_load:.1f}% / {integrated_name}"
            )
        if 'gpu_integrated_name_label' in self.labels:
            self.labels['gpu_integrated_name_label'].config(
                text=f"Integrated GPU Name: {integrated_name}"
            )

        if 'gpu_primary_label' in self.labels:
            self.labels['gpu_primary_label'].config(
                text=f"Primary GPU: {primary_load:.1f}% / {primary_name}"
            )
        if 'gpu_primary_name_label' in self.labels:
            self.labels['gpu_primary_name_label'].config(
                text=f"Primary GPU Name: {primary_name}"
            )

        # Keep the GPU chart focused on primary GPU history
        self.chart_manager.update_gpu_chart(self.stats_manager.gpu_history)
        
        disk_percent = self.stats_manager.get_disk_info()
        self.labels['disk_label'].config(text=f"Disk: {disk_percent:.1f}%")
        disk_type, disk_model = self.stats_manager.get_disk_hardware_info()
        if 'disk_info_label' in self.labels:
            self.labels['disk_info_label'].config(text=f"Disk Info: {disk_type} - {disk_model}")
        
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
        if self.canvas is not None:
            self.canvas.config(bg=theme_colors['bg'])
        if self.scrollbar is not None:
            # Dark-themed scrollbar
            self.scrollbar.config(bg=theme_colors['bg'], troughcolor=theme_colors['accent'],
                                  activebackground=theme_colors['accent_hover'], bd=0,
                                  highlightthickness=0, relief='flat')
        self.main_container.config(bg=theme_colors['bg'])
        
        for section_key, frame in self.section_frames.items():
            self._apply_section_theme(frame, theme_colors)
        
        for label_key, label in self.labels.items():
            if isinstance(label, tk.Label):
                label.config(bg=theme_colors['section_bg'], fg=theme_colors['fg'])

    def _apply_section_theme(self, frame, theme_colors):
        frame.config(bg=theme_colors['section_bg'], borderwidth=0)
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

    def _on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame."""
        if self.canvas is not None:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Ensure the inner frame always matches the canvas width."""
        if self.canvas is not None:
            self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        """Handle mouse wheel events for scrolling."""
        if self.canvas is None:
            return
        # Windows / MacOS use event.delta, Linux often uses Button-4/5
        if hasattr(event, "delta") and event.delta != 0:
            direction = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(direction, "units")
        elif hasattr(event, "num"):
            if event.num == 4:  # scroll up
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # scroll down
                self.canvas.yview_scroll(1, "units")

