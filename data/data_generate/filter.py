from utils.data_utils import data_utils
from utils.prompt_utils import prompt_utils
from utils.Model import Model
from colorama import Fore, Back, Style, init
import argparse
import re


def parse_args():
    parser = argparse.ArgumentParser(
        description="Data filtering."
    )

    parser.add_argument(
        "--source_data_path",
        type=str,
        default="source_code.jsonl",
        help="Path to the source code data file.",
    )

    parser.add_argument(
        "--output_data_path",
        type=str,
        default="output.jsonl",
        help="Path for the output data file.",
    )

    parser.add_argument(
        "--is_manual_filter",
        type=bool,
        default=True,
        help="Whether to manually filter or not.",
    )

    parser.add_argument(
        "--is_discriminator_filter",
        type=bool,
        default=True,
        help="Whether to use discriminator filter or not.",
    )

    return parser.parse_args()


def filter_by_code_length(code, min, max):
    words = code.split()
    words_length = len(words)
    if words_length > min and words_length < max:
        return True
    return False


def filter_by_fsm(fsm_json_text):
    fsm = data_utils.extract_fsm(fsm_json_text)

    json_error, states_count, events_count, func_count = data_utils.repair_and_get_json(fsm)

    if not json_error and states_count > 2 and events_count != 0 and func_count != 0 \
        and func_count < 10  and 'State1' not in fsm and 'actionA' not in fsm \
        and 'EventA' not in fsm_json_text and 'variable1' not in fsm:
                return True
    return False


def filter_by_discriminator(model: Model, user_requirement: str, smart_contract_code: str, fsm: str):
     
    prompt = prompt_utils.discriminator_prompt(user_requirement, smart_contract_code, fsm)
    response = model.single_dialogue(prompt)

    # Use regular expressions to extract the answer
    match = re.search(r"<answer, (Yes|No)>", response)

    # Determine the answer and define the variable
    if match:
        final_answer = match.group(1) == "Yes" 
    else:
        raise ValueError("No valid answer found in the response.")
    
    return final_answer


def main(args):
    init(autoreset=True)

    dataset = data_utils.load_jsonl_dataset(args.source_data_path)
    
    filter_list_1 = []
    if args.is_manual_filter:
        for i, data in enumerate(dataset):
              if filter_by_fsm(data['code']):
                   filter_list_1.append(i)
        
    if len(filter_list_1) != 0 : 
         filter_dataset_1 = dataset.select(filter_list_1)
    else:
         filter_dataset_1 = dataset

    filter_list_2 = []
    if args.is_discriminator_filter:

        gpt = Model('openai')

        for j, data in enumerate(filter_dataset_1):
            if filter_by_discriminator(gpt, data['user_requirement'], data['code'], data['FSM']):
                filter_list_2.append(j)
    
    if len(filter_list_2) != 0 : 
         filter_dataset_2 = filter_dataset_1.select(filter_list_2)
         filter_dataset_2.to_json(args.output_data_path)
    elif len(filter_list_1) != 0:
         filter_dataset_1.to_json(args.output_data_path)
    else:
         print(Fore.RED + 'Incorrect filtering condition settings.')


if __name__ == '__main__':
    args = parse_args()
    main(args)