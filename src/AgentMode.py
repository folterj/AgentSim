from enum import Enum

class AgentMode(Enum):
    idle = 1
    exploring = 2
    eating = 3
    returning_food = 4
    returning_tired = 5
    following_pheromone = 6
    following_ant = 7
    distressed = 8
    following_alarm = 9
    dead = 10
