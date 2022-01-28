# Start bones and flow of code

import pandas as pd
import yaml

# Read in indicator data from repo
# Might be able to use sdg-build helper functions here
def read_indicator_data(indicator):

    data = pd.read_csv("data/indicator_" + indicator + ".csv")
    print('data is read')

    return data


# Read indicator configuration file and get the configs needed for measurement
def read_indicator_config(indicator):

    ind_config_path = 'indicator-config/' + indicator + '.yml'

    with open(ind_config_path, 'r') as stream:
        config = yaml.safe_load(stream)
        print('config is read')

    defaults = {'base_year': 2015, 'target_year': 2030, 'direction': 'negative'}  # set defaults
    config = {key: value for key, value in config.items() if config[key]}  # remove empty/non-configured keys

    # Loop over the defaults & check if they should be changed based on configs
    # TODO: I feel like this should use the update() method but i can't figure it out
    for key in defaults.keys():
        if key not in config.keys():
            config[key] = defaults[key]

    # get target from configs, if it exists; or set as blank if it doesn't exist
    if 'target' in config.keys():
        config['target'] = float(config['target'])
    else:
        config['target'] = ''

    # if target is 0, set to 0.001
    if config['target'] == 0:
        config['target'] = 0.001
    print("target is " + str(config['target']))

    return config


def progress_threshold_configs(config, method):

    progress_thresholds = {}

    if 'progress_thresholds' in config.keys():
        if bool(config['progress_thresholds']):
            print('updating progress thresholds to configs')
            progress_thresholds = config['progress_thresholds']
            progress_thresholds = {key: value for x in progress_thresholds for key, value in x.items()}

    elif method == 1:
        print('updating progress thresholds to defaults for metho 1')
        progress_thresholds = {'high': 0.01, 'med': 0, 'low': -0.01}

    elif method == 2:
        print('updating progress thresholds to defaults for metho 2')
        progress_thresholds = {'high': 0.95, 'med': 0.6, 'low': 0}

    else:
        print("error with progress thresholds")

    print(progress_thresholds)
    config.update(progress_thresholds)

    return config

def output_configs(indicator, output):

    ind_config_path = 'indicator-config/' + indicator + '.yml'

    with open(ind_config_path, 'r') as stream:
        raw_config = yaml.safe_load(stream)

    raw_config.update(output)

    with open(ind_config_path, 'w') as file:
        raw_config = yaml.dump(raw_config, file)

    return raw_config

def methodology_1(data, config):
    print("Running methodology 1")

    direction = str(config['direction'])
    t         = float(config['current_year'])
    t_0       = float(config['base_year'])
    x         = float(config['high'])
    y         = float(config['med'])
    z         = float(config['low'])

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


def methodology_2(data, config):
    print("Running methodology 2")

    direction = str(config['direction'])
    t         = float(config['current_year'])
    t_0       = float(config['base_year'])
    target    = float(config['target'])
    t_tao     = float(config['target_year'])
    x         = float(config['high'])
    y         = float(config['med'])
    z         = float(config['low'])


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

    data = read_indicator_data(indicator)      # read indicator data
    config = read_indicator_config(indicator)  # read configations
    print(config)

    years = data["Year"]              # get years from data
    base_year = config['base_year']   # set base year value
    current_year = float(years.max()) # set current year to be MAX(Year)
    print("current year is " + str(current_year))
    config.update({'current_year': current_year})

    # check if assigned base year is in data
    # if not, assign min(Year) to be base year
    # TODO: why is this throwing a warning all of a sudden?
    if base_year not in years.values:
        base_year = years.min()
    print('base year is ' + str(base_year))

    # Check if there is enough data to calculate progress
    if current_year - base_year <= 2:
        output = 'Insufficient data to calculate progress'

    # TODO: i might need to add a config to specify which data point to calculate progress on
    cols = data.columns.values
    if len(cols) > 2:
        cols = cols[1:-1]
        data = data[data[cols].isna().all('columns')]
        data = data.iloc[:, [0, -1]]

    print(data)

    # determine which methodology to run
    # TODO: output target as a config
    if config['target'] == '':
        config = progress_threshold_configs(config, method=1)
        output = methodology_1(data=data, config=config)
        print(output)

    elif isinstance(config['target'], float):
        config = progress_threshold_configs(config, method=2)
        output = methodology_2(data=data, config=config)
        print(output)

    else:
        output = 'Error'

    output = {'progress_status': output}




# TODO: Grab first year if year is in fiscal format (e.g. 3.5.2)
measure_indicator_progress('3-2-1')




