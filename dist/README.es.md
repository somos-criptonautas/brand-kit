# Criptonautas — kit de marca

[ENGLISH](README.md) | **ESPAÑOL**

Todo lo necesario para diseñar para la comunidad: logo, color, tipografía, imágenes, voz, splash y plantillas. Las reglas de uso están en la página pública, **https://criptonautas.co/kit**; este repositorio es la fuente de la que sale todo.

## Estructura

```
src/        el código que genera cada archivo
  simbolo.py      el símbolo, construido geométricamente (GUTTER = espacio entre figuras)
  nombre.py       el nombre "Criptonautas", reconstruido del PNG de 2023 (src/fuente/)
  horizontal.py   símbolo + nombre
  splash.py       animación de carga para Discourse
  kit.py          arma dist/, el ZIP y la página
  pagina.py       el HTML de la página
  discourse.json  esquema de color del tema de Discourse
fonts-src/  Inter Tight, Lora y Lato con su licencia OFL
dist/       archivos listos para usar (generados)
discourse/  imágenes para los settings de Discourse (logos, íconos, splash, push)
  tema/           el código de color del componente del tema (violeta de botón oscuro), como referencia
ghost/      imágenes para Design & branding y Newsletter de Ghost (ícono, logos, portada, social)
docs/       la página que se publica en criptonautas.co/kit (generada)
```

## Regenerar

```
pip install cairosvg numpy pillow scikit-image fonttools brotli
make
```

`make` primero verifica (simetría del símbolo, fidelidad del nombre respecto del original, animación sin SMIL) y después regenera `dist/` y `docs/`. Si una verificación falla, no se genera nada. Ningún archivo generado lleva metadatos.

**Para actualizar el logo:** cambiar `src/simbolo.py` o `src/nombre.py`, correr `make` y revisar `docs/index.html`. Todos los archivos, el ZIP y la página se actualizan juntos.

## Qué cambia en v1.3

- **Rojo Óxido** pasa a `#E5500A` (claro) y `#F3936A` (oscuro); antes `#E6211E` y `#F98E76`. Los nombres no cambian (`rojo-oxido`, `--cn-rojo-oxido`, las claves de `tokens.json`), así que nada que los use se rompe. El rojo claro da 3,07:1 sobre Paper: solo texto grande y gráficos, como antes.
- **Violeta Tinta · botones** `#8E4CFF`, token solo de modo oscuro (`--cn-violeta-boton`): fondo de botones primarios con texto blanco, 4,54:1. Los enlaces siguen en `#C89DFF`, porque `#8E4CFF` como texto sobre `#181719` da solo 3,94:1. El código de Discourse que lo aplica está en `discourse/tema/`.
- **Lato** se suma a la tipografía: texto e interfaz del foro. Inter Tight sigue en los titulares de todas las superficies y Lora en la lectura larga del blog.
- Los TTF del ZIP se recortan al set latino que usa el kit (siguen siendo instalables y conservan los ejes variables): el ZIP baja a ~1 MB. `fonts-src/` conserva los archivos completos.
- **Splash** más lento: de 0,55 s a 0,9 s por paso en `src/splash.py` (`discourse/splash.svg` ya iba a 0,9 s).
- `make` no regenera `discourse/` ni `ghost/`: su rojo se cambió en el lugar. Las imágenes ya subidas a Discourse o Ghost hay que volver a subirlas, y en la paleta del foro hay que actualizar `quaternary` a mano.

## Splash en Discourse

1. Activar la imagen de splash en `/admin/config/upcoming-changes`.
2. Subir `dist/splash/criptonautas-splash.svg` en el ajuste `splash screen image`.
3. Revisar en modo claro y oscuro: los colores salen del tema.

## Portadas automáticas

Las portadas automáticas para los posts de Ghost sin imagen destacada, y para los topics de wiki, curso y glosario de Discourse, las genera [criptonautas-featured-cover](https://github.com/somos-criptonautas/criptonautas-featured-cover), sobre la plantilla 1200×630 de este kit.

## Publicar con nginx

```nginx
location = /kit { return 301 /kit/; }
location /kit/ {
    alias /srv/brand-kit/docs/;
    index index.html;
    location ~* \.(svg|png|woff2|zip)$ { expires 7d; add_header Cache-Control "public"; }
}
```

Las rutas de la página son relativas: funciona en `/kit/` o en cualquier otra carpeta.

## Contribuir

Ver [`CONTRIBUTING.md`](CONTRIBUTING.md) para los cambios al kit y la [guía de la organización](https://github.com/somos-criptonautas/.github/blob/main/CONTRIBUTING.md) para las convenciones generales.

## Licencia

Código MIT; plantillas y textos CC BY-NC-SA 4.0; logo y nombre de uso abierto con reglas; tipografías OFL. Detalle en [`LICENSE.md`](LICENSE.md).

Texto de este README bajo [CC BY-NC-SA 4.0](CC-BY-NC-SA-4.0.txt).
