import pygame
import sys

def find_poster_bbox(poster_path, base_path):
    pygame.init()
    try:
        poster_img = pygame.image.load(poster_path)
        base_img = pygame.image.load(base_path)
    except Exception as e:
        print(f"Error loading images: {e}")
        return None

    w, h = poster_img.get_size()
    diffs = []
    
    # Sample every 4 pixels for speed
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            c1 = poster_img.get_at((x, y))
            c2 = base_img.get_at((x, y))
            # Check for significant difference
            if abs(c1.r - c2.r) > 15 or abs(c1.g - c2.g) > 15 or abs(c1.b - c2.b) > 15:
                diffs.append((x, y))
    
    if not diffs:
        return None
        
    min_x = min(d[0] for d in diffs)
    max_x = max(d[0] for d in diffs)
    min_y = min(d[1] for d in diffs)
    max_y = max(d[1] for d in diffs)
    
    return (min_x, min_y, max_x - min_x, max_y - min_y)

if __name__ == "__main__":
    bbox1 = find_poster_bbox('assets/textures/walls/wall_hexstorm.png', 'assets/textures/walls/wall_stone.png')
    print(f"HEXSTORM BBOX: {bbox1}")
    
    bbox2 = find_poster_bbox('assets/textures/walls/wall_wanted_poster.png', 'assets/textures/walls/wall_stone.png')
    print(f"WANTED BBOX: {bbox2}")
