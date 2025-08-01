# 1. Install and Login (run these in your terminal/notebook first)
# pip install datasets huggingface_hub
# huggingface-cli login

from datasets import load_dataset
import pprint

# 2. Load the source dataset
print("Loading the original dataset...")
original_repo_id = "ShenLab/MentalChat16K"
original_dataset = load_dataset(original_repo_id, split="train")

print("\nOriginal dataset features:")
print(original_dataset.features)
print("\nOriginal example:")
pprint.pprint(original_dataset[0])


# 3. Define the transformation function
def transform_to_conversational(example):
    """Transforms a single Dolly example to the conversational format."""
    user_content = example['input']

    return {
        "conversations": [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": example['output']}
        ]
    }

# 4. Apply the transformation
print("\nApplying transformation...")
transformed_dataset = original_dataset.map(
    transform_to_conversational,
    remove_columns=original_dataset.column_names
)

print("\nTransformed dataset features:")
print(transformed_dataset.features)
print("\nTransformed example:")
pprint.pprint(transformed_dataset[0])


# 5. Push to the Hub
# !!! IMPORTANT: Replace 'your-username' with your actual HF username !!!
new_repo_id = "nnikolovskii/chat-med"

print(f"\nPushing the transformed dataset to the Hub: {new_repo_id}")
# This creates a repository and uploads the data
transformed_dataset.push_to_hub(new_repo_id)

print("\nTransformation complete! Your dataset is now available on the Hub.")