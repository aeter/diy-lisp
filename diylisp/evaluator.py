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
    '+': operator.add,
    '-': operator.sub,
    '/': operator.div,
    '*': operator.mul,
    'mod': operator.mod,
    '>': operator.gt,
}



def evaluate(ast, env):
    """Evaluate an Abstract Syntax Tree in the specified environment."""
    if is_integer(ast) or is_boolean(ast):
        return ast
    if is_atom(ast):
        return env.lookup(ast)
    if is_list(ast):
        first = ast[0]

        if first == 'quote': # quoted expressions are not evaluated
            # 'foo  --> 'foo
            return ast[1]

        if first == 'atom':
            # (atom 5)  --> True
            return is_atom(evaluate(ast[1], env))

        if first == 'eq':
            # (eq (- 2 1) 1)  --> True
            second_evaluated = evaluate(ast[1], env)
            third_evaluated = evaluate(ast[2], env)
            # lists are never equal, only atoms are equal
            return second_evaluated == third_evaluated and not all(
                    [is_list(second_evaluated), is_list(third_evaluated)])

        if first in BASIC_FUNCS:
            # (+ 1 2 3)  --> 6
            try:
                return reduce(BASIC_FUNCS[first], [evaluate(e, env) for e in ast[1:]])
            except TypeError, e:
                raise LispError(e)

        if first == 'if':
            # (if #t 42 1000)  --> 42
            if evaluate(ast[1], env) == True:
                return evaluate(ast[2], env)
            else:
                return evaluate(ast[3], env)

        if first == 'define':
            # (define x 1000) --> env.variables[x] = 1000
            if len(ast) != 3:
                raise LispError('Wrong number of arguments for "define"')
            if not is_symbol(ast[1]): # (define #t 1000)
                raise LispError('Attempt to define a non-symbol')
            if is_list(ast[2]):
                defined = evaluate(ast[2], env)
            else:
                defined = ast[2]
            env.set(ast[1], defined)
            return defined
