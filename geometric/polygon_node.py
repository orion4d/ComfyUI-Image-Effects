import numpy as np
import torch
import cv2

class PolygonNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "polygon_sides": ("INT", {"default": 6, "min": 3, "max": 12, "step": 1}),
                "polygon_size": ("INT", {"default": 30, "min": 10, "max": 100, "step": 5}),
                "reduction_factor": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 0.9, "step": 0.1}),
            },
            "optional": {
                "color_mode": (["average", "dominant", "center"], {"default": "average"}),
                "edge_preservation": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.1}),
                "rotation": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 15.0}),
                "outline": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_polygon_reduction"
    CATEGORY = "Image Effects"

    def apply_polygon_reduction(self, image, polygon_sides, polygon_size, reduction_factor,
                               color_mode="average", edge_preservation=0.3, rotation=0.0, outline=False):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        
        # Créer l'effet de réduction polygonale
        result = self._create_polygon_reduction(img_np, polygon_sides, polygon_size, 
                                              reduction_factor, color_mode, 
                                              edge_preservation, rotation, outline)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
    
    def _create_polygon_reduction(self, image, sides, size, reduction, color_mode, 
                                edge_preservation, rotation, outline):
        """Créer l'effet de réduction polygonale"""
        h, w, c = image.shape
        
        # Calculer la nouvelle résolution
        new_w = int(w * reduction)
        new_h = int(h * reduction)
        
        # Redimensionner l'image
        reduced = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Créer l'image de sortie
        result = np.zeros_like(image)
        
        # Calculer l'espacement des polygones
        poly_spacing_x = w / new_w
        poly_spacing_y = h / new_h
        
        # Préserver les contours si demandé
        edges = None
        if edge_preservation > 0:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
        
        # Créer les polygones
        for y in range(new_h):
            for x in range(new_w):
                # Position dans l'image originale
                orig_x = int(x * poly_spacing_x + poly_spacing_x / 2)
                orig_y = int(y * poly_spacing_y + poly_spacing_y / 2)
                
                # Couleur du pixel réduit
                pixel_color = reduced[y, x]
                
                # Ajuster la couleur selon le mode
                if color_mode == "average":
                    # Moyenner la région autour du pixel
                    region_size = max(1, int(min(poly_spacing_x, poly_spacing_y) / 2))
                    x1 = max(0, orig_x - region_size)
                    x2 = min(w, orig_x + region_size)
                    y1 = max(0, orig_y - region_size)
                    y2 = min(h, orig_y + region_size)
                    region = image[y1:y2, x1:x2]
                    if region.size > 0:
                        pixel_color = np.mean(region.reshape(-1, c), axis=0)
                
                elif color_mode == "dominant":
                    # Couleur dominante dans la région
                    region_size = max(1, int(min(poly_spacing_x, poly_spacing_y) / 2))
                    x1 = max(0, orig_x - region_size)
                    x2 = min(w, orig_x + region_size)
                    y1 = max(0, orig_y - region_size)
                    y2 = min(h, orig_y + region_size)
                    region = image[y1:y2, x1:x2]
                    if region.size > 0:
                        pixels = region.reshape(-1, c)
                        unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
                        pixel_color = unique_colors[np.argmax(counts)]
                
                # Créer le polygone
                polygon_points = self._create_polygon_points(orig_x, orig_y, size, sides, rotation)
                
                # Dessiner le polygone
                cv2.fillPoly(result, [polygon_points], pixel_color.tolist())
                
                # Ajouter le contour si demandé
                if outline:
                    cv2.polylines(result, [polygon_points], True, (0, 0, 0), 1)
        
        # Préserver les contours importants
        if edge_preservation > 0 and edges is not None:
            edge_mask = edges > 0
            blend_factor = edge_preservation
            result[edge_mask] = (result[edge_mask] * (1 - blend_factor) + 
                               image[edge_mask] * blend_factor).astype(np.uint8)
        
        return result
    
    def _create_polygon_points(self, center_x, center_y, size, sides, rotation):
        """Créer les points d'un polygone"""
        points = []
        angle_step = 2 * np.pi / sides
        rotation_rad = np.radians(rotation)
        
        for i in range(sides):
            angle = i * angle_step + rotation_rad
            x = int(center_x + size * np.cos(angle))
            y = int(center_y + size * np.sin(angle))
            points.append([x, y])
        
        return np.array(points, dtype=np.int32)
