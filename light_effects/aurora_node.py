import numpy as np
import torch
import cv2

class AuroraNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "intensity": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 2.0, "step": 0.1}),
                "color_palette": (["green_blue", "purple_pink", "blue_cyan", "multicolor"], {"default": "green_blue"}),
                "wave_frequency": ("FLOAT", {"default": 0.02, "min": 0.005, "max": 0.1, "step": 0.005}),
            },
            "optional": {
                "position": (["top", "bottom", "center"], {"default": "top"}),
                "height": ("FLOAT", {"default": 0.4, "min": 0.1, "max": 0.8, "step": 0.05}),
                "animation_speed": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.1}),
                "opacity": ("FLOAT", {"default": 0.7, "min": 0.1, "max": 1.0, "step": 0.05}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_aurora"
    CATEGORY = "Image Effects"

    def apply_aurora(self, image, intensity, color_palette, wave_frequency,
                    position="top", height=0.4, animation_speed=1.0, opacity=0.7):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        result = img_np.copy().astype(np.float32)
        
        # Palettes de couleurs d'aurore
        palettes = {
            "green_blue": [(0, 255, 100), (0, 200, 255), (50, 255, 150)],
            "purple_pink": [(200, 50, 255), (255, 100, 200), (150, 0, 255)],
            "blue_cyan": [(0, 100, 255), (0, 255, 255), (100, 150, 255)],
            "multicolor": [(0, 255, 100), (255, 100, 200), (100, 150, 255), (255, 200, 0)]
        }
        
        colors = palettes[color_palette]
        
        # Créer l'aurore
        aurora_overlay = self._create_aurora_effect(h, w, colors, wave_frequency, 
                                                  position, height, animation_speed, intensity)
        
        # Fusionner avec l'image
        result = result * (1 - opacity) + (result + aurora_overlay) * opacity
        result = np.clip(result, 0, 255)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
    
    def _create_aurora_effect(self, h, w, colors, frequency, position, height_ratio, speed, intensity):
        """Créer l'effet d'aurore boréale"""
        overlay = np.zeros((h, w, 3), dtype=np.float32)
        
        # Zone d'effet selon la position
        if position == "top":
            start_y = 0
            end_y = int(h * height_ratio)
        elif position == "bottom":
            start_y = int(h * (1 - height_ratio))
            end_y = h
        else:  # center
            center = h // 2
            half_height = int(h * height_ratio / 2)
            start_y = center - half_height
            end_y = center + half_height
        
        # Animation basée sur le temps
        import time
        time_factor = time.time() * speed
        
        # Créer plusieurs couches d'aurore
        for layer in range(len(colors)):
            color = colors[layer]
            
            # Décalage temporel pour chaque couche
            layer_time = time_factor + layer * 2
            
            # Créer les vagues d'aurore
            for y in range(start_y, end_y):
                # Intensité basée sur la position verticale
                y_factor = 1.0 - abs(y - (start_y + end_y) / 2) / ((end_y - start_y) / 2)
                
                for x in range(w):
                    # Calcul des vagues multiples
                    wave1 = np.sin(x * frequency + layer_time) * 0.5
                    wave2 = np.sin(x * frequency * 2.3 + layer_time * 1.7) * 0.3
                    wave3 = np.sin(x * frequency * 0.7 + layer_time * 0.8) * 0.2
                    
                    combined_wave = wave1 + wave2 + wave3
                    
                    # Intensité de l'aurore à ce point
                    aurora_intensity = max(0, combined_wave * y_factor * intensity)
                    
                    # Ajouter la couleur avec variation
                    for c in range(3):
                        overlay[y, x, c] += color[c] * aurora_intensity * (0.3 + 0.7 / (layer + 1))
        
        # Flou pour effet de diffusion
        overlay = cv2.GaussianBlur(overlay, (21, 21), 0)
        
        # Ajouter du bruit pour plus de réalisme
        noise = np.random.random((h, w, 3)) * 10
        overlay += noise
        
        return np.clip(overlay, 0, 255)
