import locale
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    pass

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import json
import os

username = simpledialog.askstring("Kullanıcı Adı", "Lütfen bir kullanıcı adı girin:")

root = ttk.Window(themename="superhero")
root.title("Quiz Uygulaması")
root.geometry("800x600")

def load_user_data(username):
    file_path = f"{username}_data.json"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            'user_name': username,
            'history': {
                'correct': [],
                'incorrect': [],
                'categories': {},
                'focus_areas': {}
            }
        }

def save_user_data(username, data):
    file_path = f"{username}_data.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

user_data = load_user_data(username)

try:
    with open('sorular_guncellenmis.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
except FileNotFoundError:
    messagebox.showerror("Hata", "JSON dosyası bulunamadı!")
    root.quit()
    exit()

user_progress = {
    'category': None,
    'level': 1,
    'wrong_questions': [],
    'asked_questions': [],
}

current_question = None
answer_var = tk.StringVar()

level_label = ttk.Label(root, text="Seviye: 1", font=("Arial", 25), bootstyle="primary")
level_label.pack(pady=10)

question_counter_label = ttk.Label(root, text="Soru: 1 / 7", font=("Arial", 15))
question_counter_label.pack(pady=5)

question_label = ttk.Label(root, text="Başlamak İçin bir Kategori Seçin", font=("Arial", ), wraplength=500)
question_label.pack(pady=20)

choices_frame = ttk.Frame(root)
choices_frame.pack(pady=10)

choices_buttons = []
for i in range(4):
    rb = ttk.Radiobutton(choices_frame, text=f"Seçenek {i+1}", variable=answer_var, value=chr(65 + i))
    rb.pack(anchor="w")
    choices_buttons.append(rb)

def ask_question():
    global current_question
    category = user_progress['category']
    level = user_progress['level']

    print(f"Kategori: {category}, Seviye: {level}")  # DEBUG

    answer_var.set(None)

    if user_progress['wrong_questions']:
        current_question = user_progress['wrong_questions'].pop(0)
    else:
        remaining_questions = [q for q in questions[category][str(level)] if q not in user_progress['asked_questions']]
        if remaining_questions:
            current_question = random.choice(remaining_questions)
            user_progress['asked_questions'].append(current_question)
        else:
            messagebox.showinfo("Seviye Tamamlandı!", "Bu seviyedeki tüm soruları tamamladınız!")
            go_to_next_question()
            return

    question_label.config(text=current_question['question'])

    for i, choice in enumerate(current_question['choices']):
        choices_buttons[i].config(text=f"{choice}")

    question_counter_label.config(text=f"Soru: {len(user_progress['asked_questions'])} / 7")

def check_answer():
    global current_question
    category = user_progress['category']
    focus_area = current_question['focus_area']
    
    if focus_area not in user_data['history'].get('focus_areas', {}):
        user_data['history']['focus_areas'][focus_area] = {'correct': 0, 'incorrect': 0}

    # DEBUG
    print(f"Kullanıcı cevabı: {answer_var.get()}")
    print(f"Doğru cevap: {current_question['answer']}")
    
    if answer_var.get() == current_question['answer']:
        messagebox.showinfo("Doğru!", "Doğru cevap!")
        user_data['history']['correct'].append(current_question['question'])

        if category not in user_data['history']['categories']:
            user_data['history']['categories'][category] = {'correct': 0, 'incorrect': 0}
        user_data['history']['categories'][category]['correct'] += 1

        user_data['history']['focus_areas'][focus_area]['correct'] += 1

    else:
        correct_answer = current_question['answer']
        correct_answer_text = next(choice for choice in current_question['choices'] if choice.startswith(correct_answer))
        messagebox.showerror("Yanlış!", f"Yanlış cevap! Doğru cevap: {correct_answer_text}")
        
        user_data['history']['incorrect'].append(current_question['question'])

        if category not in user_data['history']['categories']:
            user_data['history']['categories'][category] = {'correct': 0, 'incorrect': 0}
        user_data['history']['categories'][category]['incorrect'] += 1

        user_data['history']['focus_areas'][focus_area]['incorrect'] += 1

    save_user_data(username, user_data)
    
    go_to_next_question()

def go_to_next_question():
    category = user_progress['category']
    level = user_progress['level']
    
    if len(user_progress['asked_questions']) == len(questions[category][str(level)]) and not user_progress['wrong_questions']:
        if user_progress['level'] < 7:
            user_progress['level'] += 1
            user_progress['asked_questions'] = []

            messagebox.showinfo("Seviye Atladınız!", f"Yeni seviyeye geçtiniz! Şu an {user_progress['level']}. seviyedesiniz.")
            
            level_label.config(text=f"Seviye: {user_progress['level']}", bootstyle="success")
            root.after(500, lambda: level_label.config(bootstyle="primary"))
            ask_question()
        else:
            messagebox.showinfo("Tebrikler!", "Tüm seviyeleri tamamladınız!")
            root.quit()
    else:
        ask_question()

submit_button = ttk.Button(root, text="Cevabı Gönder", bootstyle="success", command=check_answer)
submit_button.pack(pady=10)

category_frame = ttk.Frame(root)
category_frame.pack(pady=10)

def select_category(cat):
    user_progress['category'] = cat
    user_progress['asked_questions'] = []
    ask_question()

categories = ['Spor', 'Tarih', 'Bilim', 'Edebiyat', 'Sanat', 'Coğrafya', 'Genel Kültür']
for category in categories:
    btn = ttk.Button(category_frame, text=category, bootstyle="info", command=lambda c=category: select_category(c))
    btn.pack(side="left", padx=10)

root.mainloop()
