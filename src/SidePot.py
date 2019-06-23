
class SidePot:

    playerList = []
    sidePot = 0
    pot_add = 0

    def __init__(self, side_pot, round_list, to_call):
        self.sidePot = side_pot
        self.playerList = round_list.copy()
        self.to_call = to_call
        # for n, x in enumerate(self.playerList):
        #     if x == 0:
        #         self.playerList[n] = 1

    def delete_from_side_pot(self, player_i):
        self.playerList[player_i] = -1

