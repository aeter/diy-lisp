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

        if is_list(first):
            # evaluate lambda functions directly -> ((lambda (x) x) 42) -> 42
            closure = evaluate(first, env)
            return evaluate_closure(closure, ast[1:], env)

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
            defined = evaluate(ast[2], env)
            env.set(ast[1], defined)
            return defined

        if first == 'cons':
            return [evaluate(ast[1], env)] + evaluate(ast[2], env)

        if first == 'head':
            the_list = evaluate(ast[1], env)
            if len(the_list) == 0:
                raise LispError('cannot get first element from empty list')
            return the_list[0] 

        if first == 'tail':
            the_list = evaluate(ast[1], env)
            return the_list[1:]

        if first == 'empty':
            the_list = evaluate(ast[1], env)
            return len(the_list) == 0

        if first == 'print':
            print evaluate(ast[1], env)
            return 'nil'

        if first == 'lambda':
            if not is_list(ast[1]):
                raise LispError('lambda arguments not in a list')
            if len(ast) != 3:
                raise LispError('Wrong number of arguments for lambda')
            return Closure(env, ast[1], ast[2])

        if is_closure(first):
            return evaluate_closure(first, ast[1:], env)

        if is_symbol(first) and is_closure(env.lookup(first)):
            # (define add (lambda (x y) (+ x y))) -> {'add': <closure 1234>}
            return evaluate_closure(env.lookup(first), ast[1:], env)

        # A bad call -> (#t 'foo 'bar') or (42 'foo), etc.
        raise LispError('not a function')


def evaluate_closure(closure, params, env):
    if len(closure.params) != len(params):
        raise LispError('wrong number of arguments, expected %d got %d' % (
            len(closure.params), len(params)))
    # evaluate each param passed to the closure
    params_values = []
    for p in params:
        if is_list(p):
            params_values.append(evaluate(p, env))
        else:
            params_values.append(p)
    local_fn_params = dict(zip(closure.params, params_values))
    # use variables from the environment when the closure was defined
    local_fn_params.update(closure.env.variables)
    new_env = env.extend(local_fn_params)
    return evaluate(closure.body, new_env)

