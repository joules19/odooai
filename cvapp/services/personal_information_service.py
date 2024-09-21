import openai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from docx import Document
from PyPDF2 import PdfReader
import re
import os


class ResumeProcessor:

    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def process_resume(self, resume_file):
        # Detect file format and extract text accordingly
        if resume_file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            text = self._extract_text_from_docx(resume_file)
        elif resume_file.content_type == 'application/pdf':
            text = self._extract_text_from_pdf(resume_file)
        else:
            return None

        # Use LangChain with OpenAI to extract personal info
        extracted_info = self._extract_personal_info(text)
        return extracted_info

    def _extract_text_from_docx(self, resume_file):
        # Read docx file from in-memory file
        doc = Document(resume_file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)

    def _extract_text_from_pdf(self, resume_file):
        # Read PDF file from in-memory file
        reader = PdfReader(resume_file)
        full_text = []
        for page in reader.pages:
            full_text.append(page.extract_text())
        return '\n'.join(full_text)

    def _extract_personal_info(self, text):
        prompt_template = """
        Extract the following information from the resume text:
        1. Full Name
        2. Email Address
        3. Phone Number
        4. Home Address

        Resume text:
        {text}

        Extracted Information:
        """

        prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

        # Create a LangChain LLMChain with the OpenAI model
        chain = LLMChain(
            llm=openai.Completion(),
            prompt=prompt
        )

        # Pass the resume text to the chain for extraction
        result = chain.run(text)

        # Use regex as a fallback for simple info like email, phone, etc.
        email = re.search(r'[\w\.-]+@[\w\.-]+', text)
        phone = re.search(r'\(?\+?\d{1,4}\)?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}', text)

        extracted_info = {
            "full_name": result.get("Full Name", "Not found"),
            "email": email.group(0) if email else "Not found",
            "phone": phone.group(0) if phone else "Not found",
            "address": result.get("Home Address", "Not found")
        }

        return extracted_info
