#!/bin/bash

# == Config ==
if [ -z "$1" ]; then
    echo "<!> No input directory given"
    echo "    Command usage: $0 <input_dir> <output_dir> [quality]"
    echo "    Quality can be low, medium or high"
    exit 2
elif [ -z "$2" ]; then
    echo "<!> No output directory given"
    echo "    Command usage: $0 <input_dir> <output_dir> [quality]"
    echo "    Quality can be low, medium or high"
    exit 3
fi

file="$1"
originaloutfile="$2"

# Skip if input not exists
if [[ ! -f "$file" ]]; then
    echo 'Input file missing'
    exit 7
fi

# == Quality ==
if [[ -z "$3" || "$3" == "medium" ]]; then
    CRF=21
    PRESET="fast"
    AQ_MODE="3"
    BITRATE="160k"
elif [[ "$3" == "high" ]]; then
    CRF=18
    PRESET="medium"
    AQ_MODE="3"
    BITRATE="192k"
elif [[ "$3" == "low" ]]; then
    CRF=23
    PRESET="faster"
    AQ_MODE="2"
    BITRATE="128k"
else
    echo "<!> Not a valid quality setting. Please use the following:"
    echo "      \"low\", \"medium\" or \"high\" "
    echo "    Command usage: $0 <input_dir> <output_dir> [quality]"
    exit 4
fi

# == Processing ==
filename=$(basename "$file")
outfile="${originaloutfile%.*}.mkv"

# Skip if not enough space
FILE_SIZE_MB=$(du -m "$file" 2>/dev/null | awk '{print $1}')
AVAILABLE_SPACE_MB=$(df -m "$file" 2>/dev/null | awk 'NR==2 {print $4}')

if [ -z "$FILE_SIZE_MB" ] || [ -z "$AVAILABLE_SPACE_MB" ] || (( AVAILABLE_SPACE_MB < FILE_SIZE_MB )); then
    echo "<!> NO SPACE LEFT"
    exit 5
fi

# Skip if out exists
if [[ -f "$outfile" ]]; then
    echo "<!> Skipping $filename (already exists)"
    echo ""
fi

# == Audio Mapping ==
AUDIO_MAP="-map 0:a:0" # Default to first audio stream
if ffprobe -v error -select_streams a -show_entries stream_tags=language -of default=noprint_wrappers=1:nokey=1 "$file" | grep -q 'eng'; then
    AUDIO_MAP="-map 0:a:m:language:eng" # Select English if found
fi

# == Subtitle Mapping ==
SUBTITLE_MAP="" # Default to no subtitles
if ffprobe -v error -select_streams s -show_entries stream_tags=language -of default=noprint_wrappers=1:nokey=1 "$file" | grep -q 'eng'; then
    SUBTITLE_MAP="-map 0:s:m:language:eng"
fi

ffmpeg -hide_banner -loglevel info -stats -progress pipe:1 \
    -i "$file" \
    -map 0:v:0 \
    $AUDIO_MAP \
    $SUBTITLE_MAP \
    -c:v libx265 -preset "$PRESET" -crf "$CRF" -x265-params "aq-mode=$AQ_MODE" \
    -c:a aac -b:a 192k \
    -c:s copy \
    "$outfile" \

if [[ $? -eq 0 ]]; then
    echo "Done: $filename"

    input_size=$(stat -c%s "$file")
    output_size=$(stat -c%s "$outfile")
    input_mb=$(bc <<< "scale=2; $input_size/1048576")
    output_mb=$(bc <<< "scale=2; $output_size/1048576")
    ratio=$(bc <<< "scale=2; 100- ($output_mb/$input_mb*100)")

    echo "Original: ${input_mb}MB"
    echo "Compressed: ${output_mb}MB"
    echo "Reduced by: ${ratio}%"

    # Replace if bigger than original
    if [[ output_size -gt input_size ]]; then
        echo "<!> Output bigger than input, replacing with input"
        rm "$outfile"
        cp "$file" "$originaloutfile"
    fi

else
    echo "<!> Error processing $filename - check log for details."
    echo "normally due to force quit from user (ctrl c)"
    exit 6
fi
