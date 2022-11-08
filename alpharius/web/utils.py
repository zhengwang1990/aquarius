"""Utility functions shared by multiple modules."""


def get_colored_value(value: str, color: str, with_arrow: bool = False):
    arrow = ''
    if with_arrow:
        if color == 'green':
            arrow = '<i class="uil uil-arrow-up"></i>'
        else:
            arrow = '<i class="uil uil-arrow-down"></i>'
    return f'<span style="color:{color};">{arrow}{value}</span>'


def get_signed_percentage(value: float, with_arrow: bool = False):
    color = 'green' if value >= 0 else 'red'
    return get_colored_value(f'{value * 100:+.2f}%', color, with_arrow)
