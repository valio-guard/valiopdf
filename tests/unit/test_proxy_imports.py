"""The proxy subprocess starts once per render, so its imports must stay light."""

from __future__ import annotations

import os
import subprocess
import sys

HEAVY = {"pikepdf", "pypdfium2", "playwright", "pydantic", "jinja2", "PIL", "img2pdf", "pyhanko"}


def test_proxy_addon_imports_no_heavy_packages() -> None:
    code = (
        "import sys\n"
        "import valiopdf.render._proxy_addon\n"
        f"print(sorted({{m.split('.')[0] for m in sys.modules}} & set({sorted(HEAVY)!r})))\n"
    )
    env = {k: v for k, v in os.environ.items() if not k.startswith("VALIOPDF_PROXY_")}
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True, env=env
    )

    assert result.stdout.strip() == "[]"


def test_package_exports_still_resolve() -> None:
    import valiopdf
    import valiopdf.render

    for name in valiopdf.__all__:
        assert getattr(valiopdf, name) is not None
    for name in valiopdf.render.__all__:
        assert getattr(valiopdf.render, name) is not None
