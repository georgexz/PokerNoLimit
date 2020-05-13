from PokerProbabilities import PokerBot
from SidePot import SidePot
from treys import Card
from treys import Deck
from treys import Evaluator
import random

class Player:
    distanceFromButton = 0
    isSmallBlind = False
    isBigBlind = False
    startingStackSize = 0
    singleRoundMoneyInThePot = 0
    lastAction = 0
    pot_size = 0
    side_pots = []
    actions = []

    def __init__(self, hand, stack, name, n_players):
        self.hand = hand
        self.stack = stack
        self.startingStackSize = stack
        self.n_players = n_players
        self.name = name
        if self.name != "Me":
            self.pokerBot = PokerBot(hand, stack)

    def set_small_blind(self, small_blind):
        self.isSmallBlind = True
        self.isBigBlind = False
        self.stack = self.stack - small_blind
        self.singleRoundMoneyInThePot = small_blind

    def set_big_blind(self, big_blind):
        self.isSmallBlind = False
        self.isBigBlind = True
        self.stack = self.stack - big_blind
        self.singleRoundMoneyInThePot = big_blind

    def finish_betting(self):
        self.singleRoundMoneyInThePot += self.lastAction
        self.lastAction = 0

    def action(self, pot_size, to_call_amount, board, actions):
        self.actions = actions
        if self.name == "Me":
            print("Pot size: " + str(pot_size) + "  To Call: " + str(to_call_amount))
            decision = int(input("Fold: 0, Check: 1, Call: 2, Raise: 3, All in: 4\n"))
            if decision == 3:
                bet = int(input("Raise to: "))
        else:
            self.pokerBot.stack = self.stack
            self.pokerBot.hand = self.hand
            self.pokerBot.board = board
            self.pokerBot.pot = self.pot_size
            self.pokerBot.side_pots = self.side_pots
            self.pokerBot.to_call = to_call_amount
            self.pokerBot.actions = actions
            self.pokerBot.num_players = self.n_players
            if not board:
                decision = self.pokerBot.handle_preflop()
            if len(board) == 3:
                decision = self.pokerBot.handle_flop()
            if len(board) == 4:
                decision = self.pokerBot.handle_turn()
            if len(board) == 5:
                decision = self.pokerBot.handle_river()
            if decision == 3:
                bet = self.pokerBot.bet
        if decision == 0:
            return [self.fold(), 0]
        elif decision == 1:
            if to_call_amount > 0:
                return [self.fold(), 0]
            return[self.check(), 0]
        elif decision == 2:
            if to_call_amount == 0:
                return [self.check(), 0]
            self.lastAction = to_call_amount - self.singleRoundMoneyInThePot
            if self.lastAction > self.stack:
                return [self.go_all_in(), self.lastAction]
            return[self.call(to_call_amount), to_call_amount-self.singleRoundMoneyInThePot]
        elif decision == 3:
            self.lastAction = bet - self.singleRoundMoneyInThePot
            return[self.bet(bet), self.lastAction]
        elif decision == 4:
            print("last action before update: " + str(self.lastAction))
            return[self.go_all_in(), self.lastAction]
        else:
            return [-1,-1]

    def fold(self):
        self.finish_betting()
        return 0

    def check(self):
        return 1

    def call(self, bet_size):
        amount = bet_size - self.singleRoundMoneyInThePot
        self.stack = self.stack - amount
        return 2

    def bet(self, bet_size):
        amount = bet_size - self.singleRoundMoneyInThePot
        if amount < self.stack:
            self.stack = self.stack - amount
            return 3
        else:
            return self.go_all_in()

    def go_all_in(self):
        self.lastAction = self.stack
        print("last action after all in: " + str(self.lastAction))
        self.stack = 0
        return 4
        
    def get_last_action(self):
        return self.lastAction

    def wins_hand(self, pot):
        self.stack = self.stack + pot

    def get_hand(self):
        return self.hand

    def get_stack_size(self):
        return self.stack

    def is_player_small_blind(self):
        return self.isSmallBlind

    def is_player_big_blind(self):
        return self.isBigBlind

    def set_distance_from_button(self, distance):
        self.distanceFromButton = distance

    def get_distance_from_button(self):
        return self.distanceFromButton

