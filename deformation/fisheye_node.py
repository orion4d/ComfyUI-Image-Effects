import numpy as np
import torch
import cv2

class FisheyeNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "fov": ("FLOAT", {"default": 180.0, "min": 30.0, "max": 360.0, "step": 1.0}),
                "mapping": (["equidistant", "equisolid", "orthographic", "stereographic"], {"default": "equidistant"}),
                "format": (["fullframe", "circular"], {"default": "fullframe"}),
            },
            "optional": {
                "center_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "center_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_fisheye"
    CATEGORY = "Image Effects"

    def apply_fisheye(self, image, fov, mapping, format, center_x=0.5, center_y=0.5, strength=1.0):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        
        # Centre de l'effet
        cx = int(w * center_x)
        cy = int(h * center_y)
        
        # Rayon maximum
        max_radius = min(w, h) // 2
        
        # Créer les grilles de coordonnées
        result = self._apply_fisheye_distortion(img_np, cx, cy, max_radius, fov, mapping, format, strength)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
    
    def _apply_fisheye_distortion(self, image, cx, cy, max_radius, fov, mapping, format, strength):
        h, w = image.shape[:2]
        
        # Créer les grilles de coordonnées
        map_x = np.zeros((h, w), dtype=np.float32)
        map_y = np.zeros((h, w), dtype=np.float32)
        
        fov_rad = np.radians(fov)
        
        for y in range(h):
            for x in range(w):
                # Distance du centre
                dx = x - cx
                dy = y - cy
                r = np.sqrt(dx*dx + dy*dy)
                
                if r == 0:
                    map_x[y, x] = x
                    map_y[y, x] = y
                    continue
                
                # Angle
                theta = np.arctan2(dy, dx)
                
                # Normaliser le rayon
                r_norm = r / max_radius
                
                if format == "circular" and r_norm > 1.0:
                    map_x[y, x] = x
                    map_y[y, x] = y
                    continue
                
                # Appliquer la projection selon le mapping
                if mapping == "equidistant":
                    r_fish = r_norm * fov_rad / (2 * np.pi) * max_radius
                elif mapping == "equisolid":
                    r_fish = 2 * max_radius * np.sin(r_norm * fov_rad / 4)
                elif mapping == "orthographic":
                    r_fish = max_radius * np.sin(r_norm * fov_rad / 2)
                elif mapping == "stereographic":
                    r_fish = 2 * max_radius * np.tan(r_norm * fov_rad / 4)
                
                # Appliquer la force
                r_fish *= strength
                
                # Nouvelles coordonnées
                new_x = cx + r_fish * np.cos(theta)
                new_y = cy + r_fish * np.sin(theta)
                
                map_x[y, x] = np.clip(new_x, 0, w - 1)
                map_y[y, x] = np.clip(new_y, 0, h - 1)
        
        # Appliquer la transformation
        result = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return result
