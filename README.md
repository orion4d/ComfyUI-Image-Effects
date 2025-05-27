Image Effects – Collection of Image Effects for ComfyUI
A complete collection of image effect nodes for ComfyUI, organized into 7 categories.

📦 Installation
Clone this repository into your custom_nodes folder


📚 Complete Tutorial - Image Effects Package
Detailed guide of all image effect nodes for ComfyUI, organized by categories.

🎚️ Core Effects - Fundamental Adjustments
🎚️ Levels Adjustment
Allows adjusting the brightness and contrast levels of an image by modifying the input and output points of shadows, midtones, and highlights.

Main Parameters:

Input Black: Input black point (0-255)

Input White: Input white point (0-255)

Gamma: Gamma correction for midtones (0.1-3.0)

Output Black: Output black point (0-255)

Output White: Output white point (0-255)

Usage: Ideal for correcting exposure, increasing contrast, or precisely brightening/darkening an image.

📈 RGB Curves
Allows modifying the tone curves for each color channel (Red, Green, Blue) to precisely adjust brightness and contrast.

Main Parameters:

Curve Points: Control points of the curve (0-255)

Channel: Channel selection (RGB, Red, Green, Blue)

Interpolation: Type of interpolation (linear, spline)

Usage: Perfect for advanced color corrections, creating moods, or correcting color casts.

🎨 Color Balance
Allows adjusting the color balance in shadows, midtones, and highlights to correct or stylize the image.

Main Parameters:

Shadows: Cyan-Red, Magenta-Green, Yellow-Blue balance for shadows

Midtones: Balance for midtones

Highlights: Balance for highlights

Preserve Luminosity: Preserve luminosity

Usage: Excellent for correcting color casts or creating warm/cool atmospheres.

🌈 Vibrance & Saturation
Allows increasing or decreasing the vibrance and overall saturation of colors in the image.

Main Parameters:

Vibrance: Increases saturation of dull colors (-100 to +100)

Saturation: Overall saturation (-100 to +100)

Protect Skin Tones: Protect skin tones

Usage: Ideal for making colors more vivid without oversaturating skin tones.

🌗 Shadow/Highlight
Allows correcting shadows and highlights by adjusting their brightness and contrast.

Main Parameters:

Shadow Amount: Intensity of shadow correction (0-100)

Highlight Amount: Intensity of highlight correction (0-100)

Shadow Radius: Effect radius for shadows

Highlight Radius: Effect radius for highlights

Usage: Perfect for recovering details in dark or overexposed areas.

🔀 Channel Mixer
Allows mixing color channels to create custom color effects or correct colors.

Main Parameters:

Red Output: Contribution of R, G, B channels to the final red channel

Green Output: Contribution to the final green channel

Blue Output: Contribution to the final blue channel

Monochrome: Black and white mode

Usage: Excellent for creating infrared effects, custom black and white, or advanced color corrections.

💾 Saver Plus
Allows saving generated images with advanced options like format, quality, and save path.

Main Parameters:

Format: JPEG, PNG, TIFF, WebP

Quality: Compression quality (1-100)

Path: Custom save path

Metadata: Preserve metadata

Usage: Optimized saving with full control over format and quality.

🎨 Creative Effects - Artistic Effects
🔮 Kaleidoscope Effect
Creates a kaleidoscope effect by dividing the image into symmetrical facets with mirror and blend options.

Main Parameters:

Facets: Number of segments (2-20)

Center X/Y: Center position (0.0-1.0)

Radius: Effect radius (0.1-2.0)

Rotation: Base rotation (0-360°)

Mirror Mode: Alternate, All, None

Usage: Create hypnotic symmetrical patterns and psychedelic effects.

✨ Kaleidoscope Advanced
Advanced version of the kaleidoscope with more patterns, symmetry break, chromatic aberration, and artistic effects.

Main Parameters:

Pattern Type: Triangle, Diamond, Hexagon, Custom

Inner/Outer Radius: Control of effect area

Symmetry Break: Symmetry break (0.0-1.0)

Chromatic Aberration: Chromatic aberration (0.0-10.0)

Usage: Complex kaleidoscope effects with artistic variations and controlled imperfections.

🎭 ASCII Art Generator
Converts an image into ASCII art as an image with different styles and contrast options.

Main Parameters:

ASCII Resolution: Width in characters (20-200)

Style: Classic, Detailed, Minimal, Blocks

Invert: Tone inversion

Contrast Boost: Contrast amplification (1.0-4.0)

Font Scale: Font size (0.3-1.5)

Usage: Create stylized ASCII art with high-quality rendering.

📝 ASCII Text Generator
Generates pure ASCII text from an image, with style, border, and line numbering options.

Main Parameters:

ASCII Width: Width in characters (20-200)

Style: Classic, Detailed, Minimal, Blocks, Custom

Custom Chars: Custom characters

Add Border: Unicode border

Line Numbers: Line numbering

Usage: Generate exportable ASCII text for forums, social media, or documentation.

🎛️ CSS Filters
Applies classic CSS filters (blur, brightness, contrast, saturation, sepia, invert, etc.) to an image for a stylized look.

Main Parameters:

Blur: Gaussian blur (0.0-20.0)

Brightness: Brightness (0-300%)

Contrast: Contrast (0-300%)

Saturate: Saturation (0-300%)

Hue Rotate: Hue rotation (-180° to +180°)

Invert: Inversion (0-100%)

Usage: Reproduce CSS effects for web style or quick corrections.

📼 Vintage Effects - Retro Effects
📼 VHS Glitch
Simulates VHS artifacts with shifts, color bleeding, scan lines, noise, and jitter.

Main Parameters:

Glitch Intensity: Artifact intensity (0.0-1.0)

Color Shift: Chromatic shift (0.0-1.0)

Scan Lines: Scan lines (boolean)

Tracking Errors: Tracking errors

Color Bleeding: Color bleeding (0.0-1.0)

Frame Jitter: Frame jitter (0.0-1.0)

Usage: Create authentic nostalgic VHS effects with realistic artifacts.

🎞️ Film Grain
Adds realistic film grain with size, intensity, film type, and vintage tone options.

Main Parameters:

Grain Intensity: Grain intensity (0.0-1.0)

Grain Size: Grain size (0.1-3.0)

Film Type: 35mm, 16mm, 8mm, Super8

Color Grain: Colored grain (boolean)

Vintage Tone: Vintage tone (0.0-1.0)

Vignette: Vignetting (0.0-1.0)

Usage: Simulate different film types with authentic grain and characteristics.

💡 Light Leaks
Creates organic light leaks with color, position, intensity, and blur choices.

Main Parameters:

Leak Intensity: Leak intensity (0.0-1.0)

Leak Color: Warm, Cool, Rainbow, Vintage, Custom

Leak Count: Number of leaks (1-5)

Leak Position: Random, Corners, Edges, Center

Blur Amount: Leak blur (0.0-1.0)

Custom Hue: Custom hue (0-360°)

Usage: Add artistic light leaks for authentic vintage effect.

📺 Vintage TV
Simulates a retro TV screen with CRT curvature, static noise, scan lines, and color adjustments.

Main Parameters:

TV Type: CRT Color, CRT B&W, Old TV, Security Monitor

Scan Lines: Line intensity (0.0-1.0)

Curvature: CRT curvature (0.0-1.0)

Static Noise: Static noise (0.0-1.0)

Phosphor Glow: Phosphor glow (0.0-1.0)

Usage: Simulate display on old TVs with authentic CRT effects.

📷 Polaroid Effect
Adds a Polaroid border with vintage effect, paper texture, optional text, and random rotation.

Main Parameters:

Border Size: Border size (0.0-0.3)

Vintage Tone: Vintage tone (0.0-1.0)

Fade Amount: Fading (0.0-1.0)

Add Text: Add text (boolean)

Text Content: Text content

Paper Texture: Paper texture (0.0-1.0)

Usage: Create Polaroid photo effect with characteristic border and aging.

🌊 Deformation Effects - Geometric Distortions
🐠 Fisheye
Applies a fisheye distortion with control over field of view, center, and projection type.

Main Parameters:

FOV: Field of view (30-360°)

Mapping: Equidistant, Equisolid, Orthographic, Stereographic

Format: Fullframe, Circular

Center X/Y: Center position (0.0-1.0)

Strength: Effect strength (0.1-2.0)

Usage: Create extreme wide-angle effects or correct fisheye images.

🍐 Barrel Distortion
Applies barrel distortion with coefficients k1, k2, k3 and control over center and scale.

Main Parameters:

K1, K2, K3: Distortion coefficients (-1.0 to +1.0)

Center X/Y: Distortion center (0.0-1.0)

Scale: Global scale (0.1-2.0)

Usage: Correct or create lens distortions, magnifying effects.

🌊 Ripple
Creates concentric ripples with amplitude, frequency, wave type, phase, and decay.

Main Parameters:

Amplitude: Ripple amplitude (0.0-100.0)

Frequency: Wave frequency (0.001-0.1)

Wave Type: Sine, Cosine, Both

Center X/Y: Ripple center (0.0-1.0)

Phase: Phase shift (0.0-6.28)

Decay: Decay (0.0-1.0)

Usage: Simulate water ripples or create psychedelic effects.

🔵 Spherize
Applies a spherize or cylindrical effect with control over strength, radius, and center.

Main Parameters:

Strength: Spherize strength (-2.0 to +2.0)

Radius: Effect radius (0.1-2.0)

Center X/Y: Effect center (0.0-1.0)

Mode: Spherize, Cylindrical

Usage: Create bubble, magnifying glass, or spherical distortion effects.

🤏 Pinch
Applies a pinch or stretch effect with control over strength, radius, center, and falloff.

Main Parameters:

Strength: Pinch strength (-2.0 to +2.0)

Radius: Effect radius (0.1-1.0)

Center X/Y: Pinch center (0.0-1.0)

Falloff: Effect gradient (0.0-1.0)

Usage: Create localized pinch, stretch, or distortion effects.

💡 Light Effects - Lighting Effects
💡 Lens Flare
Adds lens flares with different types, intensity, size, position, color temperature, and number of rays.

Main Parameters:

Flare Type: Classic, Anamorphic, Starburst, Hexagonal

Intensity: Light intensity (0.0-2.0)

Size: Flare size (0.1-1.0)

Position X/Y: Source position (0.0-1.0)

Color Temp: Color temperature (2000-10000K)

Rays: Number of rays (4-12)

Usage: Simulate lens reflections for cinematic effects.

🌞 God Rays
Creates god rays with control over intensity, number of rays, length, position, color temperature, and decay.

Main Parameters:

Intensity: Ray intensity (0.0-2.0)

Num Rays: Number of rays (3-20)

Ray Length: Ray length (0.1-2.0)

Source X/Y: Source position (0.0-1.0)

Color Temp: Color temperature (2000-8000K)

Decay: Decay (0.1-1.0)

Usage: Create dramatic light rays for mystical scenes.

🌟 Neon Glow
Applies neon glow around detected edges with color choice, intensity, size, threshold, inner/outer glow, and pulsate.

Main Parameters:

Glow Color: Cyan, Magenta, Yellow, Red, Green, Blue, Purple, Orange

Intensity: Glow intensity (0.0-2.0)

Glow Size: Glow size (0.1-1.0)

Edge Threshold: Detection threshold (0.1-1.0)

Inner/Outer Glow: Inner/outer glow

Pulsate: Pulsation (boolean)

Usage: Create cyberpunk neon effects or highlight edges.

🌈 Holographic
Creates a holographic effect with intensity, interference lines, color shift, chromatic aberration, transparency, and flicker.

Main Parameters:

Intensity: Effect intensity (0.0-2.0)

Interference Lines: Number of lines (20-300)

Color Shift: Color shift (0.0-1.0)

Chromatic Aberration: Chromatic aberration (0.0-1.0)

Transparency: Transparency (0.1-1.0)

Flicker: Flicker (boolean)

Usage: Simulate futuristic holograms with interference.

🌌 Aurora
Simulates northern lights with intensity, color palette, wave frequency, position, height, animation speed, and opacity.

Main Parameters:

Intensity: Aurora intensity (0.0-2.0)

Color Palette: Green-Blue, Purple-Pink, Blue-Cyan, Multicolor

Wave Frequency: Wave frequency (0.005-0.1)

Position: Top, Bottom, Center

Height: Effect height (0.1-0.8)

Animation Speed: Animation speed (0.1-3.0)

Usage: Create realistic aurora borealis with smooth animation.

🔺 Geometric Effects - Geometric Patterns
🔺 Triangulate
Transforms the image into a triangular pattern based on Delaunay triangulation with options for point distribution, color, and outlines.

Main Parameters:

Num Points: Number of points (50-2000)

Edge Threshold: Detection threshold (0.1-1.0)

Color Mode: Average, Dominant, Gradient

Point Distribution: Random, Edge-based, Grid

Triangle Outline: Triangle outlines

Smoothing: Smoothing (0.0-1.0)

Usage: Create artistic low-poly effects with mathematical triangulation.

📐 Voronoi
Creates a colored Voronoi diagram with options for seeds, color, outlines, and distribution.

Main Parameters:

Num Seeds: Number of seeds (10-500)

Color Mode: Average, Center Point, Random

Cell Outline: Cell outlines

Seed Distribution: Random, Edge-based, Grid

Outline Color: Black, White, Adaptive

Outline Thickness: Thickness (1-5)

Usage: Generate organic or geometric cell patterns.

⬡ Hexagonal Pixelate
Pixelates the image with hexagons, controlling size, color, spacing, rotation, and outlines.

Main Parameters:

Hex Size: Hexagon size (5-100)

Color Mode: Average, Center, Dominant

Spacing: Spacing (0.5-1.0)

Rotation: Rotation (0-60°)

Outline: Outlines (boolean)

Outline Thickness: Thickness (1-3)

Usage: Create stylized and geometric hexagonal pixelation.

❄️ Crystallize
Applies a crystallization effect with crystal centers, shape, color variation, outlines, and randomness.

Main Parameters:

Crystal Size: Crystal size (10-100)

Num Crystals: Number of crystals (50-1000)

Crystal Shape: Angular, Organic, Geometric

Edge Enhancement: Edge enhancement (0.0-1.0)

Color Variation: Color variation (0.0-1.0)

Randomness: Randomness (0.0-1.0)

Usage: Simulate crystalline formations with complex geometric shapes.

🔷 Polygon
Reduces the image into polygons with control over number of sides, size, reduction, color, outlines, and rotation.

Main Parameters:

Polygon Sides: Number of sides (3-12)

Polygon Size: Polygon size (10-100)

Reduction Factor: Reduction factor (0.1-0.9)

Color Mode: Average, Dominant, Center

Edge Preservation: Edge preservation (0.0-1.0)

Rotation: Rotation (0-360°)

Outline: Outlines (boolean)

Usage: Create polygonal reduction effects with intelligent detail preservation.

🚀 General Usage Tips
Effect chaining: Combine multiple nodes for complex results
Progressive parameters: Start with low values and gradually increase
Preview: Use test images to understand effects
Saving: Use Saver Plus to save your creations with optimal quality

This package offers 32 nodes covering all aspects of creative image processing, from basic corrections to advanced artistic effects.
