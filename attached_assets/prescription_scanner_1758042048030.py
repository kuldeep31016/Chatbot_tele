import re
import pytesseract
import cv2
import numpy as np
from PIL import Image

class PrescriptionExtractor:
    def __init__(self):
        self.medicine_pattern = re.compile(
            r"(paracetamol\s*\d*\s*mg?|ibuprofen\s*\d*\s*mg?|amoxicillin\s*\d*\s*mg?)",
            re.I
        )
        self.dosage_pattern = re.compile(r"(\d+\s*(mg|ml|tab))", re.I)
        self.frequency_pattern = re.compile(
            r"(once\s*daily|twice\s*daily|thrice\s*daily|morning|evening|night|daily)", re.I
        )
        self.duration_pattern = re.compile(r"(for\s*\d+\s*(day|days|week|weeks))", re.I)

    def extract(self, text):
        lines = text.split("\n")
        results = []
        current = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            med = self.medicine_pattern.search(line)
            if med:
                if current:
                    results.append(current)
                current = {
                    "name": med.group().strip(),
                    "dosage": "",
                    "frequency": "",
                    "duration": ""
                }

            dose = self.dosage_pattern.search(line)
            if dose and current:
                current["dosage"] = dose.group().strip()

            freq = self.frequency_pattern.search(line)
            if freq and current:
                current["frequency"] = freq.group().strip()

            dur = self.duration_pattern.search(line)
            if dur and current:
                current["duration"] = dur.group().strip()

        if current:
            results.append(current)
        return results


class PrescriptionScanner:
    def __init__(self, tesseract_path=None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.extractor = PrescriptionExtractor()

    def scan_pil_image(self, pil_image):
        img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
        text = pytesseract.image_to_string(gray)
        return text

    def process(self, input_data, is_image=True):
        if is_image:
            raw_text = self.scan_pil_image(input_data)
        else:
            raw_text = input_data
        medicines = self.extractor.extract(raw_text)
        return {"raw_text": raw_text, "medicines": medicines}


# ------------------------------
# Main program to run the scanner
# ------------------------------
if __name__ == "__main__":
    # Set this to the path where Tesseract OCR is installed
    # macOS example:
    tesseract_path = '/usr/local/bin/tesseract'
    # Windows example:
    # tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    scanner = PrescriptionScanner(tesseract_path=tesseract_path)

    # Load your image file here
    image_path = "your_prescription.jpg"  # Change to your actual image file path
    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: File {image_path} not found.")
        exit(1)

    result = scanner.process(image, is_image=True)

    print("------ OCR Raw Text ------")
    print(result['raw_text'])
    print("\n------ Extracted Medicines ------")
    if result['medicines']:
        for med in result['medicines']:
            print(f"Name: {med['name']}")
            print(f"Dosage: {med['dosage']}")
            print(f"Frequency: {med['frequency']}")
            print(f"Duration: {med['duration']}")
            print("-" * 20)
    else:
        print("No medicines found.")
