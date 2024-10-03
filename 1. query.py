import html
import pubmed_parser as pp
import os
from chat_zeroshot import get_response # for zero-shot settings
import pandas as pd
import time

def main():
    os.environ['api_key'] = "sk-XXX"
    gpt_4 = "gpt-4-turbo-2024-04-09"
    gpt_35 = "gpt-3.5-turbo-0125"
    gpt_4o = "gpt-4o-2024-05-13"
    fine_tuned = "ft:gpt-3.5-turbo-0125:personal::XXX"
    model = gpt_4
    
    base = "BASE/TO/XML_FILES/"
    files = os.listdir(base)

    df = pd.DataFrame(columns=['id', 'definition', 'others'])
    
    for i, paper in enumerate(files):

        file_name = paper.split(".")[0]
        path = os.path.join(base, file_name)
        text = get_text(path)

        response_1 = get_response(
            api=os.getenv('api_key'),
            model_version=model,
            is_definition=True,
            text=text,
        )
        time.sleep(2)
        response_2 = get_response(
            api=os.getenv('api_key'),
            model_version=model,
            is_definition=False,
            text=text,
        )
        time.sleep(2)

        df.loc[i,'id'] = file_name
        df.loc[i,'definition'] = response_1
        df.loc[i,'others'] = response_2

    save_path = f"D:/Users/migi/Dropbox/Chen/work/522/5_LLM/repsonse/{model}.xlsx"
    df.to_excel(save_path, index=False)


def get_text(path):
    title = pp.parse_pubmed_xml(path)['full_title']
    abstract = pp.parse_pubmed_xml(path)['abstract']
    paragraph = pp.parse_pubmed_paragraph(path, all_paragraph=True)
    caption = pp.parse_pubmed_caption(path)
    text = title + '\n' + abstract + '\n'
    for para in paragraph:
        content = para['text']
        if len(content) > 1:
            text += content.rstrip("\n ") + '\n'
    for cap in caption:
        content = cap['fig_caption']
        if len(content) > 1:
            text += content.rstrip("\n ") + '\n'
    text = html.unescape(text)
    text = text.replace("\n\n\n", "")
    return text

if __name__ == "__main__":
    main()