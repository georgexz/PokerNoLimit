from PokerProbabilities import PokerBot
from SidePot import SidePot
from deuces import Card
from deuces import Deck
from deuces import Evaluator
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
            decision = self.pokerBot.handle_preflop()
            if decision == 3:
                bet = self.pokerBot.bet
        if decision == 0:
            return [self.fold(), 0]
        elif decision == 1:
            if to_call_amount > 0:
                return [self.fold(), 0]
            return[self.check(), 0]
        elif decision == 2:
            self.lastAction = to_call_amount - self.singleRoundMoneyInThePot
            return[self.call(to_call_amount), to_call_amount-self.singleRoundMoneyInThePot]
        elif decision == 3:
            self.lastAction = bet - self.singleRoundMoneyInThePot
            return[self.bet(bet), self.lastAction]
        elif decision == 4:
            return[self.go_all_in(), self.lastAction]


    def fold(self):
        self.finish_betting()
        return 0

    def check(self):
        return 1

    def call(self, bet_size):
        amount = bet_size - self.singleRoundMoneyInThePot
        if amount < self.stack:
            self.stack = self.stack - amount
            return 2
        else:
            return self.go_all_in()

    def bet(self, bet_size):
        amount = bet_size - self.singleRoundMoneyInThePot
        if amount < self.stack:
            self.stack = self.stack - amount
            return 3
        else:
            return self.go_all_in()

    def go_all_in(self):
        self.lastAction = self.stack
        self.stack = 0
        return 4

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


class Table:

    playerList = []
    playerStackList = []
    playerNames = []
    roundList = []
    justBegun = False
    button = 0
    board = []
    pot = 0
    sidePots = []
    toCall = 0
    done = False
    actions = []

    def __init__(self, n_players, small_blind, big_blind, ante):
        self.n_players = n_players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.ante = ante
        self.justBegun = True

    # description of setup
    def get_number_of_players(self):
        return self.n_players

    def get_small_blind(self):
        return self.small_blind

    def get_big_blind(self):
        return self.big_blind

    def get_ante(self):
        return self.ante

    def get_pot_size(self):
        return self.pot

    # beginning of game, player's chips
    def set_player_stack(self, stack_size):
        self.playerStackList.append(stack_size)

    # board position
    def update_pot(self, bet):
        # someone wins the pot
        if bet == -1:
            self.pot = 0
        else:
            # someone adds to the pot
            self.pot = self.pot + bet

    # betting begins
    def start_round(self):
        # preflop
        if self.justBegun:
            self.justBegun = False
            index = self.button + 3
            while self.get_number_of_turns_left() > 0:
                if self.roundList.count(-1) == self.n_players - 1:
                    self.no_bets()
                    break
                if index >= self.n_players:
                    index = index - self.n_players
                    print("Player " + self.playerList[index].name + "'s turn.\n")
                    self.playerList[index].pot_size = self.pot
                    for s in self.sidePots:
                        if s.playerList[index] != 1 or s.playerList[index] != -2:
                            self.playerList[index].side_pots.append(s.sidePot)
                    player_action = self.playerList[index].action(self.pot, self.toCall, self.board, self.actions)
                    self.actions.append(player_action)
                    index = self.round_continuation(index, player_action)
                else:
                    print("Player " + self.playerList[index].name + "'s turn.\n")
                    self.playerList[index].pot_size = self.pot
                    for s in self.sidePots:
                        if s.playerList[index] != 1 or s.playerList[index] != -2:
                            self.playerList[index].side_pots.append(s.sidePot)
                    player_action = self.playerList[index].action(self.pot, self.toCall, self.board, self.actions)
                    self.actions.append(player_action)
                    index = self.round_continuation(index, player_action)

        # after preflop
        else:
            index = self.button + 1
            next_index = self.button
            while self.get_number_of_turns_left() >= 1:
                next_index += 1
                while next_index >= len(self.roundList):
                    print("next_index: " + str(next_index))
                    print("length of roundList: " + str(len(self.roundList)))
                    next_index -= len(self.roundList)
                if self.roundList[next_index] == 1:
                    index = next_index
                    break

            while self.get_number_of_turns_left() > 0:
                if self.roundList.count(-1) == self.n_players - 1:
                    self.no_bets()
                    break
                if index >= self.n_players:
                    index = index - self.n_players
                    print("Player " + self.playerList[index].name + "'s turn.\n")
                    self.playerList[index].pot_size = self.pot
                    for s in self.sidePots:
                        if s.playerList[index] != 1 or s.playerList[index] != -2:
                            self.playerList[index].side_pots.append(s.sidePot)
                    player_action = self.playerList[index].action(self.pot, self.toCall, self.board, self.actions)
                    self.actions.append(player_action)
                    index = self.round_continuation(index, player_action)
                else:
                    print("Player " + self.playerList[index].name + "'s turn.\n")
                    self.playerList[index].pot_size = self.pot
                    for s in self.sidePots:
                        if s.playerList[index] != 1 or s.playerList[index] != -2:
                            self.playerList[index].side_pots.append(s.sidePot)
                    player_action = self.playerList[index].action(self.pot, self.toCall, self.board, self.actions)
                    self.actions.append(player_action)
                    index = self.round_continuation(index, player_action)

        # end of betting in preflop
        for n, i in enumerate(self.roundList):
            if i == 0:
                self.roundList[n] = 1

        if self.roundList.count(1) == 0:
            self.no_bets()

    def round_continuation(self, player_i, player_action):
        self.update_side_pots()
        self.check_side_pots(player_i, player_action)
        # folded, out of the round
        if player_action[0] == 0:
            self.roundList[player_i] = -1
            print("Player " + self.playerList[player_i].name + " folded.")
        elif player_action[0] == 1:
            self.roundList[player_i] = 0
            print("Player " + self.playerList[player_i].name + " checked.")
        elif player_action[0] == 2:
            self.update_pot(player_action[1])
            self.roundList[player_i] = 0
            print("Player " + self.playerList[player_i].name + " called " + str(player_action[1] + self.playerList[player_i].
                                                               singleRoundMoneyInThePot))
            print("Pot: " + str(self.pot))
        elif player_action[0] == 3:
            self.update_pot(player_action[1])
            self.toCall = player_action[1] + self.playerList[player_i].singleRoundMoneyInThePot
            for n, i in enumerate(self.roundList):
                if i == 0:
                    self.roundList[n] = 1

            self.roundList[player_i] = 0
            print("Player " + self.playerList[player_i].name + " raised to " + str(self.toCall))
            print("Pot: " + str(self.pot))
        # side pot scenarios?
        elif player_action[0] == 4:
            self.roundList[player_i] = 2
            # all in is essentially a raise
            if self.toCall < player_action[1] + self.playerList[player_i].singleRoundMoneyInThePot:
                self.toCall = player_action[1] + self.playerList[player_i].singleRoundMoneyInThePot
                for n, i in enumerate(self.roundList):
                    if i == 0:
                        self.roundList[n] = 1
            self.update_pot(player_action[1])
            print("Player " + self.playerList[player_i].name + " went all in for " + str(player_action[1] + self.playerList[player_i].singleRoundMoneyInThePot))
            print("Pot: " + str(self.pot))
        self.playerList[player_i].finish_betting()
        next_index = player_i
        print("new round values: " + str(self.roundList))
        while self.get_number_of_turns_left() >= 1:
            next_index += 1
            while next_index >= len(self.roundList):
                next_index -= len(self.roundList)
            if self.roundList[next_index] == 1:
                return next_index

    def update_side_pots(self):
        self.sidePots.sort(key=lambda side_pot: side_pot.to_call, reverse=True)
        count = 0
        for i, e in reversed(list(enumerate(self.sidePots))):
            if count == 0:
                count += 1
                self.sidePots[i].pot_add = self.sidePots[i].to_call
                continue
            self.sidePots[i].pot_add = self.sidePots[i].to_call - self.sidePots[i+1].to_call

    def check_side_pots(self, player_i, player_action):
        # fold
        if player_action[0] == 0:
            for n,x in enumerate(self.sidePots):
                self.sidePots[n].delete_from_side_pot(player_i)
        # check
        if player_action[0] == 1:
            for n,x in enumerate(self.sidePots):
                self.sidePots[n].playerList[player_i] = 0
        # call
        elif player_action[0] == 2:
            for n, x in enumerate(self.sidePots):
                self.sidePots[n].sidePot += self.sidePots[n].pot_add
                self.sidePots[n].playerList[player_i] = 0
        # raise
        elif player_action[0] == 3:
            if self.sidePots:
                self.sidePots.append(SidePot(player_action[1] + self.playerList[player_i].singleRoundMoneyInThePot
                                             - self.sidePots[0].to_call, self.roundList, player_action[1]))
                for n, x in enumerate(self.sidePots[-1].playerList):
                    if x == 2:
                        self.sidePots[-1].playerList[n] = -2
                self.update_side_pots()
                for n, x in enumerate(self.sidePots):
                    self.sidePots[n].sidePot += self.sidePots[n].pot_add
                    for m, i in enumerate(self.sidePots[n].playerList):
                        if i == 0:
                            self.sidePots[n].playerList[m] = 1
                    self.sidePots[n].playerList[player_i] = 0
        # all in
        elif player_action[0] == 4:
            # assuming there are side pots, what do we do if player's all in is a raise?
            if self.sidePots:
                if self.sidePots[0].to_call < player_action[1]:
                    self.sidePots.append(SidePot(player_action[1] + self.playerList[player_i].singleRoundMoneyInThePot
                                                 - self.sidePots[0].to_call, self.roundList, player_action[1]))
                    for n, x in enumerate(self.sidePots[-1].playerList):
                        if x == 2:
                            self.sidePots[-1].playerList[n] = -2
                    self.update_side_pots()
                    for n, x in enumerate(self.sidePots):
                        self.sidePots[n].sidePot += self.sidePots[n].pot_add
                        for m, i in enumerate(self.sidePots[n].playerList):
                            if i == 0:
                                self.sidePots[n].playerList[m] = 1
                        self.sidePots[n].playerList[player_i] = 2

                # player went all in to call but not enough
                if self.sidePots[0].to_call > player_action[1] + self.playerList[player_i].singleRoundMoneyInThePot:

                    for n, x in enumerate(self.sidePots):
                        if x.to_call == player_action[1]:
                            self.sidePots[n].playerList[player_i] = 2
                            self.sidePots[n].sidePot += self.sidePots[n].pot_add
                            for i, e in reversed(list(enumerate(self.sidePots))):
                                if i == n:
                                    break
                                else:
                                    self.sidePots[i].playerList[player_i] = 2
                                    self.sidePots[i].sidePot += self.sidePots[i].pot_add
                            break
                        if x.to_call < player_action[1]:
                            for i in range(n, len(self.sidePots)):
                                self.sidePots[i].playerList[player_i] = 2
                                self.sidePots[i].sidePot += self.sidePots[i].pot_add
                            self.sidePots.append(SidePot((player_action[1] - self.sidePots[n].to_call,
                                                 self.roundList, player_action[1])))
                            self.sidePots[n-1].pot_add = self.sidePots[n-1].to_call - self.sidePots[-1].to_call
                            self.sidePots[n-1].sidePot = (self.sidePots[n-1].playerList.count(0) + self.sidePots[n-1].
                                                          playerList.count(2))*self.sidePots[n-1].pot_add
                            for i in range(0,n):
                                self.sidePots[i].playerList[player_i] = -2
                            self.sidePots[-1].sidePot += (self.sidePots[-1].playerList.count(0) + self.sidePots[-1].
                                                          playerList.count(2))*(self.sidePots[-1].to_call
                                                                                - self.sidePots[n].to_call)
                            self.update_side_pots()
                            break
            # new side pot, no side pots before, all in is short
            else:
                if self.toCall > player_action[1] + self.playerList[player_i].singleRoundMoneyInThePot:

                    self.sidePots.append(SidePot(player_action[1] + self.playerList[player_i].singleRoundMoneyInThePot,
                                                 self.roundList, player_action[1]))
                    self.sidePots[0].sidePot += (player_action[1] + self.playerList[player_i].singleRoundMoneyInThePot)\
                                                *(self.roundList.count(0) + self.roundList.count(2))
                    self.sidePots.append(SidePot((self.roundList.count(0) + self.roundList.count(2))
                                                 *(self.toCall - (player_action[1] + self.playerList[player_i]
                                                                  .singleRoundMoneyInThePot)), self.roundList,
                                                 self.toCall))
                    self.sidePots[-1].playerList[player_i] = -2
                    self.update_side_pots()

    def no_bets(self):
        if self.roundList.count(-1) == self.n_players - 1:
            index = 0
            for i, x in enumerate(self.roundList):
                if x != -1:
                    index = i
                    break
            self.playerList[index].stack += self.pot
            self.roundList[index] = 0
            self.pot = 0
            self.done = True
            print("Player " + self.playerList[index].name + " takes the pot.")
        self.board.clear()

    def get_number_of_turns_left(self):
        return self.roundList.count(1)

    # dealing cards to each player and instantiating each player
    def deal_preflop(self, deck):
        if not self.playerList:
            for i in range(self.n_players):
                self.playerList.append(Player(deck.draw(2), self.playerStackList[i], self.playerNames[i], self.n_players))

                # everyone is waiting for their turn
                self.roundList.append(1)
        else:
            for i in range(self.n_players):
                if self.playerList[i].stack > 0:
                    self.playerList[i].hand = deck.draw(2)
                    self.roundList[i] = 1
                else:
                    self.roundList[i] = -1

    # dealing to the board
    def deal_flop(self, deck):
        self.board = deck.draw(3)
        Card.print_pretty_cards(self.board)

    def deal_turn(self, deck):
        self.board.append(deck.draw(1))
        Card.print_pretty_cards(self.board)

    def deal_river(self, deck):
        self.board.append(deck.draw(1))
        Card.print_pretty_cards(self.board)

    def clear_cards(self):
        self.board.clear()

    # set up blinds
    # clockwise rotation synchronized with increasing index
    def declare_button(self):
        self.button = random.randrange(0, self.n_players)
        print("button: " + str(self.button))
        # depending where the button is
        if self.button + 1 >= self.n_players:
            self.playerList[self.button + 1 - self.n_players].set_small_blind(self.small_blind)
            self.playerList[self.button + 2 - self.n_players].set_big_blind(self.big_blind)
        elif self.button + 2 >= self.n_players:
            self.playerList[self.button + 1].set_small_blind(self.small_blind)
            self.playerList[self.button + 2 - self.n_players].set_big_blind(self.big_blind)
        else:
            self.playerList[self.button + 1].set_small_blind(self.small_blind)
            self.playerList[self.button + 2].set_big_blind(self.big_blind)
        self.update_pot(self.small_blind + self.big_blind)
        self.toCall = self.big_blind
        for i in range(self.n_players):
            index = self.button + i
            while index >=self.n_players:
                index -= self.n_players
            self.playerList[index].distanceFromButton = i

    def rotate_button(self):
        self.button += 1
        while self.button >= self.n_players:
            self.button -= self.n_players
        print("button: " + str(self.playerList[self.button].name))

        # depending where the button is
        if self.button + 1 >= self.n_players:
            self.playerList[self.button + 1 - self.n_players].set_small_blind(self.small_blind)
            self.playerList[self.button + 2 - self.n_players].set_big_blind(self.big_blind)
        elif self.button + 2 >= self.n_players:
            self.playerList[self.button + 1].set_small_blind(self.small_blind)
            self.playerList[self.button + 2 - self.n_players].set_big_blind(self.big_blind)
        else:
            self.playerList[self.button + 1].set_small_blind(self.small_blind)
            self.playerList[self.button + 2].set_big_blind(self.big_blind)
        self.update_pot(self.small_blind + self.big_blind)
        self.toCall = self.big_blind
        for i in range(self.n_players):
            index = self.button + i
            while index >=self.n_players:
                index -= self.n_players
            self.playerList[index].distanceFromButton = i

    # visual functions
    def get_player_hands(self):
        list_of_hands = []
        for player in self.playerList:
            list_of_hands.append([player.get_hand(), player.name])
        return list_of_hands

    def get_player_stack_sizes(self):
        list_of_stack_sizes = []
        for player in self.playerList:
            list_of_stack_sizes.append([player.get_stack_size(), player.name])
        self.playerStackList = list_of_stack_sizes
        return list_of_stack_sizes

    def give_winnings(self):
        evaluated_hands = []
        evaluator = Evaluator()

        for i in range(self.n_players):
            evaluated_hands.append(evaluator.evaluate(self.playerList[i].hand, self.board))
            print("Score for player " + self.playerList[i].name + ": " + str(evaluator.evaluate(self.playerList[i].hand, self.board)))

        for k in range(self.n_players):
            if self.roundList[k] != -1:
                best_score = evaluated_hands[k]
                best_index = k
                break
        for j in range(0, self.n_players):
            if evaluated_hands[j] < best_score and evaluated_hands[j] != 0 and self.roundList[j] != -1:
                best_score = evaluated_hands[j]
                best_index = j
            evaluated_hands[j] = 0

        while self.sidePots:
            for n, x in enumerate(self.sidePots):
                for m, p in enumerate(x.playerList):
                    if p != -1 or p != -2:
                        self.playerList[best_index].stack += x.sidePot
                        print(self.playerList[best_index].name + " wins side pot of " + str(x.sidePot))
                        self.sidePots.pop(n)
                        break
            for j in range(0, self.n_players):
                if evaluated_hands[j] < best_score and evaluated_hands[j] != 0 and self.roundList[j] != -1:
                    best_score = evaluated_hands[j]
                    best_index = j
                evaluated_hands[j] = 0
            self.pot = 0
        if self.pot > 0:
            self.playerList[best_index].stack += self.pot
            print()
            print(self.playerList[best_index].name + " takes the pot.")
            self.pot = 0


def main():
    number_of_players = int(input("How many players? "))
    small_blind = int(input("Small Blind: "))
    big_blind = int(input("Big Blind: "))
    # just put 0 for ante
    ante = int(input("Ante: "))
    deck = Deck()
    game = Table(number_of_players, small_blind, big_blind, ante)

    for i in range(number_of_players):
        stack_size = int(input("Stack size for player " + str(i) + ": "))
        game.playerNames.append(input("Name: "))
        game.set_player_stack(stack_size)

    for n in range(15):
        if len(game.playerList) == 1:
            print()
            print("Winner is " + game.playerList[0].name)
            break
        print()
        print("New Deck")
        print()
        deck.GetFullDeck()
        deck.shuffle()
        # pot has small blind and big blind and ante
        game.deal_preflop(deck)
        if n == 0:
            game.declare_button()
        else:
            game.rotate_button()

        # testing preflop cards
        for hand in game.get_player_hands():
            print("Player " + str(hand[1]))
            Card.print_pretty_cards(hand[0])
            # print("rank: " + str(Card.get_rank_int(hand[0][0])))
            # print("suit: " + str(Card.get_suit_int(hand[0][0])))
            # print("rank: " + str(Card.get_rank_int(hand[0][1])))
            # print("suit: " + str(Card.get_suit_int(hand[0][1])))

        for s, stack in enumerate(game.get_player_stack_sizes()):
            print("Stack for " + str(stack[1]) + " is " + str(stack[0]))
        for player in game.playerList:
            if player.name != "Me":
                player.pokerBot.stackList = game.playerStackList
        game.start_round()
        game.actions.clear()
        for i in range(game.n_players):
            game.playerList[i].singleRoundMoneyInThePot = 0

        if game.done:
            game.done = False
            game.board.clear()
            continue

        game.deal_flop(deck)

        for n, stack in enumerate(game.get_player_stack_sizes()):
            print("Stack for " + str(stack[1]) + " is " + str(stack[0]))
        game.toCall = 0

        for player in game.playerList:
            if player.name != "Me":
                player.pokerBot.stackList = game.playerStackList
        game.start_round()
        game.actions.clear()

        for i in range(game.n_players):
            game.playerList[i].singleRoundMoneyInThePot = 0

        if game.done:
            game.done = False
            game.board.clear()
            continue

        game.deal_turn(deck)
        game.toCall = 0

        for n, stack in enumerate(game.get_player_stack_sizes()):
            print("Stack for " + str(stack[1]) + " is " + str(stack[0]))

        for player in game.playerList:
            if player.name != "Me":
                player.pokerBot.stackList = game.playerStackList

        game.start_round()
        game.actions.clear()

        for i in range(game.n_players):
            game.playerList[i].singleRoundMoneyInThePot = 0

        if game.done:
            game.done = False
            game.board.clear()
            continue

        game.deal_river(deck)
        game.toCall = 0

        for n, stack in enumerate(game.get_player_stack_sizes()):
            print("Stack for " + str(stack[1]) + " is " + str(stack[0]))

        for player in game.playerList:
            if player.name != "Me":
                player.pokerBot.stackList = game.playerStackList

        game.start_round()
        game.actions.clear()

        game.give_winnings()

        for n, stack in enumerate(game.get_player_stack_sizes()):
            print("Stack for " + str(stack[1]) + " is " + str(stack[0]))
            if stack[0] == 0:
                print("Player " + str(stack[1]) + " is gone.")
                ax = game.playerList[0]
                for x in game.playerList:
                    if x.name == stack[1]:
                        ax = x
                        break
                game.playerList.remove(ax)
                game.n_players -= 1
        for m in range(game.n_players):
            game.playerList[m].n_players = game.n_players

        if game.done:
            game.board.clear()
            game.done = False
            continue


main()
