import numpy as np
import torch
import cv2

class RippleNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "amplitude": ("FLOAT", {"default": 20.0, "min": 0.0, "max": 100.0, "step": 1.0}),
                "frequency": ("FLOAT", {"default": 0.02, "min": 0.001, "max": 0.1, "step": 0.001}),
                "wave_type": (["sine", "cosine", "both"], {"default": "sine"}),
            },
            "optional": {
                "center_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "center_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "phase": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 6.28, "step": 0.1}),
                "decay": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_ripple"
    CATEGORY = "Image Effects"

    def apply_ripple(self, image, amplitude, frequency, wave_type, 
                    center_x=0.5, center_y=0.5, phase=0.0, decay=0.0):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        
        # Centre des ondulations
        cx = w * center_x
        cy = h * center_y
        
        # Créer les grilles de coordonnées
        map_x = np.zeros((h, w), dtype=np.float32)
        map_y = np.zeros((h, w), dtype=np.float32)
        
        for y in range(h):
            for x in range(w):
                # Distance du centre
                dx = x - cx
                dy = y - cy
                distance = np.sqrt(dx*dx + dy*dy)
                
                # Facteur de décroissance
                decay_factor = 1.0
                if decay > 0:
                    max_dist = np.sqrt(w*w + h*h) / 2
                    decay_factor = np.exp(-decay * distance / max_dist)
                
                # Calcul de l'ondulation
                if wave_type == "sine":
                    ripple = np.sin(distance * frequency + phase)
                elif wave_type == "cosine":
                    ripple = np.cos(distance * frequency + phase)
                else:  # both
                    ripple = (np.sin(distance * frequency + phase) + np.cos(distance * frequency + phase)) / 2
                
                # Amplitude avec décroissance
                effective_amplitude = amplitude * decay_factor * ripple
                
                # Direction de l'ondulation (radiale)
                if distance > 0:
                    angle = np.arctan2(dy, dx)
                    offset_x = effective_amplitude * np.cos(angle)
                    offset_y = effective_amplitude * np.sin(angle)
                else:
                    offset_x = offset_y = 0
                
                map_x[y, x] = np.clip(x + offset_x, 0, w - 1)
                map_y[y, x] = np.clip(y + offset_y, 0, h - 1)
        
        # Appliquer la transformation
        result = cv2.remap(img_np, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
