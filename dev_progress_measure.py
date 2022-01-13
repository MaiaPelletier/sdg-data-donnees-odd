# Start bones and flow of code

import pandas as pd
import yaml

# Read in indicator data from repo
# Might be able to use sdg-build helper functions here
def read_indicator_data(indicator):

    data = pd.read_csv("data/indicator_" + indicator + ".csv")

    return(data)


# Read indicator configuration file here
def read_indicator_config(indicator):

    ind_config_path = 'indicator-config/' + indicator + '.yml'

    with open(ind_config_path, 'r') as stream:
        config = yaml.safe_load(stream)

    return(config)


def methodology_1():
    print("Running methodology 1")


def methodology_2(data, direction, target, t_tao, t_0, t, x=0.95, y=0.6, z=0):
    print("Running methodology 2")

    current_value = data.Value[data.Year == t].values[0]
    print('current value is ' + str(current_value))
    base_value = data.Value[data.Year == t_0].values[0]
    print('base value is ' + str(base_value))

    if (direction == "negative" and current_value <= target) or (direction == "positive" and current_value >= target):
        print("Target achieved")
        return "Target achieved"
    else:
        print("Target not yet achieved. Continue calculating progress...")

    cagr_o = ( (current_value / base_value) ** (1 / (t - t_0)) ) - 1
    print('observed growth is ' + str(cagr_o))
    cagr_r = ( (target / base_value) ** (1 / (t_tao - t_0)) ) - 1
    print('theoretical growth is ' + str(cagr_r))

    ratio = cagr_o / cagr_r
    print('growth ratio is ' + str(ratio))


def measure_indicator_progress(indicator, base_year=2015, target_year=2030, direction='negative'):

    data = read_indicator_data(indicator)
    config = read_indicator_config(indicator)

    ## get configs from indicator config file ##
    target = float(config['target'])
    if target == 0:
        target = 0.001
    print("target is " + str(target))

    # SIMPLIFY THIS WITH ADDING ALL THE PARAMS TO A LIST/DICT AND USE A FOR LOOP #
    # if base_year is set in config file, use that instead of default
    if str(config['base_year']) != '':
        base_year = str(config['base_year'])

    # if target_year is set in config file, use that instead of default
    if str(config['target_year']) != '':
        target_year = str(config['target_year'])
    print("target year is " + target_year)

    # if direction is set in config file, use that instead of default
    if str(config['direction']) != '':
        direction = str(config['direction'])
    print("desired direction of progress is " + direction)

    # Get years from data
    years = data["Year"]

    # Set current year to be MAX(Year)
    current_year = years.max()
    print("current year is " + str(current_year))

    # Check if assigned base year is in data
    # If not, assign min(Year) to be base year
    if base_year not in years.values:
        base_year = years.min()
    print('base year is ' + str(base_year))

    # Check if there is enough data to calculate progress
    if current_year - base_year <= 2:
        return 'Insufficient data to calculate progress'

    ### NEED TO REMOVE ALL LINES BUT TOTALS FROM DATA ###

    if target == '':
        methodology_1()
    elif isinstance(target, float):
        # I wouldn't mind getting rid of these floats in the function call
        methodology_2(data=data, direction=direction, target=float(target), t_tao=float(target_year), t_0=float(base_year), t=float(current_year))
    else:
        print("Error")



measure_indicator_progress('3-1-1')




