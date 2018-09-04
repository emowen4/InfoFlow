'''InfoFlow.py
("InfoFlow" problem)
A SOLUZION problem formulation.  UPDATED SEP 2018.
The XML-like tags used here may not be necessary, in the end.
But for now, they serve to identify key sections of this
problem formulation.  It is important that COMMON_CODE come
before all the other sections (except METADATA), including COMMON_DATA.
'''
# <METADATA>
SOLUZION_VERSION = "0.1"
PROBLEM_NAME = "Info Flow"
PROBLEM_VERSION = "0.1"
PROBLEM_AUTHORS = ["Dylan Li", "Joey Pan", "Owen Wang", "Shirley Zhang"]
PROBLEM_CREATION_DATE = "04-Sep-2018"
PROBLEM_DESC = \
    '''
    Info Flow.
    '''
# </METADATA>

# <COMMON_CODE>
from enum import Enum


class Challenge:
    @staticmethod
    def random(): pass


class PlayerInfo:
    def __init__(self, score: int = 0,
                 finished: int = 0,
                 income: int = 0,
                 total_income: int = 0,
                 upgraded_cpu: bool = False,
                 upgraded_internet: bool = False):
        self.score = score
        self.finished = finished
        self.income = income
        self.total_income = total_income
        self.upgraded_cpu = upgraded_cpu
        self.upgraded_internet = upgraded_internet


class State:
    def __init__(self, clone: 'State'):
        if clone:
            self.info = clone.info
            self.challenge = clone.challenge
            self.round = clone.round
        else:
            self.info = PlayerInfo()
            self.challenge = None
            self.round = 0

    def has_challenge(self) -> bool:
        return self.challenge is not None

    def is_applicable_operator(self, op: 'Operator') -> bool:
        pass

    def apply_operator(self, op: 'Operator') -> 'State':
        pass

    def is_goal(self) -> bool:
        pass

    def __eq__(self, s):
        if self == s: return True
        if s is None: return False
        return type(self) is type(s) and self.info == s.info and self.challenge == s.challenge and self.round == s.round

    def __str__(self) -> str:
        pass

    def __hash(self):
        return hash(str(self))


# Tell the background of the game, introduce the game mechanics, and declare the goal
class GameStartState(State):
    def is_applicable_operator(self, op):
        return op


class MainMenuState(State): pass


class ChallengeState(State): pass


# Player can upgrade CPU and Internet plan
class UpgradeState(State): pass


# If needed
class GameEndState(State): pass


def goal_message(s: State) -> str:
    return f"Congratulations! You makes the goal in {s.round}{'s' if s.round > 1 else ''}"


def copy_state(s: State) -> State:
    if isinstance(s, GameStartState):
        return GameStartState(s)
    if isinstance(s, MainMenuState):
        return MainMenuState(s)
    if isinstance(s, ChallengeState):
        return ChallengeState(s)
    if isinstance(s, UpgradeState):
        return UpgradeState(s)
    raise ValueError()


class OperatorIds(Enum):
    MENU_CHALLENGE = "Move to challenge view"
    MENU_UPGRADE = "Move to upgrade view"
    MENU_BACK = "Move to upper menu"
    MENU_CONTINUE = "Continue..."
    CHALLENGE_ACCEPT = "Accept the challenge"
    CHALLENGE_DECINE = "Decine the challenge"
    CHALLENGE_SEARCH = "Search information online"
    CHALLENGE_ANALYZE = "Analyze current information"
    CHALLENGE_SUBMIT = "Submit the information you have now"
    UPGRADE_CPU = "Upgrade your CPU to analyze faster"
    UPGRADE_INTERNET_PLAN = "Upgrade your Internet plan to search faster"


class Operator:
    def __init__(self, name, id: 'OperatorIds'):
        self.name = name
        self.id = id

    def is_applicable(self, s) -> bool:
        return s.is_applicable_operator(self)

    def apply(self, s) -> 'State':
        return s.apply(self)


# </COMMON_CODE>

# <COMMON_DATA>
# </COMMON_DATA>

# <INITIAL_STATE>
INITIAL_STATE = GameStartState()
# </INITIAL_STATE>

# <OPERATORS>
OPERATORS = [Operator(id.value, id) for id in list(OperatorIds)]
# </OPERATORS>

# <GOAL_TEST> (optional)
GOAL_TEST = lambda s: isinstance(s, GameEndState) and s.is_goal()
# </GOAL_TEST>

# <GOAL_MESSAGE_FUNCTION> (optional)
GOAL_MESSAGE_FUNCTION = goal_message
# </GOAL_MESSAGE_FUNCTION>

# <STATE_VIS>

# </STATE_VIS>
