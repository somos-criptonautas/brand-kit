# Logos de categoría — prompts para Qwen Image

**Estado:** aprobado · **Fecha:** 2026-10-11 · paleta `color-system` v1.1
**Base:** Riso Symbol Plate de `imagery-guidelines.md`, variante limpia; paleta de `color-system` v1.1.

## Reglas

- Solo como **logo de categoría** (página de categoría e índice). Los badges de los listados siguen en Square o Icon. Sin imagen de fondo de categoría.
- Tinta `#14110F` + un único acento violeta `#5814EA` sobre Paper `#E8E6E1`. El rojo queda reservado.
- Sin desfase de tintas, sin trama de puntos, sin texto.
- Variante oscura: se vectoriza la elegida y se recolorea (tinta → `#E8E6E1`, violeta → `#7C36FF`). No se regenera.
- Flujo: 4 variantes a 2048×2048 → elegir 1 → vectorizar → exportar a 512 → comprobar lectura a 64 px.

## Cómo armar cada prompt

**Prompt = BASE + línea SÍMBOLO.** El NEGATIVO va en el campo de prompt negativo.

### BASE

```
Ícono editorial minimalista para una categoría de comunidad. Un único símbolo plano y centrado, construido con formas geométricas simples y trazo de tinta de grosor uniforme, ocupa el 60 % del lienzo con margen amplio alrededor. Placa de dos tintas: líneas y masas en negro tinta #14110F, un solo elemento de acento en violeta intenso #5814EA, sobre fondo liso gris papel claro #E8E6E1. Colores planos y mates, sin degradados, sin sombras, sin texturas, sin relieve. Sobrio, moderno y elegante, legible a 64 píxeles. Vista frontal y plana, sin perspectiva. Sin texto, sin letras, sin números.
```

### NEGATIVO

```
fotorrealismo, render 3D, volumen, sombra, degradado, brillo, neón, resplandor, cromo, holograma, sepia, papel envejecido, ornamento, filigrana, detalle excesivo, trama de puntos, textura, escena de fondo, rostros, retratos, robot, cohete, luna, toro, oso, velas japonesas, flechas hacia arriba, monedas, logotipos, texto, letras, números, marca de agua
```

### SÍMBOLO por categoría

| Categoría | Línea SÍMBOLO |
|---|---|
| Curso | `SÍMBOLO: una brújula circular sobre un mapa plegado en tres paneles; la aguja es el acento violeta.` |
| Análisis técnico | `SÍMBOLO: un compás de dibujo técnico abierto sobre una cuadrícula de líneas finas; el arco trazado es el acento violeta.` |
| En la mira | `SÍMBOLO: un faro de silueta simple con dos haces dibujados como bandas planas y rectas hacia los lados; los haces son el acento violeta.` |
| Líderes | `SÍMBOLO: un libro de registro cerrado con un sello circular estampado en la tapa; el sello es el acento violeta.` |
| Coaching | `SÍMBOLO: una antena de transmisión de silueta simple con tres arcos concéntricos a un lado; los arcos son el acento violeta.` |
