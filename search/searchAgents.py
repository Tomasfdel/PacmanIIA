# -*- coding: utf-8 -*-

# searchAgents.old.py
# -------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"""
This file contains all of the agents that can be selected to
control Pacman.  To select an agent, use the '-p' option
when running pacman.py.  Arguments can be passed to your agent
using '-a'.  For example, to load a SearchAgent that uses
depth first search (dfs), run the following command:

> python pacman.py -p SearchAgent -a searchFunction=depthFirstSearch

Commands to invoke other search strategies can be found in the
project description.

Please only change the parts of the file you are asked to.
Look for the lines that say

"*** YOUR CODE HERE ***"

The parts you fill in start about 3/4 of the way down.  Follow the
project description for details.

Good luck and happy searching!
"""
from game import Directions
from game import Agent
from game import Actions
from util import *

import time
import search
import searchAgents

class GoWestAgent(Agent):
    "An agent that goes West until it can't."

    def getAction(self, state):
        "The agent receives a GameState (defined in pacman.py)."
        if Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        else:
            return Directions.STOP

#######################################################
# This portion is written for you, but will only work #
#       after you fill in parts of search.py          #
#######################################################

class SearchAgent(Agent):
    """
    This very general search agent finds a path using a supplied search algorithm for a
    supplied search problem, then returns actions to follow that path.

    As a default, this agent runs DFS on a PositionSearchProblem to find location (1,1)

    Options for fn include:
      depthFirstSearch or dfs
      breadthFirstSearch or bfs


    Note: You should NOT change any code in SearchAgent
    """

    def __init__(self, fn='depthFirstSearch', prob='PositionSearchProblem', heuristic='nullHeuristic'):
        # Warning: some advanced Python magic is employed below to find the right functions and problems

        # Get the search function from the name and heuristic
        if fn not in dir(search):
            raise AttributeError, fn + ' is not a search function in search.py.'
        func = getattr(search, fn)
        if 'heuristic' not in func.func_code.co_varnames:
            print('[SearchAgent] using function ' + fn)
            self.searchFunction = func
        else:
            if heuristic in dir(searchAgents):
                heur = getattr(searchAgents, heuristic)
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            else:
                raise AttributeError, heuristic + ' is not a function in searchAgents.py or search.py.'
            print('[SearchAgent] using function %s and heuristic %s' % (fn, heuristic))
            # Note: this bit of Python trickery combines the search algorithm and the heuristic
            self.searchFunction = lambda x: func(x, heuristic=heur)

        # Get the search problem type from the name
        if prob not in dir(searchAgents) or not prob.endswith('Problem'):
            raise AttributeError, prob + ' is not a search problem type in SearchAgents.py.'
        self.searchType = getattr(searchAgents, prob)
        print('[SearchAgent] using problem type ' + prob)

    def registerInitialState(self, state):
        """
        This is the first time that the agent sees the layout of the game board. Here, we
        choose a path to the goal.  In this phase, the agent should compute the path to the
        goal and store it in a local variable.  All of the work is done in this method!

        state: a GameState object (pacman.py)
        """
        if self.searchFunction == None: raise Exception, "No search function provided for SearchAgent"
        starttime = time.time()
        problem = self.searchType(state) # Makes a new search problem
        self.actions  = self.searchFunction(problem) # Find a path
        totalCost = problem.getCostOfActions(self.actions)
        print('Path found with total cost of %d in %.1f seconds' % (totalCost, time.time() - starttime))
        if '_expanded' in dir(problem): print('Search nodes expanded: %d' % problem._expanded)

    def getAction(self, state):
        """
        Returns the next action in the path chosen earlier (in registerInitialState).  Return
        Directions.STOP if there is no further action to take.

        state: a GameState object (pacman.py)
        """
        if 'actionIndex' not in dir(self): self.actionIndex = 0
        i = self.actionIndex
        self.actionIndex += 1
        if i < len(self.actions):
            return self.actions[i]
        else:
            return Directions.STOP

class PositionSearchProblem(search.SearchProblem):
    """
    A search problem defines the state space, start state, goal test,
    successor function and cost function.  This search problem can be
    used to find paths to a particular point on the pacman board.

    The state space consists of (x,y) positions in a pacman game.

    Note: this search problem is fully specified; you should NOT change it.
    """

    def __init__(self, gameState, costFn = lambda x: 1, goal=(1,1), start=None, warn=True):
        """
        Stores the start and goal.

        gameState: A GameState object (pacman.py)
        costFn: A function from a search state (tuple) to a non-negative number
        goal: A position in the gameState
        """
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        if start != None: self.startState = start
        self.goal = goal
        self.costFn = costFn
        if warn and (gameState.getNumFood() != 1 or not gameState.hasFood(*goal)):
            print 'Warning: this does not look like a regular search maze'

        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal

        # For display purposes only
        if isGoal:
            self._visitedlist.append(state)
            import __main__
            if '_display' in dir(__main__):
                if 'drawExpandedCells' in dir(__main__._display): #@UndefinedVariable
                    __main__._display.drawExpandedCells(self._visitedlist) #@UndefinedVariable

        return isGoal

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append( ( nextState, action, cost) )

        # Bookkeeping for display purposes
        self._expanded += 1
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999
        """
        if actions == None: return 999999
        x,y= self.getStartState()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x,y))
        return cost

class StayEastSearchAgent(SearchAgent):
    """
    An agent for position search with a cost function that penalizes being in
    positions on the West side of the board.

    The cost function for stepping into a position (x,y) is 1/2^x.
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: .5 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn)

class StayWestSearchAgent(SearchAgent):
    """
    An agent for position search with a cost function that penalizes being in
    positions on the East side of the board.

    The cost function for stepping into a position (x,y) is 2^x.
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: 2 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn)

def manhattanHeuristic(position, problem, info={}):
    "The Manhattan distance heuristic for a PositionSearchProblem"
    xy1 = position
    xy2 = problem.goal
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

def euclideanHeuristic(position, problem, info={}):
    "The Euclidean distance heuristic for a PositionSearchProblem"
    xy1 = position
    xy2 = problem.goal
    return ( (xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2 ) ** 0.5

#####################################################
# This portion is incomplete.  Time to write code!  #
#####################################################

class CornersProblem(search.SearchProblem):
    """
    This search problem finds paths through all four corners of a layout.

    You must select a suitable state space and successor function
    """

    def __init__(self, startingGameState, costFn = lambda x: 1): #agregamos costFn
        """
        Stores the walls, pacman's starting position and corners.
        """
        self.walls = startingGameState.getWalls()
        self.startingPosition = startingGameState.getPacmanPosition()
        top, right = self.walls.height-2, self.walls.width-2
        self.corners = ((1,1), (1,top), (right, 1), (right, top))
        for corner in self.corners:
            if not startingGameState.hasFood(*corner):
                print 'Warning: no food in corner ' + str(corner)
        self._expanded = 0 # Number of search nodes expanded

        #*** YOUR CODE HERE ***
        #Agregamos el campo "función de costo asociado a un nodo".
        self.costFn = costFn


    def getStartState(self):
        """
        Returns the start state (in your state space, not the full Pacman state space)
        """
        #*** YOUR CODE HERE ***
        #Estructuramos una tupla que sean las esquinas que aún no hayamos recorrido
        remainingCorners = tuple(x for x in self.corners if x != self.startingPosition)
        return (self.startingPosition, remainingCorners)
        
        
    def isGoalState(self, state):
        """
        Returns whether this search state is a goal state of the problem
        """
        #"*** YOUR CODE HERE ***"
        #Preguntamos si recorrimos todas las esquinas y devolvemos acorde.
        return state[1] == ()

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """

        currentPosition = state[0] #Posicion actual
        remainingCorners = state[1] #Esquinas restantes
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = currentPosition
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            hitsWall = self.walls[nextx][nexty]

            #*** YOUR CODE HERE ***
            #Realizamos un movimiento y corroboramos las esquinas que faltan recorrer. 
            if not hitsWall:
                nextPosition = (nextx, nexty)
                newCorners = tuple(x for x in remainingCorners if x != nextPosition)
                cost = self.costFn(nextPosition)
                successors.append( ((nextPosition, newCorners), action, cost) )
                
        self._expanded += 1
        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999.  This is implemented for you.
        """
        if actions == None: return 999999
        x,y= self.startingPosition
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
        return len(actions)


# Función auxiliar para la heurística del cornersProblem.
# Dada una posición y una tupla de objetivos, devuelve la longitud
# del camino mínimo que parte de la posición y recorre todos los objetivos.
def MinimumPathLength(currentPosition, remainingCorners):
    if(remainingCorners == ()):
        return 0;
    
    distances = []
    for target in remainingCorners:
        cornersWithoutTarget = tuple(x for x in remainingCorners if x != target)
        subpathLength = MinimumPathLength(target, cornersWithoutTarget)
        distances = distances + [subpathLength + manhattanDistance(currentPosition, target)]
    
    return min(distances)


def cornersHeuristic(state, problem):
    """
    A heuristic for the CornersProblem that you defined.

      state:   The current search state
               (a data structure you chose in your search problem)

      problem: The CornersProblem instance for this layout.

    This function should always return a number that is a lower bound
    on the shortest path from the state to a goal of the problem; i.e.
    it should be admissible (as well as consistent).
    """
    corners = problem.corners # These are the corner coordinates
    walls = problem.walls # These are the walls of the maze, as a Grid (game.py)

    "*** YOUR CODE HERE ***"
    # Se detallan los intentos sucesivos que tuvimos en la búsqueda de una heurística adecuada.
    # En todas las situaciones partimos del problema relajado al no considerar que haya paredes en el laberinto.
    # Se agregan para cada caso las estadísticas dadas para tinyCorners, mediumCorners y bigCorners.
    
    """
    # PRIMER INTENTO
    # Función heurística: Mínima distancia Manhattan a una esquina no visitada.
    # La función es admisible, pero no es muy buena. Se terminan expandiendo
    # demasiados nodos.
 
    #         Costo    Nodos_expandidos
    # Tiny:   28       226
    # Medium: 106      1491
    # Big:    162      5862

    remainingCorners = state[1]
    if(remainingCorners == ()):
        return 0
    
    currentPos = state[0]    
    
    return min(manhattanDistance(currentPos, corner) for corner in remainingCorners)
    """
    
    """
    # SEGUNDO INTENTO
    # Función heurística: Suma de distancias Euclídeas a todas las esquinas no visitadas.
    # Si bien presenta una mejora en la cantidad de nodos expandidos
    # sin ser tan compleja computacionalmente, vimos que la heurística no es admisible
    # pues, por ejemplo, sobreestima el costo de ruta si quedan dos esquinas para visitar
    # y nos encontramos en una tercer esquina.
    # En este caso, se forma un triángulo rectángulo entre nuestra posición y los objetivos,
    # y la heurística devuelve un costo de ruta mayor (un cateto + hipotenusa) que la ruta óptima
    # (un cateto + el otro cateto).
    
    #         Costo   Nodos_expandidos
    # Tiny:   28      182
    # Medium: 106     722
    # Big:    166     2681    (Vemos que devuelve un costo de ruta subóptimo)
    
    remainingCorners = state[1]
    if(remainingCorners == ()):
        return 0
    
    currentPos = state[0]    
    
    return sum((euclideanDistance(currentPos, corner)) for corner in remainingCorners)
    """
    
    """
    # TERCER INTENTO
    # Función heurística: Suma de distancias Manhattan recorriendo las esquinas restantes de una forma greedy.
    # Agregando un poco de procesamiento, podemos llegar a una función que mejora el rendimiento de una manera 
    # notable. Sin embargo, encontramos que en un caso muy peculiar la función también sobreestimaría el costo de ruta,
    # haciéndola no admisible en casos particulares.
    
    #         Costo   Nodos_expandidos
    # Tiny:   28      155
    # Medium: 106     692
    # Big:    162     1740
    
    remainingCorners = state[1]
    currentPos = state[0]
    currentSum = 0
    while(remainingCorners != ()):
        nextCornerAndDist = min([(x, manhattanDistance(x, currentPos)) for x in remainingCorners], key = lambda x: x[1])
        remainingCorners = tuple(x for x in remainingCorners if x != nextCornerAndDist[0])
        currentSum = currentSum + nextCornerAndDist[1]
        currentPos = nextCornerAndDist[0]
    
    return currentSum
    """
    
    # CUARTO INTENTO
    # Función heurística: Cantidad de desplazamientos necesarios para recorrer las esquinas restantes de manera óptima.
    # Aprovechando que el problema requiere siempre recorrer a lo sumo cuatro puntos, creemos que podemos demandar
    # un poco más de procesamiento y llegar a una heurística con las bondades del caso anterior, pero que se mantenga admisible.
    # Vemos que expande más nodos en los casos pequeños, pero la misma cantidad en el más grande. 
    
    #         Costo   Nodos_expandidos
    # Tiny:   28      159
    # Medium: 106     741
    # Big:    162     1740
    
    return MinimumPathLength(state[0], state[1])
    
    
    
    
    
    
class AStarCornersAgent(SearchAgent):
    "A SearchAgent for FoodSearchProblem using A* and your foodHeuristic"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, cornersHeuristic)
        self.searchType = CornersProblem

class FoodSearchProblem:
    """
    A search problem associated with finding the a path that collects all of the
    food (dots) in a Pacman game.

    A search state in this problem is a tuple ( pacmanPosition, foodGrid ) where
      pacmanPosition: a tuple (x,y) of integers specifying Pacman's position
      foodGrid:       a Grid (see game.py) of either True or False, specifying remaining food
    """
    def __init__(self, startingGameState):
        self.start = (startingGameState.getPacmanPosition(), startingGameState.getFood())
        self.walls = startingGameState.getWalls()
        self.startingGameState = startingGameState
        self._expanded = 0
        self.heuristicInfo = {} # A dictionary for the heuristic to store information

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state[1].count() == 0

    def getSuccessors(self, state):
        "Returns successor states, the actions they require, and a cost of 1."
        successors = []
        self._expanded += 1
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextFood = state[1].copy()
                nextFood[nextx][nexty] = False
                successors.append( ( ((nextx, nexty), nextFood), direction, 1) )
        return successors

    def getCostOfActions(self, actions):
        """Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999"""
        x,y= self.getStartState()[0]
        cost = 0
        for action in actions:
            # figure out the next state and see whether it's legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost

class AStarFoodSearchAgent(SearchAgent):
    "A SearchAgent for FoodSearchProblem using A* and your foodHeuristic"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, foodHeuristic)
        self.searchType = FoodSearchProblem

# Dada la grilla de posiciones de comida, devolvemos una lista con las coordenadas
# de cada una de ellas.
def GridToList(foodGrid):
    foodList = []
    for (x, column) in enumerate(foodGrid):
        for (y, hasFood) in enumerate (column):
            if(hasFood):
                foodList = foodList + [(x, y)]
    return foodList

# Función auxiliar del algoritmo de Kruskal.
# Dado un vértice, devuelve la raíz del subárbol al que pertenece.
def findParent(parent, vertex):
    if parent[vertex] == vertex:
        return vertex
    return findParent(parent, parent[vertex])

# Función auxiliar del algoritmo de Kruskal.
# Dados dos vértices, combina los subárboles a los que pertenece cada uno.
def union(parent, rank, firstRoot, secondRoot):
    if(rank[firstRoot] < rank[secondRoot]):
        parent[firstRoot] = secondRoot
    elif(rank[firstRoot] > rank[secondRoot]):
        parent[secondRoot] = firstRoot
    else:
        parent[secondRoot] = firstRoot
        rank[firstRoot] += 1
    
# Algoritmo de Kruskal para encontrar el árbol recubridor minimal del grafo
# pasado como argumento.
def kruskalWeight(edges, numVertices):
    
    edges = sorted(edges, key = lambda x: x[2])
    
    parent = []
    rank = []
    
    for index in range(numVertices):
        parent.append(index)
        rank.append(0)
    
    edgeCounter = 0
    edgeIndex = 0
    weightSum = 0
    
    while edgeCounter < numVertices - 1:
        firstV, secondV, distance = edges[edgeIndex]
        edgeIndex = edgeIndex + 1
        
        firstParent = findParent(parent, firstV)
        secondParent = findParent(parent, secondV) 
        
        if firstParent != secondParent:
            edgeCounter = edgeCounter + 1
            weightSum = weightSum + distance
            union(parent, rank, firstParent, secondParent)
    
    return weightSum
    
    
# Dada la lista de posiciones, construimos una lista de aristas del grafo.
# Para ello, las renombramos para que sean de la forma [0, 1, ..., listLength - 1].
# Si ambos vértices son puntos de comida, ya calculamos su distancia en el laberinto,
# por lo que utilizamos ese valor como peso del arista. 
# Si no, uno de los elementos es la posición del jugador, con lo que 
# simplemente utilizamos la distancia Manhattan entre ambos puntos.
def minSpanTreeWeight(vertices, distanceDict):
    edges = []
    firstIndex = 0
    listLength = len(vertices)
    
    while(firstIndex < listLength - 1):
        firstP = vertices[firstIndex]
        secondIndex = firstIndex + 1
        while(secondIndex < listLength):
            secondP = vertices[secondIndex]
            if( (firstP, secondP) in distanceDict):
                edges = edges + [(firstIndex, secondIndex, distanceDict[(firstP, secondP)])]
            else:
                edges = edges + [(firstIndex, secondIndex, manhattanDistance(firstP, secondP))]
            secondIndex = secondIndex + 1
        firstIndex = firstIndex + 1
            
    return kruskalWeight(edges, listLength)


# Dada la lista inicial de posiciones de comida, se genera un diccionario que dice
# la distancia en el laberinto para cada par de puntos.
# Esta función llama a un BFS para cada par de puntos, lo que podría optimizarse
# llamando a un BFS por punto y calculando las distancias a todos los demás
# en un único llamado. Sin embargo, eso requeriría redefinir toda la parte de BFS
# específicamente para el problema, con lo cual dejamos esta implementación.
def fillMazeDistances(foodList, problem):
    distances = {}
    firstIndex = 0
    listLength = len(foodList)
    
    while(firstIndex < listLength - 1):
        firstP = foodList[firstIndex]
        secondIndex = firstIndex + 1
        while(secondIndex < listLength):
            secondP = foodList[secondIndex]
            pointsDistance = mazeDistance(firstP, secondP, problem.startingGameState)
            distances[(firstP, secondP)] = pointsDistance
            distances[(secondP, firstP)] = pointsDistance
            secondIndex = secondIndex + 1
        firstIndex = firstIndex + 1
    
    return distances


def foodHeuristic(state, problem):
    """
    Your heuristic for the FoodSearchProblem goes here.

    This heuristic must be consistent to ensure correctness.  First, try to come up
    with an admissible heuristic; almost all admissible heuristics will be consistent
    as well.

    If using A* ever finds a solution that is worse uniform cost search finds,
    your heuristic is *not* consistent, and probably not admissible!  On the other hand,
    inadmissible or inconsistent heuristics may find optimal solutions, so be careful.

    The state is a tuple ( pacmanPosition, foodGrid ) where foodGrid is a
    Grid (see game.py) of either True or False. You can call foodGrid.asList()
    to get a list of food coordinates instead.

    If you want access to info like walls, capsules, etc., you can query the problem.
    For example, problem.walls gives you a Grid of where the walls are.

    If you want to *store* information to be reused in other calls to the heuristic,
    there is a dictionary called problem.heuristicInfo that you can use. For example,
    if you only want to count the walls once and store that value, try:
      problem.heuristicInfo['wallCount'] = problem.walls.count()
    Subsequent calls to this heuristic can access problem.heuristicInfo['wallCount']
    """
    position, foodGrid = state
    "*** YOUR CODE HERE ***"
    # Función heurística: Suma de los pesos de las aristas del Árbol Recubridor Minimal
    # (Minimum Spanning Tree) formado por los puntos faltantes y la posición actual,
    # tomando como pesos de las aristas la distancia en el laberinto entre los puntos involucrados.
    # Sabemos que la función es admisible: El objetivo es encontrar un camino Hamiltoniano
    # de suma de pesos de arista mínimos con los vértices antes descriptos. Un camino Hamiltoniano
    # es un árbol recubridor del grafo, con lo cual el árbol recubridor minimal siempre tendrá
    # una suma de pesos de aristas menor o igual a la cantidad de movimientos que necesitaríamos
    # para recorrer el camino óptimo.
    # Para calcular el valor de la heurística, construimos el grafo antes descripto calculando las 
    # distancias entre todos los vértices. Luego, generamos un árbol recubridor minimal 
    # usando el algoritmo de Kruskal y retornamos la suma de los pesos de las aristas elegidas.
    
    # Generamos una lista de todos los puntos con comida.
    foodList = GridToList(foodGrid)
    
    # Precalculamos las distancias en el laberinto entre cada par de puntos con comida.
    if(len(problem.heuristicInfo) == 0):
        problem.heuristicInfo = fillMazeDistances(foodList, problem)
    
    # Calculamos el peso del árbol recubridor minimal, pasando como vertices
    # las coordenadas de la comida restante junto con la posición actual,
    # además de las distancias entre comidas en el laberinto.
    return minSpanTreeWeight(foodList + [position], problem.heuristicInfo)
    
    
class ClosestDotSearchAgent(SearchAgent):
    "Search for all food using a sequence of searches"
    def registerInitialState(self, state):
        self.actions = []
        currentState = state
        while(currentState.getFood().count() > 0):
            nextPathSegment = self.findPathToClosestDot(currentState) # The missing piece
            self.actions += nextPathSegment
            for action in nextPathSegment:
                legal = currentState.getLegalActions()
                if action not in legal:
                    t = (str(action), str(currentState))
                    raise Exception, 'findPathToClosestDot returned an illegal move: %s!\n%s' % t
                currentState = currentState.generateSuccessor(0, action)
        self.actionIndex = 0
        print 'Path found with cost %d.' % len(self.actions)

    def findPathToClosestDot(self, gameState):
        "Returns a path (a list of actions) to the closest dot, starting from gameState"
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition()
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState)

        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

class AnyFoodSearchProblem(PositionSearchProblem):
    """
      A search problem for finding a path to any food.

      This search problem is just like the PositionSearchProblem, but
      has a different goal test, which you need to fill in below.  The
      state space and successor function do not need to be changed.

      The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
      inherits the methods of the PositionSearchProblem.

      You can use this search problem to help you fill in
      the findPathToClosestDot method.
    """

    def __init__(self, gameState):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test
        that will complete the problem definition.
        """
        x,y = state

        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

##################
# Mini-contest 1 #
##################

class ApproximateSearchAgent(Agent):
    "Implement your contest entry here.  Change anything but the class name."

    def registerInitialState(self, state):
        "This method is called before any moves are made."
        "*** YOUR CODE HERE ***"

    def getAction(self, state):
        """
        From game.py:
        The Agent will receive a GameState and must return an action from
        Directions.{North, South, East, West, Stop}
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def mazeDistance(point1, point2, gameState):
    """
    Returns the maze distance between any two points, using the search functions
    you have already built.  The gameState can be any game state -- Pacman's position
    in that state is ignored.

    Example usage: mazeDistance( (2,4), (5,6), gameState)

    This might be a useful helper function for your ApproximateSearchAgent.
    """
    x1, y1 = point1
    x2, y2 = point2
    walls = gameState.getWalls()
    assert not walls[x1][y1], 'point1 is a wall: ' + point1
    assert not walls[x2][y2], 'point2 is a wall: ' + str(point2)
    prob = PositionSearchProblem(gameState, start=point1, goal=point2, warn=False)
    return len(search.bfs(prob))
