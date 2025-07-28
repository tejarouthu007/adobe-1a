from transformers import AutoModel, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("nreimers/MiniLM-L6-H384-uncased")
model = AutoModel.from_pretrained("nreimers/MiniLM-L6-H384-uncased")

tokenizer.save_pretrained("./minilm")
model.save_pretrained("./minilm")
