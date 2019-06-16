import operator as op
from functools import reduce
from deuces import Card
from deuces import Deck
from deuces import Evaluator
import numpy as np
import math
import itertools
import random

class PokerBot:
    board = []
    stackList = []
    bet = 0
    pot = 0
    side_pots = []
    to_call = 0
    actions = []

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
        # check for pairs
        strength = 0
        pairs = []
        board_pairs = []
        for c in itertools.combinations(self.hand + self.board, 2):
            if PokerProbabilities.same_rank(c):
                pairs.append(Card.get_rank_int(c[0]))
        for cb in itertools.combinations(self.hand + self.board, 2):
            if PokerProbabilities.same_rank(cb):
                board_pairs.append(Card.get_rank_int(cb[0]))
        board_three = -1
        if PokerProbabilities.same_rank(self.board):
            board_three = Card.get_rank_int(self.board[0])
        three_of_a_kind = -1
        for ci in itertools.combinations(self.hand + self.board, 3):
            if PokerProbabilities.same_rank(ci):
                three_of_a_kind = Card.get_rank_int(ci[0])
        four_of_a_kind = -1
        if PokerProbabilities.same_rank(self.hand):
            for cf in itertools.combinations(self.board, 2):
                if PokerProbabilities.same_rank(cf):
                    if Card.get_rank_int(cf[0]) == Card.get_rank_int(self.hand[0]):
                        four_of_a_kind = Card.get_rank_int(cf[0])

        if four_of_a_kind != -1:
            strength = 20
            return strength
        if four_of_a_kind == -1 and three_of_a_kind != -1:
            strength = 8
            return strength
        if PokerProbabilities.is_straight_flush(self.hand + self.board):
            strength = 25
            return strength
        if PokerProbabilities.is_straight(self.hand + self.board):
            strength = 12
            return strength
        if PokerProbabilities.is_flush(self.hand + self.board):
            strength = 15
            return strength
        if PokerProbabilities.is_full_house(self.hand + self.board):
            strength = 18
            return strength
        if board_three == -1 and three_of_a_kind == -1 and pairs:
            pairs.sort(reverse=True)
            # if pairs are in your hand
            for s in self.hand:
                for i, p in enumerate(pairs):
                    if Card.get_rank_int(s) == p:
                        if i == 0:
                            if p >= PokerProbabilities.highest_card(self.board):
                                strength += 5  # likely top pair
                            else:
                                strength += 4  # low pair
                        if i == 1:
                            strength += 2  # two pair
            return strength
        if not pairs:
            if PokerProbabilities.highest_card(self.hand) > PokerProbabilities.highest_card(self.board):
                strength = 2
            else:
                strength = 1
            return strength
        # contemplate three of a kind possibilities for other players affecting strength of your hand


    def turn(self):
        strength = 0
        pairs = []
        board_pairs = []
        for c in itertools.combinations(self.hand + self.board, 2):
            if PokerProbabilities.same_rank(c):
                pairs.append(Card.get_rank_int(c[0]))
        for cb in itertools.combinations(self.hand + self.board, 2):
            if PokerProbabilities.same_rank(cb):
                board_pairs.append(Card.get_rank_int(cb[0]))
        board_three = -1
        for cn in itertools.combinations(self.board, 3):
            if PokerProbabilities.same_rank(self.board):
                board_three = Card.get_rank_int(cn[0])
        three_of_a_kind = -1

        for ci in itertools.combinations(self.hand + self.board, 3):
            if PokerProbabilities.same_rank(ci):
                three_of_a_kind = Card.get_rank_int(ci[0])
        four_of_a_kind = -1
        if PokerProbabilities.same_rank(self.hand):
            for cf in itertools.combinations(self.board, 2):
                if PokerProbabilities.same_rank(cf):
                    if Card.get_rank_int(cf[0]) == Card.get_rank_int(self.hand[0]):
                        four_of_a_kind = Card.get_rank_int(cf[0])

        if four_of_a_kind != -1:
            strength = 20
            return strength
        if four_of_a_kind == -1 and three_of_a_kind != -1:
            strength = 8
            return strength
        for cm in itertools.combinations(self.hand + self.board, 5):
            if PokerProbabilities.is_straight_flush(cm):
                strength = 25
                return strength
        for cp in itertools.combinations(self.hand + self.board, 5):
            if PokerProbabilities.is_straight(cp):
                strength = 12
                return strength
        for d in itertools.combinations(self.hand + self.board, 5):
            if PokerProbabilities.is_flush(d):
                strength = 15
                return strength
        for v in itertools.combinations(self.hand + self.board, 5):
            if PokerProbabilities.is_full_house(v):
                strength = 18
                return strength
        if board_three == -1 and three_of_a_kind == -1 and pairs:
            pairs.sort(reverse=True)
            # if pairs are in your hand
            for s in self.hand:
                for i, p in enumerate(pairs):
                    if Card.get_rank_int(s) == p:
                        if i == 0:
                            if p >= PokerProbabilities.highest_card(self.board):
                                strength += 5  # likely top pair
                            else:
                                strength += 4  # low pair
                        if i == 1:
                            strength += 2  # two pair
            return strength
        if not pairs:
            if PokerProbabilities.highest_card(self.hand) > PokerProbabilities.highest_card(self.board):
                strength = 2
            else:
                strength = 1
            return strength

    def river(self):
        strength = 0
        pairs = []
        board_pairs = []
        for c in itertools.combinations(self.hand + self.board, 2):
            if PokerProbabilities.same_rank(c):
                pairs.append(Card.get_rank_int(c[0]))
        for cb in itertools.combinations(self.hand + self.board, 2):
            if PokerProbabilities.same_rank(cb):
                board_pairs.append(Card.get_rank_int(cb[0]))
        board_three = -1
        for cn in itertools.combinations(self.board, 3):
            if PokerProbabilities.same_rank(self.board):
                board_three = Card.get_rank_int(cn[0])
        three_of_a_kind = -1

        for ci in itertools.combinations(self.hand + self.board, 3):
            if PokerProbabilities.same_rank(ci):
                three_of_a_kind = Card.get_rank_int(ci[0])
        four_of_a_kind = -1
        if PokerProbabilities.same_rank(self.hand):
            for cf in itertools.combinations(self.board, 2):
                if PokerProbabilities.same_rank(cf):
                    if Card.get_rank_int(cf[0]) == Card.get_rank_int(self.hand[0]):
                        four_of_a_kind = Card.get_rank_int(cf[0])

        if four_of_a_kind != -1:
            strength = 20
            return strength
        if four_of_a_kind == -1 and three_of_a_kind != -1:
            strength = 8
            return strength
        for cm in itertools.combinations(self.hand + self.board, 5):
            if PokerProbabilities.is_straight_flush(cm):
                strength = 25
                return strength
        for cp in itertools.combinations(self.hand + self.board, 5):
            if PokerProbabilities.is_straight(cp):
                strength = 12
                return strength
        for d in itertools.combinations(self.hand + self.board, 5):
            if PokerProbabilities.is_flush(d):
                strength = 15
                return strength
        for v in itertools.combinations(self.hand + self.board, 5):
            if PokerProbabilities.is_full_house(v):
                strength = 18
                return strength
        if board_three == -1 and three_of_a_kind == -1 and pairs:
            pairs.sort(reverse=True)
            # if pairs are in your hand
            for s in self.hand:
                for i, p in enumerate(pairs):
                    if Card.get_rank_int(s) == p:
                        if i == 0:
                            if p >= PokerProbabilities.highest_card(self.board):
                                strength += 5  # likely top pair
                            else:
                                strength += 4  # low pair
                        if i == 1:
                            strength += 2  # two pair
            return strength
        if not pairs:
            if PokerProbabilities.highest_card(self.hand) > PokerProbabilities.highest_card(self.board):
                strength = 2
            else:
                strength = 1
            return strength

    def handle_preflop(self):
        strength = self.preflop()
        if strength >= 12:
            if self.to_call <= 8:
                if self.stack > 50:
                    self.bet = random.randrange(10, 16)
                    return 3
                else:
                    return 4
            else:
                return 2
        elif strength > 7:
            if self.to_call < self.stack/5:
                return 2
            else:
                return 0
        else:
            if self.to_call < 4 and self.stack > self.to_call*10:
                return 1
            else:
                return 0

    def handle_flop(self):
        strength = self.flop()
        if strength >= 12:
            if self.to_call <=8:
                if self.stack > 50:
                    self.bet = random.randrange(10, 16)
                    return 3
                else:
                    return 4
            else:
                return 2
        elif strength >= 5:
            choice = random.randrange(2,4)
            if choice == 3:
                self.bet = random.randrange(2*(self.to_call + 1), 3*(self.to_call + 1))
            return choice
        elif strength >= 4:
            return 2
        else:
            return 1

    def handle_turn(self):
        strength = self.turn()
        if strength >= 12:
            if self.to_call <=8:
                if self.stack > 50:
                    self.bet = random.randrange(10, 16)
                    return 3
                else:
                    return 4
            else:
                return 2
        elif strength >= 5:
            choice = random.randrange(2,4)
            if choice == 3:
                self.bet = random.randrange(2*(self.to_call + 1), 3*(self.to_call + 1))
            return choice
        elif strength >= 4:
            return 2
        else:
            return 1

    def handle_river(self):
        strength = self.river()
        if strength >= 12:
            if self.to_call <= 8:
                if self.stack > 50:
                    self.bet = random.randrange(10, 16)
                    return 3
                else:
                    return 4
            else:
                return 2
        elif strength >= 5:
            choice = random.randrange(2, 4)
            if choice == 3:
                self.bet = random.randrange(2 * (self.to_call + 1), 3 * (self.to_call + 1))
            return choice
        elif strength >= 4:
            return 2
        else:
            return 1

class PokerProbabilities:
    @staticmethod
    def highest_card(cards):
        rank = Card.get_rank_int(cards[0])
        for card in cards:
            if rank > Card.get_rank_int(card):
                rank = Card.get_rank_int(card)
        return rank
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
        ranks[Card.get_rank_int(cards[0])] = 1
        for c in range(1, len(cards)):
            if Card.get_rank_int(c) in ranks:
                ranks[Card.get_rank_int(c)] += 1
            else:
                ranks[Card.get_rank_int(c)] = 1
        count = list(ranks.values())
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

