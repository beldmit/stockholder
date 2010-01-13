# -*- coding: utf-8 -*-
"""
Реализация стратегий игрока.
"""
from termcolor import colored
import game
class Player:
	"""
	Класс игрока.
	"""
	def compare_self(self, all_players, card, new_stocks, new_cost, new_money):
		"""Максимизируем свой счет"""
		result = game.stocks2money(new_stocks, new_cost)+new_money
		return result

	def compare_small_first(self, all_players, card, new_stocks, new_cost, new_money):
		"""Максимизируем свой счет, предпочитая 
		раньше расставаться с малыми картами"""
		result = game.stocks2money(new_stocks, new_cost)+new_money
		if (card[-1] == 'small'):
			result *= 2 
		return result

	def compare_avg_delta(self, all_players, card, new_stocks, new_cost, new_money):
		"""Оптимизируем отрыв от оппонента"""
		players = 0
		delta   = 0
		test_money = 0
		for player in all_players:
			if player.idx == self.idx:
				test_money = self.money
				for color in game.colors:
					test_money += new_stocks[color]*max(new_cost[color], game.cost[color])
			else:
				players += 1
				delta_money = player.money
				for color in game.colors:
					if new_cost[color] < game.min_price:
						stocks_to_leave = delta_money//(game.cost[color] - new_cost[color])
						stocks_left = min(stocks_to_leave, player.stocks[color])
						delta_money -= stocks_left*(game.cost[color] - new_cost[color])
						delta += stocks_left * game.min_price
					else:
						delta += player.stocks[color] * new_cost[color]

				delta += delta_money
		
		result = test_money - delta//players

		if card[-1] == 'small' and result > 0:
			result *= 3
		elif card[-1] == 'small' and result < 0:
			result //= 3
		return result

	def compare_avg_delta_div(self, all_players, card, new_stocks, new_cost, new_money):
		"""Оптимизируем отрыв от оппонента"""
		players = 0
		delta   = 0
		test_money = 0
		for player in all_players:
			if player.idx == self.idx:
				test_money = self.money
				for color in game.colors:
					test_money += new_stocks[color]*max(new_cost[color], game.cost[color])
			else:
				players += 1
				delta_money = player.money
				for color in game.colors:
					if new_cost[color] < game.min_price:
						stocks_to_leave = delta_money//(game.cost[color] - new_cost[color])
						stocks_left = min(stocks_to_leave, player.stocks[color])
						delta_money -= stocks_left*(game.cost[color] - new_cost[color])
						delta += stocks_left * game.min_price
					else:
						delta += player.stocks[color] * new_cost[color]

				delta += delta_money

		if delta == 0:
			delta = 1
		result = float(test_money) / delta//players

		if card[-1] == 'small' and result > 1:
			result *= 5
		elif card[-1] == 'small' and result < 1:
			result //= 3
		print card, "%2.5f" % result
			
		return result

	def compare_avg_delta_primitive(self, all_players, card, new_stocks, new_cost, new_money):
		"""Оптимизируем отрыв от оппонента"""
		players = 0
		delta   = 0
		test_money = 0
		for player in all_players:
			if player.idx == self.idx:
				test_money = self.money
				for color in game.colors:
					test_money += new_stocks[color]*new_cost[color]
			else:
				players += 1
				delta += game.stocks2money(new_stocks, new_cost)

		result = test_money - delta//players
		if card[-1] == 'small' and result > 0:
			result *= 3
		elif card[-1] == 'small' and result < 0:
			result //= 3
		return result

#
# Стратегии покупки после карты
#
	def buy_none(self):
		"""Не покупаем ничего"""
		pass

	def buy_all_equal_money(self):
		"""Вкладываем поровну во все акции, кроме тех,
		в которые у нас вложено наибольшие деньги"""
		max_in_color = 0
		max_color = None

		for color in game.colors:
			if self.stocks[color]*game.cost[color] >= max_in_color:
				max_color = color
				max_in_color = self.stocks[color]*game.cost[color]

		if max_in_color == 0 and self.money == 0:
			return
		
		part_to_invest = self.money//3
		for color in game.colors:
			if color != max_color:
				can_buy = part_to_invest//game.cost[color]
				self.stocks[color] += can_buy
				self.money -= game.cost[color]*can_buy
		return self.buy_cheapest()
	
	def buy_all_equal(self):
		"""Покупаем поровну всех акций в штуках, кроме тех,
		в которые у нас вложено наибольшие деньги"""
		max_in_color = 0
		max_color = None

		for color in game.colors:
			if self.stocks[color]*game.cost[color] >= max_in_color:
				max_color = color
				max_in_color = self.stocks[color]*game.cost[color]

		if max_in_color == 0 and self.money == 0:
			return

		sum_price = 0
		for color in game.colors:
			if color != max_color:
				sum_price += game.cost[color]

		can_buy = self.money//sum_price
		for color in game.colors:
			if color != max_color:
				self.stocks[color] += can_buy
				self.money -= game.cost[color]*can_buy

		return self.buy_cheapest()
		
		
	def buy_cheapest(self):
		"""Покупаем самые дешевые акции"""
		min_price = None
		min_color = None
		for color in game.colors:
			if min_price is None:
				min_price = game.cost[color]
				min_color = color
			else:
				if game.cost[color] < min_price:
					min_price = game.cost[color]
					min_color = color

		if min_color:
			can_buy = self.money //min_price
			self.stocks[min_color] += can_buy
			self.money = self.money % min_price
		return
	
	def buy_by_estimate(self):
		"""Смотрим прогноз и выбираем самые дорогие в будущем"""
		evaluations = self.evaluate_colors()
		estimations = game.cost.copy()

		max_color = None
		max_estimate = None
		for color in game.colors:
		#	estimations[color] += evaluations[color]
			if max_color is None or evaluations[color] > max_estimate:
				max_estimate = estimations[color]
				max_color    = color

		can_buy = self.money//game.cost[max_color]
		self.stocks[max_color] += can_buy
		self.money = self.money % game.cost[max_color]
		return self.buy_cheapest

	def __init__(self, player_id):
		"""Конструктор"""
		self.idx = player_id
		self.name = "Player " + str(self.idx)
		
		self.money = 0
		self.stocks = {}
		self.cards      = []
		self.used_cards = [] 
		for color in game.colors:
			self.stocks[color] = 1

		#Настройки стратегий по умолчанию
		self.interactive = 0 

		self.compare    = self.compare_avg_delta
		self.buy_after  = self.buy_cheapest
		return

	def invariant(self):
		"""Базовые проверки"""
		if self.money < 0:
			raise NameError, 'Money < 0' + repr(self)

		for color in game.colors:
			if self.stocks[color] < 0:
				raise NameError, 'Stocks ' + color + ' < 0'
		return
	
	def __repr__(self):
		"""Печать текущего состояния игрока"""
		repr = self.name
		repr = repr + "\nStocks: " + str(self.stocks) + "\nMoney: "+ str(self.money) 
		if len(self.cards):
			repr +=	"\nCards: " + str(self.cards)
		repr += "\n=========================="
		return repr

	def get_best_move(self, cost):
		"""Выбор оптимальной карты для хода"""
		best = {}
		best['card']    = []
		best['variant'] = []
		best['money']   = None
		best['stocks']  =	self.stocks.copy() 

		new_stocks  = {}

		free_money  = 0

		for card in self.cards:
			for variant in game.variants(card):
				new_cost  = game.evaluate_card(card, variant, cost)
		
				if len(self.cards) > 1:
					stocks_up = None
					money_in_others = self.money
					for key in new_cost.keys():
						if new_cost[key] > cost[key]:
							stocks_up = key
							new_stocks[key] = self.stocks[key]
						else:
							money_in_others += self.stocks[key]*cost[key]
							new_stocks[key] = 0
					
					new_stocks[stocks_up] += money_in_others//cost[stocks_up]
					new_money = money_in_others % cost[stocks_up]
				else:
					new_money  = self.money
					new_stocks = self.stocks
				
#				if self.idx == 1 and len(self.used_cards) < len(self.cards):
#					self.compare = self.compare_small_first
#				else:
#					self.compare = self.compare_avg_delta
				result = self.compare(game.players, card, new_stocks, new_cost, new_money)
				if best['money'] is None or result > best['money']:
					best['card']    = card
					best['variant'] = variant
					best['money']   = result
					best['stocks']  = new_stocks.copy()
					free_money    = new_money

		return (best, free_money)
	
	def mini_report(self, msg, params = ()):
		"""Минимальная информация о текущем состоянии"""
		print msg, "\nТекущая стоимость: "
		for color in game.colors:
			print colored("%6s: цена %3d, на руках %d" % (color, game.cost[color], self.stocks[color]), color, attrs = ['bold'] )
		print " денег: %d" % self.money
		if 'used' in params:
			print "Использованы карты:", self.used_cards
		return
	
	def sell_interactive(self, prev_stocks):
		"""Продажа акций"""
		self.mini_report ("Имущество игрока перед продажей: ")

		for color in game.colors:
			if prev_stocks is None:	
				can_sell = self.stocks[color]
			else:
				can_sell = min(prev_stocks[color], self.stocks[color])

			if can_sell == 0: 
				continue	

			sell = game.limited_input("Продать " + color + ", %d - %d: ", 0, can_sell)
			self.stocks[color] -= sell
			self.money += game.cost[color] * sell
		return self.money

	def buy_interactive(self):
		"""Покупка акций"""
		self.mini_report ("Имущество игрока перед покупкой: ")
		for color in game.colors:
			can_buy = self.money//game.cost[color]
			if can_buy == 0: 
				continue
			buy = game.limited_input("Купить " + color + ", %d - %d: ", 0, can_buy)
			self.stocks[color] += buy
			self.money -= game.cost[color] * buy
		return self.money
	
	def get_best_move_interactive(self, cost):
		"""Для игры в ручном режиме"""
		print "Текущая стоимость: ", cost
		print "Мое имущество: ", self
		best = {}
		if len(self.cards) > 1:
			self.money = self.sell_interactive(None)
			self.mini_report ("Имущество игрока после продажи: ")
			self.money = self.buy_interactive ()
		best['stocks']  = self.stocks

		self.mini_report ("Имущество игрока перед картой: ")
		#выбрать карту
		idx = 0
		for card in self.cards:
			print idx, "-", colored(card, card[0], attrs = ['bold'])
			idx += 1
		
		card_idx = game.limited_input("Выберите карту, %d - %d: ", 0, idx - 1)
		best['card'] = self.cards[card_idx]

		#выбрать вариант
		variants = game.variants(best['card'])
		idx_var = 0
		for variant in variants:
			print idx_var, "-", variant
			idx_var += 1

		var_idx = game.limited_input("Выберите вариант, %d - %d: ", 0, idx_var - 1)
		best['variant'] = variants[var_idx]
		return best, self.money

	def after_card_applied(self, prev_stocks):
		"""Последняя фаза хода
		Продаем все, что можно"""
		if len(self.cards) > 0:
			if self.interactive:
				self.sell_interactive(prev_stocks)	
				self.mini_report ("Имущество игрока после продажи: ")
				self.buy_interactive()
				self.mini_report ("Имущество игрока после покупки: ")
			else:
				for color in game.colors:
					if prev_stocks[color] > 0:
						max_to_sale = min(self.stocks[color], prev_stocks[color])
						self.stocks[color] -= max_to_sale
						self.money += max_to_sale*game.cost[color]

				self.buy_after()
				self.mini_report ("Имущество игрока после хода: ")
		return

	def make_move(self):
		"""Главная процедура хода"""
		self.invariant()
		#Сохраняем предыдущее состояние
		prev_stocks = self.stocks.copy()

		print "\n", self.name
		self.mini_report ("Имущество игрока на начало хода: ", ('used'))

		#Выбрали лучший ход
		if self.interactive:
			best, free_money = self.get_best_move_interactive(game.cost)
		else:
			best, free_money = self.get_best_move(game.cost)
#			if self.idx == 0:
#				best, free_money = self.get_best_move(game.cost)
#			else:
#				best, free_money = self.get_best_move_2colors(game.cost)

		self.stocks = best['stocks']
		self.money  = free_money
		
		self.mini_report("Состояние счета перед применением карты: ")
		print "Применяем карту", best['variant']

		self.cards.remove(best['card'])
		self.used_cards.append(best['card'])
		game.make_player_move(self.idx, best['card'], best['variant'])
		self.invariant()

		self.after_card_applied(prev_stocks)
		self.invariant()

		cards_left = {'small': 0, 'large': 0}
		if not self.interactive:
			for card in self.cards:
				cards_left[card[-1]] += 1

			print "Осталось карт", cards_left
			
		return

	def process_crash(self, color, delta):
		"""
		Обрабатывает ситуацию частичного банкротства.
		Сначала изымает средства, чтобы компенсировать падение части акций.
		Потом продает остаток акций
		"""
		if self.stocks[color] > 0:
			stocks_to_leave = self.money//delta
			stocks_left = min(stocks_to_leave, self.stocks[color])
			self.money  -= stocks_left*delta
			self.stocks[color] = stocks_left
		return

	def evaluate_colors(self):
		"""Оценка способности остатка карт на руках"""
		evaluations = {}
		for color in game.colors:
			evaluations[color] = 0

		for card in self.cards:
			if card[-1] == 'small':
				if card[1] > 0:
					evaluations[card[0]] += card[1]
				else:
					for color in game.colors:
						if color != card[0]:
							evaluations[color] += 90 + card[1]
			else:
				if card[1] == ':2':
					for color in game.colors:
						if color != card[0]:
							evaluations[color] += game.cost[color]
				elif card[1] == '*2':
					evaluations[card[0]] += game.cost[card[0]]
				else:
					evaluations[card[0]] += 100
		print "Ожидания:", evaluations
		return evaluations

	def get_best_move_2colors(self, cost):
		"""Выбор оптимальной карты для хода
		
		На первом ходу выбираем 2 цвета, 
		которые мы можем поменять этим ходом
		и продаем остальные акции, покупая акции этих цветов
		затем предъявляем карту

		На каждом следующем ходу, кроме последнего
		Находим цвета, которые можем повышать

		Если у нас акции обоих цветов допускают повышение, то ничего не делаем.
		Если одного допускают повышение, другого - нет, то продаем тот, который не допускает 
		Если карты ни одного цвета не допускают повышение, то продаем оба, покупаем остальные

		Применяем карту по стандартному алгоритму

		продаем карты, которые повысились, если можем, или которые не трогались
		покупаем карты, которые сможем повысить следующим ходом по максимуму
		"""

		best = {}
		best['card']    = []
		best['variant'] = []
		best['money']   = None
		best['stocks']  =	self.stocks.copy() 

		new_stocks  = self.stocks.copy()

		free_money  = self.money
		if len(self.used_cards) == 0:
			for card in self.cards:
				if len(best['card']) > 0:
					break
				for variant in game.variants(card):
					sum_our    = 0
					sum_others = 0
					for color in game.colors:
						if color in (variant[0][0], variant[1][0]):
							sum_our += cost[color]
						else:
							sum_others += cost[color]
					
					if sum_our > sum_others:
						best['card'] = card
						best['variant'] = variant
						break

			for color in game.colors:
				if color not in (best['variant'][0][0], best['variant'][1][0]):
					free_money += cost[color]*new_stocks[color]
					new_stocks[color] = 0

			while (free_money > cost[best['variant'][0][0]]) or \
			      (free_money > cost[best['variant'][1][0]]):
				for color in (best['variant'][0][0], best['variant'][1][0]):
					if free_money > cost[color]:
						free_money -= cost[color]
						new_stocks[color] += 1
			best['stocks'] = new_stocks
		else:
			return self.get_best_move(cost)
			if len(self.cards) > 1:
				my_colors = filter(lambda x: self.stocks[x] > 0, game.colors)
				evaluations = self.evaluate_colors()
				to_sell   = []
				
				for color in my_colors:
					if evaluations[color] == 0:
						to_sell.append(color)
				
				for color in to_sell:
					free_money += new_stocks[color]*cost[color]
					new_stocks[color] = 0

				colors_with_stocks = len(filter(lambda x: new_stocks[x] > 0, game.colors))

				if colors_with_stocks:
					for card in self.cards:
						for variant in game.variants(card):
							new_cost  = game.evaluate_card(card, variant, cost)

							stocks_up = None
							for key in new_cost.keys():
								if new_cost[key] > cost[key]:
									stocks_up = key
									new_stocks[key] = self.stocks[key]
									break
							new_stocks[stocks_up] += free_money//cost[stocks_up] 
							new_money = free_money % cost[stocks_up]
							result = self.compare(game.players, card, new_stocks, new_cost, new_money)
							print card, variant, success, test_money
							if best['money'] is None or result > best['money']:
								best['card']    = card
								best['variant'] = variant
								best['money']   = result
								best['stocks']  = new_stocks.copy()
								free_money    = new_money

				else:
					colors_to_buy = filter(lambda x: evaluations[x] > 0, game.colors)

					sum_to_buy = 0
					for color in colors_to_buy:
						sum_to_buy += cost[color]

					for color in colors_to_buy:
						new_stocks[color] = free_money//sum_to_buy
						new_money         = free_money % sum_to_buy
					for card in self.cards:
						for variant in game.variants(card):
							new_cost  = game.evaluate_card(card, variant, cost)
							result = self.compare(game.players, card, new_stocks, new_cost, new_money)
							if success:
								best['card']    = card
								best['variant'] = variant
								best['money']   = result
								best['stocks']  = new_stocks.copy()
								free_money    = new_money
			else:
				new_money  = self.money
				new_stocks = self.stocks

				for card in self.cards:
					for variant in game.variants(card):
						new_cost  = game.evaluate_card(card, variant, cost)
						result = self.compare(game.players, card, new_stocks, new_cost, new_money)
						if success:
							best['card']    = card
							best['variant'] = variant
							best['money']   = result
							best['stocks']  = new_stocks.copy()
							free_money    = new_money

		return (best, free_money)

	def buy_by_2colors(self):
		evaluations = self.evaluate_colors()
		good_colors = filter(lambda x: evaluations[x] > 0, game.colors)

		colors_to_buy = []
		for color in good_colors:
			colors_to_buy.append(color)

		def compare_by_percent(a,b):
			if evaluations[a]//game.cost[a] < evaluations[b]//game.cost[b]:
				return 1
			if evaluations[a]//game.cost[a] > evaluations[b]//game.cost[b]:
				return -1
			return 0

		colors_to_buy.sort(compare_by_percent)
		print colors_to_buy
		
		sum_to_buy = 0
		i = 0
		for color in colors_to_buy:
			i += 1
			sum_to_buy += game.cost[color]
			if i == 2:
				break
		
		i = 0
		for color in colors_to_buy:
			i += 1
			self.stocks[color] = self.money//sum_to_buy
			if i == 2:
				break
		self.money         = self.money % sum_to_buy

		return self.buy_cheapest()
	
