import os
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import pywt

def run_ela(image_path, quality=90):
    try:
        tmp_img = "tmp_ela.jpg"
        im = Image.open(image_path).convert('RGB')
        im.save(tmp_img, 'JPEG', quality=quality)
        
        saved_im = Image.open(tmp_img)
        ela_im = ImageChops.difference(im, saved_im)
        
        extrema = ela_im.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
        scale = 255.0 / max_diff
        
        ela_im = ImageEnhance.Brightness(ela_im).enhance(scale)
        os.remove(tmp_img)
        
        ela_array = np.array(ela_im)
        ela_std = np.std(ela_array)
        
        ela_map_file = "ela_map.jpg"
        ela_data_file = "ela_data.npy"
        ela_viz = cv2.normalize(ela_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        ela_gray = cv2.cvtColor(ela_viz, cv2.COLOR_RGB2GRAY) if len(ela_viz.shape) == 3 else ela_viz
        ela_grid = cv2.resize(ela_gray, (24, 24), interpolation=cv2.INTER_AREA)
        np.save(ela_data_file, ela_grid)
        
        ela_heatmap = cv2.applyColorMap(ela_gray, cv2.COLORMAP_JET)
        
        color_im = cv2.imread(image_path)
        if color_im is not None:
             overlay = cv2.addWeighted(color_im, 0.5, ela_heatmap, 0.5, 0)
             cv2.imwrite(ela_map_file, overlay)
        else:
             cv2.imwrite(ela_map_file, ela_heatmap)
        
        if ela_std > 10.0:
            return {"severity": "high", "module": "ELA", "finding": f"Inconsistent compression detected (ELA standard deviation: {ela_std:.2f}). Map saved.", "visual_map": ela_map_file, "heatmap_data": ela_data_file}
        else:
            return {"severity": "low", "module": "ELA", "finding": "No significant compression inconsistencies detected.", "visual_map": ela_map_file, "heatmap_data": ela_data_file}
            
    except Exception as e:
         return {"severity": "error", "module": "ELA", "finding": f"Error during ELA analysis: {e}"}

def run_prnu(image_path):
    try:
        im = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if im is None:
            return {"severity": "error", "module": "PRNU", "finding": "Could not read image for PRNU extraction."}
        
        # Haar wavelet transform for noise extraction
        coeffs = pywt.dwt2(im, 'haar')
        cA, (cH, cV, cD) = coeffs
        
        noise_energy = np.mean(cH**2) + np.mean(cV**2) + np.mean(cD**2)
        
        prnu_map_file = "prnu_map.jpg"
        prnu_data_file = "prnu_data.npy"
        # Normalize and save the PRNU map as a Heatmap overlay
        prnu_viz = np.abs(cH) + np.abs(cV) + np.abs(cD)
        prnu_viz = cv2.normalize(prnu_viz, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        prnu_grid = cv2.resize(prnu_viz, (24, 24), interpolation=cv2.INTER_AREA)
        np.save(prnu_data_file, prnu_grid)
        
        prnu_viz_resized = cv2.resize(prnu_viz, (im.shape[1], im.shape[0]))
        prnu_heatmap = cv2.applyColorMap(prnu_viz_resized, cv2.COLORMAP_JET)
        
        color_im = cv2.imread(image_path)
        if color_im is not None:
             overlay = cv2.addWeighted(color_im, 0.5, prnu_heatmap, 0.5, 0)
             cv2.imwrite(prnu_map_file, overlay)
        else:
             cv2.imwrite(prnu_map_file, prnu_heatmap)
        
        if noise_energy > 500: # Threshold for anomaly
            return {"severity": "medium", "module": "PRNU", "finding": f"Anomalous high sensor noise patterns detected (Energy: {noise_energy:.2f}). Map saved.", "visual_map": prnu_map_file, "heatmap_data": prnu_data_file}
        else:
            return {"severity": "low", "module": "PRNU", "finding": f"Normal PRNU noise patterns (Energy: {noise_energy:.2f}). Map saved.", "visual_map": prnu_map_file, "heatmap_data": prnu_data_file}
    except Exception as e:
        return {"severity": "error", "module": "PRNU", "finding": f"Error during PRNU analysis: {e}"}

def run_shadow_luminance(image_path):
    try:
        im = cv2.imread(image_path)
        if im is None:
             return {"severity": "error", "module": "Shadow/Luminance", "finding": "Could not read image for shadow analysis."}
        
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        magnitude = cv2.magnitude(grad_x, grad_y)
        mean_mag = np.mean(magnitude)
        
        luminance_map_file = "luminance_map.jpg"
        lum_data_file = "luminance_data.npy"
        mag_viz = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        lum_grid = cv2.resize(mag_viz, (24, 24), interpolation=cv2.INTER_AREA)
        np.save(lum_data_file, lum_grid)
        
        lum_heatmap = cv2.applyColorMap(mag_viz, cv2.COLORMAP_JET)
        
        color_im = cv2.imread(image_path)
        if color_im is not None:
             lum_overlay = cv2.addWeighted(color_im, 0.4, lum_heatmap, 0.6, 0)
             cv2.imwrite(luminance_map_file, lum_overlay)
        else:
             cv2.imwrite(luminance_map_file, lum_heatmap)
        
        if mean_mag < 10.0:
            return {"severity": "medium", "module": "Shadow/Luminance", "finding": f"Unnaturally smooth luminance gradients (Magnitude: {mean_mag:.2f}). Potential airbrushing or GAN generation. Map saved.", "visual_map": luminance_map_file, "heatmap_data": lum_data_file}
        return {"severity": "low", "module": "Shadow/Luminance", "finding": f"Natural shadow and luminance gradients detected (Magnitude: {mean_mag:.2f}). Map saved.", "visual_map": luminance_map_file, "heatmap_data": lum_data_file}
    except Exception as e:
         return {"severity": "error", "module": "Shadow/Luminance", "finding": str(e)}

def run_jpeg_ghost(image_path):
    try:
        tmp_img = "tmp_ghost.jpg"
        ghost_map_file = "ghost_map.jpg"
        ghost_data_file = "ghost_data.npy"
        im = Image.open(image_path).convert('RGB')
        
        # Test qualities to find ghosting anomalies (typically tampered areas have different compression)
        im.save(tmp_img, 'JPEG', quality=60)
        im_60 = Image.open(tmp_img)
        diff_im = ImageChops.difference(im, im_60)
        os.remove(tmp_img)
        
        diff_array = np.array(diff_im)
        avg_diff = np.mean(diff_array)
        
        # Normalize diff and save as heatmap
        diff_viz = cv2.normalize(diff_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        if len(diff_viz.shape) == 3:
             diff_gray = cv2.cvtColor(diff_viz, cv2.COLOR_RGB2GRAY)
        else:
             diff_gray = diff_viz
             
        ghost_grid = cv2.resize(diff_gray, (24, 24), interpolation=cv2.INTER_AREA)
        np.save(ghost_data_file, ghost_grid)
        
        ghost_heatmap = cv2.applyColorMap(diff_gray, cv2.COLORMAP_JET)
        
        color_im = cv2.imread(image_path)
        if color_im is not None:
             ghost_overlay = cv2.addWeighted(color_im, 0.5, ghost_heatmap, 0.5, 0)
             cv2.imwrite(ghost_map_file, ghost_overlay)
        else:
             cv2.imwrite(ghost_map_file, ghost_heatmap)
        
        if avg_diff > 12.0:
            return {"severity": "high", "module": "JPEG Ghost", "finding": f"Possible double quantization detected (Avg Diff: {avg_diff:.2f}). Spliced regions might compress differently.", "visual_map": ghost_map_file, "heatmap_data": ghost_data_file}
        return {"severity": "low", "module": "JPEG Ghost", "finding": f"Normal JPEG compression consistency (Avg Diff: {avg_diff:.2f}). Map saved.", "visual_map": ghost_map_file, "heatmap_data": ghost_data_file}
    except Exception as e:
         return {"severity": "error", "module": "JPEG Ghost", "finding": f"Error running JPEG Ghost: {e}"}

def analyze(image_path):
    alerts = []
    alerts.append(run_ela(image_path))
    alerts.append(run_prnu(image_path))
    alerts.append(run_shadow_luminance(image_path))
    alerts.append(run_jpeg_ghost(image_path))
    return alerts
