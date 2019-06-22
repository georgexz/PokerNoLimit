import re

class Printer:
	def __init__(self,nrow, ncol,num_tabs=2):
		self.nrow = nrow
		self.ncol = ncol
		self.num_tabs = num_tabs
		self.strip_ANSI_pat = re.compile(r"""
		\x1b     # literal ESC
		\[       # literal [
		[;\d]*   # zero or more digits or semicolons
		[A-Za-z] # a letter
		""", re.VERBOSE).sub

	def strip_ANSI(self,s):
		return self.strip_ANSI_pat("", s)

	def getPadding(self,s,left_portion=0.5):
		left_padding = ((int(self.ncol*left_portion)-1) - len(self.strip_ANSI(s))//2)
		right_padding = ((self.ncol//2-1) - len(self.strip_ANSI(s))//2)
		return left_padding, right_padding

	def applyPadding(self,s,padding):
		left_padding, right_padding = padding
		return '\t'*self.num_tabs + "|" + " "*left_padding + s + " "*right_padding + "|"

	def playerPadding(self,s,padding):
		left_padding, right_padding = padding
		return '\t'*self.num_tabs + " "*left_padding + s + " "*right_padding

	def printBoard(self, p_round, river_str, pot, side_pot=0):
		round_str = "Round: {}\n".format(p_round)
		tops = ["\t"*self.num_tabs + self.ncol * '=']
		inner = ["\t"*self.num_tabs + '|' + " "*(self.ncol-2) + '|']*(self.nrow-2)
		
		rows = tops + inner + tops
		player_str = "{}, ${} in stack".format("Shyam",10)

		middle = self.nrow // 2
		potstr = "pot: {}, side pot: {}".format(pot,side_pot)

		rows[middle-1] = self.applyPadding(potstr,self.getPadding(potstr))
		rows[middle] = self.applyPadding(river_str,self.getPadding(river_str))

		return '\n'  + round_str + '\n' + self.playerPadding(player_str,self.getPadding(player_str,0.0)) + '\n' + '\n'.join(rows) + '\n'*2


	def check(self):
		print("hey")

if __name__ == "__main__":
	from treys import Card

	board = [
	 Card.new('Ah'),
	 Card.new('Kd'),
	 Card.new('Jc')
	]
	hand = [
	Card.new('Qs'),
	Card.new('Th')
	]

	p = Printer(15,50)
	s = p.printBoard(1,Card.print_pretty_cards(board),pot=10)
	print(s)
