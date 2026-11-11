import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CALC = RAIZ / "fuente" / "calculos"
sys.path.insert(0, str(CALC))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
