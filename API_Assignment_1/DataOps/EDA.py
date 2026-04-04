"""
EDA orchestration and shared dataset paths for DataOps scripts.

Change RAW_CSV / PROCESSED_CSV (or DATA_DIR) here to point all assignments at one dataset.
"""

from pathlib import Path

_DATA_OPS_DIR = Path(__file__).resolve().parent
DATA_DIR = _DATA_OPS_DIR.parent
RAW_CSV = DATA_DIR / "uspop_data.csv"
PROCESSED_CSV = DATA_DIR / "us_pop_processed_value.csv"

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
