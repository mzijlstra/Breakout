import pygame, os, sys, random

def main():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()

    size = width, height = 640, 480
    ballspeed = [2, 2]
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)

    #images and rectangles
    ballimg= pygame.image.load("ball4.png")
    ball = ballimg.get_rect()

    paddleimg = pygame.image.load("paddle.png")
    paddle = paddleimg.get_rect()
    paddle.left = (width / 2) - 16
    paddle.top = height - 20

    brickimg = pygame.image.load('brick.png')
    brickrect = brickimg.get_rect()
    bricks = []

    # create brick positions
    rows = 4
    cols = width / brickrect.width
    brickW = brickrect.width
    brickH = brickrect.height
    
    for row in range(rows):
        for col in range(cols):
            x = col * brickW
            y = 64 + row * brickH
            bricks.append(pygame.Rect(x, y, brickW, brickH))

    #game clock
    clock = pygame.time.Clock()

    # game state is either new or playing
    state = 'new'

    while True:

        # quit on window close or escape key
        for event in pygame.event.get():
            if event.type == pygame.QUIT \
               or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit_game()
                sys.exit()


        #move paddle based on left and right arrows
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle = paddle.move([-2, 0])
        if keys[pygame.K_RIGHT] and paddle.right < width:
            paddle = paddle.move([2, 0])

        if state == 'playing':
            #move ball, and bounce it against top / left / right (not bottom)
            ball = ball.move(ballspeed)
            if ball.left < 0 or ball.right > width:
                ballspeed[0] = -ballspeed[0]
            if ball.top < 0: # or ball.bottom > height:
                ballspeed[1] = -ballspeed[1]
                
            # if we hit the paddle
            if ball.colliderect(paddle):
                ballspeed[1] = -ballspeed[1]
                ballspeed[0] = random.randint(-3,3)
                # make sure we exit the paddle right away
                ball.move(ballspeed)

            # ball goes off screen at the bottom / change to new ball
            if ball.bottom > height:
                state = 'new'

            # check block collisions
            bindex = ball.collidelist(bricks)
            if bindex != -1:
                bricks.pop(bindex)
                ballspeed[1] = -ballspeed[1]

        else: # state is new
            ball.left = paddle.left + 12
            ball.top = paddle.top - 8

            if keys[pygame.K_SPACE]:
                ballspeed[1] = -2
                ballspeed[0] = random.randint(-3,3)
                state = 'playing'
            

        #draw screen
        screen.fill(black)
        screen.blit(ballimg, ball)
        screen.blit(paddleimg, paddle)
        for b in bricks:
            screen.blit(brickimg, b)
        pygame.display.flip()

        #do all this at 40 fps
        clock.tick(40)

def quit_game():
    pygame.quit()
    
if __name__ == '__main__': main()
