import numpy as np
import torch
import cv2
from scipy.spatial import Delaunay

class TriangulateNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "num_points": ("INT", {"default": 500, "min": 50, "max": 2000, "step": 50}),
                "edge_threshold": ("FLOAT", {"default": 0.3, "min": 0.1, "max": 1.0, "step": 0.05}),
                "color_mode": (["average", "dominant", "gradient"], {"default": "average"}),
            },
            "optional": {
                "point_distribution": (["random", "edge_based", "grid"], {"default": "edge_based"}),
                "triangle_outline": ("BOOLEAN", {"default": False}),
                "outline_thickness": ("INT", {"default": 1, "min": 1, "max": 5, "step": 1}),
                "smoothing": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_triangulate"
    CATEGORY = "Image Effects"

    def apply_triangulate(self, image, num_points, edge_threshold, color_mode,
                         point_distribution="edge_based", triangle_outline=False, 
                         outline_thickness=1, smoothing=0.0):
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        h, w, c = img_np.shape
        
        # Générer les points selon la distribution
        points = self._generate_points(img_np, num_points, point_distribution, edge_threshold)
        
        # Triangulation de Delaunay
        tri = Delaunay(points)
        
        # Créer l'image triangulée
        result = self._create_triangulated_image(img_np, points, tri.simplices, 
                                               color_mode, triangle_outline, outline_thickness)
        
        # Appliquer le lissage si demandé
        if smoothing > 0:
            result = self._apply_smoothing(result, smoothing)
        
        result_tensor = torch.from_numpy(result.astype(np.float32) / 255.0).unsqueeze(0)
        return (result_tensor,)
    
    def _generate_points(self, image, num_points, distribution, edge_threshold):
        """Générer les points pour la triangulation"""
        h, w = image.shape[:2]
        points = []
        
        # Ajouter les coins
        points.extend([[0, 0], [w-1, 0], [w-1, h-1], [0, h-1]])
        
        if distribution == "random":
            # Distribution aléatoire
            for _ in range(num_points - 4):
                x = np.random.randint(0, w)
                y = np.random.randint(0, h)
                points.append([x, y])
                
        elif distribution == "edge_based":
            # Basé sur les contours
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, int(edge_threshold * 100), int(edge_threshold * 200))
            
            # Points sur les contours
            edge_points = np.column_stack(np.where(edges > 0))
            if len(edge_points) > 0:
                # Échantillonner les points de contour
                indices = np.random.choice(len(edge_points), 
                                         min(num_points // 2, len(edge_points)), 
                                         replace=False)
                for idx in indices:
                    y, x = edge_points[idx]
                    points.append([x, y])
            
            # Points aléatoires pour compléter
            remaining = num_points - len(points)
            for _ in range(remaining):
                x = np.random.randint(0, w)
                y = np.random.randint(0, h)
                points.append([x, y])
                
        elif distribution == "grid":
            # Distribution en grille avec variation
            grid_size = int(np.sqrt(num_points))
            for i in range(grid_size):
                for j in range(grid_size):
                    if len(points) >= num_points:
                        break
                    x = int((j + 0.5) * w / grid_size) + np.random.randint(-w//20, w//20)
                    y = int((i + 0.5) * h / grid_size) + np.random.randint(-h//20, h//20)
                    x = np.clip(x, 0, w-1)
                    y = np.clip(y, 0, h-1)
                    points.append([x, y])
        
        return np.array(points)
    
    def _create_triangulated_image(self, image, points, triangles, color_mode, outline, thickness):
        """Créer l'image triangulée"""
        h, w, c = image.shape
        result = np.zeros_like(image)
        
        for triangle in triangles:
            # Points du triangle
            pts = points[triangle].astype(np.int32)
            
            # Calculer la couleur du triangle
            color = self._get_triangle_color(image, pts, color_mode)
            
            # Dessiner le triangle
            cv2.fillPoly(result, [pts], color.tolist())
            
            # Dessiner le contour si demandé
            if outline:
                cv2.polylines(result, [pts], True, (0, 0, 0), thickness)
        
        return result
    
    def _get_triangle_color(self, image, triangle_points, mode):
        """Calculer la couleur d'un triangle"""
        # Créer un masque pour le triangle
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [triangle_points], 255)
        
        if mode == "average":
            # Couleur moyenne
            masked_pixels = image[mask > 0]
            if len(masked_pixels) > 0:
                return np.mean(masked_pixels, axis=0)
            else:
                return np.array([128, 128, 128])
                
        elif mode == "dominant":
            # Couleur dominante (approximation)
            masked_pixels = image[mask > 0]
            if len(masked_pixels) > 0:
                # Quantifier les couleurs et prendre la plus fréquente
                pixels_reshaped = masked_pixels.reshape(-1, 3)
                unique_colors, counts = np.unique(pixels_reshaped, axis=0, return_counts=True)
                dominant_color = unique_colors[np.argmax(counts)]
                return dominant_color
            else:
                return np.array([128, 128, 128])
                
        elif mode == "gradient":
            # Gradient basé sur la position
            center = np.mean(triangle_points, axis=0)
            h, w = image.shape[:2]
            gradient_factor = center[1] / h  # Gradient vertical
            base_color = np.mean(image[mask > 0], axis=0) if np.any(mask > 0) else np.array([128, 128, 128])
            return base_color * (0.5 + 0.5 * gradient_factor)
    
    def _apply_smoothing(self, image, smoothing):
        """Appliquer un lissage à l'image"""
        kernel_size = int(smoothing * 10) * 2 + 1
        smoothed = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        return image * (1 - smoothing) + smoothed * smoothing
