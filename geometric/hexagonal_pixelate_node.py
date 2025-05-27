import numpy as np
import torch
import cv2

class HexagonalPixelateNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "hex_size": ("INT", {"default": 20, "min": 5, "max": 100, "step": 5}),
                "color_mode": (["average", "center", "dominant"], {"default": "average"}),
            },
            "optional": {
                "spacing": ("FLOAT", {"default": 0.9, "min": 0.5, "max": 1.0, "step": 0.05}),
                "rotation": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 60.0, "step": 5.0}),
                "outline": ("BOOLEAN", {"default": False}),
                "outline_thickness": ("INT", {"default": 1, "min": 1, "max": 3, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_hexagonal_pixelate"
    CATEGORY = "Image Effects"

    def apply_hexagonal_pixelate(self, image, hex_size, color_mode,
                                spacing=0.9, rotation=0.0, outline=False, outline_thickness=1):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        
        # Créer l'image hexagonale
        result = self._create_hexagonal_pattern(img_np, hex_size, color_mode, 
                                              spacing, rotation, outline, outline_thickness)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
    
    def _create_hexagonal_pattern(self, image, hex_size, color_mode, spacing, rotation, outline, thickness):
        """Créer le motif hexagonal"""
        h, w, c = image.shape
        result = np.zeros_like(image)
        
        # Calculer les dimensions hexagonales
        hex_height = hex_size * 2
        hex_width = int(hex_size * np.sqrt(3))
        
        # Espacement entre hexagones
        effective_size = hex_size * spacing
        
        # Rotation en radians
        rot_rad = np.radians(rotation)
        
        # Parcourir la grille hexagonale
        for row in range(-1, h // int(hex_height * 0.75) + 2):
            for col in range(-1, w // hex_width + 2):
                # Position de l'hexagone
                if row % 2 == 0:
                    x = col * hex_width
                else:
                    x = col * hex_width + hex_width // 2
                
                y = row * int(hex_height * 0.75)
                
                # Appliquer la rotation
                if rotation != 0:
                    center_x, center_y = w // 2, h // 2
                    x_rot = (x - center_x) * np.cos(rot_rad) - (y - center_y) * np.sin(rot_rad) + center_x
                    y_rot = (x - center_x) * np.sin(rot_rad) + (y - center_y) * np.cos(rot_rad) + center_y
                    x, y = int(x_rot), int(y_rot)
                
                # Vérifier si l'hexagone est dans l'image
                if -hex_size <= x <= w + hex_size and -hex_size <= y <= h + hex_size:
                    # Créer l'hexagone
                    hex_points = self._create_hexagon_points(x, y, effective_size, rotation)
                    
                    # Obtenir la couleur de l'hexagone
                    color = self._get_hexagon_color(image, hex_points, color_mode)
                    
                    # Dessiner l'hexagone
                    if hex_points is not None:
                        cv2.fillPoly(result, [hex_points], color.tolist())
                        
                        # Ajouter le contour si demandé
                        if outline:
                            cv2.polylines(result, [hex_points], True, (0, 0, 0), thickness)
        
        return result
    
    def _create_hexagon_points(self, center_x, center_y, size, rotation):
        """Créer les points d'un hexagone"""
        points = []
        rot_rad = np.radians(rotation)
        
        for i in range(6):
            angle = i * np.pi / 3 + rot_rad
            x = center_x + size * np.cos(angle)
            y = center_y + size * np.sin(angle)
            points.append([int(x), int(y)])
        
        return np.array(points, dtype=np.int32)
    
    def _get_hexagon_color(self, image, hex_points, mode):
        """Obtenir la couleur d'un hexagone"""
        h, w, c = image.shape
        
        # Créer un masque pour l'hexagone
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [hex_points], 255)
        
        # Obtenir les pixels dans l'hexagone
        masked_pixels = image[mask > 0]
        
        if len(masked_pixels) == 0:
            return np.array([128, 128, 128])  # Couleur par défaut
        
        if mode == "average":
            return np.mean(masked_pixels, axis=0)
        elif mode == "center":
            # Couleur du centre de l'hexagone
            center = np.mean(hex_points, axis=0).astype(int)
            if 0 <= center[0] < w and 0 <= center[1] < h:
                return image[center[1], center[0]]
            else:
                return np.mean(masked_pixels, axis=0)
        elif mode == "dominant":
            # Couleur dominante (approximation)
            pixels_reshaped = masked_pixels.reshape(-1, 3)
            unique_colors, counts = np.unique(pixels_reshaped, axis=0, return_counts=True)
            return unique_colors[np.argmax(counts)]
        
        return np.mean(masked_pixels, axis=0)
