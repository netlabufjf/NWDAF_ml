#!/usr/bin/env bash

# Helper script to iterate over all CSV files to add a label to their names
# this is necessary to help adding the labels to the data on the next step

CSV_FOLDER=./pcap/output/3-JSON-export/ # read CSV files from here
OUT_FOLDER=./pcap/output/4-ML/preprocess/labeled_files/ # save the output there
COUNTER=0

# List all CSV files in the input folder
FILES=("$CSV_FOLDER"*.csv)
FILES_LIST_SIZE=${#FILES[@]}

if [ $FILES_LIST_SIZE -eq 0 ]; then
    echo "[ERRO] No CSV files found in the directory: $CSV_FOLDER"
    exit 1
fi

echo "[INFO] Read $FILES_LIST_SIZE files"

# Loop through each file and rename it based on user input
for FILE in "${FILES[@]}"; do
    ((COUNTER++))

    # Extract the base name of the file (without extension)
    BASE_NAME=$(basename "$FILE" .csv)
    
    while true; do

        # Display options to the user
        echo "[INFO] Working on file $COUNTER of $FILES_LIST_SIZE"
        echo "Choose a label for $BASE_NAME :"
        echo "1. eMBB"
        echo "2. URLLC"
        echo "3. mMTC / mIoT"
        echo "4. Skip this file for now"
        echo "5. Cancel and exit"
        echo "" # new line to improve readability
    
        read -p "Enter an option (1-5): " OPTION
        
        # Validate the user's input
        case "$OPTION" in
            1)
                LABEL="embb"
                break
                ;;
            2)
                LABEL="urllc"
                break
                ;;
            3)
                LABEL="mmtc"
                break
                ;;
            4)
                break
                ;;
            5)
                echo "[INFO] User asked to quit"
                exit 1
                ;;
            *)
                echo "[ERRO] Invalid option!"
                sleep 2
                ;;
        esac
    done
    
    # Construct the new filename with the label appended
    NEW_FILE="$OUT_FOLDER$BASE_NAME"_"$LABEL.csv"
    
    # Move and rename the file
    mv "$FILE" "$NEW_FILE"
    # echo "[DEBU] Moved and renamed '$FILE' to '$NEW_FILE'" # DEBUG
done

echo "[INFO] All files have been processed"
