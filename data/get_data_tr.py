# import statements
import numpy as np
import pandas as pd
import datetime

def get_data_nba(date, attributes):
    '''
    Gets the attributes for each team on the supplied date, from TeamRankings.
    :param date: Target date. String.
    :param attributes: The factors to retrieve from TeamRankings. Must match the URL exactly. Passed as a dictionary. Dictionary.
    :return: Data frame of all speficied attributes for the given date, for all teams.
    '''

    # initiate data frame
    output = pd.DataFrame({'team': []})
    # index by team name
    output = output.set_index('team')

    # for each key in the factor dictionary, create a data frame
    for attribute in list(attributes.keys()):
        # if it's a proprietary ranking, the URL is a little different
        if 'by-other' in attribute:
            # create the URL to fetch
            url = 'https://www.teamrankings.com/nba/ranking/' + attribute + '?date=' + date
        else:
            url = 'https://www.teamrankings.com/nba/stat/' + attribute + '?date=' + date

        # read the data from the table on the supplied URL
        z = pd.read_html(url, flavor='html5lib')[0]

        # throw out the nonsense
        z = z.iloc[:, 0:3]

        # ranking, team name, attribute value
        z.columns = [attribute + '_rank', 'team', attribute]

        # set the index
        z = z.set_index('team')

        # merge the attribute data frames, one by one
        output = pd.merge(z, output, how='left', on=['team'])

    # fix format to be numeric
    for column in output.columns:
        if '--' in list(output[column].unique()):
            output[column] = output[column].replace(np.nan, '--')
            output[column] = [str(x).strip('%') for x in output[column]]
            output[column] = output[column].replace('--', np.nan)
            output[column] = pd.to_numeric(output[column])
        else:
            output[column] = [str(x).strip('%') for x in output[column]]
            output[column] = output[column].replace('nan', np.nan)
            output[column] = pd.to_numeric(output[column])

    # create rankings (the TeamRankings one are broken by special characters)
    for column in output.columns:
        if 'rank' in column:
            key = column.split('_rank')[0]
            if attributes[key] == 'desc':
                output[column] = output[key].rank(ascending=False)
            else:
                output[column] = output[key].rank(ascending=True)

    # output data frame
    return output

def get_historical_nba_data(dates, attributes):
    '''
    Grabs historical data for NBA teams from TR.
    :param dates: The dates for which you want to grab data. List.
    :param attributes: The attributes that you want to grab from TR. Dictionary.
    :return: Data frame of all speficied attributes for the given date range, for all teams.
    '''
    # Create a list to hold a data frame for each year
    df_list = []

    # I don't remember what this does - I know this is the number of weeks to grab after the start date
    for date in date_list:
        try:
            to_concat = get_data_nba(date, attributes)
            print("Got ", date)
        except:
            continue
            ("Broken: ", date)
        to_concat['Year'] = date[0:4]
        to_concat['Date'] = date

        df_list.append(to_concat)

    output = pd.concat(df_list)

    output['Week'] = output['Week'].astype('int32')
    output['Year'] = output['Year'].astype('int32')

    return (output)

### Example function calls
#test = get_data_nba('2023-11-01', {'true-shooting-percentage': 'desc'})

#start = datetime.datetime.strptime('2022-10-31', '%Y-%m-%d')
#end = datetime.datetime.strptime('2023-04-09', '%Y-%m-%d')
#date_list = [datetime.datetime.strftime(end - datetime.timedelta(days=x), '%Y-%m-%d') for x in range((end - start).days)]

#samp = get_historical_nba_data(date_list, {'true-shooting-percentage': 'desc'})

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