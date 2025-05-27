import numpy as np
import torch
import cv2

class PinchNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "strength": ("FLOAT", {"default": 0.5, "min": -2.0, "max": 2.0, "step": 0.1}),
                "radius": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 1.0, "step": 0.05}),
            },
            "optional": {
                "center_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "center_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "falloff": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_pinch"
    CATEGORY = "Image Effects"

    def apply_pinch(self, image, strength, radius, center_x=0.5, center_y=0.5, falloff=0.5):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        
        # Centre de l'effet
        cx = w * center_x
        cy = h * center_y
        
        # Rayon effectif
        effect_radius = min(w, h) / 2 * radius
        
        # Créer les grilles de coordonnées
        map_x = np.zeros((h, w), dtype=np.float32)
        map_y = np.zeros((h, w), dtype=np.float32)
        
        for y in range(h):
            for x in range(w):
                # Distance du centre
                dx = x - cx
                dy = y - cy
                distance = np.sqrt(dx*dx + dy*dy)
                
                if distance == 0 or distance > effect_radius:
                    map_x[y, x] = x
                    map_y[y, x] = y
                    continue
                
                # Facteur de distance normalisé
                norm_distance = distance / effect_radius
                
                # Calcul du facteur de pincement avec falloff
                if falloff > 0:
                    # Falloff doux
                    falloff_factor = 1 - np.power(norm_distance, 1 / falloff)
                else:
                    # Falloff linéaire
                    falloff_factor = 1 - norm_distance
                
                # Facteur de pincement
                if strength > 0:
                    # Pincement vers l'intérieur
                    pinch_factor = 1 - (strength * falloff_factor)
                else:
                    # Étirement vers l'extérieur
                    pinch_factor = 1 + (abs(strength) * falloff_factor)
                
                # Nouvelles coordonnées
                new_distance = distance * pinch_factor
                angle = np.arctan2(dy, dx)
                
                new_x = cx + new_distance * np.cos(angle)
                new_y = cy + new_distance * np.sin(angle)
                
                map_x[y, x] = np.clip(new_x, 0, w - 1)
                map_y[y, x] = np.clip(new_y, 0, h - 1)
        
        # Appliquer la transformation
        result = cv2.remap(img_np, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
