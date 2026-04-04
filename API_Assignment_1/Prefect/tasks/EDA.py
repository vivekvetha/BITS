# This is not been called in the workflow. This is for local testing.
"""
EDA orchestration and shared dataset paths for DataOps scripts.

Change RAW_CSV / PROCESSED_CSV (or DATA_DIR) here to point all assignments at one dataset.
Plots and exports go to OUTPUT_DIR (Prefect/output/).
"""

from pathlib import Path

_DATA_OPS_DIR = Path(__file__).resolve().parent
DATA_DIR = _DATA_OPS_DIR.parent
OUTPUT_DIR = DATA_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_CSV = (
    DATA_DIR / "data/uspop_data.csv"
)  # data/ added additionally to match the path in the EDA scripts for Prefect workflow
PROCESSED_CSV = (
    DATA_DIR / "data/us_pop_processed_value.csv"
)  # data/ added additionally to match the path in the EDA scripts for Prefect workflow

print(f"RAW_CSV path: {RAW_CSV}")
print(f"PROCESSED_CSV path: {PROCESSED_CSV}")

if __name__ == "__main__":
    import subprocess
    import sys
    import time

    print("\nExecuting: EDA for US Population Survey Data Set \n")
    files = [
        "BasicStats.py",
        "Normalization.py",
        "Binning.py",
        "Encoding_PearsonCorrelation.py",
        "CorrelationCoeffecient.py",
        "ChiSquareSexWorkclass.py",
        "FeatureImportanceMLAlgorithms.py",
        "Visualization.py",
    ]

    for f in files:
        print(
            "\n///////////////////////////////////////////////////////////////////////////\n"
        )
        print("Executing:", f)
        print(
            "\n///////////////////////////////////////////////////////////////////////////\n"
        )
        subprocess.run([sys.executable, f])
        time.sleep(2)

    print("All files executed")
