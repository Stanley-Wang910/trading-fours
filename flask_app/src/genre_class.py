import joblib
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, precision_recall_curve, average_precision_score, roc_curve, auc
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import spotify_client as sp




class GenreClassifier:
    # def __init__(self):
    #     # self.data = pd.read_csv("rec_dataset.csv", index_col=0)
    #     self.lr_model = LogisticRegression(max_iter=500, class_weight='balanced', random_state=420, verbose=0) # Make random state 69
    #     self.rf_model = RandomForestClassifier(
    #         n_estimators=200,             # Use 200 trees
    #         max_depth=10,                 # Maximum depth of 30
    #         min_samples_split=10,         # Split nodes only if at least 10 samples
    #         min_samples_leaf=2,           # Ensure each leaf has at least 2 samples
    #         max_features='sqrt',          # Use sqrt of total features for each split
    #         class_weight='balanced',      # Adjust weights inversely proportional to class frequencies
    #         bootstrap=True,               # Use bootstrap samples
    #         random_state=69,              # Set random state for reproducibility
    #         verbose=1                     # Enable verbose output
    #     )
    #     self.scaler = MinMaxScaler()
    #     self.label_encoder = LabelEncoder()

    # def preprocess_data(self):
    #     # Test
    #     self.data = self.data.drop('popularity', axis=1)

    #     if 'Unnamed: 0' in self.data.columns:
    #         self.data = self.data.drop('Unnamed: 0', axis=1)
        
    #     categorical_features = ['key', 'mode', 'time_signature']
    #     self.data = pd.get_dummies(self.data, columns=categorical_features)  # One-hot encode categorical features

    #     # Encode the labels
    #     self.data['track_genre'] = self.label_encoder.fit_transform(self.data['track_genre'])  # Encode track_genre labels

    # def train_test_split(self, test_size=0.2):
    #     # Define features and target
    #     X = self.data.drop(['track_id', 'artists', 'track_name', 'track_genre'], axis=1)  # Drop unnecessary columns from features
    #     y = self.data['track_genre']  # Set track_genre as the target variable
        
    #     self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=test_size, random_state=69, stratify=y)  # Split data into train and test sets with stratified sampling
    #     self.X_train_df = self.X_train.copy()  # Create a copy of X_train for saving the features
    #     self.scaler.fit(self.X_train)  # Fit the scaler on X_train
    #     self.X_train = self.scaler.transform(self.X_train)  # Scale X_train
    #     self.X_test = self.scaler.transform(self.X_test)  # Scale X_test

    # # def tune_hyperparameters(self):

    #     rf_param_grid = {
    #         'n_estimators': [100, 150, 200],
    #         'max_depth': [10, 20, 30, None],
    #         'min_samples_split': [2, 5, 10],   
    #         'min_samples_leaf': [1, 2, 4],
    #         'max_features': ['auto', 'sqrt', 'log2'],
    #         'class_weight': ['balanced', 'balanced_subsample'],
    #         'bootstrap': [True, False]
    #     }

    #     rf_grid_search = GridSearchCV(self.rf_model, rf_param_grid, cv=3, n_jobs=-1, verbose=2)

    #     rf_grid_search.fit(self.X_train, self.y_train)

    #     self.rf_model = rf_grid_search.best_estimator_

    #     print("Best hyperparameters:", rf_grid_search.best_params_)

    # def train_save_model(self):
    #     # Access these from bash script
    #     rf_model_filename = '../data/models/GenreClassModel/rf_model2.joblib'  # Define the filename for the random forest model
    #     scaler_filename = '../data/models/GenreClassModel/scaler2.joblib'  # Define the filename for the scaler
    #     encoder_filename = '../data/models/GenreClassModel/encoder2.joblib'  # Define the filename for the label encoder
    #     features_filename = '../data/models/GenreClassModel/features2.joblib'  # Define the filename for the features

    #     # Train and save the logistic regression model
    #     # self.lr_model.fit(self.X_train, self.y_train)  # Train the logistic regression model
    #     # joblib.dump(self.lr_model, lr_model_filename, compress=3)  # Save the logistic regression model to a file
    #     # print(f"Logistic Regression model saved to {lr_model_filename}")

    #     # Train and save the random forest model
    #     self.rf_model.fit(self.X_train, self.y_train)  # Train the random forest model
    #     joblib.dump(self.rf_model, rf_model_filename, compress=3)  # Save the random forest model to a file
    #     print(f"Random Forest model saved to {rf_model_filename}")


    #     # Save scaler
    #     joblib.dump(self.scaler, scaler_filename)  # Save the scaler to a file
    #     print(f"Scaler saved to {scaler_filename}")

    #     # Save encoder 
    #     joblib.dump(self.label_encoder, encoder_filename)  # Save the label encoder to a file
    #     print(f"Label Encoder saved to {encoder_filename}")
        
    #     joblib.dump(self.X_train_df, features_filename, compress=3)  # Save the features to a file
    #     print(f"Features saved to {features_filename}")

    # def evaluate_all_models(self):
    #     # self.evaluate_model(self.lr_model)
    #     self.evaluate_model(self.rf_model)

    # def evaluate_model(self, model):
    #     # Predict labels using the model
    #     y_pred = model.predict(self.X_test)
        
    #     # Calculate evaluation metrics
    #     accuracy = accuracy_score(self.y_test, y_pred)  # Calculate accuracy
    #     precision = precision_score(self.y_test, y_pred, average='macro')  # Calculate precision using macro averaging
    #     recall = recall_score(self.y_test, y_pred, average='macro')  # Calculate recall using macro averaging
    #     f1 = f1_score(self.y_test, y_pred, average='macro')  # Calculate F1-score using macro averaging

    #     # Print evaluation results
    #     print(f"Model: {model.__class__.__name__}")
    #     print(f"Accuracy: {accuracy}")
    #     print(f"Precision: {precision}")
    #     print(f"Recall (R-score): {recall}")
    #     print(f"F1-score: {f1}")

    #     print("Classfication Report:\n", classification_report(self.y_test, y_pred, target_names=self.label_encoder.classes_))
            
    #     conf_mat = confusion_matrix(self.y_test, y_pred)
    #     plt.figure(figsize=(12, 8))
    #     sns.heatmap(conf_mat, annot=True, fmt="d", xticklabels=self.label_encoder.classes_, yticklabels=self.label_encoder.classes_)
    #     plt.title("Confusion Matrix")
    #     plt.ylabel("Actual")
    #     plt.xlabel("Predicted")
    #     plt.savefig('../data/visualization/confusion_matrix.png')

    #     # Compute normalized confusion matrix
    #     normalized_conf_mat = conf_mat / conf_mat.sum(axis=1, keepdims=True)

    #     # Plot normalized confusion matrix
    #     plt.figure(figsize=(12, 8))
    #     sns.heatmap(normalized_conf_mat, annot=True, fmt=".2f", xticklabels=self.label_encoder.classes_, yticklabels=self.label_encoder.classes_)
    #     plt.title("Normalized Confusion Matrix")
    #     plt.ylabel("Actual")
    #     plt.xlabel("Predicted")
    #     plt.savefig('../data/visualization/normalized_confusion_matrix.png')


    #     # Plot feature importance

    #     importances = model.feature_importances_
    #     features = self.X_train_df.columns

    #     feature_importance_df = pd.DataFrame({'feature': features, 'importance': importances})
    #     feature_importance_df = feature_importance_df.sort_values('importance', ascending=False)

    #     plt.figure(figsize=(12,8))
    #     sns.barplot(x='importance', y='feature', data=feature_importance_df)
    #     plt.title('Feature Importance')
    #     plt.savefig('../data/visualization/feature_importance.png')


    #     # Evaluate on training data
    #     y_train_pred = model.predict(self.X_train)
    #     train_accuracy = accuracy_score(self.y_train, y_train_pred)
    #     train_precision = precision_score(self.y_train, y_train_pred, average='macro')
    #     train_recall = recall_score(self.y_train, y_train_pred, average='macro')
    #     train_f1 = f1_score(self.y_train, y_train_pred, average='macro')

    #     print(f"Training Accuracy: {train_accuracy}")
    #     print(f"Training Precision: {train_precision}")
    #     print(f"Training Recall: {train_recall}")
    #     print(f"Training F1-score: {train_f1}")

    #     # Cross-Validation
    #     cv_scores = cross_val_score(model, self.X_train, self.y_train, cv=5, scoring='accuracy')
    #     print(f"Cross-Validation Scores: {cv_scores}")
    #     print(f"Mean Cross-Validation Score: {cv_scores.mean()}")


    def load_model(model_choice=1):
        model_filenames = {
            # 0: 'data/models/GenreClassModel/lr_model.joblib',  # Filename for logistic regression model
            1: '../data/models/GenreClassModel/xgboost_model.joblib',  # Filename for random forest model
        }
        # Access these from bash script
        scaler_filename = '../data/models/GenreClassModel/scaler.joblib'  # Filename for scaler
        encoder_filename = '../data/models/GenreClassModel/label_encoder.joblib'  # Filename for label encoder
        features_filename = '../data/models/GenreClassModel/feature_set.joblib'  # Filename for features
        if model_choice not in model_filenames:
            raise Exception(f"Invalid model choice. Available choices are: {list(model_filenames.keys())}")

        model_filename = model_filenames[model_choice]
        xgboost_model = joblib.load(model_filename)  # Load the selected model
        #print(f"Model loaded from {model_filename}.")
        xgboost_model.verbose = 0

        standard_scaler = joblib.load(scaler_filename)  # Load the scaler
        #print(f"Scaler loaded from {scaler_filename}.")

        label_encoder_final = joblib.load(encoder_filename)  # Load the label encoder
        #print(f"Encoder loaded from {encoder_filename}.")

        feature_set = joblib.load(features_filename)  # Load the features
        #print(f"Features loaded from {features_filename}.")


        return {
            'model': xgboost_model,
            'scaler': standard_scaler,
            'label_encoder': label_encoder_final,
            'feature_set': feature_set,
        }


# # # IF RETRAINING NECESSARY
classifier = GenreClassifier()
items = classifier.load_model()
if items:
    print("Successfully loaded model.")




# classifier.preprocess_data()
# classifier.train_test_split()
# # classifier.tune_hyperparameters()
# classifier.train_save_model()
# classifier.evaluate_all_models()


# print(classifier.data['track_genre'].value_counts())