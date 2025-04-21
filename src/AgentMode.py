from enum import Enum

class AgentMode(Enum):
    Dead = -1
    Idle = 0
    Scout = 1
    Return = 2
    Eat = 3
    Recruit = 4
    Distress = 5
