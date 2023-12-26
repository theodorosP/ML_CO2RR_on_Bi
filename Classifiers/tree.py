import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error

# Function to calculate RMSE
def calculate_rmse(predictions, targets):
    return np.sqrt(mean_squared_error(predictions, targets))

# Load and preprocess data
# Replace "your_path_here" with the actual path to your CSV file
path_to_database = "your_path_here"
fdata = pd.read_csv(path_to_database)

# Specify the columns to be used in the analysis
selected_columns = ["V_vs_RHE", "binding_energy", "surface_charge", "force", "activation_barrier", "power_density"]
raw_data = fdata.loc[:, selected_columns]

# Fill missing values with the median of each column
median_raw_data = raw_data.median()
dict_median_raw_data = median_raw_data.to_dict()
data = raw_data.fillna(dict_median_raw_data)

# Standardize the data
standardized_data = (data - np.mean(data, axis=0)) / np.std(data, axis=0)

# Split data into X and y
X = standardized_data.iloc[:, :-1].values.astype(np.float32)
y = standardized_data.iloc[:, -1].values.astype(np.float32)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=751)

# Hyperparameter search space for Decision Tree
param_grid = {
    'max_depth': range(5, 21),
    'min_samples_split': range(2, 11),
    'min_samples_leaf': range(1, 11)
}

# Create and train Decision Tree model using GridSearchCV
tree_model = DecisionTreeRegressor(random_state=751)
grid_search = GridSearchCV(tree_model, param_grid, scoring='neg_mean_squared_error', cv=5)
grid_search.fit(X_train, y_train)

# Get the best model and print best hyperparameters
best_tree_model = grid_search.best_estimator_
best_hyperparameters = grid_search.best_params_
print("Best Hyperparameters:")
print(best_hyperparameters)

# Predict using the best model
predict_tree = best_tree_model.predict(X_test)

# Calculate performance metrics
rmse_val = calculate_rmse(predict_tree, y_test)

# Print results
print('Decision Tree, RMSE:', rmse_val)

# Visualize results using seaborn
results_df_tree = pd.DataFrame({
    'Predicted Maximum Power': predict_tree,
    'Real Maximum Power': y_test
})

# Plot results
plt.figure(figsize=(8, 6))
sns.set(style='whitegrid')
sns.scatterplot(x='Predicted Maximum Power', y='Real Maximum Power', data=results_df_tree, color='green', label='Decision Tree')
plt.plot([min(predict_tree), max(predict_tree)], [min(predict_tree), max(predict_tree)], linestyle='--', color='blue', label='Equality Line')
plt.title('Predicted vs. Real Maximum Power (Decision Tree)')
plt.xlabel('Predicted Maximum Power (Standardized)')
plt.ylabel('Real Maximum Power (Standardized)')
plt.legend()
plt.show()
