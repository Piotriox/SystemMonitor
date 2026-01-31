# charts.py

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class ChartManager:
    def __init__(self, theme='dark'):
        self.theme = theme
        self.cpu_canvas = None
        self.ram_canvas = None
        self.network_canvas = None

    def create_cpu_chart(self, parent, width=6, height=2.5):
        fig = Figure(figsize=(width, height), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_ylim(0, 100)
        ax.set_ylabel('CPU %', fontsize=8)
        ax.set_xlabel('Seconds', fontsize=8)
        fig.patch.set_facecolor(self._get_chart_bg())
        ax.set_facecolor(self._get_chart_bg())
        ax.tick_params(colors=self._get_chart_fg(), labelsize=7)
        ax.spines['bottom'].set_color(self._get_chart_grid())
        ax.spines['left'].set_color(self._get_chart_grid())
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3, color=self._get_chart_grid())
        fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.12)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        self.cpu_canvas = (fig, ax, canvas)
        return canvas

    def create_ram_chart(self, parent, width=6, height=2.5):
        fig = Figure(figsize=(width, height), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_ylim(0, 100)
        ax.set_ylabel('RAM %', fontsize=8)
        ax.set_xlabel('Seconds', fontsize=8)
        fig.patch.set_facecolor(self._get_chart_bg())
        ax.set_facecolor(self._get_chart_bg())
        ax.tick_params(colors=self._get_chart_fg(), labelsize=7)
        ax.spines['bottom'].set_color(self._get_chart_grid())
        ax.spines['left'].set_color(self._get_chart_grid())
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3, color=self._get_chart_grid())
        fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.12)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        self.ram_canvas = (fig, ax, canvas)
        return canvas

    def create_network_chart(self, parent, width=6, height=2.5):
        fig = Figure(figsize=(width, height), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_ylabel('Speed (KB/s)', fontsize=8)
        ax.set_xlabel('Seconds', fontsize=8)
        fig.patch.set_facecolor(self._get_chart_bg())
        ax.set_facecolor(self._get_chart_bg())
        ax.tick_params(colors=self._get_chart_fg(), labelsize=7)
        ax.spines['bottom'].set_color(self._get_chart_grid())
        ax.spines['left'].set_color(self._get_chart_grid())
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3, color=self._get_chart_grid())
        fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.12)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        self.network_canvas = (fig, ax, canvas)
        return canvas

    def update_cpu_chart(self, data):
        if self.cpu_canvas is None:
            return
        fig, ax, canvas = self.cpu_canvas
        ax.clear()
        ax.set_ylim(0, 100)
        ax.set_ylabel('CPU %', fontsize=8)
        ax.set_xlabel('Seconds', fontsize=8)
        ax.set_facecolor(self._get_chart_bg())
        ax.tick_params(colors=self._get_chart_fg(), labelsize=7)
        ax.spines['bottom'].set_color(self._get_chart_grid())
        ax.spines['left'].set_color(self._get_chart_grid())
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3, color=self._get_chart_grid())
        
        if data:
            ax.plot(range(len(data)), data, color=self._get_cpu_color(), linewidth=2)
        
        canvas.draw_idle()

    def update_ram_chart(self, data):
        if self.ram_canvas is None:
            return
        fig, ax, canvas = self.ram_canvas
        ax.clear()
        ax.set_ylim(0, 100)
        ax.set_ylabel('RAM %', fontsize=8)
        ax.set_xlabel('Seconds', fontsize=8)
        ax.set_facecolor(self._get_chart_bg())
        ax.tick_params(colors=self._get_chart_fg(), labelsize=7)
        ax.spines['bottom'].set_color(self._get_chart_grid())
        ax.spines['left'].set_color(self._get_chart_grid())
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3, color=self._get_chart_grid())
        
        if data:
            ax.plot(range(len(data)), data, color=self._get_ram_color(), linewidth=2)
        
        canvas.draw_idle()

    def update_network_chart(self, up_data, down_data):
        if self.network_canvas is None:
            return
        fig, ax, canvas = self.network_canvas
        ax.clear()
        ax.set_ylabel('Speed (KB/s)', fontsize=8)
        ax.set_xlabel('Seconds', fontsize=8)
        ax.set_facecolor(self._get_chart_bg())
        ax.tick_params(colors=self._get_chart_fg(), labelsize=7)
        ax.spines['bottom'].set_color(self._get_chart_grid())
        ax.spines['left'].set_color(self._get_chart_grid())
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3, color=self._get_chart_grid())
        
        if up_data:
            ax.plot(range(len(up_data)), up_data, color=self._get_net_up_color(), linewidth=2, label='Upload')
        if down_data:
            ax.plot(range(len(down_data)), down_data, color=self._get_net_down_color(), linewidth=2, label='Download')
        
        if up_data or down_data:
            ax.legend(loc='upper left', fontsize=7, framealpha=0.9)
        
        canvas.draw_idle()

    def set_theme(self, theme):
        self.theme = theme

    def _get_chart_bg(self):
        from constants import THEMES
        return THEMES[self.theme]['chart_bg']

    def _get_chart_fg(self):
        from constants import THEMES
        return THEMES[self.theme]['chart_fg']

    def _get_chart_grid(self):
        from constants import THEMES
        return THEMES[self.theme]['chart_grid']

    def _get_cpu_color(self):
        from constants import CHART_COLORS
        return CHART_COLORS[self.theme]['cpu']

    def _get_ram_color(self):
        from constants import CHART_COLORS
        return CHART_COLORS[self.theme]['ram']

    def _get_net_up_color(self):
        from constants import CHART_COLORS
        return CHART_COLORS[self.theme]['net_up']

    def _get_net_down_color(self):
        from constants import CHART_COLORS
        return CHART_COLORS[self.theme]['net_down']
