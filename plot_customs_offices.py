import pandas as pd
import folium
from folium import plugins
import os

def create_map(data):
    """Create an interactive map with customs offices locations."""
    
    # Calculate the center of the map (mean of all coordinates)
    center_lat = data['latitude'].mean()
    center_lon = data['longitude'].mean()
    
    # Create a map centered on the mean position
    m = folium.Map(location=[center_lat, center_lon], 
                  zoom_start=4,
                  tiles='CartoDB positron')  # Light theme map
    
    # Add a fullscreen option
    plugins.Fullscreen().add_to(m)
    
    # Add markers for each customs office
    for idx, row in data.iterrows():
        # Create popup content
        popup_content = f"""
            <b>{row['name']}</b><br>
            ID: {row['customs_office_id']}<br>
            Address: {row['street_and_address']}<br>
            {row['postcode']} {row['city']}<br>
            Country: {row['country']}
        """
        
        # Add marker with popup
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=row['name'],
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
    
    return m


def main():
    try:
        input_file = 'customs_offices_geocoded.csv'
        output_html = 'customs_offices_map.html'
        
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found.")
            print("Please run geocode_offices.py first to generate the coordinates file.")
            return
        
        # Read the CSV file
        print("Reading customs offices data...")
        df = pd.read_csv(input_file)
        
        # Remove rows with missing coordinates
        df_clean = df.dropna(subset=['latitude', 'longitude'])
        
        print(f"Found {len(df_clean)} offices with valid coordinates out of {len(df)} total offices")
        
        if len(df_clean) == 0:
            print("No valid coordinates found in the data!")
            return
        
        # Create the map
        print("Creating map...")
        m = create_map(df_clean)
        
        # Save the interactive HTML map
        m.save(output_html)
        print(f"\nMap has been created successfully!")
        print(f"Open '{output_html}' in your web browser to view the interactive map")
        
        # Print some statistics
        print(f"\nStatistics by country:")
        country_stats = df_clean.groupby('country').size().sort_values(ascending=False)
        print(country_stats)
      
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main() 