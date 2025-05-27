import numpy as np
import torch
import cv2

class VintageTVNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "tv_type": (["crt_color", "crt_bw", "old_tv", "security_monitor"], {"default": "crt_color"}),
                "scan_lines": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "curvature": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
            "optional": {
                "static_noise": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01}),
                "phosphor_glow": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
                "brightness": ("FLOAT", {"default": 0.9, "min": 0.5, "max": 1.5, "step": 0.01}),
                "contrast": ("FLOAT", {"default": 1.1, "min": 0.5, "max": 2.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_vintage_tv"
    CATEGORY = "Image Effects"

    def apply_vintage_tv(self, image, tv_type, scan_lines, curvature,
                        static_noise=0.1, phosphor_glow=0.2, brightness=0.9, contrast=1.1):
        
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        result = img_np.copy().astype(np.float32)
        
        # 1. Appliquer la courbure de l'écran CRT
        if curvature > 0:
            result = self._apply_crt_curvature(result, curvature)
        
        # 2. Ajustements selon le type de TV
        if tv_type == "crt_bw":
            # Convertir en noir et blanc avec une légère teinte verte
            gray = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_RGB2GRAY)
            result = np.stack([gray * 0.9, gray, gray * 0.9], axis=2).astype(np.float32)
        elif tv_type == "security_monitor":
            # Effet moniteur de sécurité (vert monochrome)
            gray = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_RGB2GRAY)
            result = np.stack([gray * 0.3, gray, gray * 0.3], axis=2).astype(np.float32)
        elif tv_type == "old_tv":
            # TV ancienne avec saturation réduite
            hsv = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] *= 0.7  # Réduire la saturation
            result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
        
        # 3. Lignes de balayage
        if scan_lines > 0:
            for i in range(0, h, 2):
                result[i] *= (1 - scan_lines * 0.3)
            
            # Ajouter des lignes horizontales plus prononcées
            for i in range(0, h, 4):
                if i < h:
                    result[i] *= (1 - scan_lines * 0.5)
        
        # 4. Bruit statique
        if static_noise > 0:
            noise = np.random.random((h, w, c)) * static_noise * 100
            salt_pepper = np.random.random((h, w, c)) < static_noise * 0.01
            result[salt_pepper] = np.random.choice([0, 255], size=np.sum(salt_pepper))
            result = np.clip(result + noise - static_noise * 50, 0, 255)
        
        # 5. Lueur phosphore
        if phosphor_glow > 0:
            # Créer un effet de lueur en dupliquant et floutant l'image
            glow = cv2.GaussianBlur(result.astype(np.uint8), (15, 15), 0).astype(np.float32)
            result = result * (1 - phosphor_glow * 0.3) + glow * phosphor_glow * 0.3
        
        # 6. Ajustements de luminosité et contraste
        result = np.clip((result - 127.5) * contrast + 127.5, 0, 255)
        result = np.clip(result * brightness, 0, 255)
        
        # 7. Vignette CRT
        center_x, center_y = w // 2, h // 2
        max_dist = np.sqrt(center_x**2 + center_y**2)
        y, x = np.ogrid[:h, :w]
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        vignette = 1 - (distance / max_dist) * 0.3
        vignette = np.clip(vignette, 0.7, 1)
        result = result * np.expand_dims(vignette, axis=2)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
    
    def _apply_crt_curvature(self, image, strength):
        """Appliquer la courbure caractéristique des écrans CRT"""
        h, w = image.shape[:2]
        
        # Créer la grille de déformation
        map_x = np.zeros((h, w), dtype=np.float32)
        map_y = np.zeros((h, w), dtype=np.float32)
        
        center_x, center_y = w / 2, h / 2
        
        for y in range(h):
            for x in range(w):
                # Normaliser les coordonnées
                norm_x = (x - center_x) / center_x
                norm_y = (y - center_y) / center_y
                
                # Appliquer la déformation barrel
                r2 = norm_x * norm_x + norm_y * norm_y
                distortion = 1 + strength * 0.1 * r2
                
                new_x = center_x + norm_x * center_x * distortion
                new_y = center_y + norm_y * center_y * distortion
                
                map_x[y, x] = np.clip(new_x, 0, w - 1)
                map_y[y, x] = np.clip(new_y, 0, h - 1)
        
        # Appliquer la déformation
        result = cv2.remap(image.astype(np.uint8), map_x, map_y, cv2.INTER_LINEAR)
        return result.astype(np.float32)
