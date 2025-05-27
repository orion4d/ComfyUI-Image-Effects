import numpy as np
import cv2
import torch

class KaleidoscopeNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "facettes": ("INT", {"default": 6, "min": 2, "max": 20}),
            },
            "optional": {
                "center_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "center_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "radius": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.05}),
                "rotation": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 1.0}),
                "mirror_mode": (["alternate", "all", "none"], {"default": "alternate"}),
                "blend_mode": (["add", "max", "average", "overlay"], {"default": "add"}),
                "fade_edges": ("BOOLEAN", {"default": True}),
                "color_shift": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_kaleidoscope"
    CATEGORY = "Image Effects"

    def generate_kaleidoscope(self, image, facettes, center_x=0.5, center_y=0.5, 
                            radius=1.0, rotation=0.0, mirror_mode="alternate", 
                            blend_mode="add", fade_edges=True, color_shift=0.0):
        
        # Prendre la première image du batch
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        # Convertir en numpy array
        image_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = image_np.shape
        
        # Calculer le centre personnalisé
        center = (int(w * center_x), int(h * center_y))
        
        # Calculer le rayon effectif
        max_radius = min(w, h) // 2
        effective_radius = int(max_radius * radius)
        
        # Angle de base avec rotation
        base_angle = 360 / facettes
        
        print(f"Kaleidoscope: {facettes} facettes, centre: {center}, rayon: {effective_radius}")
        
        # Créer le masque pour un secteur
        mask = self._create_sector_mask(h, w, center, facettes, effective_radius, rotation, fade_edges)
        
        # Appliquer le masque pour obtenir le secteur de base
        base_sector = cv2.bitwise_and(image_np, image_np, mask=mask)
        
        # Appliquer un décalage de couleur si demandé
        if color_shift != 0.0:
            base_sector = self._apply_color_shift(base_sector, color_shift)
        
        # Créer le résultat kaléidoscope
        result = self._create_kaleidoscope_effect(
            base_sector, facettes, center, base_angle, rotation,
            mirror_mode, blend_mode, h, w
        )
        
        # Normaliser et convertir en tensor
        result = np.clip(result, 0, 255).astype(np.float32) / 255.0
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        
        return (result_tensor,)
    
    def _create_sector_mask(self, h, w, center, facettes, radius, rotation, fade_edges):
        """Créer un masque triangulaire pour un secteur avec dégradé optionnel"""
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Calculer l'angle du secteur
        sector_angle = np.radians(360 / facettes)
        start_angle = np.radians(rotation)
        
        # Points du secteur triangulaire
        x1 = int(center[0] + radius * np.cos(start_angle))
        y1 = int(center[1] + radius * np.sin(start_angle))
        x2 = int(center[0] + radius * np.cos(start_angle + sector_angle))
        y2 = int(center[1] + radius * np.sin(start_angle + sector_angle))
        
        points = np.array([center, (x1, y1), (x2, y2)], dtype=np.int32)
        cv2.fillConvexPoly(mask, points, 255)
        
        # Ajouter un dégradé radial pour adoucir les bords
        if fade_edges:
            mask = self._apply_radial_fade(mask, center, radius)
        
        return mask
    
    def _apply_radial_fade(self, mask, center, radius):
        """Appliquer un dégradé radial pour adoucir les bords"""
        h, w = mask.shape
        y, x = np.ogrid[:h, :w]
        
        # Calculer la distance depuis le centre
        distance = np.sqrt((x - center[0])**2 + (y - center[1])**2)
        
        # Créer un dégradé radial
        fade_start = radius * 0.7
        fade_mask = np.where(distance <= fade_start, 1.0,
                           np.where(distance >= radius, 0.0,
                                  1.0 - (distance - fade_start) / (radius - fade_start)))
        
        # Appliquer le dégradé au masque
        faded_mask = (mask.astype(np.float32) / 255.0 * fade_mask * 255).astype(np.uint8)
        
        return faded_mask
    
    def _apply_color_shift(self, image, shift_amount):
        """Appliquer un décalage de couleur HSV"""
        if shift_amount == 0.0:
            return image
        
        # Convertir en HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(np.float32)
        
        # Décaler la teinte
        hsv[:, :, 0] = (hsv[:, :, 0] + shift_amount * 180) % 180
        
        # Reconvertir en RGB
        shifted = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        
        return shifted
    
    def _create_kaleidoscope_effect(self, base_sector, facettes, center, base_angle, 
                                  rotation, mirror_mode, blend_mode, h, w):
        """Créer l'effet kaléidoscope avec différents modes de fusion"""
        
        if blend_mode == "add":
            result = np.zeros((h, w, 3), dtype=np.float32)
        elif blend_mode == "max":
            result = np.zeros((h, w, 3), dtype=np.uint8)
        elif blend_mode == "average":
            result = np.zeros((h, w, 3), dtype=np.float32)
            sector_count = np.zeros((h, w, 1), dtype=np.float32)
        else:  # overlay
            result = base_sector.astype(np.float32)
        
        for i in range(facettes):
            # Calculer l'angle de rotation
            angle = base_angle * i + rotation
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1)
            rotated = cv2.warpAffine(base_sector, rotation_matrix, (w, h))
            
            # Appliquer l'effet miroir selon le mode
            if mirror_mode == "alternate" and i % 2 == 1:
                rotated = cv2.flip(rotated, 1)
            elif mirror_mode == "all":
                rotated = cv2.flip(rotated, 1)
            # mirror_mode == "none" : pas de miroir
            
            # Fusionner selon le mode de fusion
            if blend_mode == "add":
                result += rotated.astype(np.float32)
            elif blend_mode == "max":
                result = np.maximum(result, rotated)
            elif blend_mode == "average":
                mask = (rotated > 0).any(axis=2, keepdims=True)
                result += rotated.astype(np.float32) * mask
                sector_count += mask
            elif blend_mode == "overlay":
                # Mode overlay simplifié
                mask = (rotated > 0).any(axis=2, keepdims=True)
                overlay = rotated.astype(np.float32) / 255.0
                base = result / 255.0
                
                overlayed = np.where(overlay < 0.5,
                                   2 * base * overlay,
                                   1 - 2 * (1 - base) * (1 - overlay))
                
                result = np.where(mask, overlayed * 255, result)
        
        # Post-traitement selon le mode de fusion
        if blend_mode == "add":
            # Normaliser pour éviter la saturation
            max_val = np.max(result)
            if max_val > 255:
                result = result * 255 / max_val
            result = result.astype(np.uint8)
        elif blend_mode == "average":
            # Calculer la moyenne
            sector_count = np.maximum(sector_count, 1)  # Éviter la division par zéro
            result = (result / sector_count).astype(np.uint8)
        
        return result

class KaleidoscopeAdvancedNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "facettes": ("INT", {"default": 6, "min": 2, "max": 20}),
                "pattern_type": (["triangle", "diamond", "hexagon", "custom"], {"default": "triangle"}),
            },
            "optional": {
                "center_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "center_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "inner_radius": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.05}),
                "outer_radius": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.05}),
                "rotation": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 1.0}),
                "symmetry_break": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05}),
                "chromatic_aberration": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "step": 0.5}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_advanced_kaleidoscope"
    CATEGORY = "Image Effects"

    def generate_advanced_kaleidoscope(self, image, facettes, pattern_type="triangle",
                                     center_x=0.5, center_y=0.5, inner_radius=0.1, 
                                     outer_radius=1.0, rotation=0.0, symmetry_break=0.0,
                                     chromatic_aberration=0.0):
        
        # Prendre la première image du batch
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        image_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = image_np.shape
        
        center = (int(w * center_x), int(h * center_y))
        
        # Créer le masque selon le type de pattern
        mask = self._create_pattern_mask(h, w, center, facettes, pattern_type, 
                                       inner_radius, outer_radius, rotation)
        
        # Appliquer l'aberration chromatique si demandée
        if chromatic_aberration > 0:
            image_np = self._apply_chromatic_aberration(image_np, chromatic_aberration)
        
        # Créer l'effet avec brisure de symétrie
        result = self._create_advanced_effect(image_np, mask, facettes, center, 
                                            rotation, symmetry_break)
        
        result = np.clip(result, 0, 255).astype(np.float32) / 255.0
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        
        return (result_tensor,)
    
    def _create_pattern_mask(self, h, w, center, facettes, pattern_type, 
                           inner_radius, outer_radius, rotation):
        """Créer différents types de masques"""
        mask = np.zeros((h, w), dtype=np.uint8)
        
        max_radius = min(w, h) // 2
        inner_r = int(max_radius * inner_radius)
        outer_r = int(max_radius * outer_radius)
        
        if pattern_type == "triangle":
            # Masque triangulaire standard
            sector_angle = np.radians(360 / facettes)
            start_angle = np.radians(rotation)
            
            x1 = int(center[0] + outer_r * np.cos(start_angle))
            y1 = int(center[1] + outer_r * np.sin(start_angle))
            x2 = int(center[0] + outer_r * np.cos(start_angle + sector_angle))
            y2 = int(center[1] + outer_r * np.sin(start_angle + sector_angle))
            
            points = np.array([center, (x1, y1), (x2, y2)], dtype=np.int32)
            cv2.fillConvexPoly(mask, points, 255)
            
        elif pattern_type == "diamond":
            # Masque en forme de diamant
            sector_angle = np.radians(360 / facettes)
            start_angle = np.radians(rotation)
            
            # Points du diamant
            x1 = int(center[0] + outer_r * np.cos(start_angle))
            y1 = int(center[1] + outer_r * np.sin(start_angle))
            x2 = int(center[0] + inner_r * np.cos(start_angle + sector_angle/2))
            y2 = int(center[1] + inner_r * np.sin(start_angle + sector_angle/2))
            x3 = int(center[0] + outer_r * np.cos(start_angle + sector_angle))
            y3 = int(center[1] + outer_r * np.sin(start_angle + sector_angle))
            
            points = np.array([(x1, y1), (x2, y2), (x3, y3), center], dtype=np.int32)
            cv2.fillConvexPoly(mask, points, 255)
            
        # Créer un trou au centre si inner_radius > 0
        if inner_r > 0:
            cv2.circle(mask, center, inner_r, 0, -1)
        
        return mask
    
    def _apply_chromatic_aberration(self, image, strength):
        """Simuler l'aberration chromatique"""
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        
        # Séparer les canaux
        r_channel = image[:, :, 0]
        g_channel = image[:, :, 1]
        b_channel = image[:, :, 2]
        
        # Appliquer un décalage différent à chaque canal
        offset = int(strength)
        
        # Décaler le rouge vers l'extérieur
        M_r = np.float32([[1, 0, offset], [0, 1, offset]])
        r_shifted = cv2.warpAffine(r_channel, M_r, (w, h))
        
        # Décaler le bleu vers l'intérieur
        M_b = np.float32([[1, 0, -offset], [0, 1, -offset]])
        b_shifted = cv2.warpAffine(b_channel, M_b, (w, h))
        
        # Recombiner les canaux
        result = np.stack([r_shifted, g_channel, b_shifted], axis=2)
        
        return result
    
    def _create_advanced_effect(self, image, mask, facettes, center, rotation, symmetry_break):
        """Créer l'effet avec brisure de symétrie"""
        h, w = image.shape[:2]
        base_sector = cv2.bitwise_and(image, image, mask=mask)
        result = np.zeros_like(image, dtype=np.float32)
        
        base_angle = 360 / facettes
        
        for i in range(facettes):
            # Ajouter une variation aléatoire pour briser la symétrie
            angle_variation = symmetry_break * 30 * (np.random.random() - 0.5)
            angle = base_angle * i + rotation + angle_variation
            
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1)
            rotated = cv2.warpAffine(base_sector, rotation_matrix, (w, h))
            
            # Effet miroir alterné avec variation
            if i % 2 == 1:
                if symmetry_break > 0.5:
                    # Parfois ne pas appliquer le miroir pour plus de chaos
                    if np.random.random() > symmetry_break:
                        rotated = cv2.flip(rotated, 1)
                else:
                    rotated = cv2.flip(rotated, 1)
            
            result += rotated.astype(np.float32)
        
        # Normaliser
        max_val = np.max(result)
        if max_val > 255:
            result = result * 255 / max_val
        
        return result.astype(np.uint8)
