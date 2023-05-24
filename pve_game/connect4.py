import pygame
import sys
import math
import random
import imageio
import time
from functions import (
    createBoard,
    dropPiece,
    isValidLoc,
    getNextOpenRow,
    printBoard,
    winMove,
    isTied,
    minimax,
    isInRect,
)
from constants import (
    ROW,
    COL,
    SQUARESIZE,
    SIZE,
    RADIUS,
    WIDTH,
    HEIGHT,
    RED,
    BLUE,
    LBLUE,
    WHITE,
    YELLOW,
    BLACK,
    PLAYER,
    AI,
    PLAYER_PIECE,
    AI_PIECE,
)


def render_board(board):
    for c in range(COL):
        for r in range(ROW):
            pygame.draw.rect(
                screen,
                BLUE,
                (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE),
            )
            pygame.draw.circle(
                screen,
                WHITE,
                (
                    int(c * SQUARESIZE + SQUARESIZE / 2),
                    int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2),
                ),
                RADIUS,
            )

    for c in range(COL):
        for r in range(ROW):
            if board[r][c] == 1:
                pygame.draw.circle(
                    screen,
                    RED,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        HEIGHT - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )
            elif board[r][c] == 2:
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        HEIGHT - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )
    pygame.display.update()


pygame.init()

menuFont = pygame.font.SysFont("comicsansms", 30)
titleFont = pygame.font.SysFont("comicsansms", 100)
gameFont = pygame.font.SysFont("comicsansms", 75)

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Connect 4")

loading_surface = pygame.Surface(SIZE)
loading_surface.fill(BLACK)
screen.blit(loading_surface, (0, 0))

loadingText = gameFont.render("Loading...", True, WHITE)
loadingRect = loadingText.get_rect(center=(WIDTH / 2, HEIGHT / 2))
screen.blit(loadingText, loadingRect)
pygame.display.flip()

gifReader = imageio.get_reader("background.gif")

gifSurfaces = []
for frame in gifReader:
    frame_rgb = frame[:, :, :3]  # Extract RGB channels
    gifSurface = pygame.surfarray.make_surface(frame_rgb)
    gifSurface = pygame.transform.scale(gifSurface, SIZE)
    gifSurfaces.append(gifSurface)

levelOpts = [1, 2, 3, 4, 5, 6]
chosenLevel = levelOpts[0]

menu_running = True
while menu_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                chosenLevel = max(chosenLevel - 1, levelOpts[0])
            elif event.key == pygame.K_DOWN:
                chosenLevel = min(chosenLevel + 1, levelOpts[-1])
            elif event.key == pygame.K_RETURN:
                menu_running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mousePos = pygame.mouse.get_pos()
            for idx, level in enumerate(levelOpts):
                levelRect = pygame.Rect(WIDTH // 2 - 50, 250 + idx * 50, 100, 40)
                if levelRect.collidepoint(mousePos):
                    chosenLevel = level

    frameIdx = pygame.time.get_ticks() // 100 % len(gifSurfaces)
    frameSurface = gifSurfaces[frameIdx]
    screen.blit(frameSurface, (0, 0))

    # Menu title
    titleText = titleFont.render("Connect 4", True, RED)
    titleRect = titleText.get_rect(center=(WIDTH // 2, 100))
    screen.blit(titleText, titleRect)

    # Level options
    levelText = menuFont.render("Choose Your Bot Level:", True, YELLOW)
    levelRect = levelText.get_rect(center=(WIDTH // 2, 200))
    screen.blit(levelText, levelRect)

    for idx, level in enumerate(levelOpts):
        levelColor = BLUE if level == chosenLevel else WHITE
        levelText = menuFont.render(f"Level {level}", True, levelColor)
        levelRect = levelText.get_rect(center=(WIDTH // 2, 250 + idx * 50))

        if isInRect(pygame.mouse.get_pos(), levelRect) and levelColor == WHITE:
            levelColor = LBLUE
            levelText = menuFont.render(f"Level {level}", True, levelColor)

        screen.blit(levelText, levelRect)

    pygame.display.update()

board = createBoard()
printBoard(board)
game_over = False
turn = random.randint(PLAYER, AI)

render_board(board)
pygame.display.update()

gameFont = pygame.font.SysFont("sans-serif", 75)

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, SQUARESIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Player 1
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if not isValidLoc(board, col):
                    continue

                pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, SQUARESIZE))
                row = getNextOpenRow(board, col)
                dropPiece(board, row, col, PLAYER_PIECE)

                if winMove(board, PLAYER_PIECE):
                    label = gameFont.render("Player Red wins!", 1, RED)
                    screen.blit(label, (140, 30))
                    game_over = True
                elif isTied(board):
                    label = gameFont.render("Game Tied!", 1, BLUE)
                    screen.blit(label, (210, 30))
                    game_over = True

                turn += 1
                turn = turn % 2

                printBoard(board)
                render_board(board)
    # AI
    if turn == AI and not game_over:
        col, minimax_score = minimax(board, chosenLevel, -math.inf, math.inf, True)
        if chosenLevel <= 5:
            time.sleep(0.8 - (0.2 * (chosenLevel - 1)))

        if not isValidLoc(board, col):
            continue

        row = getNextOpenRow(board, col)
        dropPiece(board, row, col, AI_PIECE)

        if winMove(board, AI_PIECE):
            label = gameFont.render("Player Yellow wins!", 1, YELLOW)
            screen.blit(label, (110, 30))
            game_over = True
        elif isTied(board):
            label = gameFont.render("Game Tied!", 1, BLUE)
            screen.blit(label, (210, 30))
            game_over = True

        printBoard(board)
        render_board(board)

        turn += 1
        turn = turn % 2

    if game_over:
        pygame.time.wait(3000)
