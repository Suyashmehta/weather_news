import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import io
import speech_recognition as sr
import pyttsx3

# pyttsx3 voice engine
engine = pyttsx3.init()
engine.setProperty("rate", 145)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")
for i, voice in enumerate(voices):
    print(f"{i} - {voice.name}")
# :1 voice 
engine.setProperty("voice", voices[1].id)

root = tk.Tk()
root.title("Weather & News App")
root.geometry("700x800")
root.configure(bg="#000000")

# Global variables
current_icon = None
weather_frame = None
news_frame = None

# main menu
def show_menu():
    clear_frames()
    tk.Label(root, text="Select Weather or News", font=("Arial", 20, "bold"), bg="#c0c0c0", fg="black").pack(pady=30)
    tk.Button(root, text="Weather", command=show_weather_ui,
            bg="#0d6efd", fg="black", font=("Arial", 14, "bold"), width=20).pack(pady=20)
    tk.Button(root, text="News", command=show_news_ui,
            bg="#ff5733", fg="black", font=("Arial", 14, "bold"), width=20).pack(pady=20)

# Clear all frames
def clear_frames():
    global weather_frame, news_frame
    if weather_frame:
        weather_frame.destroy()
    if news_frame:
        news_frame.destroy()
    for widget in root.winfo_children():
        if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
            widget.destroy()

#weather function
def show_weather_ui():
    global weather_frame
    clear_frames()
    weather_frame = tk.Frame(root, bg="#000000")
    weather_frame.pack(fill="both", expand=True)

    tk.Label(weather_frame, text="Enter City Name:", font=("Arial", 15, "bold"),
             bg="#129a61", fg="black").pack(pady=15)

    city_entry = tk.Entry(weather_frame, font=("Arial", 15))
    city_entry.pack(pady=8)

    weather_label = tk.Label(weather_frame, text="", font=("Arial", 12),
                             bg="#f0f8ff", width=45, height=5, wraplength=400)
    weather_label.pack(pady=10)

    icon_label = tk.Label(weather_frame, bg="#000f1c")
    icon_label.pack(pady=10)

    def set_alert(temp, condition):
        condition_lower = condition.lower()
        if "rain" in condition_lower or "storm" in condition_lower:
            weather_label.config(bg="red", fg="white")
        elif temp > 40:
            weather_label.config(bg="red", fg="white")
        elif 30 <= temp <= 40:
            weather_label.config(bg="yellow", fg="black")
        elif 20 <= temp < 30:
            weather_label.config(bg="green", fg="white")
        else:
            weather_label.config(bg="cyan", fg="black")

    def get_weather():
        nonlocal city_entry, weather_label, icon_label
        global current_icon
        city = city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input error !!", "Please enter a city name")
            return

        try:
            api_key = "a36fa0d3564b48a9e41bedfcc9435be0"   # <-- Apna OpenWeather API key yaha daalna
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            res = requests.get(url)
            data = res.json()

            if str(data.get("cod")) != "200":
                messagebox.showerror("Error", f"City not found: {city}")
                return

            temp = data["main"]["temp"]
            condition = data["weather"][0]["description"]
            icon_code = data["weather"][0]["icon"]

            weather_label.config(text=f"{city}\nTemperature: {temp}°C\nCondition: {condition}")
            set_alert(temp, condition)

            # Fetch icon
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            icon_res = requests.get(icon_url)
            icon_img = Image.open(io.BytesIO(icon_res.content)).convert("RGBA")
            current_icon = ImageTk.PhotoImage(icon_img)
            icon_label.config(image=current_icon)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get weather: {e}")

    def speak_city():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            messagebox.showinfo("Speak", "Please say the city name")
            try:
                audio = recognizer.listen(source, timeout=5)
                city_name = recognizer.recognize_google(audio)
                city_entry.delete(0, tk.END)
                city_entry.insert(0, city_name)
                get_weather()
            except Exception as e:
                messagebox.showerror("Error", f"Could not recognize voice: {e}")

    tk.Button(weather_frame, text="Get Weather", command=get_weather,
              bg="#0d6efd", fg="black", font=("Arial", 12, "bold")).pack(pady=5)
    tk.Button(weather_frame, text="Speak City", command=speak_city,
              bg="#28a745", fg="black", font=("Arial", 12, "bold")).pack(pady=5)
    tk.Button(weather_frame, text="Back to Menu", command=show_menu,
              bg="#444", fg="white", font=("Arial", 12, "bold")).pack(pady=15)

# news section
def show_news_ui():
    global news_frame
    clear_frames()
    news_frame = tk.Frame(root, bg="#000000")
    news_frame.pack(fill="both", expand=True)

    tk.Label(news_frame, text="Enter Country Code or Keyword (e.g., in, us, world, technology):",
             font=("Arial", 12, "bold"), bg="#c0c0c0", fg="black").pack(pady=10)

    query_entry = tk.Entry(news_frame, font=("Arial", 14))
    query_entry.pack(pady=8)

    tk.Label(news_frame, text="Top News Headlines", font=("Arial", 15, "bold"),
             bg="#129a61", fg="white").pack(pady=10)

    # Text Box (news)
    text_frame = tk.Frame(news_frame)
    text_frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")

    news_box = tk.Text(text_frame, wrap="word", font=("Arial", 12),
                       bg="#000000", fg="white", yscrollcommand=scrollbar.set)
    news_box.pack(fill="both", expand=True)
    scrollbar.config(command=news_box.yview)

    def get_news():
        news_box.delete(1.0, tk.END)
        query = query_entry.get().strip()

        if not query:
            messagebox.showwarning("Input Error", "Please enter a country code or keyword")
            return

        try:
            api_key = "af1e033f6b2f46e2a2ec5e3f2d89b2d3"   # <-- Apna NewsAPI key yaha daalna
            if len(query) == 2:
                url = f"https://newsapi.org/v2/top-headlines?country={query}&apiKey={api_key}"
            else:
                url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"

            res = requests.get(url)
            data = res.json()

            if data.get("status") != "ok":
                messagebox.showerror("Error", "Failed to fetch news")
                return

            articles = data["articles"][:5]  # Top 5 news

            for i, article in enumerate(articles, start=1):
                headline = article.get("title", "No Title")
                desc = article.get("description", "")

                news_box.insert(tk.END, f"{i}. {headline}\n", "headline")
                if desc:
                    news_box.insert(tk.END, f"   {desc}\n\n")

                engine.say(headline)  # speak headlines

            engine.runAndWait()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get news: {e}")

    tk.Button(news_frame, text="Get News", command=get_news,
              bg="#ff5733", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
    tk.Button(news_frame, text="Back to Menu", command=show_menu,
              bg="#444", fg="white", font=("Arial", 12, "bold")).pack(pady=15)

# Start with menu
show_menu()
root.mainloop()
