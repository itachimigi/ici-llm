from torchmetrics.text import BLEUScore
from torchmetrics.text.bert import BERTScore
from torchmetrics.text.rouge import ROUGEScore
from sklearn.metrics.pairwise import cosine_similarity
from gpt_scoring import get_eval_score
from openai import OpenAI
import numpy as np
import os
import time

os.environ['api_key'] = "sk-XXXX" 

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