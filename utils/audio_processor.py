import yt_dlp               ##Take a YouTube URL → download its audio.
## AudioSegment
from pydub import AudioSegment        
import os

DOWNLOAD_DIR = 'downloade'           ##the folder where downloaded audio will be stored.

os.makedirs(DOWNLOAD_DIR, exist_ok = True)      ##Create the folder if it doesn't exist. If it already exists, that's fine


#takes a YouTube URL and downloads its audio.
def download_youtube_audio(url :str) ->str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    #This dictionary contains the configuration for yt-dlp.
    ydl_opts = {
        #Download the best available audio stream.
        "format": "bestaudio/best",
        #output template. 
        "outtmpl": output_path,
        "postprocessors": [
            {
                #ells yt-dlp to use FFmpeg to extract/convert the audio.
                "key": "FFmpegExtractAudio",
                #You want the final audio to be: wav : WAV is useful for speech-processing pipelines because it is typically uncompressed PCM audio.
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        #Normally yt-dlp prints lots of information:
        # so it suppress most of that output.
        "quiet": True,
    }

    try:
        import deno
        ydl_opts["js_runtimes"] = {
            "deno": {
                "path": deno.find_deno_bin()
            }
        }
    except ImportError:
        pass
    #Creating the YouTube downloader
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        #Extract information and download
        info = ydl.extract_info(url, download=True)
        #Getting the final filename
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename



# This handles local files instead of YouTube URLs.
def convert_to_wav(input_path: str) -> str:

    """Convert any audio/video file to WAV format using FFmpeg."""

    import subprocess
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, 
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", 
            output_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg conversion failed for {input_path}") from e

    return output_path


#This function takes a WAV file and divides it into smaller pieces.
# defaukt chunk value is 10 if user does not gives any value
def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:

    #Load WAV
    audio = AudioSegment.from_wav(wav_path)

    #Convert minutes to milliseconds,Because Pydub works with milliseconds for slicing.
    chunk_ms = chunk_minutes * 60 * 1000 

    #This list will contain the filenames of all generated chunks.
    chunks = []

    # start : 0 , stop : len(audio) , steps : chunk_ms(10*60*1000 = 600000) it means it takes 600000 then 1200000 then 1800000...
    for i, start in enumerate(range(0,len(audio),chunk_ms)):

        # chunk from 0 to chunk_ms
        chunk = audio[start : start + chunk_ms]

        #Creating the filename
        chunk_path = f"{wav_path}_chunk_{i}.wav"

        # export() saves that audio to the computer.
        # this creates the actual file.
        chunk.export(chunk_path , format = "wav")

        #Adding the path to chunks
        chunks.append(chunk_path)
    
    return chunks



#This is the main controller function.
# It accepts either: YouTube URL or Local file

def process_input(source: str) -> list:
     
    #if it is an yt url: youTube processing
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks



# YouTube URL
#      ↓
# yt-dlp
#      ↓
# Download audio
#      ↓
# WAV
#      ↓
# wav_path



# Local file
#     ↓
# Pydub
#     ↓
# WAV
#     ↓
# 16 kHz
#     ↓
# Mono



        #          process_input()
        #                │
        #       ┌────────┴────────┐
        #       │                 │
        #  YouTube URL         Local file
        #       │                 │
        #       ▼                 ▼
        #    yt-dlp             pydub
        #       │                 │
        #       ▼                 ▼
        #      WAV               WAV
        #       │                 │
        #       └────────┬────────┘
        #                ▼
        #       16 kHz + Mono*
        #                │
        #                ▼
        #          chunk_audio()
        #                │
        #                ▼
        #        Split every 10 min
        #                │
        #                ▼
        #       ┌────────┴────────┐
        #       ▼        ▼        ▼
        #     chunk 0  chunk 1  chunk 2

#                        ↓↓
#                      WHISPER
#                         ↓
#                    Transcribed text
 