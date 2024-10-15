import requests
import logging
from scipy.signal import find_peaks
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_video_id(youtube_url):
    """Extracts the video ID from the YouTube URL."""
    return youtube_url.split("=")[-1]

def get_most_replayed_parts(video_id, max_retries=5, backoff_factor=2):
    """Fetches most replayed parts for a given video ID."""
    url = f"https://yt.lemnoslife.com/videos?part=mostReplayed&id={video_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    retries = 0
    delay = 2  # Initial delay

    while retries <= max_retries:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            retries += 1
            if retries <= max_retries:
                logger.warning(f"Error fetching data (attempt {retries}): {e}")
                logger.warning(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= backoff_factor  # Exponential backoff
            else:
                logger.error(f"Max retries exceeded. Error: {e}")
                return None

def find_top_replayed_timestamps(most_replayed_data, peak_prominence):
    """Finds timestamps of the most replayed parts based on intensity scores."""
    if not most_replayed_data or "items" not in most_replayed_data or not most_replayed_data["items"]:
        logger.warning("No most replayed data available.")
        return []

    video_data = most_replayed_data["items"][0]
    if "mostReplayed" not in video_data or "markers" not in video_data["mostReplayed"]:
        logger.warning("Unexpected format in most replayed data.")
        return []

    markers = video_data["mostReplayed"]["markers"]
    intensities = [marker["intensityScoreNormalized"] for marker in markers]
    peaks, _ = find_peaks(intensities, prominence=peak_prominence)
    timestamps = [markers[i]["startMillis"] for i in peaks]
    print(f"Intensities: {intensities},markers: {markers}, peaks: {peaks}, timestamps: {timestamps}")
    return intensities

def main(youtube_url, peak_prominence=0.1):
    """Main function to orchestrate the extraction of most replayed timestamps."""
    video_id = extract_video_id(youtube_url)
    most_replayed_data = get_most_replayed_parts(video_id)
    timestamps = find_top_replayed_timestamps(most_replayed_data, peak_prominence)

    # print(f"Most replayed timestamps: {timestamps}")

if __name__ == "__main__":
    youtube_url = 'https://www.youtube.com/watch?v=TT-lgCSAmbI'  # Sample YouTube URL
    main(youtube_url)