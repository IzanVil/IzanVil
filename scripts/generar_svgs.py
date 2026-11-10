#!/usr/bin/env python3
"""Genera los SVG del README del perfil.

Uso:  python3 scripts/generar_svgs.py
Escribe todo en assets/, en español (.es.svg) y en inglés (.en.svg).
Los textos están en TEXTOS y PROYECTOS: cámbialos ahí y vuelve a ejecutarlo.
Los logos de scripts/iconos.json vienen de Simple Icons (CC0).
"""
import json
import os
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get("SALIDA", RAIZ / "assets"))
ICONOS = json.loads((RAIZ / "scripts" / "iconos.json").read_text())

FONDO = "#0c0c0c"
BARRA = "#1b1b1b"
BORDE = "#2b2b2b"
ACENTO = os.environ.get("ACENTO", "#51A2DA")  # azul Fedora
ACENTO_CLARO = os.environ.get("ACENTO_CLARO", "#8cc4ec")
BORRADO = "#f85149"  # rojo de las líneas borradas, como en GitHub
TEXTO = "#d4d4d4"
GRIS = "#8a8a8a"
TENUE = "#5c5c5c"
MONO = "'JetBrains Mono','Fira Code','Cascadia Code',Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
CW = 0.6  # ancho de carácter monoespaciado respecto al tamaño de fuente

# Colores de lenguaje que usa GitHub
LENGUAJES = {
    "Python": "#3572A5", "Rust": "#dea584", "TypeScript": "#3178c6",
    "Svelte": "#ff3e00", "C#": "#178600", "GDScript": "#355570",
}


def e(t: str) -> str:
    return escape(t, {'"': "&quot;"})


def svg(w: int, h: int, cuerpo: str, alt: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{e(alt)}">'
        f"<title>{e(alt)}</title>{cuerpo}\n</svg>\n"
    )


def terminal(w: int, h: int, titulo: str) -> str:
    """Ventana sencilla, como la de Konsole: barra con título y botones a la derecha."""
    return f"""
  <rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="8" fill="{FONDO}" stroke="{BORDE}"/>
  <path d="M8.5 0.5 H{w-8.5} A8 8 0 0 1 {w-0.5} 8.5 V32 H0.5 V8.5 A8 8 0 0 1 8.5 0.5 Z" fill="{BARRA}"/>
  <line x1="0.5" y1="32" x2="{w-0.5}" y2="32" stroke="{BORDE}"/>
  <text x="{w/2}" y="21" text-anchor="middle" font-family="{SANS}" font-size="12.5" fill="{GRIS}">{e(titulo)}</text>
  <g stroke="{GRIS}" stroke-width="1.4" fill="none" stroke-linecap="round">
    <path d="M{w-78} 16.5 h9"/>
    <path d="M{w-52} 12 l4.5 4.5 l4.5 -4.5"/>
    <path d="M{w-24} 12 l9 9 M{w-15} 12 l-9 9"/>
  </g>"""


def mostrar(t: float) -> str:
    """La salida de un comando aparece de golpe, como en una terminal de verdad."""
    return f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'


def prompt(x: float, y: float, fs: int) -> tuple[str, float]:
    c = fs * CW
    s = (
        f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{fs}" font-weight="700" fill="{ACENTO}" '
        f'textLength="{11*c:.1f}" lengthAdjust="spacingAndGlyphs">izan@fedora</text>'
        f'<text x="{x+11*c:.1f}" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{TEXTO}" '
        f'textLength="{3*c:.1f}" lengthAdjust="spacingAndGlyphs">:~$</text>'
    )
    return s, x + 15 * c


def comando(ident: str, x: float, y: float, texto: str, inicio: float, fs: int, vel: float = 0.055) -> tuple[str, float]:
    """Comando que se teclea letra a letra. Devuelve (svg, instante en que termina)."""
    c = fs * CW
    n = len(texto)
    anchos = ";".join(f"{i*c:.1f}" for i in range(n + 1))
    tiempos = ";".join(f"{i/n:.4f}" for i in range(n + 1))
    s = f"""
  <clipPath id="{ident}"><rect x="{x:.1f}" y="{y-fs}" width="0" height="{fs*1.5}">
    <animate attributeName="width" values="{anchos}" keyTimes="{tiempos}" calcMode="discrete" begin="{inicio:.2f}s" dur="{n*vel:.2f}s" fill="freeze"/>
  </rect></clipPath>
  <text x="{x:.1f}" y="{y}" clip-path="url(#{ident})" font-family="{MONO}" font-size="{fs}" fill="{TEXTO}" textLength="{n*c:.1f}" lengthAdjust="spacingAndGlyphs">{e(texto)}</text>"""
    return s, inicio + n * vel


def cursor(x: float, y: float, inicio: float, fs: int) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y-fs*0.8:.1f}" width="{fs*CW:.1f}" height="{fs:.1f}" fill="{TEXTO}" opacity="0">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.06s" begin="{inicio:.2f}s" repeatCount="indefinite"/></rect>'
    )


# Letras de 5x7 para el "figlet" de la cabecera
LETRAS = {
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#.#.#", "#..##", "#...#", "#...#"],
}


def pixeles(palabra: str, x: float, y: float, px: float) -> str:
    out = []
    for k, letra in enumerate(palabra):
        for i, fila in enumerate(LETRAS[letra]):
            for j, c in enumerate(fila):
                if c == "#":
                    out.append(f'<rect x="{x + (k*6 + j)*px:.1f}" y="{y + i*px:.1f}" width="{px-1.5:.1f}" height="{px-1.5:.1f}" fill="{ACENTO}"/>')
    return "".join(out)


TEXTOS = {
    "es": {
        "alt_cab": "Terminal: Izan Vílchez, estudiante de ASIR en Madrid. Busco prácticas de sistemas / DevOps.",
        "fichero": "sobre-mi.txt",
        "sobre": [
            "Izan Vílchez. Estudio ASIR en Madrid, después de sacarme SMR.",
            "Aprendo montando cosas que se puedan usar de verdad: simuladores,",
            "herramientas de datos y algún juego.",
            "Ahora mismo busco prácticas de sistemas / DevOps.",
        ],
        "azure_titulo": "Contribuciones a Microsoft Azure Linux",
        "azure_sub": "3 pull requests fusionadas · 4 archivos",
        "archivos": "archivo|archivos",
        "fusionada": "Merged",
        "servicio": "Izan Vílchez · estudiante de ASIR",
        "activo": "since 2024; aprendiendo",
        "modulos": [
            ("cloud-privada", "Proxmox VE · ZFS · iSCSI"),
            ("redes", "VLANs · Packet Tracer"),
            ("sistemas", "Linux · Windows"),
            ("bases-de-datos", "SQL · MariaDB"),
        ],
        "diario": [
            ("2024", "empiezo SMR"),
            ("2026", "termino SMR y empiezo ASIR"),
            ("2026", "3 PR fusionadas en Microsoft Azure Linux"),
            ("ahora", "busco prácticas de sistemas / DevOps"),
        ],
        "stack1": "sistemas",
        "stack2": "desarrollo",
    },
    "en": {
        "alt_cab": "Terminal: Izan Vílchez, sysadmin student in Madrid. Looking for a systems / DevOps internship.",
        "fichero": "about-me.txt",
        "sobre": [
            "Izan Vílchez. I study network systems administration (ASIR)",
            "in Madrid. I learn by building things people can actually use:",
            "simulators, data tools and the odd game.",
            "Right now I'm looking for a systems / DevOps internship.",
        ],
        "azure_titulo": "Contributions to Microsoft Azure Linux",
        "azure_sub": "3 merged pull requests · 4 files",
        "archivos": "file|files",
        "fusionada": "Merged",
        "servicio": "Izan Vílchez · sysadmin student",
        "activo": "since 2024; learning",
        "modulos": [
            ("private-cloud", "Proxmox VE · ZFS · iSCSI"),
            ("networking", "VLANs · Packet Tracer"),
            ("systems", "Linux · Windows"),
            ("databases", "SQL · MariaDB"),
        ],
        "diario": [
            ("2024", "start SMR (IT systems & networks)"),
            ("2026", "finish SMR, start ASIR"),
            ("2026", "3 PRs merged into Microsoft Azure Linux"),
            ("now", "looking for a systems / DevOps internship"),
        ],
        "stack1": "systems",
        "stack2": "development",
    },
}

# (repo, número, título del commit, archivos, +líneas, -líneas)
PRS = [
    ("microsoft/azurelinux", "18982", "docs(ci): fix broken links in ADO pipeline instructions", 1, 2, 2),
    ("microsoft/azurelinux", "18984", "fix(publish): close base channel over rpmlint and dpkg-perl deps", 1, 8, 0),
    ("microsoft/azure-linux-dev-tools", "392", "docs(config): document user-level override of project output directories", 2, 15, 0),
]

# Qué hace cada PR, explicado en corto
PRS_DESC = {
    "18982": {
        "es": "Las instrucciones del pipeline de Azure DevOps enlazaban con rutas desde la raíz y GitHub las mostraba como 404. Las cambié a rutas relativas.",
        "en": "The Azure DevOps pipeline instructions linked with repo-root paths, which GitHub rendered as 404s. I switched them to relative paths.",
    },
    "18984": {
        "es": "Al canal de publicación base le faltaban dependencias. Añadí los paquetes que necesitaba y saqué devscripts a sdk para no arrastrar perl y dpkg-dev.",
        "en": "The base publish channel was missing dependencies. I added the packages it needs and moved devscripts to sdk so perl and dpkg-dev stay out.",
    },
    "392": {
        "es": "Documenté cómo cambiar, a nivel de usuario, las carpetas de salida de un proyecto, en la guía del sistema de configuración y en la referencia.",
        "en": "Documented how to override a project's output directories at user level, in the config system guide and in the reference.",
    },
}

PROYECTOS = [
    {
        "id": "ripplerack", "nombre": "RippleRack", "version": "v0.2.4", "extra": "PyPI",
        "desc": {
            "es": "Simulador local de centros de datos y pipelines de datos. Describes racks, servidores y servicios en un YAML y te dice qué se rompe si cambias algo: un esquema, la carga o un servidor caído.",
            "en": "Local simulator for datacenters and data pipelines. You describe racks, servers and services in one YAML file and it tells you what breaks when something changes: a schema, the load or a server going down.",
        },
        "lenguajes": ["Python"],
    },
    {
        "id": "datasemver", "nombre": "datasemver", "version": "v0.8.2", "extra": "PyPI · Action",
        "desc": {
            "es": "Compara dos versiones de un dataset y te dice si el cambio es patch, minor o breaking.",
            "en": "Compares two versions of a dataset and tells you if the change is a patch, minor or breaking.",
        },
        "lenguajes": ["Python"],
    },
    {
        "id": "mosaic", "nombre": "mosaic", "version": "v0.3.0", "extra": "Linux · Win · macOS",
        "desc": {
            "es": "App de escritorio para ver todos mis proyectos y su estado de Git de un vistazo.",
            "en": "Desktop app to see all my projects and their Git status at a glance.",
        },
        "lenguajes": ["TypeScript", "Rust", "Svelte"],
    },
    {
        "id": "uptime", "nombre": "rack-and-ruin", "version": "UPTIME", "extra": "se juega en el navegador",
        "extra_en": "plays in the browser",
        "desc": {
            "es": "UPTIME · Turno de Noche: simulador de mantenimiento de un centro de datos.",
            "en": "UPTIME · Night Shift: a data center maintenance simulator.",
        },
        "lenguajes": ["C#"],
    },
    {
        "id": "tambor", "nombre": "last-click-game", "version": "v0.1.0-beta", "extra": "Linux · Windows",
        "desc": {
            "es": "El Tambor del Juicio: juego de deducción para la terminal y en Godot.",
            "en": "El Tambor del Juicio: a deduction game for the terminal and in Godot.",
        },
        "lenguajes": ["Python", "GDScript"],
    },
]

STACK_SISTEMAS = [
    ("linux", "Linux"), ("debian", "Debian"), ("fedora", "Fedora"), ("proxmox", "Proxmox"),
    ("docker", "Docker"), ("gnubash", "Bash"), ("git", "Git"), ("githubactions", "Actions"),
    ("cloudflare", "Cloudflare"), ("apache", "Apache"), ("mariadb", "MariaDB"), ("cisco", "Cisco"),
]
STACK_DESARROLLO = [
    ("python", "Python"), ("rust", "Rust"), ("typescript", "TypeScript"), ("svelte", "Svelte"),
    ("tauri", "Tauri"), ("godotengine", "Godot"), ("unity", "Unity"), ("claudecode", "Claude Code"),
]

def icono(slug: str, x: float, y: float, tam: float, color: str) -> str:
    esc = tam / 24
    return f'<path transform="translate({x:.1f} {y:.1f}) scale({esc:.4f})" d="{ICONOS[slug]}" fill="{color}"/>'


# ---------------------------------------------------------------- piezas


def cabecera(lang: str) -> str:
    T = TEXTOS[lang]
    w, fs, x0 = 1000, 17, 28
    lh = 27
    h = 72 + 84 + 34 + lh * (len(T["sobre"]) + 2) + 26
    p1, xc = prompt(x0, 64, fs)
    c1, fin1 = comando("c1", xc, 64, "figlet izan", 0.4, fs)
    figlet = f'<g opacity="0">{mostrar(fin1 + 0.15)}{pixeles("IZAN", x0, 84, 12)}</g>'
    y2 = 84 + 84 + 40
    p2, xc2 = prompt(x0, y2, fs)
    p2 = f'<g opacity="0">{mostrar(fin1 + 0.35)}{p2}</g>'
    c2, fin2 = comando("c2", xc2, y2, f"cat {T['fichero']}", fin1 + 0.7, fs)
    lineas = "".join(
        f'<text x="{x0}" y="{y2 + lh*(i+1)}" font-family="{MONO}" font-size="{fs}" fill="{TEXTO}">{e(l)}</text>'
        for i, l in enumerate(T["sobre"])
    )
    salida = f'<g opacity="0">{mostrar(fin2 + 0.15)}{lineas}</g>'
    y3 = y2 + lh * (len(T["sobre"]) + 1) + 8
    p3, xc3 = prompt(x0, y3, fs)
    p3 = f'<g opacity="0">{mostrar(fin2 + 0.3)}{p3}</g>'
    cuerpo = terminal(w, h, "izan@fedora: ~ — Konsole") + p1 + c1 + figlet + p2 + c2 + salida + p3 + cursor(xc3, y3, fin2 + 0.3, fs)
    return svg(w, h, cuerpo, T["alt_cab"])


def envolver(texto: str, max_c: int) -> list[str]:
    lineas, actual = [], ""
    for pal in texto.split():
        if len(actual) + len(pal) + 1 > max_c and actual:
            lineas.append(actual)
            actual = pal
        else:
            actual = f"{actual} {pal}".strip()
    lineas.append(actual)
    return lineas


REPO_ICONO = (
    "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"
)


def tarjeta(p: dict, lang: str, ancha: bool = False) -> str:
    w = 1000 if ancha else 492
    max_c = 118 if ancha else 56
    desc = envolver(p["desc"][lang], max_c)
    h = 66 + 21 * len(desc) + 46
    extra = p.get("extra_en", p["extra"]) if lang == "en" else p["extra"]
    nombre_w = len(p["nombre"]) * 10.4
    partes = [
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="8" fill="{FONDO}" stroke="{BORDE}"/>',
        f'<path transform="translate(22 22)" d="{REPO_ICONO}" fill="{GRIS}"/>',
        f'<text x="48" y="35" font-family="{SANS}" font-size="17" font-weight="600" fill="{ACENTO_CLARO}">{e(p["nombre"])}</text>',
        f'<rect x="{56 + nombre_w:.1f}" y="21" width="{len(p["version"])*7.2 + 16:.1f}" height="20" rx="10" fill="none" stroke="{BORDE}"/>',
        f'<text x="{64 + nombre_w:.1f}" y="35" font-family="{MONO}" font-size="12" fill="{GRIS}">{e(p["version"])}</text>',
    ]
    for i, l in enumerate(desc):
        partes.append(f'<text x="22" y="{70 + i*21}" font-family="{SANS}" font-size="14" fill="{TEXTO}">{e(l)}</text>')
    y = 70 + 21 * len(desc) + 14
    x = 22
    for leng in p["lenguajes"]:
        partes.append(
            f'<circle cx="{x+6}" cy="{y-4.5}" r="6" fill="{LENGUAJES[leng]}"/>'
            f'<text x="{x+18}" y="{y}" font-family="{SANS}" font-size="12.5" fill="{GRIS}">{e(leng)}</text>'
        )
        x += 18 + len(leng) * 7.4 + 16
    partes.append(f'<text x="{x+4}" y="{y}" font-family="{SANS}" font-size="12.5" fill="{TENUE}">{e(extra)}</text>')
    return svg(w, h, "".join(partes), f'{p["nombre"]} — {p["desc"][lang]}')


def stack(lang: str) -> str:
    T = TEXTOS[lang]
    w = 1000
    tile, gap = 64, 14
    h = 32 + 2 * (26 + tile + 26) + 30
    partes = [terminal(w, h, "~/stack")]

    def fila(items, y, etiqueta):
        total = len(items) * tile + (len(items) - 1) * gap
        x = (w - total) / 2
        out = [f'<text x="{x:.1f}" y="{y}" font-family="{MONO}" font-size="12.5" fill="{TENUE}"># {e(etiqueta)}</text>']
        y += 12
        for slug, nombre in items:
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{tile}" height="{tile}" rx="8" fill="#141414" stroke="{BORDE}"/>')
            out.append(icono(slug, x + 16, y + 10, 32, "#e2e2e2"))
            out.append(f'<text x="{x + tile/2:.1f}" y="{y + tile - 8}" text-anchor="middle" font-family="{SANS}" font-size="10.5" fill="{GRIS}">{e(nombre)}</text>')
            x += tile + gap
        return "".join(out)

    partes.append(fila(STACK_SISTEMAS, 66, T["stack1"]))
    partes.append(fila(STACK_DESARROLLO, 66 + 26 + tile + 26, T["stack2"]))
    nombres = ", ".join(n for _, n in STACK_SISTEMAS + STACK_DESARROLLO)
    return svg(w, h, "".join(partes), f"Stack: {nombres}")


def boton(ident: str, texto: str, icono_svg: str, ancho: int) -> str:
    h = 34
    cuerpo = (
        f'<rect x="0.5" y="0.5" width="{ancho-1}" height="{h-1}" rx="6" fill="{FONDO}" stroke="{BORDE}"/>'
        f"{icono_svg}"
        f'<text x="38" y="22" font-family="{SANS}" font-size="13.5" font-weight="600" fill="{TEXTO}">{e(texto)}</text>'
    )
    return svg(ancho, h, cuerpo, texto)


def botones() -> dict[str, str]:
    globo = (
        f'<g transform="translate(13 9)" fill="none" stroke="{ACENTO}" stroke-width="1.5">'
        '<circle cx="8" cy="8" r="7.2"/><ellipse cx="8" cy="8" rx="3.2" ry="7.2"/><path d="M1 8h14M2.2 4.2h11.6M2.2 11.8h11.6"/></g>'
    )
    linkedin = (
        f'<rect x="13" y="9" width="16" height="16" rx="3" fill="{ACENTO}"/>'
        '<text x="21" y="22" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" fill="#0c0c0c">in</text>'
    )
    correo = icono("gmail", 12, 9, 17, ACENTO)
    return {
        "portfolio": boton("p", "Portfolio", globo, 122),
        "linkedin": boton("l", "LinkedIn", linkedin, 116),
        "email": boton("m", "Email", correo, 96),
    }


VERDE = "#11d116"
MORADO = "#8957e5"  # color de "Merged" en GitHub
AZURE = "#0089D6"


def azure_banner(lang: str) -> str:
    T = TEXTOS[lang]
    w, h = 1000, 92
    cuerpo = (
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="8" fill="{FONDO}" stroke="{BORDE}"/>'
        + icono("microsoftazure", 26, 22, 48, AZURE)
        + f'<text x="94" y="44" font-family="{SANS}" font-size="22" font-weight="700" fill="#f0f0f0">{e(T["azure_titulo"])}</text>'
        f'<text x="94" y="70" font-family="{MONO}" font-size="13.5" fill="{GRIS}">{e(T["azure_sub"])} · '
        f'<tspan fill="{VERDE}">+25</tspan> <tspan fill="{BORRADO}">−2</tspan></text>'
        f'<g transform="translate({w-150} 32)"><rect width="122" height="28" rx="14" fill="{MORADO}"/>'
        f'<g transform="translate(13 6)" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round">'
        '<circle cx="3.5" cy="3" r="2.2"/><circle cx="3.5" cy="13.5" r="2.2"/><circle cx="12.5" cy="8.2" r="2.2"/>'
        '<path d="M3.5 5.2 V11.3 M3.5 5.2 C3.5 8.2 7 8.2 10.3 8.2"/></g>'
        f'<text x="72" y="19" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="700" fill="#fff">3 merged</text></g>'
    )
    return svg(w, h, cuerpo, T["azure_titulo"])


def pr_terminal(i: int, lang: str) -> str:
    T = TEXTOS[lang]
    repo, num, titulo, archivos, mas, menos = PRS[i]
    desc = PRS_DESC[num][lang]
    w, fs = 324, 12.5
    lineas = envolver(titulo, 36)
    texto = envolver(desc, 44)
    # misma altura en las tres terminales
    max_t = max(len(envolver(t[2], 36)) for t in PRS)
    max_d = max(len(envolver(PRS_DESC[t[1]][lang], 44)) for t in PRS)
    h = 32 + 34 + 24 + 22 * max_t + 32 + 19 * max_d + 46 + 16
    p, xc = prompt(16, 56, fs)
    partes = [
        terminal(w, h, repo.split('/')[1]),
        p,
        f'<text x="{xc:.1f}" y="56" font-family="{MONO}" font-size="{fs}" fill="{TEXTO}">gh pr view {num}</text>',
        f'<text x="16" y="84" font-family="{MONO}" font-size="{fs}" fill="{GRIS}">{e(repo)} #{num}</text>',
    ]
    y = 84 + 24
    for l in lineas:
        partes.append(f'<text x="16" y="{y}" font-family="{MONO}" font-size="{fs+0.5}" font-weight="700" fill="#f0f0f0">{e(l)}</text>')
        y += 22
    y += 6 + 22 * (max_t - len(lineas))
    partes.append(
        f'<rect x="16" y="{y-15}" width="66" height="22" rx="11" fill="{MORADO}"/>'
        f'<text x="49" y="{y}" text-anchor="middle" font-family="{SANS}" font-size="12" font-weight="700" fill="#fff">{T["fusionada"]}</text>'
        f'<text x="92" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{GRIS}">IzanVil</text>'
    )
    y += 30
    for l in texto:
        partes.append(f'<text x="16" y="{y}" font-family="{SANS}" font-size="13" fill="#bdbdbd">{e(l)}</text>')
        y += 19
    y = h - 22
    partes.append(f'<line x1="16" y1="{y-20}" x2="{w-16}" y2="{y-20}" stroke="{BORDE}"/>')
    uno, varios = T["archivos"].split("|")
    partes.append(
        f'<text x="16" y="{y}" font-family="{MONO}" font-size="{fs}" xml:space="preserve">'
        f'<tspan fill="{GRIS}">{archivos} {uno if archivos == 1 else varios}  </tspan>'
        f'<tspan fill="{VERDE}">+{mas}</tspan> <tspan fill="{BORRADO}">−{menos}</tspan></text>'
    )
    # barrita de diffstat como la de GitHub (5 cuadros)
    total = mas + menos
    verdes = round(5 * mas / total)
    rojos = 5 - verdes if menos else 0
    for k in range(5):
        col = VERDE if k < verdes else (BORRADO if k < verdes + rojos else "#3a3a3a")
        partes.append(f'<rect x="{w - 16 - (5-k)*13}" y="{y-10}" width="10" height="10" rx="2" fill="{col}"/>')
    return svg(w, h, "".join(partes), f"{repo}#{num}: {titulo} (merged). {desc}")


def systemctl(lang: str) -> str:
    T = TEXTOS[lang]
    w, fs, lh = 1000, 14.5, 24
    c = fs * CW
    x0 = 28
    xk = x0 + 2 * c           # columna de claves alineadas a la derecha
    filas = 5 + len(T["modulos"]) + 1 + len(T["diario"])
    h = 32 + 44 + lh * filas + 42
    p, xc = prompt(x0, 62, fs)
    partes = [
        terminal(w, h, "izan@fedora: ~ — Konsole"), p,
        f'<text x="{xc:.1f}" y="62" font-family="{MONO}" font-size="{fs}" fill="{TEXTO}">systemctl status izan</text>',
    ]
    y = 62 + lh + 6
    partes.append(
        f'<text x="{x0}" y="{y}" font-family="{MONO}" font-size="{fs}"><tspan fill="{VERDE}">●</tspan>'
        f'<tspan fill="#f0f0f0" font-weight="700"> izan.service</tspan><tspan fill="{TEXTO}"> - {e(T["servicio"])}</tspan></text>'
    )

    def campo(clave, valor_svg, y):
        return (
            f'<text x="{xk + 10*c:.1f}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="{fs}" fill="{TEXTO}">{e(clave)}:</text>'
            f'<text x="{xk + 11.5*c:.1f}" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{TEXTO}">{valor_svg}</text>'
        )

    y += lh
    partes.append(campo("Loaded", "loaded (/etc/systemd/system/izan.service; enabled)", y))
    y += lh
    partes.append(campo("Active", f'<tspan fill="{VERDE}" font-weight="700">active (running)</tspan> {e(T["activo"])}', y))
    y += lh
    partes.append(campo("Docs", "https://miportfolio.i-vilches.workers.dev", y))
    y += lh
    copiloto = "Copiloto" if lang == "es" else "Copilot"
    partes.append(
        f'<text x="{xk + 10*c:.1f}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="{fs}" fill="{TENUE}">{copiloto}:</text>'
        f'<text x="{xk + 11.5*c:.1f}" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{TENUE}">Claude Code</text>'
    )
    y += lh
    partes.append(campo("CGroup", "/asir.slice/izan.service", y))
    xr = xk + 11.5 * c
    for i, (mod, cosas) in enumerate(T["modulos"]):
        y += lh
        rama = "└─" if i == len(T["modulos"]) - 1 else "├─"
        partes.append(
            f'<text x="{xr:.1f}" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{TENUE}" textLength="{2*c:.1f}" lengthAdjust="spacingAndGlyphs">{rama}</text>'
            f'<text x="{xr + 3*c:.1f}" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{ACENTO_CLARO}">{e(mod)}</text>'
            f'<text x="{xr + 19*c:.1f}" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{TEXTO}">{e(cosas)}</text>'
        )
    y += lh
    for cuando, que in T["diario"]:
        y += lh
        ahora = cuando in ("ahora", "now")
        partes.append(
            f'<text x="{x0}" y="{y}" font-family="{MONO}" font-size="{fs}" xml:space="preserve">'
            f'<tspan fill="{GRIS}">{e(cuando.ljust(6))}fedora izan[2024]: </tspan>'
            f'<tspan fill="{"#f0f0f0" if ahora else TEXTO}" font-weight="{700 if ahora else 400}">{e(que)}</tspan></text>'
        )
    return svg(w, h, "".join(partes), f"systemctl status izan — {T['servicio']}")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for viejo in OUT.glob("*.svg"):
        viejo.unlink()
    for nombre, contenido in botones().items():
        (OUT / f"boton-{nombre}.svg").write_text(contenido, encoding="utf-8")
    for lang in ("es", "en"):
        (OUT / f"cabecera.{lang}.svg").write_text(cabecera(lang), encoding="utf-8")
        (OUT / f"azure.{lang}.svg").write_text(azure_banner(lang), encoding="utf-8")
        for i in range(len(PRS)):
            (OUT / f"pr-{PRS[i][1]}.{lang}.svg").write_text(pr_terminal(i, lang), encoding="utf-8")
        (OUT / f"sobre-mi.{lang}.svg").write_text(systemctl(lang), encoding="utf-8")
        (OUT / f"stack.{lang}.svg").write_text(stack(lang), encoding="utf-8")
        for i, p in enumerate(PROYECTOS):
            (OUT / f"proyecto-{p['id']}.{lang}.svg").write_text(tarjeta(p, lang, ancha=(i == 0)), encoding="utf-8")
    print("SVG generados en", OUT)


if __name__ == "__main__":
    main()
