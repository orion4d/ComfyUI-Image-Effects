import numpy as np
import torch
from scipy import interpolate

class CurvesNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "channel": (["RGB", "Red", "Green", "Blue"], {"default": "RGB"}),
                # Points de contrôle pour la courbe (format: x,y;x,y;...)
                "curve_points": ("STRING", {"default": "0,0;64,64;128,128;192,192;255,255", "multiline": False}),
                "interpolation": (["linear", "cubic", "quadratic"], {"default": "cubic"}),
            },
            "optional": {
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}),
                "preserve_luminosity": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_curves"
    CATEGORY = "Image Effects"

    def parse_curve_points(self, curve_points_str):
        """Parse la chaîne de points de courbe en coordonnées"""
        try:
            points = []
            pairs = curve_points_str.split(';')
            for pair in pairs:
                x, y = map(float, pair.split(','))
                # Normaliser les valeurs entre 0 et 1
                points.append((x/255.0, y/255.0))
            
            # Trier par x pour assurer l'ordre croissant
            points.sort(key=lambda p: p[0])
            
            # S'assurer que les points de début et fin sont présents
            if points[0][0] > 0:
                points.insert(0, (0, 0))
            if points[-1][0] < 1:
                points.append((1, 1))
                
            return points
        except:
            # Points par défaut si erreur de parsing
            return [(0, 0), (0.25, 0.25), (0.5, 0.5), (0.75, 0.75), (1, 1)]

    def create_lookup_table(self, points, interpolation_method):
        """Crée une table de correspondance pour la courbe"""
        x_points = [p[0] for p in points]
        y_points = [p[1] for p in points]
        
        # Créer 256 points pour la LUT
        x_lut = np.linspace(0, 1, 256)
        
        if interpolation_method == "linear":
            y_lut = np.interp(x_lut, x_points, y_points)
        elif interpolation_method == "cubic":
            if len(points) >= 4:
                # Spline cubique
                tck = interpolate.splrep(x_points, y_points, s=0, k=min(3, len(points)-1))
                y_lut = interpolate.splev(x_lut, tck)
            else:
                # Fallback vers linéaire si pas assez de points
                y_lut = np.interp(x_lut, x_points, y_points)
        else:  # quadratic
            if len(points) >= 3:
                tck = interpolate.splrep(x_points, y_points, s=0, k=min(2, len(points)-1))
                y_lut = interpolate.splev(x_lut, tck)
            else:
                y_lut = np.interp(x_lut, x_points, y_points)
        
        # Clipper les valeurs entre 0 et 1
        y_lut = np.clip(y_lut, 0, 1)
        
        return y_lut

    def rgb_to_luminance(self, rgb):
        """Convertit RGB en luminance"""
        return 0.299 * rgb[:,:,0] + 0.587 * rgb[:,:,1] + 0.114 * rgb[:,:,2]

    def apply_curves(self, image, channel, curve_points, interpolation, strength=1.0, preserve_luminosity=False):
        # Prendre la première image du batch
        if len(image.shape) == 4:
            img_tensor = image[0]
        else:
            img_tensor = image
        
        # Convertir en numpy
        image_np = img_tensor.cpu().numpy()
        h, w, c = image_np.shape
        
        # Parser les points de courbe
        points = self.parse_curve_points(curve_points)
        
        # Créer la table de correspondance
        lut = self.create_lookup_table(points, interpolation)
        
        # Copier l'image
        result = image_np.copy()
        
        # Sauvegarder la luminance originale si nécessaire
        if preserve_luminosity:
            original_luminance = self.rgb_to_luminance(result)
        
        # Déterminer les canaux à traiter
        if channel == "RGB":
            channels_to_process = [0, 1, 2]
        elif channel == "Red":
            channels_to_process = [0]
        elif channel == "Green":
            channels_to_process = [1]
        elif channel == "Blue":
            channels_to_process = [2]
        
        # Appliquer la courbe
        for ch in channels_to_process:
            channel_data = result[:, :, ch]
            
            # Convertir en indices pour la LUT (0-255)
            indices = np.clip((channel_data * 255).astype(int), 0, 255)
            
            # Appliquer la courbe
            curved_data = lut[indices]
            
            # Mélanger avec l'original selon la force
            result[:, :, ch] = channel_data * (1 - strength) + curved_data * strength
        
        # Restaurer la luminance si demandé
        if preserve_luminosity and channel == "RGB":
            new_luminance = self.rgb_to_luminance(result)
            # Éviter la division par zéro
            ratio = np.where(new_luminance > 0.001, original_luminance / new_luminance, 1.0)
            ratio = np.expand_dims(ratio, axis=2)
            result = result * ratio
        
        # Clipper les valeurs finales
        result = np.clip(result, 0, 1)
        
        # Reconvertir en tensor
        result_tensor = torch.from_numpy(result).unsqueeze(0)
        
        return (result_tensor,)
