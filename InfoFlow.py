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
    '''Welcome to Info Flow!
    2025, this is a technology highly developed time, many types of work that used completed by human is now replaced by AI machine working. Lives became more convenience, but finding a job became more and more difficult. 
At this time, a mysteric website appeared: they offer huge amounts of cash for employees, but once you chose this website all your personal information is connected with the website (no matter public information or private things, they need all of your information). You need to complete tasks for them in order to pay the debt. These tasks are complicated and covered from online to physical activities, and if you did well, they even pay you bonus for your work. 
It sounds good to work for this website right? But here is one thing you should know, if you cannot finish the final goal to pay the debt, that will definitely end even worse than be in a jail……
You are just a normal student in college. One day there was a group of people suddenly broke into your house and saying that your father owe them huge amount of money-- Your father gambled and lost all property in your family. You have to leave the school and work to earn money. But you are just a student who even did not finished college course, what could you do?
There is no way to earn money except for that website, and today is you will be facing the first challenge from that website, what will that be……?

    '''
# </METADATA>

# <COMMON_CODE>
from enum import Enum
from typing import List, Dict


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
    energy_accept_multiplier_level = 5

    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level

    def accept(self, p: 'PlayerInfo'):
        p.energy -= self.energy_consume()

    def cancel(self, p: 'PlayerInfo'):
        p.score += Challenge.score_cancel_multiplier_level * self.level
        p.money += Challenge.money_cancel_multiplier_level * self.level

    def submit(self, p: 'PlayerInfo'):
        raise NotImplementedError()

    def energy_consume(self):
        return self.level * Challenge.energy_accept_multiplier_level

    def __str__(self):
        return self.name


class SortChallenge(Challenge):
    class SortInformation:
        def __init__(self, content: str, category: str):
            self.content = content
            self.category = category

        def __eq__(self, other):
            if other is None:
                return False
            return isinstance(other, type(self)) and self.category == other.category and self.content == other.content

        def __str__(self):
            return self.content

    score_correct_info = 10
    score_incorrect_info = -20

    def __init__(self, level: int, to_sort: List[SortInformation], categories: List[str] = None, sorted: Dict[str, List[SortInformation]] = None):
        super().__init__("News Sort Challenge", level)
        self.level = level
        self.to_sort = to_sort
        self.categories = categories if categories else list(set([info.category for info in to_sort]))
        self.sorted = sorted if sorted else {}

    def sort_to(self, info: 'SortInformation', category: 'str'):
        self.sorted.setdefault(category, [])
        self.sorted[category].append(info)

    def remove_from(self, info: 'SortInformation', category: 'str'):
        if category in self.to_sort and info in self.to_sort[category]:
            self.to_sort[category].remove(info)

    def submit(self, p: 'PlayerInfo'):
        correct = 0
        for cat, infos in self.sorted:
            for info in infos:
                if info.category == cat:
                    p.score += SortChallenge.score_correct_info
                    correct += 1
                else:
                    p.score += SortChallenge.score_incorrect_info
        correct_level = correct / len(self.to_sort)
        if correct_level >= .8:  # Require at least 80% of the information are sorted correctly to get success in this challenge
            p.score += self.level * Challenge.score_correct_multiplier_level
            p.money += Challenge.challenge_rewards[self.level] * Challenge.reward_completion_multiplier[int(correct_level * 5)]
            return True, correct_level
        else:
            return False, correct_level

    def __str__(self):
        return (f"{super().__str__()}\tLevel: {self.level}\n"
                "\n".join([f"\t{'{0:3}'.format(ind)}: {info.content}" for ind, info in enumerate(self.to_sort)]))

    @staticmethod
    def clone(c: 'SortChallenge') -> 'SortChallenge':
        return SortChallenge(c.level, c.to_sort, c.categories, c.sorted)

    @staticmethod
    def random() -> 'SortChallenge':
        # TODO
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
        self._debt = debt
        self._energy = energy
        self.current_challenge = current_challenge

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, val):
        self._energy = 0 if val < 0 else 100 if val > 100 else val

    @property
    def debt(self):
        return self._debt

    @debt.setter
    def debt(self, val):
        self._debt = 0 if val < 0 else val

    def has_accepted_challenge(self):
        return self.current_challenge is not None

    def __str__(self):
        block_full, block_three_forth, block_half, block_one_fourth, block_empty = '█', '▊', '▌', '▎', '　'
        energy_blocks = block_full * (self.energy // 20)
        energy_rest = self.energy % 20
        energy_rest = block_three_forth if energy_rest >= 15 else block_half if energy_rest >= 10 else block_one_fourth if energy_rest >= 5 else ''
        energy_spaces = block_empty * max(0, 5 - len(energy_blocks) - len(energy_rest))
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
            self.player = PlayerInfo.clone(clone.player)
            self.challenge = SortChallenge.clone(clone.challenge) if clone.challenge else None
            self.round = clone.round
        else:
            self.player = PlayerInfo()
            self.challenge = None
            self.round = 1

    def has_challenge(self) -> bool:
        return self.challenge is not None

    def is_applicable_operator(self, op: 'Operator') -> bool:
        return op.id is OperatorIds.FINISH_ROUND or op.id is OperatorIds.PAY_DEBT

    def apply_operator(self, op: 'Operator') -> 'State':
        ns = copy_state(self)
        if op.id is OperatorIds.FINISH_ROUND:
            ns.round += 1
            ns.player.energy += 80  # Recover 80% of total energy after each round
            ns.player.debt = int(ns.player.debt * 1.05)  # Add 5% debt according to the remaining debt after each round
        elif op.id is OperatorIds.PAY_DEBT:
            if ns.player.money > 0:
                to_pay = min(ns.player.debt, ns.player.money)
                ns.player.debt -= to_pay
                ns.player.money -= to_pay
                return MessageDisplayState(ns.check_win_lose_state(), "Great!", f"${to_pay} is paid for your debt.")
            else:
                return MessageDisplayState(ns.check_win_lose_state(), "Failed!", "You don't have any money to pay for your debt!")
        return ns.check_win_lose_state()

    def check_win_lose_state(self):
        if self.is_goal():
            return GameEndState(self.player, "Congratulations!", self.goal_message())
        elif self.round >= 30 and not self.is_goal():
            return GameEndState(self.player, "You Lose!", self.lose_message())
        else:
            return self

    def is_goal(self) -> bool:
        return self.player.debt is 0

    def goal_message(self) -> str:
        return (f"You makes the goal in {self.round}{'s' if self.round > 1 else ''} with a score of {self.player.score}. "
                f"You payed all the debt and there is {self.player.money} left.")

    def lose_message(self) -> str:
        return (f"You didn't make the goal in {self.round}{'s' if self.round > 1 else ''} with a score of {self.player.score}. "
                f"You have {self.player.money} and {self.player.debt} is needed to pay.")

    def __eq__(self, s):
        if self == s:
            return True
        if s is None:
            return False
        return type(self) is type(s) and self.player == s.info and self.challenge == s.challenge and self.round == s.round

    def __str__(self):
        return f"Round {self.round}\n{self.player}"

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

    def __init__(self):
        super().__init__()

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
        return (super().is_applicable_operator(op)
                or (not self.has_challenge() and (op.id is OperatorIds.CHALLENGE_ACCEPT or op.id is OperatorIds.CHALLENGE_DECINE)))

    def apply_operator(self, op: 'Operator'):
        if super().is_applicable_operator(op):
            return super().apply_operator(op)
        ns = ChallengeState(self)
        # TODO challenge related
        return ns.check_win_lose_state()


class MessageDisplayState(State):
    def __init__(self, continue_to: 'State', title: str, info: str):
        super().__init__(continue_to)
        self.continue_to = continue_to
        self.title = title
        self.info = info

    def is_applicable_operator(self, op: 'Operator'):
        return op.id is OperatorIds.MENU_CONTINUE

    def apply_operator(self, op: 'Operator'):
        return self.continue_to

    def __str__(self):
        return f"{self.title}\n{self.info}"


# If needed
class GameEndState(MessageDisplayState):
    def __init__(self, player: 'PlayerInfo', title: str, info: str):
        super().__init__(None, title, info)
        self.player = player

    def is_applicable_operator(self, op: 'Operator'):
        return False

    def is_goal(self):
        return True


def goal_message(s: State) -> str:
    return s.goal_message()


def copy_state(s: State) -> State:
    if isinstance(s, GameStartState):
        return GameStartState()
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
    PAY_DEBT = "Pay for the debt"
    FINISH_ROUND = "End round"


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
