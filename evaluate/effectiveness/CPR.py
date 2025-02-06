import os
from utils.data_utils import data_utils
from utils.solidity_utils import solidity_utils
import argparse
from colorama import Fore, init


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze compilation pass rate of generated code."
    )

    parser.add_argument(
        "--data_path",
        type=str,
        default=None,
        help="Please enter the data path here.",
    )

    parser.add_argument(
        "--result_path",
        type=str,
        default="",
        help="Please enter the result path here.",
    )

    parser.add_argument(
        "--remove_import_statements",
        type=bool,
        default=False,
        help="Whether to remove import statements.",
    )

    return parser.parse_args()



def compile_list(smart_contract_list):
    results = []
    success_count = 0

    for smart_contract in smart_contract_list:
        
        compile_result, compile_info = solidity_utils.compile_solidity(smart_contract)
        results.append({
            'compile_result': compile_result,
            'compile_info': compile_info
        })
        
        if compile_result:
            success_count += 1

    total_contracts = len(smart_contract_list)
    success_rate = (success_count / total_contracts) * 100 if total_contracts > 0 else 0

    return {
        'success_rate': success_rate,
        'results': results
    }



def calculate_compilation_pass_rate(data_path, result_path, remove_import_statements):
    dataset = data_utils.load_jsonl_dataset(data_path)

    code_list = []
    for data in dataset:
        code = data_utils.extract_code(data['code'])

        if remove_import_statements:
            code = data_utils.remove_import_statements(code)
        else:
            openzeppelin_path = './openzeppelin'
            code = code.replace('@openzeppelin', openzeppelin_path)
        code_list.append(code)

    compile_results = compile_list(code_list)

    # for compile_result in compile_results['results']:
    #     print(str(compile_result['compile_info']))

    print(Fore.GREEN + f"compilation pass rate(CPR): {compile_results['success_rate']}%")

    data_utils.append_jsonl(result_path, {'file': data_path, 'compilation_pass_rate(CPR)': f"{compile_results['success_rate']}%"})




def main(args):
    init(autoreset=True)

    if not args.data_path:
        print("please enter data path")
        return
    
    if args.result_path == '':
        file_name = args.data_path.split('/')[-1]
        result_folder = args.data_path.replace(file_name, '') + 'evaluation_result/'
        if not os.path.exists(result_folder):
            os.mkdir(result_folder)
        args.result_path = result_folder + file_name.split('.')[0] + '_effectiveness_result.jsonl'
    
    
    calculate_compilation_pass_rate(args.data_path, args.result_path, args.remove_import_statements)




if __name__ == "__main__":
    args = parse_args()
    main(args)