# constants.py
import swisseph as swe

PLANET_IDS = [
    swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER,
    swe.VENUS, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO
]

PLANET_SYMBOLS = {
    swe.SUN: '၁', swe.MOON: '၂', swe.MARS: '၃',
    swe.MERCURY: '၄', swe.JUPITER: '၅',
    swe.VENUS: '၆', swe.SATURN: '၀',
    swe.URANUS: 'U', swe.NEPTUNE: 'N',
    swe.PLUTO: 'P',
    swe.TRUE_NODE: '၈', swe.MEAN_NODE: '၈',
    'RAHU': '၈', 'KETU': '၉', 'LAGNA': 'လ'
}

ZODIAC_SIGNS_EN = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

MOVABLE_SIGNS = [1,4,7,10]
FIXED_SIGNS   = [2,5,8,11]
DUAL_SIGNS    = [3,6,9,12]

ODD_SIGNS  = [1,3,5,7,9,11]
EVEN_SIGNS = [2,4,6,8,10,12]
