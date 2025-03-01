
# osu!Restore Toolkit

**Scripts for fetching, extracting, parsing and downloading automatically for restoring played osu! beatmaps from a specified user.**

![Full CSV Support](https://raw.githubusercontent.com/ad1107/osu-restore-toolkit/refs/heads/main/demo.jpg)

# Features
**Included in repo:**
- getID: 
	- osu!Bancho APIv2 connection code, with easy-to-enter Client-ID and Client-Secret - More on that in the tutorial below.
	- Getting raw data, played beatmap supposed in the "most_played" category in profile.
	- Raw output.json shows all merged-from-paginated data from osu! database of played beatmaps, with filtered ID in the ID.txt. Feel free to use for aiding other automation tools.
	- Support all gamemodes/rulesets.
	- Detailed CSV with ALL Parsed data, Good for visualization, or analytics.
- Fields Parsed:
	- Index:  `Index`
	- Username:  `username` (fetched from osu! API using `USER_ID`)
	- User ID:  `USER_ID`
	- Beatmapset Name:  `beatmapset.title`
	- Beatmapset ID:  `beatmapset.id`
	- Beatmapset Artist:  `beatmapset.artist`
	- Beatmap Creator:  `beatmapset.creator`
	- Beatmap Difficulty Title:  `beatmap.version`
	- Beatmap Difficulty ID:  `beatmap.id`
	- Mode:  `beatmap.mode`
	- Status:  `beatmap.status`
	- Length:  `beatmap.total_length` (converted to `mm:ss`)
	- Star Rating:  `beatmap.difficulty_rating`
	- Retry count:  `count`


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
