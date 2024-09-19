# INFORMATION ------------------------------------------------------------------------------------------------------- #


# Author:  Steven Spratley
# Date:    04/01/2021
# Purpose: Implements an example breadth-first search agent for the COMP90054 competitive game environment.


# IMPORTS AND CONSTANTS ----------------------------------------------------------------------------------------------#


import time, random
from Azul.azul_model import AzulGameRule as GameRule
from copy import deepcopy
from collections import deque

THINKTIME   = 0.9
NUM_PLAYERS = 2


# FUNCTIONS ----------------------------------------------------------------------------------------------------------#


# Defines this agent.
class myAgent():
    def __init__(self, _id):
        self.id = _id # Agent needs to remember its own id.
        self.game_rule = GameRule(NUM_PLAYERS) # Agent stores an instance of GameRule, from which to obtain functions.
        # More advanced agents might find it useful to not be bound by the functions in GameRule, instead executing
        # their own custom functions under GetActions and DoAction.
        self.turn_count = 0
    # Generates actions from this state.
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)
    
    # Carry out a given action on this state and return True if goal is reached received.
    def DoAction(self, state, action):
        new_state = self.game_rule.generateSuccessor(state, action, self.id)
        
        self._place_tiles(new_state, action)
        
        goal_reached = self._check_round_end(new_state)
        
        if goal_reached:
            self._end_round(new_state)
        
        return goal_reached

    def _place_tiles(self, state, action):
        if action.action_type == 'TAKE_FROM_FACTORY':
            factory = state.factories[action.factory_id]
            color = action.tile_type
            state.agents[self.id].pattern_lines[action.pattern_line_dest].extend([t for t in factory.tiles if t == color])
            # 将其他颜色的瓷砖移到中心
            state.center_pool.extend([t for t in factory.tiles if t != color])
            factory.tiles.clear()
        elif action.action_type == 'TAKE_FROM_CENTER':
            color = action.tile_type
            state.agents[self.id].pattern_lines[action.pattern_line_dest].extend([t for t in state.center_pool if t == color])
            # 从中心移除这些瓷砖
            state.center_pool = [t for t in state.center_pool if t != color]

    def _check_round_end(self, state):
        factories_empty = all(len(factory.tiles) == 0 for factory in state.factories)

        center_empty = len(state.center_pool) == 0
        
        # 如果所有工厂和中心区域都为空，则回合结束
        return factories_empty and center_empty

    def _end_round(self, state):
        for agent in state.agents:
            self._wall_tiling(agent)
            self._calculate_score(agent)
        self._refill_factories(state)

    def _wall_tiling(self, agent):
        for i, line in enumerate(agent.pattern_lines):
            if len(line) == i + 1:  # 如果这行已满
                color = line[0]
                # 将瓷砖移到墙上对应的位置
                agent.grid_state[i][agent.grid_scheme[i].index(color)] = 1
                # 清空这行模式线
                agent.pattern_lines[i] = []
                # 剩余的瓷砖放入地板线
                agent.floor.extend(line[1:])

    def _calculate_score(self, agent):
        pass

    def _refill_factories(self, state):
        pass

    # Take a list of actions and an initial state, and perform breadth-first search within a time limit.
    # Return the first action that leads to goal, if any was found.
    def SelectAction(self, actions, rootstate):
        start_time = time.time()
        queue      = deque([ (deepcopy(rootstate),[]) ]) # Initialise queue. First node = root state and an empty path.
        
        # Conduct BFS starting from rootstate.
        while len(queue) and time.time()-start_time < THINKTIME:
            state, path = queue.popleft() # Pop the next node (state, path) in the queue.
            new_actions = self.GetActions(state) # Obtain new actions available to the agent in this state.
            
            for a in new_actions: # Then, for each of these actions...
                next_state = deepcopy(state)              # Copy the state.
                next_path  = path + [a]                   # Add this action to the path.
                goal     = self.DoAction(next_state, a) # Carry out this action on the state, and check for goal
                if goal:
                    print(f'Move {self.turn_count}, path found:', next_path)
                    return next_path[0] # If the current action reached the goal, return the initial action that led there.
                else:
                    queue.append((next_state, next_path)) # Else, simply add this state and its path to the queue.
        
        return random.choice(actions) # If no goal was found in the time limit, return a random action.
        
    
# END FILE -----------------------------------------------------------------------------------------------------------#