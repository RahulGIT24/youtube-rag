from core.config import settings
from groq import Groq

class LLM:
    API_KEY=settings.LLM_API_KEY
    MODEL=settings.LLM_MODEL_NAME
    SYSTEM_PROMPT = """
        You are a video analysis API. Your task is to answer the user's question based strictly on the provided context.

        INSTRUCTIONS:
        1. Analyze the Context carefully.
        2. If the answer is found, extract the 'start' time of the most relevant segment.
        3. Output your response in strict JSON format.
        4. Do NOT output any conversational text, markdown, or code blocks. Start the response with '{'.

        JSON STRUCTURE:
        {
        "answer": "Concise answer to the question.",
        "timestamp": 120.5,  // Float or null
        "found": true        // Boolean
        }

        If the context does not contain the answer:
        {
        "answer": "I cannot find the answer in this video.",
        "timestamp": null,
        "found": false
        }

        ### Here's Your Context
    """

    groq_client = None

    def __init__(self):
        self.groq_client = Groq(
            api_key=LLM.API_KEY,
        )

    def construct_prompt(self,context,query):
        return LLM.SYSTEM_PROMPT + "\n\n" + context + "\n\n" + "This is the user's query" + "\n\n" + query
    
    def call_llm(self,context,query):
        try:
            prompt = self.construct_prompt(context=context,query=query)
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=LLM.MODEL,
            )
            return chat_completion
        except Exception as e:
            print(e)
            raise e


