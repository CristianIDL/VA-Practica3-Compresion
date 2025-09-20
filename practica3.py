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

# --- Funciones por implementar la compresión ---
def comprimir_imagen(matriz, bits):
    """Función principal de compresión"""
    # Crear matriz de aproximación [P] con el mismo patrón del apunte
    aproximada = calcular_valores_desconocidos(matriz)
    
    # Calcular matriz de error [E] = [O] - [P]
    error = calcular_matriz_error(matriz, aproximada)
    
    # Cuantizar errores para obtener MEQ
    meq = cuantizar_errores(error, bits)
    
    # Reconstruir imagen final
    reconstruida = reconstruir_imagen(meq, aproximada, bits)
    
    return reconstruida

def calcular_valores_desconocidos(matriz):
    """Implementa el método de promedios - Patrón del apunte"""
    # Crear copia de la matriz original
    aproximada = matriz.copy().astype(np.float64)
    
    # Aplicar el patrón que vimos en clase
    # Para una imagen grande, aplicar este patrón en bloques 3x3
    height, width = matriz.shape
    
    # Asegurarnos de que la imagen tenga dimensiones múltiplos de 3
    # Para simplificar, trabajamos con el bloque completo
    for i in range(1, height, 2):  # Filas impares (1, 3, 5...)
        for j in range(1, width, 2):  # Columnas impares (1, 3, 5...)
            if i + 1 < height and j + 1 < width:
                # Aplicar el patrón del apunte para bloque 3x3
                # [i-1, j-1] [i-1, j] [i-1, j+1]
                # [i, j-1]   [b1]     [b2]
                # [i+1, j-1] [b3]     [b4]
                
                # b1 = promedio de todos los conocidos en el bloque
                conocidos = [
                    matriz[i-1, j-1], matriz[i-1, j], matriz[i-1, j+1],
                    matriz[i, j-1], matriz[i+1, j-1]
                ]
                b1 = np.mean(conocidos)
                aproximada[i, j] = b1
                
                # b2 = promedio de b1 y vecinos izquierda/arriba
                b2 = np.mean([b1, matriz[i-1, j], matriz[i-1, j+1]])
                aproximada[i, j+1] = b2
                
                # b3 = promedio de b1, b2 y vecinos conocidos
                b3 = np.mean([b1, b2, matriz[i, j-1], matriz[i+1, j-1]])
                aproximada[i+1, j] = b3
                
                # b4 = promedio de b1, b2, b3
                b4 = np.mean([b1, b2, b3])
                aproximada[i+1, j+1] = b4
    
    return aproximada


def calcular_matriz_error(original, aproximada):
    """[O] - [P]"""
    return original.astype(np.float64) - aproximada

def cuantizar_errores(matriz_error, bits):
    """Calcula θ y genera MEQ"""
    min_error = np.min(matriz_error)
    max_error = np.max(matriz_error)
    
    # Calcular θ (salto)
    theta = (max_error - min_error) / (2 ** bits)
    
    # Crear matriz MEQ (valores enteros que representan intervalos)
    meq = np.floor((matriz_error - min_error) / theta).astype(np.int32)
    
    # Asegurar que no exceda el rango permitido
    meq = np.clip(meq, 0, (2 ** bits) - 1)
    
    return meq

def reconstruir_imagen(meq, aproximada, bits):
    """Genera MEQ⁻¹ y reconstruye"""
    min_error = np.min(aproximada - aproximada)  # 0, pero mantenemos la estructura
    max_error = np.max(aproximada - aproximada)
    
    theta = (max_error - min_error) / (2 ** bits)
    
    # Reconstruir errores (MEQ⁻¹)
    errores_reconstruidos = meq.astype(np.float64) * theta + min_error
    
    # Reconstruir imagen final: [P] + MEQ⁻¹
    reconstruida = aproximada + errores_reconstruidos
    
    return reconstruida

def interfaz_usuario(imagen):
    """Interfaz principal para selección de bits"""
    def aplicar_compression():
        try:
            bits = int(entry_bits.get())
            if bits < 1 or bits > 8:
                raise ValueError("Bits fuera de rango")
            
            # Aplicar compresión
            imagen_comprimida = comprimir_imagen(imagen, bits)
            
            # Mostrar resultados
            mostrar_imagenes(imagen, imagen_comprimida, 
                           f"Original ({imagen.shape})", 
                           f"Comprimida ({bits} bits/píxel)")
            
        except ValueError as e:
            lbl_resultado.config(text=f"Error: {str(e)}", fg="red")
        except Exception as e:
            lbl_resultado.config(text=f"Error inesperado: {str(e)}", fg="red")

    # Crear ventana principal
    ventana = tk.Tk()
    ventana.title("Compresor de Imágenes")
    ventana.geometry("400x250")
    ventana.configure(bg="#f0f0f0")

    # Marco principal
    frame = tk.Frame(ventana, bg="#f0f0f0", padx=20, pady=20)
    frame.pack(expand=True, fill="both")

    # Título
    lbl_titulo = tk.Label(frame, 
                         text="Compresión de Imágenes", 
                         font=("Arial", 16, "bold"),
                         bg="#f0f0f0")
    lbl_titulo.pack(pady=(0, 20))

    # Información de la imagen
    info_text = f"Imagen: {imagen.shape[1]}x{imagen.shape[0]} píxeles"
    lbl_info = tk.Label(frame, text=info_text, font=("Arial", 10), bg="#f0f0f0")
    lbl_info.pack(pady=(0, 15))

    # Entrada para bits
    frame_bits = tk.Frame(frame, bg="#f0f0f0")
    frame_bits.pack(pady=10)

    lbl_bits = tk.Label(frame_bits, 
                       text="Bits por píxel (1-8):", 
                       font=("Arial", 11),
                       bg="#f0f0f0")
    lbl_bits.pack(side="left", padx=(0, 10))

    entry_bits = tk.Entry(frame_bits, 
                         font=("Arial", 11),
                         width=5,
                         justify="center")
    entry_bits.insert(0, "4")  # Valor por defecto
    entry_bits.pack(side="left")

    # Botón de compresión
    btn_comprimir = ttk.Button(frame, 
                              text="Comprimir Imagen", 
                              command=aplicar_compression,
                              style="Accent.TButton")
    btn_comprimir.pack(pady=15)

    # Etiqueta para resultados
    lbl_resultado = tk.Label(frame, 
                            text="",
                            font=("Arial", 10),
                            bg="#f0f0f0",
                            fg="green")
    lbl_resultado.pack(pady=5)

    # Configurar estilo moderno
    style = ttk.Style()
    style.configure("Accent.TButton", 
                   font=("Arial", 11, "bold"),
                   padding=(20, 10))

    # Centrar ventana en la pantalla
    ventana.update_idletasks()
    width = ventana.winfo_width()
    height = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (width // 2)
    y = (ventana.winfo_screenheight() // 2) - (height // 2)
    ventana.geometry(f"{width}x{height}+{x}+{y}")

    ventana.mainloop()


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

    # Mostrar interfaz de usuario
    interfaz_usuario(imagen)


if __name__ == "__main__":
    main()