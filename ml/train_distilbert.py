"""
Fine-tuning DistilBERT on Jigsaw Toxic Comment Classification
Multi-label classification with BCEWithLogitsLoss and positive class weighting.
Designed to be run on GPU (e.g. Google Colab) or locally with a subset.
"""

import os
import argparse
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, f1_score

LABELS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

class ToxicDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt"
        )
        item = {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
        }
        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.float)
        return item

def compute_pos_weights(labels_matrix):
    """Calculate positive class weights for BCEWithLogitsLoss to counter class imbalance."""
    num_samples = len(labels_matrix)
    pos_counts = np.sum(labels_matrix, axis=0)
    # Prevent divide by zero
    pos_counts = np.maximum(pos_counts, 1)
    neg_counts = num_samples - pos_counts
    pos_weights = neg_counts / pos_counts
    # Cap weights to prevent instability
    pos_weights = np.clip(pos_weights, 1.0, 50.0)
    return torch.tensor(pos_weights, dtype=torch.float)

def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load data
    print(f"Loading data from {args.data_path}...")
    df = pd.read_csv(args.data_path)
    
    if args.sample_size and len(df) > args.sample_size:
        print(f"Subsampling to {args.sample_size} rows...")
        # Stratify sample by toxic column if available
        df = df.sample(n=args.sample_size, random_state=42).reset_index(drop=True)

    texts = df["comment_text"].fillna("").tolist()
    labels = df[LABELS].values

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.15, random_state=42
    )
    print(f"Train samples: {len(train_texts)}, Validation samples: {len(val_texts)}")

    # Tokenizer & Model
    tokenizer = DistilBertTokenizerFast.from_pretrained(args.model_name)
    model = DistilBertForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=len(LABELS),
        problem_type="multi_label_classification"
    )
    model.to(device)

    # Class-weighted loss
    pos_weights = compute_pos_weights(train_labels).to(device)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weights)

    train_dataset = ToxicDataset(train_texts, train_labels, tokenizer, max_len=args.max_len)
    val_dataset = ToxicDataset(val_texts, val_labels, tokenizer, max_len=args.max_len)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size * 2, shuffle=False)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=0.01)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=int(total_steps * 0.1), num_training_steps=total_steps
    )

    best_val_auc = 0.0
    print("\nStarting training loop...")
    for epoch in range(args.epochs):
        model.train()
        total_loss = 0.0

        for step, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            target_labels = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            loss = loss_fn(logits, target_labels)

            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            total_loss += loss.item()
            if (step + 1) % 10 == 0 or (step + 1) == len(train_loader):
                print(f"Epoch {epoch+1}/{args.epochs} | Step {step+1}/{len(train_loader)} | Loss: {loss.item():.4f}")

        # Validation
        model.eval()
        val_preds = []
        val_targets = []
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
                probs = torch.sigmoid(logits).cpu().numpy()
                val_preds.append(probs)
                val_targets.append(batch["labels"].numpy())

        val_preds = np.vstack(val_preds)
        val_targets = np.vstack(val_targets)

        # Compute ROC-AUC
        aucs = []
        for i, lbl in enumerate(LABELS):
            try:
                score = roc_auc_score(val_targets[:, i], val_preds[:, i])
                aucs.append(score)
            except Exception:
                aucs.append(0.5)
        mean_auc = np.mean(aucs)
        print(f"\n--- Epoch {epoch+1} Evaluation ---")
        for i, lbl in enumerate(LABELS):
            print(f"  {lbl}: ROC-AUC = {aucs[i]:.4f}")
        print(f"Mean ROC-AUC: {mean_auc:.4f}\n")

        if mean_auc > best_val_auc:
            best_val_auc = mean_auc
            os.makedirs(args.output_dir, exist_ok=True)
            model.save_pretrained(args.output_dir)
            tokenizer.save_pretrained(args.output_dir)
            print(f"Saved best model checkpoint to {args.output_dir}")

    print("Training complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default="data/jigsaw_sample.csv")
    parser.add_argument("--model_name", type=str, default="distilbert-base-uncased")
    parser.add_argument("--output_dir", type=str, default="ml/artifacts/toxicity_model")
    parser.add_argument("--max_len", type=int, default=128)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--learning_rate", type=float, default=2e-5)
    parser.add_argument("--sample_size", type=int, default=50000)
    args = parser.parse_args()
    train(args)

