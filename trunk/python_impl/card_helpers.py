# -*- coding: utf-8 -*-
"""
Вспомогательные процедуры, не затрагивающие
состояние игры
"""

colors = ('red', 'green', 'blue', 'yellow')
__all__ = [ 'evaluate_card', 'variants', 'stocks2money', 'limited_input', 'colors']

def evaluate_small_card(variant, orig_cost):
	"""Обработка хода малой карты"""
	new_cost = orig_cost.copy()
	for change in variant:
		new_cost[change[0]] = new_cost[change[0]] + change[1]
	return new_cost

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

def evaluate_large_card(variant, orig_cost):
	"""Обработка хода большой карты"""
	new_cost = orig_cost.copy()
	round_func = half_round_down
	if variant[0][1] == "*2":
		new_cost[variant[0][0]] = new_cost[variant[0][0]]*2
		new_cost[variant[1][0]] = round_func(new_cost[variant[1][0]])
	elif variant[0][1] == ":2":
		new_cost[variant[0][0]] = round_func(new_cost[variant[0][0]])
		new_cost[variant[1][0]] = new_cost[variant[1][0]]*2
	elif variant[0][1] == 100: 
		for change in variant:
			new_cost[change[0]] = new_cost[change[0]] + change[1]
	return new_cost

def evaluate_card(card, variant, orig_cost):
	"""Оцениваем вариант применения карты"""
	if card[2] == 'small':
		return evaluate_small_card(variant, orig_cost)
	else:	
		return evaluate_large_card(variant, orig_cost)

def variants(card):
	"""Все изменения цен от карты"""
	actions   = []
	color, delta, card_type = card

	if card_type == "small":
		other_delta = ((delta < 0 and 90 + delta) or -90 + delta)
		for other in colors:
			if other != color:	
				actions.append( [[color, delta], [other, other_delta]] )

	elif card_type == 'large': 
		if delta == "*2":
			for other in colors:
				if other != color:	
					actions.append( [[color, "*2"], [other, ":2"]] )

		elif delta == ":2":
			for other in colors:
				if other != color:	
					actions.append( [[color, ":2"], [other, "*2"]] )

		elif delta == "+100": 
			other_colors = []
			for other in colors:
				if other != color:
					other_colors.append(other)
			perms = permutations(other_colors)
			decays = (-10, -20, -30)
			for perm in perms:
				actions.append( [ [color, 100], [perm[0], decays[0]], [perm[1], decays[1]], [perm[2], decays[2]] ] )
	return actions

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
	for color in stocks:
		money += stocks[color] * test_cost[color]
	return money

def limited_input(msg, bottom, top):
	"""Запрашивает целое число с клавиатуры 
	и сравнивает с границами"""
	prompt = msg % (bottom, top)
	while(1):
		user_input = raw_input(prompt)
		
		if user_input.isdigit():
			res = int(user_input)
			if res >= bottom and res <= top:
				break
	return res

