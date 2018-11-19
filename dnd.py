from random import choice, randint, sample
import math

def roll(num=1, type=20, mod=0):
	out = 0
	for i in range(num):
		out += randint(1,type)
	return out + mod
	

def readstr(string):
	mod = 0
	
	ind = max(string.find('+'), string.find('-'))
	if ind != -1:
		mod = int(string[ind:])
		string = string[:ind]
	
	spl = string.split('d')
	num = int(spl[0])
	type = int(spl[1])
	
	return (num, type, mod)


def sroll(string):
	return roll(*readstr(string))


def dropleast(num, type, mod, times):
	res = [roll(num, type, mod) for i in range(times)]
	res.remove(min(res))
	return sum(res)


def d20(mod,adv=None):
	if adv == 'advantage':
		return max(roll(), roll()) + mod
	elif adv == 'disadvantage':
		return min(roll(), roll()) + mod
	else:
		return roll() + mod
	

def genStats():
	stats = {}
	mods = {}
	for stat in ("str", "dex", "con", "int", "wis", "cha"):
		stats[stat] = dropleast(1, 6, 0, 4)
		mods[stat] =(stats[stat]-10)//2
	return {'stats': stats, 'mods': mods}
	

print(readstr("1d4"))


