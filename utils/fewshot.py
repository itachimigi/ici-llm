import pandas as pd
import random
from pubmed_parser import parse_pubmed_xml, parse_pubmed_paragraph, parse_pubmed_caption
import html
import os

def get_fewshot_input(is_definition, text):

    sample_definition, sample_others = create_sample()

    system_message, user_message = get_message(is_definition, text)

    if is_definition:
        user_message = sample_definition + "Input:\n\n" + user_message + "\n\nOutput:"
    else: 
        user_message = sample_others + "Input:\n\n" + user_message + "\n\nOutput:"
    
    return system_message, user_message


def create_sample():
    format_definition = "{{'Predictor': '{predictor}', " \
    "'Feature': '{feature}', " \
    "'Model': '{model}'}}"

    format_others = "{{'Data Required': '{data_required}', " \
    "'Biosample Required': '{biosample_required}', " \
    "'Cancer': '{cancer}', " \
    "'Species': '{species}', " \
    "'Treatment': '{treatment}', " \
    "'Cohort Details': '{cohort}', " \
    "'Target Outcome': '{outcome}', " \
    "'Correlation with Efficacy': '{correlation}'}}"

    ici_path = "data/ici_efficacy.xlsx"
    ici = pd.read_excel(ici_path)
    train_base = "outputs/cleaned_xml/train/"
    train_papers = os.listdir(train_base)
    papers = random.sample(train_papers, 3)
    sample_definition = ''''''
    sample_others = ''''''

    for paper in papers:
        path = train_base + paper
        id = paper.split(".")[0]
        text = get_text(path)
        _, user_message_1 = get_message(True, text)
        sample_definition += f"Input:\n\n{user_message_1}\n\n"
        information = ici.loc[ici['id']==id,]
        index = information.index[0]
        response_1 = format_definition.format(
            predictor=information.loc[index,'Predictor(s)'],
            feature=information.loc[index,'Feature(s)'],
            model=information.loc[index,'Model'],
        )
        sample_definition += f"Output:\n\n{response_1}\n\n"

        _, user_message_2 = get_message(False, text)
        sample_others += f"Input:\n\n{user_message_2}\n\n"
        response_2 = format_others.format(
            data_required=information.loc[index,'Data Required'],
            biosample_required=information.loc[index,'Biosample Required'],
            cancer=information.loc[index,'Cancer'],
            species=information.loc[index,'Species'],
            treatment=information.loc[index,'Treatment'],
            cohort=information.loc[index,'Cohort Details'],
            outcome=information.loc[index,'Target Outcome'],
            correlation=information.loc[index,'Correlation with Efficacy'],
        )
        sample_others += f"Output:\n\n{response_2}\n\n"
    
    return sample_definition, sample_others

        
def get_message(is_definition, text):

    system_w_source = "You are an assistant that extracts information from papers about immune checkpoint inhibitors. " \
    "If an answer is provided, it must be annotated with a source text that supports or provides evidence for the answer."

    system_wo_source = "You are an assistant that extracts information from papers about immune checkpoint inhibitors."

    template = "Please take the following considerations, then extract information from the input paper " \
    "after 'Context: ' to generate result using the given JSON format.\n\n" \
    "Considerations: {consideration}\n\nFormat: {format}\n\nContext: {text}"

    consideration_definition = "1. The input paper provides predictor(s) to predict the immunotherapy response, " \
    "which should be an integral model or single biomarker; 2. The feature should be the final selected features, " \
    "and there might be additional information about the definition/calculation/determination of the features; " \
    "3. The model should be how the predictive model trained or the predictor used to predict immunotherapy response."

    consideration_others = "1. Data Required is the input data that is required for the calculation of biomakers or features, e.g. Protein Level - ELISA Test; " \
    "2. Biosample is required to acquire the input data, which could be tumor tissue, normal tissue, blood sample, stool sample or not applicable; " \
    "3. Cancer is cancer type that demonstrated correlation between the predictor and the response in cohort study, e.g. Lung - Non-small Cell Lung Cancer; " \
    "4. Species should be Human, Mouse, which is the species involved in the discovery and testing of the predictors; " \
    "5. Treatment is the drug that demonstrates correlation between the predictor and the response, should be anti-{Checkpoint: PD-L1 OR PD-1 OR CTLA-4} - {drug name, if applicable} " \
    "6. Cohort Details are datasets(cancer type, patient size) that are used to discover/test/validate the predictor; " \
    "7. Target Outcome is indicator of the treatment in achieving a desired clinical outcome, e.g. overall survival, progression-free survival, RECIST; " \
    "8. Correlation of the predictor output (value) with ICI efficacy should be positive or negative, " \
    "positive if higher value in responders and negative if lower value in responders."

    format_definition = "{'Predictor': 'the name of predictor. (Source: ...)', " \
    "'Feature': 'the features. (Source: ...)', " \
    "'Model': 'description of the model. (Source: ...)'}"

    format_others = "{'Data Required': '...', " \
    "'Biosample Required': '...', " \
    "'Cancer': '...', " \
    "'Species': '...', " \
    "'Treatment': '...', " \
    "'Cohort Details': '...', " \
    "'Target Outcome': '...', " \
    "'Correlation with Efficacy': '...'}"

    if is_definition:
        return system_w_source, template.format(
            consideration=consideration_definition, format=format_definition, text=text,
        )
    else:
        return system_wo_source, template.format(
            consideration=consideration_others, format=format_others, text=text,
        )


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