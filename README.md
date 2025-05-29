# osu!Restore Toolkit

**A comprehensive toolkit for fetching, extracting, parsing, and downloading beatmaps from osu! and various popular private servers. (Extendable)**

![Full CSV Support](https://raw.githubusercontent.com/ad1107/osu-restore-toolkit/refs/heads/main/demo.jpg)



## Features

### Server Support
- **Official osu! (Bancho v2)** - Full OAuth authentication with most played beatmaps
- **Private Servers**:
  - **Akatsuki** - Multi-gamemode support (osu!, taiko, catch, mania)
  - **Ripple** - Best scores endpoint
  - **Gatari** - Best scores endpoint
  - Easily extendable for more servers

### Data Collection (getID.py)
- **Convenient username input** - just type the username, no user ID lookup needed
- Connect to multiple osu! servers using configurable API endpoints
- Fetch played beatmap data with automatic pagination
- Export raw data to JSON for further processing or analysis
- Generate filtered beatmap IDs in a simple text file
- Create detailed CSV reports with comprehensive beatmap metadata
- Command-line arguments for server selection and username specification

### Data Fields Parsed
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
(might be different in non-bancho servers)

### Download Support (download.py)
- Automatically process IDs from the generated file
- Download from multiple mirror sources:
  - [Beatconnect](https://beatconnect.io/)
  - [catboy (Mino)](https://catboy.best/)
- Configurable concurrent downloads with multi-threading
- Proper file naming and format preservation

## Beatmap Requirements
This script should restore **most**, if not all beatmaps that meet these criteria:
- **For Official osu!bancho**: User must have played the beatmap at least once, beatmap must be in official listing (including graveyarded), player must not be banned/restricted
- **For Private Servers**: Requirements vary by server, generally requires having played the map at least once

## Usage Guide

### Setup
1. Clone this repository and install `requirements.txt`

### For Official osu! Server
1. **Get your API credentials**:
   - Log in to your osu! account
   - Go to [account settings](https://osu.ppy.sh/home/account/edit)
   - Scroll down to OAuth and create a new OAuth application
   - Enter any name for the application (Callback URL can be left blank)
   - Copy your CLIENT_ID and CLIENT_SECRET
   - Update these values in `getID.py`

### Using the Toolkit
0. You can also run the file directly by editing the config arguments in the `getID.py` file.

1. **Simply enter a username** and run:
   ```bash
   # Using default settings (edit USERNAME in getID.py)
   python getID.py
   
   # Or specify parameters
   python getID.py --username cookiezi --server 1
   python getID.py --username your_username --server 2  # Akatsuki
   python getID.py --username your_username --server 3  # Ripple
   python getID.py --username your_username --server 4  # Gatari
   ```

2. **Download the beatmaps**:
   ```bash
   python download.py
   ```

### Server Options
- **1**: osu! (Bancho v2) - Requires OAuth setup
- **2**: Akatsuki - All 4 gamemodes supported
- **3**: Ripple - Best scores
- **4**: Gatari - Best scores


## Adding New Servers
You can easily add new servers by updating the `SERVERS` dictionary in `getID.py`:

```python
5: {
    "name": "Your Server Name",
    "base_url": "https://your-server.com/api/v1",
    "scores_endpoint": "/users/scores/best",
    "user_endpoint": "/users/full",
    "auth_required": False,
    "pagination": {"limit_param": "l", "page_param": "p", "name_param": "name"}
}
```

## Resources and License
- [osu!APIv2 documentation](https://osu.ppy.sh/docs/index.html)
- [ripple APIv1 documentation](https://docs.ripple.moe/docs/api/v1)
- GPLv3 License. See the LICENSE file for more information.
