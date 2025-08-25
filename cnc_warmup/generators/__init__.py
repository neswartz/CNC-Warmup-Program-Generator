# re-export generator entry points
from .fanuc31i_warmup import generate_program as generate_fanuc_program
from .tnc640_warmup import generate_program as generate_tnc_program

__all__ = [
    "generate_fanuc_program",
    "generate_tnc_program",
]


