import numpy as np
import torch
import cv2

class HolographicNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "intensity": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 2.0, "step": 0.1}),
                "interference_lines": ("INT", {"default": 100, "min": 20, "max": 300, "step": 10}),
                "color_shift": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.1}),
            },
            "optional": {
                "chromatic_aberration": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.05}),
                "transparency": ("FLOAT", {"default": 0.7, "min": 0.1, "max": 1.0, "step": 0.05}),
                "flicker": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_holographic"
    CATEGORY = "Image Effects"

    def apply_holographic(self, image, intensity, interference_lines, color_shift,
                         chromatic_aberration=0.3, transparency=0.7, flicker=True):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        result = img_np.copy().astype(np.float32)
        
        # Effet de scintillement
        flicker_factor = 1.0
        if flicker:
            import time
            flicker_factor = 0.8 + 0.2 * np.sin(time.time() * 10) * np.random.uniform(0.5, 1.0)
        
        # Appliquer la transparence
        result *= transparency
        
        # Aberration chromatique
        if chromatic_aberration > 0:
            result = self._apply_chromatic_aberration(result, chromatic_aberration)
        
        # Décalage de couleur holographique
        if color_shift > 0:
            result = self._apply_holographic_color_shift(result, color_shift)
        
        # Lignes d'interférence
        interference_overlay = self._create_interference_lines(h, w, interference_lines, intensity)
        result += interference_overlay
        
        # Appliquer le scintillement
        result *= flicker_factor
        
        # Normaliser
        result = np.clip(result, 0, 255)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
    
    def _apply_chromatic_aberration(self, image, strength):
        """Appliquer l'aberration chromatique"""
        h, w = image.shape[:2]
        
        # Séparer les canaux
        r_channel = image[:, :, 0]
        g_channel = image[:, :, 1]
        b_channel = image[:, :, 2]
        
        # Décalages pour chaque canal
        offset = int(strength * 3)
        
        # Décaler le rouge
        M_r = np.float32([[1, 0, offset], [0, 1, 0]])
        r_shifted = cv2.warpAffine(r_channel, M_r, (w, h))
        
        # Décaler le bleu
        M_b = np.float32([[1, 0, -offset], [0, 1, 0]])
        b_shifted = cv2.warpAffine(b_channel, M_b, (w, h))
        
        # Recombiner
        result = np.stack([r_shifted, g_channel, b_shifted], axis=2)
        return result
    
    def _apply_holographic_color_shift(self, image, shift_strength):
        """Appliquer un décalage de couleur holographique"""
        # Convertir en HSV
        hsv = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        
        # Créer un gradient de décalage de teinte
        h, w = image.shape[:2]
        y_gradient = np.linspace(0, 1, h).reshape(-1, 1)
        hue_shift = y_gradient * shift_strength * 180
        
        # Appliquer le décalage
        hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
        
        # Augmenter la saturation pour l'effet holographique
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + shift_strength * 0.5), 0, 255)
        
        # Reconvertir en RGB
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
        return result
    
    def _create_interference_lines(self, h, w, num_lines, intensity):
        """Créer des lignes d'interférence holographiques"""
        overlay = np.zeros((h, w, 3), dtype=np.float32)
        
        # Lignes horizontales d'interférence
        line_spacing = h // num_lines
        
        for i in range(0, h, line_spacing):
            # Variation d'intensité aléatoire
            line_intensity = intensity * np.random.uniform(0.3, 1.0)
            
            # Couleur arc-en-ciel basée sur la position
            hue = (i / h) * 360
            color = self._hsv_to_rgb(hue, 100, 100)
            
            # Dessiner la ligne avec dégradé
            line_thickness = max(1, line_spacing // 3)
            for j in range(line_thickness):
                if i + j < h:
                    alpha = 1.0 - (j / line_thickness)
                    overlay[i + j, :] = np.array(color) * line_intensity * alpha
        
        return overlay
    
    def _hsv_to_rgb(self, h, s, v):
        """Convertir HSV en RGB"""
        h = h / 60.0
        s = s / 100.0
        v = v / 100.0
        
        c = v * s
        x = c * (1 - abs((h % 2) - 1))
        m = v - c
        
        if 0 <= h < 1:
            r, g, b = c, x, 0
        elif 1 <= h < 2:
            r, g, b = x, c, 0
        elif 2 <= h < 3:
            r, g, b = 0, c, x
        elif 3 <= h < 4:
            r, g, b = 0, x, c
        elif 4 <= h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return ((r + m) * 255, (g + m) * 255, (b + m) * 255)
