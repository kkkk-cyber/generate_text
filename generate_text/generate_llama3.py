import torch
import json
import re
import argparse
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, HfArgumentParser, GenerationConfig
from peft import PeftModel
from typing import Union
import queue
from generate_text.config_module import (
    model_config,
    train_config,
    lora_config,
    data_config,
)

class prompter(object):
    __slots__ = "template"

    def __init__(self, template):
        with open(template) as fp:
            self.template = json.load(fp)

    def generate_prompt(
            self,
            instruction: str,
            input: Union[None, str] = None,
            output: Union[None, str] = None,
    ) -> str:
        if input:
            res = self.template["prompt_input"].format(
                instruction=instruction, input=input
            )
        else:
            res = self.template["prompt_no_input"].format(
                instruction=instruction
            )

        if output:
            res = f"{res}{output}"

        return res

    def get_response(self, output: str) -> str:
        result = output.split(self.template["response_split"])[1].strip()
        result = re.sub(r'\[.*?\]', '', result)
        result = re.sub(r'\(.*?\)', '', result)
        keyword="\n"
        keyword_position = result.find(keyword)
        if keyword_position != -1:
            # 获取关键词之前的内容
            text= result[:keyword_position]
        else:
            text = result
        hash_indices = [i for i, char in enumerate(text) if char == '#']

        # 如果#的数量少于3个，直接返回原文本
        if len(hash_indices) < 3:
            print(text)
            return text
        third_hash_index = hash_indices[2]
        # 输出第三个#之前的内容

        return text[:third_hash_index]

    def get_style(self, output: str) -> str:
        result = output.split(self.template["response_split"])[1].strip()
        result = re.sub(r'\[.*?\]', '', result)
        result = re.sub(r'\(.*?\)', '', result)

        keyword="Response:"
        keyword_position = result.find(keyword)
        if keyword_position != -1:
            print(result)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(result)
        else:
            print("Style rewriting error, please check the output format.")
        return result

def generate_blog(input,style):
    if torch.cuda.is_available():
        device = torch.device('cuda:0')
    else:
        device = torch.device('cpu')
    # 创建 parser 并指定数据类
    parser = HfArgumentParser(
        (model_config, train_config, lora_config, data_config)
    )

    # 从命令行解析参数到数据类
    (
        model_args,
        train_args,
        lora_args,
        data_args,
    ) = parser.parse_args_into_dataclasses()

    args = argparse.Namespace(
        **vars(model_args), **vars(train_args), **vars(lora_args), **vars(data_args)
    )

    # 导入模型
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        load_in_8bit=True,  # 修改为True可以加快运行速度和优化显存占用，修改为False则运行效果更好
        device_map=device,
        torch_dtype=torch.float16,
    )

    tokenizer = AutoTokenizer.from_pretrained(
        args.tokenizer,
        padding_side="right",
        legacy=False,
    )
    if 'Llama-3' in args.base_model:
        # print('Adding special tokens <unk=128002>.')
        tokenizer.unk_token_id = 128002

    tokenizer.pad_token_id = tokenizer.unk_token_id
    model.config.unk_token_id = tokenizer.unk_token_id
    model.config.pad_token_id = tokenizer.eos_token_id

    template_path = "./generate_blog/prompt_SFT.json"
    Prompter = prompter(template_path)

    @torch.no_grad()
    def evaluate(
            instruction,
            input,
            temperature=0.4, #0.1
            top_p=0.7, #0.9
            top_k=40,  #50
            repetition_penalty=1.2,
            max_new_tokens=128,
            do_sample=True,
    ):
        generation_params = GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            do_sample=do_sample,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id,
        )

        prompt = Prompter.generate_prompt(instruction, input)
        input_tokenizer = tokenizer(prompt, return_tensors="pt")
        input_ids = input_tokenizer["input_ids"].to(device)
        print(prompt)


        # 使用cuda进行forward计算输出
        with torch.no_grad():
            if "Rewrite" in instruction:
                # 把lora和原模型组合
                if os.path.exists(args.output_dir2):
                    model_rewrite = PeftModel.from_pretrained(
                        model,
                        args.output_dir2,
                        torch_dtype=torch.float16,
                    ).to(device)
                print("rewrite text....")
                # 生成文本....
                generation_output = model_rewrite.generate(
                    input_ids=input_ids,
                    generation_config=generation_params,
                    return_dict_in_generate=True,
                    output_scores=True,
                    max_new_tokens=1024,
                )
            else:
                if os.path.exists(args.output_dir):
                    model_generate = PeftModel.from_pretrained(
                        model,
                        args.output_dir,
                        torch_dtype=torch.float16,
                    ).to(device)
                print("generate text....")
                # 改写文本....
                generation_output = model_generate.generate(
                    input_ids=input_ids,
                    generation_config=generation_params,
                    return_dict_in_generate=True,
                    output_scores=True,
                    max_new_tokens=128,
                )

        s = generation_output.sequences[0]
        output = tokenizer.decode(s, skip_special_tokens=True)
        if "Rewrite" in instruction:
            return Prompter.get_style(output)
        else:

            return Prompter.get_response(output)

    instruction="This is your identity information, please Select a message and write a Twitter post. Use a natural tone and style, and avoid overly formal or rigid expressions. Add some common colloquial expressions and emotional words to make sentences closer to human communication."
    text1 = evaluate(instruction,input)
    input_style ="Context:"+text1
    instruction_style="Task:Rewrite the sentence style without changing the content of the sentence.The target style:"+style+". Let's think about it step by step. First, describe the style. Then, describe the language pattern of this style. Finally, output the rewritten sentence without explanation."
    text2 = evaluate(instruction_style,input_style,temperature=0.2,top_p=0.75,top_k=40,repetition_penalty=1.1)
    return text2
if __name__ == "__main__":
    main()
