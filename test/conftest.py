import sys
from pathlib import Path

# 项目根目录（test 的父目录）
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 将 core/src 与 app/src 放入 sys.path，便于 import core.* 和 app.*
SRC_PATHS = [
    PROJECT_ROOT / "core" / "src",
    PROJECT_ROOT / "app" / "src",
]

for p in SRC_PATHS:
    if p.exists():
        sys.path.insert(0, str(p))