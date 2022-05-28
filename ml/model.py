from sklearn import metrics
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import regularizers
import datetime
import numpy as np
import tabulate
import tensorflow as tf
import os

_ML_ROOT = os.path.dirname(os.path.realpath(__file__))
_ROOT = os.path.dirname(_ML_ROOT)


def make_model():
    inter_input = layers.Input(shape=(240, 3))
    intra_input = layers.Input(shape=(66, 3))
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
    output = layers.Dense(1, use_bias=False, activation='tanh', kernel_regularizer=regularizers.L2(1e-2))(dense_droop)
    model = keras.Model(inputs=[inter_input, intra_input], outputs=[output])
    return model


class Model:

    def __init__(self):
        self._model = None
        output_num = 1
        ml_output_dir = os.path.join(_ML_ROOT, 'outputs')
        while True:
            output_dir = os.path.join(ml_output_dir,
                                      datetime.datetime.now().strftime('%m-%d'),
                                      f'{output_num:02d}')
            if not os.path.exists(output_dir):
                self._output_dir = output_dir
                os.makedirs(output_dir, exist_ok=True)
                break
            output_num += 1

    def train(self, data, labels):
        tf.random.set_seed(0)
        self._model = make_model()
        self._model.compile(optimizer='adam', loss='mse')
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='loss', patience=10, restore_best_weights=True)
        w = np.arange(len(labels)) / len(labels) + 0.5
        self._model.fit(x=data, y=labels, sample_weight=w, batch_size=512, epochs=1000, callbacks=[early_stopping])

    def save(self, output_file):
        output_path = os.path.join(_ML_ROOT, 'models', output_file)
        self._model.save(output_path)

    def load(self, input_file):
        input_path = os.path.join(_ML_ROOT, 'models', input_file)
        self._model = keras.models.load_model(input_path)

    def predict(self, data, long_threshold, short_threshold):
        results = self._model.predict(data)
        bins = [-1 + 0.25 * i for i in range(8)] + [float('inf')]
        histogram = np.histogram(results, bins=bins)[0]
        self.print(f'Pred Result distribution:\n{tabulate.tabulate([bins[:-1], histogram], tablefmt="grid")}')
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
        confusion_matrix = [['', 'y_pred=-1', 'y_pred=0', 'y_pred=1']] + \
                           [[name] + list(row) for name, row in zip(['y_true=-1', 'y_true=0', 'y_true=1'],
                                                                    metrics.confusion_matrix(labels, int_results))]
        self.print(f'Accuracy: {accuracy : .4f}')
        self.print(f'Long precision: {long_precision : .4f}')
        self.print(f'Short precision: {short_precision : .4f}')
        self.print(f'Confusion matrix:\n{tabulate.tabulate(confusion_matrix, tablefmt="grid")}')

    def print(self, output_string):
        output_file = os.path.join(self._output_dir, 'evaluation.txt')
        with open(output_file, 'a') as f:
            f.write(output_string)
            f.write('\n')
        print(output_string)
