# gui/widgets.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
from app.database import buscar_produtos_similares


class AutoCompleteCombobox(ttk.Combobox):
    """Combobox com autocomplete"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
    
    def handle_keyrelease(self, event):
        """Lida com liberação de teclas para autocomplete"""
        value = event.widget.get()
        
        if value == '':
            self['values'] = []
        elif len(value) >= 2:
            # Buscar produtos similares
            sugestoes = buscar_produtos_similares(value, limite=10)
            if sugestoes:
                self['values'] = sugestoes
                self.event_generate('<Down>')


class ValidatedEntry(ttk.Entry):
    """Entry com validação"""
    
    def __init__(self, parent, validate_type='float', **kwargs):
        super().__init__(parent, **kwargs)
        self.validate_type = validate_type
        self.valid = True
        
        if validate_type == 'float':
            vcmd = (self.register(self.validate_float), '%P')
            self.config(validate='key', validatecommand=vcmd)
        elif validate_type == 'date':
            vcmd = (self.register(self.validate_date), '%P')
            self.config(validate='key', validatecommand=vcmd)
    
    def validate_float(self, text):
        """Valida entrada como float"""
        if text == "":
            self.valid = True
            return True
        
        try:
            # Permite números, ponto e vírgula
            if text.replace(',', '').replace('.', '').isdigit():
                self.valid = True
                return True
            self.valid = False
            return False
        except:
            self.valid = False
            return False
    
    def validate_date(self, text):
        """Valida entrada como data"""
        if text == "":
            self.valid = True
            return True
        
        # Permite apenas números e barras
        if all(c.isdigit() or c == '/' for c in text):
            self.valid = True
            return True
        
        self.valid = False
        return False
    
    def get_float(self):
        """Retorna o valor como float"""
        text = self.get().replace(',', '.')
        try:
            return float(text)
        except:
            return 0.0
    
    def get_date(self):
        """Retorna o valor como date"""
        text = self.get()
        try:
            return datetime.strptime(text, "%d/%m/%Y").date()
        except:
            return None