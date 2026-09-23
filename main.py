class FiniteStateMachine:
    def __init__(self):
        self.current_state = 'F7'  # Starting state
        self.variables = {'d': 0, 'q': 0, 'u': 0}
        self.seen_methods = set()  # Track successfully executed methods
        self.seen_edges = set()   # Track state transitions
        self.step_count = 0       # Count successful transitions

        # Define the state transition table
        # Format: (current_state, method, condition):
        #         (next_state, output)
        self.transitions = {
            ('F7', 'forge', None): ('F5', 'H1'),

            ('F5', 'etch', 'q==0'): ('F3', 'H2'),
            ('F5', 'etch', 'q==1'): ('F2', 'H4'),

            ('F3', 'slur', None): ('F4', 'H4'),

            ('F4', 'slur', 'd==0'): ('F7', 'H3'),
            ('F4', 'slur', 'd==1'): ('F0', 'H3'),

            ('F0', 'stay', 'u==1'): ('F0', 'H2'),
            ('F0', 'stay', 'u==0'): ('F4', 'H0'),
            ('F0', 'stay', 'u==2'): ('F6', 'H0'),

            ('F6', 'slog', None): ('F1', 'H3'),

            ('F1', 'slur', None): ('F2', 'H1'),
        }

        # Define all known methods in the FSM
        self.known_methods = {'forge', 'slur', 'etch', 'stay', 'slog'}

    def d(self, value):
        """Set variable d"""
        self.variables['d'] = value
        return None

    def q(self, value):
        """Set variable q"""
        self.variables['q'] = value
        return None

    def u(self, value):
        """Set variable u"""
        self.variables['u'] = value
        return None

    def select(self, method):
        """Execute a transition method"""
        if not self._is_valid_method(method):
            return 'unknown'

        valid_transitions = self._find_valid_transitions(method)
        if not valid_transitions:
            return 'unsupported'

        return self._execute_transition(valid_transitions[0], method)

    def _is_valid_method(self, method):
        """Check if method is known in the FSM"""
        return method in self.known_methods

    def _find_valid_transitions(self, method):
        """Find all valid transitions for current state and method"""
        valid_transitions = []
        for key, (next_state, output) in self.transitions.items():
            current_state, trans_method, condition = key
            if self._is_matching_transition(current_state,
                                            trans_method, method):
                if self._satisfies_condition(condition):
                    valid_transitions.append((next_state, output))
        return valid_transitions

    def _is_matching_transition(self, current_state,
                                trans_method, target_method):
        """Check if transition matches current state and target method"""
        return (current_state == self.current_state
                and trans_method == target_method)

    def _satisfies_condition(self, condition):
        """Check if the condition is satisfied"""
        if condition is None:
            return True
        return self._evaluate_condition(condition)

    def _execute_transition(self, transition, method):
        """Execute the transition and update state"""
        next_state, output = transition

        # Record the transition
        self.seen_methods.add(method)
        self.seen_edges.add((self.current_state, next_state))
        self.step_count += 1

        # Update current state
        self.current_state = next_state

        return output

    def _evaluate_condition(self, condition):
        """Evaluate a condition string like 'd==1'"""
        if condition == 'd==0':
            return self.variables['d'] == 0
        elif condition == 'd==1':
            return self.variables['d'] == 1
        elif condition == 'q==0':
            return self.variables['q'] == 0
        elif condition == 'q==1':
            return self.variables['q'] == 1
        elif condition == 'u==0':
            return self.variables['u'] == 0
        elif condition == 'u==1':
            return self.variables['u'] == 1
        else:
            return self.variables['u'] == 2

    def seen_method(self, method):
        """Check if a method has been successfully executed"""
        return method in self.seen_methods

    def seen_edge(self, from_state, to_state):
        """Check if a transition between two states has occurred"""
        return (from_state, to_state) in self.seen_edges

    def get_step(self):
        """Get the number of successful transitions"""
        return self.step_count


def main():
    """Return an instance of the finite state machine"""
    return FiniteStateMachine()


def test():
    """Test the finite state machine with 100% branch coverage"""
    obj = main()

    # Test variable setting
    assert obj.d(1) is None
    assert obj.q(0) is None
    assert obj.u(2) is None

    # Test seen_method before any method calls
    assert obj.seen_method('stay') is False
    assert obj.seen_method('forge') is False

    # Test seen_edge before any transitions
    assert obj.seen_edge('F3', 'F4') is False
    assert obj.seen_edge('F7', 'F5') is False

    # Test initial step count
    assert obj.get_step() == 0

    # Test unsupported method in current state
    assert obj.select('slur') == 'unsupported'

    # Test unknown method
    assert obj.select('look') == 'unknown'
    assert obj.select('march') == 'unknown'
    assert obj.select('stall') == 'unknown'

    # Test successful transitions
    obj.d(0)  # Reset d to 0 for slur transition from F7
    assert obj.select('forge') == 'H1'  # F7->F4 with d=0
    assert obj.get_step() == 1
    assert obj.seen_method('forge') is True
    assert obj.seen_edge('F7', 'F5') is True

    # Test stay transition with u=0 (self-loop)
    obj.q(0)
    assert obj.select('etch') == 'H2'
    assert obj.get_step() == 2
    assert obj.seen_method('etch') is True
    assert obj.seen_edge('F5', 'F3') is True

    assert obj.select('slur') == 'H4'

    # Test slur transition from F4 to F0
    obj.d(1)
    assert obj.select('slur') == 'H3'  # F4->F0 with d=1
    assert obj.get_step() == 4
    assert obj.seen_edge('F4', 'F0') is True

    # Test stay transition with u=2
    obj.u(2)
    assert obj.select('stay') == 'H0'  # F0->F6 with u=2
    assert obj.get_step() == 5
    assert obj.seen_edge('F0', 'F6') is True

    # Test slog transition
    assert obj.select('slog') == 'H3'  # F6->F1
    assert obj.get_step() == 6
    assert obj.seen_method('slog') is True
    assert obj.seen_edge('F6', 'F1') is True

    # Test slur from F1 to F2
    assert obj.select('slur') == 'H1'  # F1->F2
    assert obj.get_step() == 7
    assert obj.seen_edge('F1', 'F2') is True

    # Test unsupported method from F2 (no outgoing transitions)
    assert obj.select('slur') == 'unsupported'
    assert obj.select('stay') == 'unsupported'
    assert obj.select('forge') == 'unsupported'

    # Start new test sequence for other branches
    obj2 = main()
    obj2.d(0)
    obj2.q(1)
    obj2.u(1)

    # Test forge transition from F7
    assert obj2.select('forge') == 'H1'  # F7->F5
    assert obj2.seen_method('forge') is True
    assert obj2.seen_edge('F7', 'F5') is True

    # Test etch with q=1
    assert obj2.select('etch') == 'H4'  # F5->F2 with q=1
    assert obj2.seen_method('etch') is True
    assert obj2.seen_edge('F5', 'F2') is True

    # Start another test sequence for remaining branches
    obj3 = main()
    obj3.d(0)
    obj3.q(0)

    assert obj3.select('forge') == 'H1'  # F7->F5
    assert obj3.select('etch') == 'H2'   # F5->F3 with q=0
    assert obj3.seen_edge('F5', 'F3') is True

    assert obj3.select('slur') == 'H4'   # F3->F4
    assert obj3.seen_edge('F3', 'F4') is True

    # Test stay with u=1 (self-loop in F0)
    obj3.d(1)
    obj3.u(1)
    assert obj3.select('slur') == 'H3'   # F4->F0 with d=1
    assert obj3.select('stay') == 'H2'   # F0->F0 with u=1 (self-loop)
    assert obj3.seen_edge('F0', 'F0') is True

    # Test edge that should not have been seen
    assert obj3.seen_edge('F1', 'F5') is False
    assert obj3.seen_edge('F2', 'F3') is False

    obj4 = main()
    assert obj4.select('slog') == 'unsupported'
    assert obj4.get_step() == 0

    obj4.d(1)
    obj4.q(0)
    obj4.u(0)
    assert obj4.seen_edge('F0', 'F6') is False
    assert obj4.select('stall') == 'unknown'
    assert obj4.select('forge') == 'H1'
    assert obj4.select('etch') == 'H2'

    obj4.q(0)
    assert obj4.seen_method('forge') is True
    assert obj4.select('slur') == 'H4'
    assert obj4.select('slur') == 'H3'
    assert obj4.select('trace') == 'unknown'

    obj4.d(0)
    assert obj4.select('apply') == 'unknown'
    assert obj4.seen_method('forge') is True
    assert obj4.select('sway') == 'unknown'
    assert obj4.select('stay') == 'H0'

# DO NOT ADD THIS TO KISPYTHON.RU !!!!!!!!!
if __name__ == "__main__":
    test()
