import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List

@dataclass
class CustomsOffice:
    customs_office_id: str
    name: str
    country: str
    street_and_address: str
    postcode: str
    city: str

def parse_customs_offices(xml_file: str) -> List[CustomsOffice]:
    # Define the XML namespaces
    namespaces = {
        'ns0': 'http://xmlns.ec.eu/BusinessObjects/CSRD2/ReferenceDataExportBASServiceType/V2',
        'ns2': 'http://xmlns.ec.eu/BusinessObjects/CSRD2/RDEntityEntryListType/V2',
        'ns3': 'http://xmlns.ec.eu/BusinessObjects/CSRD2/RDEntityType/V2',
        'ns4': 'http://xmlns.ec.eu/BusinessObjects/CSRD2/RDEntryType/V2'
    }

    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    customs_offices = []

    # Find all RDEntry elements
    for entry in root.findall('.//ns3:RDEntry', namespaces):
        # Initialize variables
        office_id = None
        name = None
        country = None
        street = None
        postcode = None
        city = None

        # Get customs office ID (ReferenceNumber)
        ref_number = entry.find('.//ns4:dataItem[@name="ReferenceNumber"]', namespaces)
        if ref_number is not None:
            office_id = ref_number.text

        # Get country code
        country_code = entry.find('.//ns4:dataItem[@name="CountryCode"]', namespaces)
        if country_code is not None:
            country = country_code.text

        # Get postal code
        postal_code = entry.find('.//ns4:dataItem[@name="PostalCode"]', namespaces)
        if postal_code is not None:
            postcode = postal_code.text

        # Find CustomsOfficeLsd group
        lsd_group = entry.find('.//ns4:dataGroup[@name="CustomsOfficeLsd"]', namespaces)
        if lsd_group is not None:
            # Get customs office name
            name_elem = lsd_group.find('.//ns4:dataItem[@name="CustomsOfficeUsualName"]', namespaces)
            if name_elem is not None:
                name = name_elem.text

            # Get street and number
            street_elem = lsd_group.find('.//ns4:dataItem[@name="StreetAndNumber"]', namespaces)
            if street_elem is not None:
                street = street_elem.text

            # Get city
            city_elem = lsd_group.find('.//ns4:dataItem[@name="City"]', namespaces)
            if city_elem is not None:
                city = city_elem.text

        if all([office_id, name, country, street, postcode, city]):
            customs_offices.append(CustomsOffice(
                customs_office_id=office_id,
                name=name,
                country=country,
                street_and_address=street,
                postcode=postcode,
                city=city
            ))

    return customs_offices

def main():
    try:
        offices = parse_customs_offices('RD_ICS2_CustomsOffices.xml')
        print(f"Found {len(offices)} customs offices")
        
        # Print the first few offices as example
        for office in offices[:5]:
            print("\nCustoms Office:")
            print(f"ID: {office.customs_office_id}")
            print(f"Name: {office.name}")
            print(f"Country: {office.country}")
            print(f"Address: {office.street_and_address}")
            print(f"Postcode: {office.postcode}")
            print(f"City: {office.city}")
            
    except FileNotFoundError:
        print("Error: Could not find the XML file 'RD_ICS2_CustomsOffices.xml'")
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main() 