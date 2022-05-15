from sklearn import metrics
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import tabulate
import tensorflow as tf
import os

_ML_ROOT = os.path.dirname(os.path.realpath(__file__))


def make_model():
    inter_input = layers.Input(shape=(240, 3))
    intra_input = layers.Input(shape=(67, 2))
    inter_lstm = layers.LSTM(25)(inter_input)
    inter_drop = layers.Dropout(0.2)(inter_lstm)
    inter_dense = layers.Dense(15, activation='relu')(inter_drop)
    intra_lstm = layers.LSTM(20)(intra_input)
    intra_drop = layers.Dropout(0.2)(intra_lstm)
    intra_dense = layers.Dense(10, activation='relu')(intra_drop)
    concat = layers.Concatenate(axis=1)([inter_dense, intra_dense])
    dense = layers.Dense(5, activation='relu')(concat)
    output = layers.Dense(1, activation='tanh')(dense)
    model = keras.Model(inputs=[inter_input, intra_input], outputs=[output])
    return model


class Model:

    def __init__(self):
        self._model = None

    def train(self, data, labels):
        tf.random.set_seed(0)
        self._model = make_model()
        self._model.compile(optimizer='adam', loss='mse')
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='loss', patience=10, restore_best_weights=True)
        self._model.fit(x=data, y=labels, batch_size=512, epochs=1000, callbacks=[early_stopping])

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
        print(f'Pred Result distribution:\n{tabulate.tabulate([bins[:-1], histogram], tablefmt="grid")}')
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
        print('Accuracy:', accuracy)
        print('Long precision:', long_precision)
        print('Short precision:', short_precision)
        print(f'Confusion matrix:\n{tabulate.tabulate(confusion_matrix, tablefmt="grid")}')
