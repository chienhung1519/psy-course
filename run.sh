# python run.py \
#   --train_file data/processed/data_230406_train.xlsx \
#   --eval_file data/processed/data_230406_eval.xlsx \
#   --test_file data/processed/data_230406_test.xlsx \
#   --output_dir ./outputs/t5-base/ \
#   --model_name_or_path t5-base

# CV
python run_cv.py \
  --data_file data/processed/data_230502.xlsx \
  --output_dir ./outputs/t5-base-cv/ \
  --model_name_or_path t5-base