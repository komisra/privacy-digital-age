import nest_asyncio
nest_asyncio.apply()
import collections
import numpy as np
import tensorflow as tf
import tensorflow_federated as tff

SEED = 200328059  #TODO: set seed to stuent ID number
np.random.seed(SEED) #TODO: random number generator seed set to stuent ID number

# preprocess the input data 
def preprocess(dataset, epoch):
  def batch_format_fn(element):
    """Flatten a batch `pixels` and return the features as an `OrderedDict`."""
    return collections.OrderedDict(
        x=tf.reshape(element['pixels'], [-1, 784]),
        y=tf.reshape(element['label'], [-1, 1]))

  return dataset.repeat(epoch).shuffle(100, seed=SEED).batch(
      20).map(batch_format_fn).prefetch(10)

# combine data from multiple clients
def make_federated_data(client_data, client_ids, epoch):
  return [
      preprocess(client_data.create_tf_dataset_for_client(x), epoch)
      for x in client_ids
  ]

# download the MNIST data 
emnist_train, emnist_test = tff.simulation.datasets.emnist.load_data()
print ("Total number of clients: ",len(emnist_train.client_ids))

# determine the sample data input data structure for ML model 
example_dataset = emnist_train.create_tf_dataset_for_client(emnist_train.client_ids[0])
preprocessed_example_dataset = preprocess(example_dataset, 0)

# Neural network model
def create_keras_model():
  return tf.keras.models.Sequential([
      tf.keras.layers.InputLayer(input_shape=(784,)),
      tf.keras.layers.Dense(10, kernel_initializer='zeros'),
      tf.keras.layers.Softmax(),
  ])
  
def model_fn():
  # We _must_ create a new model here, and _not_ capture it from an external
  # scope. TFF will call this within different graph contexts.
  keras_model = create_keras_model()
  return tff.learning.from_keras_model(
      keras_model,
      input_spec=preprocessed_example_dataset.element_spec,
      loss=tf.keras.losses.SparseCategoricalCrossentropy(),
      metrics=[tf.keras.metrics.SparseCategoricalAccuracy()])

NUM_CLIENTS = 5 #TODO: change number of clients as needed
NUM_EPOCHS = 5 #TODO: change the number of training epoch for local training by each client

## you need to iteratively change NUM_CLIENTS for part 'a'
for NUM_CLIENTS in [5, 50, 100]:
    sample_clients = np.random.choice(emnist_train.client_ids, NUM_CLIENTS)
    print ("Client IDs selected: ", sample_clients)

    # conside data from only the selected clients
    federated_train_data = make_federated_data(emnist_train, sample_clients, NUM_EPOCHS)
    print(f'Number of client datasets considered: {len(sample_clients)}')

    # Initialize the iterative training object with the right learning parameter
    iterative_process = tff.learning.build_federated_averaging_process(
        model_fn,
        client_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=0.01),
        server_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=1.0))

    # initialize the parameters of the ML model (you need to initialize this each time you change the client number or epoch numer)
    state = iterative_process.initialize()

    # total number of server and client interactions
    NUM_ROUNDS = 11
    for round_num in range(1, NUM_ROUNDS):
      state, metrics = iterative_process.next(state, federated_train_data)
      print('round {:2d}, training accuracy= {}%'.format(round_num, metrics['train']['sparse_categorical_accuracy']*100))

    # evalute the latest converged model 
    evaluation = tff.learning.build_federated_evaluation(model_fn)
    federated_test_data = make_federated_data(emnist_test, sample_clients, 5)
    test_metrics = evaluation(state.model, federated_test_data)
    print('Test Accuracy: {}%'.format(str(test_metrics['eval']['sparse_categorical_accuracy']*100)))

## you need to iteratively change NUM_EPOCHS for part 'b'
for NUM_EPOCHS in [5, 50, 100]:
    sample_clients = np.random.choice(emnist_train.client_ids, NUM_CLIENTS)
    print ("Client IDs selected: ", sample_clients)

    # conside data from only the selected clients
    federated_train_data = make_federated_data(emnist_train, sample_clients, NUM_EPOCHS)
    print(f'Number of client datasets considered: {len(sample_clients)}')

    # Initialize the iterative training object with the right learning parameter
    iterative_process = tff.learning.build_federated_averaging_process(
        model_fn,
        client_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=0.01),
        server_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=1.0))

    # initialize the parameters of the ML model (you need to initialize this each time you change the client number or epoch numer)
    state = iterative_process.initialize()

    # total number of server and client interactions
    NUM_ROUNDS = 11
    for round_num in range(1, NUM_ROUNDS):
      state, metrics = iterative_process.next(state, federated_train_data)
      print('round {:2d}, training accuracy= {}%'.format(round_num, metrics['train']['sparse_categorical_accuracy']*100))

    # evalute the latest converged model 
    evaluation = tff.learning.build_federated_evaluation(model_fn)
    federated_test_data = make_federated_data(emnist_test, sample_clients, 5)
    test_metrics = evaluation(state.model, federated_test_data)
    print('Test Accuracy: {}%'.format(str(test_metrics['eval']['sparse_categorical_accuracy']*100)))