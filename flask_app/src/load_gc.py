import joblib

def load_model():
    model_filename = '../data/models/GenreClassModel/xgboost_model.joblib'  # Filename for xg_boost
    scaler_filename = '../data/models/GenreClassModel/scaler.joblib'  # Filename for scaler
    encoder_filename = '../data/models/GenreClassModel/label_encoder.joblib'  # Filename for label encoder
    features_filename = '../data/models/GenreClassModel/feature_set.joblib'  # Filename for features
    xgboost_model = joblib.load(model_filename)  # Load the selected model
    xgboost_model.verbose = 0
    standard_scaler = joblib.load(scaler_filename)  # Load the scaler
    label_encoder_final = joblib.load(encoder_filename)  # Load the label encoder
    feature_set = joblib.load(features_filename)  # Load the features
    class_items =  {
        'model': xgboost_model,
        'scaler': standard_scaler,
        'label_encoder': label_encoder_final,
        'feature_set': feature_set,
    }
    return class_items