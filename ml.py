import os
import pandas as pd
import pickle
import csv
from numpy import mean,std,linspace
from datetime import datetime
from time import time_ns
from sklearn.preprocessing import MinMaxScaler,OrdinalEncoder
from sklearn.model_selection import train_test_split,cross_val_score,RepeatedStratifiedKFold,cross_validate,GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier,RandomForestClassifier,AdaBoostClassifier,StackingClassifier,VotingClassifier
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
                            confusion_matrix,
                            make_scorer)

from util import (glob_get_files_list,
                  read_csv,
                  delete_files,
                  plot_confusion_matrix,
                  preprocess_data,
                  read_and_label_data,
                  data_oversample,
                  data_undersample,
                  generate_smaller_dataframe,
                  get_available_threads)

# File paths
working_folder = "./pcap/output/4-ML/"
input_files_path = working_folder + "preprocess/labeled_files/" # read CSV files from here
output_files_path_preprocessed_data = working_folder + "preprocess/data_ready_to_ml/" # save preprocessed data there
output_files_path_labeled_data = working_folder + "preprocess/labeled_data/" # save the labeled output files there
output_files_path_resampled_data = working_folder + "preprocess/resampled_data/" # save the labeled output files there
output_files_path_models = working_folder + "models/" # save the model files there
output_files_path_results = output_files_path_models + "training_results/" # save the model files there

# Control the execution of each function
run_model_training = True
run_cross_val = True #Cross validation
run_SMOTE = True # Oversampling
run_OSS = False # Undersampling

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
total_run_time_begin = datetime.now()

def classifier_select(classifier_acronym):
    match classifier_acronym:
        case 'LR':
            clf = LogisticRegression()
        case 'DT':
            clf = DecisionTreeClassifier(max_depth=3)
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
        case 'AdaBoost':
            clf = AdaBoostClassifier()
        case 'Stacking':
            estimators = [
            ('dt', DecisionTreeClassifier(max_depth=2)),
            ('svc', LinearSVC()),
            ('ada', AdaBoostClassifier())
            ]
            clf = StackingClassifier(estimators=estimators, final_estimator=LogisticRegression())
        case 'Voting':
            estimators = [
            ('dt', DecisionTreeClassifier(max_depth=3)),
            ('lr', LogisticRegression()),
            ('ada', AdaBoostClassifier())
            ]
            clf = VotingClassifier(estimators=estimators, voting='soft', weights=[0.1, 0.1, 0.8])
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
def read_and_split_train_data(csv_file_list, split, dataset_percentage=100):
    training_data = pd.DataFrame()
    if (dataset_percentage == 100): # use the whole dataset
        for file in csv_file_list:
            if 'training' in file:
                df = read_csv(file)
                training_data = pd.concat([training_data, df], ignore_index=True)
            elif 'inference' in file:
                # print("[DEBU] Skipped inference file found at", file) # DEBUG
                pass
            elif 'SMOTE' in file and len(csv_file_list) == 1:
                training_data = read_csv(csv_file_list[0])
            else:
                raise ValueError(f"[ERRO] Could not determine data set type from filename {file}")
                exit()
    else: # or a smaller portion of it (useful for testing the implementation)
        training_data = generate_smaller_dataframe(csv_file_list, dataset_percentage)

    # Prepare data for supervised learning
    X = training_data.drop('label', axis=1)  # Features
    y = training_data['label']  # Target variable

    # print("\n[DEBU] Split data")
    # print("[DEBU] Class distrib.:", y.value_counts()) # summarize class distribution
    # print("[DEBU] Class distrib. (%):\n", y.value_counts(dropna=False, normalize=True)) # summarize class distribution
    # print("[DEBU] Total no. training samples:", len(y))

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
    if (model_name != "LinearSVC" and model_name != "StackingClassifier"): # LinearSVC doesn't implement proba
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

def cross_val(clf, X, y):
    model_name = clf.__class__.__name__
    data_num_rows = len(X)
    print("[INFO] Running Cross Validation on", model_name)
    scoring = {'prec_macro': 'precision_macro',
            'rec_macro': make_scorer(recall_score, average='macro'),
            'f1-score_avg': make_scorer(f1_score, average='weighted'),
            # 'f1-score_class0': make_scorer(f1_score, average=None, labels=[0])[0]
            }
    cv_folds = 10 # reduce this number to reduce RAM usage during CV
    # 3 uses up to around 50GB, 10 uses up to around 128GB (except for LinearSVC that requires more)
    amount_of_cpus_to_use = 0.9 # e.g. if there are 16 CPUs available, 90% will be equals to 14
    
    # Run StratifiedKFold
    scores = cross_validate(clf, X, y, scoring=scoring, cv=cv_folds, return_train_score=True, n_jobs=get_available_threads(amount_of_cpus_to_use))

    s_fit_time_sec = scores['fit_time'] # time is in seconds for more information, see the URLs below
    s_score_time_sec = scores['score_time'] # time is in seconds for more information, see the URLs below
    # https://stackoverflow.com/questions/73548091/unit-for-fit-time-and-score-time-in-sklearn-cross-validate
    # https://github.com/scikit-learn/scikit-learn/blob/55a65a2fa5653257225d7e184da3d0c00ff852b1/sklearn/model_selection/_validation.py#L673
    s_train_precision = scores['train_prec_macro']
    s_train_recall = scores['train_rec_macro']
    s_train_f_score = scores['train_f1-score_avg']
    s_test_precision = scores['test_prec_macro']
    s_test_recall = scores['test_rec_macro']
    s_test_f_score = scores['test_f1-score_avg']

    # print("[DEBU] Fit time:", s_fit_time)
    # print("[DEBU] Score time:", s_score_time)
    # print("[DEBU] -Train-")
    # print("[DEBU] Precision:", s_train_precision)
    # print("[DEBU] Recall:", s_train_recall)
    # print("[DEBU] Average F1-Score:", s_train_f_score)
    # print("[DEBU] -Test-")
    # print("[DEBU] Precision:", s_test_precision)
    # print("[DEBU] Recall:", s_test_recall)
    # print("[DEBU] Average F1-Score:", s_test_f_score)

    avg_s_test_precision = mean(s_test_precision)
    avg_s_test_recall = mean(s_test_recall)
    avg_s_test_f_score = mean(s_test_f_score)
    cv_total_time_sec = s_fit_time_sec + s_score_time_sec

    new_row = {
            columns_cross_val_results_df[0]: model_name,
            columns_cross_val_results_df[1]: data_num_rows,
            columns_cross_val_results_df[2]: mean(s_train_precision),
            columns_cross_val_results_df[3]: mean(s_train_recall),
            columns_cross_val_results_df[4]: mean(s_train_f_score),
            columns_cross_val_results_df[5]: avg_s_test_precision,
            columns_cross_val_results_df[6]: avg_s_test_recall,
            columns_cross_val_results_df[7]: avg_s_test_f_score,
            columns_cross_val_results_df[8]: std(s_test_precision, mean=avg_s_test_precision), # reuse the mean to improve performance
            columns_cross_val_results_df[9]: std(s_test_recall, mean=avg_s_test_recall),       # see the URL below
            columns_cross_val_results_df[10]: std(s_test_f_score, mean=avg_s_test_f_score),    # https://numpy.org/doc/stable/reference/generated/numpy.std.html
            columns_cross_val_results_df[11]: mean(s_fit_time_sec),
            columns_cross_val_results_df[12]: mean(s_score_time_sec),
            columns_cross_val_results_df[13]: mean(cv_total_time_sec),
        }

    # Add new row to the dataframe using loc[] method
    cross_val_results_df.loc[len(cross_val_results_df)] = new_row

    cross_val_results_df.to_csv(f"{output_files_path_results}{timestamp}_cross_val_{cv_folds}_folds_results.csv", index=False)

    print(f"[INFO] {model_name} Cross Validation done")

# Buid the CSV files list
csv_files = glob_get_files_list(input_files_path, file_format="csv")

# Preprocess the data
preprocess_data(csv_files, output_files_path_preprocessed_data, output_files_path_results, timestamp, drop_protocols_and_ports=True)

# Update the list of CSV files
csv_files = glob_get_files_list(output_files_path_preprocessed_data, file_format="csv")

# Label all data inside CSV files
[read_and_label_data(file, output_files_path_labeled_data, False) for file in csv_files]

# Update the list of CSV files
csv_files = glob_get_files_list(output_files_path_labeled_data, file_format="csv")

# Prepare data splits to train the models
if (run_model_training or run_SMOTE or run_OSS):
    print("[INFO] Preparing training data splits ... ", end='', flush=True)
    if (run_OSS):
        data_amount = 1 # amount of data to be used in OSS
    else:
        data_amount = 100
    X_train, X_test, y_train, y_test = read_and_split_train_data(csv_files, split=True, dataset_percentage=data_amount)
    print("[ OK ]")

# Apply some data undersampling with OSS
if (run_OSS):
    # OSS parameters
    k = 1
    seed = 100

    print("[INFO] Applying OSS on training data ... ", end='', flush=True)
    OSS_run_time_begin = datetime.now()
    X_train_oss, y_train_oss = data_undersample(X_train, y_train, k, seed)
    print("[ OK ]")
    # print("[DEBU] Data before OSS")
    # print("[DEBU] Class distrib.:", y_train.value_counts()) # summarize class distribution
    # print("[DEBU] Class distrib. (%):\n", y_train.value_counts(dropna=False, normalize=True)) # summarize class distribution
    # print("[DEBU] Total no. training samples:", len(y_train))
    # print("[DEBU] Data after OSS")
    # print("[DEBU] Class distrib.:", y_train_oss.value_counts()) # summarize class distribution
    # print("[DEBU] Class distrib. (%):\n", y_train_oss.value_counts(dropna=False, normalize=True)) # summarize class distribution
    # print("[DEBU] Total no. training samples:", len(y_train_oss))
    
    # Save the undersampled dataset on disk
    undersampled_data = X_train_oss.join(y_train_oss)
    undersampled_data.to_csv(f"{output_files_path_resampled_data}{timestamp}_OSS_undersample_k_{k}_seed_{seed}.csv", header=True, index=False)
    
    # Use the undersampled data in the model training
    X_train = X_train_oss
    y_train = y_train_oss
    
    OSS_run_time_end = datetime.now()
    print(f"[INFO] Parameters: k = {k}, seed = {seed}")
    print("[INFO] OSS run time:", (OSS_run_time_end - OSS_run_time_begin).total_seconds(), "(seconds)")

# resampled_csv_files = glob_get_files_list(output_files_path_resampled_data, file_format="csv")
# TODO load the preprocessed files and use them to train the models

# Apply some data oversampling with SMOTE
if (run_SMOTE):
    # SMOTE parameters
    k = 5
    strategy = 'minority'
    # Update the list of CSV files
    smote_files_available = glob_get_files_list(output_files_path_resampled_data, file_name_pattern=f"{k}*{strategy}", file_format="csv")
    smote_files_available.sort()
    smote_file = smote_files_available[-1] # get the most recent file

    if smote_file:
        print(f"[INFO] File {smote_file} was found, skipping SMOTE")

        print("[INFO] Reading preprocessed SMOTE file ... ", end='', flush=True)
        X_train, X_test, y_train, y_test = read_and_split_train_data([str(smote_file)], split=True)
        print("[ OK ]")

    else:
        print("[INFO] Applying SMOTE on training data ... ", end='', flush=True)
        SMOTE_run_time_begin = datetime.now()
        X_train_smote, y_train_smote = data_oversample(X_train, y_train, strategy=strategy, k=k)
        print("[ OK ]")
        # print("[DEBU] Data before SMOTE")
        # print("[DEBU] Class distrib.:", y_train.value_counts()) # summarize class distribution
        # print("[DEBU] Class distrib. (%):\n", y_train.value_counts(dropna=False, normalize=True)) # summarize class distribution
        # print("[DEBU] Total no. training samples:", len(y_train))
        # print("[DEBU] Data after SMOTE")
        # print("[DEBU] Class distrib.:", y_train_smote.value_counts()) # summarize class distribution
        # print("[DEBU] Class distrib. (%):\n", y_train_smote.value_counts(dropna=False, normalize=True)) # summarize class distribution
        # print("[DEBU] Total no. training samples:", len(y_train_smote))
        X_train = X_train_smote
        y_train = y_train_smote

        # Save the oversampled dataset on disk
        oversampled_data = X_train_smote.join(y_train_smote)
        oversampled_data.to_csv(f"{output_files_path_resampled_data}{timestamp}_SMOTE_oversample_k_{k}_strategy_{strategy}.csv", header=True, index=False)

        SMOTE_run_time_end = datetime.now()
        print("[INFO] SMOTE run time:", (SMOTE_run_time_end - SMOTE_run_time_begin).total_seconds(), "(seconds)")

model_names_list = ['LR', 'DT', 'RF', 'MLP', 'SVM', 'HGB', 'LightGBM', 'XGB', 'AdaBoost', 'Stacking', 'Voting']

# Cross validation
if (run_cross_val):
    columns_cross_val_results_df = ["model_name", "data_num_rows", "train_precision_avg", "train_recall_avg",
                                "train_f1_score_avg", "test_precision_avg", "test_recall_avg", "test_f1_score_avg",
                                "test_precision_stdev", "test_recall_stdev", "test_f1_score_stdev",
                                "fit_time_sec_avg", "score_time_sec_avg", "total_cross_val_time_sec_avg"]
    cross_val_results_df = pd.DataFrame(columns=columns_cross_val_results_df) # df to save the CV results

    X, y = read_and_split_train_data(csv_files, split=False, dataset_percentage=100) # prepare data splits to cross val
    for i in model_names_list:
        clf = classifier_select(i)
        cross_val(clf, X, y)

# Model training
if (run_model_training):
    columns_training_results_df = ["model_name", "data_num_rows", "accuracy", "precision_avg", "recall_avg", 
                                "f1_score_avg", "f1_score_class0", "f1_score_class1", "f1_score_class2",
                                "auc_score_avg", "training_time_ms", "training_disk_time_ms", "training_total_time_ms"]
    training_results_df = pd.DataFrame(columns=columns_training_results_df) # df to save the training results
    # Execute the actual model training
    for i in model_names_list:
        clf = classifier_select(i)

        train_models(clf, X_train, X_test, y_train, y_test)

total_run_time_end = datetime.now()
print("[INFO] ML total run time:", (total_run_time_end - total_run_time_begin).total_seconds(), "(seconds)")
