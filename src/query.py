import os, html
import argparse
import time
import pandas as pd
from pubmed_parser import parse_pubmed_xml, parse_pubmed_paragraph, parse_pubmed_caption

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.zeroshot import get_response as get_zero_response
from utils.fewshot import get_response as get_few_response


def parse_args():

    p = argparse.ArgumentParser()

    p.add_argument('--xml-dir', required=True, help="Cleaned XML input directory")
    p.add_argument('--out-dir', required=True, help="Output directory for responses")
    p.add_argument('--model', required=True, help="OpenAI model name")
    p.add_argument('--api-key', required=True, help="OpenAI API key")
    p.add_argument('--mode', choices=['zero','few'], default='zero', help="zero-shot or few-shot")
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


def main(xml_dir, out_dir, model, api_key, mode):
    os.makedirs(out_dir, exist_ok=True)
    os.environ['api_key'] = api_key
    files = [f for f in os.listdir(xml_dir) if f.lower().endswith(('.xml', '.nxml'))]
    df = pd.DataFrame(columns=['id', 'definition', 'others'])

    for i, fn in enumerate(files):
        paper_id = os.path.splitext(fn)[0]
        path = os.path.join(xml_dir, fn)
        text = get_text(path)
        if mode == 'zero':
            resp1 = get_zero_response(api_key, model, True, text)
            time.sleep(2)
            resp2 = get_zero_response(api_key, model, False, text)
        else:
            resp1 = get_few_response(api_key, model, True, text)
            time.sleep(2)
            resp2 = get_few_response(api_key, model, False, text)
        df.loc[i] = [paper_id, resp1, resp2]

    out_path = os.path.join(out_dir, f"responses_{model.replace('/', '_')}.xlsx")
    df.to_excel(out_path, index=False)

if __name__ == '__main__':

    args = parse_args()
    main(args.xml_dir, args.out_dir, args.model, args.api_key, args.mode)