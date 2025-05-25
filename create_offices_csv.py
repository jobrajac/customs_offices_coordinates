from parse_customs_offices import parse_customs_offices
import csv
import os

def create_offices_csv():
    """Create a CSV file from the customs offices XML data."""
    
    xml_file = 'RD_ICS2_CustomsOffices.xml'
    csv_file = 'customs_offices.csv'
    
    if not os.path.exists(xml_file):
        print(f"Error: {xml_file} not found. Please run download_customs_data.py first.")
        return
    
    print(f"Parsing {xml_file}...")
    offices = parse_customs_offices(xml_file)
    print(f"Found {len(offices)} customs offices")
    
    print(f"Creating {csv_file}...")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow([
            'customs_office_id',
            'name',
            'country',
            'street_and_address',
            'postcode',
            'city',
            'latitude',
            'longitude'
        ])
        
        # Write data
        for office in offices:
            writer.writerow([
                office.customs_office_id,
                office.name,
                office.country,
                office.street_and_address,
                office.postcode,
                office.city,
                '',  # Empty latitude to be filled by geocoding
                ''   # Empty longitude to be filled by geocoding
            ])
    
    print(f"\nCreated {csv_file} with {len(offices)} offices")
    print("You can now run geocode_offices.py to add coordinates")

if __name__ == "__main__":
    create_offices_csv() 