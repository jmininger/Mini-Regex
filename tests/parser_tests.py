import parser
from tokenizer import Tokenizer
from util import nfa_to_table, table_to_nfa
from nfa import NFAState
import unittest as ut


class ParserTest(ut.TestCase):
    def test_concat_merges_two_states_to_one(self):
        a_table = {0: ({'a': 1}, []), 1: ({}, [])}
        a_nfa = table_to_nfa(a_table, 0, 1)
        b_table = {2: ({'b': 3}, []), 3: ({}, [])}
        b_nfa = table_to_nfa(b_table, 2, 3)
        concat_graph = parser.concat(a_nfa, b_nfa)
        actual_table = nfa_to_table(concat_graph.start)
        expected_states = len(a_table.keys()) + len(b_table.keys()) - 1
        self.assertEqual(len(actual_table.keys()), expected_states)

    def test_concat_adds_single_epsilon(self):
        # state 2 is removed by concat, as it is merged with state 1
        expected = {
                0: ({'a': 1}, []),
                1: ({'b': 3}, []),
                3: ({}, [])}
        a_nfa = table_to_nfa({0: ({'a': 1}, []), 1: ({}, [])}, 0, 1)
        b_nfa = table_to_nfa({2: ({'b': 3}, []), 3: ({}, [])}, 2, 3)
        concat_graph = parser.concat(a_nfa, b_nfa)
        actual = nfa_to_table(concat_graph.start)
        self.assertEqual(expected, actual)

    def test_union_adds_2_states(self):
        expected = {
                0: ({'a': 1}, []),
                1: ({}, [5]),
                2: ({'b': 3}, []),
                3: ({}, [5]),
                4: ({}, [0, 2]),
                5: ({}, [])}
        a_nfa = table_to_nfa({0: ({'a': 1}, []), 1: ({}, [])}, 0, 1)
        b_nfa = table_to_nfa({2: ({'b': 3}, []), 3: ({}, [])}, 2, 3)
        id_alloc = CounterStub(4)
        result_nfa = parser.union(a_nfa, b_nfa, id_alloc)
        result = nfa_to_table(result_nfa.start)
        self.assertEqual(expected, result)

    def test_kstar(self):
        a_nfa = table_to_nfa({0: ({'a': 1}, []), 1: ({}, [])}, 0, 1)
        expected = {0: ({'a': 1}, []), 1: ({}, [3, 0]),
                    2: ({}, [0, 3]), 3: ({}, [])}
        id_alloc = CounterStub(2)
        actual_nfa = parser.kstar(a_nfa, id_alloc)
        actual = nfa_to_table(actual_nfa.start)
        self.assertEqual(expected, actual)

    def test_parenthesis_builds_inner_nfa_first(self):
        # Note the difference between "(ab)*" and ab*
        re_parser1 = parser.RegexParser(Tokenizer("(ab)*"))
        nfa1 = re_parser1.construct_nfa()
        table1 = nfa_to_table(nfa1.start)

        re_parser2 = parser.RegexParser(Tokenizer("ab*"))
        nfa2 = re_parser2.construct_nfa()
        table2 = nfa_to_table(nfa2.start)
        self.assertNotEqual(table1, table2)


class CounterStub:
    def __init__(self, start_val):
        self.val = start_val

    def create_id(self):
        val = self.val
        self.val += 1
        return val