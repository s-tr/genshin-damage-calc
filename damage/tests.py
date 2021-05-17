import unittest
import numpy.testing as npt

from calculator import *


class TestRegularDamage(unittest.TestCase):
	def test1(self):
		"""
		Test base damage calculation - no crits, no damage bonus, etc.
		"""
		dmg_instance = RegularDamage(Element.PHYSICAL,DamageSource.NORMAL_ATTACK,1.00)
		stats = make_stats(1000,0,0,0,0)
		dmg = dmg_instance.calculate_base_damage(stats)[0]
		self.assertAlmostEqual(dmg,1000)

		dmg_instance = RegularDamage(Element.ELECTRO,DamageSource.NORMAL_ATTACK,4.00)
		stats = make_stats(1600,0,0,0,0)
		dmg = dmg_instance.calculate_base_damage(stats)[0]
		self.assertAlmostEqual(dmg,6400)

	def test2(self):
		"""
		Test base damage calculation - with crits
		"""
		dmg_instance = RegularDamage(Element.PYRO,DamageSource.NORMAL_ATTACK,1.00)
		stats = make_stats(1000,0,0,0.50,1.00)
		dmg = dmg_instance.calculate_base_damage(stats)[0]
		self.assertAlmostEqual(dmg,1500)
		
		dmg_instance = RegularDamage(Element.ANEMO,DamageSource.ELEMENTAL_SKILL,0.60)
		stats = make_stats(2500,0,0,0.70,1.40)
		dmg = dmg_instance.calculate_base_damage(stats)[0]
		self.assertAlmostEqual(dmg,2970)

	def test3(self):
		"""
		Test base damage calculation - with crits and damage bonus
		"""
		dmg_instance = RegularDamage(Element.PYRO,DamageSource.CHARGED_ATTACK,2.50)
		stats = make_stats(2000,0,0,0.50,1.00,0.40)
		dmg = dmg_instance.calculate_base_damage(stats)[0]
		self.assertAlmostEqual(dmg,10500)
		
		dmg_instance = RegularDamage(Element.GEO,DamageSource.ELEMENTAL_BURST,5.00)
		stats = make_stats(1600,0,0,0.80,1.75,0.75)
		dmg = dmg_instance.calculate_base_damage(stats)[0]
		self.assertAlmostEqual(dmg,33600)
		
class TestCalculator(unittest.TestCase):
	def test1(self):
		"""
		One damage instance, no buffs
		1000 ATK, 50% CRate, 200% CDMG, 100% scaling, equal level = 1000 damage
		"""
		stats = make_stats(1000, 0, 0, 0.50, 2.00, 0)
		dmg_instance = RegularDamage(Element.PYRO,DamageSource.NORMAL_ATTACK,1.00)
		res = make_resistances(0,0)

		calc = Calculator(stats,[])
		calc.addEvents([dmg_instance])
		npt.assert_almost_equal(calc.calcDamage(100,100,res,itemize=True),[1000])

	def test2(self):
		"""
		Two damage instances, one unconditional buff between them
		1000 ATK, 50% CRate, 200% CDMG, 100% scaling, equal level = 1000 damage
		50% +ATK after 1st attack => 1500 damage
		"""
		stats = make_stats(1000, 0, 0, 0.50, 2.00, 0)
		buff1 = ConditionalBuff([[Stats.ATK_PERCENT,50]])
		dmg_instance = RegularDamage(Element.PYRO,DamageSource.NORMAL_ATTACK,1.00)
		res = make_resistances(0,0)

		calc = Calculator(stats,[])
		calc.addEvents([dmg_instance, buff1, dmg_instance])
		npt.assert_almost_equal(calc.calcDamage(100,100,res,itemize=True),[1000,1500])

	def test3(self):
		"""
		Two damage instances, one conditional buff between them (does not apply)
		1000 ATK, 50% CRate, 200% CDMG, 100% scaling, equal level = 1000 damage
		50% +ATK after 1st attack => 1500 damage
		"""
		stats = make_stats(1000, 0, 0, 0.50, 2.00, 0)
		buff1 = ConditionalBuff([[Stats.ATK_PERCENT,50]],element=Element.HYDRO)
		dmg_instance = RegularDamage(Element.PYRO,DamageSource.NORMAL_ATTACK,1.00)
		res = make_resistances(0,0)

		calc = Calculator(stats,[])
		calc.addEvents([dmg_instance, buff1, dmg_instance])
		npt.assert_almost_equal(calc.calcDamage(100,100,res,itemize=True),[1000,1000])

	def test4(self):
		"""
		Three damage instances, middle one is buffed
		1000 ATK, 50% CRate, 200% CDMG, 100% scaling, equal level = 1000 damage
		50% +ATK after 1st attack => 1500 damage
		"""
		stats = make_stats(1000, 0, 0, 0.50, 2.00, 0)
		buff1 = ConditionalBuff([[Stats.ATK_PERCENT,50]])
		dmg_instance = RegularDamage(Element.PYRO,DamageSource.NORMAL_ATTACK,1.00)
		res = make_resistances(0,0)

		calc = Calculator(stats,[])
		calc.addEvents([dmg_instance, buff1, dmg_instance, EndBuff(buff1), dmg_instance])
		npt.assert_almost_equal(calc.calcDamage(100,100,res,itemize=True),[1000,1500,1000])

	def test5(self):
		"""
		dmg - buff1 - dmg - buff2 - dmg - end all buffs - dmg
		"""
		stats = make_stats(1000, 0, 0, 0.50, 2.00, 0)
		buff1 = ConditionalBuff([[Stats.ATK_PERCENT,50]])
		buff2 = ConditionalBuff([[Stats.DAMAGE_BONUS,0.20]],element=Element.PYRO)
		dmg_instance = RegularDamage(Element.PYRO,DamageSource.NORMAL_ATTACK,1.00)
		res = make_resistances(0,0)

		calc = Calculator(stats,[])
		calc.addEvents([
			dmg_instance, buff1, 
			dmg_instance, buff2,
			dmg_instance, EndBuff(buff1), EndBuff(buff2),
			dmg_instance])
		npt.assert_almost_equal(calc.calcDamage(100,100,res,itemize=True),[1000,1500,1800,1000])

	def test5(self):
		"""
		dmg - buff1 - dmg - conversion - dmg - end buff1 - dmg
		"""
		stats = make_stats(1000, 1000, 0, 0.50, 2.00, 0)
		buff1 = ConditionalBuff([[Stats.ATK_PERCENT,50]])
		buff2 = StatConversion(Stats.DEF,0.75,Stats.ATK_FLAT)
		dmg_instance = RegularDamage(Element.PYRO,DamageSource.NORMAL_ATTACK,1.00)
		res = make_resistances(0,0)

		calc = Calculator(stats,[])
		calc.addEvents([
			dmg_instance, buff1, 
			dmg_instance, buff2,
			dmg_instance, EndBuff(buff1),
			dmg_instance])
		npt.assert_almost_equal(calc.calcDamage(100,100,res,itemize=True),[1000,1500,2250,1750])
	



if __name__ == '__main__':
	unittest.main()