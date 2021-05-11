import pygame
import neat
import time
import os
import random
pygame.font.init()

GEN = 0				# gen variable for NEAT.

WIN_WIDTH = 576		# main value for window width
WIN_HEIGHT = 800	# main valie for window height

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
			pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
			pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))] #img sources for game

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))		# img sources for game
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))	# img sources for game	
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))		# img sources for game

STAT_FONT = pygame.font.SysFont("comicsans",50)		# choosing the font for text display on screen.

class Bird:
	"""Class for all the Bird attributes in the game"""

	IMGS = BIRD_IMGS # defining de source of bird images

	MAX_ROTATION = 25				# max rotation the bird sprite will have.
	ROT_VEL = 20					# velocity of bird sprite rotating,
	ANIMATION_TIME = 5				# every sprite time on screen

	def __init__(self, x, y):
		self.x = x 					# bird horizontal position 
		self.y = y					# bird vertical position
		self.tilt = 0				# tilt value for bird
		self.tick_count = 0
		self.vel = 0				# bird speed
		self.height = self.y		# bird initial height
		self.img_count = 0			# number of actual sprite on screen
		self.img = self.IMGS[0]		# first bird sprite to be shown

	def jump(self):
		""" Defines the bird Jump due to its high and velocity. """
		self.vel = -10.5			# speed value for negative direction (upwards)
		self.tick_count = 0
		self.height = self.y		# bird vertical position

	def move(self):
		""" Defines the bird movement due its speed, and sprite rotation animation. """
		self.tick_count += 1		# tick count adds 1 when moving

		d = self.vel+self.tick_count + 1.5*self.tick_count**2	# phisyc formula for bird movement upwards

		if d >=16:					# d value cannot pass 16
			d = 16

		if d < 0:					# d value only can be 2 when negative
			d -= 2

		self.y = self.y + d 		# change in the bird vertical position given by adding d value
 	
		if d < 0 or self.y < self.height + 50:	# is d lower than 0 or is vertical position lower than height + 50
			if self.tilt < self.MAX_ROTATION:	# if it is, we have to ask if the tilt is lower than the max rotation allowed
				self.tilt = self.MAX_ROTATION	# if it is, set tilt to its max rotation

		else:									# d is neither lower than 0 or vertical position lower than height + 50
			if self.tilt > -90:					# is the tilt greater than -90 ?
				self.tilt -= self.ROT_VEL		# yes, let be tilt rot_vel - 1



	def draw(self, win):
		""" Draws the bird on screen, given the window attribute. """
		self.img_count += 1

		if self.img_count <= self.ANIMATION_TIME:
			self.img = self.IMGS[0]

		elif self.img_count <= self.ANIMATION_TIME*2:
			self.img = self.IMGS[1]
		elif self.img_count <= self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count <= self.ANIMATION_TIME*4:
			self.img = self.IMGS[1]
		elif self.img_count <= self.ANIMATION_TIME*4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0

		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2
		
		rotated_image = pygame.transform.rotate(self.img, self.tilt)
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
		win.blit(rotated_image, new_rect.topleft)

	def get_mask(self):
		return pygame.mask.from_surface(self.img)

class Pipe:
	""" This class defines the Pipes behavior in the game. """
	GAP = 200
	VEL = 5

	def __init__(self,x):
		self.x = x
		self.height = 0
		self.gap = 100

		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
		self.PIPE_BOTTOM = PIPE_IMG

		self.passed = False

		self.set_height()

	def set_height(self):
		""" Defines a random height for each generated pipe in the game, either in top or bottom of the screen. """
		self.height = random.randrange(50,400)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		""" Moves the pipes in the opposite direction the bird is moving. """
		self.x -= self.VEL

	def draw(self,win):
		""" Draws the pipes on screen, on top or bottom. """
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

	def collide(self, bird):
		""" This method configures the trigger when the bird and pipe pixels collide, so the bird loses the game. """
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask, top_offset)

		if t_point or b_point:
			return True

		return False

class Base:
	""" This class defines how the base bellow the bird will behavior. """
	VEL = 5
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		""" This function moves the base bellow in the opposite horizontal speed the bird is moving.
			Two bases are used so one can go after the first when this one goes out of screen in the left side, so basically this is a loop
			that gives the illusion the ground is infinitely. """
		self.x1 -= self.VEL
		self.x2 -= self.VEL

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		""" Draws the base img on screen. """
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen):
	""" This method generates the game screen with all the needed elements defined in previous classes. """
	win.blit(BG_IMG, (0,0))
	#bird.draw(win)
	for pipe in pipes:
		pipe.draw(win)

	text = STAT_FONT.render("Score: " + str(score), 1 ,(255,255,255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
	text = STAT_FONT.render("Gen: " + str(gen), 1 ,(255,255,255))
	win.blit(text, (10 , 10))
	

	base.draw(win)

	for bird in birds:
		bird.draw(win)

	pygame.display.update()


def main(genomes, config):
	""" Main loop where the game runs. """
	global GEN
	GEN += 1
	nets = []
	ge = []
	birds = []


	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		birds.append(Bird(230,315))
		g.fitness = 0
		ge.append(g)


	base = Base(730)
	pipes = [Pipe(700)]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	clock = pygame.time.Clock()

	score = 0

	run = True
	while run:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()

		pipe_ind = 0
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
				pipe_ind = 1

		else:
			run = False
			break

		for x, bird in enumerate(birds):
			bird.move()
			ge[x].fitness += 0.1

			output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

			if output[0] > 0.5:
				bird.jump()


		#bird.move()
		add_pipe = False
		rem = []
		for pipe in pipes:
			for x, bird in enumerate(birds):
				if pipe.collide(bird):
					ge[x].fitness -= 1
					birds.pop(x)
					nets.pop(x)
					ge.pop(x)

				if not pipe.passed and pipe.x < bird.x:
					pipe.passed = True
					add_pipe = True

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				rem.append(pipe)

			pipe.move()

		if add_pipe:
			score += 1
			for g in ge:
				g.fitness += 5
			pipes.append(Pipe(600))

		for r in rem:
			pipes.remove(r)

		for x, bird in enumerate(birds):
			if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)

		base.move()
		draw_window(win, birds, pipes, base, score, GEN)

	

#main()

def run(config_path):
	""" Running method for NEAT module configuration, here all the needed parameters are given to neat config attribute.
		Parameter values are given in config-feedforward.txt document, placed in the same directory as this file. """	
	config = neat.config.Config(neat.DefaultGenome, 
			neat.DefaultReproduction, 
			neat.DefaultSpeciesSet,
			neat.DefaultStagnation,
			config_path)

	p = neat.Population(config)

	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(main,50)

if __name__ == "__main__":
	""" This if block reaches the config-feedforward.txt document for all the variable values neat needs to work. """
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)

