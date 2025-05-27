import numpy as np
import torch
import cv2

class NeonGlowNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "glow_color": (["cyan", "magenta", "yellow", "red", "green", "blue", "purple", "orange"], {"default": "cyan"}),
                "intensity": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 2.0, "step": 0.1}),
                "glow_size": ("FLOAT", {"default": 0.3, "min": 0.1, "max": 1.0, "step": 0.05}),
            },
            "optional": {
                "edge_threshold": ("FLOAT", {"default": 0.3, "min": 0.1, "max": 1.0, "step": 0.05}),
                "inner_glow": ("BOOLEAN", {"default": True}),
                "outer_glow": ("BOOLEAN", {"default": True}),
                "pulsate": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_neon_glow"
    CATEGORY = "Image Effects"

    def apply_neon_glow(self, image, glow_color, intensity, glow_size,
                       edge_threshold=0.3, inner_glow=True, outer_glow=True, pulsate=False):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        result = img_np.copy().astype(np.float32)
        
        # Couleurs néon prédéfinies
        neon_colors = {
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "yellow": (255, 255, 0),
            "red": (255, 50, 50),
            "green": (50, 255, 50),
            "blue": (50, 50, 255),
            "purple": (200, 50, 255),
            "orange": (255, 150, 0)
        }
        
        color = neon_colors[glow_color]
        
        # Effet de pulsation
        pulse_factor = 1.0
        if pulsate:
            import time
            pulse_factor = 0.7 + 0.3 * np.sin(time.time() * 3)
        
        effective_intensity = intensity * pulse_factor
        
        # Détecter les contours
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, int(edge_threshold * 100), int(edge_threshold * 200))
        
        # Créer l'effet néon
        neon_overlay = self._create_neon_effect(edges, color, glow_size, 
                                              effective_intensity, inner_glow, outer_glow)
        
        # Fusionner avec l'image
        result = np.clip(result + neon_overlay, 0, 255)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
    
    def _create_neon_effect(self, edges, color, glow_size, intensity, inner_glow, outer_glow):
        """Créer l'effet néon à partir des contours"""
        h, w = edges.shape
        overlay = np.zeros((h, w, 3), dtype=np.float32)
        
        # Convertir les contours en image couleur
        edge_color = np.zeros((h, w, 3), dtype=np.float32)
        edge_mask = edges > 0
        edge_color[edge_mask] = color
        
        # Lueur intérieure
        if inner_glow:
            inner_blur_size = max(3, int(glow_size * 20))
            if inner_blur_size % 2 == 0:
                inner_blur_size += 1
            inner_glow_layer = cv2.GaussianBlur(edge_color, (inner_blur_size, inner_blur_size), 0)
            overlay += inner_glow_layer * 0.8
        
        # Lueur extérieure
        if outer_glow:
            outer_blur_size = max(5, int(glow_size * 40))
            if outer_blur_size % 2 == 0:
                outer_blur_size += 1
            outer_glow_layer = cv2.GaussianBlur(edge_color, (outer_blur_size, outer_blur_size), 0)
            overlay += outer_glow_layer * 0.4
        
        # Contour principal brillant
        overlay += edge_color * 1.5
        
        # Appliquer l'intensité
        overlay *= intensity
        
        return overlay
