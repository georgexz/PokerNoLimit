from treys import Card
import re

strip_ANSI_pat = re.compile(r"""
    \x1b     # literal ESC
    \[       # literal [
    [;\d]*   # zero or more digits or semicolons
    [A-Za-z] # a letter
    """, re.VERBOSE).sub

def strip_ANSI(s):
    return strip_ANSI_pat("", s)


def getPadding(ncol,s):
	left_padding = ((ncol//2-1) - len(strip_ANSI(s))//2)
	right_padding = ((ncol//2-1) - len(strip_ANSI(s))//2)
	return left_padding, right_padding

def applyPadding(ncol,s,num_tabs):
	left_padding, right_padding = getPadding(ncol,s)
	return '\t'*num_tabs + "|" + " "*left_padding + s + " "*right_padding + "|"

def printBoard(nrow, ncol, river,pot, side_pot=0,num_tabs=2):
    tops = ["\t"*num_tabs + ncol * '=']
    inner = ["\t"*num_tabs + '|' + " "*(ncol-2) + '|']*(nrow-2)
    rows = tops + inner + tops
    river_str = Card.print_pretty_cards(river)
    middle = nrow // 2
    potstr = "pot: {}, side pot: {}".format(pot,side_pot)

    rows[middle-1] = applyPadding(ncol,potstr,num_tabs)
    rows[middle] = applyPadding(ncol,river_str,num_tabs)

    return '\n'.join(rows)


if __name__ == "__main__":
	board = [
	 Card.new('Ah'),
	 Card.new('Kd'),
	 Card.new('Jc')
	]
	hand = [
	Card.new('Qs'),
	Card.new('Th')
	]

	s = printBoard(15,50,board,pot=10)
	print(s)

	s = 'potato\x1b[01;32mpotato\x1b[0;0mpotato'
