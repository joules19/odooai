import re
import docx
from PyPDF2 import PdfReader

def convert_text_to_object(text: str):
     # Define patterns to match the different components in the text
    name_pattern = r"Full name:\s*(.*)"
    email_pattern = r"Email address:\s*([\w\.-]+@[\w\.-]+)"
    phone_pattern = r"Phone number:\s*([\(\)\d\s-]+)"
    address_pattern = r"Address:\s*(.*)"

    # Extract information using regex
    name_match = re.search(name_pattern, text)
    email_match = re.search(email_pattern, text)
    phone_match = re.search(phone_pattern, text)
    address_match = re.search(address_pattern, text)

    # Prepare the extracted information
    personal_info = {
        "name": name_match.group(1) if name_match else None,
        "email": email_match.group(1) if email_match else None,
        "phone": phone_match.group(1) if phone_match else None,
        "address": address_match.group(1) if address_match else None
    }

    return personal_info

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF using PyPDF2."""
    try:
        reader = PdfReader(file_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def extract_text_from_word(file_path: str) -> str:
    """Extract text from a Word document using python-docx."""
    try:
        doc = docx.Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        raise Exception(f"Error reading Word document: {str(e)}")
