import os
import pandas as pd
import pickle
from numpy import mean,std
from datetime import datetime
from time import time_ns
from sklearn.preprocessing import MinMaxScaler,OrdinalEncoder
from sklearn.model_selection import train_test_split,cross_val_score,RepeatedStratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier,RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import LinearSVC
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (accuracy_score,
                            precision_score,
                            recall_score,
                            f1_score,
                            roc_auc_score,
                            confusion_matrix)

from util import (glob_get_files_list,
                  read_csv,
                  delete_files,
                  plot_confusion_matrix,
                  preprocess_data,
                  read_and_label_data,
                  data_augmentation)

# File paths
working_folder = "./pcap/output/4-ML/"
input_files_path = working_folder + "preprocess/labeled_files/" # read CSV files from here
output_files_path_preprocessed_data = working_folder + "preprocess/data_ready_to_ml/" # save preprocessed data there
output_files_path_labeled_data = working_folder + "preprocess/labeled_data/" # save the labeled output files there
output_files_path_models = working_folder + "models/" # save the model files there
output_files_path_results = output_files_path_models + "training_results/" # save the model files there

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

def classifier_select(classifier_acronym):
    match classifier_acronym:
        case 'LR':
            clf = LogisticRegression()
        case 'DT':
            clf = DecisionTreeClassifier()
        case 'RF':
            clf = RandomForestClassifier()
        case 'MLP':
            clf = MLPClassifier()
        case 'SVM':
            clf = LinearSVC()
        case 'HGB':
            clf = HistGradientBoostingClassifier()
        case 'LightGBM':
            clf = LGBMClassifier(verbose=-1)
        case 'XGB':
            clf = XGBClassifier()
        case _:
            print("[ERRO] Failed to load the model")
            exit()

    return clf

def save_model_locally(model, file_name, out_dir):
    file_path = out_dir + file_name + ".pkl"
    pickle.dump(model, open(file_path, 'wb'))
    model_name = model.__class__.__name__
    print(f"[INFO] Model {model_name} sucessfully saved on {file_path}")

# Load and prepare splits from labeled training data
def read_and_split_train_data(csv_file_list, split):
    training_data = pd.DataFrame()
    for file in csv_file_list:
        if 'training' in file:
            df = read_csv(file)
            training_data = pd.concat([training_data, df], ignore_index=True)
        elif 'inference' in file:
            # print("[DEBU] Skipped inference file found at", file) # DEBUG
            pass
        else:
            raise ValueError(f"[ERRO] Could not determine data set type from filename {file}")
            exit()

    # Prepare data for supervised learning
    X = training_data.drop('label', axis=1)  # Features
    y = training_data['label']  # Target variable

    if (split):
        # Now X and y are ready for supervised learning
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        return X_train, X_test, y_train, y_test
    else:
        return X, y
    
def train_models(model, X_train, X_test, y_train, y_test):
    model_name = model.__class__.__name__
    data_num_rows = len(X_train)

    print("[INFO] Training model", model_name)
    training_time_begin = time_ns()
    model.fit(X_train, y_train)
    training_time_end = time_ns()

    training_disk_time_begin = time_ns()
    save_model_locally(model, model_name, output_files_path_models)
    training_disk_time_end = time_ns()

    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2])
    plot_confusion_matrix(cm, output_files_path_results, "", model_name, "training", timestamp, True, False)

    # Model evaluation data
    accuracy = accuracy_score(y_test, y_pred)
    precision_avg = precision_score(y_test, y_pred, average="weighted")
    recall_avg = recall_score(y_test, y_pred, average="weighted")
    f_score_avg = f1_score(y_test, y_pred, average="weighted")
    f_score_class0 = f1_score(y_test, y_pred, average=None, labels=[0])[0]
    f_score_class1 = f1_score(y_test, y_pred, average=None, labels=[1])[0]
    f_score_class2 = f1_score(y_test, y_pred, average=None, labels=[2])[0]

    # print("[DEBU] Accuracy:", round(accuracy, 10))
    # print(f"[DEBU] Confusion Matrix:\n{cm}")
    # print("[DEBU] Precision :", round(precision_avg, 10))
    # print("[DEBU] Recall    :", round(recall_avg, 10))
    # print("[DEBU] F1-score  :", round(f_score_avg, 10))
    # print("[DEBU] F1-score/class :", f1_score(y_test, y_pred, average=None, labels=[0, 1, 2]))
    if (model_name != "LinearSVC"): # LinearSVC doesn't implement proba
        auc_score = roc_auc_score(y_test, model.predict_proba(X_test), average='macro', multi_class='ovo', labels=[0, 1, 2])
        # print("[DEBU] ROC AUC Score :", round(auc_score, 10))
    else:
        # print("[DEBU] ROC AUC Score : Not calculated for", model_name)
        auc_score = "N.A."

    if (model_name == 'DecisionTreeClassifier'):
        # Record feature importance for Decision Tree
        importance_with_columns = pd.DataFrame({'feature': X_train.columns, 'importance': model.feature_importances_})
        importance_with_columns.sort_values(by='importance', ascending=False, inplace=True, ignore_index=True)
        importance_with_columns.to_csv(f"{output_files_path_results}{timestamp}_dt_feature_importance.csv", header=True)
    
    elif (model_name == 'RandomForestClassifier'):
        # Record feature importance for Random Forest
        importance_with_columns = pd.DataFrame({'feature': X_train.columns, 'importance': model.feature_importances_})
        importance_with_columns.sort_values(by='importance', ascending=False, inplace=True, ignore_index=True)
        importance_with_columns.to_csv(f"{output_files_path_results}{timestamp}_rf_feature_importance.csv", header=True)

    training_time_ms = (training_time_end - training_time_begin) / 10**6
    training_disk_time_ms = (training_disk_time_end - training_disk_time_begin) / 10**6
    training_total_time_ms = training_time_ms + training_disk_time_ms

    new_row = {
            columns_training_results_df[0]: model_name,
            columns_training_results_df[1]: data_num_rows,
            columns_training_results_df[2]: accuracy,
            columns_training_results_df[3]: precision_avg,
            columns_training_results_df[4]: recall_avg,
            columns_training_results_df[5]: f_score_avg,
            columns_training_results_df[6]: f_score_class0,
            columns_training_results_df[7]: f_score_class1,
            columns_training_results_df[8]: f_score_class2,
            columns_training_results_df[9]: auc_score,
            columns_training_results_df[10]: training_time_ms,
            columns_training_results_df[11]: training_disk_time_ms,
            columns_training_results_df[12]: training_total_time_ms,
        }
    
    # Add new row to the dataframe using loc[] method
    training_results_df.loc[len(training_results_df)] = new_row

    training_results_df.to_csv(f"{output_files_path_results}{timestamp}_training_results.csv", index=False)
    print(f"[INFO] {model_name} training finished")

# Buid the CSV files list
csv_files = glob_get_files_list(input_files_path, "csv")

# Preprocess the data
preprocess_data(csv_files, output_files_path_preprocessed_data, output_files_path_results, timestamp)

# Update the list of CSV files
csv_files = glob_get_files_list(output_files_path_preprocessed_data, "csv")

# Label all data inside CSV files
[read_and_label_data(file, output_files_path_labeled_data, False) for file in csv_files]

# Update the list of CSV files
csv_files = glob_get_files_list(output_files_path_labeled_data, "csv")

# Prepare data splits to train the models
print("[INFO] Preparing training data splits ... ", end='')
X_train, X_test, y_train, y_test = read_and_split_train_data(csv_files, split=True)
print("[ OK ]")

# Apply some data augmentation
# print("[INFO] Applying SMOTE to training data ... ", end='')
# Disabled due to the extra processing time it adds to the whole process
# X_train_smote, y_train_smote = data_augmentation(X_train, y_train)
# print("[ OK ]")
# print("[DEBU] Data before SMOTE")
# print("[DEBU]", len(y_train))
# print("[DEBU] Data after SMOTE")
# print("[DEBU]", len(y_train_smote))
# del X_train, y_train

# Cross validation steps
#cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=42)

model_names_list = ['LR', 'DT', 'RF', 'MLP', 'SVM', 'HGB', 'LightGBM', 'XGB']

columns_training_results_df = ["model_name", "data_num_rows", "accuracy", "precision_avg", "recall_avg", 
                            "f1_score_avg", "f1_score_class0", "f1_score_class1", "f1_score_class2",
                            "auc_score_avg", "training_time_ms", "training_disk_time_ms", "training_total_time_ms"]
training_results_df = pd.DataFrame(columns=columns_training_results_df) # df to save the training results

# Execute the actual model training
for i in model_names_list:
    clf = classifier_select(i)

    train_models(clf, X_train, X_test, y_train, y_test)
