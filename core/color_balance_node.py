import numpy as np
import torch

class ColorBalanceNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "adjust_type": (["shadows", "midtones", "highlights"], {"default": "midtones"}),
                "cyan_red": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0}),
                "magenta_green": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0}),
                "yellow_blue": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0}),
            },
            "optional": {
                "preserve_luminosity": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_color_balance"
    CATEGORY = "Image Effects"

    def apply_color_balance(self, image, adjust_type, cyan_red, magenta_green, yellow_blue, preserve_luminosity=True):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        image_np = img_tensor.cpu().numpy()
        result = image_np.copy()
        
        # Calculer la luminance pour chaque zone
        luminance = 0.299 * result[:,:,0] + 0.587 * result[:,:,1] + 0.114 * result[:,:,2]
        
        # Définir les masques pour chaque zone
        if adjust_type == "shadows":
            mask = np.where(luminance < 0.33, 1.0 - (luminance / 0.33), 0.0)
        elif adjust_type == "highlights":
            mask = np.where(luminance > 0.67, (luminance - 0.67) / 0.33, 0.0)
        else:  # midtones
            mask = np.where((luminance >= 0.33) & (luminance <= 0.67), 
                          1.0 - np.abs(luminance - 0.5) / 0.17, 0.0)
        
        # Normaliser les ajustements
        cyan_red_norm = cyan_red / 100.0
        magenta_green_norm = magenta_green / 100.0
        yellow_blue_norm = yellow_blue / 100.0
        
        # Appliquer les ajustements couleur
        mask = np.expand_dims(mask, axis=2)
        
        # Cyan-Red
        result[:,:,0] += cyan_red_norm * mask[:,:,0]  # Rouge
        result[:,:,1] -= cyan_red_norm * 0.5 * mask[:,:,0]  # Vert
        result[:,:,2] -= cyan_red_norm * 0.5 * mask[:,:,0]  # Bleu
        
        # Magenta-Green
        result[:,:,0] += magenta_green_norm * 0.5 * mask[:,:,0]  # Rouge
        result[:,:,1] -= magenta_green_norm * mask[:,:,0]  # Vert
        result[:,:,2] += magenta_green_norm * 0.5 * mask[:,:,0]  # Bleu
        
        # Yellow-Blue
        result[:,:,0] += yellow_blue_norm * 0.5 * mask[:,:,0]  # Rouge
        result[:,:,1] += yellow_blue_norm * 0.5 * mask[:,:,0]  # Vert
        result[:,:,2] -= yellow_blue_norm * mask[:,:,0]  # Bleu
        
        # Préserver la luminosité si demandé
        if preserve_luminosity:
            original_luminance = 0.299 * image_np[:,:,0] + 0.587 * image_np[:,:,1] + 0.114 * image_np[:,:,2]
            new_luminance = 0.299 * result[:,:,0] + 0.587 * result[:,:,1] + 0.114 * result[:,:,2]
            ratio = np.where(new_luminance > 0.001, original_luminance / new_luminance, 1.0)
            ratio = np.expand_dims(ratio, axis=2)
            result = result * ratio
        
        result = np.clip(result, 0, 1)
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        return (result_tensor,)
