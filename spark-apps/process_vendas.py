# -*- coding: utf-8 -*-
"""
Script PySpark para processamento de dados de vendas em formato Delta Lake.

Este script agora é multitenant, processando dados para uma organização específica.

Autor: Engenheiro de Dados Sênior
Projeto: DataPilot

Execução:
`spark-submit process_vendas.py <organization_id>`
O ID da organização é passado como um argumento de linha de comando.
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import FloatType, DateType


def get_spark_session(app_name="ProcessamentoVendasDelta") -> SparkSession:
    # ... (O conteúdo desta função permanece o mesmo)
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    packages = [
        "io.delta:delta-core_2.12:2.4.0",
        "org.apache.hadoop:hadoop-aws:3.3.2",
        "com.amazonaws:aws-java-sdk-bundle:1.12.262"
    ]
    spark_builder = (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.jars.packages", ",".join(packages))
        .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    )
    print("Spark Session configurada com sucesso.")
    return spark_builder.getOrCreate()

def transform_data(df):
    # ... (O conteúdo desta função permanece o mesmo)
    print("Iniciando transformações...")
    column_mapping = {
        "ID_VENDA": "id_venda",
        "DATA_PEDIDO": "data_venda",
        "VALOR_TOTAL": "valor_venda",
        "ID_CLIENTE": "id_cliente",
        "NOME_PRODUTO": "produto"
    }
    transformed_df = df
    for old_name, new_name in column_mapping.items():
        if old_name in transformed_df.columns:
            transformed_df = transformed_df.withColumnRenamed(old_name, new_name)
    transformed_df = (
        transformed_df
        .withColumn("data_venda", F.to_date(F.col("data_venda"), "yyyy-MM-dd"))
        .withColumn("valor_venda", F.col("valor_venda").cast(FloatType()))
        .filter(F.year(F.col("data_venda")) == 2024)
    )
    transformed_df = transformed_df.withColumn("mes", F.month(F.col("data_venda")))
    print(f"Transformação concluída. Total de registros para 2024: {transformed_df.count()}")
    return transformed_df

def main():
    """
    Função principal que orquestra o pipeline de ETL para uma organização.
    """
    # --- Leitura do ID da Organização ---
    if len(sys.argv) < 2:
        print("Erro: ID da organização não fornecido.")
        print("Uso: spark-submit process_vendas.py <organization_id>")
        sys.exit(1)
    
    organization_id = sys.argv[1]
    print(f"Iniciando processamento para a organização: {organization_id}")

    spark = get_spark_session(app_name=f"VendasDelta_{organization_id}")

    try:
        # --- Caminhos dinâmicos baseados no ID da Organização ---
        input_path = f"s3a://datalake/bronze/org_id={organization_id}/vendas/"
        output_path = f"s3a://datalake/gold/org_id={organization_id}/vendas_limpas/"

        print(f"Lendo dados brutos de: {input_path}")
        raw_df = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(input_path)

        clean_df = transform_data(raw_df)

        print(f"Salvando dados processados em: {output_path}")
        (
            clean_df.write.format("delta")
            .mode("overwrite")
            .partitionBy("mes")
            .option("overwriteSchema", "true")
            .save(output_path)
        )

        print(f"Processo para a organização '{organization_id}' concluído com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro durante o processamento para a organização '{organization_id}': {e}")
    finally:
        print("Finalizando a sessão Spark.")
        spark.stop()

if __name__ == "__main__":
    main()
