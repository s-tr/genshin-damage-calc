from structures import *

def make_stats(atk, defense, hp, crit_rate=0.05, crit_dmg=0.50, dmg_bonus=0):
	stats = StatLine()
	stats.set(Stats.ATK_BASE, atk)
	stats.set(Stats.DEF_BASE, defense)
	stats.set(Stats.HP_BASE, hp)
	stats.set(Stats.CRIT_RATE, crit_rate)
	stats.set(Stats.CRIT_DAMAGE, crit_dmg)
	stats.set(Stats.DAMAGE_BONUS, dmg_bonus)
	return stats

def make_resistances(phys_res,elem_res):
	return {
		Element.PHYSICAL : phys_res,
		Element.PYRO : elem_res,
		Element.HYDRO : elem_res,
		Element.CRYO : elem_res,
		Element.ELECTRO : elem_res,
		Element.ANEMO : elem_res,
		Element.GEO : elem_res,
		Element.DENDRO : elem_res
	}

class Calculator:
	"""
	Takes a list of events 
	"""

	def __init__(self, base_stats, base_buffs=[]):
		self.base_stats_ = base_stats
		self.events_ = [] + list(base_buffs)
		self.verbose_ = False

	def _log(self, message):
		if self.verbose_:
			print(message)

	def addEvent(self, event):
		self.addEvents([event])

	def addEvents(self, events):
		"""

		"""
		self.events_.extend(events)
		return self

	def calcDamage(self, self_level, opp_level, opp_res, def_shred=0, itemize=False):
		current_buffs = []
		dmg_instances = []
		for event in self.events_:
			if isinstance(event, DamageInstance):
				self._log("Damage")
				stats = self.base_stats_.copy()
				for buff in current_buffs:
					if buff.check_applies(event):
						buff.apply(stats)
						self._log(buff)
				dmg_instances.append(event.calculate_damage(stats, self_level, opp_level, opp_res, def_shred))
				self._log(dmg_instances[-1])
			elif isinstance(event, Buff):
				self._log("Buff")
				self._log(event)
				current_buffs.append(event)
			elif isinstance(event, EndBuff):
				self._log("End buff")
				self._log(event.buff_)
				current_buffs.remove(event.buff_)
		if itemize:
			return dmg_instances
		else:
			return sum(dmg_instances)


	def calcDamageWith(self, extra_events, self_level, opp_level, opp_res, def_shred=0, itemize=False):
		new_events = self.events_ + extra_events
		old_events = self.events_
		self.events_ = new_events
		dmg = self.calcDamage(self_level, opp_level, opp_res, def_shred, itemize)
		self.events_ = old_events
		return dmg
