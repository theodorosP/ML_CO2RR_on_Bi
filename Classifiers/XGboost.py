import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler  # Added import
from xgboost import XGBRegressor

# Function to calculate RMSE
def calculate_rmse(predictions, targets):
    return np.sqrt(mean_squared_error(predictions, targets))

# Load and preprocess data
path_to_database = "your_path_here"  # Replace with the actual path
fdata = pd.read_csv(path_to_database)
raw_data = fdata.loc[:, ["V_vs_RHE", "binding_energy", "surface_charge", "force", "activation_barrier", "power_density"]]
median_raw_data = raw_data.median()
dict_median_raw_data = median_raw_data.to_dict()
data = raw_data.fillna(dict_median_raw_data)
scaler = StandardScaler()
standardized_data = pd.DataFrame(scaler.fit_transform(data), columns=data.columns)

# Split data into X and y
X = standardized_data.iloc[:, :-1].values.astype(np.float32)
y = standardized_data.iloc[:, -1].values.astype(np.float32)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=751)

# Hyperparameter search space for XGBoost
param_grid = {
    'max_depth': range(3, 10),
    'learning_rate': [0.001, 0.01, 0.1, 0.2, 0.3],
    'n_estimators': [50, 100, 150, 200],
    'subsample': [0.8, 0.9, 1.0],
    'colsample_bytree': [0.8, 0.9, 1.0]
}

# Create and train XGBoost model using GridSearchCV
xgb_model = XGBRegressor(objective='reg:squarederror', random_state=751)
grid_search_xgb = GridSearchCV(xgb_model, param_grid, scoring='neg_root_mean_squared_error', cv=5)
grid_search_xgb.fit(X_train, y_train)

# Get the best model and print best hyperparameters
best_xgb_model = grid_search_xgb.best_estimator_
best_hyperparameters_xgb = grid_search_xgb.best_params_
print("Best Hyperparameters (XGBoost):")
print(best_hyperparameters_xgb)

# Predict using the best model
predict_xgb = best_xgb_model.predict(X_test)

# Calculate performance metrics
x_prediction_maximum_power_xgb = predict_xgb * scaler.scale_[-1] + scaler.mean_[-1]
y_real_maximum_power = y_test * scaler.scale_[-1] + scaler.mean_[-1]
rmse_val = calculate_rmse(x_prediction_maximum_power_xgb, y_real_maximum_power)

# Print results
print('XGBoost, RMSE:', rmse_val)

# Visualize results using seaborn
results_df_xgb = pd.DataFrame({
    'Predicted Maximum Power': x_prediction_maximum_power_xgb,
    'Real Maximum Power': y_real_maximum_power
})

# Plot results
x_y_x = np.linspace(min(x_prediction_maximum_power_xgb), max(x_prediction_maximum_power_xgb), 100)
x_y_y = x_y_x  # Assuming a simple equality line

plt.figure(figsize=(8, 6))
sns.set(style='whitegrid')
sns.scatterplot(x='Predicted Maximum Power', y='Real Maximum Power', data=results_df_xgb, color='purple', label='XGBoost')
plt.plot(x_y_x, x_y_y, linestyle='--', color='blue', label='Equality Line')
plt.title('Predicted vs. Real Maximum Power (XGBoost)')
plt.xlabel('Predicted Maximum Power (mW cm^-2)')
plt.ylabel('Real Maximum Power (mW cm^-2)')
plt.legend()
plt.show()
