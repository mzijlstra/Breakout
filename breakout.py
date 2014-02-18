import pygame, os, sys, random, math
import pygame.gfxdraw

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

class Dirt(Brick):
	img = pygame.image.load('gfx/dirt.png')

	def __init__(self, brick):
		'constructor, rect stuff plus dx'
		Brick.__init__(self, brick.x, brick.y, brick.w, brick.h)
		self.px = brick.px
		self.py = brick.py
		self.vel = brick.vel
		self.direction = brick.direction
		self.fixDxDy()

	def display(self, surface):
		'Blits dirt image to the given surface'
		surface.blit(Dirt.img, self)

	def update(self, pxarray):
		Brick.update(self)
		self.applyForce(0.2, 90);

		# wrap around the left and right
		if self.x < 0: 
			self.x = 639
		if self.x >= 640:
			self.x = 0

		if pxarray[self.x][self.y] >> 24 != 0:
			# randomly add 1, 2, or 3 px of sand
			for x in range(0,32):
				drops = random.randrange(1,4)
				for d in range (0, drops):
					y = self.y + 16
					while pxarray[self.x + x][y] >> 24 != 0:
						y -= 1
					pxarray[self.x + x][y] = (210,210,210,250)
			return False
		else:
			return True


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
		self.accel = .60

		# Track rotation
		self.trot = 0.0

		# Paddle rotation
		self.prot = 0.0

		# paddle state
		self.flying = False
		self.brk = False


	def moveLeft(self):
		'Moves paddle left'
		if not self.flying:
			self.applyForce(self.accel, 180 + self.trot)

	def moveRight(self):
		'Moves paddle right'
		if not self.flying:
			self.applyForce(self.accel, self.trot)

	def update(self, pxarray):
		# update paddle rotation based on mouse angle
		(mx, my) = pygame.mouse.get_pos()
		px = self.x + self.w / 2
		py = self.y + self.h / 2
		self.prot = getDeg(mx - px, my - py) + 90
		self.prot = self.prot % 360

		# make sure paddle can not turn more than 30 over track 
		dist = self.prot - self.trot
		if dist < 0:
			dist = 360 + dist
		if 45 < dist < 180:
			self.prot = self.trot + 30
		if 180 < dist < 315:
			self.prot = self.trot - 30

		# update track rotation based on ground
		# we want to look 14 pixels 'below' (rotated) top of paddle
		rad = math.radians(self.trot)
		x = int(-14*math.sin(rad))
		y = int(+14*math.cos(rad))

		# find top of terrain for left side of track 
		lground = False
		lx, ly = x + self.x + 2, y + self.y
		if (0 < lx < 640 and 0 < ly < 480):
			while pxarray[lx][ly] >> 24 != 0:
				lground = True
				ly -= 1

		# find top of terrain for right side of track
		rground = False
		rx, ry = x + self.x + self.w - 2, y + self.y
		if (0 < rx < 640 and 0 < ry < 480):
			while pxarray[rx][ry] >> 24 != 0:
				rground = True
				ry -= 1

		# rotate tracks 
		if lground or rground:
			self.flying = False
			# find where ground below left is
			if not lground:
				ch = 1 # change
				while lx > 0 and pxarray[lx][ly + ch] >> 24 == 0 and ch < 5:
					ch += 1
				ly += ch

			# find where ground below right is
			if not rground:
				ch = 0 # change
				while rx < 640 and pxarray[rx][ry + ch] >> 24 == 0 and ch < 5:
					ch += 1
				ry += ch

			# do the actual rotation
			deg = getDeg(rx - lx, ry - ly)
			self.trot = deg
		else:
			self.flying = True

		# move sprite up or down as needed
		if ly > ry:
			self.py = self.y = ly - 14 + 2
		else:
			self.py = self.y = ry - 14 + 2

		# apply gravity, keeping in mind rotation
		if not lground and not rground:
			self.applyForce(1.0, 90)
		else:
			deg = self.trot
			if deg < 0:
				deg += 180
			elif deg > 180:
				deg -= 180
			force = (90 - abs(deg - 90)) / 90 
			self.applyForce(force, deg)

		#slow down due to friction or breaking
		if self.flying:
			self.applyForce(self.vel * 0.05, self.direction - 180)
		elif self.brk:
			if self.vel < 0.5:
				self.stop()
			else:
				self.applyForce(self.vel * 0.25, self.direction - 180)
		else:
			if self.vel < 0.1:
				self.stop()
			else:
				self.applyForce(self.vel * 0.1, self.direction - 180)

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

	
	def display(self, surface):
		'Blits paddle image to the given surface'
		# determine track rotation frame on spritesheet
		tframe = int((self.trot % 180) / 11.25)
		tarea = pygame.Rect(tframe * 32,0,32,32)
		# determine track location relative to paddle
		rad = math.radians(self.trot)
		dx = -6*math.sin(rad)
		dy = +6*math.cos(rad)
		#determine paddle rotation frame
		pframe = int((self.prot % 180) / 11.25)
		parea = pygame.Rect(pframe * 32, 0, 32, 32)
		# blit the tracks and the paddle
		surface.blit(Paddle.tracks, (self.x + dx, self.y - 12 + dy), tarea)
		surface.blit(Paddle.paddles, (self.x, self.y - 12), parea)



def main():
	# basic init
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()

	joy = False
	joys = pygame.joystick.get_count()
	if joys > 0:
		joy = pygame.joystick.Joystick(0)
		joy.init()

	# general vars
	size = width, height = 640, 480
	screen = pygame.display.set_mode(size)
	clock = pygame.time.Clock()
	state = 'new'# either new or playing
	back = pygame.image.load('gfx/background.png').convert()

	# create terrain with random slopes
	terrain = pygame.Surface((640, 480), pygame.SRCALPHA, 32)
	terrain = terrain.convert_alpha()
	terrain.fill((0,0,0,0))

	# points along x axis with random y
	p = []
	for i in range(0, 5):
		p.append(random.randrange(380,480))

	# draw increasingly lighter colored bezier going down
	for i in range(0,100):
		points = ((0, p[0] +i), (160, p[1] +i), (320, p[2] +i), (480, p[3] +i), (639, p[4] +i))
		pygame.gfxdraw.bezier(terrain, points, 100, (int(200 + i*0.5),150 + i, i*2))

	# game elements
	paddle = Paddle(width / 2 - 16, height - 20)
	ball = Ball()
	bricks = []
	dirts = []
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
			   or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) \
			   or (event.type == pygame.JOYBUTTONDOWN and event.button == 5):
				pygame.quit()
				sys.exit()

			if (event.type == pygame.KEYDOWN and event.key == pygame.K_LCTRL) or \
					(event.type == pygame.JOYBUTTONDOWN and event.button == 12):
				paddle.brk = True
			if (event.type == pygame.KEYUP and event.key == pygame.K_LCTRL) or \
					(event.type == pygame.JOYBUTTONUP and event.button == 12):
				paddle.brk = False


		keys = pygame.key.get_pressed()
		# move paddle based on left and right arrows
		if keys[pygame.K_LEFT] or keys[pygame.K_a] or \
				(joy and (joy.get_button(2) or joy.get_axis(0) < -0.2 or joy.get_axis(2) < -0.2)):
			paddle.moveLeft()
		if keys[pygame.K_RIGHT] or keys[pygame.K_d] or \
				(joy and (joy.get_button(3) or joy.get_axis(0) > 0.2 or joy.get_axis(2) > 0.2)):
			paddle.moveRight()

		# move the paddle
		pxarray = pygame.PixelArray(terrain)
		paddle.update(pxarray)
		
		# move each block
		for brick in bricks:
			brick.update()

		if state == 'playing':
			# move ball based on it's own dx/dy
			ball.update()

			# if we hit the paddle
			if ball.colliderect(paddle):
				# new ball angle based on the angle of the paddle
				angle = (paddle.prot - 90) % 360 
				diff = ball.direction - angle
				ball.direction = (ball.direction - diff) % 360
				ball.fixDxDy()

				# make sure we exit the paddle right away
				ball.update()

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
					ball.applyForce(bricks[block].vel, -bricks[block].direction)
					dirts.append(Dirt(bricks.pop(block)))
				elif bricks[block].collidepoint(ballx, ball.y) or \
						bricks[block].collidepoint(ballx, ball.y + ball.h):
					ball.flipDy()
					dirts.append(Dirt(bricks.pop(block)))

			# check if ball hits ground, change to new ball
			# TODO move this into the ball class???
			if pxarray[ball.x + ball.w / 2][ball.top] >> 24 != 0:
				state = 'new'
				# splash ball onto ground
				for y in range(0, 5):
					y2 = int(y/2)
					for x in range(ball.left -2 + y2, ball.right + 3 -y2):
						if 0 < x < 640:
							wh = 210 + y *5;
							pxarray[x][ball.top - y] = (wh,wh,wh,250)

			# move dirts
			for dirt in dirts:
				if not dirt.update(pxarray):
					dirts.remove(dirt)


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
			
			(b1, b2, b3) = pygame.mouse.get_pressed()
			if keys[pygame.K_SPACE] or (joy and joy.get_button(11)) or b1:
				#ball.applyForce(3, random.uniform(-115, -65))
				ball.applyForce(3, paddle.prot - 90)
				ball.update()
				state = 'playing'
			
		# clean up
		del pxarray

		#draw screen
		screen.blit(back, screen.get_rect())
		screen.blit(terrain, (0, 0));
		ball.display(screen)
		paddle.display(screen)
		for b in bricks:
			b.display(screen)
		for d in dirts:
			d.display(screen)
		pygame.display.flip()

		#do all this at 60 fps
		clock.tick(60)

if __name__ == '__main__': main()
