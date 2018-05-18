# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util
import random
from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        i = 0
        states = self.mdp.getStates()
        while i < self.iterations:
            newvals = []
            for state in states:
                bestaction = self.computeActionFromValues(state)
                if bestaction == None:
                    continue
                else:
                    newvals.append((state, self.computeQValueFromValues(state, bestaction)))
            for (oldstate, newval) in newvals:
                if newval == None:
                    continue
                else:
                    self.values[oldstate] = newval
            i += 1



    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        nextstates_probs = self.mdp.getTransitionStatesAndProbs(state, action)
        total = 0
        for (newstate, prob) in nextstates_probs:
            reward = self.mdp.getReward(state, action, newstate)
            newadd = prob * (reward + (self.discount * self.getValue(newstate)))
            total += newadd
        return total

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        actionlist = self.mdp.getPossibleActions(state)
        valuelist = [self.computeQValueFromValues(state, action) for action in actionlist]
        if valuelist == []:
            return None
        maxvalue = max(valuelist)
        bestIndices = [index for index in range(len(valuelist)) if valuelist[index] == maxvalue]
        chosenIndex = random.choice(bestIndices)
        return actionlist[chosenIndex]



    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        i = 0
        states = self.mdp.getStates()
        j = 0
        while i < self.iterations:
            stateindex = j % len(states)
            state = states[stateindex]
            bestaction = self.computeActionFromValues(state)
            if bestaction == None:
                i += 1
                j += 1
                continue
            else:
                value = self.computeQValueFromValues(state, bestaction)
                if value == None:
                    i += 1
                    j += 1
                    continue
                else:
                    self.values[state] = value
            i += 1
            j += 1

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        i = 0
        states = self.mdp.getStates()
        statedict = {}
        priorities = util.PriorityQueue()
        for thing in states:
            statedict[thing] = set()
        for curstate in states:
            if curstate == 'TERMINAL_STATE':
                continue
            bestaction = self.computeActionFromValues(curstate)
            if bestaction == None:
                continue
            bestScore = self.computeQValueFromValues(curstate, bestaction)
            diff = abs(bestScore - self.values[curstate])
            priorities.push(curstate, -diff)
            for action in self.mdp.getPossibleActions(curstate):
                nextlist = self.mdp.getTransitionStatesAndProbs(curstate, action)
                if nextlist == []:
                    continue
                for (nextstate, prob) in nextlist:
                    if prob > 0:
                        statedict[nextstate].add(curstate)
        while i < self.iterations:
            if priorities.isEmpty():
                break
            poppedstate = priorities.pop()
            bestpoppedaction = self.computeActionFromValues(poppedstate)
            if bestpoppedaction == None:
                continue
            bestpoppedscore = self.computeQValueFromValues(poppedstate, bestpoppedaction)
            self.values[poppedstate] = bestpoppedscore
            for prestate in statedict[poppedstate]:
                bestpreaction = self.computeActionFromValues(prestate)
                if bestpreaction == None:
                    continue
                bestpreScore = self.computeQValueFromValues(prestate, bestpreaction)
                prediff = abs(bestpreScore - self.values[prestate])
                if prediff > self.theta:
                    priorities.update(prestate, -prediff)
            i+=1
