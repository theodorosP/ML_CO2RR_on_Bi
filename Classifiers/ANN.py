import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras import optimizers
from keras import callbacks
from keras import backend as K

# Function to calculate RMSE
def calculate_rmse(predictions, targets):
    return np.sqrt(mean_squared_error(predictions, targets))

# Function to create and train the ANN model
def train_ann_model(neurons, activation, regularizer, dropout_rate, learning_rate, epochs, batch_size, X_train, y_train, X_test, y_test):
    model = Sequential()
    model.add(Dense(neurons, input_dim=X_train.shape[1], kernel_initializer='random_normal',
                    bias_initializer='random_normal', activation=activation, kernel_regularizer=regularizer))
    model.add(Dropout(dropout_rate))
    model.add(Dense(neurons, input_dim=neurons, kernel_initializer='random_normal',
                    bias_initializer='random_normal', activation=activation, kernel_regularizer=regularizer))
    model.add(Dropout(dropout_rate))
    model.add(Dense(neurons, input_dim=neurons, kernel_initializer='random_normal',
                    bias_initializer='random_normal', activation=activation, kernel_regularizer=regularizer))
    model.add(Dropout(dropout_rate))
    model.add(Dense(neurons, input_dim=neurons, kernel_initializer='random_normal',
                    bias_initializer='random_normal', activation=activation, kernel_regularizer=regularizer))
    model.add(Dropout(dropout_rate))
    model.add(Dense(neurons, input_dim=neurons, kernel_initializer='random_normal',
                    bias_initializer='random_normal', activation=activation, kernel_regularizer=regularizer))
    model.add(Dropout(dropout_rate))
    model.add(Dense(1, activation='linear'))
    
    adam = optimizers.Adam(learning_rate=learning_rate)
    model.compile(loss='mse', optimizer=adam)
    
    early_stopping = callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    model.fit(X_train, y_train, verbose=0, epochs=epochs, batch_size=batch_size, validation_split=0.1,
              callbacks=[callbacks.TensorBoard(log_dir='mytensorboard'), early_stopping])
    
    loss = model.evaluate(X_test, y_test)
    predict_ann = model.predict(X_test)
    return predict_ann, model

# Load and preprocess data
path_to_database = "your_path_here"  # Replace with the actual path
fdata = pd.read_csv(path_to_database)
raw_data = fdata.loc[:, ["V_vs_RHE", "binding_energy", "surface_charge", "force", "activation_barrier", "power_density"]]
median_raw_data = raw_data.median()
dict_median_raw_data = median_raw_data.to_dict()
data = raw_data.fillna(dict_median_raw_data)
standardized_data = (data - np.mean(data, axis=0)) / np.std(data, axis=0)

# Split data into X and y
param = standardized_data.iloc[:, :-1]  # Assuming the last column is the target variable
power = standardized_data.iloc[:, -1]
X = param.values.astype(np.float32)
y = power.values.astype(np.float32)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=751)

# Hyperparameter search space
dropout_list = np.arange(0, 1, 0.1)
best_corr_ann = 0.0

for neurons in range(50, 750, 25):
    for activation in ['relu', 'tanh', 'sigmoid', 'softsign', 'hard_sigmoid', 'softplus']:
        for regularizer_term in [0.0001, 0.0005, 0.0008, 0.001, 0.002, 0.005, 0.0008, 0.01, 0.05, 0.1]:
            for dropout in dropout_list:
                for epochs_number in range(200, 1000, 200):
                    for batch_size_number in range(20, 200, 20):
                        for learning_rate_search in [0.001, 0.002, 0.005, 0.01, 0.02, 0.05]:
                            # Implementing hyperparameters
                            neurons1 = neurons
                            activation1 = activation
                            regularizer = optimizers.l2(regularizer_term)
                            dropout_rate = dropout

                            # Train ANN model with early stopping
                            predict_ann, model = train_ann_model(neurons1, activation1, regularizer, dropout_rate,
                                                                  learning_rate_search, epochs_number, batch_size_number,
                                                                  X_train, y_train, X_test, y_test)

                            # Calculate performance metrics
                            x_prediction_maximum_power_ann = predict_ann * np.std(data, axis=0).iloc[-1] + np.mean(data, axis=0).iloc[-1]
                            y_real_maximum_power = y_test * np.std(data, axis=0).iloc[-1] + np.mean(data, axis=0).iloc[-1]
                            x_prediction_maximum_power_ann = x_prediction_maximum_power_ann[:, 0]
                            x_prediction_maximum_power_ann_series = pd.Series(x_prediction_maximum_power_ann)
                            y_real_maximum_power_series = pd.Series(y_real_maximum_power)
                            corr_ann = round(x_prediction_maximum_power_ann_series.corr(y_real_maximum_power_series), 4)
                            rmse_val = calculate_rmse(x_prediction_maximum_power_ann, y_real_maximum_power)

                            # Print results
                            print('ANN, R2:', corr_ann, 'RMSE:', rmse_val)

                            # Check for the best correlation
                            if 0.96 < corr_ann < 1:
                                if corr_ann > best_corr_ann:
                                    best_corr_ann = corr_ann
                                    best_hyperparameters = {
                                        'neurons': neurons,
                                        'activation': activation,
                                        'regularizer_term': regularizer_term,
                                        'dropout': dropout,
                                        'epochs_number': epochs_number,
                                        'batch_size_number': batch_size_number,
                                        'learning_rate_search': learning_rate_search
                                    }
                                    best_model = model
                                break
                            else:
                                K.clear_session()
                        else:
                            continue
                        break
                    else:
                        continue
                    break
                else:
                    continue
                break
            else:
                continue
            break
        else:
            continue
        break
    else:
        continue
    break

# Print best hyperparameter
print("Best Hyperparameters:")
print(best_hyperparameters)

# Visualize results using seaborn
results_df = pd.DataFrame({
    'Predicted Maximum Power': x_prediction_maximum_power_ann,
    'Real Maximum Power': y_real_maximum_power
})

# Plot results
x_y_x = np.linspace(min(x_prediction_maximum_power_ann), max(x_prediction_maximum_power_ann), 100)
x_y_y = x_y_x  # Assuming a simple equality line

plt.figure(figsize=(8, 6))
sns.set(style='whitegrid')
sns.scatterplot(x='Predicted Maximum Power', y='Real Maximum Power', data=results_df, color='red', label='Artificial Neural Network')
plt.plot(x_y_x, x_y_y, linestyle='--', color='blue', label='Equality Line')
plt.title('Predicted vs. Real Maximum Power')
plt.xlabel('Predicted Maximum Power (mW cm^-2)')
plt.ylabel('Real Maximum Power (mW cm^-2)')
plt.legend()
plt.show()
