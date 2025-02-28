# osu!Restore Toolkit

**Scripts for fetching, extracting, parsing and downloading automatically for restoring played osu! beatmaps from a specified user.**

# Features
**Included in repo:**
- getID: 
	- osu!Bancho APIv2 connection code, with easy-to-enter Client-ID and Client-Secret - More on that in the tutorial below.
	- Getting raw data, played beatmap supposed in the "most_played" category in profile.
	- Raw output.json shows all merged-from-paginated data from osu! database of played beatmaps, with filtered ID in the result.txt
	- Support all gamemodes/rulesets.
	- Detailed CSV with ALL Parsed data.
	[Specifically: "Username", "User ID", "Beatmapset Name", "Beatmapset ID", "Beatmapset Artist", "Beatmap Creator" "Beatmap Difficulty Title", "Beatmap Difficulty ID", "Mode", "Status", "Length", "Star Rating", "Retry Count", "Download Link"]
- download:
	- Automatically get all ID in the file and sort by unique IDs to save download time and requests.
	- Uses two hosters: [Beatconnect](https://beatconnect.io/) and [catboy (Mino)](https://catboy.best/) with two stages for safe downloading
	- Retain and fix original beatmap file name format and extension - osz.
	- Adjustable threads and timeout, limits.
## Beatmap requirements
- This script should restore **most**, if not all of the beatmap that the user has those criteria:
	- Submitted a score at least once (should be a pass at any mods at any ranks)
	- Must be in the osu! official beatmap listing, so even graveyarded maps will work.
	- Must be logged in and online when playing.
    	- The player (should) not being banned or removed/restricted.
	- (For now) No custom server (devserver) supported (akatsuki, ripple,...)

## Tutorials

- First, clone the repo. It really should have gone without saying ;)
- Check all the requirements libraries.
- **(IMPORTANT)** Get yourself a client token:
	-	Log in with your osu! account, though theoretically **any** account will work.
	-	Go to [account settings](https://osu.ppy.sh/home/account/edit).
	-	Scroll down to get OAuth information and create a new one.
	-	Pick any Application Name and let Callback URLs blank.
	-	Register and get your very own CLIENT_ID and CLIENT_SECRET for [getID.py](https://github.com/ad1107/osu-restore-toolkit/blob/main/getID.py) file.
- Run getID first to export all IDs in ID.txt and then confirm to download by running download.py.

## Resources and License
- osu!APIv2 documentations https://osu.ppy.sh/docs/index.html
- GPLv3 License. Read the LICENSE for more info.
