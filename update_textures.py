import pygame

def update_textures():
    pygame.init()
    
    # Use a dummy display for convert() if needed, but better to just skip
    # pygame.display.set_mode((1, 1), pygame.NOFRAME) 

    # 1. Update Floor Tiles
    print("Updating floor tiles...")
    floor = pygame.image.load('assets/textures/floor_tiles.png')
    # Create a green tint (matching plants avg: 46, 60, 29)
    tint = pygame.Surface(floor.get_size())
    tint.fill((100, 160, 80)) # Vibrant green tint
    floor.blit(tint, (0,0), special_flags=pygame.BLEND_MULT)
    pygame.image.save(floor, 'assets/textures/floor_tiles.png')
    
    # 2. Update Walls (HEXSTORM and WANTED)
    print("Updating wall textures...")
    base_wall = pygame.image.load('assets/textures/walls/wall_panel.png')
    
    # Create wall_hexstorm
    hex_src = pygame.image.load('assets/textures/walls/wall_hexstorm.png')
    hex_dest = base_wall.copy()
    # Most original posters are centered.
    poster_rect = (200, 100, 624, 824) 
    # Use BLEND_MAX or similar to keep the poster detail?
    # Actually, we can just blit it.
    hex_dest.blit(hex_src.subsurface(poster_rect), (200, 100))
    pygame.image.save(hex_dest, 'assets/textures/walls/wall_hexstorm.png')
    
    # Create wall_wanted_poster
    wanted_src = pygame.image.load('assets/textures/walls/wall_wanted_poster.png')
    wanted_dest = base_wall.copy()
    poster_rect_2 = (250, 150, 524, 724)
    wanted_dest.blit(wanted_src.subsurface(poster_rect_2), (250, 150))
    pygame.image.save(wanted_dest, 'assets/textures/walls/wall_wanted_poster.png')
    
    print("Done!")

if __name__ == "__main__":
    update_textures()
