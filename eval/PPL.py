import re
import torch
import math
import csv
import os
import numpy as np
import pandas as pd
from transformers import GenerationConfig, AutoModelForCausalLM, AutoTokenizer



def ppl(text, model):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        max_length=1024,
        truncation=True
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss
        perplexity = math.exp(loss.item())

    return perplexity



if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

base_model: str = "../../../share/LLM-base/Llama-3-8B"
load_8bit: bool = False


if device == "cuda":
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        load_in_8bit=False,
        torch_dtype=torch.float16,
        device_map="auto",
    )

else:
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        device_map={"": device},
        low_cpu_mem_usage=True,
    )
tokenizer = AutoTokenizer.from_pretrained(
        base_model,
        use_fast=False,
    )

if 'LLaMA3-8B' in base_model:
    print('Adding special tokens <unk=128002>.')
    model.config.unk_token_id = tokenizer.unk_token_id = 128002
    tokenizer.pad_token_id = tokenizer.unk_token_id
    model.config.unk_token_id = tokenizer.unk_token_id
    model.config.pad_token_id = tokenizer.pad_token_id

if 'LLaMA2-7B' in base_model:
    tokenizer.pad_token_id = tokenizer.unk_token_id
    model.config.unk_token_id = tokenizer.unk_token_id
    model.config.pad_token_id = tokenizer.pad_token_id



folder_path = './gpt'
output_file = 'PPL_gpt.csv'
ppl_dict = {}
max_length = 0


for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        print(file_path)
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
        print(df.columns)
        text_column = df['W-text'].tolist()
        PPL_ALL = []
        i = 1

        # print(f"============ File: {filename} ==============")
        for text in text_column:
            print(f"============ File: {filename} | Position: {i} ==============")

            PPL_average = ppl(text, model)
            print(PPL_average)
            PPL_ALL.append(PPL_average)
            i += 1

        ppl_dict[filename] = PPL_ALL
        max_length = max(max_length, len(PPL_ALL))


for key in ppl_dict:
    current_length = len(ppl_dict[key])
    if current_length < max_length:
        ppl_dict[key].extend([np.nan] * (max_length - current_length))


df_ppl = pd.DataFrame(ppl_dict)
df_ppl.to_csv(output_file, index=False)

print(f"{output_file}")
