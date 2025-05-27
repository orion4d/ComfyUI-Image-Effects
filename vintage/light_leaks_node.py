import numpy as np
import torch
import cv2

class LightLeaksNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "leak_intensity": ("FLOAT", {"default": 0.4, "min": 0.0, "max": 1.0, "step": 0.01}),
                "leak_color": (["warm", "cool", "rainbow", "vintage", "custom"], {"default": "warm"}),
                "leak_count": ("INT", {"default": 2, "min": 1, "max": 5, "step": 1}),
            },
            "optional": {
                "leak_position": (["random", "corners", "edges", "center"], {"default": "random"}),
                "blur_amount": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "custom_hue": ("FLOAT", {"default": 30.0, "min": 0.0, "max": 360.0, "step": 1.0}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_light_leaks"
    CATEGORY = "Image Effects"

    def apply_light_leaks(self, image, leak_intensity, leak_color, leak_count,
                         leak_position="random", blur_amount=0.5, custom_hue=30.0):
        
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        result = img_np.copy().astype(np.float32)
        
        # Couleurs prédéfinies pour les fuites de lumière
        color_palettes = {
            "warm": [(255, 200, 100), (255, 150, 80), (255, 180, 120)],
            "cool": [(100, 150, 255), (120, 200, 255), (80, 180, 255)],
            "rainbow": [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)],
            "vintage": [(255, 220, 180), (255, 200, 150), (240, 180, 120)],
            "custom": [(255, 200, 100)]  # Sera modifié selon custom_hue
        }
        
        if leak_color == "custom":
            # Convertir la teinte personnalisée en RGB
            hsv_color = np.array([[[custom_hue / 2, 255, 255]]], dtype=np.uint8)
            rgb_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2RGB)[0, 0]
            color_palettes["custom"] = [tuple(rgb_color)]
        
        colors = color_palettes[leak_color]
        
        # Générer les fuites de lumière
        for i in range(leak_count):
            # Choisir une couleur
            color = colors[i % len(colors)]
            
            # Déterminer la position
            if leak_position == "corners":
                positions = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]
                pos_x, pos_y = positions[i % 4]
            elif leak_position == "edges":
                edge = i % 4
                if edge == 0:  # Top
                    pos_x, pos_y = np.random.randint(0, w), 0
                elif edge == 1:  # Right
                    pos_x, pos_y = w-1, np.random.randint(0, h)
                elif edge == 2:  # Bottom
                    pos_x, pos_y = np.random.randint(0, w), h-1
                else:  # Left
                    pos_x, pos_y = 0, np.random.randint(0, h)
            elif leak_position == "center":
                pos_x = w // 2 + np.random.randint(-w//4, w//4)
                pos_y = h // 2 + np.random.randint(-h//4, h//4)
            else:  # random
                pos_x = np.random.randint(0, w)
                pos_y = np.random.randint(0, h)
            
            # Créer le masque de fuite
            leak_mask = self._create_leak_mask(h, w, pos_x, pos_y, leak_intensity)
            
            # Appliquer le flou au masque
            if blur_amount > 0:
                blur_size = int(blur_amount * 50) * 2 + 1
                leak_mask = cv2.GaussianBlur(leak_mask, (blur_size, blur_size), 0)
            
            # Appliquer la couleur
            for ch in range(3):
                color_layer = leak_mask * color[ch] * leak_intensity
                result[:, :, ch] = np.clip(result[:, :, ch] + color_layer, 0, 255)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
    
    def _create_leak_mask(self, h, w, center_x, center_y, intensity):
        """Créer un masque de fuite de lumière organique"""
        # Créer un dégradé radial de base
        y, x = np.ogrid[:h, :w]
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(w**2 + h**2) / 2
        
        # Masque radial de base
        mask = 1 - (distance / max_distance)
        mask = np.clip(mask, 0, 1)
        
        # Ajouter de la variation organique avec du bruit
        noise = np.random.random((h, w)) * 0.3
        mask = mask * (0.7 + noise)
        
        # Appliquer une courbe non-linéaire pour un effet plus naturel
        mask = np.power(mask, 2) * intensity
        
        return np.clip(mask, 0, 1)
