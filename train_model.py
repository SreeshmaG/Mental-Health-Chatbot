from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
import json

# Load dataset
with open("mental_health_dataset.json", "r") as f:
    data = json.load(f)

# Convert to Hugging Face Dataset
dataset = Dataset.from_dict({
    "user": [item["user"] for item in data],
    "bot": [item["bot"] for item in data]
})

# Split into train and test
train_test = dataset.train_test_split(test_size=0.1)
train_dataset = train_test["train"]
eval_dataset = train_test["test"]

# Load model and tokenizer
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

tokenizer.pad_token = tokenizer.eos_token  # avoid padding token errors

def tokenize_function(examples):
    inputs = [f"User: {u}\nBot: {b}" for u, b in zip(examples["user"], examples["bot"])]
    tokenized = tokenizer(inputs, truncation=True, padding="max_length", max_length=128)
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

train_dataset = train_dataset.map(tokenize_function, batched=True)
eval_dataset = eval_dataset.map(tokenize_function, batched=True)

training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=10
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset
)

trainer.train()

# Save model
model.save_pretrained("mental-health-chatbot-model")
tokenizer.save_pretrained("mental-health-chatbot-model")
