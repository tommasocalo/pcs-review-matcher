# embedder.py
import numpy as np
from transformers import AutoTokenizer
from transformers.adapters import AutoAdapterModel

class SPECTEREmbedder:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
        self.model = AutoAdapterModel.from_pretrained('allenai/specter2_base')
        self.model.load_adapter(
            "allenai/specter2_adhoc_query", 
            source="hf", 
            load_as="specter2_adhoc_query",
            set_active=True
        )
        
    def embed(self, texts: list) -> np.ndarray:
        inputs = self.tokenizer(
            texts, 
            padding=True, 
            truncation=True,
            return_tensors="pt", 
            max_length=512
        )
        outputs = self.model(**inputs)
        return outputs.last_hidden_state[:, 0, :].detach().numpy()
