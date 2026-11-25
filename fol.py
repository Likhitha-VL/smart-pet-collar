import folium
import random
 

def create_map(lat,long):
    # Example latitude and longitude values (replace with your actual values)
    latitude = 12.9296  # Example: San Francisco latitude
    longitude = 77.6225  # Example: San Francisco longitude

    # Create a Folium map centered at the given latitude and longitude
    m = folium.Map(location=[latitude, longitude], zoom_start=15)

    # Add a marker for the current location
    folium.Marker(
        location=[latitude, longitude],
        popup="Current Location",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

    # Simulate nearby pet clinic locations (randomly generated)
    num_clinics = 5  # Number of nearby clinics to display
    for _ in range(num_clinics):
        # Generate random nearby coordinates (within a small radius)
        clinic_lat = latitude + random.uniform(-0.01, 0.01)
        clinic_lon = longitude + random.uniform(-0.01, 0.01)
        
        # Add a marker for each clinic
        folium.Marker(
            location=[clinic_lat, clinic_lon],
            popup="Pet Clinic",
            icon=folium.Icon(color="green", icon="paw")
        ).add_to(m)

    # Save the map to an HTML file
    m.save("static/map.html")

    # Display the map in a Jupyter Notebook (if using Jupyter)
    m