import pygame, os, sys, random, math

def getDeg(dx, dy):
	'Helper function that returns degree based on slope'
	hyp = math.hypot(dx, dy)
	if hyp == 0:
		return 0.0
	deg = math.degrees(math.acos(dx / hyp))
	if dy < 0:
		deg = 360 - deg
	return deg


class Movable(pygame.Rect):
	'Super class for movable game objects'

	def __init__(self, x, y, w, h, vel=0.0, direction=0.0):
		# init super class
		pygame.Rect.__init__(self, x, y, w, h)
		
		# precision (float) x and y 
		self.px = float(x)
		self.py = float(y)
		self.vel = vel
		self.direction = direction
		self.fixDxDy();

	def update(self):
		self.px += self.dx
		self.py += self.dy
		self.x = int(self.px)
		self.y = int(self.py)

	def applyForce(self, vel, direction):
		rad = math.radians(direction)
		new_dx = math.cos(rad) * vel
		new_dy = math.sin(rad) * vel

		self.dx = self.dx + new_dx
		self.dy = self.dy + new_dy
		self.fixVelDir()

	def stop(self):
		self.vel = 0
		self.direction = 0
		self.dx = 0
		self.dy = 0

	def fixDxDy(self):
		rad = math.radians(self.direction)
		self.dx = math.cos(rad) * self.vel
		self.dy = math.sin(rad) * self.vel

	def fixVelDir(self):
		self.vel = math.hypot(self.dx, self.dy)
		self.direction = getDeg(self.dx, self.dy)

		

class Ball(Movable):
	"""Ball class for use in Pong and Breakout"""
	img = pygame.image.load('gfx/ball.png')

	def __init__(self, x=0.0, y=0.0):
		"""Constructor: loads image, initializes position and speed 
		optional x and y parameters set initial position"""

		# run super class constructor first
		rect = Ball.img.get_rect()
		Movable.__init__(self, x, y, rect.w, rect.h)

	def update(self):
		Movable.update(self)

		if self.x < 0 or self.x > 640 - self.w: 
			self.flipDx()
			Movable.update(self)

		if self.y < 0:
			self.flipDy()
			Movable.update(self)

	def display(self, surface):
		'Blits ball image to the give surface'
		surface.blit(Ball.img, self)

	def flipDx(self):
		"Flips the ball's horizontal speed from pos to neg or visa versa"
		#self.applyFddorce(self.dx*2, 180)#always 180 because dx can be min!
		self.dx = -self.dx
		self.fixVelDir()

	def flipDy(self):
		"Flips the ball's vertical speed from pos to neg or visa versa"
		#self.applyForce(self.dy*2, 270) # always 270 because dy can be min!
		self.dy = -self.dy
		self.fixVelDir()

	def goUp(self):
		"Ensures that dy is set to make ball go up"
		if self.dy > 0:
			self.dy = -self.dy
			self.fixVelDir()

class Paddle(Movable):
	paddles = pygame.image.load('gfx/Paddle Rotations.png')
	tracks = pygame.image.load('gfx/Track Rotations.png')

	def __init__(self, x=0.0, y=0.0):
		"""Constructor: loads images, initializes position  
		optional x and y parameters set initial position"""

		# run super class constructor first
		#rect = Paddle.img.get_rect()
		Movable.__init__(self, x, y, 32, 8)

		# acceleration
		self.accel = 2.0

		# Track rotation
		self.trot = 0.0

		# Paddle rotation
		self.prot = 0.0

	def moveLeft(self):
		'Moves paddle left'
		self.applyForce(self.accel, 180 + self.trot)

	def moveRight(self):
		'Moves paddle right'
		self.applyForce(self.accel, self.trot)

#	def rotateLeft(self):
#		self.trot = (self.trot - 1) % 360
#
#	def rotateRight(self):
#		self.trot = (self.trot + 1) % 360

	def update(self, terrain):
		# apply gravity
		self.applyForce(1.0, 90)

		 #slow down due to friction
		if self.vel < 0.15:
			self.applyForce(self.vel, self.direction - 180)
		else:
			self.applyForce(self.vel * 0.20, self.direction - 180)

		# do the actual move
		Movable.update(self)

		# make sure we don't fall off the screen
		if self.x > 640 - self.w:
			self.stop()
			self.x = self.px = 640 - self.w
		elif self.x < 0:
			self.stop()
			self.x = self.px = 0

		if self.y > 480 - self.h:
			self.stop()
			self.y = self.py = 480 - self.h
		elif self.y < 0:
			self.stop()
			self.y = self.py = 0

		# make sure we're on top of the terrain
		pxarray = pygame.PixelArray(terrain)
		dug_in = False
		x, y = self.x + self.w/2, self.y - 240 + 14
		while pxarray[x][y] >> 24 != 0:
			dug_in = True
			self.py -= 1
			y = self.y = int(self.py)
		if dug_in:
			self.dy = 0
			self.fixVelDir()

		# make sure we're rotated correctly
		del pxarray

	
	def display(self, surface):
		'Blits paddle image to the given surface'
		# determine rotation frame on spritesheet
		frame = int((self.trot % 180) / 11.25)
		area = pygame.Rect(frame * 32,0,32,32)
		# determine track location relative to paddle
		rad = math.radians(self.trot)
		dx = -6*math.sin(rad)
		dy = +6*math.cos(rad)
		# blit the tracks and the paddle
		surface.blit(Paddle.tracks, (self.x + dx, self.y - 12 + dy), area)
		surface.blit(Paddle.paddles, (self.x, self.y - 12), area)

class Brick(Movable):
	img = pygame.image.load('gfx/brick.png')

	def __init__(self, x, y, w, h):
		'constructor, rect stuff plus dx'
		Movable.__init__(self, x, y, w, h)

	def display(self, surface):
		'Blits brick image to the given surface'
		surface.blit(Brick.img, self)

	def update(self):
		Movable.update(self)

		if self.x > 640:
			self.px = -32.0
		if self.x < -32:
			self.px = 640.0


def main():
	# basic init
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()

	# general vars
	size = width, height = 640, 480
	screen = pygame.display.set_mode(size)
	clock = pygame.time.Clock()
	state = 'new'# either new or playing
	back = pygame.image.load('gfx/background.png').convert()
	terrain = pygame.image.load('gfx/terrain.png').convert_alpha()

	# game elements
	paddle = Paddle(width / 2 - 16, height - 20)

	ball = Ball()
	bricks = []
	brickrect = Brick.img.get_rect()

	#optimize images
	Paddle.paddles = Paddle.paddles.convert_alpha()
	Paddle.tracks = Paddle.tracks.convert_alpha()
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
			brick = Brick(x, y, brickW, brickH)
			if row % 2 == 0:
				brick.applyForce(1, 0)
			else:
				brick.applyForce(1, 180)
			bricks.append(brick)

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
		# change paddle angle based on A and D
		if keys[pygame.K_d] and paddle.left > 0:
			paddle.rotateRight()
		if keys[pygame.K_a] and paddle.right < width:
			paddle.rotateLeft()

		# move the paddle
		paddle.update(terrain)
		
		# move each block
		for brick in bricks:
			brick.update()

		if state == 'playing':
			# move ball based on it's own dx/dy
			ball.update()

			# if we hit the paddle
			if ball.colliderect(paddle):
				ball.goUp()
				# random dx after paddle hit
				#ball.dx = random.uniform(-3,3)
				#dx = (ball.x + ball.w / 2) - (paddle.x + paddle.w / 2)
				#ball.dx = dx / float(paddle.w) * 6.0;

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
					# apply force when hitting brick left/right
					ball.applyForce(bricks[block].vel, bricks[block].direction)
					ball.flipDx()
					bricks.pop(block)
				elif bricks[block].collidepoint(ballx, ball.y) or \
						bricks[block].collidepoint(ballx, ball.y + ball.h):
					ball.flipDy()
					bricks.pop(block)

		else: # state is new
			# ball stays on top of paddle
			rad = math.radians(-paddle.trot)
			dx = -8*math.sin(rad)
			dy = +8*math.cos(rad)

			ball.px = paddle.px + 12 +dx
			ball.py = paddle.py - dy
			ball.dx = 0
			ball.dy = 0
			ball.update()

			if keys[pygame.K_SPACE]:
				ball.applyForce(3, random.uniform(-115, -65))
				ball.update()
				state = 'playing'
			

		#draw screen
		screen.blit(back, screen.get_rect())
		screen.blit(terrain, (0, 240));
		ball.display(screen)
		paddle.display(screen)
		for b in bricks:
			b.display(screen)
		pygame.display.flip()

		#do all this at 60 fps
		clock.tick(60)

if __name__ == '__main__': main()
