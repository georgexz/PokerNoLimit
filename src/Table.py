from Player import *
from collections import OrderedDict

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
    allins = []
    sum_of_sidePots = [] 

    def __init__(self, n_players, small_blind, big_blind, ante):
        self.n_players = n_players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.ante = ante
        self.justBegun = True

    def get_sum_of_sidePots(self):
        return sum_of_sidePots
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

    def set_allins(self, num_players):
        self.allins = [0] * num_players
    # board position
    def update_pot(self, bet):
        # someone wins the pot
        if bet == -1:
            self.pot = 0
        else:
            # someone adds to the pot
            self.pot = self.pot + bet

    # betting begins
    def start_round(self, single_round):
        self.set_allins(self.n_players)
        # preflop
        if self.justBegun:
            self.justBegun = False
            index = (self.button + 3) % self.n_players
            while self.get_number_of_turns_left() > 0:
                if self.roundList.count(-1) == self.n_players - 1:
                    self.no_bets()
                    break
                print("Player " + self.playerList[index].name + "'s turn.\n")
                self.playerList[index].pot_size = self.pot
                for s in self.sidePots:
                    if s.playerList[index] != 1 or s.playerList[index] != -2:
                        self.playerList[index].side_pots.append(s.sidePot)
                player_action = self.playerList[index].action(self.pot, self.toCall, self.board, self.actions)
                self.actions.append(player_action)
                index = self.round_continuation(index, player_action, single_round)
        # after preflop
        else:
            index = (self.button + 1) % self.n_players
            next_index = self.button
            while self.get_number_of_turns_left() >= 1:
                next_index = (next_index + 1) % len(self.roundList)
                if self.roundList[next_index] == 1:
                    index = next_index
                    break

            while self.get_number_of_turns_left() > 0:
                if self.roundList.count(-1) == self.n_players - 1:
                    self.no_bets()
                    break

                print("Player " + self.playerList[index].name + "'s turn.\n")
                self.playerList[index].pot_size = self.pot
                for s in self.sidePots:
                    if s.playerList[index] != 1 or s.playerList[index] != -2:
                        self.playerList[index].side_pots.append(s.sidePot)
                player_action = self.playerList[index].action(self.pot, self.toCall, self.board, self.actions)
                self.actions.append(player_action)
                index = self.round_continuation(index, player_action, single_round)
        self.sum_of_sidePots.append(self.sidePots.copy())
        self.sidePots.clear()

        # end of betting in preflop
        for n, i in enumerate(self.roundList):
            if i == 0:
                self.roundList[n] = 1

        if self.roundList.count(1) == 0:
            self.no_bets()

    def round_continuation(self, player_i, player_action, single_round):
        self.update_side_pots()
        self.check_side_pots(player_i, player_action, single_round)
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
            self.allins[player_i] = player_action[1] + self.playerList[player_i].singleRoundMoneyInThePot
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
        intro = 0
        for i, e in reversed(list(enumerate(self.sidePots))):
            if intro == 0:
                intro += 1
                self.sidePots[i].pot_add = self.sidePots[i].to_call
                continue
            self.sidePots[i].pot_add = self.sidePots[i].to_call - self.sidePots[i+1].to_call

    def figure_side_pots(self):
        for i, e in enumerate(self.sidePots):
            e.sidePot = e.pot_add * (e.playerList.count(0) + e.playerList.count(2))

        # for j, f in reversed(list(enumerate(self.sidePots))):
        #     count = 0
        #     for x in range(0, len(self.playerList)):
        #         if f.playerList[x] == 0 or f.playerList[x] == 2:
        #             count += 1
        #     f.sidePot = count*f.pot_add

    def check_side_pots(self, player_i, player_action, single_round):
        print(player_action)
        simple_money = player_action[1] + self.playerList[player_i].singleRoundMoneyInThePot
        
        # for l, y in enumerate(self.sidePots):
        #     print("sidePot: " + str(l) + "amount: " + str(y.sidePot) + " to_call: " + str(y.to_call) + " pot_add: " + str(y.pot_add) + " players: " + str(y.playerList))
        
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
                # self.sidePots[n].sidePot += self.sidePots[n].pot_add
                self.sidePots[n].playerList[player_i] = 0
        # raise
        elif player_action[0] == 3:
            if self.sidePots:
                self.sidePots.append(SidePot(0, self.roundList.copy(), simple_money, single_round))
                for n, x in enumerate(self.sidePots[-1].playerList):
                    if x == 2:
                        self.sidePots[-1].playerList[n] = -2
                    if x == 0:
                        self.sidePots[-1].playerList[n] = 1
                self.update_side_pots()
                for n, x in enumerate(self.sidePots):
                    for m, i in enumerate(self.sidePots[n].playerList):
                        if i == 0:
                            self.sidePots[n].playerList[m] = 1
                    self.sidePots[n].playerList[player_i] = 0
                    # self.sidePots[n].sidePot += self.sidePots[n].pot_add
        # all in
        elif player_action[0] == 4:
            self.allins[player_i] = simple_money
            # assuming there are side pots, what do we do if player's all in is a raise?
            if self.sidePots:
                if self.sidePots[0].to_call < simple_money:
                    self.sidePots.append(SidePot(0, self.roundList.copy(), simple_money, single_round))

                    for n, x in enumerate(self.sidePots[-1].playerList):
                        if x == 2:
                            self.sidePots[-1].playerList[n] = -2
                        if x == 0:
                            self.sidePots[-1].playerList[n] = 1
                    self.update_side_pots()
                    for n, x in enumerate(self.sidePots):
                        for m, i in enumerate(self.sidePots[n].playerList):
                            if i == 0 and x.single_round == single_round:
                                self.sidePots[n].playerList[m] = 1
                        self.sidePots[n].playerList[player_i] = 2
                        # self.sidePots[n].sidePot += self.sidePots[n].pot_add
                        
                #call with all in perfect match
                elif self.sidePots[0].to_call == simple_money and self.sidePots[0].single_round == single_round:
                    for l, b in enumerate(self.sidePots):
                        # self.sidePots[l].sidePot += self.sidePots[l].pot_add
                        self.sidePots[l].playerList[player_i] = 2
                
                # player went all in to call but not enough
                elif self.sidePots[0].to_call > simple_money:
                    match = False
                    for n, x in enumerate(self.sidePots):
                        if simple_money == x.to_call:
                            match = True
                            i = n
                            j = n - 1
                            while i < len(self.sidePots):
                                if self.sidePots[i].single_round == single_round:
                                    # self.sidePots[i].sidePot += self.sidePots[i].pot_add
                                    self.sidePots[i].playerList[player_i] = 2
                                i += 1
                            while j > 0:
                                if self.sidePots[j].playerList[player_i] == 2 and self.sidePots[j].single_round == single_round:
                                    self.sidePots[j].playerList[player_i] = -2
                                j -= 1

                    if match == False:
                        self.sidePots.append(SidePot(0, self.roundList.copy(), simple_money, single_round))
                        self.sidePots[-1].playerList[player_i] = 2
                        for n, x in enumerate(self.sidePots[-1].playerList):
                            if x == 2 and self.allins[n] < self.sidePots[-1].to_call:
                                self.sidePots[-1].playerList[n] = -2
                        self.update_side_pots()
                        #which side pots is he in
                        for m, y in enumerate(self.sidePots):
                            if y.to_call > self.allins[player_i] and y.single_round == single_round:
                                y.playerList[player_i] = -2
                            elif y.single_round == single_round:
                                y.playerList[player_i] = 2
                                # y.sidePot += y.pot_add
                        #figuring out sidepot amount
                        # for n, x in enumerate(self.sidePots):
                        #     if x.to_call == simple_money and x.single_round == single_round:
                        #         # trickle = (self.sidePots[n-1].playerList.count(0) + self.sidePots[n-1].playerList.count(2))*self.sidePots[n].pot_add
                        #         # self.sidePots[n-1].sidePot -= trickle
                        #         # self.sidePots[n].sidePot += trickle
                        #         break

            # new side pot, no side pots before, all in SCENARIOS
            else:
                if self.toCall > simple_money:

                    self.sidePots.append(SidePot(simple_money, self.roundList.copy(), simple_money, single_round))
                    self.sidePots[0].sidePot += (simple_money)*(self.roundList.count(0) + self.roundList.count(2))
                    self.sidePots[0].playerList[player_i] = 2
                    self.sidePots.append(SidePot(0, self.roundList.copy(), self.toCall, single_round))
                    self.sidePots[-1].playerList[player_i] = -2
                    # sum = 0
                    # for s in self.sidePots:
                    #     sum += s.sidePot
                    # if self.pot - sum > 0:
                    #     self.sidePots.append(SidePot(self.pot - sum, self.roundList.copy(), 0))
                    self.update_side_pots()
                
                elif self.toCall == simple_money:
                    self.sidePots.append(SidePot(0, self.roundList.copy(), self.toCall, single_round))
                    self.sidePots[0].playerList[player_i] = 2
                    # self.sidePots[0].sidePot += self.toCall*(self.roundList.count(0) + self.roundList.count(2))
                    # sum = 0
                    # for s in self.sidePots:
                    #     sum += s.sidePot
                    # if self.pot - sum > 0:
                    #     self.sidePots.append(SidePot(self.pot - sum, self.roundList.copy(), 0))
                    self.update_side_pots()

                #raise
                elif self.toCall < simple_money:
                    self.sidePots.append(SidePot(simple_money, self.roundList.copy(), simple_money, single_round))
                    self.sidePots[-1].playerList[player_i] = 2
                    
                    for m, i in enumerate(self.sidePots[0].playerList):
                        if i == 0:
                            self.sidePots[0].playerList[m] = 1
                    self.update_side_pots()
        self.figure_side_pots()
        for l, y in enumerate(self.sidePots):
            print("sidePot: " + str(l) + " amount: " + str(y.sidePot) + " to_call: " + str(y.to_call) + " pot_add: " + str(y.pot_add) + " players: " + str(y.playerList))
        




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
            self.sidePots.clear()
            self.sum_of_sidePots.clear()
            self.allins.clear()
            self.check_stacks()

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
        print(Card.print_pretty_cards(self.board))

    def deal_turn(self, deck):
        self.board.append(deck.draw(1))
        print(Card.print_pretty_cards(self.board))

    def deal_river(self, deck):
        self.board.append(deck.draw(1))
        print(Card.print_pretty_cards(self.board))

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

    def check_stacks(self):
        for n, stack in enumerate(self.get_player_stack_sizes()):
            print("Stack for " + str(stack[1]) + " is " + str(stack[0]))
            if stack[0] <= 1:
                print("Player " + str(stack[1]) + " is gone.")
                ax = self.playerList[0]
                for i, x in enumerate(self.playerList):
                    if x.name == stack[1]:
                        ax = x
                        break
                self.playerList.remove(ax)
                self.roundList.pop(i)
                self.n_players -= 1
                self.allins.clear()
        for m in range(self.n_players):
            self.playerList[m].n_players = self.n_players
        self.set_allins(self.n_players)

    def give_winnings(self):
        d = []
        evaluator = Evaluator()
        for i in range(self.n_players):
            if self.roundList[i] != -1:
                d.append([i, evaluator.evaluate(self.playerList[i].hand, self.board)])
                print("Score for player " + self.playerList[i].name + ": " + str(evaluator.evaluate(self.playerList[i].hand, self.board)))

        winner =sorted(d, key = lambda x: x[1])
        for x, w in enumerate(winner):
            print("sorted winner: " + str(w[0]) + " score: " + str(w[1]))
        split_pot = winner[0]
        split_pot_people = [winner[0][0]]
        has_split = []
        may_have_split = False
        may_divy = False
        #no side pot
        for s, t in enumerate(winner):
            if t[1] == split_pot[1] and t[0] != split_pot[0]:
                split_pot_people.append(t[0])
                may_divy = True

        #divying the dollar
        if self.sum_of_sidePots[0] == [] and self.sum_of_sidePots[1] == [] and self.sum_of_sidePots[2] == [] and self.sum_of_sidePots[3] == [] and may_divy:
            divy = int(self.pot / len(split_pot_people))
            for d in range(0, len(split_pot_people)):
                self.pot -= divy
                self.playerList[split_pot_people[d]].stack += divy
                print(self.playerList[split_pot_people[d]].name + " wins split pot: " + str(divy))


        for i in range(1,len(winner)):
            for j in range (0, i):
                if winner[i][1] == winner[j][1] and self.roundList[winner[i][0]] != -1 and self.roundList[winner[j][0]] != -1:
                    may_have_split = True
                    has_split.append([winner[i][0],winner[j][0]])
            
        new_split = self.combine_split(has_split)
        side_divy = 0
        who_split = -1
        goal = []
        keeper = []
        best = 0
        net = []
        if may_have_split:
            for i in range(0,4):
                for b, o in enumerate(self.sum_of_sidePots[i]):
                    for l, m in enumerate(o.playerList):
                        if m == 0 or m == 2:
                            goal.append(l)
                    for w, d in enumerate(winner):
                        if d[0] in goal:
                            keeper.append([d[0],d[1]])
                    keeper = sorted(keeper, key = lambda x: x[1])
                    s = 0
                    best = keeper[s][1]
                    while s < len(keeper):
                        if keeper[s][1] == best:
                            net.append(keeper[s])
                        else:
                            break
                        s += 1
                    ball = int( o.sidePot / len(net) )
                    for soccer, basketball in enumerate(net):
                        self.playerList[basketball[0]].stack += ball
                        self.pot -= ball
                        if len(net) == 1:
                            print( self.playerList[basketball[0]].name + " wins side pot of " + str(ball))
                        elif len(net) > 1:
                            print(self.playerList[basketball[0]].name + " splits pot and wins " + str(ball))
        else:
            for j in range(0,4):
                for n, x in enumerate(self.sum_of_sidePots[j]):
                    for w, d in enumerate(winner):
                        if x.playerList[d[0]] != -1 and x.playerList[d[0]] != -2:
                            self.playerList[d[0]].stack += x.sidePot
                            print(self.playerList[d[0]].name + " wins side pot of " + str(x.sidePot))  
                            self.pot -= x.sidePot
                            break


        
        if self.pot > 0:
            self.playerList[winner[0][0]].stack += self.pot
            print()
            print(self.playerList[winner[0][0]].name + " takes the pot.")
            self.pot = 0
            self.sidePots.clear()
            self.sum_of_sidePots.clear()
        self.check_stacks()

    def combine_split(self, num_array):
        for i in range(1, len(num_array)):
            for j in range(0, i):
                for k in range(0,len(num_array[j])):
                    for l in range(0,len(num_array[i])):
                        if num_array[j][k] == num_array[i][l]:
                            num_array.append(list(set(list(num_array[j][k]) + list(num_array[i][l]))))
                            num_array.remove(i)
                            num_array.remove(j)
        print("split pot array: " + str(num_array))
        return num_array

