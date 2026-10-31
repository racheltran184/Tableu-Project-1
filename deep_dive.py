"""Victoria road crashes, 2012-2024: where deaths and serious injuries concentrate.

Reads the three crash tables from the repository's Data folder and writes every
figure used on the case-study page to one JSON file.

Usage:  python3 analysis/deep_dive.py Data site_data.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DATA, OUT = Path(sys.argv[1]), Path(sys.argv[2])

# @load
crash = pd.read_csv(DATA / 'crash1.csv.gz', low_memory=False)
person = pd.read_csv(DATA / 'person1.csv.gz', low_memory=False)
vehicle = pd.read_csv(DATA / 'vehicle1.csv.gz', low_memory=False)

crash['region'] = crash['STAT_DIV_NAME']                      # Metro or Country
crash['high_speed'] = crash['SPEED_ZONE'].isin(['100 km/h', '110 km/h'])
crash['hour'] = pd.to_numeric(crash['ACCIDENT_HOUR'], errors='coerce')
crash['year'] = crash['ACCIDENT_YEAR']

# @mechanism
# One crash type per crash, from the Definitions for Classifying Accidents (DCA)
dca = crash['DCA_CODE_DESCRIPTION'].str.upper()
crash['lane_departure'] = (crash['RUN_OFFROAD'].eq('Yes')
                           | dca.str.contains('OFF CARRIAGEWAY|OFF RIGHT BEND|OFF LEFT BEND|OUT OF CONTROL|OFF END OF ROAD'))
crash['mechanism'] = np.select(
    [dca.str.contains(r'\bPED') | crash['ACCIDENT_TYPE'].eq('Struck Pedestrian'),
     dca.str.contains('HEAD ON'),
     crash['lane_departure'],
     dca.str.contains('CROSS TRAFFIC|RIGHT THROUGH|RIGHT NEAR|LEFT NEAR|RIGHT FAR|LEFT FAR|INTERSECTION'),
     dca.str.contains('REAR END')],
    ['Pedestrian struck', 'Head-on', 'Run-off-road / loss of control', 'Intersection', 'Rear-end'],
    default='Other')
crash.loc[crash['mechanism'].isin(['Pedestrian struck', 'Head-on']), 'lane_departure'] = \
    crash['mechanism'].eq('Head-on')          # head-ons count as lane departure; pedestrian crashes don't


def harm(df, by):
    g = df.groupby(by).agg(crashes=('ACCIDENT_NO', 'size'), deaths=('FATALITY', 'sum'),
                           serious=('SERIOUSINJURY', 'sum'))
    g['deaths_per_100'] = 100 * g['deaths'] / g['crashes']
    g['share_crashes'] = 100 * g['crashes'] / len(df)
    g['share_deaths'] = 100 * g['deaths'] / df['FATALITY'].sum()
    return g


out = {}
T = {'crashes': len(crash), 'deaths': int(crash.FATALITY.sum()), 'serious': int(crash.SERIOUSINJURY.sum()),
     'first': str(crash.ACCIDENT_DATE.min()), 'years': [int(crash.year.min()), int(crash.year.max())]}
T['deaths_per_100'] = 100 * T['deaths'] / T['crashes']
out['totals'] = T

# @glide
# Deaths against a straight line to half the 2018-20 average by 2030
yr = harm(crash, 'year')
base = yr.loc[2018:2020, 'deaths'].mean()


def glide(y):
    return base - (base / 2) * (y - 2020) / 10


out['glide'] = {'base': base, 'target2030': base / 2, 'rows': [
    {'y': int(y), 'deaths': int(r.deaths), 'serious': int(r.serious), 'crashes': int(r.crashes),
     'path': glide(y) if y >= 2020 else None} for y, r in yr.iterrows()]}
out['glide']['next'] = [{'y': y, 'path': glide(y)} for y in range(2025, 2031)]

# @mechanism_harm
m = harm(crash, 'mechanism').sort_values('deaths', ascending=False)
out['mech'] = [{'k': k, **{c: float(v) for c, v in r.items()}} for k, r in m.iterrows()]
for reg in ['Metro', 'Country']:
    s = crash[crash.region == reg].groupby('mechanism').FATALITY.sum()
    out['mech_' + reg.lower()] = {k: float(100 * v / s.sum()) for k, v in s.items()}

# @time
h = harm(crash, 'hour')
out['hours'] = [{'h': int(k), 'crashes': int(r.crashes), 'deaths': int(r.deaths),
                 'dp100': float(r.deaths_per_100)} for k, r in h.iterrows()]
night = crash['hour'].ge(22) | crash['hour'].le(5)
out['night'] = {'crashes': int(night.sum()), 'deaths': int(crash.loc[night, 'FATALITY'].sum())}
dow = harm(crash, 'DAY_OF_WEEK')
out['dow'] = [{'d': k, 'crashes': int(r.crashes), 'deaths': int(r.deaths), 'dp100': float(r.deaths_per_100)}
              for k, r in dow.iterrows()]
fri_pm = crash['DAY_OF_WEEK'].eq('Friday') & crash['hour'].between(15, 18)
out['fri_pm'] = {'crashes': int(fri_pm.sum()), 'deaths': int(crash.loc[fri_pm, 'FATALITY'].sum()),
                 'mix': crash.loc[fri_pm, 'mechanism'].value_counts(normalize=True).mul(100).to_dict()}

# @funnel
# Narrow all deaths down to one road type and one crash type
steps = [('All crashes', crash.index == crash.index),
         ('Regional Victoria', crash.region.eq('Country')),
         ('… on 100–110 km/h roads', crash.region.eq('Country') & crash.high_speed),
         ('… where the vehicle left its lane', crash.region.eq('Country') & crash.high_speed & crash.lane_departure),
         ('… on an undivided road', crash.region.eq('Country') & crash.high_speed & crash.lane_departure
          & crash.DIVIDED.eq('Undivided'))]
out['funnel'] = [{'k': k, 'crashes': int(f.sum()), 'deaths': int(crash.loc[f, 'FATALITY'].sum()),
                  'serious': int(crash.loc[f, 'SERIOUSINJURY'].sum())} for k, f in steps]
z = harm(crash, ['region', 'high_speed'])
out['segments'] = [{'region': a, 'high': bool(b), **{c: float(v) for c, v in r.items()}} for (a, b), r in z.iterrows()]
sz = harm(crash, 'SPEED_ZONE')
out['speed'] = {k: {c: float(v) for c, v in sz.loc[k].items()}
                for k in ['40 km/h', '50 km/h', '60 km/h', '70 km/h', '80 km/h', '100 km/h', '110 km/h']}

# @corridors
crash['road'] = (crash.ROAD_NAME.fillna('').str.title() + ' ' + crash.ROAD_TYPE.fillna('').str.title()).str.strip()
regional = crash[crash.region.eq('Country') & crash.road.ne('')]
rd = harm(regional, 'road')
rd['lgas'] = regional.groupby('road').LGA_NAME.nunique()
rd['lane_share'] = 100 * regional[regional.lane_departure].groupby('road').FATALITY.sum() / rd.deaths
top = rd.sort_values('deaths', ascending=False).head(12)
out['roads'] = [{'k': k, 'crashes': int(r.crashes), 'deaths': int(r.deaths), 'serious': int(r.serious),
                 'dp100': float(r.deaths_per_100), 'lgas': int(r.lgas), 'lane': float(r.lane_share)}
                for k, r in top.iterrows()]
out['roads_share'] = {'deaths': float(100 * top.deaths.sum() / regional.FATALITY.sum()),
                      'crashes': float(100 * top.crashes.sum() / len(regional))}
lga = harm(crash[crash.region.eq('Country')], 'LGA_NAME')
lga = lga[lga.crashes >= 500].sort_values('deaths_per_100', ascending=False).head(8)
out['lgas'] = [{'k': k.title(), 'crashes': int(r.crashes), 'deaths': int(r.deaths), 'dp100': float(r.deaths_per_100)}
               for k, r in lga.iterrows()]
metro = harm(crash[crash.region.eq('Metro') & crash.road.ne('')], 'road').sort_values('deaths', ascending=False)
out['metro_roads'] = [{'k': k, 'crashes': int(r.crashes), 'deaths': int(r.deaths), 'serious': int(r.serious)}
                      for k, r in metro.head(6).iterrows()]

# @rise
# Average deaths a year: 2018-20 against 2023-24
crash['place'] = crash.region + np.where(crash.high_speed, ' · 100–110 km/h', ' · up to 90 km/h')
person = person.merge(crash[['ACCIDENT_NO', 'region', 'high_speed', 'year', 'mechanism', 'hour']], on='ACCIDENT_NO')
person['died'] = person.INJ_LEVEL_DESC.eq('Fatality')
person['ksi'] = person.INJ_LEVEL_DESC.isin(['Fatality', 'Serious injury'])


def change(df, col, val):
    before = df[df.year.between(2018, 2020)].groupby(col)[val].sum() / 3
    after = df[df.year.between(2023, 2024)].groupby(col)[val].sum() / 2
    t = pd.DataFrame({'before': before, 'after': after}).fillna(0)
    t['delta'] = t.after - t.before
    return t.sort_values('delta', ascending=False)


rise = {'place': change(crash, 'place', 'FATALITY'), 'mech': change(crash, 'mechanism', 'FATALITY'),
        'user': change(person[person.ROAD_USER_TYPE_DESC.isin(
            ['Drivers', 'Passengers', 'Motorcyclists', 'Pedestrians', 'Bicyclists'])], 'ROAD_USER_TYPE_DESC', 'died')}
out['rise'] = {g: [{'k': k, 'before': float(r.before), 'after': float(r.after), 'delta': float(r.delta)}
                   for k, r in t.iterrows()] for g, t in rise.items()}
mm = crash[crash.region.eq('Metro') & ~crash.high_speed]
out['rise_metro_mech'] = [{'k': k, **{c: float(v) for c, v in r.items()}} for k, r in change(mm, 'mechanism', 'FATALITY').iterrows()]
out['metro_low_share'] = float(100 * mm.FATALITY.sum() / crash[crash.region.eq('Metro')].FATALITY.sum())

# @people
occ = person[person.ROAD_USER_TYPE_DESC.isin(['Drivers', 'Passengers'])]
belt = occ[occ.HELMET_BELT_WORN.isin(['Seatbelt Worn', 'Seatbelt Not Worn'])].groupby('HELMET_BELT_WORN').died.agg(['size', 'sum'])
users = person.groupby('ROAD_USER_TYPE_DESC').died.agg(['size', 'sum'])
ped = person[person.ROAD_USER_TYPE_DESC.eq('Pedestrians')]
ped70 = ped[ped.AGE_GROUP.eq('70+')]
age70 = person[person.AGE_GROUP.eq('70+')]


def row(k, n, d, group):
    return {'k': k, 'n': int(n), 'd': int(d), 'v': float(100 * d / n), 'g': group}


out['people'] = [
    row('Pedestrians aged 70+', len(ped70), ped70.died.sum(), 'Who'),
    row('Seatbelt not worn', *belt.loc['Seatbelt Not Worn'], 'Who'),
    row('All pedestrians', *users.loc['Pedestrians'], 'Who'),
    row('Motorcyclists', *users.loc['Motorcyclists'], 'Who'),
    row('Anyone aged 70+', len(age70), age70.died.sum(), 'Who'),
    row('Drivers', *users.loc['Drivers'], 'Who'),
    row('Seatbelt worn', *belt.loc['Seatbelt Worn'], 'Who')]
out['people_all'] = {'n': len(person), 'd': int(person.died.sum())}
out['occupant_deaths'] = {'all': int(occ.died.sum()),
                          'unbelted': int(occ[occ.died & occ.HELMET_BELT_WORN.eq('Seatbelt Not Worn')].shape[0]),
                          'unknown': int(occ[occ.died & occ.HELMET_BELT_WORN.eq('Unknown')].shape[0])}
unbelted = occ[occ.died & occ.HELMET_BELT_WORN.eq('Seatbelt Not Worn')]
night_occ = occ.hour.ge(22) | occ.hour.le(5)
out['unbelted'] = {'regional': int(unbelted.region.eq('Country').sum()), 'high_speed': int(unbelted.high_speed.sum()),
                   'male': int(unbelted.SEX.eq('Male').sum()),
                   'lane': int(unbelted.mechanism.isin(['Run-off-road / loss of control', 'Head-on']).sum()),
                   'night_share_of_deaths': float(100 * (occ[occ.died & night_occ].HELMET_BELT_WORN.eq('Seatbelt Not Worn')).mean()),
                   'day_share_of_deaths': float(100 * (occ[occ.died & ~night_occ].HELMET_BELT_WORN.eq('Seatbelt Not Worn')).mean())}
out['sex'] = person[person.died].SEX.value_counts().to_dict()
moto = person[person.ROAD_USER_TYPE_DESC.eq('Motorcyclists') & person.died]
out['moto'] = {'region': moto.region.value_counts().to_dict(), 'mech': moto.mechanism.value_counts().to_dict()}
out['ped'] = {'region': ped[ped.died].region.value_counts().to_dict(), 'd70': int(ped70.died.sum()),
              'd': int(ped.died.sum())}

# @vehicle_age
# Driver deaths per 1,000 drivers in a crash, by the age of their car
LIGHT = ['Car', 'Station Wagon', 'Utility', 'Panel Van', 'Taxi',
         'Light Commercial Vehicle (Rigid) <= 4.5 Tonnes GVM']
v = vehicle.merge(crash[['ACCIDENT_NO', 'year', 'region', 'high_speed']], on='ACCIDENT_NO')
made = pd.to_numeric(v.VEHICLE_YEAR_MANUF, errors='coerce').where(lambda s: s.between(1950, 2025))
v['age'] = v.year - made
drivers = person[person.ROAD_USER_TYPE_DESC.eq('Drivers')][['ACCIDENT_NO', 'VEHICLE_ID', 'died', 'HELMET_BELT_WORN', 'AGE_GROUP']]
cars = v[v.VEHICLE_TYPE_DESC.isin(LIGHT) & v.age.between(-1, 60)].merge(drivers, on=['ACCIDENT_NO', 'VEHICLE_ID'])
cars['band'] = pd.cut(cars.age, [-2, 4, 9, 14, 19, 60], labels=['0–4 years', '5–9 years', '10–14 years', '15–19 years', '20+ years'])
cars['segment'] = cars.region + np.where(cars.high_speed, ' · 100–110 km/h', ' · up to 90 km/h')
va = cars.groupby('band', observed=True).died.agg(['size', 'sum'])
seg = cars.pivot_table(index='segment', columns='band', values='died', aggfunc='mean', observed=False) * 1000
belted = cars[cars.HELMET_BELT_WORN.eq('Seatbelt Worn')]
segb = belted.pivot_table(index='segment', columns='band', values='died', aggfunc='mean', observed=False) * 1000
out['vehage'] = [{'k': str(k), 'n': int(r['size']), 'd': int(r['sum']), 'v': float(1000 * r['sum'] / r['size'])}
                 for k, r in va.iterrows()]
out['vehage_seg'] = {s: [float(x) for x in seg.loc[s]] for s in seg.index}
out['vehage_seg_belted'] = {s: [float(x) for x in segb.loc[s]] for s in segb.index}
by_driver_age = cars.pivot_table(index='AGE_GROUP', columns='band', values='died', aggfunc='mean', observed=False) * 1000
out['vehage_driver_age'] = {a: [float(x) for x in by_driver_age.loc[a]] for a in ['18-21', '30-39', '50-59', '70+']}
out['vehage_old'] = {'share_drivers': float(100 * (cars.age >= 15).mean()),
                     'share_deaths': float(100 * cars[cars.died].age.ge(15).mean()),
                     'by_region': cars.groupby('region').age.apply(lambda s: float(100 * (s >= 15).mean())).to_dict(),
                     'n': len(cars), 'd': int(cars.died.sum())}

OUT.write_text(json.dumps(out, indent=1, default=float), encoding='utf-8')
print('wrote', OUT)
