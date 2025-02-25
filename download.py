import os
import re
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

TOTAL_WORKERS = 20

download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloaded")
os.makedirs(download_dir, exist_ok=True)


def get_filename_from_cd(cd):
    """
    Extract filename from Content-Disposition header if available.
    """
    if not cd:
        return None
    fname = re.findall('filename="(.+)"', cd)
    if fname:
        return fname[0]
    fname = re.findall("filename=(.+)", cd)
    if fname:
        return fname[0]
    return None


def download_file(url, index, total, timeout, attempt, attempts, hoster):
    """
    Download a file from the URL to the download folder.
    Displays a progress bar that includes attempt information.
    Returns None on success; returns the URL on failure.
    """
    try:
        with requests.get(url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            # Try to extract filename from Content-Disposition header.
            cd = r.headers.get("Content-Disposition")
            filename = get_filename_from_cd(cd)
            if not filename:
                # Fallback: use the last part of the URL.
                filename = url.split("/")[-1]
            if not filename.lower().endswith(".osz"):
                filename += ".osz"

            local_filename = os.path.join(download_dir, filename)
            total_size = int(r.headers.get("content-length", 0))
            block_size = 1024  # 1 KB

            # Include attempt info in the progress bar description.
            progress_desc = (
                f"{index}/{total} - Attempt {attempt}/{attempts} - {filename}"
            )
            with tqdm(
                total=total_size,
                unit="iB",
                unit_scale=True,
                desc=progress_desc,
                leave=False,
            ) as bar:
                with open(local_filename, "wb") as f:
                    for data in r.iter_content(block_size):
                        f.write(data)
                        bar.update(len(data))
        return None  # Success
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return url  # Failure indicator


def attempt_download_id(id, hoster, attempts, index, total, timeout):
    """
    Attempt to download the file for a given ID from the specified hoster.
    The hoster should be a format string containing '{ID}'.
    Tries up to 'attempts' times.
    Returns True if download succeeds; False otherwise.
    """
    for attempt in range(1, attempts + 1):
        url = hoster.format(ID=id)
        result = download_file(url, index, total, timeout, attempt, attempts, hoster)
        if result is None:
            return True
    print(f"ID {id} FAILED on {hoster.split('/')[2]} after {attempts} attempts.")
    return False


def main():
    # Read IDs from result.txt (one ID per line) and deduplicate.
    with open("result.txt", "r", encoding = "UTF-8") as f:
        ids = [line.strip() for line in f if line.strip()]
    unique_ids = list(dict.fromkeys(ids))
    total_ids = len(unique_ids)
    print(f"Total unique IDs to process: {total_ids}")

    downloaded_ids = set()
    stage1_failed = []  # IDs that failed in stage 1

    hoster1 = "https://beatconnect.io/b/{ID}"
    stage1_attempts = 3
    stage1_timeout = None  # use default timeout

    # Stage 1: Try beatconnect concurrently.
    with ThreadPoolExecutor(max_workers=TOTAL_WORKERS) as executor:
        futures = {
            executor.submit(
                attempt_download_id,
                id,
                hoster1,
                stage1_attempts,
                idx,
                total_ids,
                stage1_timeout,
            ): id
            for idx, id in enumerate(unique_ids, start=1)
        }
        for future in as_completed(futures):
            id_result = futures[future]
            try:
                success = future.result()
                if success:
                    downloaded_ids.add(id_result)
                else:
                    stage1_failed.append(id_result)
            except Exception as e:
                print(f"ID {id_result} raised exception: {e}")
                stage1_failed.append(id_result)

    print(
        f"\nStage 1 complete. Downloaded: {len(downloaded_ids)} files; Failed: {len(stage1_failed)} IDs."
    )

    # Stage 2: For IDs that failed stage 1, try catboy hoster.
    hoster2 = "https://catboy.best/d/{ID}"
    stage2_attempts = 5
    stage2_timeout = 30

    stage2_failed = []  # IDs that still fail after stage 2
    with ThreadPoolExecutor(max_workers=TOTAL_WORKERS) as executor:
        futures = {
            executor.submit(
                attempt_download_id,
                id,
                hoster2,
                stage2_attempts,
                idx,
                len(stage1_failed),
                stage2_timeout,
            ): id
            for idx, id in enumerate(stage1_failed, start=1)
        }
        for future in as_completed(futures):
            id_result = futures[future]
            try:
                success = future.result()
                if success:
                    downloaded_ids.add(id_result)
                else:
                    stage2_failed.append(id_result)
            except Exception as e:
                print(f"ID {id_result} raised exception in stage 2: {e}")
                stage2_failed.append(id_result)

    total_downloaded = len(downloaded_ids)
    total_failed = len(stage2_failed)
    print(f"Total files downloaded: {total_downloaded}")
    print(f"Total IDs failed after all attempts: {total_failed}")
    print("Failed IDs: ", end="")
    print(*stage2_failed, sep=" ")


if __name__ == "__main__":
    main()
