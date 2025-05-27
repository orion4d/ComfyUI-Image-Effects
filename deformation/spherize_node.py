import numpy as np
import torch
import cv2

class SpherizeNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "strength": ("FLOAT", {"default": 0.5, "min": -2.0, "max": 2.0, "step": 0.1}),
                "radius": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.1}),
            },
            "optional": {
                "center_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "center_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "mode": (["spherize", "cylindrical"], {"default": "spherize"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_spherize"
    CATEGORY = "Image Effects"

    def apply_spherize(self, image, strength, radius, center_x=0.5, center_y=0.5, mode="spherize"):
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
        max_radius = min(w, h) / 2 * radius
        
        # Créer les grilles de coordonnées
        map_x = np.zeros((h, w), dtype=np.float32)
        map_y = np.zeros((h, w), dtype=np.float32)
        
        for y in range(h):
            for x in range(w):
                # Distance du centre
                dx = x - cx
                dy = y - cy
                distance = np.sqrt(dx*dx + dy*dy)
                
                if distance == 0 or distance > max_radius:
                    map_x[y, x] = x
                    map_y[y, x] = y
                    continue
                
                # Normaliser la distance
                norm_distance = distance / max_radius
                
                if mode == "spherize":
                    # Effet sphère
                    if strength > 0:
                        # Convexe (vers l'extérieur)
                        factor = np.power(norm_distance, strength)
                    else:
                        # Concave (vers l'intérieur)
                        factor = 1 - np.power(1 - norm_distance, -strength)
                else:
                    # Effet cylindrique (seulement horizontal ou vertical)
                    if abs(dx) > abs(dy):
                        # Déformation horizontale
                        factor = np.power(abs(dx) / max_radius, strength) if strength > 0 else 1 - np.power(1 - abs(dx) / max_radius, -strength)
                        factor = factor if dx >= 0 else -factor
                        map_x[y, x] = cx + factor * max_radius
                        map_y[y, x] = y
                        continue
                    else:
                        # Déformation verticale
                        factor = np.power(abs(dy) / max_radius, strength) if strength > 0 else 1 - np.power(1 - abs(dy) / max_radius, -strength)
                        factor = factor if dy >= 0 else -factor
                        map_x[y, x] = x
                        map_y[y, x] = cy + factor * max_radius
                        continue
                
                # Nouvelles coordonnées
                new_distance = factor * max_radius
                angle = np.arctan2(dy, dx)
                
                new_x = cx + new_distance * np.cos(angle)
                new_y = cy + new_distance * np.sin(angle)
                
                map_x[y, x] = np.clip(new_x, 0, w - 1)
                map_y[y, x] = np.clip(new_y, 0, h - 1)
        
        # Appliquer la transformation
        result = cv2.remap(img_np, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
