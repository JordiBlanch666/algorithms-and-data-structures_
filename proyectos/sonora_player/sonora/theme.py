"""UI colors and supported audio formats."""

BG = "#090914"
PANEL = "#141426"
PANEL_LIGHT = "#20203a"
TEXT = "#f5f2ff"
MUTED = "#aaa6c7"
ACCENT = "#bb4dff"
MINT = "#27f5d0"
NEON_BLUE = "#39c8ff"
NEON_PINK = "#ff4fd8"

# .m4a/.aac (AAC, the iTunes format) are decoded with PyAV; everything else uses SDL_mixer.
AUDIO_TYPES = (".mp3", ".wav", ".ogg", ".flac", ".aiff", ".aif", ".m4a", ".aac")
AAC_TYPES = (".m4a", ".aac")
DRM_TYPES = (".m4p",)
