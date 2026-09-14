"""Overlap-ratio splice for the 2018->2019 emissions methodology break.

Rebases the pre-2019 WRI/SIT series in raw/us_emissions_2000_2018.csv onto the
EPA Inventory-by-State basis used for 2019-2022, then repairs the
'United States' row as column sums (the EPA workbook's 'National' geo has
no sector detail, so the append left 2019+ national sectors at 0).

Usage:
    python scripts/splice_emissions_2018_2019.py <workbook.xlsx> <raw_csv> <factors_csv>

Workbook: EPA AllStateGHGData90-22 (AllStateGHGData90-22_v082924.xlsx),
sheet 'Data by Economic Sectors', see data/DATA_SOURCES.md for the URL.

Method (standard overlap-ratio splicing): for each state x column with a
usable 2018 overlap, r = EPA_basis(2018) / WRI(2018); every pre-2019 value
is multiplied by r (rounded to 7dp). Usable = both sides nonzero with the
same sign. Anything else is left untouched and flagged in the factors file
(and DATA_SOURCES.md) - never fabricated. Post-2019 rows are never touched,
except the 'United States' row, which is recomputed as column-wise sums of
the states for every year (it already was exactly that in the WRI era).
"""
import sys

import numpy as np
import pandas as pd

FOSS = 'Carbon Dioxide from Fossil Fuel Combustion'
FUG = ['Coal Mining', 'Natural Gas Systems', 'Petroleum Systems',
       'Abandoned Oil and Gas Wells', 'Abandoned Underground Coal Mines']
WASTE_IND = ['Landfills - Industrial', 'Wastewater Treatment']
BASE_GASES = ['Carbon Dioxide', 'Methane', 'Nitrous Oxide']

SPLICED = ['total_emissions_excluding_lucf', 'total_emissions_including_lucf',
           'total_co2', 'total_ch4', 'total_n2o', 'total_f_gas',
           'emission_by_energy', 'emission_by_industrial',
           'emission_by_agriculture', 'emission_by_waste',
           'emission_by_forestry', 'emission_sub_electric',
           'emission_sub_commercial', 'emission_sub_residential',
           'emission_sub_industrial', 'emission_sub_transportation',
           'emission_sub_fugitive']
# untouched by design: emission_by_bunker_fuel (no EPA mapping),
# state_gdp / population / total_energy_use (not in the EPA state file)

STATE_TO_GEO = {'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ',
                'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO',
                'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL',
                'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
                'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
                'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
                'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA',
                'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
                'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE',
                'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
                'New Mexico': 'NM', 'New York': 'NY',
                'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
                'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
                'Rhode Island': 'RI', 'South Carolina': 'SC',
                'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
                'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
                'Washington': 'WA', 'West Virginia': 'WV',
                'Wisconsin': 'WI', 'Wyoming': 'WY',
                'District Of Columbia': 'DC'}


def epa_basis(eco, geo, year):
    """Recompute one state-year on the EPA basis (same mapping as the
    2019-2022 append; see DATA_SOURCES.md). Units: Tg (= MMT)."""
    Y = 'Y%d' % year
    d = eco[eco['geo_ref'] == geo]
    dnl = d[d['econ_sector'] != 'LULUCF Sector Net Total']
    o = {}
    o['total_co2'] = dnl[dnl['ghg'] == 'Carbon Dioxide'][Y].sum()
    o['total_ch4'] = dnl[dnl['ghg'] == 'Methane'][Y].sum()
    o['total_n2o'] = dnl[dnl['ghg'] == 'Nitrous Oxide'][Y].sum()
    o['total_f_gas'] = dnl[~dnl['ghg'].isin(BASE_GASES)][Y].sum()
    o['total_emissions_excluding_lucf'] = (o['total_co2'] + o['total_ch4']
                                           + o['total_n2o']
                                           + o['total_f_gas'])
    o['emission_by_forestry'] = d[d['econ_sector']
                                  == 'LULUCF Sector Net Total'][Y].sum()
    o['total_emissions_including_lucf'] = (
        o['total_emissions_excluding_lucf'] + o['emission_by_forestry'])
    o['emission_by_energy'] = o['total_co2']
    di = d[d['econ_sector'] == 'Industry']
    ind_foss = di[di['econ_subsector'] == FOSS][Y].sum()
    ind_mob = di[di['econ_subsector'] == 'Mobile Combustion'][Y].sum()
    ind_neu = di[di['econ_subsector'] == 'Non-Energy Use of Fuels'][Y].sum()
    fug = di[di['econ_subsector'].isin(FUG)][Y].sum()
    waste_ind = di[di['econ_subsector'].isin(WASTE_IND)][Y].sum()
    ag_foss = d[(d['econ_sector'] == 'Agriculture')
                & (d['econ_subsector'] == FOSS)][Y].sum()
    elec = d[(d['econ_sector'] == 'Electric Power Industry')
             & (d['econ_subsector'] == FOSS)][Y].sum()
    res = d[(d['econ_sector'] == 'Residential')
            & (d['econ_subsector'] == FOSS)][Y].sum()
    com = d[(d['econ_sector'] == 'Commercial')
            & (d['econ_subsector'] == FOSS)][Y].sum()
    o['emission_sub_electric'] = elec
    o['emission_sub_residential'] = res
    o['emission_sub_commercial'] = com
    o['emission_sub_industrial'] = ind_foss + ind_mob + ind_neu + ag_foss
    tra = d[d['econ_sector'] == 'Transportation']
    o['emission_sub_transportation'] = tra[tra['econ_subsector'].isin(
        [FOSS, 'Mobile Combustion', 'Non-Energy Use of Fuels'])][Y].sum()
    o['emission_sub_fugitive'] = fug
    o['emission_by_waste'] = (
        d[(d['econ_sector'] == 'Commercial')
          & (d['econ_subsector'] == 'Landfills - Municipal')][Y].sum()
        + waste_ind
        + d[(d['econ_sector'] == 'Commercial')
            & (d['econ_subsector'] == 'Wastewater Treatment')][Y].sum()
        + d[(d['econ_sector'] == 'Commercial')
            & (d['econ_subsector'] == 'Composting')][Y].sum()
        + d[(d['econ_sector'] == 'Commercial')
            & (d['econ_subsector']
               == 'Anaerobic Digestion at Biogas Facilities')][Y].sum()
        + d[(d['econ_sector'] == 'Electric Power Industry')
            & (d['econ_subsector'] == 'Incineration of Waste')][Y].sum())
    ag_total = d[d['econ_sector'] == 'Agriculture'][Y].sum()
    o['emission_by_agriculture'] = ag_total - ag_foss
    o['emission_by_industrial'] = (di[Y].sum() - ind_foss - ind_mob
                                   - ind_neu - fug - waste_ind - ag_foss)
    return o


def main():
    workbook_path, raw_path, factors_path = sys.argv[1:4]
    eco = pd.read_excel(workbook_path, sheet_name='Data by Economic Sectors')
    raw = pd.read_csv(raw_path)

    # 1. The mapping must reproduce every appended EPA row before we trust
    #    the EPA-basis 2018 it produces for the overlap.
    max_err = 0.0
    for state, geo in STATE_TO_GEO.items():
        for year in (2019, 2020, 2021, 2022):
            mapped = epa_basis(eco, geo, year)
            row = raw[(raw.State == state) & (raw.Year == year)]
            assert len(row) == 1, 'missing %s %d' % (state, year)
            row = row.iloc[0]
            for col in SPLICED:
                max_err = max(max_err, abs(mapped[col] - row[col]))
    print('mapping check: max abs err vs 2019-2022 rows = %.6f' % max_err)
    assert max_err < 1e-3, 'mapping does not reproduce appended rows'

    # 2. Overlap ratios from the single shared year, 2018.
    factors, statuses = {}, {}
    for state, geo in STATE_TO_GEO.items():
        mapped = epa_basis(eco, geo, 2018)
        wri = raw[(raw.State == state) & (raw.Year == 2018)].iloc[0]
        for col in SPLICED:
            wv, ev = wri[col], mapped[col]
            if (pd.notna(wv) and pd.notna(ev) and abs(wv) > 1e-9
                    and abs(ev) > 1e-9 and np.sign(wv) == np.sign(ev)):
                factors[(state, col)] = ev / wv
                statuses[(state, col)] = 'spliced'
            else:
                factors[(state, col)] = 1.0
                statuses[(state, col)] = (
                    'NO OVERLAP (WRI2018=%s, EPA2018=%.4f); left untouched'
                    % (wv, ev))

    # 3. Apply to pre-2019 rows only.
    out = raw.copy()
    for (state, col), ratio in factors.items():
        if statuses[(state, col)] == 'spliced':
            mask = (out.State == state) & (out.Year < 2019)
            out.loc[mask, col] = (out.loc[mask, col] * ratio).round(7)

    # 4. National row = column sums of the states, every year. (The EPA
    #    workbook's 'National' geo carries no sector detail, so the append
    #    left 2019+ national sectors at 0; the frontend reads united_states.)
    states = [s for s in out.State.unique() if s != 'United States']
    sum_cols = [c for c in out.columns
                if c not in ('State', 'Year', 'state_gdp', 'population',
                             'total_energy_use', 'emission_by_bunker_fuel')]
    for year in sorted(out.Year.unique()):
        totals = out[(out.State.isin(states))
                     & (out.Year == year)][sum_cols].sum()
        idx = out[(out.State == 'United States')
                  & (out.Year == year)].index
        assert len(idx) == 1
        for col in sum_cols:
            out.loc[idx, col] = round(float(totals[col]), 7)

    # plain UTF-8 + CRLF, matching the checked-in raw file (no BOM)
    out.to_csv(raw_path, index=False, lineterminator='\r\n',
               encoding='utf-8')

    rows = [{'state': state, 'column': col,
             'EPA2018_WRI2018_ratio': round(factors[(state, col)], 6),
             'status': statuses[(state, col)]}
            for (state, col) in factors]
    rows += [{'state': 'United States', 'column': col,
              'EPA2018_WRI2018_ratio': 'n/a (sum of states)',
              'status': 'national = column-wise sum of states'}
             for col in SPLICED]
    pd.DataFrame(rows).to_csv(factors_path, index=False)
    print('spliced %d state-series; %d left untouched (see %s)'
          % (sum(1 for s in statuses.values() if s == 'spliced'),
             sum(1 for s in statuses.values() if s != 'spliced'),
             factors_path))


if __name__ == '__main__':
    main()
