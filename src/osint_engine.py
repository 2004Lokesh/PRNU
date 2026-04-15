import os
import exifread
import folium
import requests

def _convert_to_degrees(value):
    try:
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)
        return d + (m / 60.0) + (s / 3600.0)
    except:
        return None

def get_weather_description(code):
    weatherDict = {
        0: 'Sunny / Clear sky',
        1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
        45: 'Fog', 48: 'Depositing rime fog',
        51: 'Light Drizzle', 53: 'Moderate Drizzle', 55: 'Dense Drizzle',
        56: 'Light Freezing Drizzle', 57: 'Dense Freezing Drizzle',
        61: 'Slight Rain', 63: 'Moderate Rain', 65: 'Heavy Rain',
        66: 'Light Freezing Rain', 67: 'Heavy Freezing Rain',
        71: 'Slight Snow', 73: 'Moderate Snow', 75: 'Heavy Snow',
        77: 'Snow grains',
        80: 'Slight Rain Showers', 81: 'Moderate Rain Showers', 82: 'Violent Rain Showers',
        85: 'Slight Snow Showers', 86: 'Heavy Snow Showers',
        95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail'
    }
    return weatherDict.get(code, f"Unknown ({code})")

def analyze(image_path):
    alerts = []
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
            
        if not tags:
            alerts.append({"severity": "medium", "module": "Metadata", "finding": "No EXIF metadata found. The image metadata has been completely stripped or is unsupported."})
        else:
            # Extract basic visible metadata
            make = tags.get('Image Make', 'Unknown')
            model = tags.get('Image Model', 'Unknown')
            date = tags.get('EXIF DateTimeOriginal', tags.get('Image DateTime', 'Unknown'))
            dims = f"{tags.get('EXIF ExifImageWidth', 'Unknown')}x{tags.get('EXIF ExifImageLength', 'Unknown')}"
            
            basic_info = []
            if str(make) != 'Unknown' or str(model) != 'Unknown':
                basic_info.append(f"Camera: {make} {model}".strip())
            if str(date) != 'Unknown':
                basic_info.append(f"Date: {date}")
            if dims != 'UnknownxUnknown':
                basic_info.append(f"Dimensions: {dims}")
                
            if basic_info:
                alerts.append({"severity": "info", "module": "Metadata", "finding": f"Basic EXIF data recovered: {' | '.join(basic_info)}"})
            else:
                 alerts.append({"severity": "low", "module": "Metadata", "finding": f"Some EXIF tags present but core fields (Camera/Date) are missing. Found {len(tags)} raw tags."})

            software = tags.get('Image Software', '')
            if software and any(sw in str(software).lower() for sw in ['adobe', 'photoshop', 'gimp']):
                alerts.append({"severity": "high", "module": "Metadata", "finding": f"Image editing software signature found: {software}"})
            else:
                 if software:
                     alerts.append({"severity": "info", "module": "Metadata", "finding": f"Software signature found: {software}."})
            
            gps_lat = tags.get('GPS GPSLatitude')
            gps_lat_ref = tags.get('GPS GPSLatitudeRef')
            gps_lon = tags.get('GPS GPSLongitude')
            gps_lon_ref = tags.get('GPS GPSLongitudeRef')

            if gps_lat and gps_lat_ref and gps_lon and gps_lon_ref:
                lat = _convert_to_degrees(gps_lat)
                lon = _convert_to_degrees(gps_lon)
                
                if lat is not None and lon is not None:
                    if str(gps_lat_ref.values) != 'N':
                        lat = 0 - lat
                    if str(gps_lon_ref.values) != 'E':
                        lon = 0 - lon
                        
                    alerts.append({"severity": "medium", "module": "OSINT", "finding": f"GPS Coordinates exposed: {lat:.6f}, {lon:.6f}"})
                    
                    m = folium.Map(location=[lat, lon], zoom_start=12)
                    folium.Marker([lat, lon], popup='Image Map Location').add_to(m)
                    map_file = "gps_map.html"
                    m.save(map_file)
                    alerts.append({"severity": "info", "module": "OSINT", "finding": f"GPS map saved to {map_file}"})
                    
                    # Fetch Weather Data (from Jayant's implementation logic)
                    if str(date) != 'Unknown':
                        try:
                            # Format date: "YYYY:MM:DD HH:MM:SS" -> "YYYY-MM-DD" "HH"
                            parts = str(date).strip().split(' ')
                            if len(parts) >= 2:
                                ymd = parts[0].replace(':', '-')
                                hour = parts[1].split(':')[0]
                                
                                # Call Open-Meteo
                                weather_url = f"https://archive-api.open-meteo.com/v1/era5?latitude={lat}&longitude={lon}&start_date={ymd}&end_date={ymd}&hourly=weathercode&timezone=auto"
                                w_res = requests.get(weather_url).json()
                                
                                if 'hourly' in w_res and 'weathercode' in w_res['hourly']:
                                    code = w_res['hourly']['weathercode'][int(hour)]
                                    if code is not None:
                                        weather_desc = get_weather_description(code)
                                        alerts.append({"severity": "info", "module": "OSINT (Weather)", "finding": f"Historical weather at location on {ymd} at {hour}:00 was: {weather_desc}"})
                                    else:
                                        alerts.append({"severity": "low", "module": "OSINT (Weather)", "finding": f"Could not determine historical weather for hour {hour}:00."})
                        except Exception as we:
                            alerts.append({"severity": "warning", "module": "OSINT (Weather)", "finding": f"Failed to fetch historical weather: {str(we)}"})
                    else:
                        alerts.append({"severity": "low", "module": "OSINT (Weather)", "finding": "Historical Weather Analysis skipped: Missing Date parameter in EXIF."})
                else:
                    alerts.append({"severity": "low", "module": "OSINT (Weather)", "finding": "Historical Weather Analysis skipped: Invalid GPS coordinates in EXIF."})
            else:
                alerts.append({"severity": "low", "module": "OSINT (Weather)", "finding": "Historical Weather Analysis skipped: Missing GPS coordinates in the image EXIF metadata."})
    except Exception as e:
        alerts.append({"severity": "error", "module": "Metadata", "finding": f"Error parsing metadata: {str(e)}"})

    # SerpApi reverse image search
    try:
        # First upload the image temporarily to get a public URL for Google Lens
        with open(image_path, "rb") as f:
            upload_res = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f})
        
        if upload_res.status_code == 200:
            public_url = upload_res.text.strip()
            # Call SerpApi Google Lens
            serpapi_key = "8bf9d77a15fabea7c77a10aa5c507bbf8764b71fb750986eca62d161c884edf7"
            serp_url = f"https://serpapi.com/search?engine=google_lens&url={public_url}&api_key={serpapi_key}"
            serp_res = requests.get(serp_url).json()
            
            matches = serp_res.get("visual_matches", [])
            if matches:
                 top_matches = [m.get('title', 'Unknown') for m in matches[:3]]
                 alerts.append({"severity": "info", "module": "OSINT (SerpApi)", "finding": f"Reverse image search matches found: {', '.join(top_matches)}"})
            else:
                 alerts.append({"severity": "low", "module": "OSINT (SerpApi)", "finding": "No significant visual matches found via Reverse Image Search."})
        else:
             alerts.append({"severity": "warning", "module": "OSINT (SerpApi)", "finding": "Failed to upload image for reverse search."})
             
    except Exception as e:
        alerts.append({"severity": "error", "module": "OSINT (SerpApi)", "finding": f"Error during Reverse Image Search: {str(e)}"})
    
    return alerts
