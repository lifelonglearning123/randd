import openai
from decouple import config  # Import config from decouple
openai = OpenAI(default_headers={"OpenAI-Beta": "assistants=v1"})
openai.api_key = config("OPENAI_API_KEY")  # Use config to get the API key


def hmrc_randd_qu(full_response):
    question_dict = {
        "Qu1": f"Scientific or Technological Advance : What was the scientific or technological advance sought? Note: The advance must be in the overall knowledge or capability in a field of science or technology, not just the company’s own knowledge or capability.6. An advance in science or technology means an advance in overall knowledge or capability in a field of science or technology (not a company’s own state of knowledge or capability alone). This includes the adaptation of knowledge or capability from another field of science or technology in order to make such an advance where this adaptation was not readily deducible. An advance in science or technology may have tangible consequences (such as a new or more efficient cleaning product, or a process which generates less waste) or more intangible outcomes (new knowledge or cost improvements, for example).8. A process, material, device, product, service or source of knowledge does not become an advance in science or technology simply because science or technology is used in its creation. Work which uses science or technology but which does not advance scientific or technological capability as a whole is not an advance in science or technology. A project which seeks to, for example,a) extend overall knowledge or capability in a field of science or technology; or b) create a process, material, device, product or service which incorporates or represents an increase in overall knowledge or capability in a field of science or technology; or c) make an appreciable improvement to an existing process, material, device, product or service through scientific or technological changes; or d) use science or technology to duplicate the effect of an existing process, material, device, product or service in a new or appreciably improved way (e.g. a product which has exactly the same performance characteristics as existing models, but is built in a fundamentally different manner) will therefore be R&D. Even if the advance in science or technology sought by a project is not achieved or not fully realised, R&D still takes place. If a particular advance in science or technology has already been made or attempted but details are not readily available (for example, if it is a trade secret), work to achieve such an advance can still be an advance in science or technology. However, the routine analysis, copying or adaptation of an existing product, process, service or material, will not be an advance in science or technology.",
        "Qu2" : f"Scientific or Technological Uncertainties: What were the scientific or technological uncertainties involved in the project? The advance must be due to overcoming a scientific or technological uncertainty. Note: Uncertainties that can be resolved through brief discussions or have been overcome in previous projects are not considered technological uncertainties. The activities which directly contribute to achieving this advance in science or technology through the resolution of scientific or technological uncertainty are R&D.13. Scientific or technological uncertainty exists when knowledge of whether something is scientifically possible or technologically feasible, or how to achieve it in practice, is not readily available or deducible by a competent professional working in the field. This includes system uncertainty. Scientific or technological uncertainty will often arise from turning something that has already been established as scientifically feasible into a cost-effective, reliable and reproducible process, material, device, product or service. 14. Uncertainties that can readily be resolved by a competent professional working in the field are not scientific or technological uncertainties. Similarly, improvements, optimisations and fine-tuning which do not materially affect the underlying science or technology do not constitute work to resolve scientific or technological uncertainty.",
        "Qu3" : f"Overcoming Uncertainties: How and when were these uncertainties actually overcome? Describe the methods, investigations, and analysis used, focusing on successes and failures and their impact on the overall project.",
        "Qu4" : f"Field of Science or Technology: What was the field of science or technology being advanced? Need to consider what is not considered science, excluding work in the arts, humanities, and social sciences. Science is the systematic study of the nature and behaviour of the physical and material universe. Work in the arts, humanities and social sciences, including economics, is not science for the purpose of these Guidelines. Mathematical techniques are frequently used in science. From April 2023 mathematical advances in themselves are treated as science for the purposes of these Guidelines, whether or not they are advances in representing the nature and behaviour of the physical and material universe. These Guidelines apply equally to work in any branch or field of science. Technology is the practical application of scientific principles and knowledge, where ‘scientific’ is based on the definition of science above. These Guidelines apply equally to work in any branch or field of technology.",
        "Qu5" : f"Baseline of Science or Technology: What was the baseline of the science or technology when the project began?",
        "Qu6" : f"Knowledge Deduction by a Competent Professional: Why was the knowledge being sought not readily deducible by a competent professional in the field?",
        "Qu7" : f"Please provide a list of the competent professionals involved in the project, including their qualifications, experience and what work they did for the project"
    }

    for key, value in question_dict.items():
    # Step 3: Access and print the content of each item
        #print(f"Key: {key}, Value: {question_dict[key]}")
            # Call OpenAI with the value as the prompt
        value = "Answer the following questions based on the text provided. Please answer in at least 500 words " + value + full_response
        #print(value)
        try:
            response = openai.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {   "role": "system",
                    "content" : "You are a R&D grant writer. Your audience is HMRC. You need to write a report to HMRC based on the information provided. Just answer the question and don't write an introduction or conclusion",
                        "role":"user",
                    "content": value
                    }
                ]
            )
            # Update the value of the key with the response
            #question_dict[key] = response.choices[0].message.content
            #print(question_dict[key])
            
            # Extract the answer from the response
            answer = response.choices[0].message.content
            
            # Update the dictionary to store both the question and its answer
            question_dict[key] = {"Question": key, "Answer": answer}
            
        except Exception as e:
            print(f"Error occurred for key {key}: {e}")
    return question_dict

