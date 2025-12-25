"""
BreakGuard Theme Configuration
Centralized definition of colors, fonts, and spacing.
"""

from dataclasses import dataclass

@dataclass
class Colors:
    """Color palette for the application"""
    PRIMARY = "#0d7377"
    PRIMARY_HOVER = "#14a19f"
    BACKGROUND = "#f5f5f5"
    SURFACE = "#ffffff"
    TEXT = "#333333"
    TEXT_SECONDARY = "#595959"  # Changed from #666666 for better contrast (WCAG AA: 7:1 on white)
    TEXT_MUTED = "#95a5a6"  # Light gray for helper/hint text
    TEXT_DARK = "#2c3e50"  # Dark blue-gray for titles
    TEXT_MEDIUM = "#7f8c8d"  # Medium gray for subtitles
    TEXT_BODY = "#34495e"  # Dark gray for body text
    ICON_DARK = "#555555"  # Dark gray for icons
    SUCCESS = "#28a745"
    WARNING = "#e89f00"  # Darkened from #ffc107 for better contrast
    ERROR = "#dc3545"
    BORDER = "#e0e0e0"
    DIVIDER = "#ecf0f1"  # Very light gray for dividers
    
    # Legacy colors mapped to new system
    LOCK_BG = "#1e1e1e"  # Dark background for lock screen
    LOCK_TEXT = "#ffffff"

@dataclass
class Fonts:
    """Font configurations"""
    FAMILY_PRIMARY = "Segoe UI"
    FAMILY_MONO = "Consolas"
    
    SIZE_SMALL = "12px"
    SIZE_DEFAULT = "14px"
    SIZE_LARGE = "18px"
    SIZE_XL = "24px"
    SIZE_XXL = "32px"
    
    WEIGHT_NORMAL = "normal"
    WEIGHT_BOLD = "bold"

@dataclass
class Spacing:
    """Spacing scale"""
    XS = "4px"
    S = "8px"
    M = "12px"
    L = "16px"
    XL = "24px"
    XXL = "32px"

def load_stylesheet():
    """Load the QSS stylesheet"""
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    style_path = os.path.join(current_dir, 'styles.qss')
    
    try:
        with open(style_path, 'r') as f:
            qss = f.read()
            
        # Replace placeholders with actual values
        # This is a simple template engine for QSS
        replacements = {
            "@PRIMARY": Colors.PRIMARY,
            "@PRIMARY_HOVER": Colors.PRIMARY_HOVER,
            "@BACKGROUND": Colors.BACKGROUND,
            "@SURFACE": Colors.SURFACE,
            "@TEXT": Colors.TEXT,
            "@TEXT_SECONDARY": Colors.TEXT_SECONDARY,
            "@TEXT_MUTED": Colors.TEXT_MUTED,
            "@TEXT_DARK": Colors.TEXT_DARK,
            "@TEXT_MEDIUM": Colors.TEXT_MEDIUM,
            "@TEXT_BODY": Colors.TEXT_BODY,
            "@ICON_DARK": Colors.ICON_DARK,
            "@SUCCESS": Colors.SUCCESS,
            "@WARNING": Colors.WARNING,
            "@ERROR": Colors.ERROR,
            "@BORDER": Colors.BORDER,
            "@DIVIDER": Colors.DIVIDER,
            "@FONT_FAMILY": Fonts.FAMILY_PRIMARY,
            "@SPACING_M": Spacing.M,
            "@SPACING_L": Spacing.L
        }
        
        # Sort keys by length (descending) to prevent substring replacement issues
        # e.g. replace @PRIMARY_HOVER before @PRIMARY
        sorted_keys = sorted(replacements.keys(), key=len, reverse=True)
        
        for key in sorted_keys:
            qss = qss.replace(key, replacements[key])
            
        return qss
    except Exception as e:
        print(f"Error loading stylesheet: {e}")
        return ""
