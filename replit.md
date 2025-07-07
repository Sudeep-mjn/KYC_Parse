# PDF Data Extraction & Form Filling Application

## Overview

This is a Streamlit-based web application that extracts data from user-provided PDFs (supporting both Nepali and English text), parses the extracted information, and automatically fills editable PDF templates. The application supports bulk processing and provides a user-friendly interface for document processing workflows.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid web app development
- **Design Pattern**: Single-page application with expandable sections
- **Layout**: Wide layout configuration with organized sections for different functionalities
- **State Management**: Streamlit session state for maintaining upload status and processed files

### Backend Architecture
- **Language**: Python 3.x
- **Architecture Pattern**: Modular design with separate classes for different responsibilities
- **Text Extraction**: PyMuPDF (fitz) for robust PDF text extraction with Unicode support
- **PDF Manipulation**: PyPDF2 for reading and filling editable PDF forms
- **Data Processing**: Regular expressions for pattern matching and data extraction

## Key Components

### 1. PDFProcessor (`pdf_processor.py`)
- **Purpose**: Handles PDF text extraction with support for multilingual content
- **Technology**: PyMuPDF (fitz) library
- **Features**: 
  - Unicode text extraction for Nepali and English support
  - Page-by-page text extraction
  - Text cleaning and preprocessing
- **Rationale**: PyMuPDF chosen over alternatives for better Unicode support and reliability with complex scripts

### 2. DataParser (`data_parser.py`)
- **Purpose**: Parses extracted text to identify and extract specific data fields
- **Approach**: Regular expression patterns for field identification
- **Supported Fields**: 
  - Personal information (name, DOB, gender, citizenship)
  - Address details (country, province, district, municipality)
  - Family member information
  - Bank details and occupation data
- **Language Support**: Dual pattern sets for English and Nepali field names

### 3. FormFiller (`form_filler.py`)
- **Purpose**: Fills editable PDF templates with extracted and parsed data
- **Technology**: PyPDF2 for PDF form manipulation
- **Field Mapping**: Configurable mapping between parsed data keys and PDF form field names
- **Error Handling**: Graceful handling of missing fields or mapping issues

### 4. Main Application (`app.py`)
- **Purpose**: Streamlit interface and application orchestration
- **Features**:
  - File upload interface for templates and source PDFs
  - Processing workflow management
  - Download functionality with proper naming conventions
  - Progress tracking and status updates

## Data Flow

1. **Template Upload**: User uploads editable PDF template
2. **Source PDF Upload**: User uploads one or multiple source PDFs containing data
3. **Text Extraction**: PDFProcessor extracts text from each source PDF
4. **Data Parsing**: DataParser identifies and extracts structured data using regex patterns
5. **Form Filling**: FormFiller populates template fields with extracted data
6. **Output Generation**: Filled PDFs generated with naming convention `original_filename_output.pdf`
7. **Download**: Individual or bulk download options provided to user

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **PyMuPDF (fitz)**: PDF text extraction with Unicode support
- **PyPDF2**: PDF form reading and writing
- **io**: In-memory file operations
- **zipfile**: Bulk download functionality
- **os**: File system operations
- **re**: Regular expression pattern matching

### Rationale for Technology Choices
- **Streamlit**: Chosen for rapid prototyping and simple deployment
- **PyMuPDF**: Selected over PDFMiner for better performance and Unicode handling
- **PyPDF2**: Reliable library for PDF form manipulation
- **Regex Patterns**: Flexible approach for multilingual data extraction

## Deployment Strategy

### Environment Requirements
- Python 3.7+
- Required dependencies installable via pip
- No database requirements (stateless processing)
- Minimal system resources needed

### Deployment Options
- **Local Development**: Direct Streamlit run
- **Cloud Platforms**: Compatible with Streamlit Cloud, Heroku, or similar platforms
- **Containerization**: Docker-ready for containerized deployments

### Configuration
- No external configuration files required
- Environment variables not currently used
- Self-contained application with embedded patterns and mappings

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

- **July 06, 2025 (Latest)**: Major improvements to data extraction and PDF form filling
  - Fixed PDF data visibility and editability issues by switching from PyPDF2 to PyMuPDF
  - Enhanced data extraction to 29 fields with 22.4% form fill rate (30/134 fields)
  - Added comprehensive field mappings for issue district, issue date, financial details, and addresses
  - Implemented proper text boundary patterns to prevent overlapping family member names
  - Added support for temporary address, permanent address, and income limit extraction
  - Resolved checkbox handling for gender, occupation, and account types

## Changelog

- July 06, 2025. Initial setup and comprehensive feature development