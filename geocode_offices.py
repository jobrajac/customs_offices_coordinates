import os
import pandas as pd
import googlemaps
from dotenv import load_dotenv
import time

def load_csv(filename):
    """Load the CSV file into a pandas DataFrame."""
    return pd.read_csv(filename)

def geocode_address(gmaps_client, row):
    """
    Geocode an address using Google Maps API.
    Returns a tuple of (latitude, longitude).
    """
    # Construct the full address
    address_parts = [
        str(row['street_and_address']),
        str(row['postcode']),
        str(row['city']),
        str(row['country'])
    ]
    address = ', '.join(part for part in address_parts if part and part.lower() != 'nan')
    
    try:
        # Add a small delay to respect API rate limits
        time.sleep(0.1)
        
        # Get geocoding result
        result = gmaps_client.geocode(address)
        
        if result and len(result) > 0:
            location = result[0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"No results found for address: {address}")
            return None, None
    except Exception as e:
        print(f"Error geocoding address {address}: {str(e)}")
        return None, None

def main():
    input_file = 'customs_offices.csv'
    output_file = 'customs_offices_geocoded.csv'
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Please run create_offices_csv.py first.")
        return
    
    # Load environment variables
    load_dotenv()
    
    # Get Google Maps API key
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        raise ValueError("Please set the GOOGLE_MAPS_API_KEY environment variable")
    
    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=api_key)
    
    # Load the CSV file
    print(f"Loading {input_file}...")
    df = load_csv(input_file)
    print(f"Found {len(df)} offices to process")
    
    # Process each row
    print("\nStarting geocoding process...")
    for index, row in df.iterrows():
        # Skip if coordinates already exist
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            continue
            
        print(f"\nProcessing office: {row['customs_office_id']}")
        print(f"Address: {row['street_and_address']}, {row['postcode']}, {row['city']}, {row['country']}")
        
        # Geocode the address
        lat, lng = geocode_address(gmaps, row)
        
        # Update the DataFrame
        df.at[index, 'latitude'] = lat
        df.at[index, 'longitude'] = lng
        
        if lat and lng:
            print(f"Found coordinates: {lat}, {lng}")
        else:
            print("No coordinates found")
        
        # Save progress every 10 offices
        if index % 10 == 0:
            df.to_csv(output_file, index=False)
            print(f"Progress saved to {output_file}")
    
    # Save final results
    df.to_csv(output_file, index=False)
    
    # Print statistics
    total_offices = len(df)
    offices_with_coords = len(df[df['latitude'].notna()])
    print(f"\nGeocoding complete!")
    print(f"Results saved to {output_file}")
    print(f"\nStatistics:")
    print(f"Total offices: {total_offices}")
    print(f"Offices with coordinates: {offices_with_coords}")
    print(f"Coverage: {offices_with_coords/total_offices*100:.1f}%")

if __name__ == "__main__":
    main() 