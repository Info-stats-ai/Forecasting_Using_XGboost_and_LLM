# scripts/run_structuring.py

import json
from pathlib import Path
import pandas as pd
from transformers import T5ForConditionalGeneration, T5Tokenizer

def main():
    """
    This is the main production script to structure our text data.
    It reads the 900+ text files, uses an AI model to extract key information,
    and saves the final, clean data to a CSV file.
    """
    print("--- Starting AI Data Structuring Pipeline ---")
    
    # --- Configuration ---
    # Define the main directory for all our data.
    DATA_DIR = Path("data")
    
    # Define the input folder where our .txt files are located.
    TEXT_INPUT_DIR = DATA_DIR 
    
    # Define the path for our final, structured output file.
    STRUCTURED_CSV_PATH = DATA_DIR / "structured_data.csv"
    
    # --- Step 1: Load the AI Model ---
    # We will use 'google/flan-t5-large', a powerful instruction-following model.
    model_name = "google/flan-t5-large"
    print(f"\n--- Step 1: Loading the AI model '{model_name}' onto the CPU ---")
    
    # Load the main model and its tokenizer, which prepares text for the AI.
    model = T5ForConditionalGeneration.from_pretrained(model_name, device_map="cpu")
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    print("✅ AI model loaded successfully.")

    # --- Step 2: Find and Process the Text Files ---
    print(f"\n--- Step 2: Starting the data structuring process ---")
    
    # Find all files ending in .txt inside our data directory.
    text_files_to_process = sorted(list(TEXT_INPUT_DIR.glob("*.txt")))
    
    # A safety check to ensure we found the files before starting the main loop.
    if not text_files_to_process:
        print(f"❌ CRITICAL ERROR: No .txt files were found in the '{TEXT_INPUT_DIR}' folder.")
        print("Please ensure your 900 .txt files have been uploaded to the 'data' folder.")
        return
        
    print(f"   - Success! Found {len(text_files_to_process)} text files to process.")
    
    # This list will hold the structured data for each file.
    all_structured_data = []

    # Loop through every text file we found.
    for i, filepath in enumerate(text_files_to_process):
        if (i + 1) % 25 == 0 or i == 0:
            print(f"  Processing file {i+1}/{len(text_files_to_process)}: {filepath.name}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # This is the instruction we give to the AI model.
        prompt = f"From the following document, extract project_type, summary_description, total_cost (as a number or null), and line_items (as a list of objects or an empty list). Provide the output as a valid JSON object. DOCUMENT: --- {content} --- JSON OUTPUT:"
        
        try:
            # Prepare the prompt for the model, telling it to truncate if it's too long.
            input_ids = tokenizer(
                prompt, 
                return_tensors="pt", 
                max_length=512,      # The model's non-negotiable limit
                truncation=True      # The instruction to safely shorten oversized text
            ).input_ids.to("cpu")

            # Ask the AI to generate the structured text.
            outputs = model.generate(input_ids, max_length=512)
            
            # Decode the AI's output from numbers back into human-readable text.
            result_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Convert the AI's text string into a real JSON object.
            structured_data = json.loads(result_text)
            
            # Add the original filename for our records.
            structured_data['source_file'] = filepath.name
            
            # Add the clean data to our master list.
            all_structured_data.append(structured_data)
            
        except Exception as e:
            print(f"   - SKIPPING {filepath.name}: Could not process with AI. Reason: {e}")
            
    # --- Step 3: Save the Final CSV File ---
    if all_structured_data:
        print("\n✅ Processing complete! Saving results to a CSV file...")
        
        # Convert our list of structured data into a table.
        final_dataframe = pd.DataFrame(all_structured_data)
        
        # Save the table to the final CSV file.
        final_dataframe.to_csv(STRUCTURED_CSV_PATH, index=False, encoding='utf-8')
        
        print(f"✅✅✅ All tasks complete! ✅✅✅")
        print(f"Successfully created '{STRUCTURED_CSV_PATH}' with {len(final_dataframe)} rows.")

if __name__ == "__main__":
    main()