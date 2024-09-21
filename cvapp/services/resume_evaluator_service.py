import os
import openai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from cvapp.utils import extract_text_from_pdf, extract_text_from_word

class ResumeEvaluator:
    def __init__(self):
        # Set your OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def evaluate_resume(self, resume_file, role, qualifications):
        # Extract the resume text based on file type
        if resume_file.name.endswith('.docx'):
            resume_text = extract_text_from_word(resume_file)
        elif resume_file.name.endswith('.pdf'):
            resume_text = extract_text_from_pdf(resume_file)
        else:
            return None

        # Use LangChain and OpenAI to evaluate the resume and generate a rating
        return self._generate_rating_from_text(resume_text, role, qualifications)


    def _generate_rating_from_text(self, resume_text, role, qualifications):
        # Format the list of qualifications
        qualifications_str = qualifications

        # Create the prompt for rating the resume
        prompt_template = """
        You are an expert hiring manager. Based on the resume text provided, evaluate how well the candidate fits the job role: {role}.
        Rate the candidate on a scale of 0 to 100, based on how well they match the following desired qualifications: {qualifications}.
        
        Resume Text:
        {resume_text}

        Provide only the rating (0 to 100):
        """

        # Create a LangChain PromptTemplate
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["resume_text", "role", "qualifications"]
        )

        # Use .format() to fill in the template with variables
        formatted_prompt = prompt.format(resume_text=resume_text, role=role, qualifications=qualifications_str)

        # Call OpenAI's GPT model via LangChain's LLMChain
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can switch to "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a hiring manager evaluating candidates."},
                {"role": "user", "content": formatted_prompt}
            ],
            max_tokens=50
        )

        # Extract the rating from the response
        rating_text = response['choices'][0]['message']['content'].strip()

        try:
            # Convert the response into a numeric rating (ensure it's a valid number)
            rating = int(rating_text)
            return rating
        except ValueError:
            return None