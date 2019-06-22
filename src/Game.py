from Table import *

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

    for n in range(100):
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
            print(Card.print_pretty_cards(hand[0]))
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

        for i in range(game.n_players):
            game.playerList[i].singleRoundMoneyInThePot = 0

        if game.done:
            game.done = False
            game.board.clear()
            continue

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
                game.roundList.pop(n)
                game.n_players -= 1
        for m in range(game.n_players):
            game.playerList[m].n_players = game.n_players

        if game.done:
            game.board.clear()
            game.done = False
            continue


main()
