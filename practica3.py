import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

def leer_imagen():
    """Lee una imagen y la convierte a escala de grises"""
    root = tk.Tk()
    root.withdraw()
    ruta = filedialog.askopenfilename(
        title="Seleccionar imagen",
        filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.bmp;*.tif")]
    )
    root.destroy()

    if not ruta:
        print("No seleccionaste ninguna imagen. Programa finalizado.")
        return None

    # Leer imagen en color y convertir a escala de grises
    imagen = cv2.imread(ruta)
    if imagen is None:
        print("No se pudo cargar la imagen.")
        return None
    
    imagen_gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    print(f"Imagen cargada: {imagen_gray.shape} - Rango: [{imagen_gray.min()}, {imagen_gray.max()}]")
    return imagen_gray

def mostrar_imagenes(original, comprimida, titulo_original="Original", titulo_comprimida="Comprimida"):
    """Muestra ambas imágenes lado a lado para comparación"""
    # Normalizar para visualización (escala 0-255)
    comprimida_display = normalizar_para_despliegue(comprimida)
    
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.imshow(original, cmap='gray', vmin=0, vmax=255)
    plt.title(titulo_original)
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.imshow(comprimida_display, cmap='gray', vmin=0, vmax=255)
    plt.title(titulo_comprimida)
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def normalizar_para_despliegue(matriz):
    """Aplica +128 y ajusta al rango [0,255] para visualización"""
    matriz_display = matriz + 128
    matriz_display = np.clip(matriz_display, 0, 255)
    return matriz_display.astype(np.uint8)

# --- Funciones por implementar en los siguientes pasos ---
def comprimir_imagen(matriz, bits):
    """Función principal de compresión"""
    pass

def calcular_valores_desconocidos(matriz):
    """Implementa el método de promedios"""
    pass

def calcular_matriz_error(original, aproximada):
    """[O] - [P]"""
    pass

def cuantizar_errores(matriz_error, bits):
    """Calcula θ y genera MEQ"""
    pass

def reconstruir_imagen(meq, aproximada, bits):
    """Genera MEQ⁻¹ y reconstruye"""
    pass

def interfaz_usuario():
    """Interfaz principal para selección de bits"""
    pass

# Función principal temporal para testing
def main():
    # Cargar imagen
    imagen = leer_imagen()
    if imagen is None:
        return
    
    # Mostrar imagen original
    plt.imshow(imagen, cmap='gray')
    plt.title("Imagen Original")
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    main()