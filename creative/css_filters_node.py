import numpy as np
import torch
from PIL import Image, ImageEnhance, ImageFilter
import cv2

class CSSFiltersNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "blur": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 20.0, "step": 0.1}),
                "brightness": ("FLOAT", {"default": 100.0, "min": 0.0, "max": 300.0, "step": 1.0}),
                "contrast": ("FLOAT", {"default": 100.0, "min": 0.0, "max": 300.0, "step": 1.0}),
                "grayscale": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 1.0}),
                "sepia": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 1.0}),
                "hue_rotate": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0}),
                "saturate": ("FLOAT", {"default": 100.0, "min": 0.0, "max": 300.0, "step": 1.0}),
                "invert": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 1.0}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_css_filters"
    CATEGORY = "Image Effects"

    def apply_css_filters(self, image, blur=0.0, brightness=100.0, contrast=100.0, 
                         grayscale=0.0, sepia=0.0, hue_rotate=0.0, saturate=100.0, invert=0.0):
        
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        # Convertir en PIL
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        pil_img = Image.fromarray(img_np)
        
        # Appliquer les filtres CSS équivalents
        result = pil_img.copy()
        
        # Blur (flou)
        if blur > 0:
            result = result.filter(ImageFilter.GaussianBlur(radius=blur))
        
        # Brightness (luminosité)
        if brightness != 100.0:
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(brightness / 100.0)
        
        # Contrast (contraste)
        if contrast != 100.0:
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(contrast / 100.0)
        
        # Saturate (saturation)
        if saturate != 100.0:
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(saturate / 100.0)
        
        # Convertir en numpy pour les filtres avancés
        result_np = np.array(result)
        
        # Grayscale (niveaux de gris)
        if grayscale > 0:
            gray = cv2.cvtColor(result_np, cv2.COLOR_RGB2GRAY)
            gray_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            alpha = grayscale / 100.0
            result_np = (result_np * (1 - alpha) + gray_rgb * alpha).astype(np.uint8)
        
        # Sepia
        if sepia > 0:
            sepia_filter = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])
            sepia_img = result_np @ sepia_filter.T
            sepia_img = np.clip(sepia_img, 0, 255)
            alpha = sepia / 100.0
            result_np = (result_np * (1 - alpha) + sepia_img * alpha).astype(np.uint8)
        
        # Hue rotate (rotation de teinte)
        if hue_rotate != 0:
            hsv = cv2.cvtColor(result_np, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 0] = (hsv[:, :, 0] + hue_rotate) % 180
            result_np = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        
        # Invert (inversion)
        if invert > 0:
            inverted = 255 - result_np
            alpha = invert / 100.0
            result_np = (result_np * (1 - alpha) + inverted * alpha).astype(np.uint8)
        
        # Reconvertir en tensor
        result_tensor = torch.from_numpy(result_np.astype(np.float32) / 255.0).unsqueeze(0)
        
        return (result_tensor,)
