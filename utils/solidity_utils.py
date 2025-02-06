import re
from colorama import Fore, Back, Style, init
from solcx import (
    get_installed_solc_versions,    
    install_solc,                   
    set_solc_version,               
    get_solc_version,               
    compile_source,                 
    compile_files,                  
)
from solc_select import solc_select
import subprocess



class solidity_utils:

    # Compare two version strings.
    @staticmethod
    def compare_versions(version1: str, version2: str) -> int:
        v1_parts = list(map(int, version1.split('.')))
        v2_parts = list(map(int, version2.split('.')))
        
        # Compare each part of the version
        for v1, v2 in zip(v1_parts, v2_parts):
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
                
        # If all parts are equal and one version has more parts
        return len(v1_parts) - len(v2_parts)
    

    # Extract the Solidity version from the provided content.
    @staticmethod
    def extract_solc_version(content) -> str:
        print('--------------------------------------------------------------------------------------------------------------')
        try:
            matches = re.findall(r'pragma\s+solidity\s*(=|>=|<=|\^)?\s*(\d+\.\d+\.\d+);', content)
            if matches:
                exact_versions = [version for operator, version in matches if operator == '=']
                chosen_version = exact_versions[0] if exact_versions else matches[0][1]
                # print(Fore.GREEN + f"Using Solidity version: {chosen_version}")

                if solidity_utils.compare_versions(chosen_version, "0.4.11") < 0:
                    print(Fore.YELLOW + "Extracted version is lower than 0.4.11. Defaulting to 0.4.12")
                    return "0.4.12"
                
                return chosen_version
            else:
                print(Fore.YELLOW + "No Solidity version found. Defaulting to 0.8.0")
                return "0.8.0"
        except Exception as e:
            print(Fore.RED + f"Error reading Solidity file: {e}")
            raise


    
    # Switching the compiler version of the py-solc-x library
    @staticmethod
    def switch_solcx_version(version):
        installed_versions = [str(v) for v in get_installed_solc_versions()]

        if version in installed_versions:
            print(f"Version {version} is already installed, switching directly.")
        else:
            print(f"Version {version} is not installed, downloading...")
            install_solc(version)
            print(f"Version {version} has been downloaded.")

        set_solc_version(version)
        print(f"Successfully switched to version {version}.")

        current_version = get_solc_version()
        return f"The current Solidity compiler version being used is: {current_version}"
    

    # Compiling Solidity Code with the py-solc-x Library
    @staticmethod
    def compile_solidity(solidity_code):
        version = solidity_utils.extract_solc_version(solidity_code)
        solidity_utils.switch_solcx_version(version)
        try:
            compiled_sol = compile_source(solidity_code)
            print(Fore.GREEN + "Compile Successfully")
            return True, compiled_sol
        except Exception as e:
            print(Fore.RED + "Compile Failure")
            return False, e
    

    # Switch the version of solc-select
    @staticmethod
    def switch_solc_select_version(version):
        installed_versions = [str(v) for v in solc_select.installed_versions()]

        if version in installed_versions:
            print(f"Version {version} is already installed, switching directly.")
        else:
            print(f"Version {version} is not installed, downloading...")
            subprocess.run(['solc-select', 'install', version], check=True, capture_output=True)
            print(f"Version {version} has been downloaded.")

        subprocess.run(['solc-select', 'use', version], check=True, capture_output=True)
        print(f"Successfully switched to version {version}.")

        # result = subprocess.run(['solc', '--version'], capture_output=True, text=True)
        # return f"The current Solidity compiler version being used is: {result.stdout.strip()}"


    @staticmethod
    def extract_solcx_compile_error(compile_error: str):
        stderr_content = re.search(r'> stderr:.*', compile_error, re.DOTALL)
        if stderr_content:
            return stderr_content.group(0).strip()
        return 'extract error fail!'


def main():
    solidity_utils.switch_solc_select_version('0.8.0')


if __name__ == '__main__':
    main()