import logging
from argparse import ArgumentParser, Namespace
import pandas as pd

from simpletransformers.t5 import T5Model, T5Args


logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--train_file", type=str, required=True)
    parser.add_argument("--eval_file", type=str, required=True)
    parser.add_argument("--test_file", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--model_name_or_path", type=str, required=True)
    parser.add_argument("--wandb_project", type=str, default="t5-tranlated")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    return args


def main():

    args = parse_args()

    train_df = pd.read_excel(args.train_file)
    eval_df = pd.read_excel(args.eval_file)
    test_df = pd.read_excel(args.test_file)

    # Configure the model
    model_args = T5Args()
    model_args.manual_seed = args.seed
    model_args.num_train_epochs = 10
    model_args.train_batch_size = 4
    model_args.eval_batch_size = 4
    model_args.max_seq_length = 550
    model_args.max_length = 80
    model_args.overwrite_output_dir = True
    model_args.reprocess_input_data = True
    model_args.preprocess_inputs = False
    model_args.num_return_sequences = 1

    model_args.save_steps = -1
    model_args.save_eval_checkpoints = False
    model_args.no_cache = True
    model_args.save_model_every_epoch = False

    model_args.evaluate_generated_text = True
    model_args.evaluate_during_training = True
    model_args.evaluate_during_training_verbose = True

    model_args.use_early_stopping = True
    model_args.early_stopping_patience = 3

    model_args.use_multiprocessing = False
    model_args.use_multiprocessed_decoding = False
    model_args.use_multiprocessing_for_evaluation = False
    model_args.fp16 = False

    model_args.wandb_project = args.wandb_project
    model_args.output_dir = args.output_dir

    model = T5Model("t5", args.model_name_or_path, args=model_args, cuda_device=0)

    # Train the model
    model.train_model(train_df, eval_data=eval_df)

    # Make predictions with the model
    to_predict = [
        f"{row.prefix}: {row.input_text}" for row in test_df.itertuples()
    ]
    preds = model.predict(to_predict)

    # Save test results
    test_df["pred_text"] = preds
    test_df.to_excel(args.output_dir + "outputs.xlsx", index=False)


if __name__ == '__main__':
    main()