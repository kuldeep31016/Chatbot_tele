# services/prescription_ocr.py
import re
from PIL import Image
import pytesseract
import cv2
import numpy as np

class PrescriptionExtractor:
    """Extract medicine name, dosage, frequency, and duration from OCR text."""
    def __init__(self):
        # Flexible regex patterns for messy OCR
        self.medicine_pattern = re.compile(r"([A-Z][a-zA-Z]{2,}\s*\d*\s*\.?\d*\s*(mg|ml|tab|caps)?)", re.I)
        self.dosage_pattern = re.compile(r"(\d+\s*\.?\d*\s*(mg|ml|tab|caps))", re.I)
        self.frequency_pattern = re.compile(
            r"(od|bd|tds|qhs|once daily|twice daily|thrice daily|morning|evening|night|ts)", re.I
        )
        self.duration_pattern = re.compile(r"(for\s*\d+\s*(day|days|week|weeks))", re.I)

    def extract(self, text: str):
        # Clean OCR noise
        text = text.replace("|", " ").replace(";", " ").replace("/", " ").replace("\n\n", "\n")
        lines = text.split("\n")
        medicines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Only process lines with dosage info
            if not self.dosage_pattern.search(line):
                continue

            med_match = self.medicine_pattern.search(line)
            dosage_match = self.dosage_pattern.search(line)
            freq_match = self.frequency_pattern.search(line)
            dur_match = self.duration_pattern.search(line)

            if med_match:
                medicines.append({
                    "name": med_match.group().strip(),
                    "dosage": dosage_match.group().strip() if dosage_match else "",
                    "frequency": freq_match.group().strip() if freq_match else "As prescribed",
                    "duration": dur_match.group().strip() if dur_match else ""
                })

        return medicines


class PrescriptionOCR:
    """Main class to scan a PIL image of a prescription and extract medicines."""
    def __init__(self, tesseract_path: str = None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.extractor = PrescriptionExtractor()

    def extract_prescription_data(self, image: Image.Image):
        """
        Scan the PIL image and return structured prescription data.
        :param image: PIL Image
        :return: dict containing raw_text and extracted medicines
        """
        # Convert PIL image to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        # OCR text extraction
        text = pytesseract.image_to_string(gray)

        # Extract structured medicine info
        medicines = self.extractor.extract(text)

        return {
            "raw_text": text,
            "medicines": medicines
        }


# Optional test
if __name__ == "__main__":
    tesseract_path = "/opt/homebrew/bin/tesseract"  # Update if needed
    ocr = PrescriptionOCR(tesseract_path=tesseract_path)

    image_path = "your_prescription.jpg"  # Replace with your test image
    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        print(f"File {image_path} not found")
        exit(1)

    result = ocr.extract_prescription_data(image)

    print("------ OCR Raw Text ------")
    print(result['raw_text'])
    print("\n------ Extracted Medicines ------")
    if result['medicines']:
        for med in result['medicines']:
            print(
                f"Name: {med['name']}, Dosage: {med['dosage']}, "
                f"Frequency: {med['frequency']}, Duration: {med['duration']}"
            )
    else:
        print("⚠️ No medicines found")
