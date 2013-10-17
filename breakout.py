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
	trackA = pygame.image.load('Track A.png')
	trackB = pygame.image.load('Track B.png')

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
		self.speed = 2.5
	
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
		surface.blit(Paddle.trackA, (self.x, self.y + 8))

class Brick(pygame.Rect):
	img = pygame.image.load('brick3.png')

	def __init__(self, x, y, w, h, dx):
		'constructor, rect stuff plus dx'
		pygame.Rect.__init__(self, x, y, w, h)
		self.dx = dx

	def display(self, surface):
		'Blits brick image to the given surface'
		surface.blit(Brick.img, self)

	def update(self):
		self.x += self.dx
		if self.x > 640:
			self.x = -32;
		if self.x < -32:
			self.x = 640


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
	back = pygame.image.load('background.png').convert()

	# game elements
	paddle = Paddle(width / 2 - 16, height - 20)
	ball = Ball()
	bricks = []
	brickrect = Brick.img.get_rect()

	#optimize images
	Paddle.img = Paddle.img.convert_alpha()
	Paddle.trackA = Paddle.trackA.convert_alpha()
	Paddle.trackB = Paddle.trackB.convert_alpha()
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
			y = 32 + row * brickH * 3
			dx = 1
			if row % 2 == 0:
				dx = -1
			bricks.append(Brick(x, y, brickW, brickH, dx))

	# game loop
	while True:

		# quit on window close or escape key
		for event in pygame.event.get():
			if event.type == pygame.QUIT \
			   or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				pygame.quit()
				sys.exit()


		keys = pygame.key.get_pressed()
		# move paddle based on left and right arrows
		if keys[pygame.K_LEFT] and paddle.left > 0:
			paddle.moveLeft()
		if keys[pygame.K_RIGHT] and paddle.right < width:
			paddle.moveRight()

		# move paddle based on mouse
		#(mx, my) = pygame.mouse.get_pos()
		#if my > 640 - paddle.h:
		#	my = 640 - paddle.h
		#elif my < 240:
		#	my = 240

		#paddlehw = paddle.w / 2
		#if mx < paddlehw:
		#	mx = paddlehw
		#elif mx > 640 - paddlehw:
		#	mx = paddlehw

		#paddle.x = mx - paddlehw
		#paddle.y = my

		# move each block
		for brick in bricks:
			brick.update()

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
				#ball.dx = random.uniform(-3,3)
				dx = (ball.x + ball.w / 2) - (paddle.x + paddle.w / 2)
				ball.dx = dx / float(paddle.w) * 6.0;

				# make sure we exit the paddle right away
				ball.update()

			# ball goes off screen at the bottom / change to new ball
			if ball.bottom > height:
				state = 'new'

			# check block collisions
			blocks = ball.collidelistall(bricks)
			for block in blocks:
				bally = ball.y + ball.h / 2
				ballx = ball.x + ball.w / 2
				if block >= len(bricks):
					continue
				if (bricks[block].collidepoint(ball.x, bally) or \
					bricks[block].collidepoint(ball.x + ball.w, bally)):
					ball.flipDx()
					bricks.pop(block)
				elif bricks[block].collidepoint(ballx, ball.y) or \
						bricks[block].collidepoint(ballx, ball.y + ball.h):
					ball.flipDy()
					bricks.pop(block)

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

		#do all this at 60 fps
		clock.tick(60)

if __name__ == '__main__': main()
