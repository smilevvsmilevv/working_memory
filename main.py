import os
import sys
import csv
import tkinter as tk
import sounddevice as sd
from tkinter import messagebox, filedialog, Toplevel, scrolledtext, ttk, simpledialog
from datetime import datetime
from psychopy import sound, prefs
from digit_sets import digit_set1, digit_set2

VOLUME_FACTOR = 1

ENG_TITLE_FONT = "Calibri"
ENG_TEXT_FONT = "Calibri"

# ------- 리소스 경로 처리 -------
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

# 저장 경로 선택
def choose_folder():
    path = filedialog.askdirectory()
    if path:
        save_path.set(path)

# Manual 팝업
def open_manual():
    manual_window = Toplevel(root)
    manual_window.title("Manual")
    manual_window.geometry("700x500")

    manual_text = scrolledtext.ScrolledText(manual_window, wrap='word')
    manual_text.pack(expand=True, fill='both', padx=10, pady=10)

    try:
        with open(resource_path("manual.md"), "r", encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = "Manual 파일을 찾을 수 없습니다.'./manual.md' 파일을 생성해주세요."

    manual_text.insert('1.0', content)
    manual_text.config(state='disabled')

# ------- 저장 기능 -------
def save_data(digit_set_selected):
    global data_saved

    subj = participant_name.get().strip()
    path = save_path.get().strip()

    if not subj or not path:
        messagebox.showwarning("입력 필요", "Participant name과 Save path를 모두 입력해주세요.")
        return

    date_str = datetime.today().strftime("%Y-%m-%d")
    filename = f"{subj}_WM_{date_str}.csv"
    fullpath = os.path.join(path, filename)

    if os.path.exists(fullpath):
        messagebox.showerror("파일 중복", f"이미 동일한 이름의 파일이 존재합니다:\n{fullpath}")
        return

    try:
        with open(fullpath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Set", "Step", "DigitLength", "Answer", "Response", "Correct"])
            for key, (row_vars, checkvar) in response_widgets.items():
                parts = key.split('_')
                set_id = f"{parts[0]}_{parts[1]}"
                step = int(parts[2])
                answer = ''.join(str(d) for d in digit_set_selected[key])
                
                if parts[0] == "F":
                    response = ''.join(str(d) for i, d in enumerate(digit_set_selected[key]) if row_vars[i].get() == 1)
                else:
                    response = ''.join(str(d) for i, d in enumerate(reversed(digit_set_selected[key])) if row_vars[len(row_vars)-1-i].get() == 1)

                correct = int(checkvar.get())
                writer.writerow([set_id, step, len(answer), answer, response, correct])

        messagebox.showinfo("저장 완료", f"데이터가 저장되었습니다:\n{fullpath}")
        data_saved = True

    except Exception as e:
        messagebox.showerror("저장 실패", str(e))

# ------- 종료 전 확인 -------
def on_closing():
    if not data_saved:
        if messagebox.askyesno("종료 확인", "데이터를 저장하지 않았습니다. 정말 종료하시겠습니까?"):
            root.destroy()
    else:
        root.destroy()

# ------- play digit loop -------
def run_play_digit_loop(path_list, idx=0):
    global audio
    if idx >= len(path_list):
        return
    path = path_list[idx]
    prefs.hardware['audioDevice'] = selected_device.get()    
    audio = sound.Sound(path, volume=VOLUME_FACTOR)
    duration = audio.getDuration()
    audio.play()
    gap = 0.5 # second
    delay = int((duration + gap) * 1000)
    root.after(delay, lambda: run_play_digit_loop(path_list, idx+1))

# ------- get audio devices -------
def get_audio_devices():
    devices = sd.query_devices()
    output_devices = [device['name'] for i, device in enumerate(devices) if device['max_output_channels'] > 0]
    return output_devices

# ------- pop up for Name and Digit Set Selection -------
def initial_popup(root):
    popup = tk.Toplevel(root)
    popup.title("Name and Digit Set Selection")
    popup.geometry("300x250")
    popup.grab_set()

    tk.Label(popup, text="Participant Name", font=(ENG_TITLE_FONT, 14, "bold")).pack(pady=10)
    participant_input = tk.StringVar()
    tk.Entry(popup, textvariable=participant_input, width=20).pack(pady=5)

    tk.Label(popup, text="Select Digit Set", font=(ENG_TITLE_FONT, 14, "bold")).pack(pady=10)
    selected_set = tk.StringVar(value="digit_set1")

    tk.Radiobutton(popup, text="Digit Set 1", variable=selected_set, value="digit_set1").pack()
    tk.Radiobutton(popup, text="Digit Set 2", variable=selected_set, value="digit_set2").pack()


    def confirm_selection():
        if not participant_input.get():
            messagebox.showwarning("Input Required", "Please enter a participant name.")
            return
        
        popup.participant_input = participant_input.get()
        popup.digit_set = selected_set.get()
        popup.destroy()

    tk.Button(popup, text="Confirm", command=confirm_selection).pack(pady=20)
    root.wait_window(popup)

    return popup.participant_input, popup.digit_set

def toggle(btn, vars_list, check_var, check_btn):
    # check if ALL buttons in row are selected
    if all(v.get() == 1 for v in vars_list):
        check_var.set(1)
        check_btn.config(state="disabled")  # make read-only
    else:
        check_var.set(0)
        check_btn.config(state="normal")

prefs.hardware['audioLib'] = 'sounddevice'

# ------- 전역 상태 -------
data_saved = False
response_widgets = {}
base_path = resource_path("")

os.makedirs(base_path, exist_ok=True)


# ------- GUI 초기화 -------
root = tk.Tk()
root.withdraw()  # hide main window first

# ------- Participant name popup -------
participant_input, digit_set_input = initial_popup(root)

root.deiconify()  # show main window again

root.title("Digit-span test")
root.geometry("1650x500")

# ------- 상단 정보 입력 영역 -------
top_frame = tk.Frame(root)
top_frame.pack(fill='x', padx=10, pady=5)

top_frame.grid_columnconfigure(0, weight=0)
top_frame.grid_columnconfigure(1, weight=0)
top_frame.grid_columnconfigure(2, weight=0)
top_frame.grid_columnconfigure(3, weight=1)
top_frame.grid_columnconfigure(4, weight=0)
top_frame.grid_columnconfigure(5, weight=0)

participant_name = tk.StringVar(value=participant_input)

default_path = os.path.join(base_path, participant_name.get())
if not os.path.exists(default_path):
    os.makedirs(default_path, exist_ok=True)

save_path = tk.StringVar(value=default_path)

# Participant 입력
tk.Label(top_frame, text="Participant name:").grid(row=0, column=0, sticky='e')
tk.Entry(top_frame, textvariable=participant_name, width=30, state="readonly").grid(row=0, column=1, padx=2)

digit_set_selected = digit_set1 if digit_set_input == "digit_set1" else digit_set2

# Save path selection
tk.Label(top_frame, text="Save path:").grid(row=1, column=0, sticky='e')
tk.Label(top_frame, textvariable=save_path, fg='blue').grid(row=1, column=1, sticky='w')
tk.Button(top_frame, text="...", bg="lightgray", command=choose_folder).grid(row=1, column=2)

# Audio device selection
tk.Label(top_frame, text="Audio Device:").grid(row=0, column=4, sticky='e')
device_list = get_audio_devices()
selected_device = tk.StringVar()
device_dropdown = ttk.Combobox(top_frame, textvariable=selected_device, values=device_list, state="readonly", width=35)
device_dropdown.grid(row=0, column=5, padx=5, sticky='e')
if device_list:
    device_dropdown.current(0)

# Manual 버튼 활성화
tk.Button(top_frame, text="Manual", bg="lightgray", command=open_manual).grid(row=1, column=5, padx=5, pady=8, sticky='e')

# 제목
tk.Label(root, text="Digit-span test", font=("Helvetica", 16, "bold")).pack(pady=5)

# ------- 메인 테스트 영역 -------
main_frame = tk.Frame(root)
main_frame.pack()

set_categories = ["F_S1", "F_S2", "B_S1", "B_S2"]
column_titles = ["Forward\nSet1", "Forward\nSet2", "Backward\nSet1", "Backward\nSet2"]

for col, set_prefix in enumerate(set_categories):
    section = tk.LabelFrame(main_frame, text=column_titles[col], padx=5, pady=5)
    section.grid(row=0, column=col, padx=5, pady=5)

    tk.Label(section, text="Step", font=("Arial", 10, "bold"), width=4).grid(row=0, column=0, padx=1)
    tk.Label(section, text="Answer", font=("Arial", 10, "bold"), width=8).grid(row=0, column=1, padx=1)
    tk.Label(section, text="", width=5).grid(row=0, column=2)
    tk.Label(section, text="Response", font=("Arial", 10, "bold"), width=12).grid(row=0, column=3, columnspan=9, padx=1)
    tk.Label(section, text="Correct?", font=("Arial", 10, "bold"), width=6).grid(row=0, column=12)

    relevant_keys = [k for k in digit_set_selected if k.startswith(set_prefix)]

    relevant_keys.sort(key=lambda x: int(x.split('_')[2]))

    for r, key in enumerate(relevant_keys, start=1):
        step = key.split('_')[2]
        answer_str = ''.join(str(d) for d in digit_set_selected[key])

        audio_path_list = []

        # Add the digit audio files paths to the list
        for digit in digit_set_selected[key]:
            audio_path_list.append(resource_path(os.path.join("wav", "digits_wav", f"{digit}.wav")))

        # Add a beep sound file path at the end
        audio_path_list.append(resource_path(os.path.join("wav", "digits_wav", "beep_freq700Hz_dur0p5s_rms0p08_mono.wav")))

        tk.Label(section, text=step, width=4).grid(row=r, column=0, padx=1, pady=2)
        tk.Label(section, text=answer_str, width=8).grid(row=r, column=1, padx=1, pady=2)
        tk.Button(section, text="▶", width=2, bg="lightgray", command=lambda pathlist=audio_path_list: run_play_digit_loop(pathlist)).grid(row=r, column=2, padx=1, pady=2)

        check_var = tk.IntVar()
        check_btn = tk.Checkbutton(section, variable=check_var)
        check_btn.grid(row=r, column=12)
        
        row_vars = []
        
        for idx_digit, digit in enumerate(digit_set_selected[key]):
            var = tk.IntVar()
            row_vars.append(var)

            btn = tk.Checkbutton(
                section,
                variable=var,
                text=digit,
                indicatoron=False,
                bg="SystemButtonFace",
                selectcolor="green",
            )
            btn.var = var
            btn.config(
                command=lambda b=btn, vars_list=row_vars, cv=check_var, cb=check_btn: toggle(b, vars_list, cv, cb)
            )

            if set_prefix.startswith("F"):
                column_index = 3 + idx_digit
            else:
                column_index = 11 - idx_digit - (9 - len(digit_set_selected[key]))

            btn.grid(row=r, column=column_index, padx=1, pady=2)

        response_widgets[key] = (row_vars, check_var)

# ------- 저장 버튼 -------
tk.Button(root, text="SAVE DATA", font=("Arial", 12, "bold"), width=25, height=2, bg="#afc4bf", command=lambda: save_data(digit_set_selected)).pack(pady=20)

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
