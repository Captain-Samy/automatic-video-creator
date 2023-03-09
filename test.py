from datetime import datetime, timedelta

def combine_short_subtitles(srt_file):
    with open(srt_file, 'r') as file:
        srt_content = file.read()

    # Split the content into subtitle blocks
    subtitle_blocks = srt_content.strip().split('\n\n')

    # Initialize variables to store combined blocks and time period
    combined_blocks = []
    start_time = None
    end_time = None
    pusher = 0

    for block in subtitle_blocks:
        
        # Split the block into lines
        lines = block.split('\n')

        # Extract the time period from the first line
        time_str = lines[1]
        start_time_str, end_time_str = time_str.split(' --> ')

        # Convert time strings to datetime objects
        start_time = datetime.strptime(start_time_str, '%H:%M:%S,%f')
        end_time = datetime.strptime(end_time_str, '%H:%M:%S,%f')

        # Combine subtitle blocks that are shorter than 13 characters
        
        ### Workaround
        print(lines) 
        try:
            current_line = lines[2]
        except:
            current_line = lines[3]
            pusher = pusher + 1
        ###


        
        if combined_blocks and len(combined_blocks[-1]) + len(lines[2]) + 1 < 8:
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
with open("subtitlesTest.srt", 'w') as f:
    f.write(srt)