import pygame
import os

def analyze():
    pygame.init()
    path = r'c:\Users\Rawap\OneDrive\Bureaublad\HEXSTORM\assets\textures\enemy\boss\boss_sprites_no_bg.png'
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    img = pygame.image.load(path)
    w, h = img.get_size()
    print(f"Image Size: {w}x{h}")
    
    for cols, rows in [(4, 4), (8, 5), (10, 5), (8, 8), (4, 1)]:
        print(f"\n--- Testing Grid {cols}x{rows} ---")
        fw, fh = w // cols, h // rows
        for r in range(rows):
            row_data = []
            for c in range(cols):
                try:
                    sub = img.subsurface((c * fw, r * fh, fw, fh))
                    # Count non-transparent pixels
                    mask = pygame.mask.from_surface(sub)
                    row_data.append(mask.count())
                except:
                    row_data.append(-1)
            print(f"Row {r}: {row_data}")
    
    pygame.quit()

if __name__ == "__main__":
    analyze()
