from pathlib import Path
import tempfile

from ic_experiments.backends.sparse_parity import SparseParityConfig, generate_sparse_parity_family, save_sparse_parity_family
from ic_experiments.backends.sequence_dsl import SequenceDSLConfig, generate_sequence_dsl_family, make_lm_batch, CausalTransformerLM
import torch


def main():
    sp = generate_sparse_parity_family(SparseParityConfig(n_bits=20, n_tasks=8, degrees=(3, 5), seed=0))
    assert len(sp.tasks) == 8
    assert sp.structure_table().shape[0] == 8
    with tempfile.TemporaryDirectory() as td:
        paths = save_sparse_parity_family(sp, Path(td) / "sp")
        assert Path(paths["structure_table"]).exists()

    seq = generate_sequence_dsl_family(SequenceDSLConfig(vocab_content=16, input_len=4, n_atomic=4, n_composite=2, seed=0))
    assert len(seq.tasks) == 12  # 4 atomics + 2 composites + default controls
    tokens, labels, task_ids = make_lm_batch(seq.tasks, seq.config, batch_size=4, device="cpu")
    assert tokens.shape == labels.shape
    model = CausalTransformerLM(vocab_size=seq.config.vocab_size, max_seq_len=tokens.shape[1], d_model=32, n_layers=1, n_heads=4, d_mlp=64)
    logits = model(tokens)
    assert logits.shape[:2] == tokens.shape
    assert logits.shape[-1] == seq.config.vocab_size
    print("backend tests passed")


if __name__ == "__main__":
    main()
