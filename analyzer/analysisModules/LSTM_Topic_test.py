from keras.preprocessing.text import Tokenizer #Needed?
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from keras.layers import LSTM, Input, Dense
from keras import Model
import keras.backend as K
import os.path
from scipy import spatial



#load articles and labels from DB:
articles
labels
#clean data
#create FastTextVectors for articles and labels

if not os.path.isfile("test.model"):

	#create model:
	inputs = Input(shape=(None, 300)) # unknown timespan, fixed feature size
	x = LSTM(128, return_sequences=True)(inputs)
	x = LSTM(128, return_sequences=True)(x)
	x = Dense(256, activation="relu")(x)
	outputs = Dense(10, activation="softmax")(x)
	
	model = Model(inputs=inputs, outputs=outputs)
	
	model.summary()

	model.save("test.model")
	
	del model


model = keras.models.load_model("test.model")


def custom_loss(y_true, y_pred):
	distances=[]
	for i, p_word in enumerate(y_pred):
		for j, r_word in enumerate(y_true):
			dist = spatial.distance.cosine(r_word, p_word) 
 			distances.append( (i,j, dist) )
 	for i in range(min(len(y_pred),len(y_true)))
 		minimum=distances[0]
 		for distance in distances:
 			if distance[2] < minimum[2]:
 				maximum = distance
 		for distance in distances:
 			if distance[1] == maximum[1] and distance != maximum:
 				distances.remove(distance)
 	loss = 0
 	for distance in distances:
 			loss += distance[2]
 	if len(y_pred) > len(y_true):
 		#insert weight for additional topics
 		pass
 		#possible use length of vector before softmax?
    return loss

#train model
model.compile(
    loss=custom_loss,
    optimizer=keras.optimizers.Adam(),
    metrics=["accuracy"],
)

history = model.fit(x_train, y_train, batch_size=64, epochs=2, validation_split=0.2)

test_scores = model.evaluate(x_test, y_test, verbose=2)
print("Test loss:", test_scores[0])
print("Test accuracy:", test_scores[1])

model.save("test.model")

#test model on examples


