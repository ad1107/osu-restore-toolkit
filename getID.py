import requests
import json

# Replace these with your actual osu! API credentials
CLIENT_ID = "CLIENT"
CLIENT_SECRET = "SECRET"
USER_ID = "ID"
API_URL = f"https://osu.ppy.sh/api/v2/users/{USER_ID}/beatmapsets/most_played"


def get_access_token(client_id, client_secret):
    """
    Obtain an access token from the osu! API using client credentials.
    """
    token_url = "https://osu.ppy.sh/oauth/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "public",
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print("Error obtaining token:", response.status_code, response.text)
        return None


def fetch_api_data(url, access_token):
    """
    Send a GET request to the provided API URL with the proper Authorization header.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response


def fetch_all_data():
    """
    Paginate through the API, fetch all data, and export it to 'output.json'.
    """
    token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    if not token:
        return None

    print("Access token obtained successfully.")

    all_data = []
    limit = 50
    offset = 0

    while True:
        paginated_url = f"{API_URL}?limit={limit}&offset={offset}"
        print(f"Fetching data from: {paginated_url}")
        response = fetch_api_data(paginated_url, token)
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            break

        data = response.json()
        # If no data is returned, we have reached the end.
        if not data:
            break

        all_data.extend(data)
        print(f"Fetched {len(data)} results.")

        # If fewer results than 'limit' are returned, assume it's the last page
        if len(data) < limit:
            break

        offset += limit

    # Export the raw combined JSON data to output.json
    with open("output.json", "w") as outfile:
        json.dump(all_data, outfile, indent=4)
    print("\nData exported to output.json")
    return all_data


def parse_and_export(input_filename, output_filename):
    """
    Parse the exported JSON data to extract desired fields and export links to 'result.txt'.
    """

    # Load the JSON data from the file
    with open(input_filename, "r") as infile:
        data = json.load(infile)

    with open(output_filename, "w") as outfile:
        for index, item in enumerate(data, start=1):
            beatmapset_id = item.get("beatmap", {}).get("beatmapset_id", "N/A")
            outfile.write(f"{beatmapset_id}\n")

    print(f"Parsed data exported to {output_filename}")


def main():
    # Step 1: Fetch and export raw API data
    data = fetch_all_data()
    if data is None:
        print("No data fetched. Exiting.")
        return

    # Step 2: Parse the exported data and create a result file
    parse_and_export("output.json", "result.txt")


if __name__ == "__main__":
    main()
