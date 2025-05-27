import numpy as np
import torch
import cv2
from PIL import Image, ImageDraw, ImageFont

class PolaroidNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "border_size": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 0.3, "step": 0.01}),
                "vintage_tone": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
                "fade_amount": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
            "optional": {
                "add_text": ("BOOLEAN", {"default": False}),
                "text_content": ("STRING", {"default": "Summer '85", "multiline": False}),
                "paper_texture": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
                "color_shift": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_polaroid_effect"
    CATEGORY = "Image Effects"

    def apply_polaroid_effect(self, image, border_size, vintage_tone, fade_amount,
                             add_text=False, text_content="Summer '85", paper_texture=0.3, color_shift=0.1):
        
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        
        # 1. Calculer les dimensions avec bordure
        border_h = int(h * border_size)
        border_w = int(w * border_size)
        bottom_border = border_h * 3  # Bordure inférieure plus large (caractéristique Polaroid)
        
        new_h = h + border_h + bottom_border
        new_w = w + border_w * 2
        
        # 2. Créer l'image avec bordure blanche
        polaroid = np.full((new_h, new_w, c), 245, dtype=np.uint8)  # Blanc cassé
        
        # 3. Traitement de l'image principale
        result = img_np.copy().astype(np.float32)
        
        # Effet vintage/sépia
        if vintage_tone > 0:
            sepia_matrix = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])
            sepia_img = result @ sepia_matrix.T
            result = result * (1 - vintage_tone) + sepia_img * vintage_tone
        
        # Décoloration caractéristique des Polaroids
        if fade_amount > 0:
            # Réduire légèrement le contraste
            result = (result - 127.5) * (1 - fade_amount * 0.3) + 127.5
            
            # Ajouter une teinte jaunâtre
            result[:, :, 0] *= (1 + fade_amount * 0.1)  # Plus de rouge
            result[:, :, 1] *= (1 + fade_amount * 0.05)  # Légèrement plus de vert
            result[:, :, 2] *= (1 - fade_amount * 0.1)   # Moins de bleu
        
        # Décalage de couleur subtil
        if color_shift > 0:
            hsv = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 0] = (hsv[:, :, 0] + color_shift * 10) % 180
            result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
        
        # Vignette douce
        center_x, center_y = w // 2, h // 2
        max_dist = np.sqrt(center_x**2 + center_y**2)
        y, x = np.ogrid[:h, :w]
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        vignette = 1 - (distance / max_dist) * 0.2
        vignette = np.clip(vignette, 0.8, 1)
        result = result * np.expand_dims(vignette, axis=2)
        
        result = np.clip(result, 0, 255)
        
        # 4. Placer l'image dans la bordure
        polaroid[border_h:border_h+h, border_w:border_w+w] = result.astype(np.uint8)
        
        # 5. Ajouter de la texture papier
        if paper_texture > 0:
            texture = self._generate_paper_texture(new_h, new_w, paper_texture)
            polaroid = polaroid.astype(np.float32)
            polaroid += texture
            polaroid = np.clip(polaroid, 0, 255)
        
        # 6. Ajouter du texte si demandé
        if add_text and text_content:
            polaroid = self._add_handwritten_text(polaroid, text_content, bottom_border)
        
        # 7. Légère rotation aléatoire pour un effet authentique
        angle = np.random.uniform(-2, 2)
        center = (new_w // 2, new_h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        polaroid = cv2.warpAffine(polaroid.astype(np.uint8), rotation_matrix, (new_w, new_h),
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(240, 240, 240))
        
        result_tensor = torch.from_numpy(polaroid.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)

    def _generate_paper_texture(self, h, w, intensity):
        """Générer une texture de papier photo"""
        # Créer du bruit pour simuler la texture du papier
        texture = np.random.normal(0, intensity * 10, (h, w))
        
        # Ajouter des variations de grain plus grossières
        coarse_texture = np.random.normal(0, intensity * 5, (h // 4, w // 4))
        coarse_texture = cv2.resize(coarse_texture, (w, h), interpolation=cv2.INTER_LINEAR)
        
        texture = texture + coarse_texture
        texture = np.expand_dims(texture, axis=2)
        texture = np.repeat(texture, 3, axis=2)
        
        return texture

    def _add_handwritten_text(self, image, text, bottom_border):
        """Ajouter du texte dans la bordure inférieure"""
        h, w = image.shape[:2]
        
        # Convertir en PIL pour le texte
        pil_image = Image.fromarray(image.astype(np.uint8))
        draw = ImageDraw.Draw(pil_image)
        
        # Essayer de charger une police
        try:
            font_size = max(12, bottom_border // 4)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Position du texte (centré dans la bordure inférieure)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (w - text_width) // 2
        y = h - bottom_border + (bottom_border - text_height) // 2
        
        # Couleur du texte (gris foncé pour un effet authentique)
        text_color = (80, 80, 80)
        draw.text((x, y), text, fill=text_color, font=font)
        
        return np.array(pil_image)
