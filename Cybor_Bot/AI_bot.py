import pandas as pd
import numpy as np
from numpy.linalg import norm
import warnings
import tensorflow as tf
from tensorflow.keras import layers, activations, models, preprocessing, utils
from tf_keras.models import load_model
import pandas as pd

warnings.filterwarnings("ignore")


class AI_BOT:
    """AI CHAT BOT"""

    def __init__(self) -> None:
        self.encoder_input_data = None
        self.max_input_length = None
        self.input_word_dict = None
        self.num_input_tokens = None
        self.decoder_input_data = None
        self.max_output_length = None
        self.output_word_dict = None
        self.num_output_tokens = None
        self.tokenized_output_lines = None
        self.loaded_model = self.load_trained_model()

    def read_data(self):
        """Read data"""
        dataframe = pd.read_csv("mera_hr.csv", header=0, names=["input", "output"])
        return dataframe

    def input_data_for_encoder(self, dataframe: pd.DataFrame):
        """input data preparation for encoder"""
        input_lines = list()
        for line in dataframe.input:
            input_lines.append(line)

        tokenizer = preprocessing.text.Tokenizer()
        tokenizer.fit_on_texts(input_lines)
        tokenized_input_lines = tokenizer.texts_to_sequences(input_lines)

        length_list = list()
        for token_seq in tokenized_input_lines:
            length_list.append(len(token_seq))
        self.max_input_length = np.array(length_list).max()
        print("Input max length is {}".format(self.max_input_length))

        padded_input_lines = preprocessing.sequence.pad_sequences(
            tokenized_input_lines, maxlen=self.max_input_length, padding="post"
        )
        self.encoder_input_data = np.array(padded_input_lines)
        print("Encoder input data shape -> {}".format(self.encoder_input_data.shape))

        self.input_word_dict = tokenizer.word_index
        self.num_input_tokens = len(self.input_word_dict) + 1
        print("Number of Input tokens = {}".format(self.num_input_tokens))

    def input_data_for_decoder(self, dataframe: pd.DataFrame):
        """Input data preparation for decoder"""
        output_lines = list()
        for line in dataframe.output:
            output_lines.append("<START> " + line + " <END>")

        tokenizer = preprocessing.text.Tokenizer()
        tokenizer.fit_on_texts(output_lines)
        self.tokenized_output_lines = tokenizer.texts_to_sequences(output_lines)

        length_list = list()
        for token_seq in self.tokenized_output_lines:
            length_list.append(len(token_seq))
        self.max_output_length = np.array(length_list).max()
        print("Output max length is {}".format(self.max_output_length))

        padded_output_lines = preprocessing.sequence.pad_sequences(
            self.tokenized_output_lines, maxlen=self.max_output_length, padding="post"
        )
        self.decoder_input_data = np.array(padded_output_lines)
        print("Decoder input data shape -> {}".format(self.decoder_input_data.shape))

        self.output_word_dict = tokenizer.word_index
        self.num_output_tokens = len(self.output_word_dict) + 1
        print("Number of Output tokens = {}".format(self.num_output_tokens))

    def output_data_for_decoder(self):
        """Output data for deocder"""
        decoder_target_data = list()
        for token_seq in self.tokenized_output_lines:
            decoder_target_data.append(token_seq[1:])

        padded_output_lines = preprocessing.sequence.pad_sequences(
            decoder_target_data, maxlen=self.max_output_length, padding="post"
        )
        onehot_output_lines = utils.to_categorical(
            padded_output_lines, self.num_output_tokens
        )
        self.decoder_target_data = np.array(onehot_output_lines)
        print("Decoder target data shape -> {}".format(self.decoder_target_data.shape))

    def setup_encoder_decoder_data(self):
        """Setup encoder and decoder data"""
        self.encoder_inputs = tf.keras.layers.Input(shape=(None,))
        self.encoder_embedding = tf.keras.layers.Embedding(
            self.num_input_tokens, 256, mask_zero=True
        )(self.encoder_inputs)
        encoder_outputs, state_h, state_c = tf.keras.layers.LSTM(
            256, return_state=True, recurrent_dropout=0.2, dropout=0.2
        )(self.encoder_embedding)
        self.encoder_states = [state_h, state_c]

        self.decoder_inputs = tf.keras.layers.Input(shape=(None,))
        self.decoder_embedding = tf.keras.layers.Embedding(
            self.num_output_tokens, 256, mask_zero=True
        )(self.decoder_inputs)
        self.decoder_lstm = tf.keras.layers.LSTM(
            256,
            return_state=True,
            return_sequences=True,
            recurrent_dropout=0.2,
            dropout=0.2,
        )
        self.decoder_outputs, _, _ = self.decoder_lstm(
            self.decoder_embedding, initial_state=self.encoder_states
        )
        decoder_dense = tf.keras.layers.Dense(
            self.num_output_tokens, activation=tf.keras.activations.softmax
        )
        self.output = decoder_dense(self.decoder_outputs)

    def train_model(self, batch_size, epoch):
        """Train model"""
        model = tf.keras.models.Model(
            [self.encoder_inputs, self.decoder_inputs], self.output
        )
        model.compile(
            optimizer=tf.keras.optimizers.Adam(), loss="categorical_crossentropy"
        )

        model.summary()
        model.fit(
            [self.encoder_input_data, self.decoder_input_data],
            self.decoder_target_data,
            batch_size=batch_size,
            epochs=epoch,
        )
        model.save("model_new.h5")
        return model

    def load_trained_model(self):
        """Load trained model"""
        model = load_model("AI-Projects/Cybor_Bot/model10.h5", compile=False)
        print(model.summary)
        return model

    def encoder_decoder_model(self, model):
        self.encoder_inputs = model.input[0]
        embedding_layer_1 = model.layers[2]

        self.encoder_embedding = embedding_layer_1(self.encoder_inputs)
        self.encoder_lstm = model.layers[4]
        encoder_output, state_h, state_c = self.encoder_lstm(self.encoder_embedding)
        self.encoder_states = [state_h, state_c]

        self.decoder_inputs = model.input[1]
        self.decoder_embedding = model.layers[3](self.decoder_inputs)
        self.decoder_lstm = model.layers[5]
        self.decoder_outputs, _, _ = self.decoder_lstm(
            self.decoder_embedding, initial_state=self.encoder_states
        )

        decoder_state_input_h = tf.keras.layers.Input(shape=(256,))
        decoder_state_input_c = tf.keras.layers.Input(shape=(256,))

        self.decoder_state_inputs = [decoder_state_input_h, decoder_state_input_c]
        self.new_decoder_outputs, new_state_h, new_state_c = self.decoder_lstm(
            self.decoder_embedding, initial_state=self.decoder_state_inputs
        )
        self.decoder_states = [new_state_h, new_state_c]
        self.new_decoder_outputs = model.layers[6](self.new_decoder_outputs)

        encoder_model = tf.keras.models.Model(self.encoder_inputs, self.encoder_states)
        decoder_model = tf.keras.models.Model(
            [self.decoder_inputs] + self.decoder_state_inputs,
            [self.new_decoder_outputs] + self.decoder_states,
        )

        return encoder_model, decoder_model

    def str_to_tokens(self, sentence: str):
        words = sentence.lower().split()
        tokens_list = list()
        for word in words:
            tokens_list.append(self.input_word_dict[word])
        return preprocessing.sequence.pad_sequences(
            [tokens_list], maxlen=self.max_input_length, padding="post"
        )

    def predict_output(self, question: str):
        """Predict output"""
        model = self.loaded_model
        enc_model, dec_model = self.encoder_decoder_model(model)
        states_values = enc_model.predict(self.str_to_tokens(question))
        empty_target_seq = np.zeros((1, 1))
        empty_target_seq[0, 0] = self.output_word_dict["start"]
        stop_condition = False
        decoded_translation = ""
        while not stop_condition:
            dec_outputs, h, c = dec_model.predict([empty_target_seq] + states_values)
            sampled_word_index = np.argmax(dec_outputs[0, -1, :])
            sampled_word = None
            for word, index in self.output_word_dict.items():
                if sampled_word_index == index:
                    decoded_translation += " {}".format(word)
                    sampled_word = word

            if (
                sampled_word == "end"
                or len(decoded_translation.split()) > self.max_output_length
            ):
                stop_condition = True

            empty_target_seq = np.zeros((1, 1))
            empty_target_seq[0, 0] = sampled_word_index
            states_values = [h, c]

        return decoded_translation.replace(" end", "")

    def run(self):
        """run"""
        lines = pd.read_csv("new_hr_data.csv", header=0, names=["input", "output"])
        # lines=lines.drop(index=0)
        # lines=lines.drop(index=33)
        lines.head(5)
        input_lines = list()
        for line in lines.input:
            input_lines.append(line)

        tokenizer = preprocessing.text.Tokenizer()
        tokenizer.fit_on_texts(input_lines)
        tokenized_input_lines = tokenizer.texts_to_sequences(input_lines)

        length_list = list()
        for token_seq in tokenized_input_lines:
            length_list.append(len(token_seq))
        max_input_length = np.array(length_list).max()
        print("Input max length is {}".format(max_input_length))

        padded_input_lines = preprocessing.sequence.pad_sequences(
            tokenized_input_lines, maxlen=max_input_length, padding="post"
        )
        encoder_input_data = np.array(padded_input_lines)
        print("Encoder input data shape -> {}".format(encoder_input_data.shape))

        input_word_dict = tokenizer.word_index
        num_input_tokens = len(input_word_dict) + 1
        print("Number of Input tokens = {}".format(num_input_tokens))
        output_lines = list()
        for line in lines.output:
            output_lines.append("<START> " + line + " <END>")

        tokenizer = preprocessing.text.Tokenizer()
        tokenizer.fit_on_texts(output_lines)
        tokenized_output_lines = tokenizer.texts_to_sequences(output_lines)

        length_list = list()
        for token_seq in tokenized_output_lines:
            length_list.append(len(token_seq))
        max_output_length = np.array(length_list).max()
        print("Output max length is {}".format(max_output_length))

        padded_output_lines = preprocessing.sequence.pad_sequences(
            tokenized_output_lines, maxlen=max_output_length, padding="post"
        )
        decoder_input_data = np.array(padded_output_lines)
        print("Decoder input data shape -> {}".format(decoder_input_data.shape))

        output_word_dict = tokenizer.word_index
        num_output_tokens = len(output_word_dict) + 1
        print("Number of Output tokens = {}".format(num_output_tokens))
        decoder_target_data = list()
        for token_seq in tokenized_output_lines:
            decoder_target_data.append(token_seq[1:])

        padded_output_lines = preprocessing.sequence.pad_sequences(
            decoder_target_data, maxlen=max_output_length, padding="post"
        )
        onehot_output_lines = utils.to_categorical(
            padded_output_lines, num_output_tokens
        )
        decoder_target_data = np.array(onehot_output_lines)
        print("Decoder target data shape -> {}".format(decoder_target_data.shape))
        encoder_inputs = tf.keras.layers.Input(shape=(None,))
        encoder_embedding = tf.keras.layers.Embedding(
            num_input_tokens, 256, mask_zero=True
        )(encoder_inputs)
        encoder_outputs, state_h, state_c = tf.keras.layers.LSTM(
            256, return_state=True, recurrent_dropout=0.2, dropout=0.2
        )(encoder_embedding)
        encoder_states = [state_h, state_c]

        decoder_inputs = tf.keras.layers.Input(shape=(None,))
        decoder_embedding = tf.keras.layers.Embedding(
            num_output_tokens, 256, mask_zero=True
        )(decoder_inputs)
        decoder_lstm = tf.keras.layers.LSTM(
            256,
            return_state=True,
            return_sequences=True,
            recurrent_dropout=0.2,
            dropout=0.2,
        )
        decoder_outputs, _, _ = decoder_lstm(
            decoder_embedding, initial_state=encoder_states
        )
        decoder_dense = tf.keras.layers.Dense(
            num_output_tokens, activation=tf.keras.activations.softmax
        )
        output = decoder_dense(decoder_outputs)

        model = tf.keras.models.Model([encoder_inputs, decoder_inputs], output)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(), loss="categorical_crossentropy"
        )

        model.summary()
        model.fit(
            [encoder_input_data, decoder_input_data],
            decoder_target_data,
            batch_size=64,
            epochs=500,
        )
        model.save("model_new.h5")
        return model

    # def model_fit(self,model):
    #     """model_fit"""
    #     model.fit([encoder_input_data , decoder_input_data], decoder_target_data, batch_size=64, epochs=500)
    #     model.save( 'model_new.h5' )
    #     return model


if __name__ == "__main__":
    bot = AI_BOT()
    df = bot.read_data()
    bot.input_data_for_encoder(df)
    bot.input_data_for_decoder(df)
    bot.output_data_for_decoder()
    bot.setup_encoder_decoder_data()
    # bot=AI_BOT()
    df = bot.read_data()
    bot.input_data_for_encoder(df)
    bot.input_data_for_decoder(df)
    bot.output_data_for_decoder()
    bot.setup_encoder_decoder_data()
    # bot.train_model("128","2")
    print(bot.predict_output("what is the dress code in office"))
    print(bot.predict_output("how to activate darwinbox account"))
    # data = pd.read_csv("new_hr_data.csv")
    # question="how can i see my profile on darwinbox"
    # df=bot.create_num_vector(data)
    # index=bot.match_vector_similarity(df,question)
    # print(data['Answers'][index-1])
    # kk=bot.model_fit(model)
