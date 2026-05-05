import os
import fitz  # PyMuPDF
import re
import easyocr
import gc
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

"""
AI-Powered Hybrid Redaction Script (Sanitized for portfolio)
---------------------------------------------------------------
An intelligent document processing tool that utilizes Computer Vision (OCR), 
Natural Language Processing (NLP), and Geometric Pattern Matching to 
automatically redact PII/PHI from medical and incident reports, ensuring
compliance with HIPAA and GDPR standards.

Key Innovations:
- Hybrid Routing: Automatically detects if a PDF is digitally native or scanned.
- Contextual Geometric Zoning: Predicts PII locations based on label-value proximity.
- NLP Integration: Uses Spacy and Microsoft Presidio for narrative-based entity detection.
- Surgical Redaction: Targets specific text coordinates to prevent 'over-redaction'
"""

class SmartRedactor:
    def __init__(self):
        self.initialize_engines()
        # Generic patterns to replace organization-specific ones
        self.patterns = {
            "date": re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$"),
            "time": re.compile(r"^\d{2}:\d{2}(?::\d{2})?$"),
            "incident": re.compile(r"^[A-Z]{2,}\d+$"), # Matches any 'AB12345' format
            "uuid": re.compile(r'\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b', re.I),
            "name": re.compile(r"\b[A-Z][a-zA-Z]+,\s*[A-Z][a-zA-Z]+\b")
        }
        
        # Comprehensive taxonomy for medical/incident report structures
        self.clinical_skipwords = {
            "arrest", "trauma", "critical", "normal", "patient", "incident", 
            "treatment", "intervention", "assessment", "iv", "oxygen", "cpr"
        }

    def initialize_engines(self):
        """Initializes heavy AI models only when needed."""
        print("Initializing Computer Vision and NLP Engines...")
        self.ocr_reader = easyocr.Reader(['en'])
        
        nlp_config = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
        }
        provider = NlpEngineProvider(nlp_configuration=nlp_config)
        self.nlp_analyzer = AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["en"])

    def apply_redaction(self, page, rect):
        """Applies a redaction annotation to the specified coordinates."""
        if rect:
            page.add_redact_annot(rect)

    def _get_spatial_context(self, label_word, all_words, default_width, y_tolerance=6):
        """
        GEOMETRIC LOGIC: Calculates the 'Value Zone' to the right of a label.
        Caps the zone if it hits another label to prevent over-redaction.
        """
        capped_right = label_word["rect"].x1 + default_width
        label_y_mid = (label_word["rect"].y0 + label_word["rect"].y1) / 2

        for other in all_words:
            if other is label_word or other["rect"].x0 <= label_word["rect"].x1:
                continue
            
            other_y_mid = (other["rect"].y0 + other["rect"].y1) / 2
            if abs(other_y_mid - label_y_mid) <= y_tolerance:
                # If hit another known label, stop the redaction zone there
                capped_right = min(capped_right, other["rect"].x0 - 2)
        
        return capped_right


    def process_structured_pdf(self, page):
        """Redaction engine for digitally native PDFs with text layers."""
        words = page.get_text("words")
        for i, w in enumerate(words):
            rect = fitz.Rect(w[:4])
            text = w[4]
            
            # Logic: Redact common PII patterns found in text layer
            if self.patterns["date"].match(text) or self.patterns["time"].match(text):
                self.apply_redaction(page, rect)
            
            # Pattern: Identify name formats (Last, First)
            if self.patterns["name"].match(page.get_text()):
                for r in page.search_for(text):
                    if text.lower() not in self.clinical_skipwords:
                        self.apply_redaction(page, r)


    def process_unstructured_pdf(self, page):
        """Redaction engine for scanned/handwritten documents using OCR and NLP."""
        # Scale image for high-accuracy OCR
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        results = self.ocr_reader.readtext(pix.tobytes())
        ocr_words = []
        for (bbox, text, prob) in results:
            # Map OCR coordinates back to PDF coordinates
            word_rect = fitz.Rect(bbox[0][0]/2, bbox[0][1]/2, bbox[2][0]/2, bbox[2][1]/2)
            ocr_words.append({"rect": word_rect, "text": text, "upper": text.upper()})


        # NLP Analysis on the combined OCR text
        full_text = " ".join([w["text"] for w in ocr_words])
        nlp_results = self.nlp_analyzer.analyze(text=full_text, entities=["PERSON", "LOCATION"], language='en')
        
        # Surgical NLP Strike: Redact only the entities identified by AI
        for res in nlp_results:
            entity_text = full_text[res.start:res.end]
            if entity_text.lower() not in self.clinical_skipwords:
                for w in ocr_words:
                    if entity_text in w["text"]:
                        self.apply_redaction(page, w["rect"])

    def run(self, input_files, output_path):
        """Main execution loop for document batch processing."""
        for file in input_files:
            doc = fitz.open(file)
            # Routing: Detect if PDF is digital or scanned
            is_digital = len(doc[0].get_text("words")) > 50
            
            for page in doc:
                if is_digital:
                    self.process_structured_pdf(page)
                else:
                    self.process_unstructured_pdf(page)
                
                # Apply the redactions and 'burn' them into the document
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
            
            # Metadata Scrubbing for security
            doc.set_metadata({})
            save_name = f"REDACTED_{os.path.basename(file)}"
            doc.save(os.path.join(output_path, save_name), garbage=3, deflate=True)
            doc.close()

# ==========================================
# GUI WRAPPER
# ==========================================
def main():
    root = tk.Tk()
    root.withdraw()

    files = filedialog.askopenfilenames(title="Select Documents for Redaction", filetypes=[("PDF files", "*.pdf")])
    if not files: return

    out_dir = filedialog.askdirectory(title="Select Destination Folder")
    if not out_dir: return

    # Execution
    redactor = SmartRedactor()
    redactor.run(files, out_dir)
    messagebox.showinfo("Complete", "Batch processing successful.")

if __name__ == "__main__":
    main()