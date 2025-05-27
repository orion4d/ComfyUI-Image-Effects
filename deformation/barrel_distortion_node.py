import numpy as np
import torch
import cv2

class BarrelDistortionNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "k1": ("FLOAT", {"default": 0.2, "min": -1.0, "max": 1.0, "step": 0.01}),
                "k2": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01}),
                "k3": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01}),
            },
            "optional": {
                "center_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "center_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "scale": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_barrel_distortion"
    CATEGORY = "Image Effects"

    def apply_barrel_distortion(self, image, k1, k2, k3, center_x=0.5, center_y=0.5, scale=1.0):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        
        # Centre de distorsion
        cx = w * center_x
        cy = h * center_y
        
        # Créer les grilles de coordonnées
        map_x = np.zeros((h, w), dtype=np.float32)
        map_y = np.zeros((h, w), dtype=np.float32)
        
        # Normalisation
        max_radius = max(w, h) / 2
        
        for y in range(h):
            for x in range(w):
                # Coordonnées normalisées par rapport au centre
                xu = (x - cx) / max_radius
                yu = (y - cy) / max_radius
                
                # Distance radiale
                r2 = xu*xu + yu*yu
                r4 = r2*r2
                r6 = r4*r2
                
                # Facteur de distorsion
                distortion = 1 + k1*r2 + k2*r4 + k3*r6
                
                # Nouvelles coordonnées
                xd = xu * distortion * scale
                yd = yu * distortion * scale
                
                # Reconvertir en coordonnées image
                map_x[y, x] = xd * max_radius + cx
                map_y[y, x] = yd * max_radius + cy
        
        # Appliquer la transformation
        result = cv2.remap(img_np, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
