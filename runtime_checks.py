from importlib.util import find_spec
import sys


def running_in_browser_python() -> bool:
    return sys.platform == "emscripten"


def ensure_supported_runtime() -> None:
    if running_in_browser_python():
        raise RuntimeError(
            "This project does not run in browser-only notebook runtimes such as "
            "Pyodide/JupyterLite. Open the repository locally in VS Code or Jupyter, "
            "create a virtual environment, install requirements with "
            "`pip install -r requirements.txt`, and select that local Python kernel."
        )


def ensure_packages(packages):
    missing = [pkg for pkg in packages if find_spec(pkg) is None]
    if missing:
        joined = ", ".join(missing)
        raise ModuleNotFoundError(
            "Missing required Python packages: "
            f"{joined}. Install the project environment with "
            "`pip install -r requirements.txt` and use that interpreter/kernel."
        )

