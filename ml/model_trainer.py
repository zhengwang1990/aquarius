from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf
import os


_ML_ROOT = os.path.dirname(os.path.realpath(__file__))


def make_model():
    inter_input = layers.Input(shape=(240, 3))
    intra_input = layers.Input(shape=(68, 2))
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


class ModelTrainer:

    def __init__(self):
        self._model = None

    def train(self, data, labels):
        tf.random.set_seed(0)
        self._model = make_model()
        self._model.compile(optimizer='adam', loss='mse')
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss', patience=10, restore_best_weights=True)
        self._model.fit(x=data, y=labels, batch_size=512, epoch=1000, callbacks=[early_stopping])

    def save(self, output_file):
        output_path = os.path.join(_ML_ROOT, 'models', output_file)
        self._model.save(output_path)
