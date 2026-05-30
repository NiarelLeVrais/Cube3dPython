import pygame
import sys
import math

WIDTH, HEIGHT = 800, 600
FPS = 100
FOCAL = 400

FACE = False
EDGES = True
ROTATE_X = False
ROTATE_Y = False
VERT = False

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Renderer")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None,30)

def project(x, y, z):
    sx = (x / z) * FOCAL + WIDTH // 2
    sy = -(y / z) * FOCAL + HEIGHT // 2
    return (int(sx),int(sy))

def draw_button(surface, label, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, (60,60,60), rect)
    pygame.draw.rect(surface, (200,200,200), rect, 2)
    text = font.render(label, True,(255,255,255))
    surface.blit(text, (x + (w - text.get_width()) // 2, y + (h - text.get_height()) // 2))
    return rect

vertices = [
    (-1, -1, -1),
    ( 1, -1, -1),
    ( 1,  1, -1),
    (-1,  1, -1),
    (-1, -1,  1),
    ( 1, -1,  1),
    ( 1,  1,  1),
    (-1,  1,  1),
]

edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # face arrière
    (4, 5), (5, 6), (6, 7), (7, 4),  # face avant
    (0, 4), (1, 5), (2, 6), (3, 7),  # liaisons
]

faces = [
    (0, 1, 2, 3),  # arrière
    (4, 5, 6, 7),  # avant
    (0, 1, 5, 4),  # bas
    (2, 3, 7, 6),  # haut
    (0, 3, 7, 4),  # gauche
    (1, 2, 6, 5),  # droite
]


angle_x = 0
angle_y = 0

dragging = None
drag_z = 0.0

def rotate(x, y, z, ax, ay):
    #Transfo x
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z*math.cos(ax)
    #Transfo y
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    return x, y, z

def unrotate(x,y,z,ax,ay):
    #Inverser par raport a rotate (sin et cos)
    x, z = x*math.cos(ay) - z*math.sin(ay), x*math.sin(ay) + z*math.cos(ay)
    y, z = y*math.cos(ax) + z*math.sin(ax), -y*math.sin(ax) + z*math.cos(ax)
    return x, y, z    

while True:
    pygame.display.set_caption(f"3D Renderer | FPS: {clock.get_fps():.0f}")
    screen.fill((0, 0, 0))  # fond noir


    rotated = [rotate(*v, angle_x, angle_y) for v in vertices]

    # BOUTON
    btn_rotatex = draw_button(screen, "Rotate X", 10, 10, 100, 35)
    btn_rotatey = draw_button(screen, "Rotate Y", 120, 10, 100, 35)
    btn_faces = draw_button(screen, "Faces", 10, 55, 100, 35)
    btn_edges = draw_button(screen, "Edges", 10, 100, 100, 35)
    btn_vert = draw_button(screen, "Verticies", 10, 145, 100, 35)

    # --- events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        #BOUTON
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_rotatex.collidepoint(event.pos):
                ROTATE_X = not ROTATE_X
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_rotatey.collidepoint(event.pos):
                ROTATE_Y = not ROTATE_Y
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_faces.collidepoint(event.pos):
                FACE = not FACE
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_edges.collidepoint(event.pos):
                EDGES = not EDGES
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_vert.collidepoint(event.pos):
                VERT = not VERT    
        if event.type == pygame.MOUSEBUTTONDOWN:       
            if VERT and not any(b.collidepoint(event.pos) for b in [btn_rotatex, btn_rotatey, btn_faces, btn_edges, btn_vert]):
                for i, v in enumerate(rotated):
                    p = project(v[0], v[1], v[2]+3)
                    if math.dist(p, event.pos) < 10:
                        dragging = i
                        drag_z = rotated[i][2]
                        ROTATE_X = False
                        ROTATE_Y = False
                        break
        if event.type == pygame.MOUSEMOTION and dragging is not None and VERT:
            mx, my = event.pos
            rx = (mx - WIDTH//2) * (drag_z+3) / FOCAL
            ry = -(my - HEIGHT//2) * (drag_z+3) / FOCAL
            vertices[dragging] = unrotate(rx, ry, drag_z, angle_x, angle_y)
        if event.type == pygame.MOUSEBUTTONUP and VERT:
            dragging = None
            

    #EVENT CONTROL                
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        angle_y -= 0.05
    if keys[pygame.K_RIGHT]:
        angle_y += 0.05
    if keys[pygame.K_UP]:
        angle_x += 0.05
    if keys[pygame.K_DOWN]:
        angle_x -= 0.05


    # --- draw ---



    if ROTATE_X:
        angle_x += 0.01
    if ROTATE_Y:
        angle_y += 0.01

    # Rendu 3D 
    LIGHT = (0.577, 0.577, -0.577)

    if FACE:
        face_list = []
        for face in faces:
            pts3d = [rotated[i] for i in face]
            avg_z = sum(p[2] for p in pts3d) / 4
            pts2d = [project(x, y, z + 3) for x, y, z in pts3d]
            ax = pts3d[1][0]-pts3d[0][0]; ay = pts3d[1][1]-pts3d[0][1]; az = pts3d[1][2]-pts3d[0][2]
            bx = pts3d[2][0]-pts3d[0][0]; by = pts3d[2][1]-pts3d[0][1]; bz = pts3d[2][2]-pts3d[0][2]
            nx = ay*bz - az*by
            ny = az*bx - ax*bz
            nz = ax*by - ay*bx
            nlen = math.sqrt(nx*nx + ny*ny + nz*nz)
            intensity = abs(nx*LIGHT[0] + ny*LIGHT[1] + nz*LIGHT[2]) / nlen
            color = (int(100*intensity), int(100*intensity), int(220*intensity))
            face_list.append((avg_z, pts2d, color))

        face_list.sort(key=lambda f: f[0], reverse=True)

        for avg_z, pts2d, color in face_list:
            pygame.draw.polygon(screen, color, pts2d)

    if EDGES:    
        for a, b in edges:
            x1, y1, z1 = rotated[a]
            x2, y2, z2 = rotated[b] 
            p1 = project(x1,y1,z1+3)
            p2 = project(x2,y2,z2+3)
            pygame.draw.line(screen, (255,255,255), p1, p2)

    if VERT:
        for v in rotated:
            pygame.draw.circle(screen, (255, 100, 100), project(v[0], v[1], v[2]+3), 5)

    pygame.display.flip()
    clock.tick(FPS)
