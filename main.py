from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from parse_customs_offices import parse_customs_offices
import csv
import time

def get_coordinates(geolocator, office):
    """Get coordinates for a customs office address with fallback to city and postcode."""
    def try_geocode(address):
        try:
            time.sleep(1)  # Rate limiting
            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude
            return None, None
        except (GeocoderTimedOut, GeocoderServiceError):
            print(f"Warning: Geocoding failed for address: {address}")
            return None, None

    # First attempt: Try with full address
    full_address = f"{office.street_and_address}, {office.postcode}, {office.country}"
    latitude, longitude = try_geocode(full_address)
    
    if latitude is not None and longitude is not None:
        print(f"Found coordinates using full address: {full_address}")
        return latitude, longitude
        
    # Second attempt: Try with city and postcode
    lsd_group = office.city  # Assuming we add city to the CustomsOffice class
    if lsd_group:
        city_postcode = f"{office.city}, {office.postcode}, {office.country}"
        print(f"Trying fallback with city and postcode: {city_postcode}")
        latitude, longitude = try_geocode(city_postcode)
        if latitude is not None and longitude is not None:
            print(f"Found coordinates using city and postcode: {city_postcode}")
            return latitude, longitude
    
    print(f"Could not find coordinates for office {office.customs_office_id}")
    return None, None

def main():
    try:
        # Initialize the geocoder
        geolocator = Nominatim(user_agent="customs_offices_app")
        
        # Parse customs offices
        print("Parsing customs offices XML file...")
        offices = parse_customs_offices('RD_ICS2_CustomsOffices.xml')
        print(f"Found {len(offices)} customs offices")
        
        # Prepare CSV file
        csv_filename = 'customs_offices_coordinates.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['customs_office_id', 'name', 'country', 'street_and_address', 
                           'postcode', 'city', 'latitude', 'longitude'])
            
            # Process each office
            for i, office in enumerate(offices, 1):
                print(f"\nProcessing office {i}/{len(offices)}: {office.customs_office_id}")
                
                # Get coordinates
                latitude, longitude = get_coordinates(geolocator, office)
                
                # Write to CSV
                writer.writerow([
                    office.customs_office_id,
                    office.name,
                    office.country,
                    office.street_and_address,
                    office.postcode,
                    office.city,
                    latitude if latitude is not None else '',
                    longitude if longitude is not None else ''
                ])
                
        print(f"\nProcessing complete! Results saved to {csv_filename}")
        print("Sample of processed data:")
        
        # Show first few lines of the CSV
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            for i, line in enumerate(csvfile):
                if i <= 5:  # Header + 5 entries
                    print(line.strip())
                else:
                    break
                    
    except FileNotFoundError:
        print("Error: Could not find the XML file 'RD_ICS2_CustomsOffices.xml'")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main() 