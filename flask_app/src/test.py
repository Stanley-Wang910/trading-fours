import pandas as pd 
import joblib




X_train = joblib.load('../data/models/GenreClassModel/features.joblib')
X_train.to_csv('X_train.csv')                          
