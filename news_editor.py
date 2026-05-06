#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Редактор новостей для KC-251 сайта
News Editor for KC-251 Website
"""

import json
import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkFont

class NewsEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("KC-251 — Редактор новостей")
        self.root.geometry("1100x700")
        self.root.minsize(800, 500)
        
        # Стили
        self.setup_styles()
        
        # Путь к файлу новостей
        self.news_file = Path(__file__).parent / "news.json"
        self.news_history_file = Path(__file__).parent / "news_history.json"
        
        # Данные
        self.news_data = []
        self.selected_news = None
        
        # Загружаем новости
        self.load_news()
        
        # Создаем интерфейс
        self.create_widgets()
        self.refresh_news_list()
    
    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цвета
        bg_color = "#2b2b2b"
        fg_color = "#ffffff"
        accent_color = "#0078d4"
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', background=accent_color, foreground=fg_color)
        style.configure('TListbox', background="#1e1e1e", foreground=fg_color)
        
        self.root.configure(bg=bg_color)
    
    def load_news(self):
        """Загружаем новости из JSON"""
        try:
            if self.news_file.exists():
                with open(self.news_file, 'r', encoding='utf-8') as f:
                    self.news_data = json.load(f)
            else:
                self.news_data = []
                messagebox.showwarning("Внимание", f"Файл {self.news_file} не найден.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке: {e}")
            self.news_data = []
    
    def save_news(self):
        """Сохраняем новости в JSON"""
        try:
            # Сортируем по дате (новые в начале)
            sorted_news = sorted(self.news_data, key=lambda x: x.get('date', ''), reverse=True)
            
            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump(sorted_news, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", "Новости сохранены!")
            self.refresh_news_list()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")
    
    def create_widgets(self):
        """Создаем элементы интерфейса"""
        
        # Главный контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === ЛЕВАЯ ЧАСТЬ (Список новостей) ===
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Заголовок списка
        title_label = ttk.Label(left_frame, text="Список новостей", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Фрейм для поиска
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Список новостей
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.news_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                       bg="#1e1e1e", fg="#ffffff", 
                                       selectmode=tk.SINGLE, font=("Arial", 10))
        self.news_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.news_listbox.bind('<<ListboxSelect>>', self.on_select_news)
        scrollbar.config(command=self.news_listbox.yview)
        
        # Кнопки действий со списком
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="➕ Новая", command=self.add_news).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🗑️ Удалить", command=self.delete_news).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="💾 Сохранить", command=self.save_news).pack(side=tk.LEFT, padx=2)
        
        # === ПРАВАЯ ЧАСТЬ (Редактирование) ===
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        edit_title_label = ttk.Label(right_frame, text="Редактор новости", 
                                     font=("Arial", 14, "bold"))
        edit_title_label.pack(pady=(0, 10))
        
        # Поля для редактирования
        self.edit_widgets = {}
        
        # Заголовок
        ttk.Label(right_frame, text="Заголовок:", font=("Arial", 10)).pack(anchor=tk.W)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(right_frame, textvariable=self.title_var, font=("Arial", 10))
        title_entry.pack(fill=tk.X, pady=(0, 10))
        self.edit_widgets['title'] = self.title_var
        
        # Дата
        ttk.Label(right_frame, text="Дата (YYYY-MM-DD):", font=("Arial", 10)).pack(anchor=tk.W)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(right_frame, textvariable=self.date_var, font=("Arial", 10))
        date_entry.pack(fill=tk.X, pady=(0, 10))
        self.edit_widgets['date'] = self.date_var
        
        # Текст новости
        ttk.Label(right_frame, text="Текст новости:", font=("Arial", 10)).pack(anchor=tk.W)
        self.text_var = tk.StringVar()
        text_entry = tk.Text(right_frame, height=8, font=("Arial", 10), 
                            bg="#1e1e1e", fg="#ffffff", wrap=tk.WORD)
        text_entry.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.edit_widgets['text'] = text_entry
        
        # Автор
        ttk.Label(right_frame, text="Автор:", font=("Arial", 10)).pack(anchor=tk.W)
        self.author_var = tk.StringVar()
        author_entry = ttk.Entry(right_frame, textvariable=self.author_var, font=("Arial", 10))
        author_entry.pack(fill=tk.X, pady=(0, 10))
        self.edit_widgets['author_profile'] = self.author_var
        
        # Флаги
        flags_frame = ttk.Frame(right_frame)
        flags_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.important_var = tk.BooleanVar()
        ttk.Checkbutton(flags_frame, text="⭐ Важная новость", 
                       variable=self.important_var).pack(side=tk.LEFT, padx=5)
        
        self.pinned_var = tk.BooleanVar()
        ttk.Checkbutton(flags_frame, text="📌 Закрепить", 
                       variable=self.pinned_var).pack(side=tk.LEFT, padx=5)
        
        # Статус
        ttk.Label(right_frame, text="Статус:", font=("Arial", 10)).pack(anchor=tk.W)
        self.status_var = tk.StringVar(value="published")
        status_combo = ttk.Combobox(right_frame, textvariable=self.status_var, 
                                    values=["published", "draft"], state='readonly')
        status_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Кнопка сохранения изменений
        ttk.Button(right_frame, text="✅ Сохранить новость", 
                  command=self.save_current_news).pack(fill=tk.X, pady=(0, 10))
        
        # Статус-бар
        self.status_label = ttk.Label(right_frame, text="Нужно выбрать новость для редактирования", 
                                      font=("Arial", 9))
        self.status_label.pack(fill=tk.X)
    
    def refresh_news_list(self):
        """Обновляем список новостей"""
        search_term = self.search_var.get().lower()
        self.news_listbox.delete(0, tk.END)
        
        filtered_news = []
        for news in self.news_data:
            title = news.get('title', '(без заголовка)')
            date = news.get('date', '')
            
            if search_term in title.lower() or search_term in date.lower():
                filtered_news.append(news)
        
        for news in filtered_news:
            title = news.get('title', '(без заголовка)')
            date = news.get('date', '')
            important = '⭐ ' if news.get('important', False) else ''
            pinned = '📌 ' if news.get('pinned', False) else ''
            display_text = f"{important}{pinned}{title} — {date}"
            self.news_listbox.insert(tk.END, display_text)
    
    def on_search_change(self, *args):
        """Обработчик изменения поиска"""
        self.refresh_news_list()
    
    def on_select_news(self, event):
        """Выбран элемент в списке"""
        selection = self.news_listbox.curselection()
        if not selection:
            return
        
        # Находим выбранную новость
        search_term = self.search_var.get().lower()
        filtered_news = []
        for news in self.news_data:
            title = news.get('title', '')
            date = news.get('date', '')
            if search_term in title.lower() or search_term in date.lower():
                filtered_news.append(news)
        
        self.selected_news = filtered_news[selection[0]]
        self.display_news(self.selected_news)
    
    def display_news(self, news):
        """Отображает новость в редакторе"""
        self.title_var.set(news.get('title', ''))
        self.date_var.set(news.get('date', ''))
        self.edit_widgets['text'].delete(1.0, tk.END)
        self.edit_widgets['text'].insert(1.0, news.get('text', ''))
        self.author_var.set(news.get('author_profile', ''))
        self.important_var.set(news.get('important', False))
        self.pinned_var.set(news.get('pinned', False))
        self.status_var.set(news.get('status', 'published'))
        
        self.status_label.config(text=f"Редактирование: {news.get('title', 'Новость')}")
    
    def save_current_news(self):
        """Сохраняет текущую редактируемую новость"""
        if self.selected_news is None:
            messagebox.showwarning("Внимание", "Выберите новость для редактирования")
            return
        
        # Обновляем данные
        self.selected_news['title'] = self.title_var.get()
        self.selected_news['date'] = self.date_var.get()
        self.selected_news['text'] = self.edit_widgets['text'].get(1.0, tk.END).strip()
        self.selected_news['author_profile'] = self.author_var.get()
        self.selected_news['important'] = self.important_var.get()
        self.selected_news['pinned'] = self.pinned_var.get()
        self.selected_news['status'] = self.status_var.get()
        
        self.status_label.config(text="✅ Изменения сохранены (нажмите 'Сохранить' внизу слева для записи в файл)")
    
    def add_news(self):
        """Добавляет новую новость"""
        new_news = {
            "id": int(datetime.now().timestamp() * 1000000) % (10**9),
            "title": "Новая новость",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "text": "Введите текст новости...",
            "important": False,
            "pinned": False,
            "status": "draft",
            "author_profile": "Администратор"
        }
        
        self.news_data.append(new_news)
        self.selected_news = new_news
        self.display_news(new_news)
        self.refresh_news_list()
        self.status_label.config(text="✅ Новая новость создана. Заполните поля и сохраните.")
    
    def delete_news(self):
        """Удаляет выбранную новость"""
        if self.selected_news is None:
            messagebox.showwarning("Внимание", "Выберите новость для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", f"Удалить '{self.selected_news.get('title', 'Новость')}'?"):
            self.news_data.remove(self.selected_news)
            self.selected_news = None
            
            # Очищаем редактор
            self.title_var.set('')
            self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
            self.edit_widgets['text'].delete(1.0, tk.END)
            self.author_var.set('')
            self.important_var.set(False)
            self.pinned_var.set(False)
            self.status_var.set('published')
            self.status_label.config(text="Новость удалена")
            
            self.refresh_news_list()


def main():
    root = tk.Tk()
    app = NewsEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
