import tkinter as tk
from tkinter import ttk, messagebox, Tk, Frame, Label, Entry, StringVar, BooleanVar, filedialog
from db_utils import (
    init_db, register_user, authenticate_user, get_categories, add_category, update_category, delete_category,
    get_events, add_event, update_event, delete_event,
    get_favorites, add_favorite, remove_favorite, get_connection
)
import datetime
from tkcalendar import DateEntry
import pandas as pd
from tkinter import font
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm

# регистрируем шрифт с поддержкой кириллицы
try:
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
except:
    print("Не удалось зарегистрировать шрифт Arial. Будут использованы встроенные шрифты.")

# основной класс приложения
class EventDesignApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('EventDesign')
        self.geometry('1400x700')
        self.resizable(False, False)
        self.current_frame = None
        self.current_user = None  # user_id, user_name
        self.theme = 'dark'  # по умолчанию
        self.style = ttk.Style(self)
        self.apply_theme()
        init_db()  # инициализация базы при запуске
        self.show_welcome()

    def apply_theme(self):
        if self.theme == 'dark':
            bg = '#232323'
            fg = 'white'
            btn_bg = '#3399ff'
            btn_fg = 'white'
            btn_active = '#4da3ff'
            entry_bg = '#232323'
            entry_fg = 'white'
            combo_bg = '#3399ff'
            combo_fg = 'white'
        else:
            bg = 'white'
            fg = 'black'
            btn_bg = '#3399ff'
            btn_fg = 'black'
            btn_active = '#4da3ff'
            entry_bg = 'white'
            entry_fg = 'black'
            combo_bg = 'white'
            combo_fg = 'black'
        self.configure(bg=bg)
        self.style.theme_use('default')
        
        self.style.configure('TButton', background=btn_bg, foreground=btn_fg, font=('Arial', 12), padding=6)
        
        self.style.element_create('RoundedFrame', 'from', 'default')
        self.style.layout('Rounded.TButton', [
            ('Button.focus', {'children': [
                ('Button.border', {'border': '2', 'sticky': 'nswe', 'children': [
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nswe'})
                    ]})
                ]})
            ]}),
        ])
        self.style.configure('Rounded.TButton', background=btn_bg, foreground=btn_fg, font=('Arial', 12, 'bold'), 
                           padding=6, borderwidth=2, relief="raised", bordercolor=btn_bg)
        self.style.map('Rounded.TButton', background=[('active', btn_active), ('pressed', btn_active)],
                     relief=[('pressed', 'raised')])
        
        self.style.configure('TEntry', fieldbackground=entry_bg, foreground=entry_fg, borderwidth=1, 
                           relief="solid", padding=8)
        
        self.style.configure('Treeview', background=bg, fieldbackground=bg, foreground=fg)
        self.style.configure('Treeview.Heading', background=btn_bg, foreground=btn_fg, font=('Arial', 11, 'bold'))
        
        self.style.configure('CustomCombobox.TCombobox', fieldbackground=combo_bg, background=combo_bg, 
                           foreground=combo_fg, selectbackground=combo_bg, selectforeground=combo_fg, 
                           bordercolor=btn_bg, lightcolor=btn_bg, darkcolor=btn_bg)
        self.style.map('CustomCombobox.TCombobox', fieldbackground=[('readonly', combo_bg)], 
                     foreground=[('readonly', combo_fg)])
        
        if self.current_frame:
            self.current_frame.update_theme(bg, fg, btn_bg, btn_fg)

    def set_theme(self, theme):
        self.theme = theme
        self.apply_theme()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_welcome(self):
        self.clear_frame()
        self.current_frame = WelcomeFrame(self, self.show_register, self.show_login)
        self.current_frame.pack(expand=True)

    def show_login(self):
        self.clear_frame()
        self.current_frame = LoginFrame(self, self.on_login_success, self.show_register)
        self.current_frame.pack(expand=True)

    def show_register(self):
        self.clear_frame()
        self.current_frame = RegisterFrame(self, self.on_register_success)
        self.current_frame.pack(expand=True)

    def on_login_success(self, user):
        self.current_user = user
        self.show_main_menu()

    def on_register_success(self, user):
        self.current_user = user
        self.show_main_menu()

    def show_main_menu(self):
        self.clear_frame()
        self.current_frame = MainMenuFrame(self, self.show_events, self.show_categories, self.show_favorites, self.show_settings, self.show_reports)
        self.current_frame.pack(expand=True)

    def show_events(self):
        self.clear_frame()
        self.current_frame = EventsFrame(self, self.show_main_menu)
        self.current_frame.pack(expand=True)

    def show_categories(self):
        self.clear_frame()
        self.current_frame = CategoriesFrame(self, self.show_main_menu)
        self.current_frame.pack(expand=True)

    def show_favorites(self):
        self.clear_frame()
        self.current_frame = FavoritesFrame(self, self.show_main_menu, self.current_user)
        self.current_frame.pack(expand=True)

    def show_settings(self):
        self.clear_frame()
        self.current_frame = SettingsFrame(self, self.show_main_menu)
        self.current_frame.pack(expand=True)

    def show_reports(self):
        self.clear_frame()
        self.current_frame = ReportsFrame(self, self.show_main_menu)
        self.current_frame.pack(expand=True)

class ThemedFrame(tk.Frame):
    def update_theme(self, bg, fg, btn_bg, btn_fg):
        self.configure(bg=bg)
        for w in self.winfo_children():
            if isinstance(w, (tk.Label, tk.Frame)):
                w.configure(bg=bg, fg=fg if isinstance(w, tk.Label) else None)
            if isinstance(w, ttk.Button):
                w.configure(style='TButton')
            if isinstance(w, ttk.Entry):
                w.configure(style='TEntry')
            if isinstance(w, ttk.Treeview):
                w.configure(style='Treeview')
            if isinstance(w, ttk.Combobox):
                w.configure(foreground=fg)

class WelcomeFrame(ThemedFrame):
    def __init__(self, master, on_register, on_login):
        super().__init__(master, bg=master['bg'])
        tk.Label(self, text='\uD83D\uDCC5 EventDesign', font=('Arial', 22), fg=master.style.lookup('TButton', 'foreground'), bg=master['bg']).pack(pady=20)
        btn_width = 25
        welcome_container = tk.Frame(self, bg=master['bg'], padx=20, pady=20)
        welcome_container.pack()
        
        form = tk.Frame(welcome_container, bg=master['bg'], 
                       highlightthickness=0, bd=0, padx=30, pady=30)
        form.pack()
        
        ttk.Button(form, text='Зарегистрироваться', command=on_register, width=btn_width, style='Rounded.TButton').pack(pady=15, ipady=8)
        ttk.Button(form, text='Авторизация', command=on_login, width=btn_width, style='Rounded.TButton').pack(pady=15, ipady=8)
    def update_theme(self, bg, fg, btn_bg, btn_fg):
        super().update_theme(bg, fg, btn_bg, btn_fg)

class LoginFrame(ThemedFrame):
    def __init__(self, master, on_login_success, on_register):
        super().__init__(master, bg=master['bg'])
        tk.Label(self, text='Авторизация', font=('Arial', 20), fg=master.style.lookup('TButton', 'foreground'), bg=master['bg']).pack(pady=20)
        
        form_container = tk.Frame(self, bg=master['bg'], padx=20, pady=20)
        form_container.pack(pady=10)
        
        form = tk.Frame(form_container, bg=master['bg'], 
                       highlightthickness=0, bd=0, padx=20, pady=20)
        form.pack()
        
        tk.Label(form, text='Логин', fg=master.style.lookup('TButton', 'foreground'), 
                bg=master['bg'], anchor='w', font=('Arial', 12)).pack(anchor='w', pady=(0, 5))
        self.login_entry = ttk.Entry(form, style='TEntry', width=40, font=('Arial', 12))
        self.login_entry.pack(pady=(0, 15), ipady=5)
        
        tk.Label(form, text='Пароль', fg=master.style.lookup('TButton', 'foreground'), 
                bg=master['bg'], anchor='w', font=('Arial', 12)).pack(anchor='w', pady=(0, 5))
        self.password_entry = ttk.Entry(form, show='*', style='TEntry', width=40, font=('Arial', 12))
        self.password_entry.pack(pady=(0, 20), ipady=5)
        
        login_btn = ttk.Button(form, text='Вход', command=self.try_login, style='Rounded.TButton', width=25)
        login_btn.pack(pady=12, ipady=5)
        
        # ссылка на регистрацию
        link_frame = tk.Frame(form, bg=master['bg'])
        link_frame.pack(pady=10)
        tk.Label(link_frame, text='Нет аккаунта?', fg=master.style.lookup('TButton', 'foreground'), 
                bg=master['bg'], font=('Arial', 11)).pack(side='left')
        reg_link = tk.Label(link_frame, text='Зарегистрироваться', fg='#4da3ff', bg=master['bg'], 
                           cursor='hand2', font=('Arial', 11, 'underline'))
        reg_link.pack(side='left', padx=5)
        reg_link.bind('<Button-1>', lambda e: master.show_register())
        self.on_login_success = on_login_success

    def try_login(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # валидация входных данных
        if not login:
            messagebox.showerror('Ошибка', 'Поле логина не может быть пустым')
            return
            
        if not password:
            messagebox.showerror('Ошибка', 'Поле пароля не может быть пустым')
            return
        
        user = authenticate_user(login, password)
        if user:
            messagebox.showinfo('Успех', f'Добро пожаловать, {user[1]}!')
            self.on_login_success(user)
        else:
            messagebox.showerror('Ошибка', 'Неверный логин или пароль')

class RegisterFrame(ThemedFrame):
    def __init__(self, master, on_register_success):
        super().__init__(master, bg=master['bg'])
        tk.Label(self, text='Регистрация', font=('Arial', 20), fg=master.style.lookup('TButton', 'foreground'), bg=master['bg']).pack(pady=20)
        
        form_container = tk.Frame(self, bg=master['bg'], padx=20, pady=20)
        form_container.pack(pady=10)
        
        form = tk.Frame(form_container, bg=master['bg'], 
                       highlightthickness=0, bd=0, padx=20, pady=20)
        form.pack()
        
        # стилизованные поля ввода
        self.entries = {}
        labels = ['Почта', 'Имя', 'Логин', 'Пароль']
        
        for label in labels:
            tk.Label(form, text=label, fg=master.style.lookup('TButton', 'foreground'), 
                    bg=master['bg'], anchor='w', font=('Arial', 12)).pack(anchor='w', pady=(0, 5))
            entry = ttk.Entry(form, show='*' if label == 'Пароль' else None, 
                             style='TEntry', width=40, font=('Arial', 12))
            entry.pack(pady=(0, 15), ipady=5)
            self.entries[label] = entry
        
        # стилизованная кнопка регистрации
        register_btn = ttk.Button(form, text='Зарегистрироваться', command=self.try_register, 
                                 style='Rounded.TButton', width=25)
        register_btn.pack(pady=12, ipady=5)
        
        # ссылка на вход
        link_frame = tk.Frame(form, bg=master['bg'])
        link_frame.pack(pady=10)
        tk.Label(link_frame, text='Есть аккаунт?', fg=master.style.lookup('TButton', 'foreground'), 
                bg=master['bg'], font=('Arial', 11)).pack(side='left')
        login_link = tk.Label(link_frame, text='Войти', fg='#4da3ff', bg=master['bg'], 
                             cursor='hand2', font=('Arial', 11, 'underline'))
        login_link.pack(side='left', padx=5)
        login_link.bind('<Button-1>', lambda e: master.show_login())
        self.on_register_success = on_register_success

    def try_register(self):
        email = self.entries['Почта'].get().strip()
        name = self.entries['Имя'].get().strip()
        login = self.entries['Логин'].get().strip()
        password = self.entries['Пароль'].get().strip()
            
        # валидация формы
        if not (email and name and login and password):
            messagebox.showerror('Ошибка', 'Все поля обязательны!')
            return
            
        # валидация email: должен содержать @
        if '@' not in email:
            messagebox.showerror('Ошибка', 'Неверный формат email. Email должен содержать символ @')
            return
            
        # валидация имени: только буквы и пробелы
        if not all(c.isalpha() or c.isspace() for c in name):
            messagebox.showerror('Ошибка', 'Имя должно содержать только буквы и пробелы, без цифр и специальных символов')
            return
            
        # валидация пароля: минимум 6 символов
        if len(password) < 6:
            messagebox.showerror('Ошибка', 'Пароль должен содержать минимум 6 символов')
            return
            
        # проверка на наличие цифры в пароле
        has_digit = any(c.isdigit() for c in password)
        
        if not has_digit:
            messagebox.showerror('Ошибка', 'Пароль должен содержать хотя бы одну цифру')
            return
        
        # Если все проверки пройдены, регистрируем пользователя
        ok, err = register_user(name, login, password, email)
        if ok:
            # Получаем user_id для нового пользователя
            user = authenticate_user(login, password)
            messagebox.showinfo('Успех', 'Регистрация прошла успешно!')
            self.on_register_success(user)
        else:
            messagebox.showerror('Ошибка', err or 'Ошибка регистрации')

class MainMenuFrame(ThemedFrame):
    def __init__(self, master, on_events, on_categories, on_favorites, on_settings, on_reports):
        super().__init__(master, bg=master['bg'])
        tk.Label(self, text='\uD83D\uDCC5 EventDesign', font=('Arial', 22), fg=master.style.lookup('TButton', 'foreground'), bg=master['bg']).pack(pady=20)
        
        menu_container = tk.Frame(self, bg=master['bg'], padx=20, pady=10)
        menu_container.pack()
        
        menu_frame = tk.Frame(menu_container, bg=master['bg'], 
                       highlightthickness=0, bd=0, padx=30, pady=30)
        menu_frame.pack()
        
        btn_width = 30
        for text, cmd in [
            ('Мероприятия', on_events),
            ('Категории', on_categories),
            ('Избранное', on_favorites),
            ('Настройки', on_settings),
            ('Отчеты', on_reports)
        ]:
            ttk.Button(menu_frame, text=text, command=cmd, style='Rounded.TButton', width=btn_width).pack(pady=10, ipady=8)

class EventsFrame(ThemedFrame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=master['bg'])
        self.master = master  

        back_btn = ttk.Button(
            self, 
            text="Назад", 
            command=on_back, 
            style='Rounded.TButton',
            width=20  
        )
    
        back_btn.pack(side='bottom', pady=20, ipady=5)
        tk.Label(self, text='Мероприятия', font=('Arial', 20), fg=master.style.lookup('TButton', 'foreground'), bg=master['bg']).pack(pady=10)
        
        table_frame = tk.Frame(self, bg=master['bg'], highlightthickness=0, bd=0)
        table_frame.pack(pady=5, padx=10, fill='both', expand=True)
        
        columns = ('id', 'name', 'category', 'location', 'date', 'desc', 'favorite')
        self.table = ttk.Treeview(table_frame, columns=columns, show='headings', height=10) 
        for col, text in zip(columns, ['ID', 'Название', 'Категория', 'Место', 'Дата', 'Описание', 'Избранное']):
            self.table.heading(col, text=text)
            self.table.column(col, width=170 if col != 'id' else 40, anchor='center')

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        self.table.pack(fill='both', expand=True)
        self.refresh_table()
        
        # --- форма ---
        form_outer = tk.Frame(self, bg=master['bg'])
        form_outer.pack(pady=10, fill='x')
        form_frame = tk.Frame(form_outer, bg=master['bg'], highlightthickness=0, bd=0)
        form_frame.pack(pady=0, padx=0)
        # название
        tk.Label(form_frame, text='Название:', fg=master.style.lookup('TButton', 'foreground'), bg=master['bg'], anchor='e').grid(row=0, column=0, sticky='e', pady=6, padx=4)
        self.name_entry = ttk.Entry(form_frame, width=25, style='TEntry')
        self.name_entry.grid(row=0, column=1, sticky='w', pady=6, padx=4)
        # категория
        tk.Label(form_frame, text='Категория:', fg=master.style.lookup('TButton', 'foreground'), bg=master['bg'], anchor='e').grid(row=0, column=2, sticky='e', pady=6, padx=4)
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(form_frame, textvariable=self.cat_var, width=23, state='readonly', style='CustomCombobox.TCombobox')
        self.cat_combo.grid(row=0, column=3, sticky='w', pady=6, padx=4)
        self.refresh_categories()
        # место
        tk.Label(form_frame, text='Место:', fg=master.style.lookup('TButton', 'foreground'), bg=master['bg'], anchor='e').grid(row=1, column=0, sticky='e', pady=6, padx=4)
        self.loc_entry = ttk.Entry(form_frame, width=25, style='TEntry')
        self.loc_entry.grid(row=1, column=1, sticky='w', pady=6, padx=4)
        # дата
        tk.Label(form_frame, text='Дата (ГГГГ-ММ-ДД):', fg=master.style.lookup('TButton', 'foreground'), bg=master['bg'], anchor='e').grid(row=1, column=2, sticky='e', pady=6, padx=4)
        self.date_entry = ttk.Entry(form_frame, width=23, style='TEntry')
        self.date_entry.grid(row=1, column=3, sticky='w', pady=6, padx=4)
        # описание
        tk.Label(form_frame, text='Описание:', fg=master.style.lookup('TButton', 'foreground'), bg=master['bg'], anchor='e').grid(row=2, column=0, sticky='e', pady=6, padx=4)
        self.desc_entry = ttk.Entry(form_frame, width=60, style='TEntry')
        self.desc_entry.grid(row=2, column=1, columnspan=3, sticky='w', pady=6, padx=4)
        # примечание
        tk.Label(form_frame, text='Примечание:', fg=master.style.lookup('TButton', 'foreground'), bg=master['bg'], anchor='e').grid(row=3, column=0, sticky='e', pady=6, padx=4)
        self.note_entry = ttk.Entry(form_frame, width=60, style='TEntry')
        self.note_entry.grid(row=3, column=1, columnspan=3, sticky='w', pady=6, padx=4)
        # чекбокс избранное
        self.favorite_var = tk.BooleanVar()
        fav_frame = tk.Frame(form_frame, bg=master['bg'])
        fav_frame.grid(row=4, column=0, columnspan=4, pady=8)
        self.favorite_check = ttk.Checkbutton(fav_frame, text='Добавить в избранное', variable=self.favorite_var)
        self.favorite_check.pack(anchor='center')
        
        # --- кнопки управления записями ---
        action_buttons = tk.Frame(self, bg=master['bg'])
        action_buttons.pack(pady=10)
        
        # кнопки в один ряд с более заметным оформлением
        ttk.Button(action_buttons, text='Добавить', command=self.add_event, style='Rounded.TButton', 
                  width=20).grid(row=0, column=0, padx=20, pady=5)
        ttk.Button(action_buttons, text='Редактировать', command=self.edit_event, style='Rounded.TButton', 
                  width=20).grid(row=0, column=1, padx=20, pady=5)
        ttk.Button(action_buttons, text='Удалить', command=self.delete_event, style='Rounded.TButton', 
                  width=20).grid(row=0, column=2, padx=20, pady=5)
        
        btn_row2 = tk.Frame(action_buttons, bg=master['bg'])
        btn_row2.grid(row=1, column=0, columnspan=3, pady=10)
        
        fav_btn = ttk.Button(btn_row2, text='Добавить в избранное', command=self.add_to_favorites, 
                           style='Rounded.TButton', width=25)
        fav_btn.pack(side='left', padx=10, ipady=5)
        
        back_btn = ttk.Button(btn_row2, text='Назад', command=on_back, 
                            style='Rounded.TButton', width=25)
        back_btn.pack(side='left', padx=10, ipady=5)
        
        self.table.bind('<<TreeviewSelect>>', self.on_select)
        self.selected_id = None

    def refresh_categories(self):
        cats = get_categories()
        self.cat_combo['values'] = ['Все'] + [c[1] for c in cats]
        self.cat_map = {c[1]: c[0] for c in cats}
        self.cat_combo.current(0)

    def refresh_table(self):
        for row in self.table.get_children():
            self.table.delete(row)
        for ev in get_events():
            # Первый элемент (ev[0]) - это ID мероприятия
            self.table.insert('', 'end', values=(ev[0], ev[1], ev[2], ev[3], ev[4], ev[5], '✔' if ev[6] else ''))

    def on_select(self, event):
        sel = self.table.selection()
        if sel:
            vals = self.table.item(sel[0])['values']
            # Первый элемент (vals[0]) - это ID мероприятия
            self.selected_id = vals[0]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, vals[1])  # Название теперь во втором элементе
            # Найти id категории по названию
            cat_name = vals[2]  # Категория теперь в третьем элементе
            self.cat_var.set(cat_name)
            self.loc_entry.delete(0, tk.END)
            self.loc_entry.insert(0, vals[3])  # Место теперь в четвертом элементе
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, vals[4])  # Дата теперь в пятом элементе
            self.desc_entry.delete(0, tk.END)
            self.desc_entry.insert(0, vals[5])  # Описание теперь в шестом элементе
            self.favorite_var.set(vals[6] == '✔')  # Избранное теперь в седьмом элементе

    def add_event(self):
        name = self.name_entry.get().strip()
        cat = self.cat_var.get()
        date = self.date_entry.get().strip()
        loc = self.loc_entry.get().strip()
        desc = self.desc_entry.get().strip()
        note = self.note_entry.get().strip()
        favorite = self.favorite_var.get()
        
        # базовая валидация на пустые поля
        if not (name and cat and date):
            messagebox.showerror('Ошибка', 'Название, категория и дата обязательны!')
            return
            
        # валидация названия (не менее 3 символов)
        if len(name) < 3:
            messagebox.showerror('Ошибка', 'Название мероприятия должно содержать минимум 3 символа')
            return
            
        # валидация места проведения (не пустое и минимум 3 символа)
        if not loc or len(loc) < 3:
            messagebox.showerror('Ошибка', 'Укажите место проведения (минимум 3 символа)')
            return
        
        # валидация даты (формат ГГГГ-ММ-ДД)
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Ошибка', 'Неверный формат даты. Используйте формат ГГГГ-ММ-ДД (например, 2023-05-15)')
            return
            
        cat_id = self.cat_map.get(cat)
        if cat_id is None:
            messagebox.showerror('Ошибка', 'Выберите корректную категорию!')
            return
        
        ok, err = add_event(name, cat_id, date, loc, desc, note, favorite)
        if ok:
            self.refresh_table()
            # если мероприятие добавлено в избранное и пользователь авторизован
            if favorite and self.master.current_user:
                # получаем id последнего добавленного мероприятия
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT LAST_INSERT_ID()')
                event_id = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                # добавляем в избранное для текущего пользователя
                add_favorite(self.master.current_user[0], event_id)
            self.clear_form()
        else:
            messagebox.showerror('Ошибка', err or 'Ошибка добавления')

    def edit_event(self):
        if not self.selected_id:
            messagebox.showerror('Ошибка', 'Выберите мероприятие для редактирования')
            return
            
        name = self.name_entry.get().strip()
        cat = self.cat_var.get()
        date = self.date_entry.get().strip()
        loc = self.loc_entry.get().strip()
        desc = self.desc_entry.get().strip()
        note = self.note_entry.get().strip()
        favorite = self.favorite_var.get()
        
        # базовая валидация на пустые поля
        if not (name and cat and date):
            messagebox.showerror('Ошибка', 'Название, категория и дата обязательны!')
            return
            
        # валидация названия (не менее 3 символов)
        if len(name) < 3:
            messagebox.showerror('Ошибка', 'Название мероприятия должно содержать минимум 3 символа')
            return
            
        # валидация места проведения (не пустое и минимум 3 символа)
        if not loc or len(loc) < 3:
            messagebox.showerror('Ошибка', 'Укажите место проведения (минимум 3 символа)')
            return
        
        # валидация даты (формат ГГГГ-ММ-ДД)
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Ошибка', 'Неверный формат даты. Используйте формат ГГГГ-ММ-ДД (например, 2023-05-15)')
            return
            
        cat_id = self.cat_map.get(cat)
        if cat_id is None:
            messagebox.showerror('Ошибка', 'Выберите корректную категорию!')
            return
            
        ok, err = update_event(self.selected_id, name, cat_id, date, loc, desc, note, favorite)
        if ok:
            # если установлен флаг избранное и пользователь авторизован
            if favorite and self.master.current_user:
                # добавляем в избранное для текущего пользователя
                add_favorite(self.master.current_user[0], self.selected_id)
            # если флаг избранное снят и пользователь авторизован
            elif not favorite and self.master.current_user:
                # удаляем из избранного для текущего пользователя
                remove_favorite(self.master.current_user[0], self.selected_id)
            self.refresh_table()
        else:
            messagebox.showerror('Ошибка', err or 'Ошибка редактирования')

    def delete_event(self):
        if not self.selected_id:
            messagebox.showerror('Ошибка', 'Выберите мероприятие для удаления')
            return
        ok, err = delete_event(self.selected_id)
        if ok:
            self.refresh_table()
            self.clear_form()
            self.selected_id = None
        else:
            messagebox.showerror('Ошибка', err or 'Ошибка удаления')

    def add_to_favorites(self):
        if not self.selected_id:
            messagebox.showerror('Ошибка', 'Выберите мероприятие для добавления в избранное')
            return
        
        if not self.master.current_user:
            messagebox.showerror('Ошибка', 'Необходимо авторизоваться для добавления в избранное')
            return
        
        # добавляем мероприятие в избранное
        user_id = self.master.current_user[0]
        
        # Также обновляем флаг favorite в таблице Events
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE Events SET favorite = 1 WHERE event_id = %s', (self.selected_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        ok, err = add_favorite(user_id, self.selected_id)
        if ok:
            messagebox.showinfo('Успех', 'Мероприятие добавлено в избранное')
            self.refresh_table()
        else:
            messagebox.showerror('Ошибка', err or 'Ошибка при добавлении в избранное')

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.loc_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)
        self.favorite_var.set(False)
        self.cat_combo.set('')

class CategoriesFrame(ThemedFrame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=master['bg'])
        
        # Добавляем кнопку НАЗАД сразу после инициализации фрейма
        # Используем стандартный синий стиль кнопки
        back_btn = ttk.Button(
            self, 
            text="Назад", 
            command=on_back, 
            style='Rounded.TButton',
            width=20  # Делаем кнопку стандартной ширины
        )
        # Размещаем кнопку внизу
        back_btn.pack(side='bottom', pady=20, ipady=5)
        
        tk.Label(self, text='Категории', font=('Arial', 20), fg=master.style.lookup('TButton', 'foreground'), bg=master['bg']).pack(pady=10)
        
        # Создаем рамку для таблицы с заметной обводкой
        table_frame = tk.Frame(self, bg=master['bg'], highlightthickness=0, bd=0)
        table_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.table = ttk.Treeview(table_frame, columns=('id', 'name', 'desc'), show='headings', height=7)
        self.table.heading('id', text='ID')
        self.table.heading('name', text='Название')
        self.table.heading('desc', text='Описание')
        self.table.column('id', width=40)
        self.table.column('name', width=150)
        self.table.column('desc', width=220)
        
        # Добавляем прокрутку
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        self.table.pack(fill='both', expand=True)
        self.refresh_table()

        # Создаем рамку для формы с заметной обводкой
        form_container = tk.Frame(self, bg=master['bg'], padx=10, pady=10)
        form_container.pack(pady=10)
        
        form = tk.Frame(form_container, bg=master['bg'],
                        highlightthickness=0, bd=0, padx=15, pady=15)
        form.pack()
        
        # Поля ввода с улучшенным стилем
        tk.Label(form, text='Название:', fg=master.style.lookup('TButton', 'foreground'), 
               bg=master['bg'], font=('Arial', 12)).grid(row=0, column=0, sticky='e', padx=10, pady=10)
        self.name_entry = ttk.Entry(form, width=25, style='TEntry', font=('Arial', 12))
        self.name_entry.grid(row=0, column=1, padx=10, pady=10, ipady=5)
        
        tk.Label(form, text='Описание:', fg=master.style.lookup('TButton', 'foreground'), 
               bg=master['bg'], font=('Arial', 12)).grid(row=1, column=0, sticky='e', padx=10, pady=10)
        self.desc_entry = ttk.Entry(form, width=25, style='TEntry', font=('Arial', 12))
        self.desc_entry.grid(row=1, column=1, padx=10, pady=10, ipady=5)

        # Кнопки управления с улучшенным стилем
        btns = tk.Frame(self, bg=master['bg'])
        btns.pack(pady=15)
        
        # Кнопки действий
        action_btns = tk.Frame(btns, bg=master['bg'])
        action_btns.pack(pady=10)
        for i, (text, cmd) in enumerate([
            ('Добавить', self.add_category),
            ('Редактировать', self.edit_category),
            ('Удалить', self.delete_category),
        ]):
            ttk.Button(action_btns, text=text, command=cmd, style='Rounded.TButton', width=25).grid(row=0, column=i, padx=20, pady=5)

        self.table.bind('<<TreeviewSelect>>', self.on_select)
        self.selected_id = None

    def refresh_table(self):
        for row in self.table.get_children():
            self.table.delete(row)
        for cat in get_categories():
            self.table.insert('', 'end', values=cat)

    def on_select(self, event):
        sel = self.table.selection()
        if sel:
            vals = self.table.item(sel[0])['values']
            self.selected_id = vals[0]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, vals[1])
            self.desc_entry.delete(0, tk.END)
            self.desc_entry.insert(0, vals[2])

    def add_category(self):
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()
        
        # валидация названия категории
        if not name:
            messagebox.showerror('Ошибка', 'Название обязательно!')
            return
            
        # название должно быть не менее 3 символов
        if len(name) < 3:
            messagebox.showerror('Ошибка', 'Название категории должно содержать минимум 3 символа')
            return
            
        # название не должно содержать специальных символов
        if not all(c.isalnum() or c.isspace() for c in name):
            messagebox.showerror('Ошибка', 'Название категории должно содержать только буквы, цифры и пробелы')
            return
            
        ok, err = add_category(name, desc)
        if ok:
            self.refresh_table()
            self.name_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
        else:
            messagebox.showerror('Ошибка', err or 'Ошибка добавления')

    def edit_category(self):
        if not self.selected_id:
            messagebox.showerror('Ошибка', 'Выберите категорию для редактирования')
            return
            
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()
        
        # валидация названия категории
        if not name:
            messagebox.showerror('Ошибка', 'Название обязательно!')
            return
            
        # название должно быть не менее 3 символов
        if len(name) < 3:
            messagebox.showerror('Ошибка', 'Название категории должно содержать минимум 3 символа')
            return
            
        # название не должно содержать специальных символов
        if not all(c.isalnum() or c.isspace() for c in name):
            messagebox.showerror('Ошибка', 'Название категории должно содержать только буквы, цифры и пробелы')
            return
            
        ok, err = update_category(self.selected_id, name, desc)
        if ok:
            self.refresh_table()
        else:
            messagebox.showerror('Ошибка', err or 'Ошибка редактирования')

    def delete_category(self):
        if not self.selected_id:
            messagebox.showerror('Ошибка', 'Выберите категорию для удаления')
            return
        ok, err = delete_category(self.selected_id)
        if ok:
            self.refresh_table()
            self.name_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.selected_id = None
        else:
            messagebox.showerror('Ошибка', err or 'Ошибка удаления')

class FavoritesFrame(ThemedFrame):
    def __init__(self, master, on_back, user):
        super().__init__(master, bg=master['bg'])
        self.user = user
        
        # Добавляем кнопку НАЗАД сразу после инициализации фрейма
        # Используем стандартный синий стиль кнопки
        back_btn = ttk.Button(
            self, 
            text="Назад", 
            command=on_back, 
            style='Rounded.TButton',
            width=20  # Делаем кнопку стандартной ширины
        )
        # Размещаем кнопку внизу
        back_btn.pack(side='bottom', pady=20, ipady=5)
        
        tk.Label(self, text='Избранное', font=('Arial', 20), fg=master.style.lookup('TButton', 'foreground'), bg=master['bg']).pack(pady=10)
        
        # Создаем рамку для таблицы с заметной обводкой
        table_frame = tk.Frame(self, bg=master['bg'], highlightthickness=0, bd=0)
        table_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        columns = ('id', 'name', 'category', 'location', 'date', 'desc', 'favorite')
        self.table = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)  # Увеличил высоту с 7 до 12
        self.table.heading('id', text='ID')
        self.table.heading('name', text='Название')
        self.table.heading('category', text='Категория')
        self.table.heading('location', text='Место')
        self.table.heading('date', text='Дата')
        self.table.heading('desc', text='Описание')
        self.table.heading('favorite', text='Избранное')
        
        # Настройка ширины колонок
        self.table.column('id', width=40)
        self.table.column('name', width=150)  # Увеличил ширину
        self.table.column('category', width=120)  # Увеличил ширину
        self.table.column('location', width=120)  # Увеличил ширину
        self.table.column('date', width=90)
        self.table.column('desc', width=220)  # Увеличил ширину
        self.table.column('favorite', width=80)
        
        # Добавляем прокрутку
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        self.table.pack(fill='both', expand=True)
        self.refresh_table()

        # Кнопка удаления из избранного
        action_btn = tk.Frame(self, bg=master['bg'])
        action_btn.pack(pady=10)
        ttk.Button(action_btn, text='Удалить из избранного', command=self.remove_fav, style='Rounded.TButton', width=30).pack(pady=5)

        self.table.bind('<<TreeviewSelect>>', self.on_select)
        self.selected_id = None

    def refresh_table(self):
        for row in self.table.get_children():
            self.table.delete(row)
        if self.user:
            favorites = get_favorites(self.user[0])
            for ev in favorites:
                self.table.insert('', 'end', values=(ev[0], ev[1], ev[2], ev[3], ev[4], ev[5], 'Да'))

    def on_select(self, event):
        sel = self.table.selection()
        if sel:
            vals = self.table.item(sel[0])['values']
            self.selected_id = vals[0]

    def remove_fav(self):
        if not self.selected_id:
            messagebox.showerror('Ошибка', 'Выберите мероприятие для удаления из избранного')
            return
        ok, err = remove_favorite(self.user[0], self.selected_id)
        if ok:
            self.refresh_table()
            self.selected_id = None
        else:
            messagebox.showerror('Ошибка', err or 'Ошибка удаления')

class SettingsFrame(ThemedFrame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=master['bg'])
        
        # Добавляем кнопку НАЗАД сразу после инициализации фрейма
        # Используем стандартный синий стиль кнопки
        back_btn = ttk.Button(
            self, 
            text="Назад", 
            command=on_back, 
            style='Rounded.TButton',
            width=20  # Делаем кнопку стандартной ширины
        )
        # Размещаем кнопку внизу
        back_btn.pack(side='bottom', pady=20, ipady=5)
        
        tk.Label(self, text='Настройки', font=('Arial', 20), fg=master.style.lookup('TButton', 'foreground'), bg=master['bg']).pack(pady=10)
        theme_frame = tk.Frame(self, bg=master['bg'])
        theme_frame.pack(pady=10)
        tk.Label(theme_frame, text='Тема:', fg=master.style.lookup('TButton', 'foreground'), bg=master['bg']).pack(side='left')
        self.theme_var = tk.StringVar(value=master.theme)
        ttk.Radiobutton(theme_frame, text='Тёмная', variable=self.theme_var, value='dark', command=lambda: master.set_theme('dark')).pack(side='left', padx=5)
        ttk.Radiobutton(theme_frame, text='Светлая', variable=self.theme_var, value='light', command=lambda: master.set_theme('light')).pack(side='left', padx=5)

    def update_theme(self, bg, fg, btn_bg, btn_fg):
        super().update_theme(bg, fg, btn_bg, btn_fg)

class ReportsFrame(ThemedFrame):
    def __init__(self, master, on_back):
        super().__init__(master, bg=master['bg'])
        self.master = master
        
        # Добавляем кнопку НАЗАД сразу после инициализации фрейма
        # Используем стандартный синий стиль кнопки
        back_btn = ttk.Button(
            self, 
            text="Назад", 
            command=on_back, 
            style='Rounded.TButton',
            width=20  # Делаем кнопку стандартной ширины
        )
        # Размещаем кнопку внизу
        back_btn.pack(side='bottom', pady=20, ipady=5)
        
        tk.Label(self, text='Отчеты', font=('Arial', 20), fg=master.style.lookup('TButton', 'foreground'), bg=master['bg']).pack(pady=10)
        
        # Создаем контейнер с фильтрами
        filter_container = tk.Frame(self, bg=master['bg'], highlightthickness=0, bd=0, padx=20, pady=15)
        filter_container.pack(pady=10, padx=20, fill='x')
        
        # Период (с выбором даты)
        period_frame = tk.Frame(filter_container, bg=master['bg'])
        period_frame.pack(fill='x', pady=5)
        
        tk.Label(period_frame, text='Период:', fg=master.style.lookup('TButton', 'foreground'), 
                bg=master['bg'], font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5)
        
        date_frame = tk.Frame(period_frame, bg=master['bg'])
        date_frame.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(date_frame, text='С:', fg=master.style.lookup('TButton', 'foreground'), 
                bg=master['bg']).grid(row=0, column=0, padx=5)
        self.date_from = DateEntry(date_frame, width=12, background=master.style.lookup('TButton', 'background'),
                                 foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd', font=('Arial', 9))
        self.date_from.grid(row=0, column=1, padx=5)
        
        tk.Label(date_frame, text='По:', fg=master.style.lookup('TButton', 'foreground'), 
                bg=master['bg']).grid(row=0, column=2, padx=5)
        self.date_to = DateEntry(date_frame, width=12, background=master.style.lookup('TButton', 'background'),
                               foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd', font=('Arial', 9))
        self.date_to.grid(row=0, column=3, padx=5)
        
        # Тип отчета
        report_type_frame = tk.Frame(filter_container, bg=master['bg'])
        report_type_frame.pack(fill='x', pady=5)
        
        tk.Label(report_type_frame, text='Тип отчета:', fg=master.style.lookup('TButton', 'foreground'), 
                bg=master['bg'], font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5)
        
        self.report_type_var = tk.StringVar(value="Все")
        report_types = ["Все", "По категориям", "По пользователям"]
        self.report_type_combo = ttk.Combobox(report_type_frame, textvariable=self.report_type_var, 
                                           values=report_types, width=20, state='readonly', 
                                           style='CustomCombobox.TCombobox')
        self.report_type_combo.grid(row=0, column=1, padx=10, pady=5)
        self.report_type_combo.bind("<<ComboboxSelected>>", self.on_report_type_change)
        
        # Категория
        self.category_frame = tk.Frame(filter_container, bg=master['bg'])
        self.category_frame.pack(fill='x', pady=5)
        
        tk.Label(self.category_frame, text='Категория:', fg=master.style.lookup('TButton', 'foreground'), 
                bg=master['bg'], font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5)
        
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(self.category_frame, textvariable=self.cat_var, width=20, 
                                    state='readonly', style='CustomCombobox.TCombobox')
        self.cat_combo.grid(row=0, column=1, padx=10, pady=5)
        self.refresh_categories()
        
        # Пользователь (скрыт по умолчанию)
        self.user_frame = tk.Frame(filter_container, bg=master['bg'])
        
        tk.Label(self.user_frame, text='Пользователь:', fg=master.style.lookup('TButton', 'foreground'), 
                bg=master['bg'], font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5)
        
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(self.user_frame, textvariable=self.user_var, width=20, 
                                     state='readonly', style='CustomCombobox.TCombobox')
        self.user_combo.grid(row=0, column=1, padx=10, pady=5)
        self.refresh_users()
        
        # Сортировка
        sort_frame = tk.Frame(filter_container, bg=master['bg'])
        sort_frame.pack(fill='x', pady=5)
        
        tk.Label(sort_frame, text='Сортировка:', fg=master.style.lookup('TButton', 'foreground'), 
                bg=master['bg'], font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5)
        
        self.sort_var = tk.StringVar(value="Дата (по убыванию)")
        sort_options = ["Дата (по убыванию)", "Дата (по возрастанию)", "Название (А-Я)", "Название (Я-А)"]
        self.sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var, values=sort_options, 
                                     width=20, state='readonly', style='CustomCombobox.TCombobox')
        self.sort_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Кнопки управления отчетом
        btn_frame = tk.Frame(filter_container, bg=master['bg'])
        btn_frame.pack(fill='x', pady=10)
        
        ttk.Button(btn_frame, text='Показать отчет', command=self.show_report, 
                 style='Rounded.TButton', width=20).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text='Экспорт в Excel', command=lambda: self.export_report('excel'), 
                 style='Rounded.TButton', width=20).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text='Экспорт в PDF', command=lambda: self.export_report('pdf'), 
                 style='Rounded.TButton', width=20).grid(row=0, column=2, padx=10, pady=5)
        
        # Таблица для отчета
        self.report_container = tk.Frame(self, bg=master['bg'], highlightthickness=0, bd=0)
        self.report_container.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Статус отчета
        self.status_label = tk.Label(self.report_container, text='Выберите параметры и нажмите "Показать отчет"', 
                                   fg=master.style.lookup('TButton', 'foreground'), bg=master['bg'], 
                                   font=('Arial', 11))
        self.status_label.pack(pady=10)
        
        # Создаем таблицу
        columns = ('id', 'name', 'category', 'location', 'date', 'description', 'favorite', 'username')
        self.table = ttk.Treeview(self.report_container, columns=columns, show='headings', height=10)
        
        # Настраиваем заголовки
        self.headings = {
            'id': 'ID', 'name': 'Название', 'category': 'Категория', 'location': 'Место', 
            'date': 'Дата', 'description': 'Описание', 'favorite': 'Избранное', 'username': 'Пользователь'
        }
        
        for col, text in self.headings.items():
            self.table.heading(col, text=text)
            # Устанавливаем ширину колонок
            width = 40 if col == 'id' else 80 if col in ['favorite', 'date'] else 100 if col == 'location' else 150
            self.table.column(col, width=width)
        
        # Добавляем полосу прокрутки
        scrollbar = ttk.Scrollbar(self.report_container, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.table.pack(fill='both', expand=True, pady=5, padx=5)
        
        # Скрываем фреймы по умолчанию
        self.user_frame.pack_forget()
        
        # Данные отчета
        self.report_data = []
        
        # Проверяем наличие данных в таблице Events после полной инициализации всех элементов интерфейса
        self.__check_data()

    def on_report_type_change(self, event):
        report_type = self.report_type_var.get()
        
        # Показываем/скрываем соответствующие фреймы
        if report_type == "По категориям":
            self.category_frame.pack(fill='x', pady=5)
            self.user_frame.pack_forget()
            # Обновляем заголовок для колонки пользователя
            self.table.heading('username', text=self.headings['username'])
        elif report_type == "По пользователям":
            self.user_frame.pack(fill='x', pady=5)
            self.category_frame.pack(fill='x', pady=5)  # Показываем категории для комбинированного отчета
            # Обновляем заголовок для колонки пользователя
            self.table.heading('username', text='Добавил в избранное')
        else:  # "Все"
            self.category_frame.pack(fill='x', pady=5)
            self.user_frame.pack(fill='x', pady=5)
            # Обновляем заголовок для колонки пользователя
            self.table.heading('username', text=self.headings['username'])

    def refresh_categories(self):
        cats = get_categories()
        self.cat_combo['values'] = ['Все'] + [c[1] for c in cats]
        self.cat_map = {c[1]: c[0] for c in cats}
        self.cat_combo.current(0)

    def refresh_users(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, user_name FROM Users')
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        self.user_combo['values'] = ['Все'] + [u[1] for u in users]
        self.user_map = {u[1]: u[0] for u in users}
        self.user_combo.current(0)

    def get_report_data(self):
        report_type = self.report_type_var.get()
        date_from = self.date_from.get_date()
        date_to = self.date_to.get_date()
        category = self.cat_var.get()
        user = self.user_var.get()
        sort_option = self.sort_var.get()
        
        try:
            # SQL запрос для получения данных
            conn = get_connection()
            cursor = conn.cursor()
            
            # Определяем SQL запрос в зависимости от типа отчета
            if report_type == "По пользователям":
                # Запрос для отчета по пользователям с объединением имен пользователей через GROUP_CONCAT
                sql = '''
                    SELECT e.event_id, e.event_name, c.category_name, e.location, e.event_date, 
                           e.description, e.favorite, IFNULL(GROUP_CONCAT(DISTINCT u.user_name SEPARATOR ', '), '') as user_names
                    FROM Events e
                    LEFT JOIN Categories c ON e.category = c.category_id
                    LEFT JOIN Favorites f ON e.event_id = f.event_id
                    LEFT JOIN Users u ON f.user_id = u.user_id
                '''
                params = []
                
                # Добавляем условия WHERE
                conditions = []
                
                # Условие для конкретного пользователя
                if user != "Все" and user:
                    conditions.append("u.user_name = %s")
                    params.append(user)
                
                # Добавляем условие категории
                if category != "Все" and category:
                    conditions.append("c.category_name = %s")
                    params.append(category)
                
                # Добавляем условие даты, если указаны даты
                if date_from and date_to:
                    conditions.append("(e.event_date BETWEEN %s AND %s OR e.event_date IS NULL)")
                    params.append(date_from)
                    params.append(date_to)
                
                # Формируем часть WHERE запроса
                if conditions:
                    sql += " WHERE " + " AND ".join(conditions)
                    
                # Группировка для объединения пользователей
                sql += " GROUP BY e.event_id, e.event_name, c.category_name, e.location, e.event_date, e.description, e.favorite"
            else:
                # Основной запрос для отчетов типа "Все" или "По категориям"
                # Используем LEFT JOIN с таблицей Favorites и Users, чтобы включить все мероприятия
                # GROUP_CONCAT объединяет имена пользователей через запятую
                sql = '''
                    SELECT e.event_id, e.event_name, c.category_name, e.location, e.event_date, 
                           e.description, e.favorite, 
                           IFNULL(GROUP_CONCAT(DISTINCT u.user_name SEPARATOR ', '), '') as user_names
                    FROM Events e
                    LEFT JOIN Categories c ON e.category = c.category_id
                    LEFT JOIN Favorites f ON e.event_id = f.event_id
                    LEFT JOIN Users u ON f.user_id = u.user_id
                '''
                params = []
                
                # Добавляем условия WHERE
                conditions = []
                
                # Добавляем условие даты, если указаны даты
                if date_from and date_to:
                    conditions.append("(e.event_date BETWEEN %s AND %s OR e.event_date IS NULL)")
                    params.append(date_from)
                    params.append(date_to)
                
                # Добавляем условие категории для отчетов типа "По категориям" или "Все"
                if category != "Все" and category:
                    conditions.append("c.category_name = %s")
                    params.append(category)
                
                # Добавляем условие пользователя для отчета типа "Все"
                if report_type == "Все" and user != "Все" and user:
                    conditions.append("(u.user_name = %s OR u.user_name IS NULL)")  # Показываем и мероприятия без избранного
                    params.append(user)
                
                # Формируем часть WHERE запроса
                if conditions:
                    sql += " WHERE " + " AND ".join(conditions)
                    
                # Группировка для объединения пользователей
                sql += " GROUP BY e.event_id, e.event_name, c.category_name, e.location, e.event_date, e.description, e.favorite"
            
            # Сортировка
            if sort_option == "Дата (по убыванию)":
                sql += " ORDER BY IFNULL(e.event_date, '2999-12-31') DESC"
            elif sort_option == "Дата (по возрастанию)":
                sql += " ORDER BY IFNULL(e.event_date, '2999-12-31') ASC"
            elif sort_option == "Название (А-Я)":
                sql += " ORDER BY e.event_name ASC"
            elif sort_option == "Название (Я-А)":
                sql += " ORDER BY e.event_name DESC"
            
            # Выполняем запрос с выводом отладочной информации
            print(f"SQL: {sql}")
            print(f"Params: {params}")
            
            cursor.execute(sql, params)
            data = cursor.fetchall()
            
            print(f"Rows fetched: {len(data)}")
            if len(data) > 0:
                print(f"First row: {data[0]}")
            
            cursor.close()
            conn.close()
            
            return data
            
        except Exception as e:
            messagebox.showerror("Ошибка запроса", f"Ошибка в запросе: {str(e)}")
            print(f"Error in get_report_data: {str(e)}")
            return []

    def show_report(self):
        # Очищаем таблицу
        for row in self.table.get_children():
            self.table.delete(row)
        
        # Получаем данные
        try:
            data = self.get_report_data()
            self.report_data = data  # Сохраняем для экспорта
            
            # Получаем тип отчета и выбранные параметры
            report_type = self.report_type_var.get()
            user = self.user_var.get()
            category = self.cat_var.get()
            
            # Обновляем статус с учетом выбранных фильтров
            status_text = f'Отчет содержит {len(data)} записей'
            
            # Добавляем информацию о типе отчета и фильтрах
            if report_type == "По пользователям":
                if user != "Все":
                    status_text += f' (Пользователь: {user}'
                else:
                    status_text += f' (Все пользователи'
                
                if category != "Все":
                    status_text += f', Категория: {category})'
                else:
                    status_text += ')'
            elif report_type == "По категориям":
                if category != "Все":
                    status_text += f' (Категория: {category})'
                else:
                    status_text += ' (Все категории)'
            else:
                filters = []
                if user != "Все":
                    filters.append(f'Пользователь: {user}')
                if category != "Все":
                    filters.append(f'Категория: {category}')
                
                if filters:
                    status_text += f' ({", ".join(filters)})'
            
            self.status_label.config(text=status_text)
            
            # Обновляем заголовок для колонки пользователя в зависимости от типа отчета
            if report_type == "По пользователям":
                self.table.heading('username', text='Добавил в избранное')
            else:
                self.table.heading('username', text=self.headings['username'])
            
            # Заполняем таблицу
            for row in data:
                # Преобразуем 'favorite' в текст
                row_list = list(row)
                if len(row_list) >= 7:  # Проверяем, что в строке достаточно элементов
                    row_list[6] = 'Да' if row[6] else 'Нет'
                    
                    # Если нет пользователя (не в избранном)
                    if len(row_list) >= 8 and (row_list[7] is None or row_list[7] == ''):
                        row_list[7] = "-"
                    
                    self.table.insert('', 'end', values=row_list)
                
        except Exception as e:
            error_msg = f"Не удалось сформировать отчет: {str(e)}"
            messagebox.showerror("Ошибка", error_msg)
            self.status_label.config(text='Ошибка формирования отчета')
            print(error_msg)

    def export_report(self, format_type):
        if not self.report_data:
            messagebox.showinfo("Информация", "Нет данных для экспорта. Сначала сформируйте отчет.")
            return
        
        report_type = self.report_type_var.get()
        date_from = self.date_from.get_date()
        date_to = self.date_to.get_date()
        
        # Форматируем даты для имени файла
        date_from_str = date_from.strftime('%Y-%m-%d')
        date_to_str = date_to.strftime('%Y-%m-%d')
        
        # Создаем имя файла
        default_filename = f"Отчет_{report_type}_{date_from_str}_{date_to_str}"
        
        if format_type == 'excel':
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=default_filename
            )
            
            if filename:
                try:
                    # Создаем DataFrame с данными отчета
                    columns = ['ID', 'Название', 'Категория', 'Место', 'Дата', 
                              'Описание', 'Избранное']
                    
                    # Добавляем правильное название колонки пользователя в зависимости от типа отчета
                    if report_type == "По пользователям":
                        columns.append('Добавил в избранное')
                    else:
                        columns.append('Пользователь')
                    
                    # Преобразуем данные (favorite в текст)
                    processed_data = []
                    for row in self.report_data:
                        row_list = list(row)
                        row_list[6] = 'Да' if row[6] else 'Нет'
                        if row_list[7] is None:
                            row_list[7] = "-"
                        processed_data.append(row_list)
                    
                    df = pd.DataFrame(processed_data, columns=columns)
                    
                    # Экспортируем в Excel
                    df.to_excel(filename, index=False)
                    messagebox.showinfo("Успех", f"Отчет успешно экспортирован в {filename}")
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось экспортировать отчет: {str(e)}")
        
        elif format_type == 'pdf':
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=default_filename
            )
            
            if filename:
                try:
                    # Создаем PDF документ с поддержкой Unicode
                    doc = SimpleDocTemplate(filename, pagesize=letter, encoding='UTF-8')
                    styles = getSampleStyleSheet()
                    
                    # Модифицируем стили для поддержки кириллицы
                    title_style = styles['Heading1']
                    title_style.alignment = TA_CENTER
                    try:
                        title_style.fontName = 'Arial-Bold'
                    except:
                        pass
                        
                    # Создаем параграф-стиль для ячеек таблицы
                    normal_style = styles['Normal']
                    try:
                        normal_style.fontName = 'Arial'
                    except:
                        pass
                    
                    elements = []
                    
                    # Заголовок отчета
                    title = Paragraph(f"Отчет {report_type} с {date_from_str} по {date_to_str}", title_style)
                    elements.append(title)
                    
                    # Добавляем пустую строку между заголовком и таблицей
                    elements.append(Paragraph("<br/><br/>", normal_style))
                    
                    # Данные для таблицы
                    columns = ['ID', 'Название', 'Категория', 'Место', 'Дата', 
                              'Описание', 'Избранное']
                    
                    # Добавляем правильное название колонки пользователя в зависимости от типа отчета
                    if report_type == "По пользователям":
                        columns.append('Добавил в избранное')
                    else:
                        columns.append('Пользователь')
                    
                    # Преобразуем данные (favorite в текст)
                    processed_data = []
                    for row in self.report_data:
                        row_list = list(row)
                        # Преобразуем все значения в строки для правильного отображения в PDF
                        for i in range(len(row_list)):
                            if row_list[i] is None:
                                row_list[i] = "-"
                            elif i == 6:  # Столбец "Избранное"
                                row_list[i] = 'Да' if row_list[i] else 'Нет'
                            else:
                                # Преобразуем все остальные значения в строки
                                row_list[i] = str(row_list[i])
                        processed_data.append(row_list)
                    
                    # Создаем таблицу для PDF с корректными размерами
                    col_widths = [1*cm, 3*cm, 3*cm, 3*cm, 2*cm, 4*cm, 2*cm, 3*cm]  # Задаем ширину столбцов
                    data = [columns] + processed_data
                    table = Table(data, colWidths=col_widths)
                    
                    # Стилизуем таблицу с кириллическими шрифтами
                    style = TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Arial-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Arial'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ])
                    
                    # Добавляем зебру (чередование цветов строк)
                    for i in range(1, len(data)):
                        if i % 2 == 0:
                            bc = colors.lightgrey
                        else:
                            bc = colors.white
                        style.add('BACKGROUND', (0, i), (-1, i), bc)
                    
                    table.setStyle(style)
                    elements.append(table)
                    
                    # Строим PDF
                    doc.build(elements)
                    messagebox.showinfo("Успех", f"Отчет успешно экспортирован в {filename}")
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось экспортировать отчет: {str(e)}")

    def __check_data(self):
        """Проверяет наличие данных и предлагает создать тестовые данные"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Events")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            if count == 0:
                if messagebox.askyesno("Информация", "В базе данных нет мероприятий. Создать тестовые данные для отчета?"):
                    # Убедимся, что все необходимые атрибуты инициализированы
                    if not hasattr(self, 'cat_combo') or self.cat_combo is None:
                        # Если self.cat_combo отсутствует, значит нужно сначала продолжить инициализацию фрейма
                        messagebox.showinfo("Информация", "Пожалуйста, дождитесь полной инициализации интерфейса перед созданием тестовых данных.")
                        return
                    
                    self.create_sample_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при проверке данных: {str(e)}")

    def create_sample_data(self):
        """Создает простые тестовые данные для отчетов"""
        try:
            # Дополнительная проверка перед началом создания данных
            if not hasattr(self, 'cat_combo') or not hasattr(self, 'cat_map'):
                messagebox.showinfo("Информация", "Интерфейс еще не полностью инициализирован. Пожалуйста, попробуйте позже.")
                return
                
            conn = get_connection()
            cursor = conn.cursor()
            
            # Проверяем наличие хотя бы одной категории
            cursor.execute("SELECT category_id FROM Categories LIMIT 1")
            cat_result = cursor.fetchone()
            
            if not cat_result:
                # Если категорий нет, создаем одну
                cursor.execute("INSERT INTO Categories (category_name, description) VALUES ('Тестовая категория', 'Тестовое описание')")
                conn.commit()
                cursor.execute("SELECT LAST_INSERT_ID()")
                cat_id = cursor.fetchone()[0]
            else:
                cat_id = cat_result[0]
            
            # Добавляем тестовые события на сегодня и ближайшие дни
            today = datetime.datetime.now().date()
            
            # Простые тестовые события
            test_events = [
                ("Тестовое событие 1", cat_id, today, "Тестовое место", "Описание события 1", "", 1),
                ("Тестовое событие 2", cat_id, today + datetime.timedelta(days=1), "Место 2", "Описание события 2", "", 0),
                ("Тестовое событие 3", cat_id, today + datetime.timedelta(days=2), "Место 3", "Описание события 3", "", 1)
            ]
            
            for event in test_events:
                cursor.execute("""
                    INSERT INTO Events (event_name, category, event_date, location, description, note, favorite)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, event)
                conn.commit()
            
            cursor.close()
            conn.close()
            
            # Обновляем списки в интерфейсе
            try:
                self.refresh_categories()
                messagebox.showinfo("Успех", "Тестовые данные успешно добавлены")
            except Exception as e:
                messagebox.showinfo("Информация", "Тестовые данные добавлены, но не удалось обновить интерфейс. Пожалуйста, обновите приложение.")
                print(f"Ошибка при обновлении интерфейса после добавления тестовых данных: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать тестовые данные: {str(e)}")

if __name__ == '__main__':
    app = EventDesignApp()
    app.mainloop() 