# Webex Teams Tools: Export to .CSV to track active/pending users and post in Teams spaces
#
# Davide Grandis (dgrandis@cisco.com)
# version 1.0 - 09/12/2018
# version 2.0 - 25/04/2019

# New in v2.0:
#   - ini file to retrieve: org_id, admin access token, post to Teams (bot): bot access token
#   - BOT for posting into Teams of summary and .csv file

from webexteamssdk import WebexTeamsAPI
import sys
import csv
import os
import configparser
import time


def main():

    inifile = 'ListUsers_config'
    CSVfile = 'UserStatusExport.csv'

    print('\nWebex Teams Adoption Tracker Tool v. 2.0 (25/04/19) by dgrandis@cisco.com')
    PrintSeparator()
    print(' - checking the configuration file...')

    # Allows for no value parameters (only for the search criteria that is optional)
    config = configparser.ConfigParser(allow_no_value=True)

    # Management of the configuration file
    if os.path.isfile('./' + inifile + '.ini'):
        try:
            config.read('./' + inifile + '.ini')
            OrgId = str(config['MAIN']['Org ID'])
            AccessToken = str(config['MAIN']['Admin access token'])
            SearchMode = str(config['MAIN']['Search mode']).lower()
            PostTeams = str(config['BOT']['Post to Teams']).lower()
            BotAccessToken = str(config['BOT']['BOT access token'])
        except Exception as e:
            print('   **ERROR** reading the file',
                  inifile + '.ini for the parameter', str(e))
            PrintSeparator()
            ResetConfigFile(inifile, newfile=False)
            quit()
    else:
        # Creates config file because it does not exist
        ResetConfigFile(inifile, newfile=True)
        quit()
    # Validates the settings from the configuration file
    #   valid org ID has len = 87
    print(' - validating the configuration file...')
    validation_error = ''
    if not OrgId or len(OrgId) != 87:
        validation_error = '   **ERROR** Org ID not valid!\n'
    #   valid access token has len > 50 (at least)
    if not AccessToken or len(AccessToken) < 50:
        validation_error += '   **ERROR** Admin access token not valid!\n'
    #   valid search mode is either a, c or p (already converted to lowercase)
    if not SearchMode or SearchMode not in ['a', 'c', 'p']:
        validation_error += '   **ERROR** Search mode not valid!\n'
    #   valid Post to Teams is either yes or no
    if not PostTeams or PostTeams not in ['yes', 'no']:
        validation_error += '   **ERROR** Post to Teams setting not valid!\n'
    #   valid BOT access token (if Post to Teams = yes)
    if PostTeams == 'yes' and (not BotAccessToken or len(BotAccessToken) < 50):
        validation_error += '   **ERROR** BOT access token not valid!\n'
    if validation_error != '':
        print(validation_error)
        print('Please set properly the configuration parameters and re-run this script.')
        PrintSeparator()
        quit()
    # Configuration parameters validated -> execution
    # Retrieve the Org name
    api = WebexTeamsAPI(access_token=AccessToken)
    try:
        org_name = api.organizations.get(OrgId)
    except Exception as e:
        print('   ***ERROR*** Please check the access token and the Org ID. Hint: the access token may have expired.')
        PrintSeparator()
        quit()
    print('   Export user list for the org:', org_name.displayName + '\r')
    # Retrieve the list of users in the Org
    try:
        users = api.people.list(orgId=OrgId)
    except Exception as e:
        print('   ***ERROR*** Please check that the provided Org ID is correct.')
        quit()
    # export to .csv file
    headers = ['First name', 'Last name',
               'Display name', 'Email', 'Invite pending']
    # if Post to Teams = yes the file is created in the same folder as the script
    if PostTeams == 'yes':
        path = CSVfile
    else:
        path = definefilepath(CSVfile)
    print(' - Work in progress, please wait... (ignore possible rate-limit warnings)')
    with open(path, 'w', encoding='utf-8') as out:
        writer = csv.DictWriter(out, headers, extrasaction='ignore')
        writer.writeheader()
        userCount = 0
        UserActiveCount = 0
        UserPendingCount = 0
        for user in users:
            if (SearchMode == 'a') or (SearchMode == 'c' and not user.invitePending) or (SearchMode == 'p' and user.invitePending):
                writer.writerow({'First name': user.firstName,
                                 'Last name': user.lastName,
                                 'Display name': user.displayName,
                                 'Email': user.emails[0],
                                 'Invite pending': str(user.invitePending)})
            userCount = userCount + 1
            if user.invitePending:
                UserPendingCount = UserPendingCount + 1
            else:
                UserActiveCount = UserActiveCount + 1
    PercActive = ' (' + str(int(UserActiveCount/userCount*100)) + '%)'
    PercPending = ' (' + str(int(UserPendingCount/userCount*100)) + '%)'
    print(' - User list export for the Org "' +
          org_name.displayName + '" completed')
    # Output
    summary = 'Total users: ' + str(userCount) + ' | Active users: ' + str(
        UserActiveCount) + PercActive + ' | Invite pending users: ' + str(UserPendingCount) + PercPending
    timeExport = time.localtime()
    dayy = str(time.strftime('%A', timeExport))
    day = str(time.strftime('%d', timeExport))
    month = str(time.strftime('%B', timeExport))
    year = str(time.strftime('%Y', timeExport))
    date = dayy + ' ' + month + ' ' + day + ' ' + year

    if PostTeams == 'yes':
        # Retrieve the list of the spaces where the BOT belongs to
        api = WebexTeamsAPI(access_token=BotAccessToken)
        try:
            # list() is required in order to convert the output into a list so that the len() function can be used
            spaces = list(api.rooms.list())
        except Exception as e:
            print(e)
            quit()
        if len(spaces) > 0:
            text = date + ': User list exported for the Org "' + \
                org_name.displayName + '"\n' + summary
            for space in spaces:
                #print(space.id, space.title)
                result = PostMessage(BotAccessToken, space.id, text, path)
                if result == 'Success':
                    print(' - Report posted in the space: "' + space.title + '"')
        else:
            print(
                '   **ERROR** The BOT has NOT been added to any space - please add it and re-run this script.')
    else:
        print('   User list exported in file {}'.format(path))
        print('   ' + summary)
    print(' - END')
    PrintSeparator()


def PrintSeparator():
    print('-------------------------------------------------------------------------')


def ResetConfigFile(filename, newfile):
    # Creates (writes or re-writes) the configuration file
    config = configparser.ConfigParser(allow_no_value=True)
    try:
        config.add_section('MAIN')
        config.set('MAIN', '# ID of the Webex Teams Org (from https://developer.webex.com/docs/api/v1/organizations/list-organizations)')
        config.set('MAIN', 'Org ID', '<REQUIRED>')
        config.set('MAIN', '# Access token of an admin account for the org (from developer.webex.com)')
        config.set('MAIN', 'Admin access token', '<REQUIRED>')
        config.set('MAIN', '# list all users [A] (default), active users [C], pending activation [P]')
        config.set('MAIN', 'Search mode', 'A')
        config.add_section('BOT')
        config.set('BOT', '# yes | no (default)')
        config.set('BOT', "# If 'no' is selected the report file is saved on the computer's desktop folder")
        config.set('BOT', 'Post to Teams', 'no')
        config.set('BOT', '# Access token of the BOT from developer.webex.com -> My Webex Teams Apps')
        config.set('BOT', "# Note: required if 'Post to Teams' = yes")
        config.set('BOT', 'BOT access token', '<add here>')
        config.set('BOT', '# Note: the report will be posted in all the spaces where the BOT has been added to')
        with open('./' + filename + '.ini', 'w') as configfile:
            config.write(configfile)
        if newfile:
            print('   Configuration file (' + filename +
                  '.ini) created in the current folder.')
        else:
            print('   Configuration file (' + filename +
                  '.ini) reset in the current folder.')
        print('Please set the required configuration parameters and re-run this script.')
        PrintSeparator()
    except:
        print('   ERROR creating the onfiguration file (' +
              filename + '.ini) in the current folder.')
        print('Please check out the file system access and re-run this script.')
        PrintSeparator()


def definefilepath(filename):
    if sys.platform == 'darwin':
        path = os.path.expanduser('~/Desktop/' + filename)
    elif sys.platform == 'win32':
        path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        path = path + '/' + filename
    else:
        path = filename
    return path


def PostMessage(token, spaceid, message, filename=''):
    api = WebexTeamsAPI(access_token=token)
    if filename == '':
        try:
            api.messages.create(spaceid, text=message)
        except:
            return 'Failure'
        return 'Success'
    else:
        # The files parameter expects to receive a LIST containing a single string with the path to the file to be uploaded
        file_list = [filename]
        #abs_path = os.path.abspath(filename)
        try:
            api.messages.create(spaceid, text=message, files=file_list)
        except:
            return 'Failure'
        return 'Success'


if __name__ == '__main__':
    main()
