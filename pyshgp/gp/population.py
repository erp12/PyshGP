"""
Classes that reperesents Individuals and Populations in evolutionary algorithms.
"""
import math, random
from copy import copy
import numpy as np

from ..utils import keep_number_reasonable, median_absolute_deviation
from ..push import translation as tran
from ..push import interpreter as interp
from ..push import simplification as simp

###########
# Classes #
###########

class Individual:
    """Holds all information about an individual.
	"""

    _genome = None
    _program = None
    _total_error = None
    _error_vector = None

    # Genome
    @property
    def genome(self):
        """Plush Genome of individual.
        """
        return self._genome

    @genome.setter
    def genome(self, value):
        self._genome = value
        self._program = tran.genome_to_program(value)

    # Program
    @property
    def program(self):
        """Push program of individual. Taken from Plush genome.
        """
        return self._program

    @program.setter
    def program(self, value):
        raise AttributeError("Cannot set Individual's program directly. Must \
                             set genome.")

    # Error vector
    @property
    def error_vector(self):
        return self._error_vector

    @error_vector.setter
    def error_vector(self, value):
        self._error_vector = value
        self._total_error = sum(value)

    # Total error
    @property
    def total_error(self):
        return self._total_error

    @total_error.setter
    def total_error(self, value):
        raise AttributeError("Cannot set Individual's total error directly." +
                             " Must set error vector.")

    def __init__(self, genome):
        self.genome = genome

    def __repr__(self):
        return "PyshIndividual<"+str(self.total_error)+">"

    def run_program(self, inputs=None, print_trace=False):
        """Runs the Individual's program.

        :param list inputs: List of input values that can be accessed by the
        Individual's program.
        :param bool print_trace: If true, prints the current program element and
        the state of the stack at each step of executing the program. Defaults
        to False.
        :returns: The final state of the push Interpreter after executing the
        program.
        """
        i = interp.PushInterpreter(inputs)
        i.run_push(self.program, print_trace)
        return i

    def evaluate(self, error_function):
        """Evaluates the individual by passing it's program to the error
        function.

        :param func error_function: The error function.
        """
        errs = error_function(self.program)
        self.error_vector = errs
        return self

    def simplify(self, error_function, steps, verbose=0):
        """Simplifies the individual's program by randomly removing some
        elements of the program and confirming that the total error remains the
        same or lower. This is acheived by silencing some genes in the
        individual's genome.
        """
        simp.auto_simplify(self, error_function, steps, verbose)

class Population(list):
    """Pyshgp population of Individuals.
    """

    def evaluate(self, error_function):
        """Evaluates every individual in the population, if the individual has
        not been previously evaluated.

        :param func error_function: The error function.
        """
        for i in self:
            if i.error_vector is None:
                i.evaluate(error_function)

    def p_evaluate(self, error_function, pool):
        """TODO: Write method docstring.
        """
        evaluated_inds = pool.map(lambda i: i.evaluate(error_function), self)
        for i in range(len(evaluated_inds)):
            self[i] = evaluated_inds[i]

    def select(self, method='lexicase', epsilon='auto', tournament_size=7):
        """Selects a individual from the population with the given selection
        method.

        TODO: Write method docstring.
        """
        if method == 'epsilon_lexicase':
            return self.epsilon_lexicase_selection(epsilon)
        elif method == 'lexicase':
            return self.lexicase_selection()
        elif method == 'tournament':
            return self.tournament_selection(tournament_size)
        else:
            raise ValueError("Unknown selection method: " + str(method))

    def lexicase_selection(self):
        """Returns an individual that does the best on the fitness cases when
        considered one at a time in random order.

        http://faculty.hampshire.edu/lspector/pubs/lexicase-IEEE-TEC.pdf

        Returns
        -------
        individual : Individual
            An individual from the population selected using lexicase selection.
        """
        candidates = self[:]
        cases = list(range(len(self[0].error_vector)))
        random.shuffle(cases)
        while len(cases) > 0 and len(candidates) > 1:
            best_val_for_case = min([ind.error_vector[cases[0]] for ind in candidates])
            candidates = [ind for ind in candidates if ind.error_vector[cases[0]] == best_val_for_case]
            cases.pop(0)
        return random.choice(candidates)

    def epsilon_lexicase_selection(self, epsilon='auto'):
        """Returns an individual that does the best on the fitness cases
        when considered one at a time in random order.

        Parameters
        ----------
        epsilon : {'auto', float, array-like}
            If an individual is within epsilon of being elite, it will
            remain in the selection pool. If 'auto', epsilon is set at
            the start of each selection even to be equal to the
            Median Absolute Deviation of each test case.

        Returns
        -------
        individual : Individual
            An individual from the population selected using lexicase
            selection.
        """
        candidates = self[:]
        cases = list(range(len(self[0].error_vector)))
        random.shuffle(cases)

        if epsilon == 'auto':
            all_errors = np.array([i.error_vector[:] for i in candidates])
            epsilon = np.apply_along_axis(median_absolute_deviation, 0,
                                          all_errors)

        while len(cases) > 0 and len(candidates) > 1:
            case = cases[0]
            errors_this_case = [i.error_vector[case] for i in candidates]
            best_val_for_case = min(errors_this_case)
            if isinstance(epsilon, (list, tuple, np.ndarray)):
                max_error = best_val_for_case + epsilon[case]
            else:
                max_error = best_val_for_case + epsilon
            test = lambda i: i.error_vector[case] <= max_error
            candidates = [i for i in candidates if test(i)]
            cases.pop(0)
        return random.choice(candidates)

    def tournament_selection(self, tournament_size=7):
        """Returns the individual with the lowest error within a random
        tournament.

        Parameters
        ----------
        tournament_size : int
            Size of each tournament.

        Returns
        -------
        individual : Individual
            An individual from the population selected using tournament
            selection.
        """
        tournament = []
        for _ in range(tournament_size):
            tournament.append(random.choice(self[:]))
        min_error_in_tourn = min([ind.total_error for ind in tournament])
        best_in_tourn = [ind for ind in tournament if ind.total_error == min_error_in_tourn]
        return best_in_tourn[0]

    def lowest_error(self):
        """Returns the lowest total error found in the population.
        """
        gnrtr = (ind.total_error for ind in self)
        return np.min(np.fromiter(gnrtr, np.float))

    def average_error(self):
        """Returns the average total error found in the population.
        """
        gnrtr = (ind.total_error for ind in self)
        return np.mean(np.fromiter(gnrtr, np.float))

    def unique(self):
        """Returns the number of unique programs found in the population.
        """
        programs_set = {str(ind.program[:]) for ind in self}
        return len(programs_set)
