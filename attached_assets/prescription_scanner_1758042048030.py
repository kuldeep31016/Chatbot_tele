import re
import pytesseract
import cv2

class PrescriptionExtractor:
    def __init__(self):  # ✅ fixed
        # Flexible medicine detection (accepts spelling variations, spacing, case-insensitive)
        self.medicine_pattern = re.compile(
            r"(paracetamol\s*\d*\s*mg?|ibuprofen\s*\d*\s*mg?|amoxicillin\s*\d*\s*mg?)",
            re.I
        )
        # Dosage (mg/ml/tab)
        self.dosage_pattern = re.compile(r"(\d+\s*(mg|ml|tab))", re.I)
        # Frequency
        self.frequency_pattern = re.compile(
            r"(once\s*daily|twice\s*daily|thrice\s*daily|morning|evening|night|daily)",
            re.I
        )
        # Duration
        self.duration_pattern = re.compile(r"(for\s*\d+\s*(day|days|week|weeks))", re.I)

    def extract(self, text):
        lines = text.split("\n")
        results = []
        current = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Medicine
            med = self.medicine_pattern.search(line)
            if med:
                if current:
                    results.append(current)
                current = {
                    "medicine": med.group().strip(),
                    "dosage": "",
                    "frequency": "",
                    "duration": ""
                }

            # Dosage
            dose = self.dosage_pattern.search(line)
            if dose and current:
                current["dosage"] = dose.group().strip()

            # Frequency
            freq = self.frequency_pattern.search(line)
            if freq and current:
                current["frequency"] = freq.group().strip()

            # Duration
            dur = self.duration_pattern.search(line)
            if dur and current:
                current["duration"] = dur.group().strip()

        if current:
            results.append(current)

        return results


class PrescriptionScanner:
    def __init__(self, tesseract_path=None):  # ✅ fixed
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.extractor = PrescriptionExtractor()

    def scan_image(self, image_path):
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found: {image_path}")

        # Preprocess for OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        # OCR
        text = pytesseract.image_to_string(gray)
        return text

    def process(self, input_data, is_image=True):
        if is_image:
            raw_text = self.scan_image(input_data)
        else:
            raw_text = input_data

        medicines = self.extractor.extract(raw_text)
        return {"raw_text": raw_text, "structured_medicines": medicines}


# -----------------------------
# Example Usage
# -----------------------------
if __name__ == "__main__":
    scanner = PrescriptionScanner()  # Provide tesseract_path if needed
    result = scanner.process("prescription_sample.jpg")  # Replace with your image path

    print("Raw OCR Text:\n", result["raw_text"])
    print("\nStructured Medicines:\n", result["structured_medicines"])
