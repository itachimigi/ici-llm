from torchmetrics.text import BLEUScore
from torchmetrics.text.bert import BERTScore
from torchmetrics.text.rouge import ROUGEScore
from sklearn.metrics.pairwise import cosine_similarity
from gpt_scoring import get_eval_score
from openai import OpenAI
import numpy as np
import pandas as pd
import os
import time
import argparse

def parse_args():

    p = argparse.ArgumentParser()

    p.add_argument('--pred', required=True, help="LLM's response")
    p.add_argument('--ref', required=True, help="reference")
    p.add_argument('--api-key', required=True, help="OpenAI API key")
    p.add_argument('--out-dir', required=True, help="Output directory")
    args = p.parse_args()

    return args

def bleu_eval(pred, ref):
    bleu = BLEUScore(n_gram=1)
    bleu_score = bleu([pred], [[ref]])
    return bleu_score.numpy()

def bert_eval(pred, ref):
    bertscore = BERTScore(model_name_or_path="microsoft/deberta-xlarge-mnli")
    score = bertscore([pred], [ref])
    f1 = score['f1']
    return f1

def rouge_eval(pred, ref):
    rouge = ROUGEScore()
    score = rouge(pred, ref)
    f_1 = score['rouge1_fmeasure'].numpy()
    f_2 = score['rouge2_fmeasure'].numpy()
    f_L = score['rougeL_fmeasure'].numpy()
    return f_1, f_2, f_L

def cos_eval(pred, ref):
    embed_model = "text-embedding-3-large"
    client = OpenAI(api_key=os.getenv('api_key'))
    embed_pred = client.embeddings.create(input=[pred], model=embed_model).data[0].embedding
    embed_ref = client.embeddings.create(input=[ref], model=embed_model).data[0].embedding
    arr1 = np.array(embed_pred).reshape(1, -1)
    arr2 = np.array(embed_ref).reshape(1, -1)
    cos_score = cosine_similarity(arr1, arr2)[0][0]
    return cos_score

def gpt_eval(pred, ref):
    response = get_eval_score(ref, pred)
    time.sleep(1.5)
    try:
        score = int(response)
        return score
    except:
        return response

def main(pred, ref, api_key, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    os.environ['api_key'] = api_key

    df = pd.DataFrame(columns=['pred', 'ref', 'bleu', 'bert', 'rouge_1', 'rouge_2', 'rouge_L', 'cos', 'gpt'])

    bleu = bleu_eval(pred, ref)
    bert = bert_eval(pred, ref)
    r_1, r_2, r_L= rouge_eval(pred, ref)
    cos = cos_eval(pred, ref)
    gpt = gpt_eval(pred, ref)
    
    df.loc[0] = [pred, ref, bleu, bert, r_1, r_2, r_L, cos, gpt]

    out_path = os.path.join(out_dir, "scoring.xlsx")
    df.to_excel(out_path, index=False)


if __name__ == '__main__':

    args = parse_args()
    main(args.pred, args.ref, args.api_key, args.out_dir)
