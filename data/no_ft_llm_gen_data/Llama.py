from _Model import _Model, Evaluation_gen
from colorama import init, Fore
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="LlaMa generates data for evaluation."
    )

    parser.add_argument(
        "--evaluation_path",
        type=str,
        default="evaluation.jsonl",
        help="Path to the evaluation data file.",
    )

    parser.add_argument(
        "--evaluation_type",
        type=str,
        default="effectiveness",
        help="The types of evaluations include effectiveness and security.",
    )

    parser.add_argument(
        "--is_use_fsm",
        type=bool,
        default=False,
        help="Whether to use fsm.",
    )

    return parser.parse_args()

def main(args):
    init(autoreset=True)
    llama = _Model('llama')

    if args.evaluation_type == 'effectiveness' or args.evaluation_type == 'security':
        Evaluation_gen.generate_code_for_effectiveness_and_security(llama, args.evaluation_path, args.is_use_fsm)
    else:
        raise Fore.RED + 'The type of evaluation is incorrect.'


if __name__ == '__main__':
    args = parse_args()
    main(args)