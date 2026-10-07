# Dataset de prueba de Futoshiki

Este directorio contiene **10 imágenes y 10 JSON esperados** del mismo nombre. Las imágenes se pueden subir directamente al programa. Los JSON representan el tamaño, las pistas y las desigualdades correctas y sirven para evaluar la extracción.

| Imagen | Tamaño | Condición |
|---|---|---|
| `01_4x4_digital.png` | 4×4 | Digital, recomendada para iniciar la demo |
| `05_5x5_digital.png` | 5×5 | Digital |
| `08_5x5_digital.png` | 5×5 | Digital, recomendada para cambiar de tamaño |
| `09_4x4_perspectiva.png` | 4×4 | Ángulo ligero simulado |
| `10_5x5_perspectiva.png` | 5×5 | Ángulo ligero simulado |
| `11_4x4_gris.png` | 4×4 | Contraste reducido |
| `12_5x5_calida.png` | 5×5 | Iluminación cálida simulada |
| `13_4x4_sombra.png` | 4×4 | Sombra gradual simulada |
| `14_5x5_jpeg.jpg` | 5×5 | Compresión JPEG |
| `15_4x4_desenfoque.png` | 4×4 | Desenfoque leve simulado |

## Procedencia y alcance

Son imágenes de tableros sintéticos generadas para la demostración y adaptadas al extractor actual. Las variaciones de iluminación y perspectiva son simuladas. Todos los tableros tienen una solución única.

El conjunto contiene 10 archivos de imagen para probar el reconocimiento de la cuadrícula, los dígitos y los signos bajo varias condiciones de entrada. Cada PNG/JPG pasa por el OCR y el extractor al cargarse en el programa.

## Demostración en la aplicación

Inicia `streamlit run app.py` y usa **Puzzle image** para cargar `01_4x4_digital.png`. Después puedes cargar `08_5x5_digital.png` y `09_4x4_perspectiva.png` para mostrar el cambio de tamaño y la rectificación de perspectiva. La aplicación extrae automáticamente los datos desde los píxeles y muestra el JSON reconocido, el resultado del solver y la solución superpuesta.

Los JSON de este directorio son las referencias esperadas para el evaluador. Para demostrar el OCR, selecciona el PNG/JPG del tablero en el cargador de imágenes.

## Evaluación

Desde la raíz del repositorio, con las dependencias instaladas y Tesseract en PATH:

```powershell
python -m scripts.evaluate_dataset data/dataset
```

En el entorno preparado en este equipo:

```powershell
$env:Path = "$(Resolve-Path '../materiales/.build/tesseract');$env:Path"
..\.materiales-venv\Scripts\python.exe -m scripts.evaluate_dataset data/dataset
```

Los 10 ejemplos se comprobaron con el extractor sin modificar su código: el tamaño, las pistas y las relaciones coinciden con sus JSON esperados. Las soluciones también coinciden con las matrices esperadas. Este resultado corresponde únicamente a estos ejemplos preparados.

Las soluciones de referencia y el registro completo de los 15 ejemplos originales siguen en `../../../materiales/soluciones` y `../../../materiales/datos/validacion_ejemplos.json`, respectivamente, respecto a este archivo. Esos materiales externos al repositorio no son necesarios para ejecutar el evaluador.
