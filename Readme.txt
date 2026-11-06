Date: 2026/11/06
Writer: 위위

File
working memory
ㄴ AMW 0. Digits wav (timing revised) X not use X
ㄴ wav
     ㄴ digits_wav
           ㄴ 0.wav
           ㄴ ...
           ㄴ 9.wav
           ㄴ beep_freq700Hz_dur0p5s_rms0p08_mono.wav
     ㄴ sp_angelina X not use X
ㄴ digit_sets.py
ㄴ main.py
ㄴ manual.md
ㄴ Readme.txt


Code Description

1. Volume Adjustment (main.py)
ㄴ VOLUME_FACTOR = 1 is used to digitally adjust the audio volume.
ㄴ Increase or decrease this value to adjust the playback volume as needed.

2. Participant Name and Saving Path
ㄴ After entering the participant's name, a folder with the same name will be automatically created.
ㄴ This folder will be set as the default saving path for the participant's data.
ㄴ You can change the saving folder later within the program.

3. Audio Playback (run_play_digit_loop)
ㄴ The gap between consecutive digits is set to 0.5 seconds.
ㄴ This interval is intentionally set to 0.5 seconds because each digit audio file has a 0.5-second offset at the beginning.
ㄴ Therefore, setting the gap to 0.5 seconds provides approximately 1 second of silence between the onset of consecutive digits.