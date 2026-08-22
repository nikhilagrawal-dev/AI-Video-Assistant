import whisper
import os
import requests
from pydub import AudioSegment

# Sarvam's sync STT-translate API rejects audio longer than 30s.
# We slice each chunk into 25s pieces (with a 5s safety margin) before sending.
SARVAM_PIECE_SECONDS = 25


WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")


SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")


#This variable will eventually contain your loaded Whisper model.
_model = None


#This function loads Whisper when necessary. 
def load_model():

    #I'm referring to the _model variable outside this function.
    global _model  

    if _model is None: 
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")

        #Whisper loads the model into memory.
        _model = whisper.load_model(WHISPER_MODEL) 

        print("Whisper model loaded.")
    return _model 



#This function transcribes one chunk using Whisper.
def transcribe_chunk_whisper(chunk_path: str) -> str:

    model = load_model()  

    result = model.transcribe(chunk_path, task="transcribe")  
    return result["text"]  



#Now we move to the second transcription engine. for hinglish
def _send_to_sarvam(piece_path: str) -> str:
    """Send one ≤ 30s WAV file to Sarvam and return the English transcript."""

    #This puts your API key into the HTTP request.
    headers = {"api-subscription-key": SARVAM_API_KEY}

    with open(piece_path, "rb") as f:
        files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
        data = {"model": SARVAM_MODEL, "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:
        print(f"\n❌ Sarvam returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    return response.json().get("transcript", "")


# 10-minute chunk
#       ↓
# 25-second pieces
#       ↓
# Sarvam
#       ↓
# individual transcripts
#       ↓
# combine them

def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Sarvam sync API only accepts ≤30s audio. We split this chunk into
    25-second pieces, send each separately, and join the transcripts.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000

    full_text = ""
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start: start + piece_ms]
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav")

        try:
            print(f"  → Sarvam piece {i + 1}/{total_pieces} ...")
            full_text += _send_to_sarvam(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()

   


 #Which transcription engine should I use?
def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """
    Route one chunk to Whisper or Sarvam depending on language choice.
    - english  → Whisper (local model)
    - hinglish → Sarvam (translates to English while transcribing)
    """
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)
    return transcribe_chunk_whisper(chunk_path)



#This function processes all the 10-minute chunks. It will transcribe all chunks
def transcribe_all(chunks: list, language: str = "english") -> str:

    full_transcript = "" 

    engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper"
    print(f"Using {engine} for transcription.")

    for i, chunk in enumerate(chunks):  

        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        text = transcribe_chunk(chunk, language=language)  

        full_transcript += text + " "  

    print("Transcription complete.")

    return full_transcript.strip()  



    #              VIDEO
    #                │
    #                ▼
    #           Audio extraction
    #                │
    #                ▼
    #          WAV 16kHz Mono
    #                │
    #                ▼
    #       ┌──────────────────┐
    #       │  10-minute chunk │
    #       └──────────────────┘
    #                │
    #       ┌────────┴─────────┐
    #       │                  │
    #    English            Hinglish
    #       │                  │
    #       ▼                  ▼
    #    Whisper             Sarvam
    #       │                  │
    #       │            25-second pieces
    #       │                  │
    #       │          ┌───────┼───────┐
    #       │          ▼       ▼       ▼
    #       │         25s     25s     25s
    #       │          │       │       │
    #       │          └───────┼───────┘
    #       │                  │
    #       │               Sarvam
    #       │                  │
    #       └────────┬─────────┘
    #                ▼
    #          Text transcript
    #                │
    #                ▼
    #        Combine all chunks
    #                │
    #                ▼
    #        FINAL TRANSCRIPT








# First chunk
#     ↓
# load Whisper
#     ↓
# transcribe

# Second chunk
#     ↓
# reuse model
#     ↓
# transcribe

# Third chunk
#     ↓
# reuse model
#     ↓
# transcribe





# 60-minute audio
#       ↓
# 6 × 10-minute chunks
#       ↓
# each chunk → ~24 × 25-second pieces
#       ↓
# ~144 Sarvam API calls