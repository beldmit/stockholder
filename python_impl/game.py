# -*- coding: utf-8 -*-
"""
Реализация игры "Акционер"
http://ru.wikipedia.org/wiki/%D0%90%D0%BA%D1%86%D0%B8%D0%BE%D0%BD%D0%B5%D1%80_(%D0%B8%D0%B3%D1%80%D0%B0)
"""
import random
import player
from card_helpers import colors, evaluate_card, stocks2money

#Глобальные настройки
num_players = 2
small = 6
large = 4
max_price = 250
min_price = 10
#
#
players = []
last_player = -1
move = 0

S = []
L = []
cost = {}
old_cost = {}

def init():
	"""
	Начальное состояние игры:
	Все акции стоят по 100
	большие и малые карты перетасованы
	и розданы игрокам
	"""
	global S
	S = []
	global L
	L = []
	global players
	players = []

	for color in colors:
		for rank in range (3, 7):
			S.append([color,  rank*10, "small"])
			S.append([color, -rank*10, "small"])
		for rank in ['*2', ':2', '+100', '+100', '+100']:
			L.append([color, rank, "large"])
		cost[color] = 100
	random.shuffle(S)
	random.shuffle(L)

	for player_id in range (num_players):
		players.append(player.Player(player_id))
		players[player_id].cards.extend(S[small*player_id:small*(player_id+1)])
		players[player_id].cards.extend(L[large*player_id:large*(player_id+1)])
	return

def set_strategies():
	"""Установка специфических стратегий для игроков"""

	players[0].buy_after = players[0].buy_all_equal_money_if_good
	players[1].buy_after = players[1].buy_all_equal_money_if_good

#	players[1].compare   = players[1].compare_avg_delta_div
#	players[1].buy_after = players[1].buy_by_2colors
	players[0].interactive = 1
	return


def make_player_move(player_id, card, variant):
	"""Меняем состояние игры в зависимости от хода игрока"""	
	global last_player 
	global old_cost
	global cost
	last_player = player_id
	old_cost    = cost.copy()
	cost = evaluate_card(card, variant, cost)
	make_compensation()
	return	

def make_compensation():
	"""Обработка компенсаций"""
	#Начисляем компенсацию за превышение над максимальной ценой
	for color in colors:
		if cost[color] > max_price:
			for cur_player in players:
				cur_player.money += (cost[color]-max_price)*cur_player.stocks[color]
			cost[color] = max_price
#Начисляем компенсацию за понижение своих акций
		if cost[color] < old_cost[color]:
			players[last_player].money += (old_cost[color] - cost[color])*players[last_player].stocks[color]
#Берем деньги за банкротство
#Вообще-то тут надо разбираться, за какие акции брать компенсацию
#при применении карты 100, если в минус ушли несколько акций сразу
	for color in colors:
		if cost[color] < min_price:
			for cur_player in players:
				cur_player.process_crash(color, min_price - cost[color])
			cost[color] = min_price
	return

if __name__ == '__main__':
	import game
	score = {0 : 0, 1 : 0}

	for i in range(1000):
		game.init()
		game.set_strategies()

		#Эталонная партия
		#
	#	game.players[0].cards[:] = [['yellow', 60, 'small'], ['green', '+100', 'large'], ['red', -60, 'small'], ['yellow', '+100', 'large'], ['yellow', -40, 'small'], ['green', '+100', 'large'], ['green', -60, 'small'], ['yellow', 50, 'small'], ['green', -30, 'small'], ['yellow', '+100', 'large']]
	#
	#	game.players[1].cards[:] = [['blue', '+100', 'large'], ['red', '+100', 'large'], ['yellow', -30, 'small'], ['red', '+100', 'large'], ['green', -40, 'small'], ['blue', 30, 'small'], ['blue', 40, 'small'], ['green', '+100', 'large'], ['blue', -30, 'small'], ['red', -50, 'small']]

	#	game.players[0].money = 190

		for i in range(small + large):
			for player in game.players:
				player.make_move()
		#	raw_input()

		result = []
		for player in game.players:
			result.append(stocks2money(player.stocks, game.cost) + player.money)
			print "+++", player
			print "+++", player.idx, result[player.idx]
		
		if result[0] > result[1]:
			score[0] += 1
		elif result[1] > result[0]:
			score[1] += 1

	print score

