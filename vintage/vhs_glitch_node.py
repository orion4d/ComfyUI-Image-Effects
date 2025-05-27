import numpy as np
import torch
import cv2
from PIL import Image, ImageEnhance

class VHSGlitchNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "glitch_intensity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "color_shift": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
                "scan_lines": ("BOOLEAN", {"default": True}),
                "noise_amount": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
            "optional": {
                "tracking_errors": ("BOOLEAN", {"default": True}),
                "color_bleeding": ("FLOAT", {"default": 0.4, "min": 0.0, "max": 1.0, "step": 0.01}),
                "frame_jitter": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_vhs_glitch"
    CATEGORY = "Image Effects"

    def apply_vhs_glitch(self, image, glitch_intensity, color_shift, scan_lines, noise_amount,
                        tracking_errors=True, color_bleeding=0.4, frame_jitter=0.1):
        
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        result = img_np.copy()
        
        # 1. Décalages horizontaux (tracking errors)
        if tracking_errors and glitch_intensity > 0:
            max_shift = int(glitch_intensity * 30)
            for i in range(0, h, np.random.randint(3, 8)):
                if np.random.random() < glitch_intensity:
                    shift = np.random.randint(-max_shift, max_shift)
                    end_row = min(i + np.random.randint(1, 5), h)
                    result[i:end_row] = np.roll(result[i:end_row], shift, axis=1)
        
        # 2. Saignement de couleur (color bleeding)
        if color_bleeding > 0:
            # Séparer les canaux RGB
            r_channel = result[:, :, 0].astype(np.float32)
            g_channel = result[:, :, 1].astype(np.float32)
            b_channel = result[:, :, 2].astype(np.float32)
            
            # Appliquer un flou horizontal différent à chaque canal
            blur_amount = int(color_bleeding * 5)
            if blur_amount > 0:
                kernel = np.ones((1, blur_amount)) / blur_amount
                r_channel = cv2.filter2D(r_channel, -1, kernel)
                b_channel = cv2.filter2D(b_channel, -1, kernel * 0.8)
            
            result = np.stack([r_channel, g_channel, b_channel], axis=2).astype(np.uint8)
        
        # 3. Décalage de couleur chromatique
        if color_shift > 0:
            hsv = cv2.cvtColor(result, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 0] = (hsv[:, :, 0] + color_shift * 180) % 180
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + color_shift * 0.3), 0, 255)
            result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        
        # 4. Lignes de balayage (scan lines)
        if scan_lines:
            for i in range(1, h, 2):
                result[i] = (result[i] * 0.8).astype(np.uint8)
        
        # 5. Bruit VHS
        if noise_amount > 0:
            noise = np.random.randint(0, int(noise_amount * 50), (h, w, c))
            result = np.clip(result.astype(np.int16) + noise - noise_amount * 25, 0, 255).astype(np.uint8)
        
        # 6. Tremblement de l'image (frame jitter)
        if frame_jitter > 0:
            jitter_x = int(np.random.uniform(-frame_jitter * 5, frame_jitter * 5))
            jitter_y = int(np.random.uniform(-frame_jitter * 3, frame_jitter * 3))
            M = np.float32([[1, 0, jitter_x], [0, 1, jitter_y]])
            result = cv2.warpAffine(result, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        
        # Conversion finale
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
