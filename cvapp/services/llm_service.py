import environ
from langchain import LLMChain, OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain.memory import ConversationSummaryMemory
from langchain.prompts import MessagesPlaceholder

# Langchain prompt template for extracting personal information
prompt_template = """
Extract the following personal information from the given text:
- Full name
- First name
- Last name
- Address
- Email address
- Phone number

Text: {text}
"""

# Function to handle LLM interaction
def get_llm_response(input_data):
    # Initialize environment variables
    env = environ.Env()
    environ.Env.read_env()
    openai_api_key = env('OPENAI_API_KEY')

    # Initialize the chat model and memory
    chat_model = ChatOpenAI(openai_api_key=openai_api_key, verbose=True)
    memory = ConversationSummaryMemory(
        memory_key="messages",
        return_messages=True,
        llm=chat_model
    )

    # Define the prompt template
    prompt_template = ChatPromptTemplate(
        input_variables=["content", "messages"],
        messages=[
            MessagesPlaceholder(variable_name="messages"),
            HumanMessagePromptTemplate.from_template("{content}")
        ]
    )

    # Create and execute the LLM chain
    llm_chain = LLMChain(
        llm=chat_model,
        prompt=prompt_template,
        memory=memory,
        verbose=True
    )

    # Process the input through the chain and return the result
    result = llm_chain({"content": input_data})
    return result["text"]

def extract_personal_info(text: str) -> dict:
    """Use OpenAI via Langchain to extract personal information."""
    try:
        prompt = PromptTemplate(input_variables=["text"], template=prompt_template)
        # Initialize OpenAI with Langchain
        llm = OpenAI(temperature=0.2, max_tokens=1500)
        filled_prompt = prompt.format(text=text)
        response = llm(filled_prompt)
        return response.strip()
    except Exception as e:
        raise Exception(f"Error extracting personal info: {str(e)}")

