import numpy as np
import torch
from PIL import Image

class AsciiTextNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "ascii_width": ("INT", {"default": 80, "min": 20, "max": 200, "step": 10}),
                "style": (["classic", "detailed", "minimal", "blocks", "custom"], {"default": "classic"}),
                "invert": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "contrast_boost": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 4.0, "step": 0.1}),
                "height_compression": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 3.0, "step": 0.1}),
                "custom_chars": ("STRING", {"default": " .-+*#@", "multiline": False}),
                "add_border": ("BOOLEAN", {"default": False}),
                "line_numbers": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("ascii_text",)
    FUNCTION = "generate_ascii_text"
    CATEGORY = "Image Effects"
    OUTPUT_NODE = True

    def generate_ascii_text(self, image, ascii_width, style, invert, 
                           contrast_boost=2.0, height_compression=2.0, 
                           custom_chars=" .-+*#@", add_border=False, line_numbers=False):
        
        # Prendre la première image du batch
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        # Convertir en numpy
        img_np = img_tensor.cpu().numpy()
        original_h, original_w, c = img_np.shape
        
        print(f"ASCII Text: {original_w}x{original_h} → {ascii_width} chars wide")
        
        # Convertir en niveaux de gris
        gray = np.dot(img_np[..., :3], [0.2989, 0.5870, 0.1140])
        
        # Calculer les dimensions ASCII avec compression de hauteur
        ascii_height = int(ascii_width * (original_h / original_w) / height_compression)
        
        # Redimensionner l'image pour l'analyse ASCII
        gray_pil = Image.fromarray((gray * 255).astype(np.uint8))
        resized = np.array(gray_pil.resize((ascii_width, ascii_height), Image.Resampling.LANCZOS))
        
        # Améliorer le contraste
        enhanced = self._enhance_contrast(resized, contrast_boost)
        
        # Inverser si demandé
        if invert:
            enhanced = 255 - enhanced
        
        # Choisir le jeu de caractères
        ascii_chars = self._get_ascii_chars(style, custom_chars)
        
        # Normaliser et mapper aux caractères
        norm_pixels = (enhanced / 255) * (len(ascii_chars) - 1)
        norm_pixels = norm_pixels.astype(int)
        
        # Générer le texte ASCII
        ascii_text_lines = []
        for row_idx, row in enumerate(norm_pixels):
            line = "".join([ascii_chars[p] for p in row])
            
            # Ajouter les numéros de ligne si demandé
            if line_numbers:
                line = f"{row_idx+1:3d}: {line}"
            
            ascii_text_lines.append(line)
        
        # Ajouter une bordure si demandé
        if add_border:
            ascii_text_lines = self._add_border(ascii_text_lines, line_numbers)
        
        # Joindre toutes les lignes
        ascii_text = "\n".join(ascii_text_lines)
        
        # Ajouter des informations d'en-tête
        header = f"ASCII Art - {ascii_width}x{ascii_height} - Style: {style}\n"
        header += "=" * len(header.strip()) + "\n"
        
        final_text = header + ascii_text
        
        print(f"ASCII généré: {len(ascii_text_lines)} lignes, {len(ascii_text)} caractères")
        
        return (final_text,)
    
    def _enhance_contrast(self, image_array, boost_factor):
        """Améliorer le contraste pour un meilleur rendu ASCII"""
        # Normaliser
        normalized = image_array.astype(np.float32) / 255.0
        
        # Appliquer un boost de contraste
        enhanced = np.power(normalized, 1.0 / boost_factor)
        
        # Étalement d'histogramme
        min_val = np.min(enhanced)
        max_val = np.max(enhanced)
        
        if max_val > min_val:
            enhanced = (enhanced - min_val) / (max_val - min_val)
        
        # Appliquer une courbe en S pour plus de contraste
        enhanced = 0.5 * (1 + np.tanh(4 * (enhanced - 0.5)))
        
        return (enhanced * 255).astype(np.uint8)
    
    def _get_ascii_chars(self, style, custom_chars):
        """Obtenir le jeu de caractères selon le style"""
        styles = {
            "classic": list(" .:-=+*#%@"),
            "detailed": list(" ░▒▓█"),
            "minimal": list(" .-#@"),
            "blocks": list(" ▁▂▃▄▅▆▇█"),
            "custom": list(custom_chars)
        }
        
        chars = styles.get(style, styles["classic"])
        
        # S'assurer qu'on a au moins 2 caractères
        if len(chars) < 2:
            chars = list(" @")
        
        return chars
    
    def _add_border(self, text_lines, has_line_numbers):
        """Ajouter une bordure autour du texte ASCII"""
        if not text_lines:
            return text_lines
        
        # Calculer la largeur maximale
        max_width = max(len(line) for line in text_lines)
        
        # Caractères de bordure
        top_left = "┌"
        top_right = "┐"
        bottom_left = "└"
        bottom_right = "┘"
        horizontal = "─"
        vertical = "│"
        
        # Ligne du haut
        top_line = top_left + horizontal * (max_width + 2) + top_right
        
        # Ligne du bas
        bottom_line = bottom_left + horizontal * (max_width + 2) + bottom_right
        
        # Lignes avec bordures latérales
        bordered_lines = [top_line]
        for line in text_lines:
            padded_line = line.ljust(max_width)
            bordered_lines.append(f"{vertical} {padded_line} {vertical}")
        bordered_lines.append(bottom_line)
        
        return bordered_lines
