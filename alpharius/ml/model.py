from .dataset import INTERDAY_DIM, INTRADAY_DIM
from alpharius.common import *
from sklearn import metrics
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import regularizers
import datetime
import numpy as np
import tabulate
import tensorflow as tf
import os


def make_model():
    inter_input = layers.Input(shape=(INTERDAY_DIM, 3), name='interday_input')
    intra_input = layers.Input(shape=(INTRADAY_DIM, 2), name='intraday_input')
    inter_lstm = layers.LSTM(25)(inter_input)
    inter_drop = layers.Dropout(0.5)(inter_lstm)
    inter_dense = layers.Dense(15, activation='relu')(inter_drop)
    intra_lstm = layers.LSTM(20)(intra_input)
    intra_drop = layers.Dropout(0.5)(intra_lstm)
    intra_dense = layers.Dense(10, activation='relu')(intra_drop)
    concat = layers.Concatenate(axis=1)([inter_dense, intra_dense])
    concat_drop = layers.Dropout(0.5)(concat)
    dense = layers.Dense(5, activation='relu')(concat_drop)
    dense_droop = layers.Dropout(0.2)(dense)
    output = layers.Dense(1, use_bias=False, activation='tanh',
                          kernel_regularizer=regularizers.L2(1e-2), name='label')(dense_droop)
    model = keras.Model(inputs=[inter_input, intra_input], outputs=[output])
    return model


class Model:

    def __init__(self):
        self._model = None
        output_num = 1
        ml_output_dir = os.path.join(OUTPUT_ROOT, 'ml')
        while True:
            output_dir = os.path.join(ml_output_dir,
                                      datetime.datetime.now().strftime('%m-%d'),
                                      f'{output_num:02d}')
            if not os.path.exists(output_dir):
                self._output_dir = output_dir
                os.makedirs(output_dir, exist_ok=True)
                break
            output_num += 1
        self._logger = logging_config(os.path.join(self._output_dir, 'evaluation.txt'),
                                      detail=False,
                                      name='evaluation')
        self._total_tp, self._total_fp = 0, 0

    def train(self, data, labels):
        bins = [-1 + i for i in range(4)]
        histogram = np.histogram(labels, bins=bins)[0]
        self._logger.info(f'Input distribution:\n{tabulate.tabulate([bins[:-1], histogram], tablefmt="grid")}')
        tf.random.set_seed(0)
        self._model = make_model()
        self._model.compile(optimizer='adam', loss='mse')
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='loss', patience=10, restore_best_weights=True)
        w = np.arange(len(labels)) / len(labels) + 0.5
        self._model.fit(x=data, y=labels, sample_weight=w, batch_size=512, epochs=1000, callbacks=[early_stopping])

    def save(self, output_path: str):
        self._model.save(output_path)

    def load(self, input_path: str):
        self._model = keras.models.load_model(input_path)

    def predict(self, data, long_threshold, short_threshold):
        results = self._model.predict(data)
        bins = [-1 + 0.25 * i for i in range(8)] + [float('inf')]
        histogram = np.histogram(results, bins=bins)[0]
        self._logger.info(f'Prediction distribution:\n{tabulate.tabulate([bins[:-1], histogram], tablefmt="grid")}')
        int_results = []
        for result in results:
            if result > long_threshold:
                int_results.append(1)
            elif result < short_threshold:
                int_results.append(-1)
            else:
                int_results.append(0)
        return int_results

    def evaluate(self, data, labels, long_threshold=0.5, short_threshold=-0.5):
        int_results = self.predict(data, long_threshold, short_threshold)
        accuracy = metrics.accuracy_score(labels, int_results)
        short_precision, _, long_precision = metrics.precision_score(labels, int_results, average=None)
        confusion = metrics.confusion_matrix(labels, int_results)
        confusion_matrix = [['', 'y_pred=-1', 'y_pred=0', 'y_pred=1']] + \
                           [[name] + list(row) for name, row in zip(['y_true=-1', 'y_true=0', 'y_true=1'],
                                                                    confusion)]
        self._logger.info(f'Accuracy: {accuracy : .4f}')
        self._logger.info(f'Long precision: {long_precision : .4f}')
        self._logger.info(f'Short precision: {short_precision : .4f}')
        self._logger.info(f'Long precision (flat excluded): '
                          f'{confusion[2][2] / (confusion[0][2] + confusion[2][2] + 1E-7): .4f}')
        self._logger.info(f'Short precision (flat excluded): '
                          f'{confusion[0][0] / (confusion[0][0] + confusion[2][0] + 1E-7): .4f}')
        self._logger.info(f'Confusion matrix:\n{tabulate.tabulate(confusion_matrix, tablefmt="grid")}')
        self._total_tp += confusion[2][2]
        self._total_fp += confusion[0][2]

    def log_title(self, title):
        self._logger.info(get_header(title))

    def summarize(self):
        tp = self._total_tp
        fp = self._total_fp
        self._logger.info(f'Estimated success rate: {tp / (tp + fp + 1E-7) : .4f} ({tp} / {tp + fp})')
