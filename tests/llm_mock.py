import os
from app.llm import Response

script_dir = os.path.dirname(os.path.abspath(__file__))

class LLMMock():
    def generate(self):
        with open(os.path.join(script_dir, "data/llm_response.json")) as file:
            return Response.model_validate_json(file.read())
