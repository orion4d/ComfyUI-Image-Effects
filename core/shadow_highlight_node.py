import numpy as np
import torch

class ShadowHighlightNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "shadow_amount": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0}),
                "highlight_amount": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0}),
                "shadow_width": ("FLOAT", {"default": 50.0, "min": 0.0, "max": 100.0, "step": 1.0}),
                "highlight_width": ("FLOAT", {"default": 50.0, "min": 0.0, "max": 100.0, "step": 1.0}),
                "radius": ("FLOAT", {"default": 30.0, "min": 0.0, "max": 100.0, "step": 1.0}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_shadow_highlight"
    CATEGORY = "Image Effects"

    def apply_shadow_highlight(self, image, shadow_amount, highlight_amount, shadow_width, highlight_width, radius):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        image_np = img_tensor.cpu().numpy()
        result = image_np.copy()
        
        # Calculer la luminance
        luminance = 0.299 * result[:,:,0] + 0.587 * result[:,:,1] + 0.114 * result[:,:,2]
        
        # Créer les masques pour ombres et hautes lumières
        shadow_threshold = shadow_width / 100.0
        highlight_threshold = 1.0 - (highlight_width / 100.0)
        
        # Masque des ombres (transition douce)
        shadow_mask = np.where(luminance < shadow_threshold,
                              1.0 - (luminance / shadow_threshold),
                              0.0)
        
        # Masque des hautes lumières (transition douce)
        highlight_mask = np.where(luminance > highlight_threshold,
                                 (luminance - highlight_threshold) / (1.0 - highlight_threshold),
                                 0.0)
        
        # Appliquer un flou gaussien pour adoucir les transitions
        if radius > 0:
            import cv2
            kernel_size = int(radius / 10) * 2 + 1
            shadow_mask = cv2.GaussianBlur(shadow_mask, (kernel_size, kernel_size), radius/30)
            highlight_mask = cv2.GaussianBlur(highlight_mask, (kernel_size, kernel_size), radius/30)
        
        # Appliquer les corrections
        shadow_factor = 1.0 + (shadow_amount / 100.0)
        highlight_factor = 1.0 + (highlight_amount / 100.0)
        
        # Correction des ombres
        if shadow_amount != 0:
            shadow_mask_3d = np.expand_dims(shadow_mask, axis=2)
            shadow_correction = result * shadow_factor
            result = result * (1 - shadow_mask_3d) + shadow_correction * shadow_mask_3d
        
        # Correction des hautes lumières
        if highlight_amount != 0:
            highlight_mask_3d = np.expand_dims(highlight_mask, axis=2)
            highlight_correction = result * highlight_factor
            result = result * (1 - highlight_mask_3d) + highlight_correction * highlight_mask_3d
        
        result = np.clip(result, 0, 1)
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        return (result_tensor,)
