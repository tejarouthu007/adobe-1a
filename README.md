# Download Minilm model

```bash
python model.py
```


# Round1A

```bash
docker build --platform linux/amd64 -t round1a:v1 .  
docker run --rm -v $(pwd)/input:/app/input  -v $(pwd)/output:/app/output  --network none round1a:v1
```