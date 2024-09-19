import math
import random
import time
from Azul.azul_model import AzulGameRule
from template import Agent

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state         
        self.parent = parent       
        self.action = action       
        self.children = []         
        self.visits = 0            
        self.value = 0             

    # check if the node is fully expanded
    def is_fully_expanded(self, game_rule, agent_id):
        legal_actions = game_rule.getLegalActions(self.state, agent_id)
        return len(self.children) == len(legal_actions)

    # choose the best child node with UCB1 formula
    def best_child(self, c_param=1.4):
        choices_weights = []
        for child in self.children:
            if child.visits == 0:
                # if child node is not visited, give high priority
                choices_weights.append(float('inf'))
            else:
                # calculate weight with UCB1 formula
                exploration_value = c_param * math.sqrt(2 * math.log(self.visits) / child.visits)
                exploitation_value = child.value / child.visits
                choices_weights.append(exploitation_value + exploration_value)
        
        return self.children[choices_weights.index(max(choices_weights))]

    # add child node
    def add_child(self, child_node):
        self.children.append(child_node)

    # update visits and value
    def update(self, value):
        self.visits += 1
        self.value += value


class myAgent(Agent):
    def __init__(self, _id):
        super().__init__(_id)
        self.game_rule = AzulGameRule(2)  # 假设是两人游戏
        self.turn_count = 0

    def SelectAction(self, actions, game_state):
        self.turn_count += 1
        start_time = time.time()
        
        # initialize root node
        root = Node(game_state)
        
        # execute MCTS within 950ms
        while time.time() - start_time < 0.95:
            leaf = self.select(root)  # select
            if not leaf.is_fully_expanded(self.game_rule, self.id):
                child = self.expand(leaf)  # expand
                if child is None:
                    print("Warning: child node is None, expansion failed.")
                    continue
                value = self.simulate(child.state)  # simulate
            else:
                value = self.simulate(leaf.state)  # if not expanded, simulate
            self.backpropagate(leaf, value)  # backpropagate
        
        # choose the best action
        best_child = root.best_child(c_param=0)
        return best_child.action

    # select an unexpanded node
    def select(self, node):
        current_node = node
        while current_node.is_fully_expanded(self.game_rule, self.id):
            current_node = current_node.best_child()
        return current_node

    # expand a legal action
    def expand(self, node):
        legal_actions = self.game_rule.getLegalActions(node.state, self.id)
        for action in legal_actions:
            if not any(child.action == action for child in node.children):
                new_state = self.game_rule.generateSuccessor(node.state, action, self.id)
                if new_state is None:
                    print(f"Warning: generateSuccessor returned None for action {action}.")
                    continue
                new_node = Node(new_state, parent=node, action=action)
                node.add_child(new_node)
                return new_node
        return None  

    # simulate until game ends, use ScoreRound to calculate score
    def simulate(self, state):
        current_state = state
        while not self.game_rule.gameEnds():
            legal_actions = self.game_rule.getLegalActions(current_state, self.id)
            if not legal_actions:
                return self.calculate_score(current_state)
            try:
                #random choose an action (improve this with heuristic?)
                action = random.choice(legal_actions)
                current_state = self.game_rule.generateSuccessor(current_state, action, self.id)
                if current_state is None:
                    print(f"Warning: generateSuccessor returned None during simulation for action {action}.")
                    continue
            except AssertionError:
                continue
        return self.calculate_round_score(current_state)

    def backpropagate(self, node, value):
        current_node = node
        while current_node is not None:
            current_node.update(value)
            current_node = current_node.parent

    # score round
    def calculate_round_score(self, state):
        agent_state = state.agents[self.id]
        score, _ = agent_state.ScoreRound()  
        return score

    
    def calculate_score(self, state):
        agent_state = state.agents[self.id]
        return agent_state.EndOfGameScore()  #final score
