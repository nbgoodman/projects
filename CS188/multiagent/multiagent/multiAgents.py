# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newNumFood = successorGameState.getNumFood()
        newFood = currentGameState.getFood().asList()
        newGhostStates = successorGameState.getGhostStates()
        newGhostPositions = successorGameState.getGhostPositions()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        #print newGhostStates
        "*** YOUR CODE HERE ***"
        minghost = 0
        for pos in newGhostPositions:
            minghost += manhattanDistance(newPos, pos)
        mindistance = manhattanDistance(newPos, newFood[0])
        for food in newFood:
            newdistance = manhattanDistance(newPos, food)
            mindistance = min(mindistance, newdistance)
        if newPos == currentGameState.getPacmanPosition():
            return -10000
        if minghost >= 3:
            return -mindistance
        return mindistance - (50 * minghost)

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game

          gameState.isWin():
            Returns whether or not the game state is a winning state

          gameState.isLose():
            Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        # Collect legal moves and successor states
        def getActionReal(self, gameState, depth, agent):
            if depth == 1 and agent == gameState.getNumAgents() - 1:
                legalMoves = gameState.getLegalActions(agent)
                states = [gameState.generateSuccessor(agent, action) for action in legalMoves]
                scores = [self.evaluationFunction(state) for state in states]
                if agent == 0:
                    return max(scores)
                else:
                    return min(scores)
            elif agent == gameState.getNumAgents() - 1:
                legalMoves = gameState.getLegalActions(agent)
                specialstates = []
                specialactions = []
                regularstates = []
                for move in legalMoves:
                    newstate = gameState.generateSuccessor(agent, move)
                    if newstate.isWin() or newstate.isLose():
                        specialstates.append(newstate)
                        specialactions.append(move)
                    else:
                        regularstates.append(newstate)
                scores = [getActionReal(self, state, depth - 1, 0) for state in regularstates]
                if scores == []:
                    scores = [float("inf")]
                specscores = [self.evaluationFunction(specstate) for specstate in specialstates]
                if specscores == []:
                    specscores = [float("inf")]
                return min(min(scores), min(specscores))
            elif agent > 0:
                legalMoves = gameState.getLegalActions(agent)
                specialstates = []
                specialactions = []
                regularstates = []
                for move in legalMoves:
                    newstate = gameState.generateSuccessor(agent, move)
                    if newstate.isWin() or newstate.isLose():
                        specialstates.append(newstate)
                        specialactions.append(move)
                    else:
                        regularstates.append(newstate)
                scores = [getActionReal(self, state, depth, agent + 1) for state in regularstates]
                if scores == []:
                    scores = [float("inf")]
                specscores = [self.evaluationFunction(specstate) for specstate in specialstates]
                if specscores == []:
                    specscores = [float("inf")]
                return min(min(scores), min(specscores))
            elif agent == 0:
                legalMoves = gameState.getLegalActions(agent)
                specialstates = []
                specialactions = []
                regularstates = []
                for move in legalMoves:
                    newstate = gameState.generateSuccessor(agent, move)
                    if newstate.isWin() or newstate.isLose():
                        specialstates.append(newstate)
                        specialactions.append(move)
                    else:
                        regularstates.append(newstate)
                scores = [getActionReal(self, state, depth, agent + 1) for state in regularstates]
                if scores == []:
                    scores = [float("-inf")]
                specscores = [self.evaluationFunction(specstate) for specstate in specialstates]
                if specscores == []:
                    specscores = [float("-inf")]
                return max(max(scores), max(specscores))


        legalMoves = gameState.getLegalActions(0)
        specialstates = []
        specialactions = []
        regularstates = []
        regularactions = []
        for move in legalMoves:
            newstate = gameState.generateSuccessor(0, move)
            if newstate.isWin() or newstate.isLose():
                specialstates.append(newstate)
                specialactions.append(move)
            else:
                regularstates.append(newstate)
                regularactions.append(move)
        compareoptions = [getActionReal(self, randstate, self.depth, 1) for randstate in regularstates]
        bestScore = float('-inf')
        if len(compareoptions) > 0:
            bestScore = max(compareoptions)
        specialscores = [self.evaluationFunction(state) for state in specialstates]
        if specialscores == []:
            specialscores = [float("-inf")]
        bestSpecial = max(specialscores)
        if bestScore < bestSpecial:
            bestIndices = [index for index in range(len(specialscores)) if specialscores[index] == bestSpecial]
            chosenIndex = random.choice(bestIndices) # Pick randomly among the best
            return specialactions[chosenIndex]
        else:
            bestIndices = [index for index in range(len(compareoptions)) if compareoptions[index] == bestScore]
            chosenIndex = random.choice(bestIndices) # Pick randomly among the best
            return regularactions[chosenIndex]


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        def max_value(gameState, depth, agent, a, b):
            v = float("-inf")
            legalMoves = gameState.getLegalActions(agent)
            for move in legalMoves:
                newState = gameState.generateSuccessor(agent, move)
                if agent == gameState.getNumAgents() - 1:
                    v = max(v, value(newState, depth - 1, 0, a, b))
                    if v > b:
                        return v
                    a = max(a,v)
                else:
                    v = max(v, value(newState, depth, agent + 1, a, b))
                    if v > b:
                        return v
                    a = max(a,v)
            return v
        def min_value(gameState, depth, agent, a, b):
            v = float("inf")
            legalMoves = gameState.getLegalActions(agent)
            for move in legalMoves:
                newState = gameState.generateSuccessor(agent, move)
                if agent == gameState.getNumAgents() - 1:
                    v = min(v, value(newState, depth - 1, 0, a, b))
                    if v < a:
                        return v
                    b = min(b,v)
                else:
                    v = min(v, value(newState, depth, agent + 1, a, b))
                    if v < a:
                        return v
                    b = min(b,v)
            return v
        def value(gameState, depth, agent, a, b):
            #print agent
            if gameState.isWin() or gameState.isLose() or (depth == 0 and agent == 0):
                #print gameState.getNumAgents()
                return self.evaluationFunction(gameState)
            elif agent > 0:
                return min_value(gameState, depth, agent, a, b)
            else:
                return max_value(gameState, depth, agent, a, b)
        legalMoves = gameState.getLegalActions(0)
        a = float("-inf")
        b = float("inf")
        scores = []
        for move in legalMoves:
            newstate = gameState.generateSuccessor(0, move)
            score = value(newstate, self.depth, 1, a, b)
            a = max(a, score)

            scores.append(score)
        #scores = [value(gameState.generateSuccessor(0, move), self.depth, 1, float("-inf"), float("-inf")) for move in legalMoves]
        bestscore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestscore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best
        return legalMoves[chosenIndex]

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        def max_value(gameState, depth, agent):
            v = float("-inf")
            legalMoves = gameState.getLegalActions(agent)
            for move in legalMoves:
                newState = gameState.generateSuccessor(agent, move)
                if agent == gameState.getNumAgents() - 1:
                    v = max(v, value(newState, depth - 1, 0))
                else:
                    v = max(v, value(newState, depth, agent + 1))
            return v
        def exp_value(gameState, depth, agent):
            v = 0.0
            legalMoves = gameState.getLegalActions(agent)
            for move in legalMoves:
                newState = gameState.generateSuccessor(agent, move)
                prob = 1.0 / float(len(legalMoves))
                if agent == gameState.getNumAgents() - 1:
                    v += prob * value(newState, depth - 1, 0)
                else:
                    v += prob * value(newState, depth, agent + 1)
            return v
        def value(gameState, depth, agent):
            #print agent
            if gameState.isWin() or gameState.isLose() or (depth == 0 and agent == 0):
                #print gameState.getNumAgents()
                return self.evaluationFunction(gameState)
            elif agent > 0:
                return exp_value(gameState, depth, agent)
            else:
                return max_value(gameState, depth, agent)
        legalMoves = gameState.getLegalActions(0)
        scores = [value(gameState.generateSuccessor(0, move), self.depth, 1) for move in legalMoves]
        bestscore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestscore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best
        return legalMoves[chosenIndex]



def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
      Move evaluation depends on food and ghost position as well as the score.
    """
    Pos = currentGameState.getPacmanPosition()
    NumFood = currentGameState.getNumFood()
    Food = currentGameState.getFood().asList()
    Capsules = currentGameState.getCapsules()
    GhostStates = currentGameState.getGhostStates()
    GhostPositions = currentGameState.getGhostPositions()
    ScaredTimes = [ghostState.scaredTimer for ghostState in GhostStates]
    #print newGhostStates
    "*** YOUR CODE HERE ***"
    minghost = 0
    if len(Food) == 0:
        return 5 * currentGameState.getScore()
    for gpos in GhostPositions:
        minghost += manhattanDistance(Pos, gpos)
    minfood = manhattanDistance(Pos, Food[0])
    for food in Food:
        newdistance = manhattanDistance(Pos, food)
        minfood = min(minfood, newdistance)
    if minghost >= 3 and len(ScaredTimes) == 0:
        return 3 * (1/minfood) + currentGameState.getScore()
    return 2 * (1/minfood) - (20 * minghost) + currentGameState.getScore()

# Abbreviation
better = betterEvaluationFunction
