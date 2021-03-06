from numpy.random import choice as weighed_choice
from random import choice, shuffle, randint, random

from equipment import *
from effects import *

# weapon generation

class Mod:
    def __init__(self):
        self.name = None
        self.tier = None

        self.mclass = None
        self.value = None


def make_mod(weapon, tier3_guarantee=False):
    # this first dict just maps out the values of our GDD mod matrix
    mod_dict = {
        "crit": {
            "tier 1": 0.05,
            "tier 2": 0.1,
            "tier 3": 0.2
        },
        "range": {
            "tier 1": 1,
            "tier 2": 2,
            "tier 3": 3
        },
        "burn": {
            "tier 1": 0.05,
            "tier 2": 0.1,
            "tier 3": 0.2
        },
        "poison": {
            "tier 1": 0.05,
            "tier 2": 0.1,
            "tier 3": 0.2
        },
        "bleed": {
            "tier 1": 0.05,
            "tier 2": 0.1,
            "tier 3": 0.2
        },
        "blind": {
            "tier 1": 0.02,
            "tier 2": 0.05,
            "tier 3": 0.1
        },
        "slow": {
            "tier 1": 0.02,
            "tier 2": 0.05,
            "tier 3": 0.1
        },
        "knock": {
            "tier 1": 0.02,
            "tier 2": 0.04,
            "tier 3": 0.08
        },
        "ap": {
            "tier 1": 1,
            "tier 2": 2,
            "tier 3": 3
        },
        "range": {
            "tier 1": 1,
            "tier 2": 2,
            "tier 3": 3
        }
    }

    # this just specifies the likelyhood of a certain mod. i.e. the AP mod once implemented, should be less 
    # likely to occur, since it is very powerful
    mod_type_likelyhood = {
        "crit": "regular",
        "range": "regular",
        "burn": "regular",
        "poison": "regular",
        "bleed": "regular",
        "blind": "regular",
        "slow": "regular",
        "knock": "half",
        "ap": "half",
        "range": "regular"
    }

    # all mods are defined by a class
    # any combat effects can then be instantiated when assigned
    # this is just how i did it; maybe not ideal
    burning_mod_class = gen_effect_mod(Burning, 3)
    poison_mod_class = gen_effect_mod(Poisoned, 3)
    bleed_mod_class = gen_effect_mod(Bleeding, 5)
    blind_mod_class = gen_effect_mod(Blinded, 2)
    slowed_mod_class = gen_effect_mod(Slowed, 2)
    knocked_mod_class = gen_effect_mod(Knocked, 2)

    # just mapping classes to effect names
    mod_bonus_dict = {
        "burn": burning_mod_class,
        "poison": poison_mod_class,
        "bleed": bleed_mod_class,
        "blind": blind_mod_class,
        "slow": slowed_mod_class,
        "knock": knocked_mod_class,
        "crit": None,  # these have no class, since they are just a value to be added
        "range": None,  # again; no class, just a value you add to a stat
        "ap": None
    }

    # here is where i select the mod
    # by first creating a probability distribution based on the "mod_type_likelyhood" dictionary
    mdkeys = mod_dict.keys()
    pdist1_ = [[1, 0.5][mod_type_likelyhood[k] != "regular"] for k in mdkeys]
    s = sum(pdist1_)
    pdist1 = [i / s for i in pdist1_]

    # here i select the tier of the mod, with a weighed distribution
    # it can be overriden to guarantee a tier 3 mod (useful in the case of creating a legendary weapon)
    mod_name = list(mdkeys)[weighed_choice(list(i for i in range(len(mdkeys))), p=pdist1)]
    if not tier3_guarantee:
        pdist2 = [0.6, 0.3, 0.1]
        mod_tier = ["tier 1", "tier 2", "tier 3"][weighed_choice(list((0, 1, 2)), p=pdist2)]
    else:
        mod_tier = "tier 3"
    mod_value = mod_dict[mod_name][mod_tier]

    # instantiate the mod, assign values
    mc = Mod()
    mc.name = mod_name
    mc.tier = mod_tier
    mc.value = mod_value
    mc.mclass = mod_bonus_dict[mod_name]

    # add to weapon
    weapon.mods.append(mc)


def create_weapon(rarity, quality, weapon):
    # from the GDD; a legendary has 4-5 mods, rare has 1-3, and common has none
    n_mods_dict = {
        "legendary": choice((4, 5)),
        "rare": choice((1, 2, 3)),
        "common": 0
    }
    n_mods = n_mods_dict[rarity]

    quality_multipliers = {
        "good": 1.5,
        "crappy": 0.5,
        "regular": 1
    }

    # make mods
    for m in range(n_mods):
        make_mod(weapon)

    # when its legendary, ensure that it gets at least two tier 3 mods.
    if rarity == "legendary":
        tier3_count = 0
        for m in weapon.mods:
            if m.tier == "tier 3":
                tier3_count += 1

        while tier3_count < 2:
            make_mod(weapon, tier3_guarantee=True)
            i = 0
            for m in weapon.mods:
                if m.tier != "tier 3":
                    kill_me = i
                    break
                i += 1
            weapon.mods.pop(kill_me)
            tier3_count += 1

    # assign weapon quality
    multiplier = quality_multipliers[quality]
    weapon.quality = quality
    weapon.quality_multiplier = multiplier

    weapon.rarity = rarity

    # finito!
    return weapon


# unit generation