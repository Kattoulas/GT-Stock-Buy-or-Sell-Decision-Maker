import numpy as np
from itertools import product

print("Assumptions of Game Theory")
print("--------------------------")
print("1. Rationality - Players choose strategies that maximise their payoff.")
print("2. Objectives - Each player has a clear objective, such as maximising profit.")
print("3. Strategic Interdependence - A player's best decision depends on the actions of other players.")
print("4. Known Rules - All players understand the rules, available strategies, and possible outcomes.")
print("5. Common Knowledge - Players know that everyone is rational, and everyone knows that everyone knows this.")
print("6. Stable Preferences - Players' objectives and preferences remain consistent throughout the game.")
print("7. Strategic Thinking - Players anticipate how others will react before making decisions.")
print("8. Comparable Payoffs - Every possible outcome can be assigned a payoff, allowing players to compare strategies.")
print("9. Information Structure - Players have either complete or incomplete information depending on the game.")
print("10. Nash Equilibrium - The game reaches a state where no player can improve their payoff by changing strategy alone.")
print()
print('For this game:')
print('There are two players in this game, the bull and the bear, both are trying to maximise their profit')
print()
print('The bull wants to either buy long futures, hold futures or exit his position and hold cash')
print()
print('The bear wants to either sell short futures, hold futures or exit his position')
print()
print('We assume if there is trailing and forecasted change in the price of the stock, that it changes linearly, so the market is either always bull, neutral or bear and that sentiment is set for a year starting today')
print()
print('We assume players do not have complete information in the game, and that they cannot accurately predict stock movement')
print()
print('We assume that the game is a one period game, of a year from today')
print()
print('Short Ratio represents the squeeze risk')
print()
print("Nash Equilibrium Assumption: A Nash equilibrium is assumed to exist when neither the bull nor the bear can increase their expected return by changing their strategy, given the other player's strategy.")
print("Due to the simplified nature of this model, Nash equilibrium is approximated by comparing player's risk-adjusted payoff and the sign of this, rather than constructing a complete payoff matrix of all possible strategies.")
print()
print('You can use this program to determine the options the players in this game have, and the payoffs in each scenario, tailored to exactly your situation in the market currently')
print()

rBu = float(input('Input the risk aversion for the bull, as a percentage:')) / 100
rBe = float(input('Input the risk aversion for the bear, as a percentage:')) / 100
p = float(input('Enter the current price of the stock:'))
g = float(input('Enter the percentage change in growth YTD:')) / 100
fG = float(input('Enter the forcasted percentage change in price YTD:')) / 100
i = float(input('Enter the rate of inflation YTD:')) / 100
shortR = float(input('What is the short ratio of this stock'))

if 0 < shortR < 1:
     k = 0.01
elif 1 < shortR < 3:
     k = 0.02
elif 3 < shortR < 5:
     k = 0.05
elif 5 < shortR < 8:
     k = 0.12
elif 8 < shortR < 12:
     k = 0.175
elif 12 < shortR < 15:
     k = 0.3
else:
     k = 0.4

squeeze_penalty = 1 + k

while True:
    future_prices = np.array(input("Enter 5 expected prices for YTD, next year: ").split(), dtype=float)
    if len(future_prices) != 5:
            print("Enter exactly 5 prices.")
            future_prices = np.array(input("Enter 5 expected prices for YTD, next year: ").split(), dtype=float)
            continue

    probability = np.array(input("Enter the percentage probabilities for each expected price respectively: ").split(), dtype=float) / 100
    if len(probability) != 5:
            print("Enter exactly 5 probabilities.")
            probability = np.array(input("Enter probabilities for each expected price respectively: ").split(), dtype=float) / 100
            continue
    
    if abs(np.sum(probability) - 1) > 0.001:
            print("Probabilities must add to 100%")
            probability = np.array(input("Enter probabilities for each expected price respectively: ").split(), dtype=float) / 100
            continue
    
    v = np.array(input('Enter the yearly historical returns for the last 5 years of the stock, as a percentage:').split(), dtype=float) / 100
    if len(v) != 5:
            print('Enter exactly 5 yearly historical returns, from the past 5 years')
            v = np.array(input('Enter the yearly historical returns for the last 5 years of the stock, as a percentage:').split(), dtype=float) / 100
            continue
    break

predictiveP = np.sum(future_prices * probability)
vol = np.std(v)
     
bull_strategies = {"Buy": 1.0, "Hold": 0.5, "Exit": 0.0}
bear_strategies = {"Short": 1.0, "Hold": 0.5, "Exit": 0.0}
 
def payoffs(p_bull: float, p_bear: float):
    bull_payoff = (((predictiveP - p) - (rBu*vol)) * squeeze_penalty) / p
    bear_payoff = (((p - predictiveP) - (rBe*vol)) / squeeze_penalty) / p
    bull_payoff = bull_payoff * p_bull
    bear_payoff = bear_payoff * p_bear

    bull_payoff = round(bull_payoff, 2)
    bear_payoff = round(bear_payoff, 2)
 
    if bear_payoff < -0.1:
        bull_payoff = bull_payoff + (-0.15)*bear_payoff
    elif bull_payoff < -0.1:
        bear_payoff = bear_payoff + (-0.15)*bull_payoff
    return bull_payoff, bear_payoff

matrix = {}
for (bull_cond, p_bull), (bear_cond, p_bear) in product(bull_strategies.items(), bear_strategies.items()):
    matrix[(bull_cond, bear_cond)] = payoffs(p_bull, p_bear)

print("Payoff matrix (Bull payoff %, Bear payoff %)")
header = f"{'':}" + "".join(f"{b:>22}" for b in bear_strategies)
print(header)
for bull_cond in bull_strategies:
    row = f"{bull_cond:10}"
    for bear_cond in bear_strategies:
        bp, bep = matrix[(bull_cond, bear_cond)]
        row += f"{'(' + str(round(bp * 100, 2)) + '%,' + str(round(bep * 100, 2)) + '%)':>22}"
    print(row)
print()

def bull_best_response(bear_cond):
     scores = {bull_cond: matrix[(bull_cond, bear_cond)][0] for bull_cond in bull_strategies}
     best =  max(scores.values())
     return [b for b, s in scores.items() if s == best]

def bear_best_response(bull_cond):
     scores = {bear_cond: matrix[(bull_cond, bear_cond)][1] for bear_cond in bear_strategies}
     best =  max(scores.values())
     return [b for b, s in scores.items() if s == best]
               
nash_equilibria = []
for bull_cond in bull_strategies:
     for bear_cond in bear_strategies:
          if bull_cond in bull_best_response(bear_cond) and bear_cond in bear_best_response(bull_cond):
               nash_equilibria.append((bull_cond, bear_cond))

print("Best strategies")
for bull_cond in bull_strategies:
     print(f"If Bull plays{bull_cond:6}, Bear's best responses: {bear_best_response(bull_cond)}")
for bear_cond in bear_strategies:
     print(f"If Bear plays{bear_cond:6}, Bull's best responses: {bull_best_response(bear_cond)}")
print()

if nash_equilibria:
     print("Pure strategy Nash equilibrium found")
     for bull_cond, bear_cond in nash_equilibria:
          bull_payoff, bear_payoff = matrix[((bull_cond, bear_cond))]
          print(f"Bull: {bull_cond}, Bear: {bear_cond} -> Payoffs: {round(bull_payoff*100)}%, {round(bear_payoff*100)}%")
else:
    print("No pure strategy Nash equilibrium found, may not exist in this matrix")

#end