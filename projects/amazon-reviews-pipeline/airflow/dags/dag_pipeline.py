from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'holden',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'amazon_reviews_pipeline',
    default_args=default_args,
    description='Ingest → dbt → classify → cluster → anomaly',
    schedule='@daily', 
    catchup=False,
    tags=['amazon', 'dbt', 'ml'],
) as dag:

    ingest = BashOperator(
        task_id='ingest',
        bash_command='cd /opt/airflow/amazon-reviews-pipeline && python ingest.py',
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/amazon-reviews-pipeline/review_pipeline && dbt run --profiles-dir .',
    )

    classify = BashOperator(
        task_id='classify',
        bash_command='cd /opt/airflow/amazon-reviews-pipeline && python 01_classify_reviews.py',
    )

    cluster = BashOperator(
        task_id='cluster',
        bash_command='cd /opt/airflow/amazon-reviews-pipeline && python 02_cluster_analysis.py',
    )

    anomaly = BashOperator(
        task_id='anomaly',
        bash_command='cd /opt/airflow/amazon-reviews-pipeline && python 03_anomaly_detection.py',
    )

    ingest >> dbt_run >> classify >> cluster >> anomaly