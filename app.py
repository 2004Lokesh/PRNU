import streamlit as st
import json
import os
from PIL import Image
import base64
import time

# Ensure src modules can be imported
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src import core

# --- Configuration & Theming ---
st.set_page_config(page_title="Forensic Event Engine Dashboard", layout="wide", page_icon="🕵️")

def inject_custom_css():
    try:
        bg_path = os.path.join(os.path.dirname(__file__), 'modern_bg.png')
        if os.path.exists(bg_path):
            with open(bg_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            bg_image_url = f"data:image/png;base64,{encoded_string}"
        else:
            bg_image_url = ""
    except Exception:
        bg_image_url = ""

    custom_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Roboto+Mono:wght@400;700&display=swap');

    html, body, [class*="css"]  {{
        font-family: 'Inter', sans-serif !important;
        color: #e2e8f0 !important;
    }}
    
    .stApp {{
        background-color: #0f172a !important;
        background-image: url("{bg_image_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(15, 23, 42, 0.85);
        z-index: -1;
    }}

    div[data-testid="metric-container"] {{
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        padding: 15px !important;
        border-radius: 8px !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), inset 0 0 10px rgba(0, 229, 255, 0.1) !important;
    }}
    
    div[data-testid="stMetricValue"] {{
        color: #00e5ff !important;
        font-family: 'Roboto Mono', monospace !important;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.5) !important;
    }}
    div[data-testid="stMetricLabel"] {{
        color: #94a3b8 !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .alert-high {{
        background: rgba(220, 38, 38, 0.15);
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 15px;
        border-left: 4px solid #ef4444;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.2);
        color: #fca5a5;
    }}
    .alert-medium, .alert-warning {{
        background: rgba(245, 158, 11, 0.15);
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 15px;
        border-left: 4px solid #f59e0b;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
        color: #fcd34d;
    }}
    .alert-low, .alert-info {{
        background: rgba(14, 165, 233, 0.15);
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 15px;
        border-left: 4px solid #0ea5e9;
        box-shadow: 0 0 15px rgba(14, 165, 233, 0.2);
        color: #7dd3fc;
    }}
    .alert-error {{
        background: rgba(153, 27, 27, 0.3);
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 15px;
        border-left: 4px solid #b91c1c;
        color: #f87171;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Inter', sans-serif !important;
        color: #f8fafc !important;
        font-weight: 800;
        letter-spacing: 0.5px;
    }}
    
    h1 {{
        text-shadow: 0 0 15px rgba(0, 229, 255, 0.3) !important;
    }}
    
    .stMarkdown p {{
        font-size: 15px;
        color: #cbd5e1;
        font-family: 'Inter', sans-serif;
    }}

    .stButton > button {{
        background: rgba(15, 23, 42, 0.8) !important;
        color: #00e5ff !important;
        border: 1px solid rgba(0, 229, 255, 0.5) !important;
        transition: all 0.2s ease !important;
        text-transform: uppercase !important;
        font-weight: 600;
        font-family: 'Roboto Mono', monospace !important;
        letter-spacing: 1px;
        border-radius: 4px !important;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.1);
    }}
    .stButton > button:hover {{
        background: rgba(0, 229, 255, 0.1) !important;
        border-color: #00e5ff !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.4) !important;
        color: #ffffff !important;
        transform: translateY(-1px);
    }}

    .hover-zoom-container {{
        overflow: hidden;
        display: inline-block;
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 6px;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        background: rgba(15, 23, 42, 0.8);
    }}
    
    .hover-zoom-container img {{
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        display: block;
        max-width: 100%;
        opacity: 0.95;
    }}
    
    .hover-zoom-container img:hover {{
        transform: scale(1.3);
        z-index: 10;
        cursor: zoom-in;
        opacity: 1;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: rgba(15, 23, 42, 0.9) !important;
        border-right: 1px solid rgba(0, 229, 255, 0.1) !important;
    }}
    
    [data-testid="stFileUploadDropzone"] {{
        background-color: rgba(0, 0, 0, 0.2) !important;
        border: 1px dashed rgba(0, 229, 255, 0.4) !important;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# --- Helper Functions ---
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode('utf-8')
    return b64_string

def display_zoomable_image(image_path, caption=""):
    try:
        b64_img = get_image_base64(image_path)
        img_html = f'''
        <div style="text-align: center;">
            <div class="hover-zoom-container">
                <img src="data:image/jpeg;base64,{b64_img}" alt="{caption}" style="max-height: 400px; object-fit: contain;"/>
            </div>
            <p style="font-style: italic; color: #666; font-size: 0.9em; margin-top: 5px;">{caption}</p>
        </div>
        '''
        st.markdown(img_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading image: {e}")

# --- Main App ---
def main():
    inject_custom_css()
    
    st.title("🛡️ Image Forensics SIEM Dashboard")
    st.markdown("---")

    # --- Sidebar: Case Management ---
    with st.sidebar:
        st.header("📂 Case Management")
        uploaded_file = st.file_uploader("Upload Evidence Image", type=["jpg", "jpeg", "png", "webp"])
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_dir = "temp_evidence"
            os.makedirs(temp_dir, exist_ok=True)
            file_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            st.success(f"Loaded: {uploaded_file.name}")
            
            # Display thumbnail
            st.image(file_path, caption="Evidence Subject", use_container_width=True)
            
            if st.button("🚀 Run Forensic Analysis", use_container_width=True):
                with st.spinner("Executing Forensic Event Engine..."):
                    # Trigger the backend pipeline
                    try:
                        report_file = core.analyze_image(file_path)
                        # Simulate a slight delay for dashboard loading feel
                        time.sleep(1)
                        st.session_state['report_path'] = report_file
                        st.session_state['image_path'] = file_path
                        st.success("Analysis Complete!")
                    except Exception as e:
                         st.error(f"Engine Error: {e}")

    # --- Main Dashboard Area ---
    if 'report_path' in st.session_state and os.path.exists(st.session_state['report_path']):
        
        # Load the report
        with open(st.session_state['report_path'], 'r') as f:
            try:
                # Need to handle case where core returns nested lists or flat lists depending on module
                raw_alerts = json.load(f)
                
                # Flatten the list if modules returned lists of dicts
                alerts = []
                for item in raw_alerts:
                     if isinstance(item, list):
                          alerts.extend(item)
                     elif isinstance(item, dict):
                          alerts.append(item)
                     else:
                          alerts.append({"severity": "error", "module": "System", "finding": f"Unknown format: {item}"})
                
            except json.JSONDecodeError:
                st.error("Failed to parse report.json")
                return

        # --- Metrics Dashboard ---
        st.subheader("📊 Executive Summary")
        
        total_alerts = len(alerts)
        high_alerts = sum(1 for a in alerts if a.get('severity', '').lower() == 'high')
        med_alerts = sum(1 for a in alerts if a.get('severity', '').lower() in ['medium', 'warning'])
        
        # Extract AI Confidence Score if present
        ai_confidence = "N/A"
        for a in alerts:
            if a.get('module') == 'AI Engine' and 'Confidence:' in a.get('finding', ''):
                try:
                    # Very simple parsing, assuming format "Confidence: 0.95"
                    finding_str = a['finding']
                    ai_confidence = finding_str.split('Confidence:')[1].strip()
                    break
                except:
                    pass

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Findings", total_alerts)
        col2.metric("Critical Anomalies", high_alerts, delta_color="inverse")
        col3.metric("Warnings", med_alerts, delta_color="inverse")
        col4.metric("AI Confidence", ai_confidence)
        
        st.markdown("---")

        # --- Visual Evidence ---
        st.subheader("👁️ Visual Evidence Analysis")
        display_zoomable_image(st.session_state['image_path'], "Hover to magnify original evidence")
        
        st.markdown("---")

        # --- Alert Timeline ---
        st.subheader("📜 Forensic Alert Timeline")
        
        # We simulate a timeline by displaying expanders for different engines/severities
        
        # Create a container for the logs
        log_container = st.container()
        
        with log_container:
            for alert in alerts:
                severity = alert.get('severity', 'info').lower()
                module = alert.get('module', 'Unknown')
                finding = alert.get('finding', 'No details provided.')
                
                # Determine CSS class based on severity
                if severity == 'high':
                    css_class = 'alert-high'
                    icon = "🚨"
                elif severity in ['medium', 'warning']:
                    css_class = 'alert-medium'
                    icon = "⚠️"
                elif severity == 'error':
                    css_class = 'alert-error'
                    icon = "❌"
                else:
                    css_class = 'alert-low'
                    icon = "ℹ️"
                
                # Construct HTML for the alert text
                alert_html = f"""
                <div class="{css_class}">
                    <strong style="color: inherit;">{icon} [{module.upper()}] - {severity.upper()}</strong><br>
                    <span style="color: inherit;">{finding}</span>
                </div>
                """
                st.markdown(alert_html, unsafe_allow_html=True)
                
                # Render heatmap overlays (like Amped Authenticate) if they exist
                if 'visual_map' in alert and os.path.exists(alert['visual_map']):
                     with st.expander(f"🔍 Inspect {module.upper()} Overlay"):
                          col_orig, col_map = st.columns(2)
                          with col_orig:
                              display_zoomable_image(st.session_state['image_path'], "Original Evidence")
                          with col_map:
                              display_zoomable_image(alert['visual_map'], f"Overlay Analysis for {module}")
                
                # If OSINT map is referenced, provide a way to see it
                if module == 'OSINT' and 'map saved' in finding.lower():
                     if os.path.exists('gps_map.html'):
                          with st.expander("📍 View OSINT GPS Coordinates Map"):
                               with open('gps_map.html', 'r') as map_f:
                                    html_data = map_f.read()
                                    st.components.v1.html(html_data, height=400)
                                    
        # --- Interactive Plotly Heatmaps ---
        import numpy as np
        try:
             import plotly.express as px
             heatmap_alerts = [a for a in alerts if 'heatmap_data' in a and os.path.exists(a['heatmap_data'])]
             if heatmap_alerts:
                 st.markdown("---")
                 st.markdown("<h2 style='color: #00e5ff; margin-bottom: 20px;'>🔥 FORGERY HEATMAP</h2>", unsafe_allow_html=True)
                 for alert in heatmap_alerts:
                     mod_name = alert.get('module', 'Unknown').upper()
                     st.markdown(f"<h3 style='text-align: center; color: white; margin-top: 10px;'>{mod_name} Consistency Map</h3>", unsafe_allow_html=True)
                     h_data = np.load(alert['heatmap_data'])
                     
                     fig = px.imshow(h_data, color_continuous_scale="inferno", aspect="auto")
                     fig.update_layout(
                         margin=dict(l=0, r=0, t=10, b=0),
                         coloraxis_showscale=True,
                         xaxis_showticklabels=False,
                         yaxis_showticklabels=False,
                         plot_bgcolor='rgba(0,0,0,0)',
                         paper_bgcolor='rgba(0,0,0,0)'
                     )
                     st.plotly_chart(fig, use_container_width=True)
                     
                     if mod_name == "PRNU":
                         st.markdown("<p style='font-size: 13px; font-style: italic; color: #cbd5e1; text-align: center;'>Darker/Black regions indicate consistent PRNU. Bright/Colored spots may indicate tampering.</p>", unsafe_allow_html=True)
                     else:
                         st.markdown(f"<p style='font-size: 13px; font-style: italic; color: #cbd5e1; text-align: center;'>Darker/Black regions indicate normal {mod_name} levels. Bright spots indicate anomalies.</p>", unsafe_allow_html=True)
        except ImportError:
             pass
        
    else:
        # Default empty state
        st.info("👈 Upload an image in the Case Management sidebar to begin analysis.")
        
        # Display some placeholder structure
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Findings", "--")
        col2.metric("Critical Anomalies", "--")
        col3.metric("Warnings", "--")
        col4.metric("AI Confidence", "--")

if __name__ == "__main__":
    main()
