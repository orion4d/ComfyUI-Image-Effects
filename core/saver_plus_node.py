import numpy as np
import torch
import os
from datetime import datetime
from PIL import Image, ImageEnhance
import json

class SaverPlusNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename": ("STRING", {"default": "output", "multiline": False}),
                "save_path": ("STRING", {"default": "output/saver_plus/", "multiline": False}),
                "output_format": (["PNG", "TIFF", "JPEG", "WEBP", "BMP"], {"default": "PNG"}),
            },
            "optional": {
                "layer_names": ("STRING", {"default": "Layer1,Layer2,Layer3", "multiline": False}),
                "include_merged": ("BOOLEAN", {"default": True}),
                "merge_mode": (["maximum", "average", "overlay", "multiply", "screen", "soft_light"], {"default": "maximum"}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
                "add_timestamp": ("BOOLEAN", {"default": False}),
                "save_metadata": ("BOOLEAN", {"default": True}),
                "create_subfolder": ("BOOLEAN", {"default": False}),
                "compression_level": ("INT", {"default": 6, "min": 0, "max": 9, "step": 1}),
                "preserve_transparency": ("BOOLEAN", {"default": True}),
                "auto_optimize": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("save_info", "folder_path")
    FUNCTION = "save_images"
    CATEGORY = "Image Effects"
    OUTPUT_NODE = True

    def save_images(self, images, filename, save_path, output_format, layer_names="", 
                   include_merged=True, merge_mode="maximum", quality=95, 
                   add_timestamp=False, save_metadata=True, create_subfolder=False,
                   compression_level=6, preserve_transparency=True, auto_optimize=True):
        
        # Créer le dossier de sortie avec structure intelligente
        final_save_path = self._create_save_path(save_path, filename, create_subfolder, add_timestamp)
        os.makedirs(final_save_path, exist_ok=True)
        
        # Générer le nom de fichier final
        final_filename = self._generate_filename(filename, add_timestamp)
        
        # Parser et valider les noms de calques
        layer_name_list = self._parse_layer_names(layer_names, len(images))
        
        # Initialiser les métadonnées complètes
        metadata = self._init_metadata(output_format, include_merged, merge_mode, 
                                     quality, compression_level, len(images))
        
        saved_files = []
        
        # Sauvegarder chaque calque avec optimisations
        for i, img_tensor in enumerate(images):
            layer_info = self._save_single_layer(
                img_tensor, final_filename, layer_name_list[i], 
                final_save_path, output_format, quality, 
                compression_level, preserve_transparency, auto_optimize
            )
            saved_files.append(layer_info["path"])
            metadata["layers"].append(layer_info["metadata"])
        
        # Créer l'image fusionnée avec mode avancé
        if include_merged and len(images) > 1:
            merged_info = self._create_merged_image(
                images, final_filename, final_save_path, output_format,
                merge_mode, quality, compression_level, 
                preserve_transparency, auto_optimize
            )
            saved_files.append(merged_info["path"])
            metadata["merged_file"] = merged_info["metadata"]
        
        # Sauvegarder les métadonnées enrichies
        if save_metadata:
            metadata_path = self._save_metadata(metadata, final_filename, final_save_path)
            saved_files.append(metadata_path)
        
        # Générer le rapport de sauvegarde
        save_info = self._generate_save_report(saved_files, final_save_path, 
                                             output_format, merge_mode, include_merged)
        
        return (save_info, final_save_path)
    
    def _create_save_path(self, base_path, filename, create_subfolder, add_timestamp):
        """Créer la structure de dossiers intelligente"""
        if create_subfolder:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            subfolder_name = f"{filename}_{timestamp}" if add_timestamp else filename
            return os.path.join(base_path, subfolder_name)
        return base_path
    
    def _generate_filename(self, filename, add_timestamp):
        """Générer le nom de fichier avec horodatage optionnel"""
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{filename}_{timestamp}"
        return filename
    
    def _parse_layer_names(self, layer_names, num_images):
        """Parser et valider les noms de calques"""
        if layer_names.strip():
            layer_list = [name.strip() for name in layer_names.split(',') if name.strip()]
        else:
            layer_list = []
        
        # Compléter avec des noms par défaut si nécessaire
        while len(layer_list) < num_images:
            layer_list.append(f"Layer_{len(layer_list)+1}")
        
        return layer_list[:num_images]  # Limiter au nombre d'images
    
    def _init_metadata(self, output_format, include_merged, merge_mode, 
                      quality, compression_level, num_layers):
        """Initialiser les métadonnées complètes"""
        return {
            "creation_date": datetime.now().isoformat(),
            "comfyui_version": "0.3.35",
            "saver_plus_version": "1.0",
            "output_format": output_format,
            "settings": {
                "quality": quality if output_format in ["JPEG", "WEBP"] else None,
                "compression_level": compression_level,
                "merged_included": include_merged,
                "merge_mode": merge_mode if include_merged else None
            },
            "statistics": {
                "total_layers": num_layers,
                "total_files": 0  # Sera mis à jour
            },
            "layers": [],
            "merged_file": None
        }
    
    def _save_single_layer(self, img_tensor, filename, layer_name, save_path, 
                          output_format, quality, compression_level, 
                          preserve_transparency, auto_optimize):
        """Sauvegarder un calque avec optimisations spécifiques au format"""
        # Convertir le tensor en image PIL
        img_np = img_tensor.cpu().numpy()
        img_array = (img_np * 255).astype(np.uint8)
        
        # Gestion intelligente des canaux
        if img_array.shape[2] == 4 and preserve_transparency:
            pil_img = Image.fromarray(img_array, 'RGBA')
        else:
            pil_img = Image.fromarray(img_array[:,:,:3], 'RGB')
        
        # Nom de fichier final
        file_extension = self._get_file_extension(output_format)
        file_path = os.path.join(save_path, f"{filename}_{layer_name}.{file_extension}")
        
        # Options de sauvegarde optimisées par format
        save_kwargs = self._get_save_options(output_format, quality, compression_level, auto_optimize)
        
        # Conversion spéciale pour JPEG (pas de transparence)
        if output_format == "JPEG" and pil_img.mode == "RGBA":
            background = Image.new("RGB", pil_img.size, (255, 255, 255))
            background.paste(pil_img, mask=pil_img.split()[-1])
            pil_img = background
        
        # Sauvegarder avec gestion d'erreurs
        try:
            pil_img.save(file_path, output_format, **save_kwargs)
            file_size = os.path.getsize(file_path)
        except Exception as e:
            raise Exception(f"Erreur lors de la sauvegarde de {layer_name}: {str(e)}")
        
        return {
            "path": file_path,
            "metadata": {
                "name": layer_name,
                "filename": os.path.basename(file_path),
                "index": len(os.listdir(save_path)) - 1,
                "dimensions": [img_array.shape[1], img_array.shape[0]],  # width, height
                "channels": img_array.shape[2],
                "file_size_bytes": file_size,
                "color_mode": pil_img.mode
            }
        }
    
    def _create_merged_image(self, images, filename, save_path, output_format,
                           merge_mode, quality, compression_level, 
                           preserve_transparency, auto_optimize):
        """Créer l'image fusionnée avec modes avancés"""
        merged = self._merge_images_advanced(images, merge_mode)
        merged_array = (merged * 255).astype(np.uint8)
        
        # Créer l'image PIL
        if merged_array.shape[2] == 4 and preserve_transparency:
            merged_pil = Image.fromarray(merged_array, 'RGBA')
        else:
            merged_pil = Image.fromarray(merged_array[:,:,:3], 'RGB')
        
        # Nom de fichier fusionné
        file_extension = self._get_file_extension(output_format)
        merged_path = os.path.join(save_path, f"{filename}_merged.{file_extension}")
        
        # Options de sauvegarde
        save_kwargs = self._get_save_options(output_format, quality, compression_level, auto_optimize)
        
        # Conversion pour JPEG
        if output_format == "JPEG" and merged_pil.mode == "RGBA":
            background = Image.new("RGB", merged_pil.size, (255, 255, 255))
            background.paste(merged_pil, mask=merged_pil.split()[-1])
            merged_pil = background
        
        merged_pil.save(merged_path, output_format, **save_kwargs)
        file_size = os.path.getsize(merged_path)
        
        return {
            "path": merged_path,
            "metadata": {
                "filename": os.path.basename(merged_path),
                "dimensions": [merged_array.shape[1], merged_array.shape[0]],
                "channels": merged_array.shape[2],
                "file_size_bytes": file_size,
                "color_mode": merged_pil.mode
            }
        }
    
    def _merge_images_advanced(self, images, merge_mode):
        """Modes de fusion avancés"""
        if len(images) == 1:
            return images[0].cpu().numpy()
        
        np_images = [img.cpu().numpy() for img in images]
        base = np_images[0]
        
        for img in np_images[1:]:
            if merge_mode == "maximum":
                base = np.maximum(base, img)
            elif merge_mode == "average":
                base = (base + img) / 2
            elif merge_mode == "overlay":
                mask = base < 0.5
                base = np.where(mask, 2 * base * img, 1 - 2 * (1 - base) * (1 - img))
            elif merge_mode == "multiply":
                base = base * img
            elif merge_mode == "screen":
                base = 1 - (1 - base) * (1 - img)
            elif merge_mode == "soft_light":
                mask = img < 0.5
                base = np.where(mask, 
                              base - (1 - 2 * img) * base * (1 - base),
                              base + (2 * img - 1) * (np.sqrt(base) - base))
        
        return np.clip(base, 0, 1)
    
    def _get_file_extension(self, output_format):
        """Obtenir l'extension de fichier correcte"""
        extensions = {
            "PNG": "png", "TIFF": "tiff", "JPEG": "jpg", 
            "WEBP": "webp", "BMP": "bmp"
        }
        return extensions.get(output_format, "png")
    
    def _get_save_options(self, output_format, quality, compression_level, auto_optimize):
        """Options de sauvegarde optimisées par format"""
        options = {}
        
        if output_format == "PNG":
            options.update({
                "optimize": auto_optimize,
                "compress_level": compression_level
            })
        elif output_format == "JPEG":
            options.update({
                "quality": quality,
                "optimize": auto_optimize,
                "progressive": True
            })
        elif output_format == "WEBP":
            options.update({
                "quality": quality,
                "optimize": auto_optimize,
                "lossless": quality >= 95
            })
        elif output_format == "TIFF":
            options.update({
                "compression": "lzw",
                "optimize": auto_optimize
            })
        elif output_format == "BMP":
            pass  # BMP n'a pas d'options spéciales
        
        return options
    
    def _save_metadata(self, metadata, filename, save_path):
        """Sauvegarder les métadonnées enrichies"""
        # Mettre à jour les statistiques
        metadata["statistics"]["total_files"] = len(metadata["layers"])
        if metadata["merged_file"]:
            metadata["statistics"]["total_files"] += 1
        
        metadata_path = os.path.join(save_path, f"{filename}_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return metadata_path
    
    def _generate_save_report(self, saved_files, save_path, output_format, merge_mode, include_merged):
        """Générer un rapport de sauvegarde détaillé"""
        total_size = sum(os.path.getsize(f) for f in saved_files if os.path.exists(f))
        size_mb = total_size / (1024 * 1024)
        
        report = f"✅ **SaverPlus - Sauvegarde terminée**\n"
        report += f"📁 **Dossier**: {save_path}\n"
        report += f"📄 **Format**: {output_format}\n"
        report += f"📊 **Fichiers**: {len(saved_files)} ({size_mb:.2f} MB)\n"
        
        if include_merged:
            report += f"🔄 **Fusion**: {merge_mode}\n"
        
        report += f"⏰ **Heure**: {datetime.now().strftime('%H:%M:%S')}"
        
        return report
