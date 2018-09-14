'''InfoFlow.py
("InfoFlow" problem)
A SOLUZION problem formulation.  UPDATED SEP 2018.
The XML-like tags used here may not be necessary, in the end.
But for now, they serve to identify key sections of this
problem formulation.  It is important that COMMON_CODE come
before all the other sections (except METADATA), including COMMON_DATA.
'''
# <METADATA>
SOLUZION_VERSION = "4.0"
PROBLEM_NAME = "Info Flow"
PROBLEM_VERSION = "4.0"
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
-------------------------------------------------------------------------------------------------------------
    You are a college student. Yesterday, there was a group of people breaking into your house and telling you that
your father owes them a huge amount of money ($300) in gambling. You have decided to drop school and pay off the debt.
You have no solidified skills but the only platform as mentioned earlier. If you cannot pay off the debt on time,
you will be captured and treated in a way you could never think of. You are asked to complete assigned challenges
to pay off your debt. Today, you will be facing your first challenge from this platform. What will that be...?'''
)
# </METADATA>

# <COMMON_CODE>
from copy import deepcopy
from enum import Enum
from itertools import chain
from random import randrange, choice
from typing import List, Dict, Set


class Debug:
    debug = False  # DEBUG


class PlayerInfo:
    def __init__(self, difficulty_level: int = 0,
                 score: int = 0,
                 finished: int = 0,
                 unfinished: int = 0,
                 canceled: int = 0,
                 challenge_count: int = 0,
                 money: int = 0 if not Debug.debug else 100,
                 debt: int = 300 if not Debug.debug else 100,
                 energy: int = 100,
                 info_got: int = 0,
                 current_challenge: 'Challenge' = None,
                 set_game_finished: bool = False,
                 is_game_finished: bool = False):
        self._difficulty_level = difficulty_level
        self.score = score
        self.finished = finished
        self.unfinished = unfinished
        self.canceled = canceled
        self.challenge_count = challenge_count
        self.money = money
        self._debt = debt
        self._energy = energy
        self.info_got = info_got
        self.current_challenge = current_challenge
        self.set_game_finished = set_game_finished
        self.is_game_finished = is_game_finished

    @property
    def difficulty_level(self):
        return self._difficulty_level

    @difficulty_level.setter
    def difficulty_level(self, val):
        self._difficulty_level = 0 if val < 0 else 4 if val > 4 else val

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

    def add_info_got(self, num: int):
        self.info_got += num

    def __eq__(self, other):
        if other is self:
            return True
        if other is None:
            return False
        return (self.energy is other.energy
                and self.score is other.score
                and self.finished is other.finished
                and self.unfinished is other.unfinished
                and self.canceled is other.canceled
                and self.challenge_count is other.challenge_count
                and self.money is other.money
                and self.debt is other.debt
                and self.energy is other.energy
                and self.info_got is other.info_got
                and self.difficulty_level is other.difficulty_level
                and self.has_accepted_challenge() is other.has_accepted_challenge()
                and self.current_challenge is other.current_challenge
                and self.set_game_finished is other.set_game_finished
                and self.is_game_finished is other.is_game_finished)

    def __str__(self):
        block_full, block_three_forth, block_half, block_one_fourth, block_empty = '█', '▊', '▌', '▎', '　'
        energy_blocks = block_full * (self.energy // 20)
        energy_rest = self.energy % 20
        energy_rest = block_three_forth if energy_rest >= 15 else block_half if energy_rest >= 10 else block_one_fourth if energy_rest >= 5 else ''
        energy_spaces = block_empty * max(0, 5 - len(energy_blocks) - len(energy_rest))
        return (f"Player Stats:"
                f"\tEnergy: {self.energy:3}▕{energy_blocks}{energy_rest}{energy_spaces}▏"
                f"\tScore: {self.score}"
                f"\tFinished/All Challenges: {self.finished}/{self.challenge_count}"
                f"\tMoney/Debt: ${self.money}/${self.debt}"
                f"\tDifficulty Level: {self.difficulty_level}"
                f"\tHas accepted challenge: {'✔' if self.has_accepted_challenge() else '×'}")

    @staticmethod
    def clone(info: 'PlayerInfo'):
        return PlayerInfo(info.difficulty_level, info.score, info.finished, info.unfinished, info.canceled, info.challenge_count,
                          info.money, info.debt, info.energy, info.info_got,
                          info.current_challenge, info.set_game_finished, info.is_game_finished)


class OperatorIds(Enum):
    MENU_CONTINUE = "Continue..."
    CHALLENGE_ACCEPT = "Accept the challenge"
    CHALLENGE_DECLINE = "Decline the challenge"
    CHALLENGE_CANCEL = "Cancel the accepted challenge"
    PAY_DEBT = "Pay off the debt"
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
    challenge_rewards = [100, 200, 300, 400, 500]  # from 0 to 5 (inclusive)
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
        p.challenge_count += 1
        p.difficulty_level -= 1

    def cancel(self, p: 'PlayerInfo') -> None:
        p.score += Challenge.score_cancel_multiplier_level * self.level
        p.money += Challenge.money_cancel_multiplier_level * self.level
        p.canceled += 1
        p.challenge_count += 1

    def submit(self, p: 'PlayerInfo') -> None:
        raise NotImplementedError()

    def __set_score_and_money(self, p: 'PlayerInfo', correct_level: float):
        p.score += self.level * Challenge.score_correct_multiplier_level
        p.money += Challenge.challenge_rewards[self.level] * Challenge.reward_completion_multiplier[int(correct_level * 5)]

    def set_finished(self, p: 'PlayerInfo', correct_level: float):
        self.__set_score_and_money(p, correct_level)
        p.finished += 1
        p.challenge_count += 1
        p.difficulty_level += 1

    def set_unfinished(self, p: 'PlayerInfo', correct_level: float):
        # self.__set_score_and_money(p, correct_level)
        p.unfinished += 1
        p.challenge_count += 1
        p.difficulty_level -= 1

    def energy_consume(self):
        return (self.level + 5) * Challenge.energy_accept_multiplier_level

    def preview(self) -> str:
        return f"{self.name}(Level: {self.level})"

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
        self.store_operator(op)
        ns = copy_state(self)
        if op.id is OperatorIds.FINISH_ROUND:
            ns.round += 1
            ns.player.energy += 80  # Recover 80% of total energy after each round
            ns.player.debt = int(ns.player.debt * 1.03)  # Add 3% debt according to the remaining debt after each round
        elif op.id is OperatorIds.PAY_DEBT:
            if not ns.player.is_game_finished:
                if ns.player.money > 0:
                    to_pay = min(ns.player.debt, ns.player.money)
                    ns.player.debt -= to_pay
                    ns.player.money -= to_pay
                    return MessageDisplayState.show_message(ns.check_win_lose_state(), "Great!", f"${to_pay} is paid off your debt.")
                else:
                    return MessageDisplayState.show_message(ns.check_win_lose_state(), "Failed!", "You don't have any money to pay off your debt!")
            else:
                return MessageDisplayState.show_message(ns.check_win_lose_state(), "Failed!", "You have already paid all the debt!")
        return ns.check_win_lose_state()

    def store_operator(self, op: 'Operator'):
        self.selected_operator = op

    def set_goal_state(self):
        self.is_goal_state = True
        return self

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
            return MessageDisplayState.show_message(ns, "Congratulations!", self.goal_message()).set_goal_state()
        return self

    def __is_goal(self) -> bool:
        return self.player.debt is 0

    def is_goal(self) -> bool:
        if not self.player.is_game_finished and self.player.set_game_finished and "is_goal_state" in self.__dict__ and self.__is_goal():
            self.player.is_game_finished = True
            return True
        else:
            return False

    def goal_message(self) -> str:
        declined = self.player.challenge_count - self.player.finished - self.player.unfinished - self.player.canceled
        return (f"You makes the goal in {self.round} round{'s' if self.round > 1 else ''} with a score of {self.player.score}. "
                f"You payed all the debt and there is ${self.player.money} left. Throughout the game, "
                f"you solved {self.player.finished} challenges in total, "
                + ("no challenge is" if self.player.challenge_count is 0 else f"{self.player.challenge_count} challenge{'s are' if self.player.challenge_count > 1 else ' is'}") + " accepted, "
                + ("no challenge is" if self.player.canceled is 0 else f"{self.player.canceled} challenge{'s are' if self.player.challenge_count > 1 else ' is'}") + " canceled, "
                + ("and no challenge is" if declined is 0 else f"and {declined} challenge{'s are' if declined > 1 else ' is'}") + " declined. "
                + f"You read about {self.player.info_got + 40} pieces of information during this game. "
                  f"Maybe you did not realize, but here is how much information you just received "
                  f"(not reach since you are actually dealing with them) in one game. "
                  f"Will you feel tired after finishing one day’s work but actually not having too much workload? "
                  f"It is mostly because you are reaching information while you did not notice. "
                  f"Emails, videos, Facebook and twitter: all kinds of information are attacking your brain. "
                  f"Also, this is why we make ‘Info Flow’ for this wicked problem (information overload), "
                  f"and here is a tip for all of you who played this game:\n"
                  f"    Stop using your smart device for a while and let your brain take a break.")

    def describe_state(self) -> str:
        return ""

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
        self.store_operator(op)
        return ChallengeMenuState(self)

    def describe_state(self) -> str:
        return f"{GameStartState.text_background}"

    def __str__(self):
        return f"{super().__str__()}\n{self.describe_state()}"


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
                         or op.id is OperatorIds.CHALLENGE_DECLINE)))

    def apply_operator(self, op: 'Operator'):
        self.store_operator(op)
        if super().is_applicable_operator(op):
            return super().apply_operator(op)
        if op.id is OperatorIds.CHALLENGE_ACCEPT:
            ns = self.random_challenge[1](self)
            ns.player.current_challenge = self.random_challenge[0]
            ns.player.current_challenge.accept(ns.player)
            return ns.check_win_lose_state()
        elif op.id is OperatorIds.CHALLENGE_DECLINE:
            ns = ChallengeMenuState(old=self)
            ns.random_challenge[0].decline(ns.player)
            ns.random_challenge = ns.__random_challenge()
            return ns.check_win_lose_state()

    def describe_state(self) -> str:
        return f"You have a challenge available: {self.random_challenge[0].preview()}."

    def __str__(self):
        return f"{super().__str__()}\n{self.describe_state()}"


class ChallengeState(State):
    def __init__(self, old: 'State' = None):
        super().__init__(old)

    def is_applicable_operator(self, op: 'Operator'):
        return op.id is OperatorIds.CHALLENGE_CANCEL

    def apply_operator(self, op: 'Operator'):
        if op.id is OperatorIds.CHALLENGE_CANCEL:
            ns = ChallengeMenuState(self)
            ns.player.current_challenge.cancel(ns.player)
            return ns


class MessageDisplayState(State):
    def __init__(self, continue_to: 'State' = None, title: str = None, info: str = None, show_title: bool = True, old: 'State' = None):
        super().__init__(old)
        self.continue_to = continue_to
        self.title = title
        self.info = info
        self.show_title = show_title

    def is_applicable_operator(self, op: 'Operator'):
        return op.id is OperatorIds.MENU_CONTINUE

    def apply_operator(self, op: 'Operator'):
        self.store_operator(op)
        return self.continue_to

    def describe_state(self) -> str:
        if self.show_title:
            return f"{self.title}\n{self.info}"
        else:
            return self.info

    def __str__(self):
        return f"{super().__str__()}\n{self.describe_state()}"

    def before(self, title: str = None, info: str = None, show_title: bool = True):
        return MessageDisplayState.show_message(self, title, info, show_title)

    @staticmethod
    def show_message(continue_to: 'State', title: str = None, info: str = None, show_title: bool = True, old: 'State' = None):
        return MessageDisplayState(continue_to, title, info, show_title, old=old if old else continue_to)


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
                p.add_info_got(1)
                if info.category == cat:
                    p.score += NewsSortingChallenge.score_correct_info
                    correct += 1
                else:
                    p.score += NewsSortingChallenge.score_incorrect_info
        correct_level = correct / len(self.to_sort)
        if correct_level >= .8:  # Require at least 80% of the information are sorted correctly to get success in this challenge
            self.set_finished(p, correct_level)
            return True, correct_level
        else:
            self.set_unfinished(p, correct_level)
            return False, correct_level

    def __str__(self):
        return (f"{super().__str__()}\tChallenge Level: {self.level}\n"
                "\n".join([f"\t{'{0:3}'.format(ind)}: {info.content}" for ind, info in enumerate(self.to_sort)]))

    def clone(self) -> 'NewsSortingChallenge':
        return NewsSortingChallenge(self.level, self.to_sort, self.categories, self.sorted)

    @staticmethod
    def random(level) -> 'NewsSortingChallenge':
        count = round(level ** 1.5) + 5 if not Debug.debug else 1
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
        self.store_operator(op)
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
            philosophy = """Here is why we made this challenge.
Just like what system did for spam emails, we receive useless information every day in our lives.
Categorizing news is just one small aspect about information, but the point is that we need to learn to accept useful information while refusing the spam ones.
This challenge is a representation of 'Variety' in Big Data."""
            if passed:
                return (MessageDisplayState.show_message(ns, "", philosophy, False)
                        .before("Great job!", f"You solved the challenge with a {int(corr * 100)}% completion!"))
            else:
                return (MessageDisplayState.show_message(ns, "", philosophy, False)
                        .before("Nice try!", f"You only have a {int(corr * 100)}% completion."))

    def describe_state(self) -> str:
        return (f"News: {self.player.current_challenge.to_sort[self.news_index]}"
                f"\t(News sorted: {self.news_index}/{len(self.player.current_challenge.to_sort)})\nWhich category should this news belong to?")

    def __str__(self):
        return f"{super().__str__()}\n{self.describe_state()}"


class Myth:
    def __init__(self, content: str, is_fact: bool):
        self.content = content
        self.is_fact = is_fact

    def __eq__(self, other):
        if other is None:
            return False
        return isinstance(other, type(self)) and self.content == other.content and self.is_fact == other.is_fact

    def __hash__(self):
        return hash(f"{self.content}:{self.is_fact}")

    def __str__(self):
        return self.content


class MythBusterChallenge(Challenge):
    provided_ops = [Operator("Is a Fact", "MYTHBUSTER_FACT"), Operator("Is a Myth", "MYTHBUSTER_MYTH")]
    all_myths = [
        Myth("Glass Is a Slow-moving Liquid.", False),
        Myth("Deoxygenated Blood Is Blue.", False),
        Myth("Glass Is a Slow-moving Liquid.", False),
        Myth("Deoxygenated Blood Is Blue.", False),
        Myth("You lose most of your body heat through your head", False),
        Myth("Chills don’t make you ill.", False),
        Myth("Hair and fingernails continue to grow after death.", False),
        Myth("Humans use only 10 percent of their brains", False),
        Myth("You can slip on an old banana peel.", False),
        Myth("The color red makes bulls angry.", False),
        Myth("Men are more attracted to blonde women.", False),
        Myth("Cats are deterred by lion feces, aluminum foil, or water bottles.", False),
        Myth("A goldfish's memory is limited to three seconds.", False),
        Myth("Hot-air hand dryers are more sanitary than paper towels.", False),
        Myth("Pouring gasoline down a toilet and igniting it will cause an explosion.", False),
        Myth("Placing a silver spoon in a bottle of champagne will keep it bubblier.", False),
        Myth("Alcohol does not make people look more attractive.", False),
        Myth("Pretty girls do not pass gas.", False),
        Myth("A whole coconut cannot be mailed without packaging.", False),
        Myth("Anti-gravity is possible.", False),
        Myth("Objects of different mass fall not at the same rate.", False),
        Myth("A rock kicked up by a lawnmower cannot deliver the same force as a bullet.", False),
        Myth("A dog bowl cannot focus enough sunlight to start a fire.", False),
        Myth("Using a cell phone while pumping gas will cause an explosion.", False),
        Myth("If a steel cable snaps, it will cut a person in two.", False),
        Myth("It is impossible to make a balloon out of lead.", False),
        Myth("Square wheels do give an advantage in hill climbing.", False),
        Myth("Water falling in front of a speaker cannot appear to freeze in place on camera.", False),
        Myth("It is possible for a person to catch a bullet with their teeth.", False),
        Myth("The Red Cross implants microchips in your bloodstream when you donate blood.", False),
        Myth("A scuba diver can be sucked up by a firefighting helicopter and dumped onto a fire.", False),
        Myth("Launching a human with water bottle rockets is feasible.", False),
        Myth("It is feasible to improvise a parachute from materials in a hotel room.", False),
        Myth("A person will not stay drier by running in the rain than by walking.", False),
        Myth("Wind alone can blow the feathers off a chicken.", False),
        Myth("Sounds can be recovered from the grooves of old pottery.", False),
        Myth("Water that has been microwaved (and cooled), is harmful to plants.", False),
        Myth("A glass of water cannot superheat in a microwave and boil over dangerously when removed.", False),
        Myth("A truck carrying birds will be lighter if the birds are flying instead of standing.", False),
        Myth("Eating poppy seeds cannot lead to a positive drug test for opioids.", False),
        Myth("A turkey can be cooked using a microwave radio or a radar antenna.", False),
        Myth("It is possible to swallow a spoonful of ground cinnamon without drinking water.", False),
        Myth("Rum is better at cleaning clothes than detergent.", False),
        Myth("A person's eyes will fly out if they sneeze with their eyes open.", False),
        Myth("Healthy people can easily avoid germs if a sick person makes no effort to contain them.", False),
        Myth("Using a hands-free cell phone while driving is not as dangerous as holding the phone.", False),
        Myth("Electric cars are more sluggish than gasoline cars.", False),
        Myth("Used cooking oil cannot be used as fuel in a diesel engine.", False),
        Myth("A cracked egg can plug a radiator leak and cola cannot be used as an emergency coolant.", False),
        Myth("A car could be split in half with a snowplow while the occupants remain unharmed.", False),
        Myth("A driver will not use more fuel when angry.", False),
        Myth("Higher-than-normal tire pressure cannot improve fuel efficiency.", False),
        Myth("McDonalds calls frequent buyers of their food 'heavy users.'", True),
        Myth("The average person spends 6 months of their lifetime waiting on a red light to turn green.", True),
        Myth("The largest recorded snowflake was in Keogh, MT during year 1887, and was inches wide.", True),
        Myth("You burn more calories sleeping than you do watching television.", True),
        Myth("There are more lifeforms living on your skin than there are people on the planet.", True),
        Myth("If you believe that you’re truly one in a million, there are still approximately 7,18more people out there just like you.", True),
        Myth("A single cloud can weight more than million pounds.", True),
        Myth("A human will eat on average 70 assorted insects and 10 spiders while sleeping.", True),
        Myth("James Buchanan, the 15th U. president continuously bought slaves with his own money in order to free them.", True),
        Myth("There are more possible iterations of a game of chess than there are atoms in the known universe.", True),
        Myth("The average person walks the equivalent of three times around the world in a lifetime.", True),
        Myth("Men are 6 times more likely to be struck by lightning than women.", True),
        Myth("Coca-Cola would be green if coloring wasn’t added to it.", True),
        Myth("You cannot snore and dream at the same time.", True),
        Myth("The world’s oldest piece of chewing gum is over 9,000 years old!", True),
        Myth("Bolts of lightning can shoot out of an erupting volcano.", True),
        Myth("New York drifts about one inch farther away from London each year.", True),
        Myth("A U. dollar bill can be folded approximately 4,000 times in the same place before it will tear.", True),
        Myth("A sneeze travels about 100 miles per hour.", True),
        Myth("Earth has traveled more than 5,000 miles in the pastminutes.", True),
        Myth("It would take a sloth one month to travel one mile.", True),
        Myth("10% of the World’s population is left handed.", True),
        Myth("A broken clock is right two times every day.", True),
        Myth("According to Amazon, the most highlighted books on Kindle are the Bible, the Steve Jobs biography, and The Hunger Games.", True),
        Myth("Bob Marley’s last words to his son before he died were “Money can’t buy life.”", True),
        Myth("A mole can dig a tunnel that is 300 feet long in only one night.", True),
        Myth("A hippo’s wide open mouth is big enough to fit a 4-foot-tall child in.", True),
        Myth("Chewing gum while you cut an onion will help keep you from crying.", True),
        Myth("If you were to stretch a Slinky out until it’s flat, it would measure 8 feet long.", True),
        Myth("Al Capone’s business card said he was a used furniture dealer", True),
        Myth("There are more collect calls on Father’s Day than on any other day of the year.", True),
        Myth("Banging your head against a wall burns 150 calories an hour.", True),
        Myth("95% of people text things they could never say in person.", True),
        Myth("A crocodile can’t poke its tongue out.", True),
        Myth("It is physically impossible for pigs to look up into the sky.", True),
        Myth("Guinness Book of Records holds the record for being the book most often stolen from Public Libraries.", True),
        Myth("Drying fruit depletes it of 30-80% of its vitamin and antioxidant content", True),
        Myth("A 2010 study found that 48% of soda fountain contained fecal bacteria, and 11% contained  Coli.", True),
        Myth("9 out of 10 Americans are deficient in Potassium.", True),
        Myth("Blueberries will not ripen until they are picked.", True),
        Myth("About 150 people per year are killed by coconuts.", True),
        Myth("Ketchup was used as a medicine back in the 1930’s.", True),
        Myth("Honey never spoils.", True),
        Myth("About half of all Americans are on a diet on any given day.", True),
        Myth("A hardboiled egg will spin, but a soft-boiled egg will not.", True),
        Myth("Avocados are poisonous to birds.", True),
        Myth("Chewing gum burns about 1calories per hour.", True),
        Myth("The number of animals killed for meat every hour in the U. is 500,000.If you try to suppress a sneeze, you can rupture a blood vessel in your head or neck "
             "and die.Celery has negative calories! It takes more calories to eat a piece of celery than the celery has in it to begin wit It’s the same with apples!More people are allergic "
             "to cow’s milk than any other food.Only 8% of dieters will follow a restrictive weight loss plan (such as hCG Drops diet, garcinia cambogia diet, etc.), "
             "Coconut water can be used as blood plasma.", True),
        Myth("Human thigh bones are stronger than concrete.", True),
        Myth("Cockroaches can live for several weeks with their heads cut off, because their brains are located inside their bod They would eventually die from being unable to eat.", True),
        Myth("Scientists have tracked butterflies that travel over 3,000 miles.", True),
        Myth("To produce a single pound of honey, a single bee would have to visit million flowers.", True),
        Myth("The population is expected to rise to 10.8 billion by the year 2080.", True),
        Myth("You breathe on average about 8,409,600 times a year", True),
        Myth("More than 60,000 people are flying over the United States in an airplane right now.", True),
        Myth("Hamsters run up to 8 miles at night on a wheel.", True),
        Myth("A waterfall in Hawaii goes up sometimes instead of down.", True),
        Myth("A church in the Czech Republic has a chandelier made entirely of human bones.", True),
        Myth("Under the Code of Hammurabi, bartenders who watered down beer were punished by execution.", True),
        Myth("Our eyes are always the same size from birth, but our nose and ears never stop growing.", True),
        Myth("During your lifetime, you will produce enough saliva to fill two swimming pools.", True),
        Myth("You are 1% shorter in the evening than in the morning", True),
        Myth("The elephant is the only mammal that can’t jump!", True),
        Myth("Most dust particles in your house are made from dead skin!", True)
    ]

    level_correct_required = [.66, .72, .78, .84, .9]
    score_correct_guess = 10
    score_incorrect_guess = -20

    def __init__(self, level: int, myths: 'List[Myth]', guesses: 'Dict[Myth, bool]'):
        super().__init__("Myth Buster Challenge", level)
        self.myths = myths
        # Guess = True if the player think it is a fact; otherwise, should be False
        self.guesses = guesses

    def guess(self, myth: 'Myth', guess: bool):
        self.guesses[myth] = guess
        return myth.is_fact == guess

    def submit(self, p: 'PlayerInfo'):
        correct = 0
        for myth, guess in self.guesses.items():
            p.add_info_got(1)
            if myth.is_fact == guess:
                correct += 1
        correct_level = correct / len(self.myths)
        if correct_level >= self.level_correct_required[self.level]:  # Require at least a specific amount of the information are sorted correctly to get success in this challenge
            self.set_finished(p, correct_level)
            return True, correct_level
        else:
            self.set_unfinished(p, correct_level)
            return False, correct_level

    def clone(self):
        return MythBusterChallenge(self.level, deepcopy(self.myths), deepcopy(self.guesses))

    @staticmethod
    def random(level):
        count = level + 5 if not Debug.debug else 1
        myths = set()
        while len(myths) < count:
            myths.add(choice(MythBusterChallenge.all_myths))
        return MythBusterChallenge(level, list(myths), {})


class MythBusterChallengeState(ChallengeState):
    def __init__(self, old: 'State' = None):
        super().__init__(old)
        self.myth_index = old.myth_index + 1 if old and isinstance(old, MythBusterChallengeState) else 0

    def is_applicable_operator(self, op: 'Operator'):
        return super().is_applicable_operator(op) or op in MythBusterChallenge.provided_ops

    def apply_operator(self, op: 'Operator'):
        self.store_operator(op)
        if super().is_applicable_operator(op):
            return super().apply_operator(op)
        if self.myth_index + 1 < len(self.player.current_challenge.myths):
            ns = MythBusterChallengeState(self)
            ret = ns.player.current_challenge.guess(self.player.current_challenge.myths[self.myth_index], op.id is MythBusterChallenge.provided_ops[0].id)
            info = "It is a truth!" if self.player.current_challenge.myths[self.myth_index].is_fact else "It is a myth!"
            ns.player.score += MythBusterChallenge.score_correct_guess if ret else MythBusterChallenge.score_incorrect_guess
            return MessageDisplayState.show_message(ns, "Correct!" if ret else "Incorrect!", info)
        else:
            ns = ChallengeMenuState(self)
            ret = ns.player.current_challenge.guess(self.player.current_challenge.myths[self.myth_index], op.id is MythBusterChallenge.provided_ops[0].id)
            info = "It is a truth!" if self.player.current_challenge.myths[self.myth_index].is_fact else "It is a myth!"
            philosophy = """It is hard to identify all those myths, right? I cannot believe some of them are myths when I found them on the internet, neither. 
Actually, maybe you did not realize, we are surrounded by fake news and information. 
This challenge is a representation of ‘Veracity’ in Big Data."""
            passed, corr = ns.player.current_challenge.submit(ns.player)
            ns.finish_challenge()
            if passed:
                return (MessageDisplayState.show_message(ns, "", philosophy, False)
                        .before("Great job!", f"You solved the challenge with a {int(corr * 100)}% completion!")
                        .before("Correct!" if ret else "Incorrect!", info))
            else:
                return (MessageDisplayState.show_message(ns, "", philosophy, False)
                        .before("Nice try!", f"You only have a {int(corr * 100)}% completion.")
                        .before("Correct!" if ret else "Incorrect!", info))

    def describe_state(self) -> str:
        return (f"Myth's Content: {self.player.current_challenge.myths[self.myth_index]}"
                f"\t(Myth Guessed: {self.myth_index}/{len(self.player.current_challenge.myths)})\nFACT or MYTH?")

    def __str__(self):
        return f"{super().__str__()}\n{self.describe_state()}"


class InstantMemChallenge(Challenge):
    provided_ops = list([Operator("First", "INSTANTMEM_FIRST"), Operator("Second", "INSTANTMEM_SECOND"), Operator("Third", "INSTANTMEM_THIRD")])
    all_sentences = [
        ["A woman weighs the positive and negative aspects of accepting a new job.",
         "A woman does not correct a stranger who mistakes her for someone else",
         "A woman impersonates someone else to seek revenge on an acquaintance."],
        ["It acknowledges that a practice favored by the author of the passage has some limitations.",
         "It illustrates with detail the arguments made in the first two paragraphs of the passage",
         "It gives an overview of a problem that has not been sufficiently addressed by the experts mentioned in the passage."],
        ["A new discovery leads to reconsideration of a theory; a classic study is adapted, and the results are summarized.",
         "An experiment is proposed but proves unworkable; a less ambitious experiment is attempted, and it yields data that give rise to a ne",
         "An anomaly is observed and simulated experimentally; the results are compared with previous findings, and a novel hypothesis is prop"],
        ["Women are not naturally suited for the exercise of civil and political rights.",
         "Men and women possess similar degrees of reasoning ability.",
         "Women do not need to remain confined to their traditional family duties."],
        ["Honeybees that are exposed to both pyrethrums and mites are likely to develop a secondary infection by a virus, a bacterium, or a fu",
         "Beekeepers who feed their honeybee colonies a diet of a single crop need to increase the use of insecticides to prevent mite infesta",
         "A honeybee diet that includes pyrethrums results in honeybee colonies that are more resistant to mite infestations."],
        ["Aside from lowering worker productivity,artificial light sources are also costly, typically constituting anywhere from 25 to 50 perc",
         "The cost of artificial light sources, aside from lowering worker productivity, typically constitutes anywhere from 25 to 50 percent",
         "Typically constituting 25 to 50 percent of a building’s energy use, artificial light sources lower worker productivity and are costl"],
        ["The growth of Harvey’s business coincided with the expansion of the Santa Fe Railway, which served large sections of the American We",
         "Harvey would end up opening dozens of restaurants and dining cars, plus 15 hotels, over his lucrative career.",
         "These benefits enabled the Harvey Girls to save money and build new and exciting lives for themselves in the so-called Wild West."],
        ["Many of the improvements to fruit quality they have discovered so far have required trade-offs in other properties of the fruit.",
         "For now many fruit sellers must weigh the relative values of aroma, color, and freshness when deciding whether to use 1-MCP.",
         "It must be acknowledged that 1-MCP, despite some inadequacies, has enabled the fruit industry to ship and store fruit in ways that w"],
        ["A character describes his dislike for his new job and considers the reasons why.",
         "Two characters employed in the same office become increasingly competitive.",
         "A young man regrets privately a choice that he defends publicly."],
        ["Fair trade coffee consistently earned greater profits than regular coffee earned.",
         "The profits earned from regular coffee did not fluctuate.",
         "Fair trade coffee profits increased between 2004 and 2006."],
        ["Expected tax increases due to demand for public works.",
         "Economic hardship due to promises made in past years.",
         "Greater overall prosperity due to an increased inner-city tax base."],
        ["Large numbers of people moved from suburban areas to urban areas in the 1990s.",
         "Growth rates fell in smaller metropolitan areas in the 1990s.",
         "Large numbers of people moved from metropolitan areas to nonmetropolitan areas in the 1990s."],
        ["One character argues with another character who intrudes on her home.",
         "One character receives a surprising request from another character.",
         "One character reminisces about choices she has made over the years."],
        ["Computer-savvy children tend to demonstrate better hand-eye coordination than do their parents.",
         "Those who criticize consumers of electronic media tend to overreact in their criticism.",
         "Improved visual-spatial skills do not generalize to improved skills in other areas."],
        ["Acting on empathy can be counterproductive.",
         "Ethical economics is defined by character.",
         "Ethical economics is still possible."],
        ["The greatest cooling during the Little Ice Age occurred hundreds of years after the temperature peaks of the Medieval Warm Period.",
         "The sharp decline in temperature supports the hypothesis of an equatorial volcanic eruption in the Middle Ages.",
         "Pyroclastic flows from volcanic eruptions continued for hundreds of years after the eruptions had ended."],
        ["GTC has invested a great deal of money in the microinjection technique",
         "GTC’s milking parlors have significantly increased milk production.",
         "ATryn has proved to be a financially beneficial product for GTC."],
        ["Less growth in metropolitan areas of all sizes than had taken place in the 1990s.",
         "More growth in small metropolitan areas than in large metropolitan areas.",
         "A significant decline in the population of small metropolitan areas compared to the 1980s"],
        ["The 2010 census demonstrated a sizeable growth in the number of middle-class families moving into inner cities.",
         "The 2010 census is not a reliable instrument for measuring population trends in American cities.",
         "Population growth and demographic inversion are distinct phenomena, and demographic inversion is evident in many American cities."],
        ["The North Pole is farther away than the cities usually reached by train.",
         "People often travel from one city to another without considering the implications.",
         "Reaching the North Pole has no foreseeable benefit to humanity."]
    ]

    score_correct_sentences = 10
    score_incorrect_sentences = -20
    level_correct_required = [.75, .5, .85, .9, .95]

    def __init__(self, level: int, sentences: 'Dict[int, (int, int)]', to_remember: 'List[int]', remembered: 'Dict[int]'):
        super().__init__("InstantMem Challenge", level)
        #  Stores {Index from 0 : (Index in InstantMemChallenge.all_sentences, Which one to remember)}
        self.sentences = sentences
        # Stores Index in self.sentences
        self.to_remember = to_remember
        # Stores {Index from 0 : Selected choices}
        self.remembered = remembered

    def submit(self, p: 'PlayerInfo'):
        correct = 0
        for i in range(len(self.remembered)):
            p.add_info_got(3)
            if self.sentences[i][1] == self.remembered[i]:
                correct += 1
                p.score += InstantMemChallenge.score_correct_sentences
            else:
                p.score -= InstantMemChallenge.score_incorrect_sentences
        correct_level = correct / len(self.to_remember)
        if correct_level >= InstantMemChallenge.level_correct_required[self.level]:
            self.set_finished(p, correct_level)
            return True, correct_level
        else:
            self.set_unfinished(p, correct_level)
            return False, correct_level

    def clone(self):
        return InstantMemChallenge(self.level, deepcopy(self.sentences), deepcopy(self.to_remember), deepcopy(self.remembered))

    @staticmethod
    def random(level: int) -> "InstantMemChallenge":
        count = (level + 2) * 2 if not Debug.debug else 1
        count_tr = level + 1 if not Debug.debug else 1
        sentence_set, sentences, to_remember = set(), {}, []
        c = 0
        while len(sentence_set) < count:
            r = randrange(0, len(InstantMemChallenge.all_sentences))
            if r not in sentence_set:
                sentence_set.add(r)
                sentences[c] = (r, randrange(0, 3))
                c += 1
                if len(to_remember) < count_tr:
                    to_remember.append(c)
        return InstantMemChallenge(level, sentences, to_remember, {})


class InstantMemChallengeState(ChallengeState):
    def __init__(self, old: 'State' = None):
        super().__init__(old)
        if old and isinstance(old, InstantMemChallengeState):
            self.phase_index = old.phase_index
            self.instant_mem_index = old.instant_mem_index + 1
        else:
            self.phase_index = 0
            self.instant_mem_index = 0

    def is_applicable_operator(self, op: 'Operator'):
        return (super().is_applicable_operator(op)
                or (self.phase_index is 0 and op.id is OperatorIds.MENU_CONTINUE)
                or (self.phase_index is 1 and op in InstantMemChallenge.provided_ops))

    def apply_operator(self, op: 'Operator'):
        self.store_operator(op)
        if super().is_applicable_operator(op):
            return super().apply_operator(op)
        if self.phase_index is 0:
            ns = InstantMemChallengeState(self)
            if ns.instant_mem_index == len(ns.player.current_challenge.sentences):
                ns.phase_index = 1
                ns.instant_mem_index = 0
                return MessageDisplayState.show_message(ns, "Warning~", "Now is the time to test your memorizations. Hope you still remember these information!")
            else:
                return ns
        elif self.phase_index is 1:
            if self.instant_mem_index + 1 < len(self.player.current_challenge.to_remember):
                ns = InstantMemChallengeState(self)
                ns.player.current_challenge.remembered[self.instant_mem_index] = (
                    0 if op.id is InstantMemChallenge.provided_ops[0]
                    else 1 if op.id is InstantMemChallenge.provided_ops[1]
                    else 2 if op.id is InstantMemChallenge.provided_ops[2]
                    else -1)
                return ns
            else:
                ns = ChallengeMenuState(self)
                ns.player.current_challenge.remembered[self.instant_mem_index] = (
                    0 if op.id is InstantMemChallenge.provided_ops[0].id
                    else 1 if op.id is InstantMemChallenge.provided_ops[1].id
                    else 2 if op.id is InstantMemChallenge.provided_ops[2].id
                    else -1)
                philosophy = """In fact, all those statements are from the Official Guide of SAT test. So you can relax because you won't see things like this in your daily life ^^.
But it is still a miniature of all information we receive. Just imagine, we are exposed to approximately 34 gigabytes of information while most of them are spam.
This challenge is a representation of 'Volume' in Big Data."""
                passed, corr = ns.player.current_challenge.submit(ns.player)
                ns.finish_challenge()
                if passed:
                    return (MessageDisplayState.show_message(ns, "", philosophy, False)
                            .before("Great job!", f"You solved the challenge with a {int(corr * 100)}% completion!"))
                else:
                    return (MessageDisplayState.show_message(ns, "", philosophy, False)
                            .before("Nice try!", f"You only have a {int(corr * 100)}% completion."))

    def describe_state(self):
        s = self.player.current_challenge.sentences[self.instant_mem_index]
        if self.phase_index is 0:
            return f"Memorize this information:\n    {InstantMemChallenge.all_sentences[s[0]][s[1]]}"
        elif self.phase_index is 1:
            choices = ''.join([f'\n    {InstantMemChallenge.provided_ops[ind].name}: {s}' for ind, s in enumerate(self.player.current_challenge.all_sentences[s[0]])])
            return f"Which was shown before in Memorization #{self.instant_mem_index}:\n{choices}"

    def __str__(self):
        return f"{super().__str__()}\n{self.describe_state()}"


class Challenges:
    all = [
        (lambda level: NewsSortingChallenge.random(level),
         lambda old: NewsSortingChallengeState(old=old),
         NewsSortingChallenge),
        (lambda level: MythBusterChallenge.random(level),
         lambda old: MythBusterChallengeState(old=old),
         MythBusterChallenge),
        (lambda level: InstantMemChallenge.random(level),
         lambda old: InstantMemChallengeState(old=old),
         InstantMemChallenge)
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
GOAL_TEST = goal_test
# </GOAL_TEST>

# <GOAL_MESSAGE_FUNCTION> (optional)
GOAL_MESSAGE_FUNCTION = goal_message
# </GOAL_MESSAGE_FUNCTION>

# <STATE_VIS>
# </STATE_VIS>
