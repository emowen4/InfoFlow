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
from typing import List


class Information:
    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return self.content


class Challenge:
    challenge_rewards = [100, 300, 500, 1000, 1500]  # from 0 to 5
    reward_completion_multiplier = [.0, .3, .6, .9, 1.2, 1.5]  # 0%, 20%, 40%, 60%, 80%, 100% completion
    score_correct_info = 100
    score_incorrect_info = -200
    score_correct_multiplier_level = 100
    score_cancel_multiplier_level = -100
    money_cancel_multiplier_level = -300

    def __init__(self, level: int, reward: int, given_info: 'List[Information]', required_info: 'List[Information]'):
        self.level = level
        self.reward = reward
        self.given_info = given_info
        self.required_info = required_info
        self.found_info = []

    def add_info(self, info: Information):
        if info not in self.found_info:
            self.found_info.append(info)
            return True
        return False

    def remove_info(self, info: Information):
        if info in self.found_info:
            self.found_info.remove(info)
            return True
        return False

    def submit(self, p: 'PlayerInfo'):
        correct = 0
        for info in self.found_info:
            if info in self.required_info:
                p.score += Challenge.score_correct_info
                correct += 1
            else:
                p.score += Challenge.score_incorrect_info
        correct_level = correct / len(self.required_info)
        if correct_level > .6:
            p.score += self.level * Challenge.score_correct_multiplier_level
            p.income += Challenge.challenge_rewards[self.level] * Challenge.reward_completion_multiplier[int(correct_level * 5)]
            return True, correct_level
        else:
            return False, correct_level

    def cancel(self, p: 'PlayerInfo'):
        p.score += Challenge.score_cancel_multiplier_level * self.level
        p.income -= Challenge.money_cancel_multiplier_level * self.level

    def __contains__(self, item):
        return item in self.required_info

    def __str__(self):
        return f"Level: {self.level}\tReward: {self.reward}\n" + "\n".join([f"\t{info}" for info in self.given_info])

    @staticmethod
    def random() -> 'Challenge':
        pass

    @staticmethod
    def clone(c: 'Challenge') -> 'Challenge':
        pass


class PlayerInfo:
    def __init__(self, score: int = 0,
                 finished: int = 0,
                 income: int = 0,
                 total_income: int = 0,
                 cpu_level: bool = 0,
                 internet_level: bool = 0):
        self.score = score
        self.finished = finished
        self._income = income
        self._total_income = total_income
        self.cpu_level = cpu_level
        self.internet_level = internet_level

    @property
    def income(self):
        return self._income

    @income.setter
    def income_setter(self, val):
        self.income += val
        if val > 0:
            self._total_income += val

    @property
    def total_income(self):
        return self._total_income

    def __str__(self):
        return (f"Player Stats:"
                f"\tScore: {self.score}"
                f"\tFinished Challenges: {self.finished}"
                f"\tIncome/Total: {self.income}/{self.total_income}"
                f"\tCPU Level: {self.cpu_level}"
                f"\tInternet Level: {self.internet_level}")

    @staticmethod
    def clone(info: 'PlayerInfo'):
        return PlayerInfo(info.score,
                          info.finished,
                          info.income,
                          info.total_income,
                          info.cpu_level,
                          info.internet_level)


class State:
    def __init__(self, clone: 'State' = None):
        if clone:
            self.info = PlayerInfo.clone(clone.info)
            self.challenge = Challenge.clone(clone.challenge) if clone.challenge else None
            self.round = clone.round
        else:
            self.info = PlayerInfo()
            self.challenge = None
            self.round = 1

    def has_challenge(self) -> bool:
        return self.challenge is not None

    def is_applicable_operator(self, op: 'Operator') -> bool:
        raise NotImplementedError()

    def apply_operator(self, op: 'Operator') -> 'State':
        raise NotImplementedError()

    def is_goal(self) -> bool:
        # TODO goal
        return False

    def __eq__(self, s):
        if self == s:
            return True
        if s is None:
            return False
        return type(self) is type(s) and self.info == s.info and self.challenge == s.challenge and self.round == s.round

    def __str__(self):
        return f"Round {self.round}\n{self.info}"

    def __hash(self):
        return hash(str(self))

    def finish_round(self, cls_state) -> 'State':
        ns = object.__new__(cls_state)
        ns.__init__(clone=self)
        ns.round += 1
        return ns


# Tell the background of the game, introduce the game mechanics, and declare the goal
class GameStartState(State):
    text_background = (
        '''<Here is the background>'''
    )

    def __init__(self, clone: 'GameStartState' = None):
        super().__init__(clone)

    def is_applicable_operator(self, op: 'Operator'):
        return op.id is OperatorIds.MENU_CONTINUE

    def apply_operator(self, op: 'Operator'):
        return MainMenuState(self)

    def __str__(self):
        return f"Background:\n{GameStartState.text_background}"


class MainMenuState(State):
    def __init__(self, clone: 'MainMenuState' = None):
        super().__init__(clone)

    def is_applicable_operator(self, op: 'Operator'):
        return (op.id is OperatorIds.MENU_CHALLENGE
                or op.id is OperatorIds.MENU_UPGRADE
                or op.id is OperatorIds.MENU_FINISH_ROUND)

    def apply_operator(self, op: 'Operator'):
        if op.id is OperatorIds.MENU_CHALLENGE:
            return ChallengeState(self)
        elif op.id is OperatorIds.MENU_UPGRADE:
            return UpgradeState(self)
        elif op.id is OperatorIds.MENU_FINISH_ROUND:
            return self.finish_round(MainMenuState)
        else:
            raise ValueError()


class ChallengeState(State):
    def __init__(self, clone: 'ChallengeState' = None):
        super().__init__(clone)

    def is_applicable_operator(self, op: 'Operator'):
        return (op.id is OperatorIds.MENU_BACK
                or (not self.has_challenge() and (op.id is OperatorIds.CHALLENGE_ACCEPT
                                                  or op.id is OperatorIds.CHALLENGE_DECINE))
                or (self.has_challenge() and (op.id is OperatorIds.CHALLENGE_SEARCH
                                              or op.id is OperatorIds.CHALLENGE_ANALYZE
                                              or op.id is OperatorIds.CHALLENGE_SUBMIT))
                or op.id is OperatorIds.MENU_FINISH_ROUND)

    def apply_operator(self, op: 'Operator'):
        if op.id is OperatorIds.MENU_BACK:
            return MainMenuState(self)
        elif op.id is OperatorIds.MENU_FINISH_ROUND:
            return self.finish_round(ChallengeState)
        ns = ChallengeState(self)
        # TODO search, analyze, and submit
        return ns


class Upgrade:
    @staticmethod
    def upgrade_cpu(current_level: int) -> int:
        return current_level * 500

    @staticmethod
    def upgrade_internet(current_level: int) -> int:
        return current_level * 500


# Player can upgrade CPU and Internet plan
class UpgradeState(State):
    def __init__(self, clone: 'UpgradeState' = None):
        super().__init__(clone)

    def is_applicable_operator(self, op: 'Operator'):
        return (op.id is OperatorIds.MENU_BACK
                or (not self.has_challenge() and (op.id is OperatorIds.UPGRADE_CPU
                                                  or op.id is OperatorIds.UPGRADE_INTERNET_PLAN))
                or op.id is OperatorIds.MENU_FINISH_ROUND)

    def apply_operator(self, op: 'Operator'):
        if op.id is OperatorIds.MENU_BACK:
            return MainMenuState(self)
        elif op.id is OperatorIds.MENU_FINISH_ROUND:
            return self.finish_round(UpgradeState)
        ns = UpgradeState(self)
        if op.id is OperatorIds.UPGRADE_CPU:
            req = Upgrade.upgrade_cpu(ns.info.cpu_level)
            if req < ns.info.income:
                ns.info.income -= req
                ns.info.cpu_level += 1
            else:
                return InformationDisplayState(ns, "Warning", "Not enough money to upgrade CPU!")
        elif op.id is OperatorIds.UPGRADE_INTERNET_PLAN:
            req = Upgrade.upgrade_internet(ns.info.internet_level)
            if req < ns.info.income:
                ns.info.income -= req
                ns.info.internet_level += 1
            else:
                return InformationDisplayState(ns, "Warning", "Not enough money to upgrade Internet!")
        return ns


class InformationDisplayState(State):
    def __init__(self, continue_to: 'State', title: str, info: str):
        self.continue_to = continue_to
        self.title = title
        self.info = info

    def is_applicable_operator(self, op: 'Operator'):
        return op.id is OperatorIds.MENU_CONTINUE

    def apply_operator(self, op: 'Operator'):
        return self.continue_to

    def __str__(self):
        return f"{self.title}: {self.info}"


# If needed
class GameEndState(InformationDisplayState):
    def __init__(self, title: str, info: str):
        super().__init__(None, title, info)

    def is_applicable_operator(self, op: 'Operator'):
        return False

    def is_goal(self):
        return True


def goal_message(s: State) -> str:
    return (f"Congratulations! You makes the goal in {s.round}{'s' if s.round > 1 else ''} with a score of {s.info.score}."
            f"You earned {s.info.total_income} in total and {s.info.income} left.")


def copy_state(s: State) -> State:
    if isinstance(s, GameStartState):
        return GameStartState(s)
    if isinstance(s, MainMenuState):
        return MainMenuState(s)
    if isinstance(s, ChallengeState):
        return ChallengeState(s)
    if isinstance(s, UpgradeState):
        return UpgradeState(s)
    if isinstance(s, InformationDisplayState):
        return InformationDisplayState(s.continue_to, s.title, s.info)
    if isinstance(s, GameEndState):
        return GameEndState(s.title, s.info)
    raise ValueError()


class OperatorIds(Enum):
    MENU_CONTINUE = "Continue..."
    MENU_CHALLENGE = "Move to challenge view"
    MENU_UPGRADE = "Move to upgrade view"
    MENU_BACK = "Move to upper menu"
    MENU_FINISH_ROUND = "Finish this round"
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

    def is_applicable(self, s: 'State') -> bool:
        return s.is_applicable_operator(self)

    def apply(self, s: 'State') -> 'State':
        return s.apply_operator(self)


Operator.all_ops = [Operator(id.value, id) for id in list(OperatorIds)]


def goal_test(s: 'State') -> bool: return s.is_goal()


# </COMMON_CODE>

# <COMMON_DATA>
# </COMMON_DATA>

# <INITIAL_STATE>
INITIAL_STATE = GameStartState()
# </INITIAL_STATE>

# <OPERATORS>
OPERATORS = Operator.all_ops[:]
# </OPERATORS>

# <GOAL_TEST> (optional)
GOAL_TEST = lambda s: isinstance(s, GameEndState) and goal_test(s)
# </GOAL_TEST>

# <GOAL_MESSAGE_FUNCTION> (optional)
GOAL_MESSAGE_FUNCTION = goal_message
# </GOAL_MESSAGE_FUNCTION>

# <STATE_VIS>
# </STATE_VIS>
