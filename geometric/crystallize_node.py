import numpy as np
import torch
import cv2
from scipy.spatial import Voronoi

class CrystallizeNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "crystal_size": ("INT", {"default": 30, "min": 10, "max": 100, "step": 5}),
                "num_crystals": ("INT", {"default": 200, "min": 50, "max": 1000, "step": 50}),
                "crystal_shape": (["angular", "organic", "geometric"], {"default": "angular"}),
            },
            "optional": {
                "edge_enhancement": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.1}),
                "color_variation": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.1}),
                "outline_strength": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.1}),
                "randomness": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_crystallize"
    CATEGORY = "Image Effects"

    def apply_crystallize(self, image, crystal_size, num_crystals, crystal_shape,
                         edge_enhancement=0.3, color_variation=0.2, outline_strength=0.5, randomness=0.3):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        
        # Générer les centres de cristaux
        crystal_centers = self._generate_crystal_centers(img_np, num_crystals, edge_enhancement)
        
        # Créer l'effet de cristallisation
        result = self._create_crystallized_image(img_np, crystal_centers, crystal_size, 
                                               crystal_shape, color_variation, 
                                               outline_strength, randomness)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
    
    def _generate_crystal_centers(self, image, num_crystals, edge_enhancement):
        """Générer les centres des cristaux"""
        h, w = image.shape[:2]
        centers = []
        
        if edge_enhancement > 0:
            # Détecter les contours pour placer plus de cristaux sur les bords
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_points = np.column_stack(np.where(edges > 0))
            
            # Placer des cristaux sur les contours
            num_edge_crystals = int(num_crystals * edge_enhancement)
            if len(edge_points) > 0:
                indices = np.random.choice(len(edge_points), 
                                         min(num_edge_crystals, len(edge_points)), 
                                         replace=False)
                for idx in indices:
                    y, x = edge_points[idx]
                    centers.append([x, y])
        
        # Compléter avec des centres aléatoires
        remaining = num_crystals - len(centers)
        for _ in range(remaining):
            x = np.random.randint(0, w)
            y = np.random.randint(0, h)
            centers.append([x, y])
        
        return np.array(centers)
    
    def _create_crystallized_image(self, image, centers, crystal_size, shape, 
                                 color_variation, outline_strength, randomness):
        """Créer l'image cristallisée"""
        h, w, c = image.shape
        result = np.zeros_like(image)
        
        # Créer une carte de régions basée sur la distance
        for y in range(h):
            for x in range(w):
                # Trouver le centre le plus proche
                distances = np.sum((centers - np.array([x, y]))**2, axis=1)
                closest_idx = np.argmin(distances)
                closest_center = centers[closest_idx]
                
                # Calculer la couleur du cristal
                color = self._get_crystal_color(image, closest_center, crystal_size, 
                                              color_variation, randomness, closest_idx)
                
                result[y, x] = color
        
        # Ajouter les contours des cristaux
        if outline_strength > 0:
            result = self._add_crystal_outlines(result, centers, outline_strength)
        
        # Appliquer la forme des cristaux
        if shape != "organic":
            result = self._apply_crystal_shape(result, centers, crystal_size, shape, randomness)
        
        return result
    
    def _get_crystal_color(self, image, center, size, variation, randomness, seed):
        """Obtenir la couleur d'un cristal"""
        h, w, c = image.shape
        center_x, center_y = int(center[0]), int(center[1])
        
        # Région autour du centre
        region_size = max(5, size // 4)
        x1 = max(0, center_x - region_size)
        x2 = min(w, center_x + region_size)
        y1 = max(0, center_y - region_size)
        y2 = min(h, center_y + region_size)
        
        region = image[y1:y2, x1:x2]
        if region.size > 0:
            base_color = np.mean(region.reshape(-1, c), axis=0)
        else:
            base_color = image[center_y, center_x] if 0 <= center_x < w and 0 <= center_y < h else np.array([128, 128, 128])
        
        # Ajouter de la variation de couleur
        if variation > 0:
            np.random.seed(seed)
            variation_amount = variation * 50
            color_shift = np.random.uniform(-variation_amount, variation_amount, 3)
            base_color = np.clip(base_color + color_shift, 0, 255)
        
        return base_color
    
    def _add_crystal_outlines(self, image, centers, strength):
        """Ajouter les contours des cristaux"""
        h, w = image.shape[:2]
        
        # Créer une carte des régions
        regions = np.zeros((h, w), dtype=np.int32)
        for y in range(h):
            for x in range(w):
                distances = np.sum((centers - np.array([x, y]))**2, axis=1)
                regions[y, x] = np.argmin(distances)
        
        # Détecter les frontières
        edges = np.zeros((h, w), dtype=np.uint8)
        for y in range(1, h-1):
            for x in range(1, w-1):
                if (regions[y, x] != regions[y-1, x] or 
                    regions[y, x] != regions[y+1, x] or
                    regions[y, x] != regions[y, x-1] or 
                    regions[y, x] != regions[y, x+1]):
                    edges[y, x] = 255
        
        # Appliquer l'effet de contour
        result = image.copy()
        edge_mask = edges > 0
        
        # Assombrir les contours
        result[edge_mask] = result[edge_mask] * (1 - strength)
        
        return result
    
    def _apply_crystal_shape(self, image, centers, size, shape, randomness):
        """Appliquer une forme spécifique aux cristaux"""
        h, w = image.shape[:2]
        result = image.copy()
        
        if shape == "angular":
            # Créer des formes angulaires
            for i, center in enumerate(centers):
                np.random.seed(i)
                num_sides = np.random.randint(3, 8)
                radius = size // 2 + np.random.randint(-size//4, size//4)
                
                # Créer un polygone angulaire
                angles = np.linspace(0, 2*np.pi, num_sides, endpoint=False)
                if randomness > 0:
                    angles += np.random.uniform(-randomness, randomness, num_sides)
                
                points = []
                for angle in angles:
                    r = radius * (1 + np.random.uniform(-randomness, randomness) * 0.3)
                    x = int(center[0] + r * np.cos(angle))
                    y = int(center[1] + r * np.sin(angle))
                    points.append([x, y])
                
                if len(points) >= 3:
                    points = np.array(points, dtype=np.int32)
                    # Obtenir la couleur moyenne de la région
                    mask = np.zeros((h, w), dtype=np.uint8)
                    cv2.fillPoly(mask, [points], 255)
                    if np.any(mask):
                        avg_color = np.mean(image[mask > 0], axis=0)
                        cv2.fillPoly(result, [points], avg_color.tolist())
        
        elif shape == "geometric":
            # Créer des formes géométriques régulières
            for i, center in enumerate(centers):
                np.random.seed(i)
                shape_type = np.random.choice(['triangle', 'square', 'hexagon'])
                radius = size // 2
                
                if shape_type == 'triangle':
                    points = self._create_triangle(center, radius)
                elif shape_type == 'square':
                    points = self._create_square(center, radius)
                elif shape_type == 'hexagon':
                    points = self._create_hexagon(center, radius)
                
                # Dessiner la forme
                mask = np.zeros((h, w), dtype=np.uint8)
                cv2.fillPoly(mask, [points], 255)
                if np.any(mask):
                    avg_color = np.mean(image[mask > 0], axis=0)
                    cv2.fillPoly(result, [points], avg_color.tolist())
        
        return result
    
    def _create_triangle(self, center, radius):
        """Créer un triangle"""
        points = []
        for i in range(3):
            angle = i * 2 * np.pi / 3
            x = int(center[0] + radius * np.cos(angle))
            y = int(center[1] + radius * np.sin(angle))
            points.append([x, y])
        return np.array(points, dtype=np.int32)
    
    def _create_square(self, center, radius):
        """Créer un carré"""
        points = []
        for i in range(4):
            angle = i * np.pi / 2 + np.pi / 4
            x = int(center[0] + radius * np.cos(angle))
            y = int(center[1] + radius * np.sin(angle))
            points.append([x, y])
        return np.array(points, dtype=np.int32)
    
    def _create_hexagon(self, center, radius):
        """Créer un hexagone"""
        points = []
        for i in range(6):
            angle = i * np.pi / 3
            x = int(center[0] + radius * np.cos(angle))
            y = int(center[1] + radius * np.sin(angle))
            points.append([x, y])
        return np.array(points, dtype=np.int32)
