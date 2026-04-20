"""
Model and training configuration with enforced architecture ceilings.

The ceilings from Phase 1 advisory (§10.3 R1) are not defaults — they are hard limits.
A model that fits within these bounds is inspectable; one that exceeds them is not.
"""

from dataclasses import asdict, dataclass

# Hard architecture ceilings. Enforced in ModelConfig.__post_init__.
MAX_LAYERS = 2
MAX_HEADS = 4
MAX_D_MODEL = 64
MAX_SEQ_LEN = 32
MAX_VOCAB = 64


@dataclass
class ModelConfig:
    vocab_size: int = 32
    d_model: int = 64
    n_layers: int = 2
    n_heads: int = 4
    seq_len: int = 16

    def __post_init__(self) -> None:
        assert self.n_layers <= MAX_LAYERS, f"n_layers {self.n_layers} > ceiling {MAX_LAYERS}"
        assert self.n_heads <= MAX_HEADS, f"n_heads {self.n_heads} > ceiling {MAX_HEADS}"
        assert self.d_model <= MAX_D_MODEL, f"d_model {self.d_model} > ceiling {MAX_D_MODEL}"
        assert self.seq_len <= MAX_SEQ_LEN, f"seq_len {self.seq_len} > ceiling {MAX_SEQ_LEN}"
        assert self.vocab_size <= MAX_VOCAB, f"vocab_size {self.vocab_size} > ceiling {MAX_VOCAB}"
        assert self.d_model % self.n_heads == 0, "d_model must be divisible by n_heads"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrainConfig:
    task: str = "induction"
    lr: float = 1e-3
    steps: int = 2000
    batch_size: int = 32
    n_train: int = 4096
    checkpoint_every: int = 100
    eval_every: int = 10
    seed: int = 42

    def to_dict(self) -> dict:
        return asdict(self)
