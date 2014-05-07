# -*- coding: utf-8 -*-

import operator

from types import Environment, LispError, Closure
from ast import is_boolean, is_atom, is_symbol, is_list, is_closure, is_integer
from asserts import assert_exp_length, assert_valid_definition, assert_boolean
from parser import unparse

"""
This is the Evaluator module. The `evaluate` function below is the heart
of your language, and the focus for most of parts 2 through 6.

A score of useful functions is provided for you, as per the above imports, 
making your work a bit easier. (We're supposed to get through this thing 
in a day, after all.)
"""

BASIC_FUNCS = {
    'quote': id, # quoted expressions are not evaluated, but returned as is
    '+': operator.add,
    '-': operator.sub,
    '/': operator.div,
    '*': operator.mul,
    'mod': operator.mod,
    '>': operator.gt,
}


def evaluate(ast, env):
    """Evaluate an Abstract Syntax Tree in the specified environment."""
    if is_atom(ast):
        return env.lookup(ast)
    elif is_list(ast):
        first = ast[0]

        if first == 'atom':
            return is_atom(evaluate(ast[1], env))

        if first == 'eq':
            second_evaluated = evaluate(ast[1], env)
            third_evaluated = evaluate(ast[2], env)
            # lists are never equal, only atoms are equal
            return second_evaluated == third_evaluated and not all(
                    [is_list(second_evaluated), is_list(third_evaluated)])

        if first in BASIC_FUNCS:
            try:
                return reduce(BASIC_FUNCS[first], ast[1:])
            except TypeError, e:
                raise LispError(e)
