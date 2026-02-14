import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from utils.config import get_default_model

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key

class LLMModel:
    def __init__(self, model_name: str | None = None):
        model_name = model_name or get_default_model()
        if not model_name:
            raise ValueError("Model is not defined.")

        self.model_name = model_name
        self.openai_model = ChatOpenAI(model=self.model_name)
        
    def get_model(self):
        return self.openai_model

if __name__ == "__main__":
    llm_instance = LLMModel()  
    llm_model = llm_instance.get_model()
    response=llm_model.invoke("hi")

    print(response)