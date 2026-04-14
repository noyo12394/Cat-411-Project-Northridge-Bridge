from pathlib import Path
import os
import subprocess
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from project_paths import build_paths


def run_step(script_name: str) -> None:
    script_path = PROJECT_ROOT / "scripts" / script_name
    mpl_dir = Path(tempfile.gettempdir()) / "cat411-mplconfig"
    mpl_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    env["MPLCONFIGDIR"] = str(mpl_dir)
    print(f"Running {script_name}...", flush=True)
    subprocess.run([sys.executable, str(script_path)], check=True, env=env)


def main() -> None:
    paths = build_paths()

    run_step("export_core_figures.py")
    run_step("run_ml_hybrid_analysis.py")
    run_step("export_recommended_hybrid.py")
    run_step("run_damage_state_classification.py")
    run_step("run_future_scenario_scoring.py")

    ndvi_required = ["PRE_NDVI_TIF", "POST_NDVI_TIF", "NDVI_CHANGE_TIF"]
    if all(paths[key].exists() for key in ndvi_required):
        run_step("prepare_ndvi_inputs.py")
        run_step("run_ndvi_pipeline.py")
        run_step("run_proxy_validation.py")
    else:
        print("Skipping NDVI figure refresh because the NDVI TIFF bundle is not available.", flush=True)


if __name__ == "__main__":
    main()
