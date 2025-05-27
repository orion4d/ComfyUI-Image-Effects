import numpy as np
import torch
import cv2

class GodRaysNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "intensity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 2.0, "step": 0.1}),
                "num_rays": ("INT", {"default": 8, "min": 3, "max": 20, "step": 1}),
                "ray_length": ("FLOAT", {"default": 0.8, "min": 0.1, "max": 2.0, "step": 0.1}),
            },
            "optional": {
                "source_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "source_y": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
                "color_temp": ("FLOAT", {"default": 3000.0, "min": 2000.0, "max": 8000.0, "step": 100.0}),
                "decay": ("FLOAT", {"default": 0.8, "min": 0.1, "max": 1.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_god_rays"
    CATEGORY = "Image Effects"

    def apply_god_rays(self, image, intensity, num_rays, ray_length,
                      source_x=0.5, source_y=0.2, color_temp=3000.0, decay=0.8):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        result = img_np.copy().astype(np.float32)
        
        # Source des rayons
        source_x_px = int(w * source_x)
        source_y_px = int(h * source_y)
        
        # Couleur des rayons
        ray_color = self._temp_to_rgb(color_temp)
        
        # Créer les rayons divins
        rays_overlay = self._create_god_rays(h, w, source_x_px, source_y_px, 
                                           num_rays, ray_length, ray_color, intensity, decay)
        
        # Fusionner avec l'image
        result = np.clip(result + rays_overlay, 0, 255)
        
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
        
        return (np.clip(red, 0, 255), np.clip(green, 0, 255), np.clip(blue, 0, 255))
    
    def _create_god_rays(self, h, w, source_x, source_y, num_rays, ray_length, color, intensity, decay):
        """Créer les rayons divins"""
        overlay = np.zeros((h, w, 3), dtype=np.float32)
        
        # Longueur maximale des rayons
        max_length = int(min(w, h) * ray_length)
        
        for i in range(num_rays):
            # Angle du rayon avec variation aléatoire
            base_angle = (2 * np.pi * i) / num_rays
            angle_variation = np.random.uniform(-0.3, 0.3)
            angle = base_angle + angle_variation
            
            # Créer un rayon individuel
            ray_overlay = self._create_single_ray(h, w, source_x, source_y, 
                                                angle, max_length, color, decay)
            overlay += ray_overlay
        
        # Normaliser et appliquer l'intensité
        overlay = np.clip(overlay, 0, 255) * intensity
        
        return overlay
    
    def _create_single_ray(self, h, w, start_x, start_y, angle, length, color, decay):
        """Créer un rayon individuel"""
        ray_overlay = np.zeros((h, w, 3), dtype=np.float32)
        
        # Calculer les points du rayon
        end_x = int(start_x + length * np.cos(angle))
        end_y = int(start_y + length * np.sin(angle))
        
        # Largeur variable du rayon
        num_segments = 50
        for i in range(num_segments):
            t = i / num_segments
            
            # Position le long du rayon
            x = int(start_x + t * (end_x - start_x))
            y = int(start_y + t * (end_y - start_y))
            
            # Largeur qui diminue avec la distance
            width = max(1, int(10 * (1 - t * decay)))
            
            # Intensité qui diminue avec la distance
            alpha = (1 - t) * decay
            
            # Dessiner un segment du rayon
            if 0 <= x < w and 0 <= y < h:
                cv2.circle(ray_overlay, (x, y), width, 
                          (color[0] * alpha, color[1] * alpha, color[2] * alpha), -1)
        
        # Flou gaussien pour adoucir
        ray_overlay = cv2.GaussianBlur(ray_overlay, (21, 21), 0)
        
        return ray_overlay
