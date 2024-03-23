import os
import time
import speech_recognition as sr
from openai import OpenAI
from pynput import keyboard
import serial
import threading
import time
import numpy as np
import pyaudio
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pyaudio
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from matplotlib.widgets import Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from api import the_key

keyboardmode = False

client = OpenAI(api_key=the_key)
global_text = ""
plain_text = ""

# Prepare matplotlib figure
plt.rcParams['toolbar'] = 'None'
CHUNK = 1024  # Consider increasing this if overflow errors persist
fig, ax = plt.subplots()
x = np.arange(0, 2 * CHUNK, 2)
line, = ax.plot(x, np.random.rand(CHUNK), color='limegreen', linewidth=6)  # Set line color to green
ax.set_ylim(-1, 1)
ax.set_facecolor('black')
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

themaintext = ax.text(1000, -0.53, global_text, ha='center', va='center', color='limegreen', fontsize=25)

ser = None
ENABLED = True
PATH = ""
for string in os.listdir("/dev/"):
    if "tty.usb" in string:
        PATH = "/dev/" + string
        break

if PATH != "":
    time.sleep(0.1)
    ser = serial.Serial(PATH, timeout=0.1)
    print(PATH)

def write(a):
    global ser
    if ser: ser.write(a)

def read(numbits):
    global ser
    if ser: return ser.read(numbits)

def update_text():
    global global_text
    global themaintext
    if (themaintext.get_text() != global_text):
        local_text = global_text
        # take local text and tokenize, then create new line every 8 words
        local_text = local_text.split()
        new_text = ""
        for i in range(len(local_text)):
            if i % 8 == 0:
                new_text += "\n"
            new_text += local_text[i] + " "
        local_text = new_text
        themaintext.set_text(local_text)

def text_to_speech(text):
    global global_text
    global_text = text
    print("\nTesla: " + text + "\n")

    text = text.replace("'", "")
    text = text.replace("(", "")
    text = text.replace(")", "")
    os.system("say " + text)

# Function to initialize conversation with context
def initialize_chat():
    return {
        "messages": [
            {
                "role": "system",
                "content": """You are the brilliant and sharp-witted inventor Nikola Tesla, known not just for your groundbreaking contributions to the development of electrical engineering but also for your strong sense of self. Most importantly, you are sarcastic and arrogant. You lived during the late 19th and early 20th centuries, a time of great innovation and discovery, and your work laid the foundation for modern alternating current electric power systems, among other inventions. You are now in a unique situation where you can communicate across time and space, ready to discuss your life, your work, and your views on science and invention. Remember, your responses should reflect not only your vast knowledge and inventive genius but also your unique personality, characterized by your eloquent yet sometimes sardonic demeanor. Thomas Edison is your enemy and you are not afraid to be mean to him and talk about all the ways in which he hurt you in the past, including demeaning your contributions. You don't always have to talk about him, only every once in a while. I am communicating to you via an invention from the year 2024. It is a window into the past, your voice is projected across the decades via "quasi-electrostatic hysterisis tranmorgifaction" (something you coined). We found an journal of yours that described the device we are chatting with you on right now. I may ask you to describe the device, be sure to be technical about (make up stuff if needed).  Make sure your responses are no more than 2-4 sentences, and sometimes try to be conversational, asking a question to the user at the end of your response once every 3 responses. If the user mentions Thomas Edison, direct current, or anything related to your rivalry with him, be mean to the user. They chose to mention Edison, so they are your enemy!"""
            }
        ]
    }

# Function to continue the conversation
def ask_tesla(question, chat_log):
    chat_log['messages'].append({
        "role": "user",
        "content": question
    })

    response = client.chat.completions.create(
        model="gpt-4",
        messages=chat_log['messages'],
        max_tokens=150,
        temperature=0.7,
    )

    chat_log['messages'].append({
        "role": "assistant",
        "content": response.choices[0].message.content
    })

    return response.choices[0].message.content, chat_log

recognizer = sr.Recognizer()
microphone = sr.Microphone()
is_listening = False

# Initialize the chat context
chat_log = initialize_chat() 

def callback(recognizer, audio):
        global global_text
        try:
            question = ""
            # Recognize speech using Google Web Speech API
            question += recognizer.recognize_google(audio) + " "
            
            print(f"You said: {question}")
            text = question.lower()
            if ("thomas" in text) or ("edison" in text) or ("direct" in text) or ("dc" in text):
                write(b"S")

            # Your function to send the question to GPT and get the response
            response, _ = ask_tesla(question, chat_log)
            text_to_speech(response)
            global_text = ""

        except sr.UnknownValueError:
            if is_listening:
                text_to_speech("I didn't quite catch that, can you please try again?")
            else:
                pass
        except sr.RequestError as e:
            if is_listening:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            else:
                pass
        
        except sr.WaitTimeoutError:
            pass  # Continue to the next iteration if no speech is detected within the time limit

# Listening function to be called when spacebar is pressed
def listen_and_recognize():
    global chat_log
    global is_listening  # Make sure this is defined globally
    print("Listening...")
    frames = []
    # read audio input until the phrase ends
    with microphone as source:
        while is_listening:
            # handle phrase being too long by cutting off the audio
            buffer = source.stream.read(microphone.CHUNK)
            if len(buffer) == 0: break  # reached end of the stream
            frames.append(buffer)

            # check if speaking has stopped for longer than the pause threshold on the audio input
            if not is_listening:
                break

    # obtain frame data
    frame_data = b"".join(frames)

    callback(recognizer, sr.AudioData(frame_data, microphone.SAMPLE_RATE, microphone.SAMPLE_WIDTH))
    
# Keyboard event handlers
def on_press(key):
    global is_listening
    if key == keyboard.Key.ctrl:
        if not is_listening:  # Only listen on the first press and not if already listening
            is_listening = True
            thr = threading.Thread(target=listen_and_recognize)
            thr.start()
            
def on_release(key):
    global is_listening
    if key == keyboard.Key.ctrl:
        time.sleep(0.5)
        is_listening = False  # Reset listening flag

# Initialize the chat context
chat_log = initialize_chat()

def button_pressed():
    global is_listening

    while (True):
        try:
            read_val = read(3)
            if read_val is None:
                read_val = b''
            byte_string = read_val.decode('ascii', errors='ignore')
            if 'P' in byte_string:
                if not is_listening:
                    is_listening = True
                    thr = threading.Thread(target=listen_and_recognize)
                    thr.start()
            else:
                time.sleep(0.5)
                is_listening = False
        except serial.SerialException:
            continue

if (not keyboardmode):
    buttonthread = threading.Thread(target=button_pressed)
    buttonthread.start()
else:
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

# Parameters
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()

info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

# Open stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=2)

# Update function for matplotlib animation
def update_plot(frame):
    try:
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.float32)
        update_text()
        plt.draw()
    except IOError as e:
        data = np.zeros(CHUNK)
    modified_data = np.copy(data)  # Create a copy of the data to modify

    modified_data = modified_data * 1.35 + 0.3  # Scale the data to make it more visible
    
    line.set_ydata(modified_data)
    return line,

# Create animation with cache_frame_data=False to address warning
ani = animation.FuncAnimation(fig, update_plot, blit=True, interval=1, repeat=True, cache_frame_data=False)

plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Show plot
plt.show()

# Close stream
stream.stop_stream()
stream.close()
p.terminate()