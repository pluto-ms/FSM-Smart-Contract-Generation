import networkx as nx

class fsm_utils:

    @staticmethod
    def validate_fsm(fsm_data):
        states = {state["name"] for state in fsm_data["states"]}
        initial_state = fsm_data["initialState"]

        # Check if the initial state exists
        if initial_state not in states:
            return False, f"Initial state {initial_state} does not exist in the state list."

        # Check if all transition targets are valid
        for state in fsm_data["states"]:
            for transition in state.get("transitions", []):
                target = transition["target"]
                if target not in states:
                    return False, f"The target {target} of state {state['name']} is invalid."

        # Check if all triggers are defined in the event list
        valid_triggers = set(fsm_data.get("events", []))
        for state in fsm_data["states"]:
            for transition in state.get("transitions", []):
                trigger = transition["trigger"]
                if trigger not in valid_triggers:
                    return False, f"The trigger {trigger} of state {state['name']} is not defined in the event list."

        return True, "FSM validation passed"



    @staticmethod
    def check_reachability_and_cycles(fsm_data):
        G = nx.DiGraph()
        initial_state = fsm_data["initialState"]
        
        # Add states and transitions to the graph
        for state in fsm_data["states"]:
            for transition in state["transitions"]:
                G.add_edge(state["name"], transition["target"])
        
        # Check if all states are reachable from the initial state
        reachable_nodes = nx.descendants(G, initial_state) | {initial_state}
        all_states = {state["name"] for state in fsm_data["states"]}
        unreachable_states = all_states - reachable_nodes
        
        # Check for cycles in the graph
        has_cycle = nx.is_directed_acyclic_graph(G) == False
        
        return unreachable_states, has_cycle
