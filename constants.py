# constants.py

THEMES = {
    'dark': {
        'bg': '#0f172a',           # overall background (slate-900 style)
        'fg': '#e5e7eb',           # main text (gray-200)
        'accent': '#1e293b',       # cards background (slate-800)
        'accent_hover': '#334155', # hover state
        'chart_bg': '#020617',     # chart background (slate-950)
        'chart_grid': '#1f2937',   # subtle grid
        'chart_fg': '#e5e7eb',     # axis text
        'border': '#111827',       # card border
        'section_bg': '#020617',   # inner section background
    },
    'light': {
        'bg': '#f3f4f6',           # overall background (gray-100)
        'fg': '#111827',           # main text (gray-900)
        'accent': '#ffffff',       # cards background (white)
        'accent_hover': '#e5e7eb', # hover state
        'chart_bg': '#ffffff',
        'chart_grid': '#d1d5db',
        'chart_fg': '#111827',
        'border': '#e5e7eb',
        'section_bg': '#ffffff',
    }
}

CHART_COLORS = {
    'dark': {
        'cpu': '#ff6b6b',
        'ram': '#4ecdc4',
        'gpu': '#a78bfa',
        'net_up': '#45b7d1',
        'net_down': '#f7dc6f',
    },
    'light': {
        'cpu': '#e74c3c',
        'ram': '#1abc9c',
        'gpu': '#8b5cf6',
        'net_up': '#3498db',
        'net_down': '#f39c12',
    }
}

UPDATE_INTERVAL = 1000
MAX_HISTORY = 60
