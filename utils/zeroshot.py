import os
from openai import OpenAI


def get_response(api, model_version, is_definition, text):

    system_message, user_message = get_message(is_definition, text)

    client = OpenAI(
        api_key=api,
    )

    completion = client.chat.completions.create(

        model=model_version,
        temperature=0.1,
        response_format={ "type": "json_object" },
        
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": user_message,
            },

        ]

    )

    response = completion.choices[0].message.content
    return response

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