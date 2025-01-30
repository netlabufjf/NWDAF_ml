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
                            auc,
                            confusion_matrix)

from util import glob_get_files_list,read_csv,delete_files

# File paths
working_folder = "./pcap/output/4-ML/"
input_files_path = working_folder + "preprocess/labeled_files/" # read CSV files from here
output_files_path_preprocessed_data = working_folder + "preprocess/data_ready_to_ml/" # save preprocessed data there
output_files_path_labeled_data = working_folder + "preprocess/labeled_data/" # save the labeled output files there
output_files_path_models = working_folder + "models/" # save the model files there
output_files_path_results = output_files_path_models + "training_results/" # save the model files there

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

def save_model_locally(model, file_name, out_dir):
    file_path = out_dir + file_name + ".pkl"
    pickle.dump(model, open(file_path, 'wb'))
    model_name = model.__class__.__name__
    print(f"[INFO] Model {model_name} sucessfully saved on {file_path}")

# Function to read and label data in CSV files
def read_and_label_data(file_path, out_dir, remove_old_files=False):
    # Read the CSV file
    file_name_without_path = file_path.split('/')[-1] # get old file name
    new_file_name_and_path = out_dir + os.path.splitext(file_name_without_path)[0] + "_labeled.csv"
    if not os.path.exists(new_file_name_and_path):
        df = pd.read_csv(file_path)
        
        # Assign labels based on filenames
        if 'embb' in file_path:
            label = 0
        elif 'urllc' in file_path:
            label = 1
        elif 'mmtc' in file_path:
            label = 2
        else:
            raise ValueError(f"Could not determine label from filename {file_path}")
            exit()
        
        
        # Add label to DataFrame
        print(f"[INFO] Labeling {file_name_without_path} ... ", end='')
        df['label'] = label
        df.to_csv(new_file_name_and_path, index=False)
        print("[ OK ]")

        # if storage space is constrained, update remove_old_files to True to free some space
        if (remove_old_files):
            delete_files(file_name_without_path, file_path)
        
        print("[DEBU] Labeled data successfully saved to", new_file_name_and_path) # DEBUG
    else:
        print(f"[INFO] The file {file_name_without_path} was already labeled")

    
def preprocess_data(files_path, output_dir):
    columns_preprocess_time_df = ["file_name", "file_num_rows", "preprocess_time_ms", "preprocess_disk_time_ms", "preprocess_total_time_ms"]
    preprocess_time_df = pd.DataFrame(columns=columns_preprocess_time_df) # df to save the results

    for i in files_path:
        file_name = i.split('/')[-1]
        out_file_path = output_dir + file_name
        preprocess_time_begin = time_ns()

        if not os.path.exists(out_file_path):
            df = read_csv(i)
            data_num_rows = len(df)
            print("[INFO] Working with", file_name)

            # Drop some data
            # df = df.dropna(axis=1, how='all') # drop columns where all values are None
            # NOTE doing so was creating an inconsistent number of available features
            # which was expected, but most models I've tested can't handle this
            df.drop(columns=["Source_IP", "Destination_IP"], axis=1, inplace=True) # drop IP addresses to avoid using them in the models
            df.drop(columns=["Packet_no"], axis=1, inplace=True) # drop packet number to avoid using it in the models
            
            # Encode the categorical features
            feature_encoder = OrdinalEncoder()
            for col in df.columns:
                if col == "TCP_compl_str" or col == "TCP_flags_str" or col == "Frame_protocols":
                    df[col] = feature_encoder.fit_transform(df[[col]])
            
            # Change None (NaN type) to an int
            df.fillna(-1, inplace=True) # required by models like LR that can't handle NaN data
            # NOTE -1 is a valid int while not representing valid data (which starts with 0)
            # df.dropna(inplace=True) # not required for now (see "fillna line" above)

            # Normalize features using standardization
            # using MinMax to avoid giving more importance to a given feature
            # for more information: https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html
            scaler = MinMaxScaler() 
            data_features_names = list(df)
            scaler.fit(df[data_features_names])
            df[data_features_names] = scaler.transform(df[data_features_names])
            preprocess_time_end = time_ns()

            # Save the normalized data
            preprocess_disk_time_begin = time_ns()
            df.to_csv(out_file_path, index=False)
            preprocess_disk_time_end = time_ns()
            print("[INFO] Preprocessed data saved to:", out_file_path)
            
            preprocess_disk_time_ms = (preprocess_disk_time_end - preprocess_disk_time_begin) / 10**6
            preprocess_time_ms = (preprocess_time_end - preprocess_time_begin) / 10**6
            preprocess_total_time_ms = (preprocess_time_ms + preprocess_disk_time_ms)

            new_row = {
                    columns_preprocess_time_df[0]: file_name,
                    columns_preprocess_time_df[1]: data_num_rows,
                    columns_preprocess_time_df[2]: preprocess_time_ms,
                    columns_preprocess_time_df[3]: preprocess_disk_time_ms,
                    columns_preprocess_time_df[4]: preprocess_total_time_ms,
                }
                
            # Add new row to the dataframe using loc[] method
            preprocess_time_df.loc[len(preprocess_time_df)] = new_row
        else:
            print(f"[INFO] The file {file_name} was already preprocessed")

    if len(preprocess_time_df) != 0:
        preprocess_time_df.to_csv(f"{output_files_path_results}{timestamp}_preprocess_time.csv", index=False)

def train_models(model):
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
    cm = confusion_matrix(y_test, y_pred)
    print("[INFO] Accuracy:", round(accuracy_score(y_test, y_pred), 10)) # TODO calculate more metrics for all models
    print(f"[DEBU] Confusion Matrix:\n{cm}") # TODO plot and save this matrix

    if (model_name == 'DecisionTreeClassifier'):
        print("[INFO] Precision :", round(precision_score(y_test, y_pred, average="weighted"), 10))
        print("[INFO] Recall    :", round(recall_score(y_test, y_pred, average="weighted"), 10))
        print("[INFO]F1-score  :", round(f1_score(y_test, y_pred, average="weighted"), 10))
        # print("[INFO] F1-score/class :", f1_score(y_test, y_pred, average=None, labels=TODO)) # TODO finish this

        # Record feature importance for Decision Tree
        importance_with_columns = pd.DataFrame({'feature': X_train.columns, 'importance': model.feature_importances_})
        importance_with_columns.sort_values(by='importance', ascending=False, inplace=True, ignore_index=True)
        importance_with_columns.to_csv("dt_feature_importance.csv", header=True)
    
    elif (model_name == 'RandomForestClassifier'):
        # Record feature importance for Random Forest
        importance_with_columns = pd.DataFrame({'feature': X_train.columns, 'importance': model.feature_importances_})
        importance_with_columns.sort_values(by='importance', ascending=False, inplace=True, ignore_index=True)
        importance_with_columns.to_csv("rf_feature_importance.csv", header=True)

    training_time_ms = (training_time_end - training_time_begin) / 10**6
    training_disk_time_ms = (training_disk_time_end - training_disk_time_begin) / 10**6
    training_total_time_ms = training_time_ms + training_disk_time_ms

    new_row = {
            columns_training_time_df[0]: model_name,
            columns_training_time_df[1]: data_num_rows,
            columns_training_time_df[2]: training_time_ms,
            columns_training_time_df[3]: training_disk_time_ms,
            columns_training_time_df[4]: training_total_time_ms,
        }
    
    # Add new row to the dataframe using loc[] method
    training_time_df.loc[len(training_time_df)] = new_row

    training_time_df.to_csv(f"{output_files_path_results}{timestamp}_training_time.csv", index=False)

# Buid the CSV files list
csv_files = glob_get_files_list(input_files_path, "csv")

# Preprocess the data
preprocess_data(csv_files, output_files_path_preprocessed_data)

# Update the list of CSV files
csv_files = glob_get_files_list(output_files_path_preprocessed_data, "csv")

# Label all data inside CSV files
[read_and_label_data(file, output_files_path_labeled_data, False) for file in csv_files]

# Update the list of CSV files
csv_files = glob_get_files_list(output_files_path_labeled_data, "csv")

# Load labeled training data
training_data = pd.DataFrame()
for file in csv_files:
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

# Now X and y are ready for supervised learning
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Cross validation steps
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=42)

model_names_list = ['LR', 'DT', 'RF', 'MLP', 'SVM', 'HGB', 'LightGBM', 'XGB']

columns_training_time_df = ["model_name", "data_num_rows", "training_time_ms", "training_disk_time_ms", "training_total_time_ms"]
training_time_df = pd.DataFrame(columns=columns_training_time_df) # df to save the results

for i in model_names_list:
    match i:
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

    train_models(clf)
