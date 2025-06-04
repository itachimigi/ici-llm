# Developing biomedical knowledgebases from the literature using large language models – a systematic assessment
This repository contains the code for reproducing all the results in the paper "Developing biomedical knowledgebases from the literature using large language models – a systematic assessment".

# Workflow
![ici-llm](workflow.svg)

# Prompt design
![image](https://github.com/user-attachments/assets/2e59787b-4d01-421b-8ef1-fdbdd46eb81d)

# 1. Clean XML
Preprocess the XML files to prevent parsing errors.

```bash
python src/xml_processing.py \
  --input-dir data/xml \
  --output-dir outputs/cleaned_xml
```

# 2. Get Responses
For each publication, we extracted its title, abstract, main text, and figure captions, and concatenated them into a single text string. We evaluated the performance of five LLMs (Supplementary Table 3), namely GPT-3.5 turbo (gpt-3.5-turbo-0125), GPT-4 turbo (gpt-4-turbo-2024-04-09), GPT-4o (gpt-4o-2024-05-13), DeepSeek-R1 (DeepSeek-R1-0528) and Gemini-2.5 (gemini-2.5-flash-preview-05-20).

```bash
python src/query.py \
  --xml-dir outputs/cleaned_xml \
  --out-dir outputs/responses \
  --model 'gpt-3.5-turbo-0125' \
  --api-key 'sk-xxx' \
  --mode 'zero'
```

# 3. Evaluate
For each answer produced by an LLM, we compared it with our manual curation result and quantified their similarity using six standard measures, namely BLEU, ROUGE-1, ROUGE-2, ROUGE-L, BERTScore, and Cosine similarity.

```bash
python src/metrics_evaluation.py \
  --pred 'RF16' \
  --ref '16 Feature Random Forest Classifier' \
  --api-key 'sk-xxx' \
  --out-dir outputs/score
```
