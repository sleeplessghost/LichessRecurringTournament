# LichessRecurringTournament
Uses the lichess API to create recurring tournaments. You can configure a tournament and have it created for you on a daily/weekly/fornightly/monthly schedule. This can:
- Create a lichess tournament on the date/time matching the configured schedule
- Send a PM notification to members of a team you lead to remind them of tournaments 24 hours before they start

## Requirements
- [python](https://www.python.org/) - created with `3.11`

### Libraries
Included in `requirements.txt`. Can install together with `pip install -r requirements.txt`, or individually as below:
- [typer](https://typer.tiangolo.com/) `pip install typer[all]`
- [requests](https://requests.readthedocs.io) `pip install requests`

## Initial setup
Run `py litourney.py setup` and you will be asked to input:
- A lichess API personal access token.
- The number of days in the future you want tournaments to be created.

You can generate a personal access token here: https://lichess.org/account/oauth/token

The token should have `tournament:write`, `team:read`, and `team:lead` permissions ([pre-filled create token link](https://lichess.org/account/oauth/token/create?scopes[]=tournament:write&scopes[]=team:read&scopes[]=team:lead&description=Lichess+Recurring+Tournament+tool)).

![team](https://user-images.githubusercontent.com/25903992/229781768-439d8065-7e9b-41e6-b9fb-d2321cba4bd7.PNG)

After completing setup configuration, you should run `py litourney.py refresh` to load and save your lichess username and which teams you lead.

If the teams you lead changes in the future, you can run `refresh` again to get the new data.

## Tournament management
These options should be fairly self explanatory as it will prompt you for inputs and provide hints as you use them:

- `py litourney.py new` - Configure a new recurring tournament
- `py litourney.py list` - List configured tournaments
- `py litourney.py edit` - Edit a configured tournament
- `py litourney.py delete` - Delete a configured tournament

You can also run `py litourney.py --help` to get a list of the available commands and some information about them.

## Templating helpers
There is some functionality for text replacement in tournament names and in PM templates, with keys that look like this `[name]`. Those keys will be replaced when creating a tournament or sending a team PM with the actual value.

#### Tournament name
- `[winner]` : name of the previous tournament winner (or removed if there was no previous tournament).

Note if using this: be cautious of the number of days in advance you are creating tournaments as it will only store the most recently created ID for looking up previous winner.

#### PM template
- `[name]` : tournament name
- `[variant]` : chess variant (e.g. standard / chess960)
- `[clocktime]` : initial clock time in minutes (e.g. for blitz `5+3`, this would return `5`)
- `[clockincrement]` : increment in seconds (e.g. for blitz `5+3`, this would return `3`)
- `[link]` : a link to the tournament
- `[br]` : a newline character

## Tournament creation
To create your configured tournaments within the next X days (from your initial setup config):
- `py litourney.py create`

This will find all configured tournaments which will next occur within the next X days and create them, if they haven't already been created.

## Team PMs
To notify your team members of upcoming tournaments:
- `py litourney.py notify`

This will find all configured tournaments that have already been created which will occur in the next 24 hours and send a PM to the team.
- This only applies to tournaments which are restricted to a particular team.
- You must be a leader of that team to be able to send PMs.
- PMs will only be sent for tournaments where you have configured a PM template (as part of configuring a new tournament).
- A PM will only be sent for a particular tournament a single time, running the `notify` command again won't resend it until the next time the tournament reccurs.

## Automation
After you have configured your tournaments, you may want to automate the creation and PM notifications so you don't need to manually run it each week. A simple way to do this in windows would be to make a batch file (`.bat`) as below:
```
py litourney.py create
py litourney.py notify
```
And using `Task Scheduler` to run this batch file automatically on a schedule e.g.
- Run daily at log on
- Repeat task every 1 hour

Or other schedules like daily at a specific time, or weekly on a specific day.

You should be able to do something similar in unix with a cron job.
