import pygame, os, sys, random

class Ball(pygame.Rect):
	"""Ball class for use in Pong and Breakout"""
	img = pygame.image.load('ball4.png')

	def __init__(self, x=0.0, y=0.0):
		"""Constructor: loads image, initializes position and speed 
		optional x and y parameters set initial position"""

		# run super class constructor first
		rect = Ball.img.get_rect()
		pygame.Rect.__init__(self, x, y, rect.w, rect.h)

		# precision position (floats)
		self.px = x
		self.py = y

		# speed
		self.dx = 0.0
		self.dy = 0.0

	def update(self):
		'updated ball position based on speed'
		self.px += self.dx
		self.py += self.dy

		# also update interal rect
		self.x = self.px
		self.y = self.py

	def display(self, surface):
		'Blits ball image to the give surface'
		surface.blit(Ball.img, self)

	def flipDx(self):
		"Flips the ball's horizontal speed from pos to neg or visa versa"
		self.dx = -self.dx

	def flipDy(self):
		"Flips the ball's vertical speed from pos to neg or visa versa"
		self.dy = -self.dy

	def goUp(self):
		"Ensures that dy is set to make ball go up"
		self.dy = -abs(self.dy)

class Paddle(pygame.Rect):
	img = pygame.image.load('paddle.png')

	def __init__(self, x=0.0, y=0.0):
		"""Constructor: loads image, initializes position and speed 
		optional x and y parameters set initial position"""

		# run super class constructor first
		rect = Paddle.img.get_rect()
		pygame.Rect.__init__(self, x, y, rect.w, rect.h)

		# precision position (floats)
		self.px = x
		self.py = y

		# speed
		self.speed = 2
	
	def moveLeft(self):
		'Moves paddle left'
		self.px -= self.speed
		self.x = self.px

	def moveRight(self):
		'Moves paddle right'
		self.px += self.speed
		self.x = self.px

	def display(self, surface):
		'Blits paddle image to the given surface'
		surface.blit(Paddle.img, self)

class Brick(pygame.Rect):
	img = pygame.image.load('brick3.png')

	def display(self, surface):
		'Blits brick image to the given surface'
		surface.blit(Brick.img, self)


def main():
	# basic init
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()

	# general vars
	black = 0, 0, 0
	size = width, height = 640, 480
	screen = pygame.display.set_mode(size)
	clock = pygame.time.Clock()
	state = 'new'# either new or playing
	back = pygame.image.load('background2.png').convert()

	# game elements
	paddle = Paddle(width / 2 - 16, height - 20)
	ball = Ball()
	bricks = []
	brickrect = Brick.img.get_rect()

	#optimize images
	Paddle.img = Paddle.img.convert_alpha()
	Ball.img = Ball.img.convert_alpha()
	Brick.img = Brick.img.convert_alpha()

	# create brick positions
	rows = 4
	cols = width / brickrect.width
	brickW = brickrect.width
	brickH = brickrect.height
	
	for row in range(rows):
		for col in range(cols):
			x = col * brickW
			y = 64 + row * brickH
			bricks.append(Brick(x, y, brickW, brickH))

	# game loop
	while True:

		# quit on window close or escape key
		for event in pygame.event.get():
			if event.type == pygame.QUIT \
			   or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				pygame.quit()
				sys.exit()


		# move paddle based on left and right arrows
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT] and paddle.left > 0:
			paddle.moveLeft()
		if keys[pygame.K_RIGHT] and paddle.right < width:
			paddle.moveRight()

		if state == 'playing':
			# move ball based on it's own dx/dy
			ball.update()

			# bounce against screen top, left and right 
			if ball.left < 0 or ball.right > width:
				ball.flipDx()
			if ball.top < 0: # or ball.bottom > height:
				ball.flipDy()
				
			# if we hit the paddle
			if ball.colliderect(paddle):
				ball.goUp()
				# random dx after paddle hit
				ball.dx = random.uniform(-3,3)
				# make sure we exit the paddle right away
				ball.update()

			# ball goes off screen at the bottom / change to new ball
			if ball.bottom > height:
				state = 'new'

			# check block collisions
			bindex = ball.collidelist(bricks)
			if bindex != -1:
				bricks.pop(bindex)
				ball.flipDy()

		else: # state is new
			ball.left = paddle.left + 12
			ball.top = paddle.top - 8

			if keys[pygame.K_SPACE]:
				#ball goes up, random angle
				ball.dy = -2
				ball.dx = random.uniform(-3, 3)

				#prepare precision movement
				ball.px = ball.x
				ball.py = ball.y

				#go to playing state
				state = 'playing'
			

		#draw screen
		#screen.fill(black)
		screen.blit(back, screen.get_rect())
		ball.display(screen)
		paddle.display(screen)
		for b in bricks:
			b.display(screen)
		pygame.display.flip()

		#do all this at 40 fps
		clock.tick(40)

if __name__ == '__main__': main()
