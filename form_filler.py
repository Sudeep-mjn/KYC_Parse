import PyPDF2
import io
import fitz  # PyMuPDF for better form handling
from typing import Dict, Optional
import streamlit as st


class FormFiller:
    """Handles filling editable PDF forms with extracted data"""

    def __init__(self):
        # Mapping between parsed data keys and actual PDF form field names from EditablePdf.pdf
        self.field_mapping = {
            # Personal Information
            'name': 'Name In Block Letter',
            'date_of_birth': 'O    A D',  # Date of Birth AD field
            'citizenship_no': 'Citizenship Number',
            'beneficiary_id': 'Beneficiary ID Number',
            'pan_no': 'PAN',
            'national_id': 'National ID Number',
            'issue_district': 'IssueDistrict',
            'issue_date': 'hfL ldlt Issue Date',

            # Current Address
            'current_country': 'Current Address Country',
            'current_province': 'Current Address Province',
            'current_district': 'Current Address District',
            'current_municipality': 'Current Address Municipality',
            'current_ward_no': 'Current Address Ward Number',
            'current_tole': 'Current Address Tole',
            'current_telephone': 'Telephone Number',
            'current_mobile': 'Mobile Number',
            'current_email': 'Email Address',

            # Permanent Address
            'permanent_country': 'Permanent Address Country',
            'permanent_province': 'Permanent Address Province',
            'permanent_district': 'Permanent Address District',
            'permanent_municipality': 'Permanent Address Municipality',
            'permanent_ward_no': 'Permanent Ward Number',
            'permanent_tole': 'Permanent Address Tole',
            'permanent_telephone': 'Permanent Telephone Number',
            'permanent_block_no': 'Permanent Block Number',

            # Temporary Address
            'temporary_country': 'Temporary Address Country',
            'temporary_province': 'Temporary Address Province',
            'temporary_district': 'Temporary Address District',
            'temporary_municipality': 'Temporary Address Municipality',
            'temporary_ward_no': 'Temporary Ward Number',
            'temporary_tole': 'Temporary Address Tole',
            'temporary_telephone': 'Temporary Telephone Number',
            'temporary_mobile': 'Temporary Mobile Number',
            'temporary_email': 'Temporary Email Address',

            # Financial Details
            'income_limit': 'Financial Details',

            # Family Members
            'father_name': "Father",
            'mother_name': "Mother",
            'grandfather_name': "GrandFather",
            'spouse_name': "Spouse's Name",
            'son_name': "Son",
            'daughter_name': "Daughter",

            # Bank Details
            'bank_account_number': 'Bank Account Number',
            'bank_name': 'Bank Name and Address',

            # Occupation
            'organization': "Organization's Name",
            'designation': 'Designation'
        }

        # Gender checkbox mappings
        self.gender_mapping = {'male': 'MaleCheck', 'female': 'FemaleCheck'}

        # Occupation checkbox mappings
        self.occupation_mapping = {
            'agriculture': 'Agriculture',
            'business': 'Businessperson',
            'service': 'Govt',  # Government service
            'student': 'Student',
            'retired': 'Retired',
            'housewife': 'House Wife',
            'foreign': 'Foreign Employment'
        }

        # Bank account type mappings
        self.account_type_mapping = {
            'saving': 'Saving Account',
            'current': 'Current Account'
        }

        # Default template path
        self.default_template_path = './EditablePdf.pdf'

    def fill_template_with_default(self, parsed_data: Dict) -> Optional[bytes]:
        """
        Fill the default PDF template with parsed data
        
        Args:
            parsed_data: Dictionary containing extracted data
            
        Returns:
            bytes: Filled PDF as bytes, or None if failed
        """
        try:
            # Read the default template
            with open(self.default_template_path, 'rb') as f:
                template_bytes = f.read()

            # Create a mock file object for compatibility
            class MockFile:

                def __init__(self, data):
                    self.data = data
                    self.position = 0

                def read(self):
                    return self.data

                def seek(self, position):
                    self.position = position

                @property
                def name(self):
                    return 'EditablePdf.pdf'

            mock_file = MockFile(template_bytes)
            return self.fill_template(mock_file, parsed_data)

        except Exception as e:
            st.error(f"Error loading default template: {str(e)}")
            return None

    def fill_template(self, template_file,
                      parsed_data: Dict) -> Optional[bytes]:
        """
        Fill the PDF template with parsed data using PyMuPDF for better form handling
        
        Args:
            template_file: Streamlit uploaded file object (PDF template)
            parsed_data: Dictionary containing extracted data
            
        Returns:
            bytes: Filled PDF as bytes, or None if failed
        """
        try:
            # Reset file pointer
            template_file.seek(0)
            template_bytes = template_file.read()

            # Use PyMuPDF for form handling
            doc = fitz.open(stream=template_bytes, filetype="pdf")

            # Prepare field updates based on our mapping
            field_updates = self._prepare_field_updates(parsed_data, {})

            # Get all form fields in the document
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()

                if widgets:
                    # st.info(f"Found {len(widgets)} form fields on page {page_num + 1}")

                    for widget in widgets:
                        field_name = widget.field_name
                        if field_name in field_updates:
                            try:
                                # Set the field value
                                value = str(field_updates[field_name])

                                # Handle different field types
                                if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                                    # Apply improved text formatting for names
                                    formatted_value = self._format_text_for_field(value, field_name, widget)
                                    widget.field_value = formatted_value
                                    
                                    # Apply font size optimization for name fields
                                    self._optimize_font_size(widget, field_name, formatted_value)
                                    
                                    widget.update()
                                elif widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                                    # For checkboxes, set based on Yes/On values
                                    if value.lower() in [
                                            'yes', 'on', 'true', '1'
                                    ]:
                                        widget.field_value = True
                                    else:
                                        widget.field_value = False
                                    widget.update()
                                elif widget.field_type == fitz.PDF_WIDGET_TYPE_RADIOBUTTON:
                                    # For radio buttons
                                    if value.lower() in [
                                            'yes', 'on', 'true', '1'
                                    ]:
                                        widget.field_value = True
                                    else:
                                        widget.field_value = False
                                    widget.update()

                                # st.success(f"Updated field '{field_name}' with value '{value}'")

                            except Exception as widget_error:
                                st.warning(
                                    f"Could not update field '{field_name}': {str(widget_error)}"
                                )
                        else:
                            # Debug: show unmapped fields (using info instead of debug)
                            pass  # st.info(f"Field '{field_name}' not in mapping")
                else:
                    st.warning(f"No form fields found on page {page_num + 1}")

            # Save the filled PDF
            output_buffer = io.BytesIO()
            doc.save(output_buffer)
            doc.close()
            output_buffer.seek(0)

            return output_buffer.getvalue()

        except Exception as e:
            st.error(f"Error filling PDF template: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")
            return None

    def _get_form_fields(self, pdf_reader) -> Dict:
        """Extract form fields from PDF"""
        form_fields = {}

        try:
            # Try different methods to get form fields
            if hasattr(pdf_reader, 'get_form_text_fields'):
                form_fields = pdf_reader.get_form_text_fields() or {}
            elif hasattr(pdf_reader, 'get_fields'):
                fields = pdf_reader.get_fields()
                if fields:
                    form_fields = {
                        name: field.get('/V', '')
                        for name, field in fields.items()
                    }

            # If still no fields, try to extract from annotations
            if not form_fields:
                for page in pdf_reader.pages:
                    if '/Annots' in page:
                        for annot_ref in page['/Annots']:
                            try:
                                annot = annot_ref.get_object()
                                if '/T' in annot:  # Field name
                                    field_name = annot['/T']
                                    field_value = annot.get('/V', '')
                                    form_fields[field_name] = field_value
                            except:
                                continue

        except Exception as e:
            st.warning(f"Could not extract form fields: {str(e)}")

        return form_fields

    def _prepare_field_updates(self, parsed_data: Dict,
                               form_fields: Dict) -> Dict:
        """Prepare field updates based on mapping"""
        field_updates = {}

        # Handle regular text fields
        for data_key, pdf_field_name in self.field_mapping.items():
            if data_key in parsed_data and parsed_data[data_key]:
                value = str(parsed_data[data_key]).strip()
                if value and value != '-':
                    field_updates[pdf_field_name] = value

        # Handle gender checkboxes
        if 'gender' in parsed_data:
            gender_value = str(parsed_data['gender']).upper()
            if gender_value in ['M', 'MALE']:
                field_updates['MaleCheck'] = 'Yes'
                field_updates['FemaleCheck'] = 'Off'
            elif gender_value in ['F', 'FEMALE']:
                field_updates['FemaleCheck'] = 'Yes'
                field_updates['MaleCheck'] = 'Off'

        # Handle bank account type checkboxes
        if 'bank_account_type' in parsed_data:
            account_type = str(parsed_data['bank_account_type']).lower()
            if 'saving' in account_type:
                field_updates['Saving Account'] = 'Yes'
                field_updates['Current Account'] = 'Off'
            elif 'current' in account_type:
                field_updates['Current Account'] = 'Yes'
                field_updates['Saving Account'] = 'Off'

        # Handle occupation checkboxes
        if 'occupation' in parsed_data:
            occupation = str(parsed_data['occupation']).lower()
            if 'agriculture' in occupation:
                field_updates['Agriculture'] = 'Yes'
            elif 'business' in occupation:
                field_updates['Businessperson'] = 'Yes'
            elif 'service' in occupation or 'govt' in occupation:
                field_updates['Govt'] = 'Yes'
            elif 'student' in occupation:
                field_updates['Student'] = 'Yes'
            elif 'retired' in occupation:
                field_updates['Retired'] = 'Yes'
            elif 'house' in occupation or 'wife' in occupation:
                field_updates['House Wife'] = 'Yes'
            elif 'foreign' in occupation or 'employment' in occupation:
                field_updates['Foreign Employment'] = 'Yes'

        return field_updates

    def _update_form_fields(self, page, field_updates: Dict):
        """Update form fields in the page"""
        if '/Annots' not in page:
            return

        for annot_ref in page['/Annots']:
            try:
                annot = annot_ref.get_object()
                if '/T' in annot:  # Field name
                    field_name = annot['/T']
                    if field_name in field_updates:
                        # Update field value
                        annot.update({
                            PyPDF2.generic.NameObject('/V'):
                            PyPDF2.generic.TextStringObject(
                                field_updates[field_name])
                        })
            except Exception:
                continue

    def _update_field_by_annotation(self, pdf_writer, field_name: str,
                                    value: str):
        """Update form field by directly modifying annotations"""
        try:
            for page_num, page in enumerate(pdf_writer.pages):
                if '/Annots' in page:
                    annotations = page['/Annots']
                    for annot_ref in annotations:
                        try:
                            annot = annot_ref.get_object()
                            if '/T' in annot and annot['/T'] == field_name:
                                # Update the field value
                                annot.update({
                                    PyPDF2.generic.NameObject('/V'):
                                    PyPDF2.generic.TextStringObject(value)
                                })
                                # Force appearance update
                                if '/AP' in annot:
                                    annot.pop('/AP', None)
                                return  # Field found and updated
                        except Exception:
                            continue
        except Exception:
            pass  # Silently handle annotation update errors

    def _fill_template_alternative(self, template_bytes: bytes,
                                   parsed_data: Dict) -> Optional[bytes]:
        """
        Alternative method to fill PDF when form fields are not detected
        This method creates a new PDF with the original template as background
        and overlays text at approximate positions
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont

            # Create a new PDF with the data
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)

            # Set font (try to use a font that supports Unicode)
            try:
                c.setFont("Helvetica", 10)
            except:
                c.setFont("Courier", 10)

            # Define approximate positions for different fields based on the template structure
            y_position = 750  # Start from top
            x_position = 100
            line_height = 20

            # Add data to PDF
            c.drawString(x_position, y_position, "FILLED PDF FORM")
            y_position -= line_height * 2

            # Add extracted data
            for key, value in parsed_data.items():
                if value and str(value).strip():
                    display_key = key.replace('_', ' ').title()
                    text = f"{display_key}: {value}"
                    c.drawString(x_position, y_position, text)
                    y_position -= line_height

                    # Start new page if needed
                    if y_position < 100:
                        c.showPage()
                        c.setFont("Helvetica", 10)
                        y_position = 750

            c.save()
            buffer.seek(0)

            # Try to merge with original template
            try:
                template_reader = PyPDF2.PdfReader(io.BytesIO(template_bytes))
                overlay_reader = PyPDF2.PdfReader(buffer)
                writer = PyPDF2.PdfWriter()

                # Merge pages
                for i in range(len(template_reader.pages)):
                    template_page = template_reader.pages[i]

                    if i < len(overlay_reader.pages):
                        overlay_page = overlay_reader.pages[i]
                        template_page.merge_page(overlay_page)

                    writer.add_page(template_page)

                # Create final output
                final_buffer = io.BytesIO()
                writer.write(final_buffer)
                final_buffer.seek(0)

                return final_buffer.getvalue()

            except Exception:
                # If merging fails, return the overlay only
                buffer.seek(0)
                return buffer.getvalue()

        except ImportError:
            st.error(
                "ReportLab library not available for alternative PDF filling method"
            )
            return None
        except Exception as e:
            st.error(f"Alternative PDF filling method failed: {str(e)}")
            return None

    def _format_text_for_field(self, value: str, field_name: str, widget) -> str:
        """
        Format text for optimal display in PDF form fields
        
        Args:
            value: Text value to format
            field_name: Name of the form field
            widget: PyMuPDF widget object
            
        Returns:
            str: Formatted text value
        """
        if not value or not value.strip():
            return value
        
        # Clean up the value first - remove extra spaces
        cleaned_value = ' '.join(value.strip().split())
        
        # For all fields, return cleaned value without any character spacing
        return cleaned_value

    def _optimize_font_size(self, widget, field_name: str, text_value: str):
        """
        Optimize font size for better text display in form fields
        
        Args:
            widget: PyMuPDF widget object
            field_name: Name of the form field
            text_value: Text value being filled
        """
        try:
            # Check if this is a field that needs character-per-box formatting
            is_character_box_field = any(field in field_name.lower() for field in [
                'name in block letter', 'father', 'mother', 'grandfather', 
                'spouse', 'son', 'daughter', 'beneficiary id number'
            ])
            
            # Check if this is a name field that might benefit from font optimization
            is_name_field = any(keyword in field_name.lower() for keyword in 
                               ['name', 'father', 'mother', 'spouse', 'son', 'daughter'])
            
            if is_character_box_field and text_value:
                # For character box fields, use smaller font to fit individual boxes
                field_width = widget.rect.width if widget.rect else 300
                char_count = len(text_value.replace(' ', ''))  # Count without spaces
                
                if char_count > 15:
                    # Very long text - use very small font
                    widget.text_fontsize = 7.0
                elif char_count > 10:
                    # Long text - use small font
                    widget.text_fontsize = 8.0
                else:
                    # Normal length - use medium font
                    widget.text_fontsize = 9.0
                
                # Ensure text color is black for visibility
                widget.text_color = (0, 0, 0)  # RGB black
                
            elif is_name_field and text_value and len(text_value) > 10:
                # For other name fields, use standard font optimization
                field_width = widget.rect.width if widget.rect else 300
                char_density = len(text_value) / field_width if field_width > 0 else 0
                
                if char_density > 0.04:
                    # High density - use smaller font
                    widget.text_fontsize = 9.0
                elif char_density > 0.035:
                    # Medium density - use medium font
                    widget.text_fontsize = 10.0
                else:
                    # Low density - use standard font
                    widget.text_fontsize = 11.0
                
                # Ensure text color is black for visibility
                widget.text_color = (0, 0, 0)  # RGB black
                
        except Exception:
            # If font optimization fails, continue without it
            pass

    def get_field_mapping_info(self) -> Dict:
        """Return information about field mappings for debugging"""
        return {
            'total_mappings': len(self.field_mapping),
            'categories': {
                'personal':
                len([
                    k for k in self.field_mapping.keys() if k in [
                        'name', 'date_of_birth', 'gender', 'citizenship_no',
                        'beneficiary_id', 'pan_no'
                    ]
                ]),
                'address':
                len([
                    k for k in self.field_mapping.keys()
                    if k.startswith('current_')
                ]),
                'family':
                len([
                    k for k in self.field_mapping.keys() if k.endswith('_name')
                ]),
                'bank':
                len([
                    k for k in self.field_mapping.keys()
                    if k.startswith('bank_')
                ]),
                'occupation':
                len([
                    k for k in self.field_mapping.keys()
                    if k in ['occupation', 'organization', 'designation']
                ])
            },
            'mappings': self.field_mapping
        }
