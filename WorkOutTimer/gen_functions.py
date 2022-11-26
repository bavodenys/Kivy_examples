# Function to convert duration in seconds -> mm:ss
def convert_s_to_min_s_str(dur_s):
    minutes = int(dur_s/60)
    seconds = int(dur_s%60)
    result = f'{minutes:02d}:{seconds:02d}'
    return result
