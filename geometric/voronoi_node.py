import numpy as np
import torch
import cv2
from scipy.spatial import Voronoi, voronoi_plot_2d

class VoronoiNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "num_seeds": ("INT", {"default": 100, "min": 10, "max": 500, "step": 10}),
                "color_mode": (["average", "center_point", "random"], {"default": "average"}),
                "cell_outline": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "seed_distribution": (["random", "edge_based", "grid"], {"default": "random"}),
                "outline_color": (["black", "white", "adaptive"], {"default": "black"}),
                "outline_thickness": ("INT", {"default": 2, "min": 1, "max": 5, "step": 1}),
                "edge_threshold": ("FLOAT", {"default": 0.3, "min": 0.1, "max": 1.0, "step": 0.05}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_voronoi"
    CATEGORY = "Image Effects"

    def apply_voronoi(self, image, num_seeds, color_mode, cell_outline,
                     seed_distribution="random", outline_color="black", 
                     outline_thickness=2, edge_threshold=0.3):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        
        # Générer les graines
        seeds = self._generate_seeds(img_np, num_seeds, seed_distribution, edge_threshold)
        
        # Créer le diagramme de Voronoï
        result = self._create_voronoi_image(img_np, seeds, color_mode, 
                                          cell_outline, outline_color, outline_thickness)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
    
    def _generate_seeds(self, image, num_seeds, distribution, edge_threshold):
        """Générer les graines pour le diagramme de Voronoï"""
        h, w = image.shape[:2]
        seeds = []
        
        if distribution == "random":
            for _ in range(num_seeds):
                x = np.random.randint(0, w)
                y = np.random.randint(0, h)
                seeds.append([x, y])
                
        elif distribution == "edge_based":
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, int(edge_threshold * 100), int(edge_threshold * 200))
            edge_points = np.column_stack(np.where(edges > 0))
            
            if len(edge_points) > 0:
                indices = np.random.choice(len(edge_points), 
                                         min(num_seeds // 2, len(edge_points)), 
                                         replace=False)
                for idx in indices:
                    y, x = edge_points[idx]
                    seeds.append([x, y])
            
            # Compléter avec des points aléatoires
            remaining = num_seeds - len(seeds)
            for _ in range(remaining):
                x = np.random.randint(0, w)
                y = np.random.randint(0, h)
                seeds.append([x, y])
                
        elif distribution == "grid":
            grid_size = int(np.sqrt(num_seeds))
            for i in range(grid_size):
                for j in range(grid_size):
                    if len(seeds) >= num_seeds:
                        break
                    x = int((j + 0.5) * w / grid_size) + np.random.randint(-w//20, w//20)
                    y = int((i + 0.5) * h / grid_size) + np.random.randint(-h//20, h//20)
                    x = np.clip(x, 0, w-1)
                    y = np.clip(y, 0, h-1)
                    seeds.append([x, y])
        
        return np.array(seeds)
    
    def _create_voronoi_image(self, image, seeds, color_mode, outline, outline_color, thickness):
        """Créer l'image avec diagramme de Voronoï"""
        h, w, c = image.shape
        result = np.zeros_like(image)
        
        # Créer une carte de distance pour chaque graine
        for y in range(h):
            for x in range(w):
                # Trouver la graine la plus proche
                distances = np.sum((seeds - np.array([x, y]))**2, axis=1)
                closest_seed_idx = np.argmin(distances)
                closest_seed = seeds[closest_seed_idx]
                
                # Déterminer la couleur de la cellule
                if color_mode == "average":
                    # Couleur moyenne autour de la graine
                    seed_x, seed_y = int(closest_seed[0]), int(closest_seed[1])
                    region_size = 10
                    x1 = max(0, seed_x - region_size)
                    x2 = min(w, seed_x + region_size)
                    y1 = max(0, seed_y - region_size)
                    y2 = min(h, seed_y + region_size)
                    region = image[y1:y2, x1:x2]
                    if region.size > 0:
                        color = np.mean(region.reshape(-1, c), axis=0)
                    else:
                        color = image[seed_y, seed_x]
                        
                elif color_mode == "center_point":
                    # Couleur du point central de la graine
                    seed_x, seed_y = int(closest_seed[0]), int(closest_seed[1])
                    color = image[seed_y, seed_x]
                    
                elif color_mode == "random":
                    # Couleur aléatoire par cellule
                    np.random.seed(closest_seed_idx)
                    color = np.random.randint(0, 256, 3)
                
                result[y, x] = color
        
        # Ajouter les contours si demandé
        if outline:
            outline_img = self._add_voronoi_outlines(result, seeds, outline_color, thickness)
            result = outline_img
        
        return result
    
    def _add_voronoi_outlines(self, image, seeds, outline_color, thickness):
        """Ajouter les contours des cellules de Voronoï"""
        h, w = image.shape[:2]
        
        # Créer une carte des régions
        regions = np.zeros((h, w), dtype=np.int32)
        for y in range(h):
            for x in range(w):
                distances = np.sum((seeds - np.array([x, y]))**2, axis=1)
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
        
        # Appliquer l'épaisseur
        if thickness > 1:
            kernel = np.ones((thickness, thickness), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Appliquer la couleur de contour
        result = image.copy()
        if outline_color == "black":
            color = [0, 0, 0]
        elif outline_color == "white":
            color = [255, 255, 255]
        elif outline_color == "adaptive":
            # Couleur adaptative basée sur la luminosité locale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            color = np.where(gray[edges > 0] > 128, [0, 0, 0], [255, 255, 255])
            result[edges > 0] = color
            return result
        
        result[edges > 0] = color
        return result
