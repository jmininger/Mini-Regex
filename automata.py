import unittest as ut


class NFA:
    def __init__(self, graph={}):
        self._transition_table = graph

    def cycle(self, nfa_state, char):
        """ Accepts a NFAState object and an input char,
        and returns the state ...."""
        next_state = NFAState()
        # TODO: Add start state and its epsilon_closure
        for partial_state in nfa_state:
            current_node = partial_state.get_current_node()
            transitions = self._transition_table.get(current_node)
            if transitions[0]:  # input-based transition
                next_state.add([self.spawn_child(transition)
                                for transition in transitions[0]])
            next_state.add([self.spawn_child(epsilon) for epsilon in
                            transitions[1]])
            return next_state

            # get_current_node()
            # NFAState(), NFAState.add(list_of_partialNfastate)
            # partial_state.spawn_child()


class NFAPartialState:
    def __init__(self, start_node=-1):
        self._node = start_node
        self._history = []

    def current_node(self):
        return self._node

    def spawn_child(self, next_state, transition=None):
        child = NFAPartialState(next_state)
        child._history = self._history.copy()
        if transition:
            child._history.append(transition)
        return child

    def history_length(self):
        return len(self._history)


def longer_history(state_iter1, state_iter2):
    if state_iter1.history_length() >= state_iter2.history_length():
        return state_iter1
    else:
        return state_iter2


class PartialStateTest(ut.TestCase):
    def test_spawn_child(self):
        # should not add to history if move to same state
        # should not add to history if epsilon transition
        # should add to history if normal transition
        state = NFAPartialState(0)
        self.assertEqual(state.current_node(), 0)
        state = state.spawn_child(1, 'a')
        self.assertEqual(state.current_node(), 1)
        self.assertEqual(state.history_length(), 1)
        state = state.spawn_child(5)
        self.assertEqual(state.current_node(), 5)
        self.assertEqual(state.history_length(), 1)
        state = state.spawn_child(3, 'a')
        self.assertEqual(state.history_length(), 2)


class NFAState:
    def __init__(self):
        # Key: NodeID, Val: PartialState for node
        # Note, only one state per node id
        # The above strategy becomes an issue when the client wants to match
        #   all possible matches in a string and not just a single one
        self._partial_states = dict()

    def add(self, partials):
        for partial_state in partials:
            node_id = partial_state.current_node()
            if self._partial_states.get(node_id, None):
                # make the above much more pythonic
                conflicting_partial = self._partial_states[node_id]
                self._partial_states[node_id] = \
                    longer_history(conflicting_partial, partial_state)
            else:
                self._partial_states[node_id] = partial_state

    def get(self):
        return self._partial_states


class NFAStateTest(ut.TestCase):
    def test_single_node_per_nfa_state(self):
        state = NFAState()
        partial_mock = NFAPartialState(4)
        partial_mock._history.extend(['a', 'b', 'c'])
        partial_mock2 = NFAPartialState(4)
        partial_mock3 = NFAPartialState(4)
        partial_mock3._history.extend(['a', 'b'])
        partial_states = [partial_mock, partial_mock2]
        state.add(partial_states)
        self.assertEqual(len(state._partial_states), 1)
        self.assertEqual(state._partial_states[4], partial_mock)
        state.add([partial_mock3])
        self.assertEqual(state._partial_states[4], partial_mock)

    def test_get_entire_state(self):
        state = NFAState()
        nfaps0 = NFAPartialState(0)
        nfaps1 = NFAPartialState(1)
        nfaps2 = NFAPartialState(2)
        nfaps3 = NFAPartialState(3)
        nfaps4 = NFAPartialState(4)
        state.add([nfaps0, nfaps1, nfaps2, nfaps3, nfaps4])
        state.add([NFAPartialState(4).spawn_child(3, 'a')])
        state_repr = state.get()
        self.assertEqual([0, 1, 2, 3, 4], list(state_repr.keys()))


class AutomataRunnerTest(ut.TestCase):
    nfa_graph = {  # represents (ab)* | c
            0: ([], [1, 2]),
            1: ([], [3, 7]),
            2: ([('c', 2)], []),
            3: ([('a', 5)], []),
            4: ([], [8]),
            5: ([('b', 6)], []),
            6: ([], [3, 7]),
            7: ([], [8]),
            8: ([], []),
    }

    def test_cycles_state(self):
        nfa = NFA(self.nfa_graph)
        start_state = NFAState()
        state = nfa.cycle(start_state, '')
        active_nodes = state.get_node_ids()
        self.assertEqual(set(0, 1, 2, 3, 7, 8), active_nodes)
        # nfa(graph), nfa_simulator(state) has nfa, nfa takes a state and
        # returns next state...state object, in charge of ensuring elem act as
        # a set, also a partial state object...

# class AutomataTest(ut.TestCase):
#     def test_single_cycle(self):
#         nfa_graph = {  # represents (ab)* | c
#                 0: ([], [1, 2]),
#                 1: ([], [3, 7]),
#                 2: ([('c', 2)], []),
#                 3: ([('a', 5)], []),
#                 4: ([], [8]),
#                 5: ([('b', 6)], []),
#                 6: ([], [3, 7]),
#                 7: ([], [8]),
#                 8: ([], []),
#         }
#         nfa = NFA(graph=nfa_graph)
#         nfa._transitions = nfa_graph
#         nfa.cycle('abe')
#         current_state = nfa.get_state()
#         self.assertEqual(current_state, set([1, 2]))
#         nfa.reset()
#         nfa.cycle('i am barry')


if __name__ == '__main__':
    ut.main()
