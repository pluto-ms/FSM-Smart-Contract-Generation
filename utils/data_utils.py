import datasets
from configparser import ConfigParser
import json
import re
import json_repair
import os
from datasketch import MinHash, MinHashLSH
import string



class data_utils:

    @staticmethod
    def load_text(file_path: str):
        with open(file_path, "r") as f:
            content= f.readlines()
        return "\n".join(content)


    # Load the dataset from the JSONL file
    @staticmethod
    def load_jsonl_dataset(file_path: str):
        dataset = datasets.load_dataset("json", data_files=file_path, split="train")
        return dataset
    

    # Load config file
    @staticmethod
    def load_config(config_path: str):
        config = ConfigParser()
        config.read(config_path, encoding='UTF-8')
        return config
    

    # Write a piece of data to the file
    @staticmethod
    def append_jsonl(file_path: str, data: str):
        with open(file_path, 'a') as file:
            line = json.dumps(data)
            file.write(line + '\n')
        
    
    # Write multiple pieces of data to a file
    @staticmethod
    def write_jsonl(file_path: str, data: str):
        with open(file_path, 'w', encoding='utf-8') as output_file:
            for item in data:
                output_file.write(json.dumps(item) + '\n')


    # Retrieve the number of words in the text
    @staticmethod
    def get_word_count(text: str):
        words = text.split()
        return len(words)


    # Merge JSONL files with the same format and return the merged dataset
    @staticmethod
    def merge_jsonl(file_path_1: str, file_path_2: str, merged_file_path: str):
        dataset_1 = data_utils.load_jsonl_dataset(file_path_1)
        dataset_2 = data_utils.load_jsonl_dataset(file_path_2)
        merged_dataset = datasets.concatenate_datasets([dataset_1, dataset_2])
        merged_dataset.to_json(merged_file_path)
        print(f'The number of merged data items is: {len(merged_dataset)}')
        return merged_dataset
    

    # Extracting Finite State Machines from Text
    @staticmethod
    def extract_fsm(mix_text):
        if re.match(r'^```(StateMachine/json)?', mix_text) and re.search(r'```$', mix_text):
            cleaned_json = re.sub(r'^```(StateMachine/json)?\s*|```$', '', mix_text, flags=re.MULTILINE)
        else:
            cleaned_json = mix_text  # If there is no label, return as is
        return cleaned_json
    

    # Extract code from text
    @staticmethod
    def extract_code(code):

        pattern = r'```solidity(.*?)```'

        match = re.search(pattern, code, re.DOTALL)
        
        if match:
            return match.group(1) 
        else:
            return code 
    

    # Remove the import statement
    @staticmethod
    def remove_import_statements(solidity_code):
        cleaned_code = re.sub(r'^\s*import\s+.*?;', '', solidity_code, flags=re.MULTILINE)
        return cleaned_code
    

    # Fix finite state machine data and retrieve data
    @staticmethod
    def repair_and_get_json(fsm_json_text):
        json_error = False
        states_count = 0
        events_count = 0
        func_count = 0
        # Check if the JSONL data is compliant
        try:
            fsm_json = json.loads(fsm_json_text)
            states_count = len(fsm_json['states'])
            events_count = len(fsm_json['events'])
            func_count = len(fsm_json['functions'])
        except json.decoder.JSONDecodeError:
            try:
                fsm_repair_json = json_repair.loads(fsm_json_text) # Fix JSON
                states_count = len(fsm_json['states'])
                events_count = len(fsm_repair_json['events'])
                func_count = len(fsm_json['functions'])
            except Exception:
                json_error = True
        
        return json_error, states_count, events_count, func_count
    
    
    @staticmethod
    def save_to_file(file_name, content):
        with open(file_name, 'w') as f:
            f.write(content)


    @staticmethod
    def delete_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    
    # Similarity-based de-duplication
    @staticmethod
    def duplicate(dataset_path, ouput_path):
        dataset = data_utils.load_jsonl_dataset(dataset_path)
        paragraphs = []

        for data in dataset:
            paragraphs.append(data['user_requirement'])


        def preprocess(text):
            text = text.lower()
            text = text.translate(str.maketrans('', '', string.punctuation))
            text = ' '.join(text.split())
            return text.split()


        # Create MinHashLSH object
        lsh = MinHashLSH(threshold=0.8, num_perm=128)

        # Dictionary for storing MinHash signatures
        minhash_dict = {}
        # Store reserved paragraph indexes
        kept_indices = set()

        # Calculate MinHash signature and insert LSH
        for i, paragraph in enumerate(paragraphs):
            tokens = preprocess(paragraph)
            m = MinHash()
            
            for token in tokens:
                m.update(token.encode('utf8'))
            
            # Search for similar items
            result = lsh.query(m)
            
            # If there are no similar items or no reserved paragraphs in the result, keep the current paragraph
            if not result or not any(idx in kept_indices for idx in result):
                lsh.insert(i, m) 
                kept_indices.add(i) 

        # Outputting de-duplicated paragraphs
        # unique_paragraphs = [paragraphs[i] for i in kept_indices]

        # print(len(unique_paragraphs))
        # print(len(kept_indices))

        filter_dataset = dataset.select(kept_indices)
        print(len(filter_dataset))
        filter_dataset.to_json(ouput_path)

