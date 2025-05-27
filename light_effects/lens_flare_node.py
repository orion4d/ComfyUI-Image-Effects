import numpy as np
import torch
import cv2

class LensFlareNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "flare_type": (["classic", "anamorphic", "starburst", "hexagonal"], {"default": "classic"}),
                "intensity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 2.0, "step": 0.1}),
                "size": ("FLOAT", {"default": 0.3, "min": 0.1, "max": 1.0, "step": 0.05}),
            },
            "optional": {
                "position_x": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
                "position_y": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
                "color_temp": ("FLOAT", {"default": 5500.0, "min": 2000.0, "max": 10000.0, "step": 100.0}),
                "rays": ("INT", {"default": 6, "min": 4, "max": 12, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_lens_flare"
    CATEGORY = "Image Effects"

    def apply_lens_flare(self, image, flare_type, intensity, size, 
                        position_x=0.7, position_y=0.3, color_temp=5500.0, rays=6):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        result = img_np.copy().astype(np.float32)
        
        # Position du flare
        flare_x = int(w * position_x)
        flare_y = int(h * position_y)
        
        # Couleur basée sur la température
        flare_color = self._temp_to_rgb(color_temp)
        
        # Créer le flare selon le type
        if flare_type == "classic":
            flare_overlay = self._create_classic_flare(h, w, flare_x, flare_y, size, flare_color, intensity)
        elif flare_type == "anamorphic":
            flare_overlay = self._create_anamorphic_flare(h, w, flare_x, flare_y, size, flare_color, intensity)
        elif flare_type == "starburst":
            flare_overlay = self._create_starburst_flare(h, w, flare_x, flare_y, size, flare_color, intensity, rays)
        elif flare_type == "hexagonal":
            flare_overlay = self._create_hexagonal_flare(h, w, flare_x, flare_y, size, flare_color, intensity)
        
        # Fusionner avec l'image
        result = np.clip(result + flare_overlay, 0, 255)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
    
    def _temp_to_rgb(self, temp):
        """Convertir température de couleur en RGB"""
        temp = temp / 100
        
        if temp <= 66:
            red = 255
            green = temp
            green = 99.4708025861 * np.log(green) - 161.1195681661
            if temp >= 19:
                blue = temp - 10
                blue = 138.5177312231 * np.log(blue) - 305.0447927307
            else:
                blue = 0
        else:
            red = temp - 60
            red = 329.698727446 * np.power(red, -0.1332047592)
            green = temp - 60
            green = 288.1221695283 * np.power(green, -0.0755148492)
            blue = 255
        
        return tuple([int(np.clip(red, 0, 255)), int(np.clip(green, 0, 255)), int(np.clip(blue, 0, 255))])
    
    def _create_classic_flare(self, h, w, cx, cy, size, color, intensity):
        """Créer un flare classique avec cercles concentriques"""
        overlay = np.zeros((h, w, 3), dtype=np.float32)
        color_tuple = tuple([int(c) for c in color])
        radius = int(min(w, h) * size * 0.3)
        cv2.circle(overlay, (cx, cy), radius, color_tuple, -1)
        for i in range(3):
            r = radius // (i + 2)
            alpha = 0.3 / (i + 1)
            circle_overlay = np.zeros_like(overlay)
            cv2.circle(circle_overlay, (cx, cy), r, color_tuple, -1)
            overlay += circle_overlay * alpha
        overlay = cv2.GaussianBlur(overlay, (51, 51), 0)
        return overlay * intensity
    
    def _create_anamorphic_flare(self, h, w, cx, cy, size, color, intensity):
        """Créer un flare anamorphique (lignes horizontales)"""
        overlay = np.zeros((h, w, 3), dtype=np.float32)
        color_tuple = tuple([int(c) for c in color])
        line_height = int(h * size * 0.1)
        line_width = int(w * size)
        y1 = max(0, cy - line_height // 2)
        y2 = min(h, cy + line_height // 2)
        x1 = max(0, cx - line_width // 2)
        x2 = min(w, cx + line_width // 2)
        overlay[y1:y2, x1:x2] = color_tuple
        radius = int(min(w, h) * size * 0.1)
        cv2.circle(overlay, (cx, cy), radius, color_tuple, -1)
        kernel = np.ones((1, 21)) / 21
        for i in range(3):
            overlay[:, :, i] = cv2.filter2D(overlay[:, :, i], -1, kernel)
        return overlay * intensity
    
    def _create_starburst_flare(self, h, w, cx, cy, size, color, intensity, rays):
        """Créer un flare en étoile"""
        overlay = np.zeros((h, w, 3), dtype=np.float32)
        color_tuple = tuple([int(c) for c in color])
        ray_length = int(min(w, h) * size)
        for i in range(rays):
            angle = (2 * np.pi * i) / rays
            x1 = cx
            y1 = cy
            x2 = int(cx + ray_length * np.cos(angle))
            y2 = int(cy + ray_length * np.sin(angle))
            cv2.line(overlay, (x1, y1), (x2, y2), color_tuple, 3)
        radius = int(min(w, h) * size * 0.05)
        cv2.circle(overlay, (cx, cy), radius, color_tuple, -1)
        overlay = cv2.GaussianBlur(overlay, (31, 31), 0)
        return overlay * intensity
    
    def _create_hexagonal_flare(self, h, w, cx, cy, size, color, intensity):
        """Créer un flare hexagonal"""
        overlay = np.zeros((h, w, 3), dtype=np.float32)
        color_tuple = tuple([int(c) for c in color])
        radius = int(min(w, h) * size * 0.2)
        points = []
        for i in range(6):
            angle = (2 * np.pi * i) / 6
            x = int(cx + radius * np.cos(angle))
            y = int(cy + radius * np.sin(angle))
            points.append([x, y])
        points = np.array(points, dtype=np.int32)
        cv2.fillPoly(overlay, [points], color_tuple)
        for i in range(1, 4):
            r = radius // (i + 1)
            hex_points = []
            for j in range(6):
                angle = (2 * np.pi * j) / 6
                x = int(cx + r * np.cos(angle))
                y = int(cy + r * np.sin(angle))
                hex_points.append([x, y])
            hex_points = np.array(hex_points, dtype=np.int32)
            hex_overlay = np.zeros_like(overlay)
            cv2.fillPoly(hex_overlay, [hex_points], color_tuple)
            overlay += hex_overlay * (0.5 / i)
        overlay = cv2.GaussianBlur(overlay, (41, 41), 0)
        return overlay * intensity
