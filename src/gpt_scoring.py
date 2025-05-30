import os
from openai import OpenAI

# Evaluation prompt template
EVALUATION_PROMPT_TEMPLATE = """
You will be given an answer generated by GPT and a reference answer written by a human. Your task is to rate the GPT's answer based on the given metric.
Please make sure you read and understand these instructions very carefully. 

Evaluation Criteria:

{criteria}

Evaluation Steps:

{steps}

Reference Answer:

{reference_answer}

GPT's Answer:

{gpt_answer}

Evaluation: (scores ONLY):

"""

# Metric: Content Accuracy

CONTENT_ACCURACY_CRITERIA = """
Content Accuracy (0-5) - the degree to which the GPT's answer accurately reflects the information in the reference answer. 
"""

CONTENT_ACCURACY_STEPS = """
1. Read the reference answer carefully and identify the main points and key information.
2. Read the GPT's answer and compare it to the reference answer.
3. Assess how well the GPT's answer covers the key information from the reference answer.
4. Assign a content accuracy score 0-5.
"""

def get_eval_score(reference_answer: str, gpt_answer: str):
    client = OpenAI(
        api_key=os.getenv('api_key'),
    )
    prompt = EVALUATION_PROMPT_TEMPLATE.format(
        criteria=CONTENT_ACCURACY_CRITERIA,
        steps=CONTENT_ACCURACY_STEPS,
        reference_answer=reference_answer,
        gpt_answer=gpt_answer,
    )
    response = client.chat.completions.create(
        model="gpt-4o-2024-05-13",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return response.choices[0].message.content