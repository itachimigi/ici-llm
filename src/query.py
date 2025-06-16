import os, html
import argparse
import time
import json
import pandas as pd
from pubmed_parser import parse_pubmed_xml, parse_pubmed_paragraph, parse_pubmed_caption
from openai import OpenAI
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.zeroshot import get_zeroshot_input
from utils.fewshot import get_fewshot_input


def parse_args():

    p = argparse.ArgumentParser()

    p.add_argument('--xml-dir', required=True, help="Cleaned XML input directory")
    p.add_argument('--out-dir', required=True, help="Output directory for responses")
    p.add_argument('--model', required=True, help="Model name: gpt-3.5-turbo, gpt-4-turbo, gpt-4o, deepseek-r1, gemini-2.5")
    p.add_argument('--api-key', required=True, help="API key")
    p.add_argument('--mode', required=True, help="zero-shot or few-shot")

    args = p.parse_args()

    return args

def get_text(path):
    data = parse_pubmed_xml(path)
    text = data.get('full_title', '') + '\n' + data.get('abstract', '') + '\n'
    for para in parse_pubmed_paragraph(path, all_paragraph=True):
        content = para.get('text', '').strip()
        if content:
            text += content + '\n'
    for cap in parse_pubmed_caption(path):
        content = cap.get('fig_caption', '').strip()
        if content:
            text += content + '\n'
    return html.unescape(text)

def process_response(response, df, index, columns):
    """Process API response and update DataFrame."""
    try:
        result = json.loads(response)
        df.loc[index,columns] = result

    except:
        df.loc[index, columns[0]] = response

def call_LLM(api_key, model, system_message, user_message):

    if model == "gpt-3.5-turbo":
        model = "gpt-3.5-turbo-0125"
        base_url = "https://api.openai.com/v1"
    elif model == "gpt-4-turbo":
        model = "gpt-4-turbo-2024-04-09"
        base_url = "https://api.openai.com/v1"
    elif model == "gpt-4o":
        model = "gpt-4o-2024-05-13"
        base_url = "https://api.openai.com/v1"
    elif model == "deepseek-r1":
        model = "deepseek-reasoner"
        base_url = "https://api.deepseek.com"
    elif model == "gemini-2.5":
        model = "gemini-2.5-flash-preview-05-20"
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"


    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    params = {
        "model": model,
        "temperature": 0.1,
        "response_format": { "type": "json_object" },
        "messages": [
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]
    }

    if model.startswith("gemini"):
        params["reasoning_effort"] = "high"

    completion = client.chat.completions.create(**params)

    response = completion.choices[0].message.content

    return response

def main(xml_dir, out_dir, model, api_key, mode):

    os.makedirs(out_dir, exist_ok=True)

    files = [f for f in os.listdir(xml_dir) if f.lower().endswith(('.xml', '.nxml'))]
    cols = ['id', 'Predictor', 'Feature', 'Model',
        'Data Required', 'Biosample Required', 'Cancer', 'Species', 'Treatment',
        'Cohort Details', 'Target Outcome', 'Correlation with Efficacy']
    df = pd.DataFrame(columns=cols, index=range(len(files)))

    for i, fn in enumerate(files):
        paper_id = os.path.splitext(fn)[0]
        path = os.path.join(xml_dir, fn)
        text = get_text(path)
        
        # Prepare system and user messages for zeroshot  prompts
        if mode == "zero-shot":
            system_message_1, user_message_1 = get_zeroshot_input(True, text)
            system_message_2, user_message_2 = get_zeroshot_input(False, text)

        # Prepare system and user messages for fewshot prompts
        elif mode == "few-shot":
            system_message_1, user_message_1 = get_fewshot_input(True, text)
            system_message_2, user_message_2 = get_fewshot_input(False, text)

        try:
            response_1 = call_LLM(api_key,  model, system_message_1, user_message_1)
        except:
            print(f"Error calling LLM for {paper_id} {mode}_1")
            response_1 = "Error"

        time.sleep(2)
        try:
            response_2 = call_LLM(api_key, model, system_message_2, user_message_2)
        except:
            print(f"Error calling LLM for {paper_id} {mode}_2")
            response_2 = "Error"
        
        time.sleep(2)

        df.loc[i, 'id'] = paper_id

        process_response(response_1, df, i, cols[1:4])
        process_response(response_2, df, i, cols[4:])


    df_zeroshot.to_excel(os.path.join(out_dir, f"responses_{model}_{mode}.xlsx"), index=False)


if __name__ == '__main__':

    args = parse_args()
    main(args.xml_dir, args.out_dir, args.model, args.api_key, args.mode)
