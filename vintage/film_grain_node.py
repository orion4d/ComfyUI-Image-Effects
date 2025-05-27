import numpy as np
import torch
import cv2

class FilmGrainNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "grain_intensity": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
                "grain_size": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.1}),
                "film_type": (["35mm", "16mm", "8mm", "super8"], {"default": "35mm"}),
            },
            "optional": {
                "color_grain": ("BOOLEAN", {"default": True}),
                "vintage_tone": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
                "vignette": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_film_grain"
    CATEGORY = "Image Effects"

    def apply_film_grain(self, image, grain_intensity, grain_size, film_type,
                        color_grain=True, vintage_tone=0.2, vignette=0.1):
        
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        result = img_np.copy().astype(np.float32)
        
        # Paramètres selon le type de film
        film_params = {
            "35mm": {"grain_scale": 1.0, "contrast": 1.1, "warmth": 0.05},
            "16mm": {"grain_scale": 1.5, "contrast": 1.2, "warmth": 0.1},
            "8mm": {"grain_scale": 2.0, "contrast": 1.3, "warmth": 0.15},
            "super8": {"grain_scale": 1.8, "contrast": 1.25, "warmth": 0.12}
        }
        
        params = film_params[film_type]
        
        # 1. Générer le grain de base
        if grain_intensity > 0:
            # Créer le grain à une résolution réduite puis l'agrandir
            grain_h = int(h / grain_size)
            grain_w = int(w / grain_size)
            
            if color_grain:
                # Grain coloré (différent pour chaque canal)
                grain_r = np.random.normal(0, grain_intensity * params["grain_scale"], (grain_h, grain_w))
                grain_g = np.random.normal(0, grain_intensity * params["grain_scale"] * 0.8, (grain_h, grain_w))
                grain_b = np.random.normal(0, grain_intensity * params["grain_scale"] * 0.9, (grain_h, grain_w))
                
                # Redimensionner le grain
                grain_r = cv2.resize(grain_r, (w, h), interpolation=cv2.INTER_LINEAR)
                grain_g = cv2.resize(grain_g, (w, h), interpolation=cv2.INTER_LINEAR)
                grain_b = cv2.resize(grain_b, (w, h), interpolation=cv2.INTER_LINEAR)
                
                grain = np.stack([grain_r, grain_g, grain_b], axis=2) * 30
            else:
                # Grain monochrome
                grain_mono = np.random.normal(0, grain_intensity * params["grain_scale"], (grain_h, grain_w))
                grain_mono = cv2.resize(grain_mono, (w, h), interpolation=cv2.INTER_LINEAR)
                grain = np.stack([grain_mono] * 3, axis=2) * 25
            
            # Appliquer le grain
            result = result + grain
        
        # 2. Ajustement du contraste selon le type de film
        if params["contrast"] != 1.0:
            result = np.clip((result - 127.5) * params["contrast"] + 127.5, 0, 255)
        
        # 3. Tonalité vintage
        if vintage_tone > 0:
            # Courbe de tonalité vintage (légèrement sépia)
            sepia_matrix = np.array([
                [1 - vintage_tone * 0.3, vintage_tone * 0.2, vintage_tone * 0.1],
                [vintage_tone * 0.1, 1 - vintage_tone * 0.1, vintage_tone * 0.1],
                [vintage_tone * 0.05, vintage_tone * 0.1, 1 - vintage_tone * 0.2]
            ])
            
            result = result @ sepia_matrix.T
            
            # Ajouter de la chaleur
            warmth = params["warmth"] * vintage_tone
            result[:, :, 0] *= (1 + warmth)  # Plus de rouge
            result[:, :, 2] *= (1 - warmth * 0.5)  # Moins de bleu
        
        # 4. Vignette
        if vignette > 0:
            center_x, center_y = w // 2, h // 2
            max_dist = np.sqrt(center_x**2 + center_y**2)
            
            y, x = np.ogrid[:h, :w]
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            vignette_mask = 1 - (distance / max_dist) * vignette
            vignette_mask = np.clip(vignette_mask, 0, 1)
            
            result = result * np.expand_dims(vignette_mask, axis=2)
        
        # Normalisation finale
        result = np.clip(result, 0, 255)
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
