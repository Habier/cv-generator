CV GENERATOR - QUICK START
==========================

ENGLISH
-------

1. Copy cv.yml.example to cv.yml in the folder where you will run the app.
2. Edit cv.yml with your information.
3. Run cv-generator.exe on Windows or ./cv-generator on Linux.
4. Find the generated PDFs in the output folder.

Use another CV file:
  cv-generator.exe --cv path\to\cv.yml

Use another template:
  cv-generator.exe --template template-name

Templates are stored in the visible templates folder. To create one, copy an
existing template folder, rename it, and edit its cv.html.j2 and style.css.

Keep the executable, templates, and _deps folders together. Do not put private
CV data in cv.yml.example when redistributing the application.


ESPANOL
-------

1. Copia cv.yml.example como cv.yml en la carpeta desde la que usaras la app.
2. Edita cv.yml con tu informacion.
3. Ejecuta cv-generator.exe en Windows o ./cv-generator en Linux.
4. Encontraras los PDF generados en la carpeta output.

Usar otro archivo de CV:
  cv-generator.exe --cv ruta\al\cv.yml

Usar otra plantilla:
  cv-generator.exe --template nombre-template

Las plantillas estan en la carpeta visible templates. Para crear una, copia
una carpeta existente, cambiale el nombre y edita cv.html.j2 y style.css.

Manten juntos el ejecutable y las carpetas templates y _deps. No incluyas datos
privados en cv.yml.example cuando redistribuyas la aplicacion.
