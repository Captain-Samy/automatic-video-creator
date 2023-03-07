import openai
from gtts import gTTS
from googleapiclient.discovery import build
from pytube import YouTube
from pydub import AudioSegment
from moviepy.video.io.VideoFileClip import VideoFileClip
from mutagen.mp3 import MP3
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from elevenlabslib import ElevenLabsUser
from pydub import AudioSegment
import pydub
import pydub.playback
import io


#Get input
print("Enter Topic: ")
topic = input()
print("Enter Youtube Video Link:")
youtubeVideoLink = input()
print("Enter Video Start in seconds: ")
videoStart = input()
if not videoStart:
    videoStart = 0
print("Enter Video End in seconds: ")
videoEnd = input()
if not videoEnd:
    videoEnd = 0
print("Enter Background Theme/music: ")
backgroundThemeLink = input()
print("Theme Start in seconds: ")
themeStart = input()
if not themeStart:
    themeStart= 0

topic = "Battlefield 4"
youtubeVideoLink = "https://www.youtube.com/watch?v=cmYVGZ1w1y4"
backgroundThemeLink = "https://www.youtube.com/watch?v=pUOibX2xV34"
themeStart = 0
videoStart = 10

###### Get Text about the Game 
API_SECRET_KEY_OPENAI = "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"

openai.api_key = API_SECRET_KEY_OPENAI

prompt = "Write an 1 sentence short ironic review about " + topic + " saying the exact opposite of what the general opinion on the games biggest pain points is"

model = "text-davinci-003"
temperature = 0.9
max_tokens = 30


response = openai.Completion.create(prompt = prompt, model = model, temperature=temperature, max_tokens = max_tokens)

text = response["choices"][0]["text"]
print(text)

"""
###### Text to Speech
#speech = gTTS(text = text, lang = "en-us", slow = False)
#speech.save("speech.mp3")
"""

user = ElevenLabsUser("50053dae449db964a829c6dda45034ce") #fill in your api key as a string
voice = user.get_voices_by_name("Josh")[0]  #fill in the name of the voice you want to use. ex: "Rachel"
voice_bytes = voice.generate_audio_bytes(text) #fill in what you want the ai to say as a string


###### BG Audio

audio = YouTube(backgroundThemeLink)
audio_stream = audio.streams.filter(only_audio=True).first()
audio_stream.download(filename="backgroundAudio.mp3",)


#Combine audio files 
speech_audio = AudioSegment.from_file_using_temporary_files(io.BytesIO(voice_bytes))
speech_audio.export("speech.mp3", format="mp3")
background_audio = AudioSegment.from_file("backgroundAudio.mp3")


# Get the duration of the speech audio in milliseconds
audioLength = MP3("speech.mp3")
speech_duration = audioLength.info.length

# Cut the background audio to the same duration as the speech audio
background_audio = background_audio[int(themeStart*1000):]
background_audio = background_audio[:speech_duration]

# Adjust the volume of the speech audio
speech_audio = speech_audio
background_audio = background_audio - 10

# Overlay the speech audio onto the background audio
speech_audio_to_combine = AudioSegment.from_mp3("speech.mp3")
combined_audio = background_audio.overlay(speech_audio_to_combine)

# Export the combined audio as an mp3 file
combined_audio.export("combinedAudio.mp3", format="mp3")

###### Get Youtube Video

# Create a YouTube object and get the highest resolution stream
yt = YouTube(youtubeVideoLink)
stream = yt.streams.get_highest_resolution()
stream.download(filename="video.mp4")
#audioLength = MP3("speech.mp3")
cutVideo = VideoFileClip("video.mp4").subclip(int(videoStart), int(videoStart) + speech_duration).without_audio()
cutVideo = cutVideo.set_audio(AudioFileClip("combinedAudio.mp3"))
cutVideo.write_videofile("cutVideo.mp4")