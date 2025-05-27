import numpy as np
import torch
import cv2

class LevelsNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "input_black": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "input_white": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "gamma": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.01}),
                "output_black": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "output_white": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
            "optional": {
                "channel": (["RGB", "Red", "Green", "Blue"], {"default": "RGB"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_levels"
    CATEGORY = "Image Effects"

    def apply_levels(self, image, input_black, input_white, gamma, output_black, output_white, channel="RGB"):
        # Prendre la première image du batch
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        # Convertir en numpy
        image_np = img_tensor.cpu().numpy()
        h, w, c = image_np.shape
        
        # Copier l'image pour éviter de modifier l'original
        result = image_np.copy()
        
        # Déterminer quels canaux traiter
        if channel == "RGB":
            channels_to_process = [0, 1, 2]
        elif channel == "Red":
            channels_to_process = [0]
        elif channel == "Green":
            channels_to_process = [1]
        elif channel == "Blue":
            channels_to_process = [2]
        
        # Appliquer les niveaux sur chaque canal sélectionné
        for ch in channels_to_process:
            channel_data = result[:, :, ch]
            
            # Étape 1: Ajuster les niveaux d'entrée
            # Normaliser entre input_black et input_white
            if input_white > input_black:
                channel_data = np.clip((channel_data - input_black) / (input_white - input_black), 0, 1)
            
            # Étape 2: Appliquer la correction gamma
            if gamma != 1.0:
                channel_data = np.power(channel_data, 1.0 / gamma)
            
            # Étape 3: Ajuster les niveaux de sortie
            channel_data = channel_data * (output_white - output_black) + output_black
            
            # Clipper les valeurs
            channel_data = np.clip(channel_data, 0, 1)
            
            result[:, :, ch] = channel_data
        
        # Reconvertir en tensor
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        
        return (result_tensor,)
