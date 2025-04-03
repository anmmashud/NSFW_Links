import streamlit as st
import yt_dlp
import os
import tempfile

# Function to fetch available combined formats (video + audio)
def get_available_formats(url):
    """Fetch and return a list of available video formats with both video and audio."""
    ydl_opts = {
        'quiet': True,  # Suppress console output
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)  # Get info without downloading
            formats = info['formats']
            # Filter for formats with both video and audio
            combined_formats = [
                f for f in formats 
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none'
            ]
            # Sort by resolution (height) in descending order
            combined_formats = sorted(combined_formats, key=lambda x: x.get('height', 0), reverse=True)
            return combined_formats
    except Exception as e:
        raise Exception(f"Failed to fetch formats: {e}")

# Function to convert file size to a human-readable format
def format_size(size):
    """Convert bytes to a readable size string (e.g., MB or GB)."""
    if size is None:
        return "unknown size"
    size_mb = size / (1024 * 1024)  # Convert to MB
    if size_mb < 1024:
        return f"{size_mb:.2f} MB"
    else:
        size_gb = size_mb / 1024  # Convert to GB
        return f"{size_gb:.2f} GB"

# Function to download the video in the selected format
def download_video(url, format_id):
    """Download the video using the specified format ID and return file details."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmpfile:
        ydl_opts = {
            'format': format_id,  # Use the selected format
            'outtmpl': tmpfile.name,  # Save to temporary file
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info['title']
                ext = info['ext']
            return tmpfile.name, title, ext
        except Exception as e:
            raise Exception(f"Download failed: {e}")

# Streamlit app interface
st.title("Video Downloader with Resolution Selection")

# Initialize session state to store formats
if 'formats' not in st.session_state:
    st.session_state.formats = []

# User input for video URL
url = st.text_input("Enter video URL:", placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Button to fetch available formats
if st.button("Fetch Formats"):
    if url:
        try:
            formats = get_available_formats(url)
            st.session_state.formats = formats
            st.success("Available formats fetched successfully!")
        except Exception as e:
            st.error(str(e))
    else:
        st.warning("Please enter a valid URL.")

# Display format selection if formats are available
if st.session_state.formats:
    display_strings = []
    for f in st.session_state.formats:
        height = f.get('height', 'unknown')  # Resolution height (e.g., 1080)
        ext = f['ext']  # File extension (e.g., mp4)
        size = f.get('filesize') if f.get('filesize') is not None else f.get('filesize_approx')
        size_str = format_size(size)  # Human-readable size
        format_id = f['format_id']  # Unique format identifier
        display_string = f"{height}p - {ext} - {size_str} (format {format_id})"
        display_strings.append(display_string)

    # Let user select a format
    selected_display = st.selectbox("Select a format to download:", display_strings)
    selected_format_id = selected_display.split("(format ")[1].split(")")[0]

    # Button to initiate download
    if st.button("Download Video"):
        try:
            with st.spinner("Downloading video, please wait..."):
                filename, title, ext = download_video(url, selected_format_id)
            with open(filename, "rb") as file:
                st.download_button(
                    label="Click to Download Video",
                    data=file,
                    file_name=f"{title}.{ext}",
                    mime=f"video/{ext}"
                )
            os.remove(filename)  # Clean up temporary file
            st.success("Video downloaded successfully!")
        except Exception as e:
            st.error(str(e))
else:
    st.info("Enter a URL and click 'Fetch Formats' to see available resolutions.")