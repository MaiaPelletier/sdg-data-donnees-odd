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


def methodology_1(data, direction, t, t_0, x=0.01, y=0.0, z=-0.01):
    print("Running methodology 1")


    current_value = data.Value[data.Year == t].values[0]
    print('current value is ' + str(current_value))
    base_value = data.Value[data.Year == t_0].values[0]
    print('base value is ' + str(base_value))

    cagr_o = ( (current_value / base_value) ** (1 / (t - t_0)) ) - 1
    print('observed growth is ' + str(cagr_o))

    if direction=="negative":
        cagr_o = -1*cagr_o

    if cagr_o > x:
        print(str(cagr_o) + ' growth is greater than ' + str(x))
        return "Significant progress"
    elif y < cagr_o <= x:
        print(str(cagr_o) + ' growth is greater than ' + str(y))
        return "Moderate progress"
    elif z <= cagr_o <= y:
        print(str(cagr_o) + ' growth is greater than ' + str(z))
        return "Moderate deterioration"
    elif cagr_o < z:
        print(str(cagr_o) + ' growth is less than ' + str(z))
        return "Deterioration"
    else:
        return "Error"


def methodology_2(data, direction, target, t_tao, t_0, t, x=0.95, y=0.6, z=0.0):
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

    if ratio >= x:
        print(str(ratio) + ' growth ratio is greater than ' + str(x))
        return "Significant progress"
    elif y <= ratio < x:
        print(str(cagr_o) + ' growth ratio is greater than ' + str(y))
        return "Moderate progress"
    elif z <= ratio < y:
        print(str(ratio) + ' growth ratio is greater than ' + str(z))
        return "Insufficient progress"
    elif ratio < z:
        print(str(ratio) + ' growth ratio is less than ' + str(z))
        return "Deterioration"
    else:
        return "Error"



def measure_indicator_progress(indicator):

    data = read_indicator_data(indicator)
    config = read_indicator_config(indicator)

    defaults = {'base_year': 2015, 'target_year': 2030, 'direction': 'negative'}  # set defaults
    config = {key: value for key, value in config.items() if config[key]}         # remove empty/non-configured keys

    # Loop over the defaults & check if they should be changed based on configs
    for key in defaults.keys():
        if key not in config.keys():
            config[key] = defaults[key]

    # set values for base year, target year, and desired direction of progress
    base_year = config['base_year']
    target_year = config['target_year']
    direction = config['direction']

    # get target from configs, if it exists; or set as blank if it doesn't exist
    if 'target' in config.keys():
        target = float(config['target'])
    elif 'graph_target_lines' in config.keys():
        graph_target = config['graph_target_lines'][0]
        target = float(graph_target['value'])
    else:
        target = ''

    # if target is 0, set to 0.001
    if target == 0:
        target = 0.001
    print("target is " + str(target))

    # TODO: I do *not* like this for the progress thresholds - its ugly and not intuitive
    # if ('progress_thresholds' in config.keys()) and (len(config['progress_thresholds']) > 0):
    #     progress_thresholds = {k: v for list_item in config['progress_thresholds'] for (k, v) in list_item.items()}
    # else:
    #     progress_thresholds = {'high': 0.95, 'med': 0.6, 'low': 0.0}
    # print(progress_thresholds)

    # get years from data
    years = data["Year"]

    # set current year to be MAX(Year)
    current_year = years.max()
    print("current year is " + str(current_year))

    # check if assigned base year is in data
    # if not, assign min(Year) to be base year

    # TODO: why is this throwing a warning all of a sudden?
    if base_year not in years.values:
        base_year = years.min()
    print('base year is ' + str(base_year))

    # Check if there is enough data to calculate progress
    if current_year - base_year <= 2:
        return 'Insufficient data to calculate progress'

    # TODO: i might need to add a config to specify which data point to calculate progress on
    #   right now we're just assuming the total line but some of the cif indicators don't have totals

    cols = data.columns.values
    if len(cols) > 2:
        cols = cols[1:-1]
        data = data[data[cols].isna().all('columns')]
        data = data.iloc[:, [0, -1]]

    print(data)

    # TODO: i wouldn't mind getting rid of these floats in the function call
    if target == '':
        # , x=float(progress_thresholds['high']), y=float(progress_thresholds['med']), z=float(progress_thresholds['low'])
        output = methodology_1(data=data, direction=direction, t=float(current_year), t_0=float(base_year))
        print(output)
    elif isinstance(target, float):
        output = methodology_2(data=data, direction=direction, target=float(target), t_tao=float(target_year), t_0=float(base_year), t=float(current_year))
        print(output)
    else:
        print("Error")


# TODO: Grab first year if year is in fiscal format (e.g. 3.5.2)

measure_indicator_progress('3-2-1')




