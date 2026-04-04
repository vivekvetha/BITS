import os
import subprocess

import pandas as pd
from prefect import flow, get_run_logger, task

from us_pop_mlflow_core import (
    configure_mlflow,
    default_csv_path,
    preprocess_data,
    run_mlflow_training_from_xy,
)


@task(log_prints=True)
def run_task(script_name):
    logger = get_run_logger()

    script_path = os.path.join(
        os.path.dirname(__file__).replace("flows", ""), "tasks", script_name
    )
    print(f"Running script: {script_path}")
    try:
        result = subprocess.run(["python", script_path], capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"Successfully executed {script_name}:\n{result.stdout}")
        else:
            logger.error(f"Error in {script_name}: {result.stderr}")

        print(result.stdout)
        print(result.stderr)

    except Exception as e:
        logger.error(f"Failed to execute {script_name}: {str(e)}")

    return 0


@task
def load_us_pop_dataset(csv_path: str | None = None):
    """Load processed US population CSV (same source as MLOps-MLFlow)."""
    path = csv_path or default_csv_path()
    return pd.read_csv(path)


@task(log_prints=True)
def preprocess_us_pop_dataset(df: pd.DataFrame):
    """Drop columns, encode categoricals, binary outcome — aligns with MLflow pipeline."""
    X, y = preprocess_data(df)
    print(f"Preprocessed features shape: {X.shape}, labels: {len(y)}")
    return X, y


@task(log_prints=True)
def train_models_with_mlflow(X_y: tuple):
    """Train RF, logistic regression, HGB; log metrics and models to MLflow."""
    X, y = X_y
    configure_mlflow()
    run_mlflow_training_from_xy(X, y)


@flow(log_prints=True)
def main_flow():
    # EDA / analysis scripts (sequential)
    data1 = run_task("BasicStats.py")
    data2 = run_task("Normalization.py", wait_for=[data1])
    data3 = run_task("Binning.py", wait_for=[data2])
    data4 = run_task("ChiSquareSexWorkclass.py", wait_for=[data3])
    data5 = run_task("CorrelationCoeffecient.py", wait_for=[data4])
    data6 = run_task("Encoding_PearsonCorrelation.py", wait_for=[data5])
    data7 = run_task("FeatureImportanceMLAlgorithms.py", wait_for=[data6])
    data8 = run_task("PearsonCorrelation.py", wait_for=[data7])
    data9 = run_task("Visualization.py", wait_for=[data8])

    # In-process data processing + MLflow (Module4-style tasks + MLOps-MLFlow behavior)
    raw = load_us_pop_dataset(wait_for=[data9])
    processed = preprocess_us_pop_dataset(raw)
    train_models_with_mlflow(processed)


if __name__ == "__main__":
    main_flow.serve(
        name="us-population-ds-workflow",
        tags=["us population datascience project workflow", "mlflow"],
        parameters={},
        interval=180,
    )  # 3 minutes
