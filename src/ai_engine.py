import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

def analyze(image_path):
    alerts = []
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        im = Image.open(image_path).convert('RGB')
        
        # 1. General GenAI Detection (SDXL/Stable Diffusion/Midjourney)
        try:
            model_name = "Organika/sdxl-detector"
            processor = AutoImageProcessor.from_pretrained(model_name)
            model = AutoModelForImageClassification.from_pretrained(model_name).to(device)
            if device == "cuda":
                model = model.half()
                
            inputs = processor(images=im, return_tensors="pt")
            if device == "cuda":
                inputs = {k: v.to(device).half() for k, v in inputs.items()}
                
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                predicted_class_idx = logits.argmax(-1).item()
                confidence = torch.softmax(logits, dim=-1)[0][predicted_class_idx].item()
                
            label = model.config.id2label[predicted_class_idx]
            is_ai_suspect = any(word in label.lower() for word in ["ai", "artificial", "fake", "synthetic", "generated"])
            
            if is_ai_suspect or (model_name == "Organika/sdxl-detector" and label == "fake"):
                alerts.append({"severity": "high", "module": "AI Engine (GenAI)", "finding": f"High probability of AI Generation (Midjourney/SD) detected. Label: {label.upper()}, Confidence: {confidence:.2f}"})
            else:
                alerts.append({"severity": "low", "module": "AI Engine (GenAI)", "finding": f"Image appears natural relative to GenAI. Top match: {label.upper()} (Confidence: {confidence:.2f})"})
        except Exception as e:
            alerts.append({"severity": "warning", "module": "AI Engine (GenAI)", "finding": f"GenAI check failed to execute: {e}"})

        # 2. Deepfake Face / Swapping Detection
        try:
            df_model_name = "dima806/deepfake_vs_real_image_detection"
            df_processor = AutoImageProcessor.from_pretrained(df_model_name)
            df_model = AutoModelForImageClassification.from_pretrained(df_model_name).to(device)
            if device == "cuda":
                df_model = df_model.half()
                
            df_inputs = df_processor(images=im, return_tensors="pt")
            if device == "cuda":
                df_inputs = {k: v.to(device).half() for k, v in df_inputs.items()}
                
            with torch.no_grad():
                df_outputs = df_model(**df_inputs)
                df_logits = df_outputs.logits
                df_predicted_class_idx = df_logits.argmax(-1).item()
                df_confidence = torch.softmax(df_logits, dim=-1)[0][df_predicted_class_idx].item()
                
            df_label = df_model.config.id2label[df_predicted_class_idx]
            
            if "fake" in df_label.lower() or "deepfake" in df_label.lower():
                alerts.append({"severity": "high", "module": "AI Engine (Deepfake)", "finding": f"WARNING: Deepfake or Face-Swap detected! Model predicts {df_label.upper()} with Confidence: {df_confidence:.2f}"})
            else:
                alerts.append({"severity": "low", "module": "AI Engine (Deepfake)", "finding": f"No Deepfake patterns detected. Model predicts {df_label.upper()} with Confidence: {df_confidence:.2f}"})
        except Exception as e:
            alerts.append({"severity": "warning", "module": "AI Engine (Deepfake)", "finding": f"Deepfake face check failed to execute: {e}"})

    except Exception as e:
        alerts.append({"severity": "error", "module": "AI Engine", "finding": f"Fatal error in AI pipeline: {e}"})
        
    return alerts
