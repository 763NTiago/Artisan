import os
import sys
from main.app import App

"""
Ponto de Entrada (Entry Point) - Artisan Desktop App

Este script inicializa a aplicação principal. Certifique-se de que
as dependências listadas em requirements.txt estejam instaladas.
"""

def main():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()