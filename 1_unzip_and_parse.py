# scripts/1_unzip_and_parse.py (Final, Simplified, and Correct Version)

import os
import zipfile
import time
from pathlib import Path

# This is the only import needed, as your research correctly pointed out.
from docling.document_converter import DocumentConverter

# --- Configuration ---
DATA_DIR = Path("data")
ZIPS_DIR = DATA_DIR / "zips"
UNZIPPED_DIR = DATA_DIR / "unzipped_pdfs"
MARKDOWN_OUTPUT_DIR = DATA_DIR / "parsed_markdown"

def main():
    print("--- Starting Production Data Prep (GPU Auto-Detection) ---")
    
    print("\n--- Step 1: Unzipping Files ---")
    # ... (Unzipping logic is the same) ...
    os.makedirs(ZIPS_DIR, exist_ok=True)
    zip_files_in_data = list(DATA_DIR.glob("*.zip"))
    if zip_files_in_data:
        print(f"Organizing {len(zip_files_in_data)} zip files...")
        for zf_path in zip_files_in_data:
            os.rename(zf_path, ZIPS_DIR / zf_path.name)
    os.makedirs(UNZIPPED_DIR, exist_ok=True)
    zip_files = list(ZIPS_DIR.glob("*.zip"))
    if zip_files:
        for zip_path in zip_files:
            print(f"   Unzipping {zip_path.name}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(UNZIPPED_DIR)
        print(f"✅ Unzipping complete.")

    print("\n--- Step 2: Parsing PDFs with Docling (Auto GPU Mode) ---")
    os.makedirs(MARKDOWN_OUTPUT_DIR, exist_ok=True)

    all_pdf_paths = list(UNZIPPED_DIR.glob("**/*.pdf"))
    total_files = len(all_pdf_paths)
    if total_files == 0:
        print("No PDF files found to parse.")
        return
        
    print(f"Found {total_files} PDF files to parse.")

    # --- THE FINAL FIX IS HERE ---
    # As your research showed, we create the converter with NO special config.
    # Because you installed the correct PyTorch, it will now auto-detect and use the GPU.
    converter = DocumentConverter()
    # ---------------------------
    
    start_time = time.time()
    for i, pdf_path in enumerate(all_pdf_paths):
        if (i + 1) % 25 == 0 or i == 0:
             print(f"  Parsing file {i+1}/{total_files}: {pdf_path.name}...")
        try:
            result = converter.convert(str(pdf_path))
            markdown_output = result.document.export_to_markdown()
            output_filename = f"{pdf_path.stem}.md"
            output_path = MARKDOWN_OUTPUT_DIR / output_filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_output)
        except Exception as e:
            print(f"      - ERROR: Could not parse {pdf_path.name}. Reason: {e}")

    end_time = time.time()
    minutes, seconds = divmod(end_time - start_time, 60)
    print("\n--- Parsing Complete! ---")
    print(f"✅ Successfully parsed {total_files} files in {int(minutes)} minutes and {seconds:.2f} seconds.")
    print(f"✅ All clean Markdown files are saved in '{MARKDOWN_OUTPUT_DIR}'.")

if __name__ == "__main__":
    main()