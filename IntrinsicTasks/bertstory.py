import tensorflow as tf
tf.enable_eager_execution()
from sklearn.model_selection import train_test_split
import pandas as pd
import tensorflow_hub as hub
from datetime import datetime
from IPython.core.debugger import set_trace
import bert
from bert import run_classifier
from bert import optimization
from bert import tokenization
from tensorflow import keras
import os
import re
from model import *
from prepare_data import *
import prepare_data
from read import *

tf.logging.set_verbosity(tf.logging.INFO)
os.environ['TFHUB_CACHE_DIR'] = '/home/djjindal/bert/script-learning'
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
# This is a path to an uncased (all lowercase) version of BERT
BERT_MODEL_HUB = "https://tfhub.dev/google/bert_uncased_L-12_H-768_A-12/1"

BATCH_SIZE = 1
LEARNING_RATE = 2e-5
NUM_TRAIN_EPOCHS = 1.0
WARMUP_PROPORTION = 0.1 # Warmup is a period of time where hte learning rate is small and gradually increases--usually helps training.

# Model configs
SAVE_CHECKPOINTS_STEPS = 100
SAVE_SUMMARY_STEPS = 100
MAX_SEQ_LENGTH = 128
# Data Preparation
current_time = datetime.now()
train_dataset = read_data_iterator("dataset/gw_extractions_with_rep.pickle")
def tokenize_if_small_enough(ds):
    small_counter = 0
    big_counter = 0
    for i, d in zip(range(30000), ds):
        try:
            yield prepare_data.tokenize_dataset_dict(d)
            small_counter += 1
        except AssertionError:
            big_counter += 1
            continue
    print("Big:", big_counter, "Small:", small_counter)
            
features = list(tokenize_if_small_enough(train_dataset))
sample_size = len(features)
training_pct = 0.8
train_set_size = int(sample_size * training_pct)
test_set_size = int(sample_size * (1-training_pct))
train_features = features[:train_set_size]
val_features = features[train_set_size:]
print("Data Size: ", sample_size)
print("Data Preparation took time ", datetime.now() - current_time)

# Compute # train and warmup steps from batch size
num_train_steps = int(len(train_features) / BATCH_SIZE * NUM_TRAIN_EPOCHS)
num_warmup_steps = int(num_train_steps * WARMUP_PROPORTION)
print(f'Number of training steps is {num_train_steps}, and number of warmup steps is {num_warmup_steps}')

run_config = tf.estimator.RunConfig(
    model_dir='output',
    save_summary_steps=SAVE_SUMMARY_STEPS,
    save_checkpoints_steps=SAVE_CHECKPOINTS_STEPS,
    log_step_count_steps=100)

model_fn = model_fn_builder(
  num_labels=len(train_features),
  learning_rate=LEARNING_RATE,
  num_train_steps=num_train_steps,
  num_warmup_steps=num_warmup_steps)

estimator = tf.estimator.Estimator(
  model_fn=model_fn,
  config=run_config,
  params={"batch_size": BATCH_SIZE})

# Create an input function for training. drop_remainder = True for using TPUs.
train_input_fn = run_classifier.input_fn_builder(
    features=train_features,
    seq_length=MAX_SEQ_LENGTH,
    is_training=True,
    drop_remainder=False)

eval_input_fn = run_classifier.input_fn_builder(
    features=val_features,
    seq_length=MAX_SEQ_LENGTH,
    is_training=False,
    drop_remainder=False)

train_test_input_fn = run_classifier.input_fn_builder(
    features=train_features,
    seq_length=MAX_SEQ_LENGTH,
    is_training=False,
    drop_remainder=False)

print(f'Beginning Training!')
current_time = datetime.now()
train_spec = tf.estimator.TrainSpec(input_fn=train_input_fn, max_steps=num_train_steps)
eval_spec = tf.estimator.EvalSpec(input_fn=eval_input_fn, throttle_secs=0)# Using default steps=100
tf.estimator.train_and_evaluate(estimator, train_spec, eval_spec)
print("Training took time ", datetime.now() - current_time)

print(f'Evaluating Training Dataset!')
print(estimator.evaluate(input_fn=train_test_input_fn))
print(f'Evaluating Validation Dataset!')
print(estimator.evaluate(input_fn=eval_input_fn))
