import numpy as np
import torch
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

class AsciiArtNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "ascii_resolution": ("INT", {"default": 80, "min": 20, "max": 200, "step": 10}),
                "style": (["classic", "detailed", "minimal", "blocks"], {"default": "classic"}),
                "invert": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "background_color": (["white", "black", "gray"], {"default": "white"}),
                "text_color": (["black", "white", "auto"], {"default": "black"}),
                "contrast_boost": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 4.0, "step": 0.1}),
                "height_compression": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 3.0, "step": 0.1}),
                "font_scale": ("FLOAT", {"default": 0.9, "min": 0.3, "max": 1.5, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_ascii_art"
    CATEGORY = "Image Effects"

    def generate_ascii_art(self, image, ascii_resolution, style, invert, 
                          background_color="white", text_color="black", 
                          contrast_boost=2.0, height_compression=2.0, font_scale=0.9):
        
        # Prendre la première image du batch
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        # Convertir en numpy
        img_np = img_tensor.cpu().numpy()
        original_h, original_w, c = img_np.shape
        
        print(f"Image d'entrée: {original_w}x{original_h} pixels")
        
        # Convertir en niveaux de gris
        gray = np.dot(img_np[..., :3], [0.2989, 0.5870, 0.1140])
        
        # Calculer les dimensions ASCII avec compression de hauteur
        ascii_width = ascii_resolution
        ascii_height = int(ascii_width * (original_h / original_w) / height_compression)
        
        print(f"Résolution ASCII: {ascii_width}x{ascii_height} caractères")
        
        # Redimensionner l'image pour l'analyse ASCII
        gray_pil = Image.fromarray((gray * 255).astype(np.uint8))
        resized = np.array(gray_pil.resize((ascii_width, ascii_height), Image.Resampling.LANCZOS))
        
        # Améliorer le contraste AVANT la conversion ASCII
        resized = self._enhance_contrast(resized, contrast_boost)
        
        # Inverser si demandé
        if invert:
            resized = 255 - resized
        
        # Choisir le jeu de caractères
        ascii_chars = self._get_ascii_chars(style)
        
        # Normaliser et mapper aux caractères
        norm_pixels = (resized / 255) * (len(ascii_chars) - 1)
        norm_pixels = norm_pixels.astype(int)
        ascii_image = ascii_chars[norm_pixels]
        
        # Convertir en lignes de texte
        ascii_lines = ["".join(row) for row in ascii_image]
        
        # Créer l'image finale avec rendu optimisé
        result_image = self._create_high_quality_output(
            ascii_lines, original_w, original_h, 
            background_color, text_color, font_scale
        )
        
        print(f"Image de sortie: {original_w}x{original_h} pixels")
        
        # Convertir en tensor ComfyUI
        result_tensor = torch.from_numpy(result_image).unsqueeze(0)
        
        return (result_tensor,)
    
    def _enhance_contrast(self, image_array, boost_factor):
        """Améliorer drastiquement le contraste"""
        # Normaliser
        normalized = image_array.astype(np.float32) / 255.0
        
        # Appliquer un boost de contraste plus agressif
        enhanced = np.power(normalized, 1.0 / boost_factor)
        
        # Étalement d'histogramme
        min_val = np.min(enhanced)
        max_val = np.max(enhanced)
        
        if max_val > min_val:
            enhanced = (enhanced - min_val) / (max_val - min_val)
        
        # Appliquer une courbe en S pour plus de contraste
        enhanced = 0.5 * (1 + np.tanh(4 * (enhanced - 0.5)))
        
        return (enhanced * 255).astype(np.uint8)
    
    def _get_ascii_chars(self, style):
        """Jeux de caractères avec meilleur contraste"""
        styles = {
            "classic": np.array(list(" .:-=+*#%@")),
            "detailed": np.array(list(" ░▒▓█")),
            "minimal": np.array(list(" .-#@")),
            "blocks": np.array(list(" ▁▂▃▄▅▆▇█"))
        }
        return styles.get(style, styles["classic"])
    
    def _create_high_quality_output(self, ascii_lines, target_width, target_height, 
                                  background_color, text_color, font_scale):
        """Créer une image sans bord avec remplissage complet"""
        
        # Définir les couleurs
        bg_colors = {"white": (255, 255, 255), "black": (0, 0, 0), "gray": (128, 128, 128)}
        txt_colors = {"white": (255, 255, 255), "black": (0, 0, 0), "auto": None}
        
        bg_color = bg_colors.get(background_color, (255, 255, 255))
        txt_color = txt_colors.get(text_color, (0, 0, 0))
        
        # Auto color avec contraste maximal
        if text_color == "auto":
            txt_color = (0, 0, 0) if background_color == "white" else (255, 255, 255)
        
        # Créer l'image
        img = Image.new("RGB", (target_width, target_height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Calculer les dimensions
        chars_width = len(ascii_lines[0])
        chars_height = len(ascii_lines)
        
        # Calculer l'espacement pour REMPLIR COMPLÈTEMENT l'image
        char_spacing_w = target_width / chars_width
        char_spacing_h = target_height / chars_height
        
        # Taille de police pour remplir l'espace
        font_size = int(min(char_spacing_w, char_spacing_h) * font_scale)
        font_size = max(1, font_size)
        
        print(f"Taille de police calculée: {font_size}px")
        
        # Charger une police monospace avec fallback robuste
        font = self._load_best_font(font_size)
        
        # Dessiner le texte en remplissant TOUTE l'image
        for row, line in enumerate(ascii_lines):
            for col, char in enumerate(line):
                x = int(col * char_spacing_w)
                y = int(row * char_spacing_h)
                draw.text((x, y), char, fill=txt_color, font=font)
        
        # Améliorer le contraste de l'image finale
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Convertir en numpy array
        img_array = np.array(img).astype(np.float32) / 255.0
        
        return img_array
    
    def _load_best_font(self, font_size):
        """Charger la meilleure police monospace disponible"""
        fonts_to_try = [
            "consola.ttf",      # Windows
            "Monaco.ttf",       # macOS
            "DejaVuSansMono.ttf",  # Linux
            "LiberationMono-Regular.ttf",  # Linux alternative
            "CourierNew.ttf"    # Fallback
        ]
        
        for font_name in fonts_to_try:
            try:
                font = ImageFont.truetype(font_name, font_size)
                print(f"Police chargée: {font_name}")
                return font
            except:
                continue
        
        # Dernière option
        print("Utilisation de la police par défaut")
        return ImageFont.load_default()
