from transformers import TrainingArguments
from dataclasses import dataclass, field
from typing import Optional, List
@dataclass
class model_config:
    #   model_config   #
    base_model: str = field(
        default='../../../share/LLM-base/Llama-3-8B', metadata={"help": "base model directory."}#../../../share/LLM-base/Llama-3-8B
    )
    tokenizer: str = field(
        default='../../../share/LLM-base/Llama-3-8B', metadata={"help": "load tokenizer directory."}#../../../share/LLM-base/Llama-3-8B
    )
    model_max_length: int = field(
        default=512,
        metadata={"help": "Maximum sequence length. Sequences will be right padded (and possibly truncated)."}
    )
    trust_remote_code: Optional[bool] = field(
        default=False,
        metadata={"help": "Enable unpickling of arbitrary code in AutoModelForCausalLM#from_pretrained."}
    )
    use_auth_token: Optional[bool] = field(default=False, metadata={"help": "Enables using Huggingface auth token from Git Credentials."})
    use_cache: Optional[bool] = field(default=False, metadata={"help": "Whether to use cache."})


@dataclass
class train_config(TrainingArguments):
    #  train_config  #
    num_train_epochs: int = field(
        default=2,
        metadata={"help": "The number of epochs for training."}
    )
    xformers: bool = field(
        default=True,
        metadata={"help": "Enables using xformers or not."}
    )
    flash_attn: bool = field(
        default=False,
        metadata={"help": "Enables using flash attention or not."}
    )
    output_dir: str = field(
        default='./generate_blog/checkpoint_short_text',
        metadata={"help": 'The output dir for logs and checkpoints'}
    )
    output_dir2: str = field(
        default='./generate_blog/checkpoint_style',
        metadata={"help": 'The output dir for logs and checkpoints'}
    )
    per_device_train_batch_size: int = field(
        default=4,
        metadata={"help": 'The training batch size per GPU. Increase for better speed.'}
    )
    gradient_accumulation_steps: int = field(
        default=2,
        metadata={"help": 'How many gradients to accumulate before to perform an optimizer step'}
    )
    load_best_model_at_end: bool = field(
        default=False,
        metadata={"help": 'If load best model(make sure eval_dataset_size > 0).'}
    )
    logging_steps: int = field(
        default=2,
        metadata={"help": 'The frequency of update steps after which to log the loss'}
    )
    gradient_checkpointing: bool = field(
        default=True,
        metadata={"help": 'Use gradient checkpointing. You want to use this.'}
    )
    cache_dir: Optional[str] = field(default=None)
    train_on_source: Optional[bool] = field(default=False,metadata={"help": "Whether to train on the input in addition to the target text."})
    full_finetune: bool = field(default=False,metadata={"help": "Finetune the entire model without adapters."})
    adam8bit: bool = field(default=False,metadata={"help": "Use 8-bit adam."})
    double_quant: bool = field(default=True,metadata={"help": "Compress the quantization statistics through double quantization."})
    quant_type: str = field(default="nf4",metadata={"help": "Quantization data type to use. Should be one of `fp4` or `nf4`."})
    bits: int = field(default=4,metadata={"help": "How many bits to use."})
    max_memory_MB: int = field(default=80000,metadata={"help": "Free memory per gpu."})
    report_to: str = field(default='none',metadata={"help": "To use wandb or something else for reporting."})
    optim: str = field(default='adamw_torch', metadata={"help": 'The optimizer to be used'})
    max_steps: int = field(default=-1, metadata={"help": 'How many optimizer update steps to take'})
    weight_decay: float = field(default=0.0, metadata={"help": 'The L2 weight decay rate of AdamW'}) # use lora dropout instead for regularization if needed
    learning_rate: float = field(default=0.0002, metadata={"help": 'The learnign rate'})
    remove_unused_columns: bool = field(default=False, metadata={"help": 'Removed unused columns. Needed to make this codebase work.'})
    max_grad_norm: float = field(default=0.3, metadata={"help": 'Gradient clipping max norm. This is tuned and works well for all models tested.'})
    predict_with_generate: bool = field(default=False, metadata={"help": 'Whether to use predict_with_generate.'})
    do_train: bool = field(default=True, metadata={"help": 'To train or not to train, that is the question?'})
    lr_scheduler_type: str = field(default='cosine', metadata={"help": 'Learning rate schedule. Constant a bit better than cosine, and has advantage for analysis'})
    warmup_ratio: float = field(default=0.03, metadata={"help": 'Fraction of steps to do a warmup for'})
    group_by_length: bool = field(default=False, metadata={"help": 'Group sequences into batches with same length. Saves memory and speeds up training considerably.'})
    save_strategy: str = field(default='steps', metadata={"help": 'When to save checkpoints'})
    save_steps: int = field(default=250, metadata={"help": 'How often to save a model'})
    save_total_limit: int = field(default=40, metadata={"help": 'How many checkpoints to save before the oldest is overwritten'})
    gradient_checkpointing_kwargs: List[bool] = field(default_factory=lambda: {"use_reentrant": True}, metadata={"help": 'debug for warning'})

@dataclass
class lora_config:
    #   lora_config   #
    r: int = field(
        default=8, metadata={"help": 'lora_r'} #8
    )
    lora_alpha: int = field(
        default=16, metadata={"help": 'lora_alpha'}
    )
    lora_dropout: float = field(
        default=0.05, metadata={"help": 'lora_dropout'}
    )
    lora_target_modules: List[str] = field(
        default_factory=lambda: ["q_proj", "v_proj", "o_proj", "gate_proj", "down_proj", "up_proj"], metadata={"help": 'lora_target_modules'}
    )
    lora_bias: str = field(
        default="none", metadata={"help": 'use lora_bias'}
    )
    task_type: str = field(
        default="CAUSAL_LM", metadata={"help": 'task_type'}
    )


@dataclass
class data_config:
    #   data_config   #
    data_path: str = field(
        default="data/modified_short_text.json", metadata={"help": "Path to the training data."}
    )
    eval_data_path: str = field(default=None, metadata={"help": "Path to the evaluation data."})
    eval_dataset_size: int = field(
        default=64, metadata={"help": "Size of validation dataset."}
    )
    max_train_samples: Optional[int] = field(default=None, metadata={"help": "For debugging purposes or quicker training, truncate the number of training examples to this value if set."})
    max_eval_samples: Optional[int] = field(default=None, metadata={"help": "For debugging purposes or quicker training, truncate the number of evaluation examples to this value if set."},)
    source_max_len: int = field(default=1024, metadata={"help": "Maximum source sequence length. Sequences will be right padded (and possibly truncated)."},)
    target_max_len: int = field(default=256, metadata={"help": "Maximum target sequence length. Sequences will be right padded (and possibly truncated)."},)
    max_train_samples: Optional[int] = field(default=None, metadata={"help": "For debugging purposes or quicker training, truncate the number of training examples to this value if set."},)
    max_eval_samples: Optional[int] = field(default=None, metadata={"help": "For debugging purposes or quicker training, truncate the number of evaluation examples to this value if set."},)
    dataset_format: str = field(default="alpaca", metadata={"help": "dataset_format."})
