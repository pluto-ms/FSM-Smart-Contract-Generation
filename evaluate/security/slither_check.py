from utils.data_utils import data_utils
from utils.solidity_utils import solidity_utils
import string
import slither
import os
import argparse
from slither.detectors import all_detectors
from colorama import Fore, Back, Style, init



# Merge check items of the same type
def merge_check_items(check_items):
    # Group by check type
    check_items_grouped = {}
    for item in check_items:
        check_type = item['check_type']
        if check_type not in check_items_grouped:
            check_items_grouped[check_type] = []
        check_items_grouped[check_type].append(item)
    
    # Merge ranges within each check type
    merged_results = []
    for check_type, items in check_items_grouped.items():
        # Sort by starting line
        items = sorted(items, key=lambda x: (x['start_line'], x['end_line']))
        # Merge ranges
        merged = []
        current = items[0]
        for next_item in items[1:]:
            if next_item['start_line'] <= current['end_line']:  # 范围重叠或相邻
                current['end_line'] = max(current['end_line'], next_item['end_line'])
            else:
                merged.append(current)
                current = next_item
        merged.append(current)  # Add the last one
        # Add to final results
        merged_results.extend(merged)
    
    return merged_results


# Use Slither to check vulnerabilities in a single smart contract
def check_one_by_slither(smart_contract: str):
    merged_check_items = []
    try:
        # Write the contract to a temporary file
        data_utils.save_to_file('temp_sc.sol', smart_contract)

        # Switch to the appropriate version
        version = solidity_utils.extract_solc_version(smart_contract)
        solidity_utils.switch_solc_select_version(version)

        # Analyze the contract with Slither
        slith = slither.Slither('temp_sc.sol')

        for detector in dir(all_detectors):
            if detector[0] in string.ascii_uppercase:
                slith.register_detector(getattr(all_detectors, detector))
        
        detector_results = sum(slith.run_detectors(), [])

        check_info = []
        for detector_result in detector_results:
            # Exclude safe check items
            if detector_result['impact'] != 'Informational' and detector_result['impact'] != 'Optimization':
                check_type = detector_result['check']
                # Extract code location information from all elements
                for element in detector_result.get("elements", []):
                    source_mapping = element.get("source_mapping", {})
                    lines = source_mapping.get("lines", []) # Corresponding lines in the code
                    # Store in the results list
                    check_info.append({
                        "check_type": check_type,
                        "impact" : detector_result['impact'],
                        "confidence": detector_result['confidence'],
                        "start_line": lines[0],
                        "end_line": lines[-1],
                        "overall_description": detector_result['description']
                    })
                    break
        
        # Merge similar check items
        merged_check_items = merge_check_items(check_info)

        for item in merged_check_items:
            print(f"Check Type: {item['check_type']}, Impact: {item['impact']}, Confidence: {item['confidence']}, Start Line: {item['start_line']}, End Line: {item['end_line']}")

    except Exception as e:
        print(Fore.RED + 'Compile Error:\n' + str(e))
        return str(e)

    finally:
        # Delete the temporary file
        data_utils.delete_file('temp_sc.sol')

    return merged_check_items


# Compute the risk score and risk proportion for a single smart contract
def compute_risk_score(smart_contract):
    merged_check_items = check_one_by_slither(smart_contract)

    if isinstance(merged_check_items, str): # Compilation error occurred
        return None

    # Record the count of risks by severity
    low_count = 0
    medium_count = 0
    high_count = 0

    # Define scoring maps
    impact_map = {'High': 3, 'Medium': 2, 'Low': 1}
    confidence_map = {'High': 3, 'Medium': 2, 'Low': 1}

    # Calculate the total risk score
    total_risk_score = 0
    total_count = len(merged_check_items)


    for item in merged_check_items:

        if item['impact'] == 'Low':
            low_count = low_count + 1
        elif item['impact'] == 'Medium':
            medium_count = medium_count + 1
        elif item['impact'] == 'High':
            high_count = high_count + 1


        impact_score = impact_map[item['impact']]
        confidence_score = confidence_map[item['confidence']]
        
        # Calculate the risk score
        risk_score = impact_score * confidence_score
        # Accumulate the total risk score
        total_risk_score += risk_score

    # Compute the average risk score
    average_risk_score = total_risk_score / total_count if total_count > 0 else 0

    # Calculate the count and proportion of risks for each severity level
    low_percent = low_count / total_count if total_count > 0 else 0
    medium_percent = medium_count / total_count if total_count > 0 else 0
    high_percent = high_count / total_count if total_count > 0 else 0

    print(f"Average Risk Score: {average_risk_score:.2f}")

    result = {}

    result['risk_score'] = average_risk_score

    result['Low'] = {'count': low_count, 'percent': low_percent}
    result['Medium'] = {'count': medium_count, 'percent': medium_percent}
    result['High'] = {'count': high_count, 'percent': high_percent}

    return result


def evaluate_security_by_slither(data_path, result_path, remove_import_statements, openzeppelin_path):
    dataset = data_utils.load_jsonl_dataset(data_path)

    risk_score_list = []
    total_risk_score = 0
    compile_failure_count = 0
    zero_risk_score_count = 0
    contain_high_risk_count = 0

    total_high_risk_count = 0
    total_medium_risk_count = 0
    total_low_risk_count = 0

    for data in dataset:
        code = data['code']
        code = data_utils.extract_code(code) if not code == '' else 'empty'

        if remove_import_statements:
            code = data_utils.remove_import_statements(code)
        else:
            code = code.replace('@openzeppelin', openzeppelin_path)

        
        result = compute_risk_score(code)
        if result is None:
            compile_failure_count += 1
            risk_score = 10  # Set the risk factor for failure to compile to 10
        else:
            risk_score = result['risk_score']

            if risk_score == 0:
                zero_risk_score_count += 1
            
            if result['High']['count'] != 0 :
                contain_high_risk_count += 1
            
            total_high_risk_count += result['High']['count']
            total_medium_risk_count += result['Medium']['count']
            total_low_risk_count += result['Low']['count']

        risk_score_list.append(risk_score)
        total_risk_score += risk_score
    
    average_risk_score = total_risk_score/len(dataset)

    compile_success_count = len(dataset) - compile_failure_count
    zero_risk_contract_percentage = (zero_risk_score_count / compile_success_count) * 100 if compile_success_count > 0 else 0
    high_risk_contract_percentage = (contain_high_risk_count / compile_success_count) * 100 if compile_success_count > 0 else 0

    print(Fore.GREEN + f"zero risk contract percentage(ZRCP): {zero_risk_contract_percentage}%")
    print(Fore.GREEN + f"high risk contract percentage(HRCP): {high_risk_contract_percentage}%")
    print(Fore.GREEN + f'vulnerability risk score(VRS): {average_risk_score}')

    data_utils.append_jsonl(result_path, {'file': data_path,
                                          'zero_risk_contract_percentage(ZRCP)': f'{zero_risk_contract_percentage}%',
                                          'high_risk_contract_percentage(HRCP)': f'{high_risk_contract_percentage}%',
                                          'vulnerability_risk_score(VRS)': average_risk_score,
                                          'total_high_risk_count': total_high_risk_count,
                                          'total_medium_risk_count': total_medium_risk_count,
                                          'total_low_risk_count': total_low_risk_count})



def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze security of generated code by Slither."
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

    parser.add_argument(
        "--openzeppelin_path",
        type=str,
        default="./openzeppelin",
        help="Path to the OpenZeppelin library.",
    )

    return parser.parse_args()



def main(args):
    init(autoreset=True)

    if not args.data_path:
        print("please enter data path")
        return
    
    # if not args.result_path:
    #     print("please enter result path")
    #     return
    
    if args.result_path == '':
        file_name = args.data_path.split('/')[-1]
        result_folder = args.data_path.replace(file_name, '') + 'evaluation_result/'
        if not os.path.exists(result_folder):
            os.mkdir(result_folder)
        args.result_path = result_folder + file_name.split('.')[0] + '_security_result.jsonl'

    evaluate_security_by_slither(args.data_path, 
                                 args.result_path, 
                                 args.remove_import_statements, 
                                 args.openzeppelin_path)


if __name__ == '__main__':
    args = parse_args()
    main(args)
