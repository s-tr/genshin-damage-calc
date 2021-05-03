import numpy as np 
from constants import *

class GameEvent:
	"""
	Base class of all things that can happen in game: damage dealt,
	buff start, buff ending
	"""
	pass

class DamageInstance(GameEvent):
	"""
	Base class for all damage instances.
	"""
	def __init__(self):
		pass

	def calculate_base_damage(self, stat_line):
		"""
		Return a tuple: (base damage, element, ignore defence stat)
		"""
		raise NotImplemented("Not implemented: DamageInstance.calculate_base_damage")

	def calculate_damage(self, stat_line, self_level, opp_level, opp_res, def_shred=0):
		(dmg, elem, ignore_def) = self.calculate_base_damage(stat_line)

		if not ignore_def:
			dmg *= (100+self_level) / ((100+self_level) + (100+opp_level)*(1-def_shred))

		res = opp_res.get(elem,0)
		if res<0:
			mult = 1 - res/2
		elif res<0.75:
			mult = 1 - res
		else:
			mult = 1/(4*res+1)

		return dmg*mult

class RegularDamage(DamageInstance):
	"""
	Represents autoattack and skill damage (i.e. those represented by %).
	"""
	def __init__(self, element, damage_source, multiplier, stat = Stats.ATK, reaction = None):
		self.elem_ = element
		self.damage_source_ = damage_source
		self.multiplier_ = multiplier
		self.stat_ = stat
		self.rx_ = reaction

		# sanity check: is the reaction type suitable for this?
		if reaction is not None:
			if isinstance(reaction, AmpReaction):
				if reaction is AmpReaction.MELT:
					if element is Element.PYRO:
						self.amp_multiplier_ = 2
					elif element is Element.CRYO:
						self.amp_multiplier_ = 1.5
					else:
						raise ValueError("Invalid element for Melt reaction: "+element.name)
				elif reaction is AmpReaction.VAPE:
					if element is Element.PYRO:
						self.amp_multiplier_ = 1.5
					elif element is Element.HYDRO:
						self.amp_multiplier_ = 2
					else:
						raise ValueError("Invalid element for Vaporize reaction: "+element.name)
				else:
					raise ValueError("Unsupported amp reaction: "+reaction.name)
			else:
				raise ValueError("Expected AmpReaction, got "+str(type(reaction)))
		else:
			self.amp_multiplier_ = 1

	def calculate_base_damage(self, stat_line):
		dmg = self.multiplier_ * stat_line.get(self.stat_)

		# multiply by crit, limiting crit rate to 100%
		crate = min(stat_line.get(Stats.CRIT_RATE), 1.00)
		cdmg = stat_line.get(Stats.CRIT_DAMAGE)
		dmg *= (1 + crate*cdmg)

		# apply damage bonus
		dmg *= (1 + stat_line.get(Stats.DAMAGE_BONUS))

		# amp reaction
		if self.amp_multiplier_ != 1:
			em = stat_line.get(Stats.ELEMENTAL_MASTERY)
			em_bonus = 2.78*em/(1400+em)
			em_bonus += stat_line.get(Stats.MELT_VAPE_BONUS)
			dmg *= self.amp_multiplier_ * (1+em_bonus)

		return (dmg, self.elem_, False)

class TransformativeReaction(DamageInstance):
	"""
	Represents transformative reaction damage (Swirl, ElectroCharge, etc)
	"""
	def __init__(self, reaction_type):
		self.reaction_type_ = reaction_type

	def calculate_base_damage(self, stat_line):
		# unimplemented
		return (0, Element.ALL, True)



class Buff(GameEvent):
	"""
	Represents a general addition of stats to the character. This can be from:
	  - Weapon stat lines
	  - Artifact stat lines
	  - Skills/Passives
	"""
	def check_applies(self, dmg_instance):
		raise NotImplemented("Not implemented: Buff.check_applies")

	def apply(self, stat_list):
		raise NotImplemented("Not implemented. Buff.apply")

class ConditionalBuff(Buff):
	"""
	Denotes an conditional increase to stats based on what kind of damage (element/damage source) the buff applies to.

	Example: Gladiator 4-set would be
	Buff([[Stats.DAMAGE_BONUS, 0.35]], damage_source=DamageSource.NORMAL_ATTACK)

	Example: Festering Desire R5 would be
	Buff([[Stats.BASE_ATK, 510], [Stats.ENERGY_RECHARGE, 0.459]])
	Buff([[Stats.DAMAGE_BONUS, 0.32], [Stats.CRIT_RATE, 0.12]], damage_source = DamageSource.ELEMENTAL_SKILL)

	Example: Crimson Witch 2-set would be
	Buff([[Stats.DAMAGE_BONUS, 0.15]], element = [Element.PYRO])

	Example: Gladiator 2-set would be
	Buff([[Stats.ATK_PERCENT, 18]])
	"""

	def __init__(self, buff_list, element=None, damage_source=None):
		self.buff_list_ = buff_list
		self.elem_ = element
		self.damage_source_ = damage_source

	def check_applies(self, dmg_instance):
		if isinstance(dmg_instance, RegularDamage):
			if self.elem_ == None or self.elem_ == dmg_instance.elem_:
				if self.damage_source_ == None or self.damage_source_ & dmg_instance.damage_source_:
					return True
			return False
		else:
			return True

	def apply(self, stat_line):
		for x in self.buff_list_:
			stat = x[0]
			amount = x[1]
			stat_line.add(stat, amount)

class StatConversion(Buff):
	"""
	Denotes a conversion of stats to other stats
	(e.g. Mona ER->Hydro%, Bennett BaseATK->ATK, Hu Tao HP -> ATK, Noelle DEF -> ATK)

	Example: Noelle's C6 Lv.13 ulti would be:
	StatConversion(Stats.DEF, 1.35, Stats.ATK_FLAT)

	Example: Hu Tao's Lv. 8 skill would be:
	StatConversion(Stats.HP, 0.0566, Stats.ATK_FLAT, Stats.ATK_BASE, 4.00)
	"""

	def __init__(self, source_stat, factor, destination_stat, limit_stat=None, limit_ratio=None):
		self.source_stat_ = source_stat
		self.factor_ = factor
		self.destination_stat_ = destination_stat
		self.limit_stat_ = limit_stat
		self.limit_ratio_ = limit_ratio

	def check_applies(self, dmg_instance):
		return True

	def apply(self, stat_line):
		amount = self.factor_ * stat_line.get(self.source_stat_)
		if self.limit_stat_ is not None:
			limit = self.limit_ratio_ * stat_line.get(self.limit_stat_)
			if amount > limit:
				amount = limit
		stat_line.add(self.destination_stat_, amount)

class EndBuff(GameEvent):
	def __init__(self, buff):
		if not isinstance(buff,Buff):
			raise ValueError("Expected Buff as input, got "+str(type(buff)))
		self.buff_ = buff

class StatLine:
	"""
	Represents a character's stats.

	Note: Unless specified in the name, percentages should be specified in absolute terms
	(i.e. 35% -> 0.35)
	"""

	def __init__(self):
		self.stats_ = {
			Stats.CONSTANT: 1,
			Stats.ATK : 0,
			Stats.ATK_BASE : 0,
			Stats.ATK_PERCENT : 0,
			Stats.ATK_FLAT : 0,
			Stats.DEF : 0,
			Stats.DEF_BASE : 0,
			Stats.DEF_PERCENT : 0,
			Stats.DEF_FLAT : 0,
			Stats.HP : 0,
			Stats.HP_BASE : 0,
			Stats.HP_PERCENT : 0,
			Stats.HP_FLAT : 0,
			Stats.ENERGY_RECHARGE : 1.00,
			Stats.ELEMENTAL_MASTERY : 0,
			Stats.CRIT_RATE : 0.05,
			Stats.CRIT_DAMAGE : 0.50,
			Stats.DAMAGE_BONUS : 0,
			Stats.MELT_VAPE_BONUS : 0,
			Stats.ELECTRO_REACTION_BONUS : 0,
			Stats.SWIRL_BONUS : 0
		}

	def _recalc(self):
		base = self.stats_[Stats.ATK_BASE]
		perc = self.stats_[Stats.ATK_PERCENT]
		flat = self.stats_[Stats.ATK_FLAT]
		self.stats_[Stats.ATK] = base*(1+perc/100)+flat

		base = self.stats_[Stats.HP_BASE]
		perc = self.stats_[Stats.HP_PERCENT]
		flat = self.stats_[Stats.HP_FLAT]
		self.stats_[Stats.HP] = base*(1+perc/100)+flat

		base = self.stats_[Stats.DEF_BASE]
		perc = self.stats_[Stats.DEF_PERCENT]
		flat = self.stats_[Stats.DEF_FLAT]
		self.stats_[Stats.DEF] = base*(1+perc/100)+flat

		self.stats_[Stats.CONSTANT] = 1


	def get(self, stat):
		if stat not in self.stats_:
			raise ValueError("Invalid stat")
		else:
			return self.stats_[stat]

	def set(self, stat, value):
		if stat not in self.stats_:
			raise ValueError("Invalid stat")
		if stat in [Stats.ATK, Stats.HP, Stats.DEF]:
			raise ValueError("Cannot directly set this stat: " + str(stat))
		self.stats_[stat] = value
		self._recalc()

	def add(self, stat, value):
		if stat not in self.stats_:
			raise ValueError("Invalid stat")
		if stat is Stats.ATK:
			stat = Stats.ATK_FLAT
		if stat is Stats.HP:
			stat = Stats.HP_FLAT
		if stat is Stats.DEF:
			stat = Stats.DEF_FLAT
		self.stats_[stat] += value
		self._recalc()

	def __str__(self):
		return str(self.stats_)

	def copy(self):
		new = StatLine()
		new.stats_ = self.stats_.copy()
		return new
