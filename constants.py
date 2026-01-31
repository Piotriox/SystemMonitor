# constants.py

THEMES = {
    'dark': {
        'bg': '#1e1e1e',
        'fg': '#e0e0e0',
        'accent': '#2d2d2d',
        'accent_hover': '#3a3a3a',
        'chart_bg': '#2a2a2a',
        'chart_grid': '#404040',
        'chart_fg': '#e0e0e0',
        'border': '#404040',
        'section_bg': '#252525',
    },
    'light': {
        'bg': '#f5f5f5',
        'fg': '#1a1a1a',
        'accent': '#e8e8e8',
        'accent_hover': '#d8d8d8',
        'chart_bg': '#ffffff',
        'chart_grid': '#d0d0d0',
        'chart_fg': '#1a1a1a',
        'border': '#d0d0d0',
        'section_bg': '#fafafa',
    }
}

CHART_COLORS = {
    'dark': {
        'cpu': '#ff6b6b',
        'ram': '#4ecdc4',
        'net_up': '#45b7d1',
        'net_down': '#f7dc6f',
    },
    'light': {
        'cpu': '#e74c3c',
        'ram': '#1abc9c',
        'net_up': '#3498db',
        'net_down': '#f39c12',
    }
}

UPDATE_INTERVAL = 1000
MAX_HISTORY = 60
