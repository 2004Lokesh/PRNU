import json
import os
import sys

# Ensure imports work regardless of how it's executed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import physics_engine
import ai_engine
import osint_engine

def analyze_image(image_path):
    print(f"Starting forensic analysis on: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Error: Image {image_path} not found.")
        return
        
    alerts = []
    
    print("Running Physics Engine (ELA, PRNU, Luminance)...")
    physics_alerts = physics_engine.analyze(image_path)
    alerts.extend(physics_alerts)
    
    print("Running AI Engine...")
    ai_alerts = ai_engine.analyze(image_path)
    alerts.extend(ai_alerts)
    
    print("Running OSINT Engine (Metadata, Reverse Search)...")
    osint_alerts = osint_engine.analyze(image_path)
    alerts.extend(osint_alerts)
    
    report_file = "report.json"
    with open(report_file, 'w') as f:
        json.dump(alerts, f, indent=4)
        
    print(f"Analysis complete. Report saved to {report_file}")
    return report_file

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_image(sys.argv[1])
    else:
        print("Usage: python -m src.core <image_path>")
