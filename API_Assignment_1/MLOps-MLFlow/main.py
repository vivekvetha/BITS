import os
import time
from pathlib import Path

import pandas as pd
import psutil
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import mlflow
import mlflow.sklearn


def _mlops_dir():
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()


# SQLite backend (recommended over plain ./mlruns file store in current MLflow).
_db_path = _mlops_dir() / "mlflow.db"
mlflow.set_tracking_uri("http://localhost:5001")

mlflow.set_experiment("us_pop_income")


def preprocess_data(data: pd.DataFrame):
    """
    Aligns with DataOps/us_pop pipeline: drop unused columns, strip strings,
    one-hot encode categoricals, binary encode income outcome.
    """
    data = data.drop(
        ["censor-sample", "education", "relationship", "capital-gain", "capital-loss"],
        axis=1,
        errors="ignore",
    )
    data = data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    y = data["outcome"].map({"<=50K": 0, ">50K": 1})
    X = data.drop("outcome", axis=1)

    cat_cols = X.select_dtypes(include=["object", "string"]).columns.tolist()
    X = pd.get_dummies(X, columns=cat_cols)

    valid = y.notna()
    X, y = X.loc[valid], y.loc[valid]

    return X, y


def train_random_forest(X_train, y_train, max_depth=12, n_estimators=100):
    clf = RandomForestClassifier(
        max_depth=max_depth,
        n_estimators=n_estimators,
        class_weight="balanced",
        random_state=42,
    )
    clf.fit(X_train, y_train)
    return clf


def train_logistic_regression(X_train, y_train, C=1.0, max_iter=1000):
    # Scale features so numeric columns are comparable to one-hot columns.
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    C=C,
                    max_iter=max_iter,
                    class_weight="balanced",
                    random_state=42,
                    solver="lbfgs",
                ),
            ),
        ]
    ).fit(X_train, y_train)


def train_hist_gradient_boosting(
    X_train,
    y_train,
    *,
    max_depth=8,
    max_iter=200,
    learning_rate=0.1,
):
    clf = HistGradientBoostingClassifier(
        max_depth=max_depth,
        max_iter=max_iter,
        learning_rate=learning_rate,
        class_weight="balanced",
        random_state=42,
    )
    clf.fit(X_train, y_train)
    return clf


def evaluate_model(model, X_test, y_test, title: str):
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n{title}")
    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["<=50K", ">50K"]))


def log_to_mlflow(
    model,
    X_test,
    y_test,
    training_time_sec: float,
    *,
    run_name: str,
    params: dict,
):
    with mlflow.start_run(run_name=run_name):
        mlflow.set_tag("algorithm", run_name)
        for key, val in params.items():
            mlflow.log_param(key, val)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
        recall = recall_score(y_test, y_pred, average="macro", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
        cm = confusion_matrix(y_test, y_pred, labels=[0, 1])

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1-score", f1)

        mlflow.log_metrics(
            {
                "true_negative": int(cm[0][0]),
                "false_positive": int(cm[0][1]),
                "false_negative": int(cm[1][0]),
                "true_positive": int(cm[1][1]),
            }
        )

        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        mlflow.log_metric("system_cpu_usage", cpu_usage)
        mlflow.log_metric("system_memory_usage", memory_usage)
        mlflow.log_metric("system_model_training", training_time_sec)

        evaluate_model(model, X_test, y_test, title=run_name)
        mlflow.sklearn.log_model(sk_model=model, name="model")


def main():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()
    csv_path = os.path.join(script_dir, "..", "us_pop_processed_value.csv")

    data = pd.read_csv(csv_path)
    X, y = preprocess_data(data)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    t0 = time.time()
    rf_model = train_random_forest(X_train, y_train)
    rf_time = time.time() - t0
    log_to_mlflow(
        rf_model,
        X_test,
        y_test,
        rf_time,
        run_name="random_forest",
        params={
            "max_depth": rf_model.max_depth,
            "n_estimators": rf_model.n_estimators,
            "class_weight": str(rf_model.class_weight),
        },
    )

    t0 = time.time()
    lr_model = train_logistic_regression(X_train, y_train)
    lr_time = time.time() - t0
    lr = lr_model.named_steps["clf"]
    log_to_mlflow(
        lr_model,
        X_test,
        y_test,
        lr_time,
        run_name="logistic_regression",
        params={
            "C": lr.C,
            "max_iter": lr.max_iter,
            "solver": lr.solver,
            "penalty": lr.penalty,
            "class_weight": str(lr.class_weight),
        },
    )

    t0 = time.time()
    hgb_model = train_hist_gradient_boosting(X_train, y_train)
    hgb_time = time.time() - t0
    log_to_mlflow(
        hgb_model,
        X_test,
        y_test,
        hgb_time,
        run_name="hist_gradient_boosting",
        params={
            "max_depth": hgb_model.max_depth,
            "max_iter": hgb_model.max_iter,
            "learning_rate": hgb_model.learning_rate,
            "class_weight": str(hgb_model.class_weight),
            "l2_regularization": hgb_model.l2_regularization,
        },
    )


if __name__ == "__main__":
    main()
