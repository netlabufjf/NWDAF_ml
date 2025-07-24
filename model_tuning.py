import numpy as np
import pandas as pd
from sklearn.metrics import make_scorer, f1_score
from sklearn.model_selection import RepeatedStratifiedKFold,cross_val_score,StratifiedKFold
from scipy.optimize import differential_evolution
from util import read_csv,glob_get_files_list

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier,RandomForestClassifier,AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import LinearSVC
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier

# File paths
working_folder = "./pcap/output/4-ML/"
input_files_path = working_folder + "preprocess/labeled_data/" # read CSV files from here

def hyperparam_tuning_DE(params, params_names, estimator, X_train, y_train):
    model_name = estimator.__class__.__name__ 
    params_dict = {params_names[i]:params[i] for i in range(len(params))}

    try:
        match model_name:
            case "LogisticRegression":
                penalty = ['l1', 'l2', 'elasticnet', None]
                solver = ['lbfgs', 'newton-cg', 'newton-cholesky', 'sag', 'saga']

                params_dict["penalty"] = penalty[int(params_dict["penalty"])]
                params_dict["solver"] = solver[int(params_dict["solver"])]

                params_dict["max_iter"] = int(params_dict["max_iter"]) # cast param to int type

            case "LinearSVC":
                penalty = ['l1', 'l2']
                loss = ['hinge', 'squared_hinge']
                
                params_dict["penalty"] = penalty[int(params_dict["penalty"])]
                params_dict["loss"] = loss[int(params_dict["loss"])]

                params_dict["max_iter"] = int(params_dict["max_iter"]) # cast param to int type
            
            case "HistGradientBoostingClassifier":
                params_dict["max_iter"] = int(params_dict["max_iter"]) # cast param to int type
                params_dict["max_leaf_nodes"] = int(params_dict["max_leaf_nodes"]) # cast param to int type
                params_dict["max_depth"] = int(params_dict["max_depth"]) # cast param to int type
                params_dict["min_samples_leaf"] = int(params_dict["min_samples_leaf"]) # cast param to int type
                params_dict["max_bins"] = int(params_dict["max_bins"]) # cast param to int type

            case "RandomForestClassifier":
                criterion = ["gini", "entropy", "log_loss"]
                max_features = ["sqrt", "log2", None]

                params_dict["criterion"] = criterion[int(params_dict["criterion"])]
                params_dict["max_features"] = max_features[int(params_dict["max_features"])]

                params_dict["n_estimators"] = int(params_dict["n_estimators"]) # cast param to int type
                params_dict["max_depth"] = int(params_dict["max_depth"]) # cast param to int type
                params_dict["min_samples_split"] = int(params_dict["min_samples_split"]) # cast param to int type
                params_dict["min_samples_leaf"] = int(params_dict["min_samples_leaf"]) # cast param to int type
                params_dict["max_leaf_nodes"] = int(params_dict["max_leaf_nodes"]) # cast param to int type

            case "DecisionTreeClassifier":
                criterion = ["gini", "entropy", "log_loss"]
                splitter = ["best", "random"]
                max_features = ["sqrt", "log2", None]

                params_dict["criterion"] = criterion[int(params_dict["criterion"])]
                params_dict["splitter"] = splitter[int(params_dict["splitter"])]
                params_dict["max_features"] = max_features[int(params_dict["max_features"])]

                params_dict["max_depth"] = int(params_dict["max_depth"]) # cast param to int type
                params_dict["min_samples_split"] = int(params_dict["min_samples_split"]) # cast param to int type
                params_dict["min_samples_leaf"] = int(params_dict["min_samples_leaf"]) # cast param to int type
                params_dict["max_leaf_nodes"] = int(params_dict["max_leaf_nodes"]) # cast param to int type

            case "MLPClassifier":
                hidden_layer_sizes = ["(100,)", "(100, 50, 25)", "(100, 100, 50)"]
                activation = ["identity", "logistic", "tanh", "relu"]
                solver = ["lbfgs", "sgd", "adam"]

                params_dict["hidden_layer_sizes"] = hidden_layer_sizes[int(params_dict["hidden_layer_sizes"])]
                params_dict["activation"] = activation[int(params_dict["activation"])]
                params_dict["solver"] = solver[int(params_dict["solver"])]

                params_dict["max_iter"] = int(params_dict["max_iter"]) # cast param to int type

            case "LGBMClassifier":
                params_dict["num_leaves"] = int(params_dict["num_leaves"]) # cast param to int type
                params_dict["max_depth"] = int(params_dict["max_depth"]) # cast param to int type
                params_dict["n_estimators"] = int(params_dict["n_estimators"]) # cast param to int type
                params_dict["subsample_for_bin"] = int(params_dict["subsample_for_bin"]) # cast param to int type
                params_dict["min_child_samples"] = int(params_dict["min_child_samples"]) # cast param to int type

            case "XGBClassifier":
                params_dict["eta"] = int(params_dict["eta"]) # cast param to int type
                params_dict["max_depth"] = int(params_dict["max_depth"]) # cast param to int type
                params_dict["min_child_weight"] = int(params_dict["min_child_weight"]) # cast param to int type
                params_dict["max_delta_step"] = int(params_dict["max_delta_step"]) # cast param to int type
                params_dict["max_leaves"] = int(params_dict["max_leaves"]) # cast param to int type
                params_dict["max_bin"] = int(params_dict["max_bin"]) # cast param to int type

            case "AdaBoostClassifier":
                params_dict["n_estimators"] = int(params_dict["n_estimators"]) # cast param to int type

            case _:
                print("[ERRO] Failed to load the model")
                exit()

        print("Params:", params_dict)

        estimator.set_params(**params_dict)

        # cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
        cv = StratifiedKFold(n_splits=3)

        cv_score = -1 * np.mean(cross_val_score(estimator, X_train, y_train, cv=cv, scoring=make_scorer(f1_score, average='weighted')))

    except Exception as e:
        # print(e)
        cv_score = 0

    print(cv_score)

    return cv_score

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
        case 'AdaBoost':
            clf = AdaBoostClassifier()

    return clf

def run_model_tuning(clf, X, y):
    model_name = clf.__class__.__name__
    print("Running for", model_name)

    # Mapping of model names to their parameters and integrality
    models = {
        "LogisticRegression": (lr_params, lr_integrality),
        "LinearSVC": (svc_params, svc_integrality),
        "HistGradientBoostingClassifier": (hgb_params, hgb_integrality),
        "RandomForestClassifier": (rf_params, rf_integrality),
        "DecisionTreeClassifier": (dt_params, dt_integrality),
        "MLPClassifier": (mlp_params, mlp_integrality),
        "LGBMClassifier": (lgbm_params, lgbm_integrality),
        "XGBClassifier": (xgb_params, xgb_integrality),
        "AdaBoostClassifier": (adaboost_params, adaboost_integrality)
    }

    # Get the parameters and integrality for the specified model
    if model_name in models:
        params, integrality = models[model_name]
        result = differential_evolution(hyperparam_tuning_DE, list(list(params.values())), args=(list(params.keys()), clf, X, y), maxiter=4, popsize=4, tol=0.01, workers=10, integrality=integrality, disp=True, updating='deferred')
        print("Dict:", result)
        print("Best params:", result.x)
    else:
        print(f"[ERRO] Model {model_name} not found.")

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
            else:
                raise ValueError(f"[ERRO] Could not determine data set type from filename {file}")
                exit()
    else: # or a smaller portion of it (useful for testing the implementation)
        training_data = generate_smaller_dataframe(csv_file_list, dataset_percentage)

    # Prepare data for supervised learning
    X = training_data.drop('label', axis=1)  # Features
    y = training_data['label']  # Target variable

    print("[DEBU] Split data")
    print("[DEBU] Class distrib.:", y.value_counts()) # summarize class distribution
    print("[DEBU] Class distrib. (%):\n", y.value_counts(dropna=False, normalize=True)) # summarize class distribution
    print("[DEBU] Total no. training samples:", len(y))
    # exit()

    if (split):
        # Now X and y are ready for supervised learning
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        return X_train, X_test, y_train, y_test
    else:
        return X, y

# Parameters to be tested
# Logistic Regression
lr_integrality = [0, 1, 1, 1]
lr_params = {
             'C': [0.01, 100.0], 
             'penalty': [0, 3],
             'solver': [0, 4],
             'max_iter': [100, 1000]
            }
# For more LR parameters check: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html

# Linear Support Vector Machine
svc_integrality = [0, 1, 1, 0, 1]
svc_params = {
              'C': [0.01, 100.0], 
              'penalty': [0, 1],
              'loss': [0, 1],
              'intercept_scaling': [1.0, 2.0],
              'max_iter': [1000, 5000]
             }
# For more LinearSVC parameters check: https://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html

# Histogram-based Gradient Boosting Classification Tree
hgb_integrality = [0, 1, 1, 1, 1, 0, 0, 1]
hgb_params = {
              'learning_rate': [0.01, 1.0], 
              'max_iter': [100, 1000],
              'max_leaf_nodes': [1, 100],
              'max_depth': [3, 50],
              'min_samples_leaf': [10, 100],
              'l2_regularization': [0.0, 1.0],
              'max_features': [1.0, 10.0],
              'max_bins': [100, 1000]
             }
# For more LinearSVC parameters check: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingClassifier.html

# Random Forest
rf_integrality = [1, 1, 1, 1, 1, 1, 1, 0]
rf_params = {
             'n_estimators': [50, 1000],
             'criterion': [0, 2],
             'max_depth': [3, 20],
             'min_samples_split': [1000, 100000],
             'min_samples_leaf': [1000, 100000],
             'max_features': [0, 2],
             'max_leaf_nodes': [1, 50],
             'min_impurity_decrease': [0.0, 0.8],
            }
# For more RandomForest parameters check: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html

# Decision Tree
dt_integrality = [1, 1, 1, 1, 1, 1, 0, 0]
dt_params = {
             'criterion': [0, 2],
             'splitter': [0, 1],
             'max_depth': [3, 20],
             'min_samples_split': [1000, 100000],
             'min_samples_leaf': [1000, 100000],
             'max_features': [0, 2],
             'max_leaf_nodes': [1, 50],
             'min_impurity_decrease': [0.0, 0.8],
             'ccp_alpha': [0.0, 1.0]
            }
# For more DecisionTreeClassifier parameters check: https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html

# Multilayer Perceptron
mlp_integrality = [1, 1, 1, 0, 0, 1, 0]
mlp_params = {
              'hidden_layer_sizes': [0, 2],
              'activation': [0, 3],
              'solver': [0, 2],
              'alpha': [0.0001, 10.0],
              'learning_rate_init': [0.001, 0.1],
              'max_iter': [200, 1000],
              'tol': [0.0001, 0.01]
              }
# For more MLPClassifier parameters check: https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html

# Light GBM
lgbm_integrality = [1, 1, 0, 1, 1, 0, 0, 1, 0, 0]
lgbm_params = {
               'num_leaves': [20, 100],
               'max_depth': [-1, 10],
               'learning_rate': [0.01, 1.0],
               'n_estimators': [50, 200],
               'subsample_for_bin': [100000, 300000],
               'min_split_gain': [0.01, 0.8],
               'min_child_weight': [0.001, 0.1],
               'min_child_samples': [1000, 10000],
               'subsample': [0.5, 1.0],
               'colsample_bytree': [0.5, 1.0]
              }
# For more LGBMClassifier parameters check: https://lightgbm.readthedocs.io/en/stable/pythonapi/lightgbm.LGBMClassifier.html

# eXtreme Gradient Boosting
xgb_integrality = [0, 0, 1, 1, 1, 0, 0, 0, 1, 1]
xgb_params = {
              'eta': [0.0, 1.0],
              'gamma': [0.0, 1.0],
              'max_depth': [5, 20],
              'min_child_weight': [1, 10000],
              'max_delta_step': [0, 10],
              'subsample': [0.5, 1.0],
              'lambda': [0.0, 2.0],
              'alpha': [0.0, 2.0],
              'max_leaves': [0, 100],
              'max_bin': [128, 512]
             }
# For more XGBClassifier parameters check: https://xgboost.readthedocs.io/en/stable/parameter.html

# AdaBoost
adaboost_integrality = [1, 0]
adaboost_params = {
                   'n_estimators': [10, 1000],
                   'learning_rate': [0.0, 5.0],
                  }
# For more AdaBoost parameters check: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostClassifier.html

model_names_list = ['LR', 'DT', 'RF', 'MLP', 'SVM', 'HGB', 'LightGBM', 'XGB', 'AdaBoost']

# Buid the CSV files list
csv_files = glob_get_files_list(input_files_path, "csv")

X, y = read_and_split_train_data(csv_files, split=False, dataset_percentage=100) # prepare data splits to tuning

# Run the tuning for all models in the list
for i in model_names_list:
        clf = classifier_select(i)
        run_model_tuning(clf, X, y)
