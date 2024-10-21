import pandas as pd
import os
from rouge import Rouge
from bert_score import BERTScorer
from transformers import BertTokenizer,BertModel
import sys
sys.setrecursionlimit(10000)



def calculate_rouge_scores(nw_text, w_text):
    rouge = Rouge()
    return [rouge.get_scores(mt, rt)[0]['rouge-l']['f'] * 100 for mt, rt in zip(nw_text, w_text)]  # rouge-l / rouge-2



def truncate_text(text, max_length=512):
    tokens = tokenizer.tokenize(text)[:max_length]
    return tokenizer.convert_tokens_to_string(tokens)

model_path = "/share/LLM-base/bert-base-uncased"
#
model = BertModel.from_pretrained(model_path)
tokenizer = BertTokenizer.from_pretrained('/share/LLM-base/bert-base-uncased')
# scorer = BERTScorer(model_type="bert-base-uncased", lang='en')
scorer = BERTScorer(model_type=None, lang='en', tokenizer=tokenizer, model=model)
folder_path = './blog'
results = {}


for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        print(file_path)
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
        nw_text = df['NW-text'].tolist()  # un-watermarked text
        w_text = df['W-text'].tolist()  # watermarked text


        scores = []
        for w, nw in zip(w_text, nw_text):
            if isinstance(w, str) and isinstance(nw, str):
                w_truncated = truncate_text(w)
                nw_truncated = truncate_text(nw)
                BERTScore1, BERTScore2, BERTScore3 = scorer.score([w_truncated], [nw_truncated])
                BERTScore3 = BERTScore3.item() * 100
                scores.append(BERTScore3)
        if scores:
            results[filename] = scores



scores_df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in results.items()]))
scores_df.to_csv('BERTScore.csv', index=False)



for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        print(file_path)
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
        nw_text = df['NW-text'].tolist()
        w_text = df['W-text'].tolist()

        rouge_score = calculate_rouge_scores(nw_text, w_text)
        results[filename] = rouge_score



max_length = max(len(scores) for scores in results.values())
final_df = pd.DataFrame.from_dict(results, orient='index').transpose()
final_df = final_df.apply(lambda x: pd.Series(x.dropna().values))
final_df.to_csv('ROUGE.csv', index=False)
