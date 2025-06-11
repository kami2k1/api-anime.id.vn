"""
Font configuration utility for the anime video management application.
Provides optimized font selection for Windows systems.
"""

import tkinter.font as tkFont

class FontManager:
    """Manages font configuration for the application"""
    
    def __init__(self):
        self._main_font = None
        self._mono_font = None
        self._available_fonts = None
        
    @property
    def available_fonts(self):
        """Get list of available system fonts"""
        if self._available_fonts is None:
            try:
                self._available_fonts = tkFont.families()
            except:
                self._available_fonts = []
        return self._available_fonts
    
    @property
    def main_font(self):
        """Get the best main font for the application"""
        if self._main_font is None:
            self._main_font = self._get_best_font()
        return self._main_font
    
    @property 
    def mono_font(self):
        """Get the best monospace font for the application"""
        if self._mono_font is None:
            self._mono_font = self._get_best_mono_font()
        return self._mono_font
    
    def _get_best_font(self):
        """Select the best available font for UI elements"""
        font_priorities = [
            "Arial",
            "Segoe UI", 
            "MS Shell Dlg 2",
            "Helvetica",
            "DejaVu Sans",
            "Liberation Sans",
            "TkDefaultFont"
        ]
        
        try:
            families = self.available_fonts
            for font in font_priorities:
                if font in families:
                    return font
        except:
            pass
        
        return "Arial"  # Fallback
    
    def _get_best_mono_font(self):
        """Select the best available monospace font"""
        mono_priorities = [
            "Consolas",
            "Courier New",
            "Monaco", 
            "DejaVu Sans Mono",
            "Liberation Mono",
            "TkFixedFont"
        ]
        
        try:
            families = self.available_fonts
            for font in mono_priorities:
                if font in families:
                    return font
        except:
            pass
        
        return "Courier New"  # Fallback
    
    def get_font_tuple(self, size=12, weight="normal"):
        """Get a font tuple for use with tkinter widgets"""
        return (self.main_font, size, weight)
    
    def get_mono_font_tuple(self, size=12, weight="normal"):
        """Get a monospace font tuple for use with tkinter widgets"""
        return (self.mono_font, size, weight)

# Global font manager instance
font_manager = FontManager()

# Convenience functions for backwards compatibility
def get_main_font():
    """Get the main application font name"""
    return font_manager.main_font

def get_mono_font():
    """Get the monospace font name"""
    return font_manager.mono_font

def get_font_tuple(size=12, weight="normal"):
    """Get a main font tuple"""
    return font_manager.get_font_tuple(size, weight)

def get_mono_font_tuple(size=12, weight="normal"):
    """Get a monospace font tuple"""
    return font_manager.get_mono_font_tuple(size, weight)

# Export the main font for direct use
MAIN_FONT = font_manager.main_font
MONO_FONT = font_manager.mono_font
