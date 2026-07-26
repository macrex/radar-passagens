"""Torna `scripts/` importavel nos testes sem instalar o pacote."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
