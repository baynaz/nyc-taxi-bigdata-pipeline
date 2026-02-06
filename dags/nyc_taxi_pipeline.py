from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# 1. CONFIGURATION
default_args = {
    'owner': 'bigdata_student',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=15),
}

# =============================================================================
# 2. DEFINITION DU DAG
# =============================================================================
with DAG(
        'nyc_taxi_pipeline',
        default_args=default_args,
        description='Pipeline : Ingestion puis Nettoyage puis Data Warehouse',
        schedule_interval=None,
        start_date=days_ago(1),
        tags=['spark', 'scala', 'docker'],
        catchup=False,
) as dag:

    # Tache 1 : Debut
    start_task = BashOperator(
        task_id='launch_pipeline',
        bash_command='echo "Demarrage de la pipeline NYC Taxi"'
    )

    # Tache 2 : Nettoyage
    run_nettoyage_donnees = BashOperator(
        task_id='nettoyage',
        bash_command="""
        echo "Lancement du nettoyage..." && \
        docker exec -i spark-master bash -c "/opt/spark/bin/spark-submit --class fr.cytech.integration.Main /opt/spark/work-dir/ex02_data_ingestion/target/scala-2.12/nyc-taxi-ingestion_2.12-1.0.jar ALL"
        """
    )

    # Tache 3 : Ingestion
    run_ingestion = BashOperator(
        task_id='ingestion_vers_postgres',
        bash_command="""
        echo "Debut de l'insertion en base" && \
        docker exec -i spark-master bash -c "/opt/spark/bin/spark-submit --class fr.cytech.integration.Branch2Production /opt/spark/work-dir/ex02_data_ingestion/target/scala-2.12/nyc-taxi-ingestion_2.12-1.0.jar s3a://nyc-clean/yellow_tripdata_*-clean"
        """
    )

    # Tache 4 : Fin
    end_task = BashOperator(
        task_id='end_pipeline',
        bash_command='echo "Pipeline termine avec succes ! Les donnees sont dans PostgreSQL."'
    )

    # 3. ORDONNANCEMENT
    start_task >> run_nettoyage_donnees >> run_ingestion >> end_task