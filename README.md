# Guiding LLM-based Smart Contract Generation with Finite State Machine

Our **Smart-Contract-MultiTask-Dataset** is available at here: https://drive.google.com/uc?export=download&id=1PMI__bgB1TRiSdDZOvvLZlr32S9IBNZ9

## Abstract
Smart contract is a kind of self-executing code based on blockchain technology with a wide range of application scenarios, but the traditional generation method relies on manual coding and expert auditing, which has a high threshold and low efficiency. Although Large Language Models (LLMs) show great potential in programming tasks, they still face challenges in smart contract generation w.r.t. effectiveness and security. To solve these problems, we propose FSM-SCG, a smart contract generation framework based on finite state machine (FSM) and LLMs, which significantly improves the quality of the generated code by abstracting user requirements to generate FSM, guiding LLMs to generate smart contracts, and iteratively optimizing the code with the feedback of compilation and security checks.
The experimental results show that FSM-SCG significantly improves the quality of smart contract generation. Compared to the best baseline, FSM-SCG improves the compilation success rate of generated smart contract code by at most 48%, and reduces the average vulnerability risk score by approximately 68%.

## Architecture
![arch](https://github.com/user-attachments/assets/394f1ea0-c695-4168-a8ae-0fe804d8eab5)


Three key elements involved in the smart contract generation process: Requirement, FSM, and Smart Contract.
![r_f_c](https://github.com/user-attachments/assets/bfe94708-5f79-4ff2-acb4-e4571c38f239)
