from structures import *

class Calculator:
	"""
	Takes a list of events 
	"""

	def __init__(self, base_stats, base_buffs=[]):
		self.base_stats_ = base_stats
		self.events_ = [] + list(base_buffs)

	def addEvent(self, event):
		self.addEvents([event])

	def addEvents(self, events):
		"""

		"""
		self.events_.extend(events)
		return self

	def calcDamage(self, self_level, opp_level, opp_res, def_shred=0):
		current_buffs = []
		total_dmg = 0
		for event in self.events_:
			if isinstance(event, DamageInstance):
				stats = self.base_stats_.copy()
				for buff in current_buffs:
					if buff.check_applies(event):
						buff.apply(stats)
				total_dmg += event.calculate_damage(stats, self_level, opp_level, opp_res, def_shred)
			elif isinstance(event, Buff):
				current_buffs.append(event)
			elif isinstance(event, EndBuff):
				current_buffs.remove(event.buff_)
		return total_dmg


	def calcDamageWith(self, extra_events, self_level, opp_level, opp_res, def_shred=0):
		new_events = self.events_ + extra_events
		old_events = self.events_
		self.events_ = new_events
		dmg = self.calcDamage(self_level, opp_level, opp_res, def_shred)
		self.events_ = old_events
		return dmg
