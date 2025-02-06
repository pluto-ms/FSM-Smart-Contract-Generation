from utils.data_utils import data_utils
from utils.prompt_utils import prompt_utils
from utils.solidity_utils import solidity_utils
from utils.Model import Model
from colorama import Fore, Back, Style, init
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate requirement and fsm."
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

    return parser.parse_args()


def generate_data(smart_contract_code: str, model: Model, output_path: str):

    requirement_prompt = prompt_utils.generate_requirement_prompt(smart_contract_code)
    requirement_response = model.single_dialogue(requirement_prompt)

    fsm_prompt = prompt_utils.generate_fsm_prompt(smart_contract_code)
    fsm_response = model.single_dialogue(fsm_prompt)

    data = {}
    data['user_requirement'] = requirement_response
    data['FSM'] = fsm_response
    data['version'] = solidity_utils.extract_solc_version(smart_contract_code)
    data['code'] = smart_contract_code

    data_utils.append_jsonl(output_path, data)



def main(args):
    init(autoreset=True)

    gpt = Model('openai')

    dataset = data_utils.load_jsonl_dataset(args.source_data_path)

    for data in dataset:
        generate_data(data['code'], gpt, args.output_data_path)



if __name__ == '__main__':
    args = parse_args()
    main(args)