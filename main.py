import os
import json
import fitz  # PyMuPDF
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.cluster import KMeans
import numpy as np

# Load model and tokenizer from local directory
model_dir = "./minilm"
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModel.from_pretrained(model_dir)
model.eval()

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=32)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def extract_candidates(doc):
    font_data = {}
    candidates = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                line_text = " ".join(span["text"] for span in line["spans"]).strip()
                if not line_text or len(line_text) > 120:
                    continue
                for span in line["spans"]:
                    font_size = round(span["size"], 1)
                    font_data[font_size] = font_data.get(font_size, 0) + 1
                    candidates.append({
                        "text": line_text,
                        "size": font_size,
                        "page": page_num + 1
                    })
                    break  # one span per line is enough

    return candidates

def assign_heading_levels(candidates, n_levels=3):
    texts = [c["text"] for c in candidates]
    vectors = [get_embedding(text) for text in texts]
    km = KMeans(n_clusters=n_levels, random_state=42).fit(vectors)
    levels = ["H1", "H2", "H3"]

    outline = []
    for idx, c in enumerate(candidates):
        label = km.labels_[idx]
        level = levels[label]
        outline.append({
            "level": level,
            "text": c["text"],
            "page": c["page"]
        })
    return outline

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    candidates = extract_candidates(doc)

    if not candidates:
        return {"title": "Untitled", "outline": []}

    outline = assign_heading_levels(candidates)
    title = next((h["text"] for h in outline if h["level"] == "H1"), "Untitled")

    return {
        "title": title,
        "outline": outline
    }

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"

    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.lower().endswith(".pdf"):
            in_path = os.path.join(input_dir, file)
            out_path = os.path.join(output_dir, file.replace(".pdf", ".json"))
            try:
                result = extract_outline(in_path)
                with open(out_path, "w") as f:
                    json.dump(result, f, indent=2)
                print(f"Processed {file}")
            except Exception as e:
                print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    main()
