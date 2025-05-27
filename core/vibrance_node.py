import numpy as np
import torch
import cv2

class VibranceNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "vibrance": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0}),
                "saturation": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0}),
            },
            "optional": {
                "protect_skin_tones": ("BOOLEAN", {"default": True}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_vibrance"
    CATEGORY = "Image Effects"

    def apply_vibrance(self, image, vibrance, saturation, protect_skin_tones=True, strength=1.0):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        image_np = img_tensor.cpu().numpy()
        result = image_np.copy()
        
        # Convertir en HSV pour les calculs de saturation
        hsv = cv2.cvtColor((result * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:,:,1] /= 255.0  # Normaliser la saturation
        hsv[:,:,2] /= 255.0  # Normaliser la valeur
        
        # Calculer la saturation actuelle
        current_saturation = hsv[:,:,1]
        
        # Appliquer la vibrance (effet sélectif)
        if vibrance != 0:
            vibrance_factor = vibrance / 100.0
            # La vibrance affecte moins les couleurs déjà saturées
            vibrance_mask = 1.0 - current_saturation
            vibrance_adjustment = vibrance_factor * vibrance_mask * strength
            hsv[:,:,1] = np.clip(current_saturation + vibrance_adjustment, 0, 1)
        
        # Appliquer la saturation globale
        if saturation != 0:
            saturation_factor = 1.0 + (saturation / 100.0) * strength
            hsv[:,:,1] = np.clip(hsv[:,:,1] * saturation_factor, 0, 1)
        
        # Protection des tons chair
        if protect_skin_tones:
            # Détecter les tons chair (teinte entre 0-30 et 330-360 degrés)
            hue = hsv[:,:,0] * 2  # Convertir en degrés (0-360)
            skin_mask = ((hue >= 0) & (hue <= 30)) | ((hue >= 330) & (hue <= 360))
            skin_protection = np.where(skin_mask, 0.5, 1.0)
            skin_protection = np.expand_dims(skin_protection, axis=2)
            
            # Réduire l'effet sur les tons chair
            protected_result = image_np * (1 - skin_protection) + result * skin_protection
            result = protected_result
        
        # Reconvertir en RGB
        hsv[:,:,1] *= 255
        hsv[:,:,2] *= 255
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32) / 255.0
        
        result = np.clip(result, 0, 1)
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        return (result_tensor,)
