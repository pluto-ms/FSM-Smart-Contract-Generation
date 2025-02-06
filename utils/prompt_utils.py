class prompt_utils:
    
    @staticmethod
    def generate_fsm_prompt(smart_contract_code: str) -> str:
        prompt = \
        f"""Please extract and summarize the finite state machine \
corresponding to the contract code based on the given smart contract code.
### Please study the content of the finite state machine carefully, and the extracted finite state machine \
should strictly follow the writing format:
```json
{state_machine_json}
```
In addition, it is essential to strictly adhere to the following points:
1.If the smart contract code to be extracted has no obvious logic and it is difficult to generate \
a finite state machine that meets the format, you only need answer [None].
2.When the provided code has multiple smart contract classes, only the last one needs to be processed.
3.Do not output anything extra except for the JSON text of the finite state machine.
### The smart contract code to be extracted is as follows:
```Solidity
{smart_contract_code}
```
"""
        return prompt
    

    @staticmethod
    def generate_requirement_prompt(smart_contract_code: str) -> str:
        prompt = \
        f"""Please extract and summarize the user's requirement description based on the following smart contract code. \
The user's requirement description should include the following content:
1. The overall type of contract (e.g. auction contract, voting contract, token contract, etc.) and its main functions.
2. The logical process of the transition between different stages of the contract and their corresponding states.
3. Main variables, functions, and events.
Try to describe these requirements in concise natural language, and summarize them in [60-150] words! Please imitate \
the following example for output:
\"""
This smart contract is a [voting contract]. The main functions include [creating proposals, voting, and calculating results]. \
The main states of the contract include [Proposal Creation, Voting in Progress, and Voting Ended]. \
The process logic for the transition of states is as follows: [First, create a proposal and initialize the voting options. \
Then, enter the voting phase, allowing users to vote on the proposal. Each address can only vote once. \
After the voting ends, calculate the result and announce the winning proposal. \
After this round of voting ends, proceed to the next round of voting]. \
The main variables include [proposal, voter list, and vote count]. \
The main functions include [proposal creation, voting, and ending voting]. \
The main events include [proposal creation, voting completion, and result announcement].
\"""
###The smart contract code to be extracted is as follows:
```Solidity
{smart_contract_code}
```
"""
        return prompt
    

    @staticmethod
    def discriminator_prompt(user_requirement: str, smart_contract_code: str, fsm: str):
        prompt = \
        f"""Your task is to evaluate the quality of the following <user_requirement, fsm, smart_contract_code> tuple based on three criteria:
1. Effectiveness: Whether the FSM and the smart contract match the description of the user's requirements.
2. Security: Whether the generated smart contract has obvious security vulnerabilities, such as overflow, permission issues or logic errors.
3. Correctness: Whether the FSM is consistent with the user requirements, and whether the conversion from FSM to smart contract code is correct and without logical deviation.
### Input Details:
User Requirement:
\"""
{user_requirement}
\"""
FSM:
\"""
{fsm}
\"""
Smart Contract Code:
\"""
{smart_contract_code}
\"""
### Your output should be as follows:
1. Provide scores (1~10) for the following aspects:
Effectiveness: <Score>
Security: <Score>
Correctness: <Score>
2. If all three scores are greater than 8, return <answer, Yes>. Otherwise, return <answer, No>.
### Output example:
Effectiveness: 9
Security: 9
Correctness: 8.5
<answer, Yes>
"""
        return prompt


    # Generate prompts for testing smart contract generation without using FSM
    @staticmethod
    def generate_code_no_fsm_prompt(user_requirement: str, version: str) -> str:
        prompt = \
        f"""Please generate the corresponding smart contract code (single contract, solidity version is {version}) based on the following user requirements. \
**Please note that there should be no extra output other than code**:
\"""
{user_requirement}
\""" """
        return prompt
    


    # Generate prompts for testing smart contract generation using FSM
    @staticmethod
    def generate_code_with_fsm_prompt(user_requirement: str, version: str) -> str:
        prompt_1 = \
        f"""You can generate corresponding finite state machines based on user requirements. **Please note that there should be no extra output other than finite state machines**:
### Please study the following content of finite state machines carefully, and the generated finite state machines should strictly follow the writing format:
```json
{state_machine_json}
```
### The user requirements are as follows:
\"""
{user_requirement}
\""" """
        
        prompt_2 = f"Then please generate the corresponding smart contract code (single contract, solidity version is {version}) \
based on the finite state machine generated above, **please note that there should be no extra output other than code**."

        return prompt_1, prompt_2
    

    # Generate prompts for testing smart contract generation using FSM
    @staticmethod
    def generate_code_with_fsm_no_example_prompt(user_requirement: str, version: str) -> str:
        prompt_1 = \
        f"""You can generate corresponding finite state machines based on user requirements. **Please note that there should be no extra output other than finite state machines**.
### The user requirements are as follows:
\"""
{user_requirement}
\""" """
        
        prompt_2 = f"Then please generate the corresponding smart contract code (single contract, solidity version is {version}) \
based on the finite state machine generated above, **please note that there should be no extra output other than code**."

        return prompt_1, prompt_2
    


    @staticmethod
    def feedback_by_compile_error_prompt(error_info):
        prompt = \
        f"""The code you generated encountered the following error after compilation:
```Error Message
{error_info}
```
### Please fix the issue in the code based on the error message above and return the modified smart contract code.

Please note:
- If it is an undeclared identifier error, ensure that the variable or function is properly declared.
- If it is a function call or method usage error, check if the parameters are passed correctly.
- If it is a syntax error, correct the code according to Solidity language specifications.
- If it is a permission-related error (such as a `require` statement), ensure the conditions are reasonable.
"""
        return prompt
    

    @staticmethod
    def feedback_by_security_risk_prompt(security_risk_info):
        prompt = "The code you generated has the following potential security vulnerabilities:\n"
        for i, risk_info in enumerate(security_risk_info):
            prompt = prompt + f"""### {i+1}. 
- vulnerability type: {risk_info['check_type']}
- level: {risk_info['impact']}
- start line: {risk_info['start_line']}
- end line: {risk_info['end_line']}
- overall description: {risk_info['overall_description']} \
--------------------------------------------------------------------------------------------
"""
        prompt = prompt + "Please fix the code according to the above security vulnerability tips."
        return prompt



state_machine_json = """\
{
    // Name of the smart contract.
    "contractName": "SimpleContract",
    // The list of contracts inherited by this contract
    "inherited contracts": ["ContractA", "ContractB"],
    // Name of the initial state.
    "initialState": "State1",
    /** states: An object containing all states(The number of states is determined by the code, do not rigidly follow this example), where each state contains a state name and a list of transitions.
        The state transition list (transitions) includes the following sections:
        trigger: The event or condition that triggers the state transition.
        target: The name of the target state.
        action: The action performed during the state transition process.
        condition[optional]: The condition for state transition.
    **/
    "states": [
      {
        "name": "State1",
        "transitions": [
          {
            "trigger": "EventA",
            "target": "State2",
            "action": "actionA",
            "condition": "conditionA"
          }
        ]
      },
      {
        "name": "State2",
        "transitions": [
          {
            "trigger": "EventB",
            "target": "State3",
            "action": "actionB",
            "condition": "conditionB"
          }
        ]
      },
      {
        "name": "State3",
        "transitions": [
          {
            "trigger": "EventC",
            "target": "State1",
            "action": "actionC"
          }
        ]
      }
    ],
    // variables: A list containing all variables, each variable containing the variable name, type, and initial value.
    "variables": [
      {
        "name": "variable1",
        "type": "uint",
        "initialValue": 0
      },
      {
        "name": "variable2",
        "type": "mapping(address => uint)",
        "initialValue": {}
      }
    ],
    // functions: Contains a list of all functions, each function contains the function name and function action.
    "functions": [
      {
        "name": "actionA",
        "function": "The function of actionA."
      },
      {
        "name": "actionB",
        "function": "The function of actionB."
      }
    ],
    // events: Contains a list of all events.
    "events": ["EventA", "EventB"]
}"""