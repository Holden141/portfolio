# 🚧 Amazon Reviews Pipeline (WIP)

> Work in progress — core pipeline complete, visualization and automation coming soon.

Automated data pipeline that ingests Amazon product reviews, transforms them with dbt, and prepares them for analysis. Built as a portfolio project to demonstrate data engineering and analytics skills.
Original Dataset: https://www.kaggle.com/datasets/arhamrumi/amazon-product-reviews .

## 🎯 What It Does

- **Ingestion**: Loads 10k Amazon reviews from CSV to BigQuery
- **Transformation**: dbt models that clean data and add sentiment classification (`POSITIVE`/`NEUTRAL`/`NEGATIVE`)
- **Testing**: Automated data quality tests (unique keys, not nulls, valid value ranges)
- **Orchestration**: Scheduled daily runs via GitHub Actions

## 🛠️ Tech Stack

| Layer | Tools |
| :--- | :--- |
| Data Warehouse | Google BigQuery |
| Transformation | dbt (SQL models) |
| Orchestration | GitHub Actions |
| Language | Python |
| Visualization | Looker Studio (planned) |
| LLM Integration | tbd |

## 📊 Pipeline Architecture


### Resources:
- dbt [docs](https://docs.getdbt.com/docs/introduction)
