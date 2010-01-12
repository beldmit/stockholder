# -*- coding: utf-8 -*-
import game

score = {0 : 0, 1 : 0}

for i in range(1000):
	game.init()
	game.deal()
	game.set_strategies()

	#Эталонная партия
	#
#	game.players[0].cards[:] = [['yellow', 60, 'small'], ['green', '+100', 'large'], ['red', -60, 'small'], ['yellow', '+100', 'large'], ['yellow', -40, 'small'], ['green', '+100', 'large'], ['green', -60, 'small'], ['yellow', 50, 'small'], ['green', -30, 'small'], ['yellow', '+100', 'large']]
#
#	game.players[1].cards[:] = [['blue', '+100', 'large'], ['red', '+100', 'large'], ['yellow', -30, 'small'], ['red', '+100', 'large'], ['green', -40, 'small'], ['blue', 30, 'small'], ['blue', 40, 'small'], ['green', '+100', 'large'], ['blue', -30, 'small'], ['red', -50, 'small']]

#	game.players[0].money = 190

	for i in range(game.small + game.large):
		game.move = i+1
		for player in game.players:
			player.make_move()
#		raw_input()

	print game.cost
	result = []
	for player in game.players:
		result.append(game.stocks2money(player.stocks, game.cost) + player.money)
		print "+++", player
		print "+++", player.idx, result[player.idx]
	
	if result[0] > result[1]:
		score[0] += 1
	elif result[1] > result[0]:
		score[1] += 1

print score
