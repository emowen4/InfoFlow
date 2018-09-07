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
    In the year 2025 when technology is highly developed, types of jobs that were completed by people are now replaced 
    by artificial intelligence. Our lives have become more convenient, but people are still struggling for livings.
    A platform gradually emerges which offers huge amounts of money for employees. The platform aims to categorize 
    complicated information using human power. However, once you choose this platform, all your personal information, 
    including privacy, will be released to this platform. It offers a variety of tasks and bonus to its users. 
    Some of those challenges are complicated, ranging from physical work to careful thinking.
    ------
    You are a college student. Yesterday, there was a group of people breaking into your house and telling you that 
    your father owes them a huge amount of money ($10000) in gambling. You have decided to drop school and pay the debt. 
    You have no solidified skills but the only platform as mentioned earlier. If you cannot pay the debt on time, 
    you will be captured and treated in a way you could never think of. You are asked to complete assigned challenges 
    to pay your debt.  Today, you will be facing your first challenge from this platform. What will that be...?
'''
# </METADATA>

# <COMMON_CODE>
from enum import Enum
from random import choice
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

    def accept(self, p: 'PlayerInfo') -> None:
        p.energy -= self.energy_consume()

    def decline(self, p: 'PlayerInfo') -> None:
        p.money -= 100
        p.difficulty_level -= 1

    def cancel(self, p: 'PlayerInfo') -> None:
        p.score += Challenge.score_cancel_multiplier_level * self.level
        p.money += Challenge.money_cancel_multiplier_level * self.level

    def submit(self, p: 'PlayerInfo') -> None:
        raise NotImplementedError()

    def set_finished(self, p: 'PlayerInfo'):
        p.finished += 1
        p.difficulty_level += 1

    def energy_consume(self):
        return self.level * Challenge.energy_accept_multiplier_level

    def preview(self) -> str:
        return f"{self.name}(Level: {self.level + 1})"

    def __str__(self):
        return self.preview()


class PlayerInfo:
    def __init__(self, difficulty_level: int = 0,
                 score: int = 0,
                 finished: int = 0,
                 money: int = 0,
                 debt: int = 10000,
                 energy: int = 100,
                 current_challenge: 'Challenge' = None):
        self._difficulty_level = difficulty_level
        self.score = score
        self.finished = finished
        self.money = money
        self._debt = debt
        self._energy = energy
        self.current_challenge = current_challenge

    @property
    def difficulty_level(self):
        return self._difficulty_level

    @difficulty_level.setter
    def difficulty_level(self, val):
        self._difficulty_level = 0 if val < 0 else 5 if val > 5 else val

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
                f"\tEnergy: {self.energy:3}▕{energy_blocks}{energy_rest}{energy_spaces}▏"
                f"\tScore: {self.score}"
                f"\tFinished Challenges: {self.finished}"
                f"\tMoney/Debt: ${self.money}/${self.debt}"
                f"\tDifficulty Level: {self.difficulty_level:03}"
                f"\tHas accepted challenge: {'✔' if self.has_accepted_challenge() else '×'}")

    @staticmethod
    def clone(info: 'PlayerInfo'):
        return PlayerInfo(info.difficulty_level, info.score, info.finished, info.money, info.debt, info.energy, info.current_challenge)


class State:
    def __init__(self, old: 'State' = None):
        if old:
            self.player = PlayerInfo.clone(old.player)
            self.challenge = NewsSortChallenge.clone(old.challenge) if old.challenge else None
            self.round = old.round
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
        '''Welcome to Info Flow!
    In the year 2025 when technology is highly developed, types of jobs that were completed by people are now
replaced by artificial intelligence. Our lives have become more convenient, but people are still struggling for livings.
A platform gradually emerges which offers huge amounts of money for employees. The platform aims to categorize 
complicated information using human power. However, once you choose this platform, all your personal information, 
including privacy, will be released to this platform. It offers a variety of tasks and bonus to its users. 
Some of those challenges are complicated, ranging from physical work to careful thinking.
------------------------------------------------------------------------------------------------------------------------
    You are a college student. Yesterday, there was a group of people breaking into your house and telling you that 
your father owes them a huge amount of money ($10000) in gambling. You have decided to drop school and pay the debt. 
You have no solidified skills but the only platform as mentioned earlier. If you cannot pay the debt on time, 
you will be captured and treated in a way you could never think of. You are asked to complete assigned challenges 
to pay your debt.  Today, you will be facing your first challenge from this platform. What will that be...?'''
    )

    def __init__(self):
        super().__init__()

    def is_applicable_operator(self, op: 'Operator'):
        return op.id is OperatorIds.MENU_CONTINUE

    def apply_operator(self, op: 'Operator'):
        return ChallengeMenuState(self)

    def __str__(self):
        return f"{super().__str__()}\nBackground:\n{GameStartState.text_background}"


class ChallengeMenuState(State):
    def __init__(self, old: 'State' = None):
        super().__init__(old)
        self.random_challenge = list(old.random_challenge if isinstance(old, ChallengeMenuState) else self.__random_challenge())
        self.random_challenge[0] = self.random_challenge[0].clone()

    def __random_challenge(self):
        c, s = choice(Challenges.all)
        return c(self.player.difficulty_level), s

    def is_applicable_operator(self, op: 'Operator'):
        return (super().is_applicable_operator(op)
                or (not self.has_challenge() and (op.id is OperatorIds.CHALLENGE_ACCEPT or op.id is OperatorIds.CHALLENGE_DECINE)))

    def apply_operator(self, op: 'Operator'):
        if super().is_applicable_operator(op):
            return super().apply_operator(op)
        if op.id is OperatorIds.CHALLENGE_ACCEPT:
            ns = self.random_challenge[1](self, self.random_challenge[0])
            ns.player.current_challenge = self.random_challenge[0]
            ns.player.current_challenge.accept(ns.player)
            return ns.check_win_lose_state()
        elif op.id is OperatorIds.CHALLENGE_DECINE:
            ns = ChallengeMenuState(old=self)
            ns.random_challenge[0].decline(ns.player)
            ns.random_challenge = ns.__random_challenge()
            return ns.check_win_lose_state()

    def __str__(self):
        return f"{super().__str__()}\nYou have a challenge available: {self.random_challenge[0].preview()}."


class ChallengeState(State):
    def __init__(self, old: 'State' = None):
        super().__init__(old)

    def is_applicable_operator(self, op: 'Operator'):
        return self.has_challenge() and (op.id is OperatorIds.CHALLENGE_CANCEL)

    def apply_operator(self, op: 'Operator'):
        if op.id is OperatorIds.CHALLENGE_CANCEL:
            ns = ChallengeState(self)
            ns.player.current_challenge.cancel(self.player)
            return ns


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


class NewsInformation:
    # News Categories:
    # Business
    # Entertainment & Arts
    # Health & Medicine
    # Nature & Environments
    # Politics
    # Religions
    # Science
    # Schools
    # Sports
    # Technology
    # Video Games
    # Weather

    def __init__(self, category: str, content: str):
        self.category = category
        self.content = content

    def __eq__(self, other):
        if other is None:
            return False
        return isinstance(other, type(self)) and self.category == other.category and self.content == other.content

    def __hash__(self):
        return hash(f"{self.category}:{self.content}")

    def __str__(self):
        return self.content


class NewsSortChallenge(Challenge):
    news_collection = [
        # TODO Crawl some real news from sites like BBC and CNN
        *[NewsInformation("A", f"A{i}") for i in range(20)],
        *[NewsInformation("B", f"B{i}") for i in range(20)],
        *[NewsInformation("C", f"C{i}") for i in range(20)],
        *[NewsInformation("D", f"D{i}") for i in range(20)],
        *[NewsInformation("E", f"E{i}") for i in range(20)],
        *[NewsInformation("F", f"F{i}") for i in range(20)],
        *[NewsInformation("G", f"G{i}") for i in range(20)],
        *[NewsInformation("H", f"H{i}") for i in range(20)],
        *[NewsInformation("I", f"I{i}") for i in range(20)]
    ]

    score_correct_info = 10
    score_incorrect_info = -20

    def __init__(self, level: int, to_sort: List[NewsInformation], categories: List[str] = None, sorted: Dict[str, List[NewsInformation]] = None):
        super().__init__("News Sort Challenge", level)
        self.level = level
        self.to_sort = to_sort
        self.categories = categories if categories else list(set([info.category for info in to_sort]))
        self.categories.sort()
        self.sorted = sorted if sorted else {}

    def sort_to(self, info: 'NewsInformation', category: 'str'):
        self.sorted.setdefault(category, [])
        self.sorted[category].append(info)

    def remove_from(self, info: 'NewsInformation', category: 'str'):
        if category in self.to_sort and info in self.to_sort[category]:
            self.to_sort[category].remove(info)

    def submit(self, p: 'PlayerInfo'):
        correct = 0
        for cat, infos in self.sorted.items():
            for info in infos:
                if info.category == cat:
                    p.score += NewsSortChallenge.score_correct_info
                    correct += 1
                else:
                    p.score += NewsSortChallenge.score_incorrect_info
        correct_level = correct / len(self.to_sort)
        if correct_level >= .8:  # Require at least 80% of the information are sorted correctly to get success in this challenge
            p.score += self.level * Challenge.score_correct_multiplier_level
            p.money += Challenge.challenge_rewards[self.level] * Challenge.reward_completion_multiplier[int(correct_level * 5)]
            return True, correct_level
        else:
            return False, correct_level

    def __str__(self):
        return (f"{super().__str__()}\tChallenge Level: {self.level}\n"
                "\n".join([f"\t{'{0:3}'.format(ind)}: {info.content}" for ind, info in enumerate(self.to_sort)]))

    def clone(self) -> 'NewsSortChallenge':
        return NewsSortChallenge(self.level, self.to_sort, self.categories, self.sorted)

    @staticmethod
    def random(level) -> 'NewsSortChallenge':
        count = int(level ** 1.5) + 10  # TODO Create an appropriate formula based on the level
        to_sort = set()
        while len(to_sort) < count:
            to_sort.add(choice(NewsSortChallenge.news_collection))
        return NewsSortChallenge(level, list(to_sort))


class NewsSortChallengeState(ChallengeState):
    def __init__(self, old: 'State' = None, challenge: 'NewsSortChallenge' = None):
        super().__init__(old)
        self.news_index = old.news_index + 1 if old and isinstance(old, NewsSortChallengeState) else 0
        global OPERATORS
        if old and isinstance(old, NewsSortChallengeState) and not challenge:
            challenge = old.player.current_challenge
        if challenge:
            OPERATORS.clear()
            OPERATORS += [Operator(f"Empty", "")] + [Operator(f"In category '{cat}'", cat) for cat in challenge.categories]

    def is_applicable_operator(self, op: 'Operator'):
        return super().is_applicable_operator(op) or op.id in self.player.current_challenge.categories

    def apply_operator(self, op: 'Operator'):
        if super().is_applicable_operator(op):
            return super().apply_operator(op)
        if self.news_index + 1 < len(self.player.current_challenge.to_sort):
            ns = NewsSortChallengeState(self)
            ns.player.current_challenge.sort_to(self.player.current_challenge.to_sort[self.news_index], op.id)
            return ns
        else:
            ns = ChallengeMenuState(self)
            global OPERATORS
            OPERATORS.clear()
            OPERATORS += Operator.all_ops
            passed, corr = ns.player.current_challenge.submit(ns.player)
            if passed:
                return MessageDisplayState(ns.check_win_lose_state(), "Great job!", f"You solved the challenge with a {int(corr * 100)}% completion!")
            else:
                return MessageDisplayState(ns.check_win_lose_state(), "Nice try!", f"You only have {int(corr * 100)}% completion.")

    def __str__(self):
        return (f"{super().__str__()}\nNews: {self.player.current_challenge.to_sort[self.news_index]}"
                f"\tNews sorted: {self.news_index}/{len(self.player.current_challenge.to_sort)}\nWhich category should this news belong to?")


class Challenges:
    all = [
        (lambda level: NewsSortChallenge.random(level), lambda old, challenge: NewsSortChallengeState(old=old, challenge=challenge))
    ]


def goal_message(s: State) -> str:
    return s.goal_message()


def copy_state(old: State) -> State:
    if isinstance(old, GameStartState):
        return GameStartState()
    if isinstance(old, ChallengeMenuState):
        return ChallengeMenuState(old)
    if isinstance(old, MessageDisplayState):
        return MessageDisplayState(old.continue_to, old.title, old.info)
    if isinstance(old, GameEndState):
        return GameEndState(old.player, old.title, old.info)
    if issubclass(type(old), State):
        clone = object.__new__(type(old))
        clone.__init__(old=old)
        return clone
    raise TypeError()


class OperatorIds(Enum):
    MENU_CONTINUE = "Continue..."
    CHALLENGE_ACCEPT = "Accept the challenge"
    CHALLENGE_DECINE = "Decine the challenge"
    CHALLENGE_CANCEL = "Cancel the accepted challenge"
    PAY_DEBT = "Pay for the debt"
    FINISH_ROUND = "End round"


class Operator:
    def __init__(self, name, id):
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
