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
PROBLEM_DESC = (
    '''Welcome to Info Flow!
    In the year 2025 when technology is highly developed, types of jobs that were completed by people are now
replaced by artificial intelligence. Our lives have become more convenient, but people are still struggling for livings.
A platform gradually emerges which offers huge amounts of money for employees. The platform aims to categorize 
complicated information using human power. However, once you choose this platform, all your personal information, 
including privacy, will be released to this platform. It offers a variety of tasks and bonus to its users. 
Some of those challenges are complicated, ranging from physical work to careful thinking.
------------------------------------------------------------------------------------------------------------------------
    You are a college student. Yesterday, there was a group of people breaking into your house and telling you that 
your father owes them a huge amount of money ($10000) in gambling. You have decided to drop school and pay off the debt. 
You have no solidified skills but the only platform as mentioned earlier. If you cannot pay off the debt on time, 
you will be captured and treated in a way you could never think of. You are asked to complete assigned challenges 
to pay off your debt.  Today, you will be facing your first challenge from this platform. What will that be...?'''
)
# </METADATA>

# <COMMON_CODE>
from copy import deepcopy
from enum import Enum
from itertools import chain
from random import choice
from typing import List, Dict


class PlayerInfo:
    def __init__(self, difficulty_level: int = 0,
                 score: int = 0,
                 finished: int = 0,
                 money: int = 0,
                 debt: int = 1000,
                 energy: int = 100,
                 current_challenge: 'Challenge' = None,
                 set_game_finished: bool = False,
                 is_game_finished: bool = False):
        self._difficulty_level = difficulty_level
        self.score = score
        self.finished = finished
        self.money = money
        self._debt = debt
        self._energy = energy
        self.current_challenge = current_challenge
        self.set_game_finished = set_game_finished
        self.is_game_finished = is_game_finished

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
                f"\tDifficulty Level: {self.difficulty_level}"
                f"\tHas accepted challenge: {'✔' if self.has_accepted_challenge() else '×'}")

    @staticmethod
    def clone(info: 'PlayerInfo'):
        return PlayerInfo(info.difficulty_level, info.score, info.finished, info.money, info.debt, info.energy,
                          info.current_challenge, info.set_game_finished, info.is_game_finished)


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

    def set_unfinished(self, p: 'PlayerInfo'):
        p.finished += 1
        p.difficulty_level -= 1

    def energy_consume(self):
        return (self.level + 2) * Challenge.energy_accept_multiplier_level

    def preview(self) -> str:
        return f"{self.name}(Level: {self.level + 1})"

    def __str__(self):
        return self.preview()

    def clone(self):
        raise NotImplementedError()


class State:
    def __init__(self, old: 'State' = None):
        if old:
            self.player = PlayerInfo.clone(old.player)
            self.challenge = old.challenge.clone() if old.challenge else None
            self.round = old.round
        else:
            self.player = PlayerInfo()
            self.challenge = None
            self.round = 1
        self.selected_operator = None

    def is_applicable_operator(self, op: 'Operator') -> bool:
        return op.id is OperatorIds.FINISH_ROUND or op.id is OperatorIds.PAY_DEBT

    def apply_operator(self, op: 'Operator') -> 'State':
        ns = copy_state(self)
        if op.id is OperatorIds.FINISH_ROUND:
            ns.round += 1
            ns.player.energy += 80  # Recover 80% of total energy after each round
            ns.player.debt = int(ns.player.debt * 1.005)  # Add 0.5% debt according to the remaining debt after each round
        elif op.id is OperatorIds.PAY_DEBT:
            if not ns.player.is_game_finished:
                if ns.player.money > 0:
                    to_pay = min(ns.player.debt, ns.player.money)
                    ns.player.debt -= to_pay
                    ns.player.money -= to_pay
                    return MessageDisplayState(ns.check_win_lose_state(), "Great!", f"${to_pay} is paid off your debt.", old=self)
                else:
                    return MessageDisplayState(ns.check_win_lose_state(), "Failed!", "You don't have any money to pay off your debt!", old=self)
            else:
                return MessageDisplayState(ns.check_win_lose_state(), "Failed!", "You have already paid all the debt!", old=self)
        return ns.check_win_lose_state()

    def store_operator(self, op: 'Operator'):
        self.selected_operator = op

    def has_challenge(self) -> bool:
        return self.challenge is not None

    def finish_challenge(self) -> None:
        self.challenge = None
        self.player.current_challenge = None

    def finish_round(self, cls_state) -> 'State':
        ns = object.__new__(cls_state)
        ns.__init__(old=self)
        ns.round += 1
        return ns

    def check_win_lose_state(self):
        if not self.player.is_game_finished and self.__is_goal():
            ns = ChallengeMenuState(self)
            ns.player.set_game_finished = True
            # return MessageDisplayState(ChallengeMenuState(self), "Congratulations!", self.goal_message())
            return ns
        return self

    def __is_goal(self) -> bool:
        return self.player.debt is 0

    def is_goal(self) -> bool:
        if not self.player.is_game_finished and self.player.set_game_finished and self.__is_goal():
            self.player.is_game_finished = True
            return True
        else:
            return False

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


# Tell the background of the game, introduce the game mechanics, and declare the goal
class GameStartState(State):
    text_background = PROBLEM_DESC

    def __init__(self, old: 'State' = None):
        super().__init__(old)

    def is_applicable_operator(self, op: 'Operator'):
        return op.id is OperatorIds.MENU_CONTINUE

    def apply_operator(self, op: 'Operator'):
        return ChallengeMenuState(self)

    def __str__(self):
        return f"{super().__str__()}\nBackground: {GameStartState.text_background}"


class ChallengeMenuState(State):
    def __init__(self, old: 'State' = None):
        super().__init__(old)
        self.random_challenge = list(self.__random_challenge())
        self.random_challenge[0] = self.random_challenge[0].clone()

    def __random_challenge(self):
        c, s, _ = choice(Challenges.all)
        return c(self.player.difficulty_level), s

    def is_applicable_operator(self, op: 'Operator'):
        return (super().is_applicable_operator(op)
                or (not self.has_challenge()
                    and ((self.player.energy >= self.random_challenge[0].energy_consume() and op.id is OperatorIds.CHALLENGE_ACCEPT)
                         or op.id is OperatorIds.CHALLENGE_DECINE)))

    def apply_operator(self, op: 'Operator'):
        if super().is_applicable_operator(op):
            return super().apply_operator(op)
        if op.id is OperatorIds.CHALLENGE_ACCEPT:
            ns = self.random_challenge[1](self)
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
            ns = ChallengeMenuState(self)
            ns.player.current_challenge.cancel(ns.player)
            return ns


class MessageDisplayState(State):
    def __init__(self, continue_to: 'State' = None, title: str = None, info: str = None, old: 'State' = None):
        super().__init__(old)
        if isinstance(old, MessageDisplayState):
            self.continue_to = old.continue_to
            self.title = old.title
            self.info = old.info
        else:
            self.continue_to = continue_to
            self.title = title
            self.info = info

    def is_applicable_operator(self, op: 'Operator'):
        return op.id is OperatorIds.MENU_CONTINUE

    def apply_operator(self, op: 'Operator'):
        return self.continue_to

    def __str__(self):
        return f"{super().__str__()}\n{self.title}\n{self.info}"


class NewsInformation:
    all_categories = ("Business", "Music & Arts", "Health & Medicine", "Nature & Environments", "Politics",
                      "Religion", "Science", "Sports", "Video Games")

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


class NewsSortingChallenge(Challenge):
    provided_ops = list([Operator(f"In category '{cat}'", cat) for cat in NewsInformation.all_categories])
    news_collection = [
        *[NewsInformation("Business", content)
          for content in ["Trump says he's ready to hit China with another $267 billion in tariffs",
                          "Kudlow: Job gains, wage growth show Trump's 'economic boom continues'",
                          "Wells Fargo shares fall after DOJ reportedly examines potential fraud in business banking",
                          "Bank of America downgrades Chevron, citing risk of losing some overseas production deals",
                          "After a Starbucks opens in town, housing prices tend to rise, Harvard study finds",
                          "Morgan Stanley raises its Amazon price target to the highest on Wall Street",
                          "Bitcoin recovers above $7,000 as key South Korean exchange comes back online",
                          "U.S. job growth surges; annual wage gain largest since 2009",
                          "U.S.-Canada trade talks grind on, but 'final' issues unresolved",
                          "Starbucks' Italian dream comes true, but it is not cheap"]],
        *[NewsInformation("Music & Arts", content)
          for content in ["Mac Miller: US rapper 'found dead at home' aged 26",
                          "Spain parishioner botches Jesus and Mary statue restoration",
                          "Burt Reynolds turned down James Bond - and 10 other stars who rejected great roles",
                          "K-Pop band BTS get presidential congrats",
                          "Nicki Minaj wanted to punch Travis Scott in the face over album battle",
                          "Toronto Film Festival: Nine rising stars to watch",
                          "Yazoo Music Festival Free music celebration set for Oct. 6 on city's historic Main Street",
                          "Avril Lavigne says she 'accepted death' before new song",
                          "Eminem's Kamikaze: Is it time for the 'greatest' to quit?",
                          "He used to play heavy metal. Now he’s a rising country star"]],
        *[NewsInformation("Health & Medicine", content)
          for content in ["Probiotics labelled 'quite useless'",
                          "Teenagers who smoke and drink suffer ill effects by age of 17",
                          "Government proposes energy drinks ban for children",
                          "Artificial intelligence used to predict cancer growth",
                          "Doctors’ mental health at tipping point",
                          "How much are good marks due to genes?",
                          "Doctors told to ditch Latin and use 'plain English'",
                          "Gene-editing hope for muscular dystrophy",
                          "Hair transplants: Fighting against my receding hairline",
                          "Use honey first for a cough, new guidelines say"]],
        *[NewsInformation("Nature & Environments", content)
          for content in ["Wind and Solar Farms Can Bring Water to Sahara",
                          "Ancient Farmers Profoundly Changed Our Climate",
                          "Tree Species Distributions in Amazonia Modeled",
                          "Endocrine Disruptors Found in Bottlenose Dolphins",
                          "Global Warming: Worrying Lessons from the Past",
                          "Why Leaf-Eating Asian Monkeys Do Not Have a Sweet Tooth",
                          "Birds Retreating from Climate Change, Deforestation in Honduras Cloud Forests",
                          "When It Rains, Snake Bites Soar",
                          "New Source of Formic Acid Discovered Over Pacific, Indian Oceans",
                          "A massive net is being deployed to pick up plastic in the Pacific",
                          "'Live Fast, Die Young' Lifestyle Reflected in Birds' Feathers"]],
        *[NewsInformation("Politics", content)
          for content in ["Will More Veterans in Politics Make Politics Better?",
                          "10 attacks Obama unleashed on Trump, GOP in midterm speech",
                          "The Point: Barack Obama asked the question everyone's been wondering about the Republican Party",
                          "Dangerous standoff developing in Syria between US and Russia",
                          "US troops seek visas for family of heroic Iraqi interpreter",
                          "Millennial Republican running for Congress in California",
                          "U.S and India bolster military ties with focus on China",
                          "Former FBI official McCabe under grand jury probe",
                          "Mayor vows to make Portland, Ore., 'cleanest and most livable' in US",
                          "Trump: New York Times should publish name of op-ed author"]],
        *[NewsInformation("Religion", content)
          for content in ["County says cross on county seal is historical not religious",
                          "New Jersey, New York announce church abuse investigations",
                          "The Latest: NJ church says it will cooperate with probe",
                          "Parishioner voices frustration over Catholic Church scandal",
                          "'Shame on you': Man interrupts Washington archbishop at Mass",
                          "Nebraska Catholic diocese rocked by old abuse allegations",
                          "Archbishop asks pope to cancel conference on youth",
                          "Pennsylvania bishop punishes predecessor over clergy abuse",
                          "The Latest: McCain returns to DC ahead of Capitol ceremony",
                          "Marc Thiessen: Pope Francis, corruption and what’s next – now I get how the Reformation happened"]],
        *[NewsInformation("Science", content)
          for content in ["Before it burned, Brazil’s National Museum gave much to science",
                          "Jocelyn Bell Burnell wins big physics prize for 1967 pulsar discovery",
                          "5 decades after his death, George Gamow’s contributions to science survive",
                          "Rubidium atoms mimic the Eiffel Tower, a Möbius strip and other 3-D shapes",
                          "‘Accessory to War’ probes the uneasy alliance between space science and the military",
                          "A new material harnesses light to deice surfaces",
                          "Electrons surf protons’ waves in a new kind of particle accelerator",
                          "Newfound skull tunnels may speed immune cells’ trek to brain injuries",
                          "A massive net is being deployed to pick up plastic in the Pacific",
                          "An elusive Higgs boson decay has finally been spotted"]],
         *[NewsInformation("Sports", content)
          for content in ["Texans RT Sentreal Henderson out for season with ankle injury",
                          "Previewing wingers for the 2018 fantasy hockey season",
                          "Nebraska coach questions play in Adrian Martinez injury",
                          "Minshew leads Washington State over San Jose State 31-0",
                          "32 things we learned from Week 1 of the 2018 NFL season",
                          "NFL Week 1 winners, losers: Cowboys offense looks stuck",
                          "Is the 2018 Basketball Hall of Fame class the best ever?",
                          "Kobe Bryant says his fans will 'fall in line' with LeBron James on the Lakers",
                          "Hockey Hall: Please, no more keg stands on Stanley Cup",
                          "NBA team-by-team offseason grades: Who won the summer?"]],
        *[NewsInformation("Video Games", content)
          for content in ["PUBG On PC Gets New Update; Here's The Full Patch Notes",
                          "Final Fantasy Crystal Chronicles Remaster Coming To Nintendo Switch, PS4",
                          "Game Release Dates Of 2018: Spider-Man PS4, Call Of Duty: Black Ops 4, Red Dead Redemption 2",
                          "Pokemon: Let's Go, Pikachu / Eevee Trailer Shows Off Brand-New Moves And Celadon City",
                          "Assassin's Creed Odyssey's Opening Hours Have Two Things We Like, And Two We Don't",
                          "Fortnite: Where Are The Different Stone Heads? (Week 9, Season 5 Challenge Locations)",
                          "League of Legends unveils Odyssey: Extraction PvE mode with new cinematic",
                          "For the first time ever, WoW's top guild will stream its race to beat the brutal new raid",
                          "Rainbow Six Siege game director talks Castle and Thatcher balance reworks",
                          "China takes down Korea to win the 2018 Asian Games"]]
    ]

    score_correct_info = 10
    score_incorrect_info = -20

    def __init__(self, level: int, to_sort: List[NewsInformation], categories: List[str] = None, sorted: Dict[str, List[NewsInformation]] = None):
        super().__init__("News Sorting Challenge", level)
        self.level = level
        self.to_sort = to_sort
        self.categories = deepcopy(categories) if categories else list(set([info.category for info in to_sort]))
        self.categories.sort()
        self.sorted = sorted if deepcopy(sorted) else {}

    def sort_to(self, info: 'NewsInformation', category: 'str'):
        self.sorted.setdefault(category, list())
        self.sorted[category].append(info)

    def remove_from(self, info: 'NewsInformation', category: 'str'):
        if category in self.to_sort and info in self.to_sort[category]:
            self.to_sort[category].remove(info)

    def submit(self, p: 'PlayerInfo'):
        correct = 0
        for cat, infos in self.sorted.items():
            for info in infos:
                if info.category == cat:
                    p.score += NewsSortingChallenge.score_correct_info
                    correct += 1
                else:
                    p.score += NewsSortingChallenge.score_incorrect_info
        correct_level = correct / len(self.to_sort)
        if correct_level >= .8:  # Require at least 80% of the information are sorted correctly to get success in this challenge
            p.score += self.level * Challenge.score_correct_multiplier_level
            p.money += Challenge.challenge_rewards[self.level] * Challenge.reward_completion_multiplier[int(correct_level * 5)]
            self.set_finished(p)
            return True, correct_level
        else:
            self.set_unfinished(p)
            return False, correct_level

    def __str__(self):
        return (f"{super().__str__()}\tChallenge Level: {self.level}\n"
                "\n".join([f"\t{'{0:3}'.format(ind)}: {info.content}" for ind, info in enumerate(self.to_sort)]))

    def clone(self) -> 'NewsSortingChallenge':
        return NewsSortingChallenge(self.level, self.to_sort, self.categories, self.sorted)

    @staticmethod
    def random(level) -> 'NewsSortingChallenge':
        count = int(level ** 1.5) + 10  # TODO Create an appropriate formula based on the level
        to_sort = set()
        while len(to_sort) < count:
            to_sort.add(choice(NewsSortingChallenge.news_collection))
        return NewsSortingChallenge(level, list(to_sort))


class NewsSortingChallengeState(ChallengeState):
    def __init__(self, old: 'State' = None):
        super().__init__(old)
        self.news_index = old.news_index + 1 if old and isinstance(old, NewsSortingChallengeState) else 0

    def is_applicable_operator(self, op: 'Operator'):
        return super().is_applicable_operator(op) or op.id in self.player.current_challenge.categories

    def apply_operator(self, op: 'Operator'):
        if super().is_applicable_operator(op):
            return super().apply_operator(op)
        if self.news_index + 1 < len(self.player.current_challenge.to_sort):
            ns = NewsSortingChallengeState(self)
            ns.player.current_challenge.sort_to(self.player.current_challenge.to_sort[self.news_index], op.id)
            return ns
        else:
            ns = ChallengeMenuState(self)
            ns.player.current_challenge.sort_to(self.player.current_challenge.to_sort[self.news_index], op.id)
            passed, corr = ns.player.current_challenge.submit(ns.player)
            ns.finish_challenge()
            if passed:
                return MessageDisplayState(ns.check_win_lose_state(), "Great job!", f"You solved the challenge with a {int(corr * 100)}% completion!", old=self)
            else:
                return MessageDisplayState(ns.check_win_lose_state(), "Nice try!", f"You only have {int(corr * 100)}% completion.", old=self)

    def __str__(self):
        return (f"{super().__str__()}\nNews: {self.player.current_challenge.to_sort[self.news_index]}"
                f"\t(News sorted: {self.news_index}/{len(self.player.current_challenge.to_sort)})\nWhich category should this news belong to?")


class Challenges:
    all = [
        (lambda level: NewsSortingChallenge.random(level),
         lambda old: NewsSortingChallengeState(old=old),
         NewsSortingChallenge)
    ]


def goal_message(s: State) -> str:
    return s.goal_message()


def copy_state(old: State) -> State:
    if issubclass(type(old), State):
        clone = object.__new__(type(old))
        clone.__init__(old=old)
        return clone
    raise TypeError()


def goal_test(s: 'State') -> bool: return s.is_goal()


# </COMMON_CODE>

# <COMMON_DATA>
# </COMMON_DATA>

# <INITIAL_STATE>
INITIAL_STATE = GameStartState()
# </INITIAL_STATE>

# <OPERATORS>
OPERATORS = Operator.all_ops + list(chain.from_iterable([ch.provided_ops for _, _, ch in Challenges.all]))
# </OPERATORS>

# <GOAL_TEST> (optional)
GOAL_TEST = lambda s: goal_test(s)
# </GOAL_TEST>

# <GOAL_MESSAGE_FUNCTION> (optional)
GOAL_MESSAGE_FUNCTION = goal_message
# </GOAL_MESSAGE_FUNCTION>

# <STATE_VIS>
# </STATE_VIS>
