# Incorporación de fotografías reales de tableros impresos

Los 10 ejemplos actuales son sintéticos. Para completar la parte de versiones impresas del enunciado hacen falta capturas de papel real. No se incluyen fotografías generadas artificialmente como si fueran capturas de cámara.

## Tableros para imprimir y fotografiar

Imprime `01_4x4_digital.png` y `08_5x5_digital.png` en papel blanco, conservando el tablero completo y los signos. No escribas soluciones ni anotaciones sobre las hojas.

Toma al menos estas capturas:

| Nuevo archivo | Tablero impreso | Condición | JSON esperado que debe copiarse |
|---|---|---|---|
| `16_4x4_impreso_frontal.jpg` | `01_4x4_digital.png` | Vista frontal con luz uniforme | `01_4x4_digital.json` |
| `17_4x4_impreso_inclinado.jpg` | `01_4x4_digital.png` | Ángulo ligero, cuatro esquinas visibles | `01_4x4_digital.json` |
| `18_5x5_impreso_frontal.jpg` | `08_5x5_digital.png` | Vista frontal con luz uniforme | `08_5x5_digital.json` |
| `19_5x5_impreso_sombra.jpg` | `08_5x5_digital.png` | Sombra suave sobre parte del papel | `08_5x5_digital.json` |

La cuadrícula debe ocupar una parte importante de la foto. Incluye sus cuatro esquinas, enfoca los números y evita otros marcos grandes alrededor. Guarda la captura original como JPG o PNG. Si conservas la extensión PNG, cambia también el nombre indicado en la tabla.

## Cómo incorporar las capturas

1. Coloca la foto en `data/dataset/`.
2. Copia el JSON del tablero impreso y renómbralo para que coincida con el nombre de la foto. Por ejemplo, `16_4x4_impreso_frontal.jpg` debe acompañarse de `16_4x4_impreso_frontal.json`.
3. Conserva las pistas y relaciones originales en el JSON, aunque el OCR no las lea correctamente. El JSON representa la verdad esperada, no el resultado del extractor.
4. Ejecuta desde la raíz del repositorio:

```powershell
python -m scripts.evaluate_dataset data/dataset
```

5. Compara la extracción exacta y las soluciones con las referencias. Registra tanto los éxitos como los errores de estas fotos, sin adaptar las fotos hasta ocultar los fallos.

## Estado de esta parte del dataset

**Pendiente de capturas reales.** Las cuatro fotografías descritas todavía no existen en el repositorio y no se cuentan como imágenes del dataset. Se requieren las fotos originales para incorporarlas y evaluar la robustez en condiciones físicas.
