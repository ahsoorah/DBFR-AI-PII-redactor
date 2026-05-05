# AI-Powered Hybrid Redactor

Executive Summary
This project is an intelligent document processing (IDP) engine designed to automate the redaction of Protected Health Information (PHI) and Personally Identifiable Information (PII) from complex medical and incident reports.

Originally developed during my Fire Technology Internship with the City of Delray Beach Fire-Rescue, this tool solves the "utility vs. privacy" dilemma by applying surgical redactions that protect sensitive data without rendering the underlying document useless for administrative analysis.

Business Impact
Operational Efficiency: Reduced manual redaction time for public record requests and HIPAA-compliant data sharing by approximately 75%.

Risk Mitigation: Utilizes a multi-layered AI approach to catch "hidden" PII in narrative text that standard pattern-matching tools often miss.

Technical Architecture
The tool uses a hybrid routing logic that automatically identifies the document type (Digitally native vs. Scanned/OCR) and selects the optimal processing pipeline.

The 4-Layer Redaction Logic
Pattern Matching (Regex): Immediate, high-speed identification of standard identifiers (Dates, Times, Case Numbers, and UUIDs).

Contextual Geometric Zoning: A custom algorithm that predicts the location of sensitive values based on their proximity to structural labels (ex. finding the "Value Zone" to the right of the string "Address").

NLP Entity Recognition: Integration with Microsoft Presidio and Spacy to identify names, locations, and organizations hidden within long-form narrative paragraphs.

Computer Vision (OCR): Utilizes EasyOCR to handle non-selectable text layers in scanned faxes or low-quality image-based PDFs.

Privacy & Sanitization Notice
This is a sanitized portfolio version of the production environment.

To comply with municipal security protocols and HIPAA regulations, this repository:
Removes all organization-specific infrastructure patterns and internal status codes.

Utilizes generalized regular expressions in place of department-specific incident formats.

Contains zero actual personnel or patient data.

Refactors the original script into a modular, Object-Oriented (OOP) structure for better maintainability.

Tech Stack
Engine: Python 3.x

Computer Vision: EasyOCR, PyMuPDF (fitz)

Natural Language Processing: Spacy (en_core_web_lg), Microsoft Presidio

UI/UX: Tkinter (Custom Progress Tracking)

Memory Management: GC (Garbage Collection) for batch processing high-resolution documents.

How It Works
The script follows a class-based execution flow:

Ingestion: Batch-loads PDF files through a GUI-driven selection.

Routing: Analyzes the first page's text-density to choose the Digital Pipeline or the OCR Pipeline.

Analysis: Runs parallel sweeps using the 4-layer logic mentioned above.

Surgical Redaction: Applies redaction annotations only to specific coordinates, preserving document layout.

Metadata Scrubbing: Physically removes XML metadata and "burns" the redactions into a flattened output file.

Author
Suriyah Saravanan
Bachelor's in Management Information Systems (MIS), Cybersecurity
Florida Atlantic University

Professional Disclaimer
This tool is intended for administrative assistance, and this specific version is for proof-of-concept purposes. While it utilizes advanced AI, final documents should always undergo a secondary human review to ensure 100% compliance with local privacy laws.
