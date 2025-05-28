<div align="center">

<h1>🎨 ComfyUI Image Effects</h1>

<img src="https://img.shields.io/badge/ComfyUI-Compatible-blue?style=for-the-badge" alt="ComfyUI Compatible">
<img src="https://img.shields.io/badge/Nodes-32-green?style=for-the-badge" alt="32 Nodes">
<img src="https://img.shields.io/badge/Categories-6-orange?style=for-the-badge" alt="6 Categories">
<img src="https://img.shields.io/badge/License-Apache%202.0-red?style=for-the-badge" alt="License">

<p><strong>Complete collection of professional image effects for ComfyUI</strong></p>

<p><em>Transform your images with 32 powerful nodes across 6 specialized categories</em></p>

<p><a href="#installation">📥 Installation</a> • <a href="#tutorial">📚 Tutorial</a> • <a href="#documentation">📖 Documentation</a></p>

</div>

<hr>

<h2>✨ <strong>Features</strong></h2>

<table>
<tr>
<td width="33%">

<h3>🎚️ <strong>Core Effects</strong> (7 nodes)</h3>
<ul>
<li>🎚️ Levels Adjustment</li>
<li>📈 RGB Curves</li>
<li>🎨 Color Balance</li>
<li>🌈 Vibrance & Saturation</li>
<li>🌗 Shadow/Highlight</li>
<li>🔀 Channel Mixer</li>
<li>💾 Saver Plus</li>
</ul>

</td>
<td width="33%">

<h3>🎨 <strong>Creative Effects</strong> (5 nodes)</h3>
<ul>
<li>🔮 Kaleidoscope Effect</li>
<li>✨ Kaleidoscope Advanced</li>
<li>🎭 ASCII Art Generator</li>
<li>📝 ASCII Text Generator</li>
<li>🎛️ CSS Filters</li>
</ul>

</td>
<td width="33%">

<h3>📼 <strong>Vintage Effects</strong> (5 nodes)</h3>
<ul>
<li>📼 VHS Glitch</li>
<li>🎞️ Film Grain</li>
<li>💡 Light Leaks</li>
<li>📺 Vintage TV</li>
<li>📷 Polaroid Effect</li>
</ul>

</td>
</tr>
<tr>
<td width="33%">

<h3>🌊 <strong>Deformation Effects</strong> (5 nodes)</h3>
<ul>
<li>🐠 Fisheye</li>
<li>🍐 Barrel Distortion</li>
<li>🌊 Ripple</li>
<li>🔵 Spherize</li>
<li>🤏 Pinch</li>
</ul>

</td>
<td width="33%">

<h3>💡 <strong>Light Effects</strong> (5 nodes)</h3>
<ul>
<li>💡 Lens Flare</li>
<li>🌞 God Rays</li>
<li>🌟 Neon Glow</li>
<li>🌈 Holographic</li>
<li>🌌 Aurora</li>
</ul>

</td>
<td width="33%">

<h3>🔺 <strong>Geometric Effects</strong> (5 nodes)</h3>
<ul>
<li>🔺 Triangulate</li>
<li>📐 Voronoi</li>
<li>⬡ Hexagonal Pixelate</li>
<li>❄️ Crystallize</li>
<li>🔷 Polygon</li>
</ul>

</td>
</tr>
</table>

<hr>

<h2 id="installation">📥 <strong>Installation</strong></h2>

<h3>Quick Install (Recommended)</h3>
<pre><code>cd ComfyUI/custom_nodes
git clone https://github.com/orion4d/ComfyUI-Image-Effects.git
cd ComfyUI-Image-Effects
pip install -r requirements.txt</code></pre>

<h3>Manual Install</h3>
<ol>
<li>Download the repository as ZIP</li>
<li>Extract to <code>ComfyUI/custom_nodes/ComfyUI-Image-Effects</code></li>
<li>Install dependencies: <code>pip install -r requirements.txt</code></li>
<li>Restart ComfyUI</li>
</ol>

<hr>

<h2 id="tutorial">📚 <strong>Tutorial - Getting Started</strong></h2>

<h3>Step 1: Basic Setup</h3>
<ol>
<li><strong>Start ComfyUI</strong> and open the default workflow</li>
<li><strong>Load an image</strong> using the "Load Image" node</li>
<li><strong>Add Image Effects nodes</strong> by right-clicking and selecting "Add Node" → "Image Effects"</li>
</ol>

<h3>Step 2: Basic Workflow</h3>
<pre><code>Load Image → Image Effect Node → Preview Image</code></pre>

<h3>Step 3: Using Core Effects</h3>
<p><strong>For color correction:</strong></p>
<ol>
<li>Add <strong>Levels Adjustment</strong> for exposure</li>
<li>Add <strong>Color Balance</strong> for temperature</li>
<li>Add <strong>Vibrance & Saturation</strong> for color intensity</li>
</ol>

<h3>Step 4: Using Creative Effects</h3>
<p><strong>For artistic transformation:</strong></p>
<ol>
<li>Add <strong>Kaleidoscope Effect</strong> for symmetrical patterns</li>
<li>Add <strong>ASCII Art Generator</strong> for text-based art</li>
<li>Add <strong>CSS Filters</strong> for web-style effects</li>
</ol>

<h3>Step 5: Using Vintage Effects</h3>
<p><strong>For retro aesthetics:</strong></p>
<ol>
<li>Add <strong>VHS Glitch</strong> for authentic artifacts</li>
<li>Add <strong>Film Grain</strong> for analog texture</li>
<li>Add <strong>Polaroid Effect</strong> for instant camera look</li>
</ol>

<h3>Step 6: Advanced Workflows</h3>
<p><strong>Combine multiple effects:</strong></p>
<pre><code>Load Image → Core Effect → Creative Effect → Vintage Effect → Save Image</code></pre>

<h3>Step 7: Tips & Tricks</h3>
<ul>
<li><strong>Start with low values</strong> and gradually increase</li>
<li><strong>Use Core effects first</strong> for color correction</li>
<li><strong>Chain effects</strong> for complex results</li>
<li><strong>Save workflows</strong> for reuse</li>
</ul>

<hr>

<h2 id="documentation">📖 <strong>Quick Reference</strong></h2>

<h3>Core Effects Usage</h3>
<table>
<tr>
<th>Node</th>
<th>Purpose</th>
<th>Best For</th>
</tr>
<tr>
<td>🎚️ Levels</td>
<td>Brightness/Contrast</td>
<td>Exposure correction</td>
</tr>
<tr>
<td>📈 Curves</td>
<td>Advanced color grading</td>
<td>Professional color work</td>
</tr>
<tr>
<td>🎨 Color Balance</td>
<td>Color temperature</td>
<td>Warm/cool adjustments</td>
</tr>
<tr>
<td>🌈 Vibrance</td>
<td>Color intensity</td>
<td>Making colors pop</td>
</tr>
<tr>
<td>🌗 Shadow/Highlight</td>
<td>Detail recovery</td>
<td>Fixing exposure</td>
</tr>
<tr>
<td>🔀 Channel Mixer</td>
<td>Color effects</td>
<td>Creative color mixing</td>
</tr>
<tr>
<td>💾 Saver Plus</td>
<td>Export control</td>
<td>High-quality saves</td>
</tr>
</table>

<h3>Creative Effects Usage</h3>
<table>
<tr>
<th>Node</th>
<th>Purpose</th>
<th>Best For</th>
</tr>
<tr>
<td>🔮 Kaleidoscope</td>
<td>Symmetrical patterns</td>
<td>Psychedelic art</td>
</tr>
<tr>
<td>✨ Kaleidoscope Advanced</td>
<td>Complex patterns</td>
<td>Advanced symmetry</td>
</tr>
<tr>
<td>🎭 ASCII Art</td>
<td>Text-based art</td>
<td>Retro computer style</td>
</tr>
<tr>
<td>📝 ASCII Text</td>
<td>Pure text output</td>
<td>Forum signatures</td>
</tr>
<tr>
<td>🎛️ CSS Filters</td>
<td>Web-style effects</td>
<td>Quick adjustments</td>
</tr>
</table>

<h3>Vintage Effects Usage</h3>
<table>
<tr>
<th>Node</th>
<th>Purpose</th>
<th>Best For</th>
</tr>
<tr>
<td>📼 VHS Glitch</td>
<td>Tape artifacts</td>
<td>Retro aesthetics</td>
</tr>
<tr>
<td>🎞️ Film Grain</td>
<td>Analog texture</td>
<td>Film simulation</td>
</tr>
<tr>
<td>💡 Light Leaks</td>
<td>Organic lighting</td>
<td>Vintage photography</td>
</tr>
<tr>
<td>📺 Vintage TV</td>
<td>CRT display</td>
<td>Old monitor look</td>
</tr>
<tr>
<td>📷 Polaroid</td>
<td>Instant camera</td>
<td>Nostalgic photos</td>
</tr>
</table>

<h3>Deformation Effects Usage</h3>
<table>
<tr>
<th>Node</th>
<th>Purpose</th>
<th>Best For</th>
</tr>
<tr>
<td>🐠 Fisheye</td>
<td>Wide-angle distortion</td>
<td>Lens effects</td>
</tr>
<tr>
<td>🍐 Barrel Distortion</td>
<td>Lens correction</td>
<td>Optical effects</td>
</tr>
<tr>
<td>🌊 Ripple</td>
<td>Water effects</td>
<td>Psychedelic distortion</td>
</tr>
<tr>
<td>🔵 Spherize</td>
<td>Bubble effects</td>
<td>Magnification</td>
</tr>
<tr>
<td>🤏 Pinch</td>
<td>Localized distortion</td>
<td>Artistic warping</td>
</tr>
</table>

<h3>Light Effects Usage</h3>
<table>
<tr>
<th>Node</th>
<th>Purpose</th>
<th>Best For</th>
</tr>
<tr>
<td>💡 Lens Flare</td>
<td>Optical reflections</td>
<td>Cinematic lighting</td>
</tr>
<tr>
<td>🌞 God Rays</td>
<td>Dramatic lighting</td>
<td>Divine effects</td>
</tr>
<tr>
<td>🌟 Neon Glow</td>
<td>Edge highlighting</td>
<td>Cyberpunk style</td>
</tr>
<tr>
<td>🌈 Holographic</td>
<td>Sci-fi effects</td>
<td>Futuristic displays</td>
</tr>
<tr>
<td>🌌 Aurora</td>
<td>Natural phenomena</td>
<td>Magical atmospheres</td>
</tr>
</table>

<h3>Geometric Effects Usage</h3>
<table>
<tr>
<th>Node</th>
<th>Purpose</th>
<th>Best For</th>
</tr>
<tr>
<td>🔺 Triangulate</td>
<td>Low-poly art</td>
<td>Geometric stylization</td>
</tr>
<tr>
<td>📐 Voronoi</td>
<td>Cellular patterns</td>
<td>Organic textures</td>
</tr>
<tr>
<td>⬡ Hexagonal Pixelate</td>
<td>Stylized pixels</td>
<td>Honeycomb effects</td>
</tr>
<tr>
<td>❄️ Crystallize</td>
<td>Crystal fragments</td>
<td>Shattered glass</td>
</tr>
<tr>
<td>🔷 Polygon</td>
<td>Shape reduction</td>
<td>Simplified art</td>
</tr>
</table>

<hr>

<h2>🛠️ <strong>Requirements</strong></h2>

<ul>
<li><strong>ComfyUI</strong> (Latest version)</li>
<li><strong>Python</strong> 3.8+</li>
<li><strong>Dependencies</strong> (auto-installed):
<ul>
<li>NumPy ≥ 1.21.0</li>
<li>OpenCV ≥ 4.5.0</li>
<li>SciPy ≥ 1.7.0</li>
<li>Pillow ≥ 8.0.0</li>
</ul>
</li>
</ul>

<hr>

<h2>🤝 <strong>Contributing</strong></h2>

<ol>
<li>Fork the repository</li>
<li>Create a feature branch</li>
<li>Commit your changes</li>
<li>Submit a pull request</li>
</ol>

<hr>

<h2>📄 <strong>License</strong></h2>

<p>This project is licensed under the <strong>Apache License 2.0</strong></p>

<hr>

<div align="center">

<h3>🌟 <strong>Show Your Support</strong></h3>

<p>If this project helped you, please consider giving it a ⭐ on GitHub!</p>

<p><strong>Made with ❤️ for the ComfyUI community</strong></p>

<p><strong>by Orion4D</strong></p>

<a href="https://ko-fi.com/orion4d">
<img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Buy Me A Coffee" height="41" width="174">
</a>

</div>

