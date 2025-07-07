import PyPDF2
import json
import streamlit as st
from typing import Dict, Any

def extract_form_fields_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extract all form fields from the PDF template and create a field mapping
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            form_fields = {}
            
            # Try to get form fields using different methods
            if hasattr(pdf_reader, 'get_form_text_fields'):
                fields = pdf_reader.get_form_text_fields()
                if fields:
                    for name, value in fields.items():
                        form_fields[name] = {
                            "field_name": name,
                            "field_type": "text",
                            "field_value": value or "",
                            "method": "get_form_text_fields"
                        }
            
            # Try alternative method
            if hasattr(pdf_reader, 'get_fields'):
                fields = pdf_reader.get_fields()
                if fields:
                    for name, field in fields.items():
                        field_type = field.get('/FT', 'unknown')
                        field_value = field.get('/V', '')
                        form_fields[name] = {
                            "field_name": name,
                            "field_type": str(field_type),
                            "field_value": str(field_value) if field_value else "",
                            "method": "get_fields"
                        }
            
            # Extract from annotations if no fields found
            if not form_fields:
                for page_num, page in enumerate(pdf_reader.pages):
                    if '/Annots' in page:
                        for annot_ref in page['/Annots']:
                            try:
                                annot = annot_ref.get_object()
                                if '/T' in annot:  # Field name
                                    field_name = str(annot['/T'])
                                    field_type = annot.get('/FT', 'unknown')
                                    field_value = annot.get('/V', '')
                                    rect = annot.get('/Rect', [])
                                    
                                    form_fields[field_name] = {
                                        "field_name": field_name,
                                        "field_type": str(field_type),
                                        "field_value": str(field_value) if field_value else "",
                                        "rect": list(rect) if rect else [],
                                        "page": page_num + 1,
                                        "method": "annotations"
                                    }
                            except Exception as e:
                                continue
            
            return form_fields
            
    except Exception as e:
        st.error(f"Error extracting form fields: {str(e)}")
        return {}

if __name__ == "__main__":
    # Extract fields from EditablePdf.pdf
    fields = extract_form_fields_from_pdf('./EditablePdf.pdf')
    
    # Save to JSON file
    with open('editable_pdf_fields.json', 'w', encoding='utf-8') as f:
        json.dump(fields, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted {len(fields)} form fields:")
    for name, info in fields.items():
        print(f"- {name}: {info.get('field_type', 'unknown')}")