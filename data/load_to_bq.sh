#!/bin/bash
# 挑戰 3 用：建 dataset 並灌入範例客群資料
set -e

bq mk --dataset --location=US "${GOOGLE_CLOUD_PROJECT}:workshop_data" || true

bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  "${GOOGLE_CLOUD_PROJECT}:workshop_data.demographics" \
  demographics.csv \
  country:STRING,age_group:STRING,interests:STRING,channels:STRING

echo "完成。驗證："
echo "  bq query --use_legacy_sql=false 'SELECT * FROM workshop_data.demographics'"
