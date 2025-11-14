import re

line = "2025-11-14 23:27:51,889 - frame-2391380INFO - frame=      ksfd16043 fps=135 q=30.7 size=    23552KiB time=00:10:41.64 bitrate= 300.7kbits/s speed=5.41x elapsed=0:01:58.56"

# Regular Expression Explanation:
# r'frame=\s*(\d+)'
# frame=     -> matches the literal text "frame="
# \s* -> matches zero or more whitespace characters (the optional space)
# (\d+)     -> matches one or more digits and captures them (this is the number you want)

match = re.search(r'frame=\s*(\d+)', line)

if match:
    # Group 1 (the parentheses in the regex) contains the captured digits
    curframe = int(match.group(1))
    print(f"The current frame is: {curframe}")
else:
    print("Frame information not found in the line.")

# Output:
# The current frame is: 16043
