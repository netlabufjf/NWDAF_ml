import numpy as np
import pickle

from sklearn import metrics
from util import read_csv

# File paths
working_folder = "./pcap/output/4-ML/"
models_folder = working_folder + "models/" # read the models from here
output_files_path_labeled_data = working_folder + "preprocess/labeled_data/" # read preprocessed data from here

models_file_list = [models_folder + "DecisionTreeClassifier.pkl", models_folder + "MLPClassifier.pkl"] # Use DT and MLP models
file_name = "udp-nc-traffic-1k_inference_mmtc_labeled.csv" # Using the mMTC probabilistic inference data in this example

# Load and prepare splits from labeled training data
df = read_csv(output_files_path_labeled_data + file_name)

# Prepare data for supervised learning
X = df.drop('label', axis=1)  # Features
y_true = df['label']  # Target variable

# Load models from disk
dt_model = pickle.load(open(models_file_list[0], 'rb'))
mlp_model = pickle.load(open(models_file_list[1], 'rb'))

# Classify data
y_pred_dt = dt_model.predict(X)
y_pred_mlp = mlp_model.predict(X)

#######################################################
# Calculating using the Python/Scikit Learn libraries #
#######################################################

# Confusion matrices
conf_matrix_dt = metrics.confusion_matrix(y_true, y_pred_dt, labels=[0,1,2])
conf_matrix_mlp = metrics.confusion_matrix(y_true, y_pred_mlp, labels=[0,1,2])

# Print matrices
print("=> Confusion matrices")
print("Decision Tree Confusion Matrix")
print(conf_matrix_dt)
print("Multilayer Perceptron Confusion Matrix")
print(conf_matrix_mlp)

# Print the performance metrics
print("=> Results using libraries")
print(metrics.classification_report(y_true, y_pred_dt, digits=8, zero_division=0.0, labels=[0,1,2]))
print(metrics.classification_report(y_true, y_pred_mlp, digits=8, zero_division=0.0, labels=[0,1,2]))

##########################
# Calculating 'manually' #
##########################

# Calculate model accuracy
def calculate_accuracy(conf_matrix):
    # True Positives and True Negatives
    TP = np.diag(conf_matrix).sum()  # Sum of diagonal elements (correct predictions)
    total = conf_matrix.sum()  # Total instances
    accuracy = TP / total if total > 0 else 0
    return accuracy

# Calculate model recall for a specific class (e.g., class 2 / mMTC)
def calculate_class_recall(conf_matrix, class_index):
    TP = conf_matrix[class_index, class_index]  # True Positives for the class
    FN = conf_matrix[:, class_index].sum() - TP  # False Negatives for the class
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    return recall

# Calculate model weighted recall
def calculate_weighted_recall(conf_matrix):
    total_instances = conf_matrix.sum()  # Total instances
    weighted_recall = 0.0
    
    for class_index in range(conf_matrix.shape[0]):
        TP = conf_matrix[class_index, class_index]  # True Positives for the class
        FN = conf_matrix[:, class_index].sum() - TP  # False Negatives for the class
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        
        # Count the number of instances for this class
        class_instances = conf_matrix[:, class_index].sum()
        
        # Update weighted recall
        weighted_recall += recall * class_instances
    
    # Normalize by total instances
    weighted_recall /= total_instances if total_instances > 0 else 1
    return weighted_recall

# Calculate accuracy, recall and weighted recall for Decision Tree
accuracy_dt = calculate_accuracy(conf_matrix_dt)
recall_dt_class_2 = calculate_class_recall(conf_matrix_dt, 2)  # Recall for class 2
weighted_recall_dt = calculate_weighted_recall(conf_matrix_dt)

# Calculate accuracy, recall and weighted recall for MLP
accuracy_mlp = calculate_accuracy(conf_matrix_mlp)
recall_mlp_class_2 = calculate_class_recall(conf_matrix_mlp, 2)  # Recall for class 2
weighted_recall_mlp = calculate_weighted_recall(conf_matrix_mlp)

# Print results
print("=> Results without libraries")
print(f"DT Accuracy: {accuracy_dt:.8f}")
print(f"DT Recall (Class 2): {recall_dt_class_2:.8f}")
print(f"DT Weighted Recall: {weighted_recall_dt:.8f}")
print(f"MLP Accuracy: {accuracy_mlp:.8f}")
print(f"MLP Recall (Class 2): {recall_mlp_class_2:.8f}")
print(f"MLP Weighted Recall: {weighted_recall_mlp:.8f}")
