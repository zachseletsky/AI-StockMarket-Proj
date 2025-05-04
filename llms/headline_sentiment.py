"""
  This file contains methods for importing finbert model, and vectorizing
  existing data. able to output a parquet file of vectors

  TODO:
  - need to implement more safety rails, such as
    - apply sha256
    - protecting processed folder by only placing files
      in folder after verification
  - enable user input tickers and files
  - automate processes
  - currently uses mean pooling for multi headlines per date
    - need to upgrade to attention pooling or some other technique
"""

import pandas as pd
import json
from pathlib import Path
from transformers import AutoTokenizer
from transformers import AutoModel
import torch
import pyarrow.parquet as pq


def load_headlines() -> pd.DataFrame:
    fp = Path("data-lake/processed/MSFT_data.json")

    with fp.open("r") as f:
        data = json.load(f)["data"]

    # print("Data: " + str(data))
    headlines = pd.DataFrame(data, columns=["date", "headlines"])
    return headlines


def load_model(device=None):
    tok = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
    bert = AutoModel.from_pretrained("yiyanghkust/finbert-tone")
    bert.eval()
    if device is None:
        if torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
    bert.to(device)
    return tok, bert, device


def make_embeddings(
    texts: list[str], tokenizer, model, device, batch_size: int = 32
) -> torch.Tensor:
    """
    Return a (N×D) tensor of embeddings, one per input string.
    """
    all_embeds = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        # 1) tokenize → padded ID tensor on device
        inputs = tokenizer(
            batch, padding=True, truncation=True, max_length=128, return_tensors="pt"
        ).to(device)

        # 2) forward pass (no grad)
        with torch.no_grad():
            outputs = model(**inputs)
            # last_hidden_state: (B, T, D)
            hidden = outputs.last_hidden_state

        # 3) CLS pooling → (B, D)
        cls_embeds = hidden[:, 0, :]

        all_embeds.append(cls_embeds.cpu())

    # concat → (N, D)
    return torch.cat(all_embeds, dim=0)


def embed_daily_headlines(
    df: pd.DataFrame, tokenizer: AutoTokenizer, model: AutoModel, device: torch.device
) -> pd.DataFrame:
    """
    Input df: columns ['date', 'headlines'], where headlines is list[str].
    Returns a new df with columns ['date'] + 768 embedding dims.
    """
    # 1. record how many headlines per row
    counts = df["headlines"].apply(len).tolist()
    # 2. flatten all headlines into one list
    flat = [h for sublist in df["headlines"] for h in sublist]
    # 3. compute embeddings for every headline
    embeds = make_embeddings(flat, tokenizer, model, device)  # shape: (total, 768)
    # 4. group & mean-pool by original row
    daily_embeds = []
    idx = 0
    for c in counts:
        group = embeds[idx : idx + c]  # (c, 768)
        pooled = group.mean(dim=0)  # (768,)
        daily_embeds.append(pooled.numpy())
        idx += c
    # 5. build a DataFrame
    emb_df = pd.DataFrame(
        daily_embeds,
        columns=[f"emb_{i}" for i in range(embeds.size(1))],
        index=df.index,
    )
    emb_df.insert(0, "date", df["date"])
    return emb_df


def train_model():
    df = load_headlines()
    tok, bert, device = load_model()

    daily_df = embed_daily_headlines(df, tok, bert, device)

    print(daily_df.shape)  # (num_dates, 769)
    daily_df.to_parquet("data-lake/processed/MSFT_daily_embeds.parquet")


def confirm_schema():
    print("Verification: ")
    pf = pq.ParquetFile("data-lake/processed/MSFT_daily_embeds.parquet")
    # print the stored schema
    print(pf.schema)


def confirm_pd():
    print("Verification: ")
    df = pd.read_parquet("data-lake/processed/MSFT_daily_embeds.parquet")
    print("info: ")
    print(df.info())  # types & non-null counts
    print("head: ")
    print(df.head())  # first few rows
    print("desc: ")
    print(df.describe())  # basic stats on numeric cols


if __name__ == "__main__":
    # train_model()
    # confirm_schema()
    confirm_pd()
