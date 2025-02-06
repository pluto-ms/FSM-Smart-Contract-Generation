from utils.data_utils import data_utils
import re
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Used to split smart contract code into functions and comments."
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
        default="func_comment.jsonl",
        help="Path for the output data file.",
    )

    return parser.parse_args()

# Extracting functions and their corresponding comments from Solidity code
def extract_function_with_comments(code):
    code_list = []
    funcname_pattern = re.compile(r'function\s+(.+?)\s*\(')
    funcbody_pattern = re.compile(r'{(.*)}', re.DOTALL)
    
    # Use finditer to retrieve all function definition matches
    func_iter = re.finditer(r'\bfunction\s+[\w]+\s*\(.*?\)\s*(?:\w+\s+)*{.*?}', code, re.DOTALL)
    
    prev_end = 0  # Track the end position of the previous function
    
    for func_match in func_iter:
        func = func_match.group()
        func_start = func_match.start()
        func_end = func_match.end()
        
        pre_text = code[prev_end:func_start]
        
        single_comment_pattern = re.compile(r'//.*$', re.MULTILINE)
        multi_comment_pattern = re.compile(r'/\*.*?\*/', re.DOTALL)
        
        multi_comments = multi_comment_pattern.findall(pre_text)

        single_comments = single_comment_pattern.findall(pre_text)
        
        # Combine comments
        comments = []
        for comment in multi_comments:
            comments.append(comment.strip())
        for comment in single_comments:
            comments.append(comment.strip())
        
        # Filter out non-comment code that may be present
        comments = [c for c in comments if c.startswith('//') or c.startswith('/*')]
        
        func_comments = '\n'.join(comments)
        
        func_name = funcname_pattern.findall(func)[0]

        func_body = funcbody_pattern.findall(func)[0].strip() if funcbody_pattern.findall(func) else ""
        
        code_list.append({
            'func_name': func_name,
            'func_code': func,
            'func_body': func_body,
            'func_comments': func_comments
        })
        
        # Update prev_end to the current function's end position
        prev_end = func_end

    return code_list


def main(args):
    dataset = data_utils.load_jsonl_dataset(args.source_data_path)

    for data in dataset:
        func_comment_list = extract_function_with_comments(data['code'])

        for func_comment in func_comment_list:
            func_comment_data = {}
            func_comment_data['comment'] = func_comment['func_comments']
            func_comment_data['function_code'] = func_comment['func_code']

            data_utils.append_jsonl(args.output_data_path, func_comment_data)



if __name__ == '__main__':
    args = parse_args()
    main(args)