import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
import openai
import os

from cvapp.services.cv_generator import generate_condensed_cv
from cvapp.services.resume_evaluator_service import ResumeEvaluator

from .utils import convert_text_to_object, extract_text_from_pdf, extract_text_from_word

from cvapp.services.llm_service import extract_personal_info, get_llm_response

# Set your OpenAI API key (ensure it's in your environment variables)
openai.api_key = os.getenv("OPENAI_API_KEY")

class CVExtractorView(APIView):
    """
    API View for extracting text from uploaded CV files.
    Supports PDF and Word documents (.docx, .doc).
    """
    
    # Define parsers to handle file uploads
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        """"
        Handles POST requests to extract text from an uploaded CV file.

        Expected file input parameter: 'file'

        Returns:
            - Extracted text content if file type is supported
            - An error message if file type is unsupported
        """
        file = request.FILES.get('file')  # Get the uploaded file

        if not file:
            return Response({"error": "No file uploaded"}, status=400)  # Return error if no file is found

        try:
            # Check the file extension and call appropriate extraction function
            if file.name.endswith('.pdf'):
                extracted_text = extract_text_from_pdf(file)
            elif file.name.endswith('.docx') or file.name.endswith('.doc'):
                extracted_text = extract_text_from_word(file)
            else:
                return Response({"error": "Unsupported file type"}, status=400)  # Return error for unsupported file types

            # Return the extracted text in the response
            return Response({"text": extracted_text}, status=200)
        
        except Exception as e:
            # Handle any unexpected errors during file processing
            return Response({"error": str(e)}, status=500)

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Save the uploaded file temporarily
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Determine the file type and extract text accordingly
        try:
            if file.name.endswith('.pdf'):
                extracted_text = extract_text_from_pdf(file_path)
            elif file.name.endswith('.docx') or file.name.endswith('.doc'):
                extracted_text = extract_text_from_word(file_path)
            else:
                return Response({"error": "Unsupported file type. Upload PDF or Word document."}, 
                                status=status.HTTP_400_BAD_REQUEST)

            # Extract personal information using OpenAI via Langchain
           
            
            personal_info = extract_personal_info(extracted_text)
            personal_info = convert_text_to_object(personal_info)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

        # return Response({"personal_info": personal_info}, status=status.HTTP_200_OK)
        return Response( personal_info, status=status.HTTP_200_OK)
class GenerateCoverLetterView(APIView):
    def post(self, request):
        try:
            # Check if file is uploaded
            if 'file' not in request.FILES:
                return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

            uploaded_file = request.FILES['file']
            file_type = uploaded_file.content_type

            # Process DOCX or PDF
            if file_type == 'application/pdf':
                resume_text = extract_text_from_pdf(uploaded_file)
            elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                resume_text = extract_text_from_word(uploaded_file)
            else:
                return Response({"error": "Unsupported file type."}, status=status.HTTP_400_BAD_REQUEST)

            if not resume_text:
                return Response({"error": "Could not extract text from the resume."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate summary using the service layer
            summary = generate_condensed_cv(resume_text)

            return Response(summary, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class EvaluateResumeView(APIView):
    def post(self, request, *args, **kwargs):
        # Validate if resume,  role, and qualifications are provided
        if 'resume' not in request.FILES or 'role' not in request.data or 'qualifications' not in request.data:
            return Response({'error': 'Resume,  role, and qualifications are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the uploaded resume,  role, and qualifications
        resume_file = request.FILES['resume']
        role = request.data['role']
        qualifications = request.data['qualifications']

        # Process the resume,  role, and qualifications
        evaluator = ResumeEvaluator()
        rating = evaluator.evaluate_resume(resume_file, role, qualifications)

        if rating is None:
            return Response({'error': 'Failed to evaluate resume.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the generated rating
        return Response({'rating': rating}, status=status.HTTP_200_OK)
   