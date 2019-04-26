# Export Webex Teams users

This script allows you as admin of a Webex Teams Org to export the full list of your users in order to track the "Status" of each and every user account.

The Status field 

![Screenshot 2019-04-26 at 15 52 52 copy](https://user-images.githubusercontent.com/47174761/56814370-5a604e00-683f-11e9-87ed-587248a0a7a2.jpg)



Export the list of the Webex Teams users in a given org with the primary goal of tracking the adoption i.e. the user account status

# Requirements
- **WebexTeamsSDK** available here: https://github.com/CiscoDevNet/webexteamssdk
- **Python 3** - tested with Python 3.7.3 on MacOS 10.14.4


# Files
- **ListUsers_v2.0.py** - the script


# Configure script
1. **Set your personal access token**
	- `myToken=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
	- enter your Personal Access token here. You can find it in https://developer.ciscospark.com, login, click your name (top right)
2. **Set your room ID**
	- `myRoom=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
	- get your room ID from the Spark for Developers page, under Rooms / List rooms
3. **Enter the path to your spreadsheet**
	- myworkbook = /Users/myname/Documents/SparkImport/attendees.xlsx
4. **Enter the start _column_ that contains the email addresses**
	- example: `mysheetStartCol = 3 `
	- Enter the column number where the email addresses start:  example: column A=1, B=2, C=3, D=4 ...
5. **Enter the start _row_ that contains the email addresses**
	- example: `mysheetStartRow = 4 `
	- Enter the row number where the email addresses start
6. **Enable test mode or production**
	- `TestOnly = yes`
	- If "yes": only PRINT results, if "no": add found email addresses to the Spark room.



  

# Run script
1. Go to the folder containing your test.py file
2. Set the "TestOnly" parameter to "yes"
3. Run "python test.py"
4. The script will show the number of succesfully added users and a list of failed users




# Other Info
- The script will only read the _first_ sheet of an Excel workbook
- I have only tested this with Excel 2016 (OSX) spreadsheets
- After the script runs it will show the users that could not be added and the _number_ of succesfully added users.
- This script uses your _personal_ access token, so it runs "as you". The personal access token may change, and could therefore break this code.
- Users will be added as normal users, not room moderators. You can assign room moderators manually
- Spark Developer documentation:  [here](https://developer.ciscospark.com/resource-rooms.html) 
- "Failed users" could have several reasons (for example: already member of that room)


---------------------
