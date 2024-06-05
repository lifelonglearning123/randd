import openai
from decouple import config  # Import config from decouple
openai = OpenAI(default_headers={"OpenAI-Beta": "assistants=v1"})

def summary(full_response):
    #print("**************")
    full_response = full_response + "Write a paragraph in 200 words summarising the technology.Do not use bullet points"
    #print(full_response)
    response = openai.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {   "role": "system",
            "content" : "You are a technology reviewer. Your audience is technology enthusiast. ",
                "role":"user",
            "content": full_response
            
            }
        ]
    )
    
    summary_text = response.choices[0].message.content
    print("*************")
    print(summary_text)
    return summary_text

