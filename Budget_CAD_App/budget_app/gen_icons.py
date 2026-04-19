#!/usr/bin/env python3
"""Génère les icônes PNG pour la PWA BudgetCAD."""
import base64, struct, zlib, os

def make_png(size, bg_color=(10,15,30), accent=(59,130,246)):
    """Crée un PNG minimal avec un fond dégradé et le symbole $."""
    w = h = size
    raw = []
    for y in range(h):
        row = [0]  # filter byte
        for x in range(w):
            # Fond dégradé
            cx, cy = x - w//2, y - h//2
            dist = (cx**2 + cy**2) ** 0.5
            max_dist = (w//2) * 1.4
            t = min(1.0, dist / max_dist)

            r = int(bg_color[0] * (1-t*0.3) + accent[0] * t * 0.15)
            g = int(bg_color[1] * (1-t*0.3) + accent[1] * t * 0.15)
            b = int(bg_color[2] * (1-t*0.3) + accent[2] * t * 0.15)

            # Cercle de fond avec bordure accent
            margin = size * 0.08
            radius = w//2 - margin
            if dist <= radius + 2 and dist >= radius - 2:
                # Bordure
                alpha = int(min(255, max(0, (1 - abs(dist - radius) / 2) * 200)))
                r = int(r * (1 - alpha/255) + accent[0] * alpha/255)
                g = int(g * (1 - alpha/255) + accent[1] * alpha/255)
                b = int(b * (1 - alpha/255) + accent[2] * alpha/255)

            # Icône $ au centre
            rel_x = (x - w//2) / (w//2)
            rel_y = (y - h//2) / (h//2)
            in_dollar = (
                abs(rel_x) < 0.12 and abs(rel_y) < 0.55 or  # Barre verticale
                (rel_y < -0.1 and rel_y > -0.4 and abs(rel_x) < 0.25 and abs(rel_x) > 0.05) or  # Arc sup
                (rel_y > 0.1 and rel_y < 0.4 and abs(rel_x) < 0.25 and abs(rel_x) > 0.05)    # Arc inf
            )
            if dist <= radius and in_dollar:
                r, g, b = 255, 255, 255

            row.extend([r, g, b, 255])
        raw.append(bytes(row))

    def chunk(name, data):
        c = name + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    ihdr = chunk(b'IHDR', ihdr_data)

    raw_bytes = b''.join(raw)
    compressed = zlib.compress(raw_bytes, 9)
    idat = chunk(b'IDAT', compressed)
    iend = chunk(b'IEND', b'')

    return header + ihdr + idat + iend

# Générer les icônes
os.makedirs('/home/claude/budget_app', exist_ok=True)
for size in [192, 512]:
    png_data = make_png(size)
    with open(f'/home/claude/budget_app/icon-{size}.png', 'wb') as f:
        f.write(png_data)
    print(f"icon-{size}.png créé ({len(png_data)} bytes)")
