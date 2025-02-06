import os
from utils.data_utils import data_utils
from utils.prompt_utils import prompt_utils
from utils.solidity_utils import solidity_utils
from utils.fsm_utils import fsm_utils
from evaluate.security import slither_check
from utils.Model import Model


class _Model(Model):

    def __init__(self, config: str):
        super().__init__(config)



    def generate_use_fsm_scg(self, user_requirement: str, version: str, openzeppelin_path: str, output_path: str, feedback_count: int=1):
        conversation = []
        prompt_1, prompt_2 = prompt_utils.generate_code_with_fsm(user_requirement, version)

        # Initial FSM generation
        response_1, conversation = self.multiple_dialogue(prompt_1, conversation, random_parameters=True)

        # FSM validation and feedback loop
        fsm = data_utils.extract_fsm(response_1)
        response_1 = self.check_fsm_format_and_graph(fsm, feedback_count, conversation)

        # Generate smart contract code
        response_2, conversation = self.multiple_dialogue(prompt_2, conversation, random_parameters=True)

        # Smart contract code compilation and security check loop
        code = data_utils.extract_code(response_2)
        code = code.replace('@openzeppelin', openzeppelin_path)
        response_2 = self.check_compilation_and_security(code, feedback_count, conversation, openzeppelin_path)


        data = {}
        data['user_requirement'] = user_requirement
        data['FSM'] = data_utils.extract_fsm(response_1)
        data['code'] = data_utils.extract_code(response_2)
        data['model'] = self.model
        data_utils.append_jsonl(output_path, data)


    def check_fsm_format_and_graph(self, fsm, feedback_count, conversation):
        fb_count = feedback_count * 2
        while True:
            is_valid, message = fsm_utils.validate_fsm(fsm)
            unreachable_states, has_cycle = fsm_utils.check_reachability_and_cycles(fsm)
            if (is_valid and not unreachable_states and has_cycle) or fb_count <= 0:
                break
            prompt = 'The generated FSM has the following issues, please regenerate the FSM:'
            if not is_valid:
                prompt += f'\n### {message}'
            if unreachable_states:
                prompt += f'\n### List of unreachable states: {unreachable_states}'
            if not has_cycle:
                prompt += '\n### The graph composed of states does not have cycles'
            response, conversation = self.multiple_dialogue(prompt, conversation, random_parameters=True)
            fsm = data_utils.extract_fsm(response)
            fb_count -= 1
        return response


    def check_compilation_and_security(self, code, feedback_count, conversation, openzeppelin_path):
        fb_count_1, fb_count_2 = feedback_count, feedback_count
        success_flag = False
        while not success_flag:
            compile_result, compile_info = solidity_utils.compile_solidity(code)
            if not compile_result and fb_count_1 > 0:
                compile_error_prompt = prompt_utils.feedback_by_compile_error_prompt(
                    solidity_utils.extract_solcx_compile_error(str(compile_info))
                )
                response, conversation = self.multiple_dialogue(compile_error_prompt, conversation, random_parameters=True)
                code = data_utils.extract_code(response)
                code = code.replace('@openzeppelin', openzeppelin_path)
                fb_count_1 -= 1
            else:
                check_info = slither_check.check_one_by_slither(code)
                if not (isinstance(check_info, str) and len(check_info) == 0) and fb_count_2 > 0:
                    security_risk_prompt = prompt_utils.feedback_by_security_risk_prompt(check_info)
                    response, conversation = self.multiple_dialogue(security_risk_prompt, conversation, random_parameters=True)
                    fb_count_2 -= 1
                else:
                    success_flag = True
        return response




class Evaluation_gen:
    @staticmethod
    def generate_code_for_effectiveness_and_security(model: _Model, evaluation_path: str, openzeppelin_path: str):
        output_path = model.model + '_use_fsm-scg_for_effectiveness_and_security.jsonl'

        dataset = data_utils.load_jsonl_dataset(evaluation_path)
        
        user_requirement_list = []
        for data in dataset:
            user_requirement_list.append(data['user_requirement'])

        for data in dataset:
            model.generate_use_fsm_scg(user_requirement=data['user_requirement'], version=data['version'], openzeppelin_path=openzeppelin_path, output_path=output_path)