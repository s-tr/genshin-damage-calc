from enum import *

class Element(Enum):
	ALL = 0
	PHYSICAL = 1
	PYRO = 2
	HYDRO = 3
	CRYO = 4
	ELECTRO = 5
	ANEMO = 6
	GEO = 7
	DENDRO = 8

class DamageSource(Flag):
	NORMAL_ATTACK = auto()
	CHARGED_ATTACK = auto()
	ELEMENTAL_SKILL = auto()
	ELEMENTAL_BURST = auto()
	OTHER = auto()
	ALL = NORMAL_ATTACK | CHARGED_ATTACK | ELEMENTAL_BURST | ELEMENTAL_SKILL | OTHER

class Stats(Enum):
	CONSTANT = 0

	ATK = 100
	ATK_BASE = 101
	ATK_PERCENT = 102
	ATK_FLAT = 103

	DEF = 200
	DEF_BASE = 201
	DEF_PERCENT = 202
	DEF_FLAT = 203
	
	HP = 300
	HP_BASE = 301
	HP_PERCENT = 302
	HP_FLAT = 303

	ENERGY_RECHARGE = 400

	ELEMENTAL_MASTERY = 500

	CRIT_RATE = 600

	CRIT_DAMAGE = 700

	DAMAGE_BONUS = 800
	MELT_VAPE_BONUS = 801
	ELECTRO_REACTION_BONUS = 802
	SWIRL_BONUS = 803
	

class AmpReaction(Enum):
	MELT = auto()
	VAPE = auto()

class TransformativeReaction(Enum):
	def __new__(cls, *args, **kwds):
		value = len(cls.__members__)+1
		obj = object.__new__(cls)
		obj._value_ = value
		return obj

	def __init__(self, type, bonus_stats):
		self.type = type
		self.bonus_stats = bonus_stats

	PYRO_SWIRL = Element.PYRO, [Stats.SWIRL_BONUS]
	CRYO_SWIRL = Element.CRYO, [Stats.SWIRL_BONUS]
	HYDRO_SWIRL = Element.HYDRO, [Stats.SWIRL_BONUS]
	ELECTRO_SWIRL = Element.ELECTRO, [Stats.SWIRL_BONUS]



