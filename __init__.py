"""
Image Effects - Collection d'effets d'image pour ComfyUI
Version: 1.0.0
"""

# Imports des modules core
from .core.channel_mixer_node import ChannelMixerNode
from .core.color_balance_node import ColorBalanceNode
from .core.curves_node import CurvesNode
from .core.levels_node import LevelsNode
from .core.saver_plus_node import SaverPlusNode
from .core.shadow_highlight_node import ShadowHighlightNode
from .core.vibrance_node import VibranceNode

# Imports des modules creative
from .creative.ascii_art_node import AsciiArtNode
from .creative.ascii_text_node import AsciiTextNode
from .creative.css_filters_node import CSSFiltersNode
from .creative.kaleidoscope_node import KaleidoscopeNode, KaleidoscopeAdvancedNode

# Imports des modules vintage
from .vintage.vhs_glitch_node import VHSGlitchNode
from .vintage.film_grain_node import FilmGrainNode
from .vintage.light_leaks_node import LightLeaksNode
from .vintage.vintage_tv_node import VintageTVNode
from .vintage.polaroid_node import PolaroidNode

# Imports des modules deformation
from .deformation.fisheye_node import FisheyeNode
from .deformation.barrel_distortion_node import BarrelDistortionNode
from .deformation.ripple_node import RippleNode
from .deformation.spherize_node import SpherizeNode
from .deformation.pinch_node import PinchNode

# Imports des modules light effects
from .light_effects.lens_flare_node import LensFlareNode
from .light_effects.god_rays_node import GodRaysNode
from .light_effects.neon_glow_node import NeonGlowNode
from .light_effects.holographic_node import HolographicNode
from .light_effects.aurora_node import AuroraNode

# Imports des modules geometric
from .geometric.triangulate_node import TriangulateNode
from .geometric.voronoi_node import VoronoiNode
from .geometric.hexagonal_pixelate_node import HexagonalPixelateNode
from .geometric.crystallize_node import CrystallizeNode
from .geometric.polygon_node import PolygonNode

NODE_CLASS_MAPPINGS = {
    # Core Effects
    "ChannelMixerNode": ChannelMixerNode,
    "ColorBalanceNode": ColorBalanceNode,
    "CurvesNode": CurvesNode,
    "LevelsNode": LevelsNode,
    "SaverPlusNode": SaverPlusNode,
    "ShadowHighlightNode": ShadowHighlightNode,
    "VibranceNode": VibranceNode,
    
    # Creative Effects
    "AsciiArtNode": AsciiArtNode,
    "AsciiTextNode": AsciiTextNode,
    "CSSFiltersNode": CSSFiltersNode,
    "KaleidoscopeNode": KaleidoscopeNode,
    "KaleidoscopeAdvancedNode": KaleidoscopeAdvancedNode,

    # Vintage Effects
    "VHSGlitchNode": VHSGlitchNode,
    "FilmGrainNode": FilmGrainNode,
    "LightLeaksNode": LightLeaksNode,
    "VintageTVNode": VintageTVNode,
    "PolaroidNode": PolaroidNode,
    
    # Deformation
    "FisheyeNode": FisheyeNode,
    "BarrelDistortionNode": BarrelDistortionNode,
    "RippleNode": RippleNode,
    "SpherizeNode": SpherizeNode,
    "PinchNode": PinchNode,
    
    # Light effects
    "LensFlareNode": LensFlareNode,
    "GodRaysNode": GodRaysNode,
    "NeonGlowNode": NeonGlowNode,
    "HolographicNode": HolographicNode,
    "AuroraNode": AuroraNode,

    # Geometric
    "TriangulateNode": TriangulateNode,
    "VoronoiNode": VoronoiNode,
    "HexagonalPixelateNode": HexagonalPixelateNode,
    "CrystallizeNode": CrystallizeNode,
    "PolygonNode": PolygonNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # Core Effects
    "ChannelMixerNode": "🔀 Channel Mixer",
    "ColorBalanceNode": "🎨 Color Balance",
    "CurvesNode": "📈 RGB Curves",
    "LevelsNode": "🎚️ Levels Adjustment",
    "SaverPlusNode": "💾 Saver Plus",
    "ShadowHighlightNode": "🌗 Shadow/Highlight",
    "VibranceNode": "🌈 Vibrance & Saturation",
    
    # Creative Effects
    "AsciiArtNode": "🎭 ASCII Art Generator",
    "AsciiTextNode": "📝 ASCII Text Generator",
    "CSSFiltersNode": "🎛️ CSS Filters",
    "KaleidoscopeNode": "🔮 Kaleidoscope Effect",
    "KaleidoscopeAdvancedNode": "✨ Kaleidoscope Advanced",

    # Vintage Effects
    "VHSGlitchNode": "📼 VHS Glitch",
    "FilmGrainNode": "🎞️ Film Grain",
    "LightLeaksNode": "💡 Light Leaks",
    "VintageTVNode": "📺 Vintage TV",
    "PolaroidNode": "📷 Polaroid Effect",
    
    # Deformation
    "FisheyeNode": "🐠 Fisheye",
    "BarrelDistortionNode": "🍐 Barrel Distortion",
    "RippleNode": "🌊 Ripple",
    "SpherizeNode": "🔵 Spherize",
    "PinchNode": "🤏 Pinch",
    
    # Light effects
    "LensFlareNode": "💡 Lens Flare",
    "GodRaysNode": "🌞 God Rays",
    "NeonGlowNode": "🌟 Neon Glow",
    "HolographicNode": "🌈 Holographic",
    "AuroraNode": "🌌 Aurora",

    # Geometric
    "TriangulateNode": "🔺 Triangulate",
    "VoronoiNode": "📐 Voronoi",
    "HexagonalPixelateNode": "⬡ Hexagonal Pixelate",
    "CrystallizeNode": "❄️ Crystallize",
    "PolygonNode": "🔷 Polygon"
}

__version__ = "1.0.0"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "__version__"]

print(f"[Image Effects] Package v{__version__} loaded with {len(NODE_CLASS_MAPPINGS)} nodes")
print(f"[Image Effects] Core: 7 nodes, Creative: 5 nodes, Vintage: 5 nodes")
