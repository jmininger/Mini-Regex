from util import Stack
import bisect


class NFAIterator:
    def __init__(self, substate, age):
        self.substate = substate
        self.age = age

    def __eq__(self, other):
        return self.age == other.age and self.substate.id == other.substate.id

    def __lt__(self, other):
        return self.age < other.age


class DFAState:
    def __init__(self):
        # List of active iterators all sorted by age
        self.partial_states = []

    def add_iterator(self, iter):
        bisect.insort_right(self.partial_states, iter)

    def is_explored(self, substate_id):
        return substate_id in self.explored

    def iterators_at_age(self, age):
        idx = self.partial_states.index(age)
        last_index = len(self.partial_state)\
            - self.partial_states[::-1].index(age)
        return self.partial_states[idx: last_index]

    def get_iterators(self):
        return self.partial_states


class DFASimulator:  # NFARunner?
    def __init__(self, nfa):
        # Constant fields
        self.nfa = nfa
        # Mutable fields
        self.current_age = 0
        self.dfa = DFAState()

        # iterators with ages in this set are invalid
        self.age_restrictions = set()

    def _build_start_iters(self):
        explored = set()
        frontier = Stack()
        closure = []
        for dst in self.nfa.start.epsilon_paths():
            if dst.id not in explored:
                explored.add(dst.id)
                frontier.push(dst)
        while not frontier.is_empty():
            dst = frontier.top()
            frontier.pop()
            closure.append(NFAIterator(dst, self.current_age))
        return closure

    def advance_multi_state(self, input):
        # prevents cycles and the access of nodes already occupied
        explored = set()
        next_state = DFAState()
        match = None
        for iter in self._build_start_iters():
            self.dfa.add_iterator(iter)
        self.dfa.add_iterator(NFAIterator(self.nfa.start, self.current_age))
        for iter in self.dfa.get_iterators():
            print(iter.substate.id)

            # If a match ending with the current char has been found, and if
            # all iterators of the same age have been updated, return the match
            if match and iter.age > match[0]:
                return match

            # Otherwise, begin a depth first search of all nodes reachable from
            # the current state
            frontier = Stack()
            for dst in iter.substate.available_paths(input):
                if dst.id not in explored:
                    explored.add(dst.id)
                    frontier.push(dst)
                    next_state.add_iterator(NFAIterator(dst, iter.age))

                # If a the edge leads to the final state, declare a match
                if dst.id == self.nfa.end.id:
                    for iter.age in range(iter.age+1, self.current_age):
                        self.age_restrictions.append(iter.age)
                    match = (iter.age, self.current_age)

            # Determine the epsilon closure of all destinations advanced from
            # the previous state
            while not frontier.is_empty():
                sub_state = frontier.top()
                frontier.pop()
                free_nodes = sub_state.epsilon_paths()
                for dst in free_nodes:
                    if dst.id not in explored:
                        explored.add(dst.id)
                        frontier.push(dst)
                        next_state.add_iterator(NFAIterator(dst, iter.age))
                        # If the edge leads to the final state, declare a match
                    if dst.id == self.nfa.end.id:
                        for iter.age in range(iter.age+1, self.current_age):
                            self.age_restrictions.append(iter.age)
                        match = (iter.age, self.current_age)

        self.current_age += 1
        self.dfa = next_state
        print([iter.substate.id for iter in self.dfa.get_iterators()])
        return match
        # Have a state container that takes care of the mess and then program
        # to its interface

    def reset(self):
        self.dfa = DFAState()

    def is_active(self):
        return len(self.dfa) != 0
