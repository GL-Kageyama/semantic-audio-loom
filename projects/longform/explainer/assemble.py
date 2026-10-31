#!/usr/bin/env python
"""解説動画の組み立て（本体は ../assemble.py。解説も演劇も同じ道具で組む）。

  PYTHONPATH=. <venv> .../explainer/assemble.py [--no-render] [--retrim]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from assemble import main  # noqa: E402

if __name__ == "__main__":
    sys.argv[1:1] = ["--dir", HERE]
    main()
