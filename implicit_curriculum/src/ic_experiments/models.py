from __future__ import annotations

import torch
from torch import nn


class MLPClassifier(nn.Module):
    """Small task-conditioned MLP for binary structure classification."""

    def __init__(self, input_dim: int, hidden_dim: int = 128, depth: int = 2, dropout: float = 0.0):
        super().__init__()
        if depth < 1:
            raise ValueError("depth must be >= 1")
        layers: list[nn.Module] = []
        dim = input_dim
        for _ in range(depth):
            layers.append(nn.Linear(dim, hidden_dim))
            layers.append(nn.ReLU())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            dim = hidden_dim
        self.encoder = nn.Sequential(*layers)
        self.head = nn.Linear(hidden_dim, 1)

    def forward(self, x: torch.Tensor, return_hidden: bool = False):
        hidden = self.encoder(x)
        logits = self.head(hidden).squeeze(-1)
        if return_hidden:
            return logits, hidden
        return logits


def build_model(model_name: str, input_dim: int, hidden_dim: int, depth: int, dropout: float) -> nn.Module:
    if model_name != "mlp":
        raise ValueError(f"Only 'mlp' is implemented in this first pass; got {model_name!r}")
    return MLPClassifier(input_dim=input_dim, hidden_dim=hidden_dim, depth=depth, dropout=dropout)
