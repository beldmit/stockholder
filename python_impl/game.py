# -*- coding: utf-8 -*-
"""
Реализация игры "Акционер"
http://ru.wikipedia.org/wiki/%D0%90%D0%BA%D1%86%D0%B8%D0%BE%D0%BD%D0%B5%D1%80_(%D0%B8%D0%B3%D1%80%D0%B0)
"""
import random
import player

#Глобальные настройки
num_players = 2
small = 6
large = 4
max_price = 250
min_price = 10
colors = ('red', 'green', 'blue', 'yellow')
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

	return

def deal():
	"""
	Раздаем карты игрокам
	"""
	for i in range (num_players):
		players.append(player.Player(i))
		players[i].cards.extend(deal_small(i))
		players[i].cards.extend(deal_large(i))
	return

def set_strategies():
	"""Установка специфических стратегий для игроков"""

	players[0].buy_after = players[0].buy_all_equal_money
	players[1].buy_after = players[1].buy_all_equal_money

	players[1].compare   = players[1].compare_avg_delta
#	players[1].buy_after = players[1].buy_by_2colors
#	players[0].interactive = 1
	return


def deal_small(player_id):
	"""Раздача малых карт"""
	return S[small*player_id:small*(player_id+1)]

def deal_large(player_id):
	"""Раздача больших карт"""
	return L[large*player_id:large*(player_id+1)]
	
def evaluate_small_card(variant, orig_cost):
	"""Обработка хода малой карты"""
	new_cost = orig_cost.copy()
	for change in variant:
		new_cost[change[0]] = new_cost[change[0]] + change[1]
	return new_cost

def evaluate_large_card(card, variant, orig_cost):
	"""Обработка хода большой карты"""
	new_cost = orig_cost.copy()
	round_func = half_round_down
	if card[1] == "*2":
		new_cost[variant[0][0]] = new_cost[variant[0][0]]*2
		new_cost[variant[1][0]] = round_func(new_cost[variant[1][0]])
	elif card[1] == ":2":
		new_cost[variant[0][0]] = round_func(new_cost[variant[0][0]])
		new_cost[variant[1][0]] = new_cost[variant[1][0]]*2
	elif card[1] == "+100": 
		for change in variant:
			new_cost[change[0]] = new_cost[change[0]] + change[1]
	return new_cost

def evaluate_card(card, variant, orig_cost):
	"""Оцениваем вариант применения карты"""
	if card[2] == 'small':
		return evaluate_small_card(variant, orig_cost)
	else:	
		return evaluate_large_card(card, variant, orig_cost)

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

def variants(card):
	"""Все изменения цен от карты"""
	actions   = []
	color     = card[0]
	card_type = card[2]

	if card_type == "small":
		delta = card[1]
		other_delta = ((delta < 0 and 90 + delta) or -90 + delta)
		for other in colors:
			if other != color:	
				actions.append( [[color, delta], [other, other_delta]] )

	elif card_type == 'large': 
		if card[1] == "*2":
			for other in colors:
				if other != color:	
					actions.append( [[color, "*2"], [other, ":2"]] )

		elif card[1] == ":2":
			for other in colors:
				if other != color:	
					actions.append( [[color, ":2"], [other, "*2"]] )

		elif card[1] == "+100": 
			other_colors = []
			for other in colors:
				if other != color:
					other_colors.append(other)
			perms = permutations(other_colors)
			decays = (-10, -20, -30)
			for perm in perms:
				actions.append( [ [color, 100], [perm[0], decays[0]], [perm[1], decays[1]], [perm[2], decays[2]] ] )
	return actions

def half_round_up(price):
	"""Округление вверх при делении на 2"""
	if price % 20 == 0:
		return price / 2
	else:
		return price / 2 + 5

def half_round_down(price):
	"""Округление вниз при делении на 2"""
	if price % 20 == 0:
		return price / 2
	else:
		return price / 2 - 5

def permutations(input_list):
	"""
	Originally from http://www.radlogic.com/releases/rad_util.py
	Return a list containing all permutations of the input list.

	Note: This is a recursive function.

	>>> perms = permutations(['a', 'b', 'c'])
	>>> perms.sort()
	>>> for perm in perms:
	...     print perm
	['a', 'b', 'c']
	['a', 'c', 'b']
	['b', 'a', 'c']
	['b', 'c', 'a']
	['c', 'a', 'b']
	['c', 'b', 'a']

	"""
	out_lists = []
	if len(input_list) > 1:
		# Extract first item in list.
		item = input_list[0]
		# Find all permutations of remainder of list. (Recursive call.)
		sub_lists = permutations(input_list[1:])
		# For every permutation of the sub list...
		for sub_list in sub_lists:
			# Insert the extracted first item at every position of the list.
			for i in range(len(input_list)):
				new_list = sub_list[:]
				new_list.insert(i, item)
				out_lists.append(new_list)
	else:
		# Termination condition: only one item in input list.
		out_lists = [input_list]
	return out_lists

def stocks2money(stocks, test_cost):
	"""Общая сумма денег в акциях"""
	money = 0
	for color in stocks.keys():
		money += stocks[color] * test_cost[color]
	return money

def make_compensation():
	"""Обработка компенсаций"""
	#Начисляем компенсацию за превышение над максимальной ценой
	for color in colors:
		if cost[color] > max_price:
			for player in players:
				player.money += (cost[color]-max_price)*player.stocks[color]
			cost[color] = max_price
#Начисляем компенсацию за понижение своих акций
		if cost[color] < old_cost[color]:
			players[last_player].money += (old_cost[color] - cost[color])*players[last_player].stocks[color]
#Берем деньги за банкротство
#Вообще-то тут надо разбираться, за какие акции брать компенсацию
#при применении карты 100, если в минус ушли несколько акций сразу
	for color in colors:
		if cost[color] < min_price:
			for player in players:
				player.process_crash(color, min_price - cost[color])
			cost[color] = min_price
	return

def limited_input(msg, bottom, top):
	"""Запрашивает целое число с клавиатуры 
	(пустая строка считается нулем)
	и сравнивает с границами"""
	prompt = msg % (bottom, top)
	while(1):
		user_input = raw_input(prompt)
		
		if user_input.isdigit():
			res = int(user_input)
			if res >= bottom and res <= top:
				break
	return res

def cost_compare(a, b):
	if cost[a] > cost[b]:
		return 1
	if cost[a] < cost[b]:
		return -1
	return 0

if __name__ == '__main__':
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

