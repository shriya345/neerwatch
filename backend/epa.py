import math
SOURCE='https://nationallakesassessment.epa.gov/webreport/#trophic-state'
CATEGORIES=[{'name':'Oligotrophic','range':'≤2 µg/L','color':'#34835b','rank':0},{'name':'Mesotrophic','range':'>2–7 µg/L','color':'#9dbd73','rank':1},{'name':'Eutrophic','range':'>7–30 µg/L','color':'#dbac55','rank':2},{'name':'Hypereutrophic','range':'>30 µg/L','color':'#bd7771','rank':3}]
def classify(value):
 if value is None or not math.isfinite(value) or value<0:return None
 return {**CATEGORIES[0 if value<=2 else 1 if value<=7 else 2 if value<=30 else 3],'source_url':SOURCE,'screening':True,'label':'Satellite-derived screening classification'}
