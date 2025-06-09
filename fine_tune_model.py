import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextDataset,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments
)
import os

# --- Configuration ---
BASE_MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
LEARNING_DATA_FILE = "learning_data.txt"
FINE_TUNED_MODEL_DIR = "tinyllama_finetuned"

# Ensure output directory exists
if not os.path.exists(FINE_TUNED_MODEL_DIR):
    os.makedirs(FINE_TUNED_MODEL_DIR)

def main():
    print("Starting fine-tuning process...")

    # 1. Load base model and tokenizer
    print(f"Loading base model: {BASE_MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL_NAME)

    # Ensure pad_token_id is set if eos_token_id is used for padding
    if tokenizer.pad_token_id is None:
        print("Setting pad_token_id to eos_token_id.")
        tokenizer.pad_token_id = tokenizer.eos_token_id
        model.config.pad_token_id = model.config.eos_token_id


    # 2. Prepare dataset
    print(f"Loading learning data from: {LEARNING_DATA_FILE}")
    if not os.path.exists(LEARNING_DATA_FILE) or os.path.getsize(LEARNING_DATA_FILE) == 0:
        print(f"'{LEARNING_DATA_FILE}' is empty or does not exist. No data to fine-tune on. Exiting.")
        return

    # For "continue pre-training" on raw text, TextDataset is suitable.
    # It tokenizes the entire file.
    # Reduce block_size for small datasets.
    # Also, ensure the tokenizer has a pad token if not already set,
    # although it was handled earlier for the model, TextDataset might also need it.
    if tokenizer.pad_token is None:
        print("Tokenizer does not have a pad token. Setting pad_token to eos_token.")
        tokenizer.pad_token = tokenizer.eos_token

    # Check minimum content length (e.g., more tokens than block_size)
    # This is a heuristic. A more robust way would be to count tokens.
    MIN_FILE_SIZE_BYTES = 64 # Arbitrary small number, adjust as needed
    if os.path.getsize(LEARNING_DATA_FILE) < MIN_FILE_SIZE_BYTES:
        print(f"Warning: '{LEARNING_DATA_FILE}' is very small. Fine-tuning might not be effective or may fail.")
        # Decide if to exit or proceed. For now, proceed with caution.

    dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=LEARNING_DATA_FILE,
        block_size=32  # Reduced block_size for smaller datasets
    )

    # It's crucial to check if TextDataset actually loaded any data.
    # len(dataset.examples) might not be the most reliable way for TextDataset before training.
    # A better check is after the dataloader is prepared or by trying to get an item.
    # For now, we rely on the later check or if Trainer itself complains.
    print(f"TextDataset initialized. Number of blocks (examples) if data > block_size: {len(dataset.examples)}")
    if len(dataset.examples) == 0:
        print("No examples were created by TextDataset. This can happen if the learning data file is smaller than the block_size or empty after tokenization. Exiting.")
        return

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # We are doing Causal LM, not Masked LM
    )
    print("Dataset and data collator prepared.")

    # 3. Configure Training Arguments
    # These are very minimal for CPU execution and quick testing.
    # Adjust per_device_train_batch_size and num_train_epochs based on available resources and data size.
    # Gradient_accumulation_steps can help simulate larger batch sizes if memory is very limited.
    training_args = TrainingArguments(
        output_dir=os.path.join(FINE_TUNED_MODEL_DIR, "training_checkpoints"),
        overwrite_output_dir=True,
        num_train_epochs=1,  # Start with 1 epoch for a quick test
        per_device_train_batch_size=1, # Smallest possible batch size
        save_steps=50, # Save a checkpoint every X steps (adjust as needed)
        save_total_limit=1, # Only keep the last checkpoint
        logging_steps=10,
        # --- Important for CPU execution ---
        no_cuda=True, # Explicitly disable CUDA
        # use_cpu=True, # Alternative way for older transformers versions, no_cuda is preferred
        # --- End Important for CPU execution ---
        # Report to none to avoid issues with wandb/tensorboard if not configured
        report_to="none"
    )
    print("Training arguments configured.")

    # 4. Create Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=dataset
    )
    print("Trainer created.")

    # 5. Start Fine-tuning
    print("Starting fine-tuning. This may take a long time on CPU...")
    try:
        trainer.train()
        print("Fine-tuning completed.")
    except Exception as e:
        print(f"Error during training: {e}")
        # Potentially log more details or handle specific errors
        return # Exit if training fails

    # 6. Save the fine-tuned model and tokenizer
    print(f"Saving fine-tuned model to: {FINE_TUNED_MODEL_DIR}")
    try:
        model.save_pretrained(FINE_TUNED_MODEL_DIR)
        tokenizer.save_pretrained(FINE_TUNED_MODEL_DIR)
        print("Model and tokenizer saved successfully.")
    except Exception as e:
        print(f"Error saving model/tokenizer: {e}")

if __name__ == "__main__":
    # Check if running on CPU and warn if not explicitly set (though TrainingArguments handles it)
    if torch.cuda.is_available():
        print("WARNING: CUDA is available, but this script is configured for CPU fine-tuning via TrainingArguments (no_cuda=True).")
        print("If you intended to use GPU, please modify TrainingArguments.")
    else:
        print("CUDA not available. Proceeding with CPU fine-tuning.")

    main()
