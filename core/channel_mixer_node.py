import numpy as np
import torch

class ChannelMixerNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "output_channel": (["Red", "Green", "Blue"], {"default": "Red"}),
                "red_source": ("FLOAT", {"default": 100.0, "min": -200.0, "max": 200.0, "step": 1.0}),
                "green_source": ("FLOAT", {"default": 0.0, "min": -200.0, "max": 200.0, "step": 1.0}),
                "blue_source": ("FLOAT", {"default": 0.0, "min": -200.0, "max": 200.0, "step": 1.0}),
                "constant": ("FLOAT", {"default": 0.0, "min": -200.0, "max": 200.0, "step": 1.0}),
            },
            "optional": {
                "monochrome": ("BOOLEAN", {"default": False}),
                "preserve_luminosity": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_channel_mixer"
    CATEGORY = "Image Effects"

    def apply_channel_mixer(self, image, output_channel, red_source, green_source, blue_source, constant, monochrome=False, preserve_luminosity=False):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        image_np = img_tensor.cpu().numpy()
        result = image_np.copy()
        
        # Normaliser les valeurs sources
        red_factor = red_source / 100.0
        green_factor = green_source / 100.0
        blue_factor = blue_source / 100.0
        constant_factor = constant / 100.0
        
        # Sauvegarder la luminance originale si nécessaire
        if preserve_luminosity:
            original_luminance = 0.299 * result[:,:,0] + 0.587 * result[:,:,1] + 0.114 * result[:,:,2]
        
        if monochrome:
            # Mode monochrome : appliquer le mélange à tous les canaux
            mixed_channel = (result[:,:,0] * red_factor + 
                           result[:,:,1] * green_factor + 
                           result[:,:,2] * blue_factor + 
                           constant_factor)
            mixed_channel = np.clip(mixed_channel, 0, 1)
            
            result[:,:,0] = mixed_channel
            result[:,:,1] = mixed_channel
            result[:,:,2] = mixed_channel
        else:
            # Mode couleur : mélanger seulement le canal sélectionné
            mixed_channel = (result[:,:,0] * red_factor + 
                           result[:,:,1] * green_factor + 
                           result[:,:,2] * blue_factor + 
                           constant_factor)
            mixed_channel = np.clip(mixed_channel, 0, 1)
            
            if output_channel == "Red":
                result[:,:,0] = mixed_channel
            elif output_channel == "Green":
                result[:,:,1] = mixed_channel
            elif output_channel == "Blue":
                result[:,:,2] = mixed_channel
        
        # Restaurer la luminance si demandé
        if preserve_luminosity and not monochrome:
            new_luminance = 0.299 * result[:,:,0] + 0.587 * result[:,:,1] + 0.114 * result[:,:,2]
            ratio = np.where(new_luminance > 0.001, original_luminance / new_luminance, 1.0)
            ratio = np.expand_dims(ratio, axis=2)
            result = result * ratio
        
        result = np.clip(result, 0, 1)
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        return (result_tensor,)
