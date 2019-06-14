import operator as op
from functools import reduce
from deuces import Card
from deuces import Deck
from deuces import Evaluator
import numpy as np
import math
import itertools

class PokerBot:
    board = []
    stackList = []
    bet = 0
    pot = 0
    side_pots = []

    def __init__(self, hand, stack):
        self.hand = hand
        self.stack = stack

    #ranks hand strength with chen formula
    def preflop(self):
        score = 0
        highest_card = max(Card.get_rank_int(self.hand[0]), Card.get_rank_int(self.hand[1]))
        if highest_card == 12:
            score += 10
        elif highest_card == 11:
            score += 8
        elif highest_card == 10:
            score += 7
        elif highest_card == 9:
            score += 6
        elif highest_card <= 8:
            score += highest_card / 2 + 1
        if Card.get_rank_int(self.hand[0]) == Card.get_rank_int(self.hand[1]):
            score = score * 2
            if score < 5:
                score = 5
        if Card.get_suit_int(self.hand[0]) == Card.get_suit_int(self.hand[1]):
            score += 2
        if abs(Card.get_rank_int(self.hand[0]) - Card.get_rank_int(self.hand[1])) == 2:
            score -= 1
        elif abs(Card.get_rank_int(self.hand[0]) - Card.get_rank_int(self.hand[1])) == 3:
            score -= 2
        elif abs(Card.get_rank_int(self.hand[0]) - Card.get_rank_int(self.hand[1])) == 4:
            score -= 4
        elif abs(Card.get_rank_int(self.hand[0]) - Card.get_rank_int(self.hand[1])) >= 5:
            score -= 5
        if abs(Card.get_rank_int(self.hand[0]) - Card.get_rank_int(self.hand[1])) <= 2 \
                and highest_card < 10:
            score += 1
        return math.ceil(score)

    def flop(self):
        return
    def turn(self):
        return
    def river(self):
        return
    def handle_preflop(self):
        strength = self.preflop()
        return 0


class PokerProbabilities:
    @staticmethod
    def is_straight(cards):
        ranks = []
        for card in cards:
            ranks.append(Card.get_rank_int(card))
        ranks.sort()
        is_straight = True
        for r in range(1, len(ranks)):
            if ranks[r] != ranks[r-1] + 1:
                is_straight = False
                break
        return is_straight

    @staticmethod
    def is_flush(cards):
        suit = Card.get_suit_int(cards[0])
        is_flush = True
        for card in cards:
            if Card.get_suit_int(card) != suit:
                is_flush = False
                break
        return is_flush

    @staticmethod
    def same_rank(cards):
        ranks = []
        for card in cards:
            ranks.append(Card.get_rank_int(card))
        same_rank = True
        for r in range(1, len(ranks)):
            if ranks[r] != ranks[r-1]:
                same_rank = False
                break
        return same_rank

    @staticmethod
    def is_straight_flush(cards):
        return PokerProbabilities.is_straight(cards) and PokerProbabilities.is_flush(cards)

    @staticmethod
    def is_full_house(cards):
        ranks = {}
        ranks.update([Card.get_rank_int(cards[0]), 1])
        for c in range(1, len(cards)):
            if Card.get_rank_int(c) in ranks:
                ranks[Card.get_rank_int(c)] += 1
            else:
                ranks.update([Card.get_rank_int(c)], 1)
        count = ranks.values()
        if len(count) == 2 and ((count[0] == 2 and count[1] == 3) or (count[0] == 3 and count[1] == 2)):
            return True
        else:
            return False

    @staticmethod
    def n_choose_r(n, r):
        r = min(r, n - r)
        numerator = reduce(op.mul, range(n, n - r, -1), 1)
        denominator = reduce(op.mul, range(1, r + 1), 1)
        return numerator / denominator

