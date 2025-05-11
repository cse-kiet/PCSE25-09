import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
import pickle

# Generate synthetic data
np.random.seed(42)
ethnicities = ['Asian', 'Hispanic', 'African-American', 'Caucasian']

# Generate base data
n_samples = 1500
data = {
    'Ethnicity': np.random.choice(ethnicities, n_samples),
    'AQI': np.random.randint(50, 300, n_samples),
    'Smokers_Percentage': np.random.randint(5, 50, n_samples),
    'Lung_Disease': np.zeros(n_samples)  # Default to no disease
}

df = pd.DataFrame(data)

# Add higher-risk scenarios with higher probabilities
high_risk_samples = pd.DataFrame({
    'Ethnicity': np.random.choice(ethnicities, 500),
    'AQI': np.random.randint(200, 300, 500),  # High AQI
    'Smokers_Percentage': np.random.randint(30, 50, 500),  # High smokers percentage
    'Lung_Disease': np.ones(500)  # Disease present
})

# Combine datasets
df = pd.concat([df, high_risk_samples], ignore_index=True)

# Encode ethnicity
encoder = LabelEncoder()
df['Ethnicity'] = encoder.fit_transform(df['Ethnicity'])

# Features and target
X = df[['Ethnicity', 'AQI', 'Smokers_Percentage']]
y = df['Lung_Disease']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train logistic regression model with class weights
model = LogisticRegression(class_weight='balanced')  # Balanced weights to handle skewed data
model.fit(X_train, y_train)

# Save the model
with open('model.pkl', 'wb') as file:
    pickle.dump(model, file)

print("Rebalanced model trained and saved as model.pkl")
