import openai
from gtts import gTTS
from googleapiclient.discovery import build
import re
from pytube import YouTube
from moviepy.video.io.VideoFileClip import VideoFileClip
import os
from mutagen.mp3 import MP3
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip



###### Get Text about the Game 
API_SECRET_KEY_OPENAI = "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"
retro_game = "League of Legends"

openai.api_key = API_SECRET_KEY_OPENAI

prompt = "Write a long Text for a video about " + retro_game

model = "text-davinci-003"
temperature = 0.9
max_tokens = 200


response = openai.Completion.create(prompt = prompt, model = model, temperature=temperature, max_tokens = max_tokens)

text = response["choices"][0]["text"]
print(text)

###### Text to Speech
speech = gTTS(text = text, lang = "en", slow = False, tld="co.uk")
speech.save(retro_game + ".mp3")



###### Get Youtube Snippets

# Set up the YouTube API client
api_key_youtube = 'AIzaSyBSTrU4CFKU-l6zH1tmSwA1n12UvU9JP50'
youtube = build('youtube', 'v3', developerKey = api_key_youtube)

# Search for videos related to "Super Mario Bros."
maxResults = 10
search_response = youtube.search().list(
    q= retro_game,
    type='video',
    part='id',
    maxResults= maxResults
).execute()

video_ids = [item['id']['videoId'] for item in search_response['items']]

# Retrieve information about the videos
video_info = youtube.videos().list(
        part='contentDetails',
        id=','.join(video_ids)
    ).execute()

    # Create a list to store the video links and lengths
video_list = []

for item in video_info['items']:
        # Extract the video ID and length
        video_id = item['id']
        duration = item['contentDetails']['duration']
        duration_seconds = int(re.search(r'\d+', duration).group())

        # Create the video URL
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Add the video link and length to the list
        video_list.append({'url': video_url, 'length': duration_seconds})

# Print the list of video links and lengths
print(video_list)

download_dir = "./videos"
for file in os.listdir(download_dir):
    file_path = os.path.join(download_dir, file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f'Error deleting file {file_path}: {e}')

#Download the videos
for link in video_list:
    # Set the URL of the YouTube video you want to download
    url = link["url"]

    # Create a YouTube object and get the highest resolution stream
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()

    # Download the video to the current working directory
    stream.download(download_dir)
    



####### JUST FOR FUN 


audio = MP3(retro_game + ".mp3")
video_length = audio.info.length /  maxResults

# directory containing the videos to be cut
video_dir = './videos'

# duration in seconds for the cut videos
cut_duration = video_length

# loop through all the videos in the directory
for filename in os.listdir(video_dir):
    if filename.endswith('.mp4'):
        # read the video file
        video = VideoFileClip(os.path.join(video_dir, filename))
        
        # cut the video to the desired duration
        cut_video = video.subclip(0, cut_duration).without_audio()
        
        # write the cut video to a new file
        cut_filename = 'cut_' + filename
        cut_video.write_videofile(os.path.join(video_dir, cut_filename))
        
video_clips = []
for filename in os.listdir(video_dir):
    if filename.endswith('.mp4') & filename.startswith("cut_"):
        # read the video file
        video_clip = VideoFileClip(os.path.join(video_dir, filename))
        
        # add the video clip to the list
        video_clips.append(video_clip)

# concatenate all the video clips
final_clip = concatenate_videoclips(video_clips)

# read the audio file
audio_file = AudioFileClip('./' + retro_game+".mp3")

# set the audio of the final clip to the audio file
final_clip = final_clip.set_audio(audio_file)

# write the final clip to a file
final_clip.write_videofile('./output.mp4', audio_codec='aac')








