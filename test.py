from typing import Optional
import openai
from gtts import gTTS
from googleapiclient.discovery import build
from pyparsing import Sequence
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
from moviepy.video.fx.all import crop
import pvleopard
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.0-Q16-HDRI\\magick.exe"})

def second_to_timecode(x: float) -> str:
    hour, x = divmod(x, 3600)
    minute, x = divmod(x, 60)
    second, x = divmod(x, 1)
    millisecond = int(x * 1000.)

    return '%.2d:%.2d:%.2d,%.3d' % (hour, minute, second, millisecond)

def to_srt(words: Sequence[pvleopard.Leopard.Word]) -> str:
    def _helper(word: pvleopard.Leopard.Word, prev_end: float) -> float:
        start = prev_end
        lines.append("%d" % section)
        lines.append(
            "%s --> %s" %
            (
                second_to_timecode(start),
                second_to_timecode(word.end_sec)
            )
        )
        if len(word.word) <= 12:
            lines.append(word.word + '\n')
        else:
            lines.append('\n' + word.word + '\n')
        return word.end_sec
        
    lines = []
    section = 1
    prev_end = 0.0
    for word in words:
        prev_end = _helper(word, prev_end)
        section += 1

    return '\n'.join(lines)


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
videoStart = 40

###### Get Text about the Game 
API_SECRET_KEY_OPENAI = "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"

openai.api_key = API_SECRET_KEY_OPENAI

prompt = "Write a one sentence review about " + topic + " in the style of SsethTzeentach mocking the developers and making fun of community members which liked the game nevertheless using curse words"

model = "text-davinci-003"
temperature = 0.9
max_tokens = 50


response = openai.Completion.create(prompt = prompt, model = model, temperature=temperature, max_tokens = max_tokens)

text = response["choices"][0]["text"]
print(text)

user = ElevenLabsUser("50053dae449db964a829c6dda45034ce") #fill in your api key as a string
voice = user.get_voices_by_name("Josh")[0]  #fill in the name of the voice you want to use. ex: "Rachel"
voice_bytes = voice.generate_audio_bytes(text) #fill in what you want the ai to say as a string




audio = YouTube(backgroundThemeLink)
audio_stream = audio.streams.filter(only_audio=True).first()
audio_stream.download(filename="backgroundAudio.mp3",)


#Combine audio files 
speech_audio = AudioSegment.from_file_using_temporary_files(io.BytesIO(voice_bytes))
speech_audio.export("speech.mp3", format="mp3")
background_audio = AudioSegment.from_file("backgroundAudio.mp3")


# Get the duration of the speech audio in milliseconds
speech_duration = len(speech_audio)

# Cut the background audio to the same duration as the speech audio
background_audio = background_audio[int(themeStart*1000):]
background_audio = background_audio[:speech_duration]

# Adjust the volume of the speech audio
speech_audio = speech_audio + 5  # increase volume by 25 dB
background_audio = background_audio - 10

# Overlay the speech audio onto the background audio
combined_audio = background_audio.overlay(speech_audio)

# Export the combined audio as an mp3 file
combined_audio.export("combinedAudio.mp3", format="mp3")

###### Get Youtube Video

# Create a YouTube object and get the highest resolution stream
yt = YouTube(youtubeVideoLink)
stream = yt.streams.get_highest_resolution()
stream.download(filename="video.mp4")
audioLength = MP3("speech.mp3")
cutVideo = VideoFileClip("video.mp4").subclip(int(videoStart), int(videoStart) + audioLength.info.length).without_audio()
cutVideo = cutVideo.set_audio(AudioFileClip("combinedAudio.mp3"))
cutVideo.write_videofile("cutVideo.mp4")


# Change video format to 9:16

input_file = "cutVideo.mp4"
output_file = "croppedVideo.mp4"

# Load the video clip
clip = VideoFileClip(input_file)

# Get the original aspect ratio
original_aspect_ratio = clip.w / clip.h

# Set the output aspect ratio to 9:16
output_aspect_ratio = 9 / 16

# Compute the required crop
if original_aspect_ratio > output_aspect_ratio:
    # Crop the width
    new_width = clip.h * output_aspect_ratio
    x1 = (clip.w - new_width) / 2
    x2 = x1 + new_width
    y1, y2 = 0, clip.h
else:
    # Crop the height
    new_height = clip.w / output_aspect_ratio
    y1 = (clip.h - new_height) / 2
    y2 = y1 + new_height
    x1, x2 = 0, clip.w

# Crop the video clip
cropped_clip = clip.crop(x1, y1, x2, y2)

# Set the output aspect ratio and size
output_size = (int(cropped_clip.h * output_aspect_ratio), cropped_clip.h)

# Set the output format
output_format = {"fps": clip.fps, "codec": "libx264"}

# Write the cropped clip to the output file
cropped_clip.resize(height=output_size[1]).write_videofile(output_file, **output_format)



#for srt file
leopard = pvleopard.create(access_key="4nWg2kn7sSJd2A+d/cAHNCtuU7sA5y5U6b2/H2aqEX5d3592eXv7HA==")
transcript, words = leopard.process_file("combinedAudio.mp3")

with open("subtitles.srt", 'w') as f:
    f.write(to_srt(words))


# Load the video and subtitle files
video = VideoFileClip("croppedVideo.mp4")
subtitles = SubtitlesClip("subtitles.srt")

generator = lambda txt: TextClip(txt, font='courier-new-bold', method="caption", fontsize=50, color='orange', kerning=2, stroke_color="white", align="center")
subs = SubtitlesClip('subtitles.srt', generator)
subtitles = SubtitlesClip(subs, generator)

result = CompositeVideoClip([video, subtitles.set_position(("center", 0.7), relative=True)])

result.write_videofile("output.mp4")



