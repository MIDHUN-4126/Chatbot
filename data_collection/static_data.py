"""
Static Data Builder
Creates initial knowledge base from manually curated government service information
Use this when websites are not scrapable or for testing
"""

import json
import sqlite3
from datetime import datetime
import os

# Tamil Nadu Government Services Data
GOVERNMENT_SERVICES_DATA = {
    "services": [
        {
            "id": "birth_certificate",
            "name_en": "Birth Certificate",
            "name_ta": "பிறப்பு சான்றிதழ்",
            "description_en": "Official document certifying the birth of a person",
            "description_ta": "ஒரு நபரின் பிறப்பை சான்றளிக்கும் அதிகாரப்பூர்வ ஆவணம்",
            "department": "Revenue Department",
            "department_ta": "வருவாய் துறை",
            "requirements": [
                "Hospital birth certificate or declaration",
                "Parents' ID proof (Aadhaar/Voter ID)",
                "Address proof"
            ],
            "requirements_ta": [
                "மருத்துவமனை பிறப்பு சான்றிதழ் அல்லது அறிவிப்பு",
                "பெற்றோரின் அடையாள சான்று (ஆதார்/வாக்காளர் அடையாள அட்டை)",
                "முகவரி சான்று"
            ],
            "procedure": [
                "Visit e-Sevai center or apply online",
                "Submit required documents",
                "Pay prescribed fees",
                "Collect certificate after verification"
            ],
            "procedure_ta": [
                "இ-சேவை மையத்தை பார்வையிடவும் அல்லது ஆன்லைனில் விண்ணப்பிக்கவும்",
                "தேவையான ஆவணங்களை சமர்ப்பிக்கவும்",
                "நிர்ணயிக்கப்பட்ட கட்டணத்தை செலுத்தவும்",
                "சரிபார்ப்புக்கு பிறகு சான்றிதழை சேகரிக்கவும்"
            ],
            "fees": "Free",
            "fees_ta": "இலவசம்",
            "contact": "1800-425-1000",
            "url": "https://www.tnedistrict.gov.in"
        },
        {
            "id": "income_certificate",
            "name_en": "Income Certificate",
            "name_ta": "வருமான சான்றிதழ்",
            "description_en": "Certificate stating the annual income of an individual or family",
            "description_ta": "ஒரு நபர் அல்லது குடும்பத்தின் ஆண்டு வருமானத்தை குறிக்கும் சான்றிதழ்",
            "department": "Revenue Department",
            "department_ta": "வருவாய் துறை",
            "requirements": [
                "Aadhaar card",
                "Ration card",
                "Salary certificate or income proof",
                "Address proof"
            ],
            "requirements_ta": [
                "ஆதார் அட்டை",
                "ரேஷன் அட்டை",
                "சம்பள சான்றிதழ் அல்லது வருமான சான்று",
                "முகவரி சான்று"
            ],
            "procedure": [
                "Visit Taluk office or e-Sevai center",
                "Fill application form",
                "Submit required documents",
                "Pay fees (if applicable)",
                "Certificate issued after verification"
            ],
            "procedure_ta": [
                "தாலுக்கா அலுவலகம் அல்லது இ-சேவை மையத்தை பார்வையிடவும்",
                "விண்ணப்ப படிவத்தை நிரப்பவும்",
                "தேவையான ஆவணங்களை சமர்ப்பிக்கவும்",
                "கட்டணத்தை செலுத்தவும் (பொருந்தினால்)",
                "சரிபார்ப்புக்கு பிறகு சான்றிதழ் வழங்கப்படும்"
            ],
            "fees": "₹10",
            "fees_ta": "₹10",
            "processing_time": "7-15 days",
            "contact": "1800-425-1000",
            "url": "https://www.tnedistrict.gov.in"
        },
        {
            "id": "community_certificate",
            "name_en": "Community Certificate",
            "name_ta": "சமூக சான்றிதழ்",
            "description_en": "Certificate proving community status (SC/ST/OBC/MBC)",
            "description_ta": "சமூக நிலையை நிரூபிக்கும் சான்றிதழ் (SC/ST/OBC/MBC)",
            "department": "Revenue Department",
            "department_ta": "வருவாய் துறை",
            "requirements": [
                "Aadhaar card",
                "Parent's community certificate (if available)",
                "School records",
                "Address proof"
            ],
            "requirements_ta": [
                "ஆதார் அட்டை",
                "பெற்றோரின் சமூக சான்றிதழ் (இருந்தால்)",
                "பள்ளி பதிவுகள்",
                "முகவரி சான்று"
            ],
            "procedure": [
                "Apply through e-Sevai center",
                "Submit application with documents",
                "Verification by Tahsildar",
                "Certificate issued after approval"
            ],
            "procedure_ta": [
                "இ-சேவை மையம் மூலம் விண்ணப்பிக்கவும்",
                "ஆவணங்களுடன் விண்ணப்பத்தை சமர்ப்பிக்கவும்",
                "தஹசில்தார் மூலம் சரிபார்ப்பு",
                "ஒப்புதலுக்கு பிறகு சான்றிதழ் வழங்கப்படும்"
            ],
            "fees": "Free",
            "fees_ta": "இலவசம்",
            "processing_time": "15-30 days",
            "contact": "1800-425-1000",
            "url": "https://www.tnedistrict.gov.in"
        },
        {
            "id": "ration_card",
            "name_en": "Ration Card",
            "name_ta": "ரேஷன் அட்டை",
            "description_en": "Card for purchasing subsidized food grains from Public Distribution System",
            "description_ta": "பொது விநியோக அமைப்பிலிருந்து மானிய உணவு தானியங்களை வாங்குவதற்கான அட்டை",
            "department": "Civil Supplies Department",
            "department_ta": "சிவில் சப்ளைஸ் துறை",
            "requirements": [
                "Aadhaar card of all family members",
                "Income certificate",
                "Address proof (Electricity bill/Water bill)",
                "Passport size photos"
            ],
            "requirements_ta": [
                "அனைத்து குடும்ப உறுப்பினர்களின் ஆதார் அட்டை",
                "வருமான சான்றிதழ்",
                "முகவரி சான்று (மின்சாரம்/தண்ணீர் பில்)",
                "பாஸ்போர்ட் அளவு புகைப்படங்கள்"
            ],
            "types": [
                "Priority Household Card (PHH)",
                "Non-Priority Household Card (NPHH)"
            ],
            "procedure": [
                "Apply online at tnpds.gov.in",
                "Upload required documents",
                "Submit at Civil Supplies office",
                "Inspection and verification",
                "Card issued after approval"
            ],
            "procedure_ta": [
                "tnpds.gov.in இல் ஆன்லைனில் விண்ணப்பிக்கவும்",
                "தேவையான ஆவணங்களை பதிவேற்றவும்",
                "சிவில் சப்ளைஸ் அலுவலகத்தில் சமர்ப்பிக்கவும்",
                "ஆய்வு மற்றும் சரிபார்ப்பு",
                "ஒப்புதலுக்கு பிறகு அட்டை வழங்கப்படும்"
            ],
            "fees": "Free",
            "fees_ta": "இலவசம்",
            "contact": "1967 (Toll-free)",
            "url": "https://www.tnpds.gov.in"
        }
    ],
    "departments": [
        {
            "name": "Revenue Department",
            "name_ta": "வருவாய் துறை",
            "services": ["Birth Certificate", "Income Certificate", "Community Certificate"],
            "contact": "1800-425-1000",
            "website": "https://www.tn.gov.in/revenue"
        },
        {
            "name": "Civil Supplies Department",
            "name_ta": "சிவில் சப்ளைஸ் துறை",
            "services": ["Ration Card", "Fair Price Shop"],
            "contact": "1967",
            "website": "https://www.tnpds.gov.in"
        }
    ],
    "faqs": [
        {
            "question_en": "How to apply for birth certificate online?",
            "question_ta": "பிறப்பு சான்றிதழுக்கு ஆன்லைனில் எப்படி விண்ணப்பிப்பது?",
            "answer_en": "Visit tnedistrict.gov.in, select Birth Certificate service, fill the form, upload documents, and pay fees if applicable.",
            "answer_ta": "tnedistrict.gov.in ஐ பார்வையிடவும், பிறப்பு சான்றிதழ் சேவையை தேர்ந்தெடுக்கவும், படிவத்தை நிரப்பவும், ஆவணங்களை பதிவேற்றவும், மற்றும் பொருந்தினால் கட்டணம் செலுத்தவும்."
        },
        {
            "question_en": "What documents are required for income certificate?",
            "question_ta": "வருமான சான்றிதழுக்கு என்ன ஆவணங்கள் தேவை?",
            "answer_en": "Aadhaar card, ration card, salary certificate or income proof, and address proof are required.",
            "answer_ta": "ஆதார் அட்டை, ரேஷன் அட்டை, சம்பள சான்றிதழ் அல்லது வருமான சான்று, மற்றும் முகவரி சான்று தேவை."
        }
    ]
}


def create_static_knowledge_base():
    """Create initial knowledge base from static data"""
    # Create directories
    os.makedirs('../data/scraped', exist_ok=True)
    
    # Save to JSON
    json_path = '../data/scraped/static_data.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(GOVERNMENT_SERVICES_DATA, f, ensure_ascii=False, indent=2)
    
    # Save to SQLite
    db_path = '../data/scraped/government_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id TEXT PRIMARY KEY,
            name_en TEXT,
            name_ta TEXT,
            description_en TEXT,
            description_ta TEXT,
            department TEXT,
            department_ta TEXT,
            requirements TEXT,
            requirements_ta TEXT,
            procedure TEXT,
            procedure_ta TEXT,
            fees TEXT,
            fees_ta TEXT,
            processing_time TEXT,
            contact TEXT,
            url TEXT
        )
    ''')
    
    # Insert services
    for service in GOVERNMENT_SERVICES_DATA['services']:
        cursor.execute('''
            INSERT OR REPLACE INTO services VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            service['id'],
            service['name_en'],
            service['name_ta'],
            service['description_en'],
            service['description_ta'],
            service['department'],
            service['department_ta'],
            json.dumps(service['requirements']),
            json.dumps(service['requirements_ta']),
            json.dumps(service['procedure']),
            json.dumps(service['procedure_ta']),
            service['fees'],
            service['fees_ta'],
            service.get('processing_time', 'N/A'),
            service['contact'],
            service['url']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Static knowledge base created")
    print(f"  - JSON: {json_path}")
    print(f"  - Database: {db_path}")
    print(f"  - Services: {len(GOVERNMENT_SERVICES_DATA['services'])}")


if __name__ == '__main__':
    create_static_knowledge_base()
