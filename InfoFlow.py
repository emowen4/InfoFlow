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
    reward_completion_multiplier = [.00, .25, .50, .75, 1.00, 1.25]  # 0%, 20%, 40%, 60%, 80%, 100% completion
    score_correct_multiplier_level = 100
    score_cancel_multiplier_level = -100
    money_cancel_multiplier_level = -300

    def __init__(self, name: str):
        self.name = name

    def accept(self, p: 'PlayerInfo') -> 'State':
        raise NotImplementedError()

    def cancel(self, p: 'PlayerInfo') -> 'State':
        raise NotImplementedError()

    def submit(self, p: 'PlayerInfo') -> 'State':
        raise NotImplementedError()

    def __str__(self):
        return self.name


class SortChallenge2(Challenge):
    score_correct_info = 100
    score_incorrect_info = -200

    def __init__(self, level: int, reward: int, given_info: 'List[Information]', required_info: 'List[Information]'):
        super().__init__("Sort Challenge")
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
            p.money += Challenge.challenge_rewards[self.level] * Challenge.reward_completion_multiplier[int(correct_level * 5)]
            return True, correct_level
        else:
            return False, correct_level

    def cancel(self, p: 'PlayerInfo'):
        p.score += Challenge.score_cancel_multiplier_level * self.level
        p.money += Challenge.money_cancel_multiplier_level * self.level

    def __contains__(self, item):
        return item in self.required_info

    def __str__(self):
        return f"Level: {self.level}\tReward: {self.reward}\n" + "\n".join([f"\t{info}" for info in self.given_info])

    @staticmethod
    def random() -> 'SortChallenge2':
        pass

    @staticmethod
    def clone(c: 'SortChallenge2') -> 'SortChallenge2':
        pass


class PlayerInfo:

    def __init__(self, score: int = 0,
                 finished: int = 0,
                 money: int = 0,
                 debt: int = 10000,
                 energy: int = 100,
                 current_challenge: 'Challenge' = None):
        self.score = score
        self.finished = finished
        self.money = money
        self.debt = debt
        self._energy = energy
        self.current_challenge = current_challenge

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, val):
        self._energy = val
        if self._energy < 0:
            self._energy = 0
        if self._energy > 100:
            self._energy = 100

    def has_accepted_challenge(self):
        return self.current_challenge is not None

    def __str__(self):
        block_full, block_three_forth, block_half, block_one_fourth, block_empty = '█', '▊', '▌', '▎', '　'
        energy_blocks = block_full * (self.energy // 20)
        energy_rest = self.energy % 20
        energy_rest = block_three_forth if energy_rest >= 15 else block_half if energy_rest >= 10 else block_one_fourth if energy_rest >= 5 else ''
        energy_spaces = block_empty * (max(0, 5 - len(energy_blocks) - len(energy_rest)))
        return (f"Player Stats:"
                f"\tEnergy: {'{0:3}'.format(self.energy)}▕{energy_blocks}{energy_rest}{energy_spaces}▏"
                f"\tScore: {self.score}"
                f"\tFinished Challenges: {self.finished}"
                f"\tMoney/Debt: {self.money}/{self.debt}"
                f"\t Has accepted challenge: {'✔' if self.has_accepted_challenge() else '×'}")

    @staticmethod
    def clone(info: 'PlayerInfo'):
        return PlayerInfo(info.score,
                          info.finished,
                          info.money,
                          info.debt,
                          info.energy,
                          info.current_challenge)


class State:
    def __init__(self, clone: 'State' = None):
        if clone:
            self.info = PlayerInfo.clone(clone.info)
            self.challenge = SortChallenge2.clone(clone.challenge) if clone.challenge else None
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

    def __init__(self, clone: 'State' = None):
        super().__init__(clone)

    def is_applicable_operator(self, op: 'Operator'):
        return op.id is OperatorIds.MENU_CONTINUE

    def apply_operator(self, op: 'Operator'):
        return ChallengeState(self)

    def __str__(self):
        return f"Background:\n{GameStartState.text_background}"


class ChallengeState(State):
    def __init__(self, clone: 'State' = None):
        super().__init__(clone)

    def is_applicable_operator(self, op: 'Operator'):
        return ((not self.has_challenge() and (op.id is OperatorIds.CHALLENGE_ACCEPT
                                                  or op.id is OperatorIds.CHALLENGE_DECINE))
                or (self.has_challenge() and (op.id is OperatorIds.CHALLENGE_CANCEL)))

    def apply_operator(self, op: 'Operator'):
        ns = ChallengeState(self)
        # TODO challenge related
        return ns


class MessageDisplayState(State):
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
class GameEndState(MessageDisplayState):
    def __init__(self, title: str, info: str):
        super().__init__(None, title, info)

    def is_applicable_operator(self, op: 'Operator'):
        return False

    def is_goal(self):
        return True


def goal_message(s: State) -> str:
    return (f"Congratulations! You makes the goal in {s.round}{'s' if s.round > 1 else ''} with a score of {s.info.score}."
            f"You earned {s.info.total_money} in total and {s.info.money} is left.")


def copy_state(s: State) -> State:
    if isinstance(s, GameStartState):
        return GameStartState(s)
    if isinstance(s, ChallengeState):
        return ChallengeState(s)
    if isinstance(s, MessageDisplayState):
        return MessageDisplayState(s.continue_to, s.title, s.info)
    if isinstance(s, GameEndState):
        return GameEndState(s.title, s.info)
    raise ValueError()


class OperatorIds(Enum):
    MENU_CONTINUE = "Continue..."
    CHALLENGE_ACCEPT = "Accept the challenge"
    CHALLENGE_DECINE = "Decine the challenge"
    CHALLENGE_CANCEL = "Cancel the accepted challenge"
    PAY_DEBT = ""


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
