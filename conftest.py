# conftest.py
import sys, os

# Ajouter la racine du projet au PYTHONPATH pour pytest
root = os.path.abspath(os.path.dirname(__file__))
if root not in sys.path:
    sys.path.insert(0, root)
