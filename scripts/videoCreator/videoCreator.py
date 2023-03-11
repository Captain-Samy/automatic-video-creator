from datetime import datetime, timedelta
import os
import sys
import openai
from pyparsing import Sequence
from pytube import YouTube
from pydub import AudioSegment
from moviepy.video.io.VideoFileClip import VideoFileClip
from mutagen.mp3 import MP3
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from elevenlabslib import ElevenLabsUser
from pydub import AudioSegment
import io
import pvleopard
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.config import change_settings
from yt_dlp import YoutubeDL
from googleapiclient.discovery import build
from gtts import gTTS


#For ImageMagick Idk what it does but idc
change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.0-Q16-HDRI\\magick.exe"})


def videoCreator(topic, videoLink, themeLink, openAiApiKey, tts, videoStartTime, themeStartTime):
    #create srt files from text
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
            lines.append(word.word.upper() + '\n')
            return word.end_sec
            
        lines = []
        section = 1
        prev_end = 0.0
        for word in words:
            prev_end = _helper(word, prev_end)
            section += 1

        return '\n'.join(lines)

    #Settings for Testing 
    themeStart = int(themeStartTime)
    videoStart = int(videoStartTime)

    ###### Text Creation with OpenAI ChatGPT
    openai.api_key = openAiApiKey
    model = "text-davinci-003"
    temperature = 0.9
    max_tokens = 500
    response = openai.Completion.create(prompt = topic, model = model, temperature=temperature, max_tokens = max_tokens)
    text = response["choices"][0]["text"]
    print("--> Openai Text generated")

    if tts == "false" :
        ###### Text to Speech with Elevenlabs
        user = ElevenLabsUser("50053dae449db964a829c6dda45034ce") #fill in your api key as a string
        voice = user.get_voices_by_name("Josh")[0]  #fill in the name of the voice you want to use. ex: "Rachel"
        voice_bytes = voice.generate_audio_bytes(text) #fill in what you want the ai to say as a string
        speech_audio = AudioSegment.from_file_using_temporary_files(io.BytesIO(voice_bytes))
        speech_audio.export("speech.mp3", format="mp3")
        print("--> Text to Speech Audo generated with elevenlabs")

    else:
        speech_audio = gTTS(text = text, lang = "en", slow = False, tld="co.uk")
        speech_audio.save("speech.mp3")
        speech_audio = AudioSegment.from_file("speech.mp3")
        print("--> Text to Speech Audo generated with gtts")


    audio = YouTube(themeLink)
    audio_stream = audio.streams.filter(only_audio=True).first()
    audio_stream.download(filename="backgroundAudio.mp3",)
    background_audio = AudioSegment.from_file("backgroundAudio.mp3")
    print("--> BackgroundAudio downloadet")


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
    print("--> CombinedAudio created")

    ###### Get Youtube Video

    # Create a YouTube object and get the highest resolution stream
    os.remove("video.mp4")
    ydl_opts = {
    'format': 'bestvideo[ext=mp4][ext=mp4]',
    'outtmpl': 'video.mp4',
    'postprocessors': [],
    'no_post_overwrites': True,
    'allsubtitles': False,
    'nooverwrites': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([videoLink])
    print("--> Youtube Video downloadet")
    audioLength = MP3("speech.mp3")
    cutVideo = VideoFileClip("video.mp4").subclip(int(videoStart), int(videoStart) + audioLength.info.length).without_audio()
    cutVideo = cutVideo.set_audio(AudioFileClip("combinedAudio.mp3"))
    cutVideo.write_videofile("cutVideo.mp4")
    print("--> Cutted Video to length")

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
    print("--> Cropped Video to Mobile Size")


    #for srt file
    leopard = pvleopard.create(access_key="4nWg2kn7sSJd2A+d/cAHNCtuU7sA5y5U6b2/H2aqEX5d3592eXv7HA==")
    transcript, words = leopard.process_file("combinedAudio.mp3")

    with open("subtitles.srt", 'w') as f:
        f.write(to_srt(words))
    print("--> Created srt file")
    
    ### Function to Improve SRT File
    def combine_short_subtitles(srt_file):
        with open(srt_file, 'r') as file:
            srt_content = file.read()

        # Split the content into subtitle blocks
        subtitle_blocks = srt_content.strip().split('\n\n')

        # Initialize variables to store combined blocks and time period
        combined_blocks = []
        start_time = None
        end_time = None

        for block in subtitle_blocks:
            print(block)
            
            # Split the block into lines
            lines = block.split('\n')

            # Extract the time period from the first line
            time_str = lines[1]
            start_time_str, end_time_str = time_str.split(' --> ')

            # Convert time strings to datetime objects
            start_time = datetime.strptime(start_time_str, '%H:%M:%S,%f')
            end_time = datetime.strptime(end_time_str, '%H:%M:%S,%f')

            # Combine subtitle blocks that are shorter than 13 characters
            if len(combined_blocks) > 0:
                if lines[2] and len(combined_blocks[-1]) + len(lines[2]) + 1 < 8:
                    # If the last block can be combined with the current block, append the current block to it
                    combined_blocks[-1][0] += ' ' + lines[2]
                    # Update the end time to cover the duration of the combined blocks
                    end_time = end_time + timedelta(seconds=(len(lines[2])+1)/1000)
                    last_index = len(combined_blocks)-1
                    combined_blocks[last_index].append(start_time)
                    combined_blocks[last_index].append(end_time)
                else:
                    if len(combined_blocks) > 1:
                        last_index = len(combined_blocks)-1
                        combined_blocks.append([lines[2], combined_blocks[last_index][2], end_time])
                    else:
                        # Otherwise, add a new combined block
                        combined_blocks.append([lines[2], start_time, end_time])
            else:
                # Otherwise, add a new combined block
                combined_blocks.append([lines[2], start_time, end_time])

 

        # Build the new SRT content with combined blocks and updated time period
        new_srt_content = ''
        for i in range(len(combined_blocks)):
            new_srt_content += str(i + 1) + '\n'
            new_srt_content += combined_blocks[i][1].strftime('%H:%M:%S,%f') + ' --> '
            new_srt_content += combined_blocks[i][2].strftime('%H:%M:%S,%f') + '\n'
            new_srt_content += combined_blocks[i][0] + '\n\n'
            # Update the start time to cover the duration of the previous combined blocks
            start_time = end_time + timedelta(milliseconds=1)


        return new_srt_content
    
    srt = combine_short_subtitles("subtitles.srt")
    with open("subtitles.srt", 'w') as f:
        f.write(srt)
    

    # Load the video and subtitle files
    video = VideoFileClip("croppedVideo.mp4")

    font_size = int(min(video.h, 1920) / 20) #Important because fontsize has to be variable compared to the video quality
    generator = lambda txt: TextClip(txt, font='Arial-Black', method="label", fontsize=font_size-5, color='orange', kerning=0, stroke_color="black")
    subs = SubtitlesClip('subtitles.srt', generator)
    subtitles = SubtitlesClip(subs, generator)

    result = CompositeVideoClip([video, subtitles.set_position(("center", 0.7), relative=True)])

    result.write_videofile("output.mp4")
    print("************************************")
    print("************************************")
    print("********** Video finished **********")
    print("************************************")
    print("************************************")
    
    #Delete files afterwards
    os.remove("backgroundAudio.mp3")
    os.remove("combinedAudio.mp3")
    os.remove("croppedVideo.mp4")
    os.remove("cutVideo.mp4")
    os.remove("speech.mp3")


#run the script
videoCreator(topic = sys.argv[1], videoLink=sys.argv[2], themeLink=sys.argv[3], openAiApiKey = sys.argv[4], tts = sys.argv[5], videoStartTime = sys.argv[6], themeStartTime = sys.argv[7])