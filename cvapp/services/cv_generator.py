from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

def generate_condensed_cv(resume_text):
    # Define the prompt to be used for summarization
    prompt_template = PromptTemplate(
        input_variables=["resume_text"],
        template="Summarize the following resume text into a concise professional CV (no more than 150 words). Please exclude  personal information like address, email, phone number and dates:\n\n{resume_text}\n\n---\n\nSummary:",
    )

    # Use OpenAI's language model
    llm = OpenAI(temperature=0.7, max_tokens=300)

    # Create a chain with the prompt template and the LLM
    chain = LLMChain(prompt=prompt_template, llm=llm)

    # Run the chain to generate the summary
    summary = chain.run(resume_text=resume_text)

    return summary.strip()
