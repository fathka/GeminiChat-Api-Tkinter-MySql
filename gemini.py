import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
from datetime import datetime
import google.generativeai as genai
from random import random, randrange
import os

class GeminiChatBot:
    def __init__(self):
        try:
            api_key = "AIzaSyDwKimiIa2N9iCByoEiNXG_tB6TifDah8w"

            genai.configure(api_key=api_key)
            
            self.temperature = 0
            self.top_p = 0
            self.top_k = 1
            
            self._reset_model()
            
        except Exception as e:
            messagebox.showerror("API Initialization Error", f"Could not initialize Gemini API: {e}")
            raise

    def send_message(self, message, chat_history_text):
        try:
            response = self.chat.send_message(message)
            timestamp = datetime.now().strftime("%H:%M")
            
            chat_history_text.config(state=tk.NORMAL)
            chat_history_text.insert(tk.END, f"You ({timestamp}): {message}\n", "user")
            chat_history_text.insert(tk.END, f"Gemini ({timestamp}): {response.text}\n", "bot")
            chat_history_text.config(state=tk.DISABLED)
            chat_history_text.see(tk.END)
            
            return response.text
        except Exception as e:
            messagebox.showerror("Message Send Error", f"Could not send message: {e}")
            return None

    def _reset_model(self):
        generation_config = genai.GenerationConfig(
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k
        )
        self.model = genai.GenerativeModel('gemini-pro', generation_config=generation_config)
        self.chat = self.model.start_chat(history=[])

    def change_temperature(self):
        try:
            self.temperature = random()
            self._reset_model()
            return f"Temperature changed to {self.temperature:.2f}"
        except Exception as e:
            messagebox.showerror("Temperature Change Error", str(e))

    def change_top_k(self):
        try:
            self.top_k = randrange(40) + 1
            self._reset_model()
            return f"Top K changed to {self.top_k}"
        except Exception as e:
            messagebox.showerror("Top K Change Error", str(e))

    def change_top_p(self):
        try:
            self.top_p = random()
            self._reset_model()
            return f"Top P changed to {self.top_p:.2f}"
        except Exception as e:
            messagebox.showerror("Top P Change Error", str(e))

    def max_randomness(self):
        try:
            self.temperature = 1
            self.top_p = 1
            self.top_k = 40
            self._reset_model()
            return "Maximum randomness set"
        except Exception as e:
            messagebox.showerror("Randomness Change Error", str(e))

    def save_chat_history(self, username):
        try:
            filename = f'chat_history_{username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            with open(filename, 'w', encoding='utf-8') as file:
                for message in self.chat.history:
                    file.write(f"{message.role}: {message.parts[0].text}\n")
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save chat history: {e}")
            return False

class DatabaseManager:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'gemini_chat')
            )
            self.cursor = self.conn.cursor(dictionary=True)
            self.create_tables()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Could not connect to database: {err}")
            raise

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

    def create_tables(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            self.cursor.execute(create_table_query)
            self.conn.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Table Creation Error", f"Could not create tables: {err}")

    def register_user(self, username, password):
        try:
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            self.cursor.execute(query, (username, password))
            self.conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False

    def authenticate_user(self, username, password):
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        self.cursor.execute(query, (username, password))
        return self.cursor.fetchone() is not None

class ChatInterface:
    def __init__(self, username):
        self.username = username
        self.root = tk.Tk()
        self.root.title(f"Gemini Chat - {username}")
        self.root.geometry("800x600")
                
        try:
            self.chatbot = GeminiChatBot()
            self.setup_gui()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Could not initialize chat interface: {e}")
            self.root.destroy()
            return

    def setup_gui(self):
        # Chat history display
        self.setup_chat_history()
        
        # Message input
        self.setup_message_input()
        
        # Control buttons
        self.setup_control_buttons()
        
        # Start main loop
        self.root.mainloop()

    def setup_chat_history(self):
        chat_history_frame = tk.Frame(self.root)
        chat_history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.chat_history_text = tk.Text(chat_history_frame, state=tk.DISABLED, wrap=tk.WORD)
        self.chat_history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(chat_history_frame, command=self.chat_history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_history_text.config(yscrollcommand=scrollbar.set)

        # Configure text tags
        self.chat_history_text.tag_config("user", foreground="blue")
        self.chat_history_text.tag_config("bot", foreground="green", font=("Arial", 10, "italic"))
        self.chat_history_text.tag_config("system", foreground="red", font=("Arial", 10, "bold"))

    def setup_message_input(self):
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.message_entry = tk.Entry(input_frame, font=("Arial", 12))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_entry.bind('<Return>', lambda e: self.send_message())

        send_button = tk.Button(input_frame, text="Send", command=self.send_message,
                              font=("Arial", 12), bg="#007BFF", fg="white")
        send_button.pack(side=tk.LEFT)

    def setup_control_buttons(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        buttons = [
            ("Save History", self.save_history),
            ("Change Temp", self.change_temp),
            ("Change TopK", self.change_top_k),
            ("Change TopP", self.change_top_p),
            ("Max Random", self.max_randomness)
        ]

        for text, command in buttons:
            tk.Button(control_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)

    def send_message(self):
        message = self.message_entry.get().strip()
        if not message:
            messagebox.showwarning("Input Error", "Message cannot be empty!")
            return

        self.chatbot.send_message(message, self.chat_history_text)
        self.message_entry.delete(0, tk.END)

    def show_system_message(self, message):
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_history_text.config(state=tk.NORMAL)
        self.chat_history_text.insert(tk.END, f"System ({timestamp}): {message}\n", "system")
        self.chat_history_text.config(state=tk.DISABLED)
        self.chat_history_text.see(tk.END)

    def save_history(self):
        if self.chatbot.save_chat_history(self.username):
            messagebox.showinfo("Success", "Chat history saved successfully!")

    def change_temp(self):
        result = self.chatbot.change_temperature()
        if result:
            self.show_system_message(result)

    def change_top_k(self):
        result = self.chatbot.change_top_k()
        if result:
            self.show_system_message(result)

    def change_top_p(self):
        result = self.chatbot.change_top_p()
        if result:
            self.show_system_message(result)

    def max_randomness(self):
        result = self.chatbot.max_randomness()
        if result:
            self.show_system_message(result)

class LoginWindow:
    def __init__(self):
        self.db = DatabaseManager()
        self.root = tk.Tk()
        self.root.title("Gemini Chat Login")
        self.root.geometry("600x400")
        self.setup_gui()

    def setup_gui(self):
        # Setup canvas and background
        canvas = tk.Canvas(self.root, width=1280, height=720)
        canvas.pack(fill="both", expand=True)

        try:
            bg_image = Image.open("bg.jpeg")
            bg_image = bg_image.resize((1280, 800), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        except FileNotFoundError:
            canvas.create_rectangle(0, 0, 1280, 720, fill="#f0f0f0")

        # Login frame
        login_frame = tk.Frame(self.root, bg="white", bd=5)
        login_frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=350)

        # Login components
        tk.Label(login_frame, text="Login", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        tk.Label(login_frame, text="Username:", font=("Arial", 12), bg="white").pack(anchor="w", padx=10)
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12))
        self.username_entry.pack(fill="x", padx=10, pady=5)

        tk.Label(login_frame, text="Password:", font=("Arial", 12), bg="white").pack(anchor="w", padx=10)
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), show="*")
        self.password_entry.pack(fill="x", padx=10, pady=5)

        tk.Button(login_frame, text="Login", command=self.login,
                 font=("Arial", 12), bg="#007BFF", fg="white").pack(pady=10, fill="x", padx=10)
        
        tk.Button(login_frame, text="Register", command=self.register,
                 font=("Arial", 12), bg="#28A745", fg="white").pack(pady=5, fill="x", padx=10)

        self.root.mainloop()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Username and Password cannot be empty!")
            return

        if self.db.authenticate_user(username, password):
            messagebox.showinfo("Success", f"Welcome, {username}!")
            self.root.destroy()
            ChatInterface(username)
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Username and Password cannot be empty!")
            return

        if self.db.register_user(username, password):
            messagebox.showinfo("Success", "Account created successfully. Please log in.")
        else:
            messagebox.showerror("Error", "Username already exists.")

if __name__ == "__main__":
    try:
        app = LoginWindow()
    except Exception as e:
        print(f"An error occurred: {e}")