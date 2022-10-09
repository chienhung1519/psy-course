import logging
from argparse import ArgumentParser, Namespace
import pandas as pd
import numpy as np

from simpletransformers.t5 import T5Model, T5Args


logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--data_file",
        type=str,
        required=True,
        help="Path to the data.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Directory to store the outputs files.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed.",
    )
    args = parser.parse_args()
    return args


def main():

    args = parse_args()

    data = pd.read_excel(args.data_file, engine='openpyxl', dtype=str)
    train_df, eval_df, test_df = np.split(data.sample(frac=1, random_state=args.seed), [int(.6*len(data)), int(.8*len(data))])

    # Configure the model
    model_args = T5Args()
    model_args.num_train_epochs = 10
    model_args.train_batch_size = 8
    model_args.eval_batch_size = 8
    model_args.max_seq_length = 128
    model_args.overwrite_output_dir = True
    model_args.reprocess_input_data = True
    model_args.preprocess_inputs = False
    model_args.num_return_sequences = 1

    model_args.no_cache = True

    model_args.save_steps = -1
    model_args.save_eval_checkpoints = False
    model_args.save_model_every_epoch = False

    model_args.evaluate_generated_text = True
    model_args.evaluate_during_training = True
    model_args.evaluate_during_training_verbose = True

    model_args.use_early_stopping = True
    model_args.early_stopping_patience = 3

    model_args.use_multiprocessing = False
    model_args.fp16 = False

    model = T5Model("t5", "t5-base", args=model_args)

    # Train the model
    model.train_model(train_df, eval_data=eval_df)

    # Make predictions with the model
    to_predict = [
        f"{row.prefix}: {row.input_text}" for row in test_df.itertuples()
    ]
    preds = model.predict(to_predict)

    # Save test results
    test_df["pred_text"] = preds
    test_df.to_excel(args.output_dir+"results.xlsx", index=False)


if __name__ == '__main__':
    main()