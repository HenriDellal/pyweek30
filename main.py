import pygame, random
pygame.init()

pygame.font.init()
main_font = pygame.font.SysFont("default", 32)

pause_text_surfaces = []
pause_strings = ["The game is simple",
				"Use the fishing rod to catch a fish",
				"The fishing line may tear if fish gets too far",
				"or you roll the line for too long when fish resists heavily",
				"",
				"Controls:",
				"Right - Roll fishing line",
				"P - Pause",
				"Enter (Return) - New game",
				"",
				"Hope you enjoy this game :)"]
for text in pause_strings:
	pause_text_surfaces.append(main_font.render(text, True, (0, 0, 0)))

pause_text_pos = main_font.size("PAUSE")
line_tear_text_surface = main_font.render("The fishing line is torn", True, (0, 0, 0))
line_tear_pos = main_font.size("The fishing line is torn")
fish_caught_text_surface = main_font.render("You've caught a fish!", True, (0, 0, 0))
fish_caught_pos = main_font.size("You've caught a fish!")
press_enter_text_surface = main_font.render("Press Enter to continue", True, (0, 0, 0))
press_enter_pos = main_font.size("Press Enter to continue")

width = 800
height = 600

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Catch the life")

color_sky = (90, 217, 249)
color_sea = (0, 125, 255)
color_sun = (253, 197, 19)
color_shore = (234, 226, 178)
color_shore_dark = (163, 158, 124)
color_line = (230, 230, 230)

horizon = 420

rect_sea = pygame.Rect(0, horizon, width, height-horizon)

sun_position = (width/8, height/6)
sun_radius = height/18

img_cloud = pygame.image.load("cloud.png")
cloud_rect = img_cloud.get_rect()
cloud_rect.centerx = 200
cloud_rect.centery = 180

img_wp = pygame.image.load("wp.png")
wp_rect = img_wp.get_rect()
wp_rect.centerx = 250
wp_rect.centery = 520

img_line_tear = pygame.image.load("line-tear.png")
img_fish_caught = pygame.image.load("fish-caught.png")
img_fisher = pygame.image.load("fisher.png")

rod_velocity = 4

rod_point = (600, 300)

pygame.key.set_repeat(0)

FISH_VELOCITY_CHANGED_EVENT = pygame.USEREVENT
ADD_CLOUD_EVENT = pygame.USEREVENT + 1

pygame.time.set_timer(FISH_VELOCITY_CHANGED_EVENT, random.randint(3,6) * 1000)
pygame.time.set_timer(ADD_CLOUD_EVENT, random.randint(10,15) * 1000)

FISHING = 0
LINE_TEAR = 1
FISH_CAUGHT = 2
state = FISHING
paused = True

MAX_TENSION = 80
tension = 0

done = False

class Cloud():
	def __init__(self, left, centery):
		self.img = pygame.image.load("cloud.png")
		self.rect = self.img.get_rect()
		self.rect.left = left
		self.rect.centery = centery
		self.step_x = -1

	def draw(self, screen):
		screen.blit(self.img, self.rect)
	
	def update(self):
		self.rect.centerx += self.step_x
	
	def out_of_screen(self):
		return self.rect.right < 0

clouds = [Cloud(random.randint(100, 500), random.randint(100, 200)),
			Cloud(random.randint(500, 700), random.randint(100, 200))]

is_any_fish_tied = False

class Fish():
	filenames = ["fish1.png", "fish2.png", "fish3.png"]
	def __init__(self):
		self.img = pygame.image.load(self.filenames[random.randint(0,2)])
		self.rect = self.img.get_rect()
		self.rect.x = random.randint(100, 350)
		self.rect.y = random.randint(500, 560)
		self.x_direction = 1
		self.y_direction = 0
		self.speed_x = random.randint(2,6)
		self.speed_y = 0
		self.tied_x = False
		self.tied_y = False

	def draw(self, screen):
		screen.blit(self.img, self.rect)
	
	def update(self, wp):
		prev_x_direction = self.x_direction
		xdiff = wp.centerx - self.get_head_coord()
		ydiff = wp.centery - self.rect.centery
		if not self.tied_x and abs(xdiff) <= 50 and not is_any_fish_tied:
			if xdiff < -10:
				self.x_direction = -1
			elif xdiff > 10:
				self.x_direction = 1
			else:
				self.set_head_coord(wp)
				self.tied_x = True
		
		if is_any_fish_tied:
			self.speed_y = 0
		elif not self.tied_y and abs(ydiff) <= 50:
			if ydiff < -10:
				self.y_direction = -1
				self.speed_y = 1
			elif ydiff > 10:
				self.y_direction = 1
				self.speed_y = 1
			else:
				self.speed_y = 0
				self.rect.centery = wp.centery
				self.tied_y = True
		
		if self.tied_x:
			self.set_head_coord(wp)
		else:
			self.rect.x += self.x_direction * self.speed_x
		
		self.rect.y += self.y_direction * self.speed_y
		if self.rect.right > 610:
			self.x_direction = -1
		elif self.rect.left < 0:
			self.x_direction = 1
		
		if prev_x_direction != self.x_direction:
			self.img = pygame.transform.flip(self.img, True, False)
	
	def get_head_coord(self):
		if self.x_direction == 1:
			return self.rect.right
		else:
			return self.rect.left

	def set_head_coord(self, wp):
		if self.x_direction == 1:
			self.rect.right = wp.centerx
		else:
			self.rect.left = wp.centerx
		
		self.rect.centery = wp.centery

	def caught(self):
		if self.rect.h < self.rect.w:
			self.img = pygame.transform.rotate(self.img, self.x_direction * 90)
			self.rect = self.img.get_rect()
			self.rect.centerx = rod_point[0]
			self.rect.top = rod_point[1]+60


fishes = [Fish(), Fish(), Fish()]
tied_fish = None

def fishing_init():
	global paused, state, fish_velocity, tension, is_any_fish_tied, fishes, tied_fish
	tension = 0
	is_any_fish_tied = False
	tied_fish = None
	wp_rect.centerx = 200
	fishes = [Fish(), Fish(), Fish()]
	pygame.time.set_timer(FISH_VELOCITY_CHANGED_EVENT, random.randint(3,7) * 1000)
	state = FISHING
	paused = False
	pygame.key.set_repeat(16)

def handle_event(ev):
	global done, fish_velocity, tension
	if ev.type == pygame.QUIT:
		done = True
	elif not paused:
		if ev.type == pygame.KEYDOWN:
			if ev.key == pygame.K_RIGHT:
				wp_rect.centerx += rod_velocity
				if tied_fish is not None and tied_fish.speed_x > rod_velocity:
					tension += 1
		elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RIGHT:
			if tension > 20:
				tension -= 20
			else:
				tension = 0
		elif ev.type == FISH_VELOCITY_CHANGED_EVENT:
			for fish in fishes:
				fish.speed_x = random.randint(2, 6)
			pygame.time.set_timer(FISH_VELOCITY_CHANGED_EVENT, random.randint(3,7) * 1000)
		elif ev.type == ADD_CLOUD_EVENT:
			clouds.append(Cloud(width, random.randint(100, 200)))
			pygame.time.set_timer(ADD_CLOUD_EVENT, random.randint(5,15) * 1000)


def handle_pressed_keys():
	global paused
	pressed_keys = pygame.key.get_pressed()
	if pressed_keys[pygame.K_p]:
		paused = not paused
		if paused:
			pygame.key.set_repeat(0)
		else:
			pygame.key.set_repeat(16)
	elif pressed_keys[pygame.K_RETURN] and paused:
		fishing_init()


def draw_bg():
	screen.fill(color_sky)
	pygame.draw.rect(screen, color_sea, rect_sea)
	pygame.draw.circle(screen, color_sun, (150, 150), 75, 0)
	pygame.draw.ellipse(screen, color_shore, pygame.Rect(650, 380, 400, 70))
	for cloud in clouds:
		cloud.update()
		cloud.draw(screen)
		if cloud.out_of_screen():
			clouds.remove(cloud)
	
	screen.blit(img_fisher, rod_point)

def draw_ingame_window():
	pygame.draw.aaline(screen, color_line, (rod_point[0], rod_point[1]+60), rod_point)
	pygame.draw.rect(screen, color_shore, pygame.Rect(250, 100, width-250*2, height-100*2))
	pygame.draw.rect(screen, color_shore_dark, pygame.Rect(250, 100, width-250*2, height-100*2), 5)
	if state == FISH_CAUGHT:
		screen.blit(fish_caught_text_surface, ((width-fish_caught_pos[0])/2, 400))
		screen.blit(img_fish_caught, (300, 150, 200, 200))
	elif state == LINE_TEAR:
		screen.blit(line_tear_text_surface, ((width-line_tear_pos[0])/2, 400))
		screen.blit(img_line_tear, (300, 150, 200, 200))
	
	screen.blit(press_enter_text_surface, ((width-press_enter_pos[0])/2, 460))
	pygame.draw.rect(screen, color_shore_dark, pygame.Rect(300, 150, 200, 200), 3)

def draw_pause_window():
	pygame.draw.rect(screen, color_shore, pygame.Rect(50, 50, width-50*2, height-50*2))
	pygame.draw.rect(screen, color_shore_dark, pygame.Rect(50, 50, width-50*2, height-50*2), 5)
	text_y = 70
	for surface in pause_text_surfaces:
		screen.blit(surface, (70, text_y))
		text_y += 40

while not done:
	for ev in pygame.event.get():
		handle_event(ev)

	handle_pressed_keys()
	if state == FISHING and not paused:
		if tied_fish is not None:
			wp_rect.centerx -= tied_fish.speed_x
		for fish in fishes:
			fish.update(wp_rect)
			if tied_fish is None:
				if fish.tied_x and fish.tied_y:
					is_any_fish_tied = True
					tied_fish = fish
		
		if wp_rect.centerx > rod_point[0]:
			state = FISH_CAUGHT
			paused = True
		elif wp_rect.centerx < 0 or tension >= MAX_TENSION:
			state = LINE_TEAR
			paused = True

	draw_bg()
	if state == FISHING:
		screen.blit(img_wp, wp_rect)
		pygame.draw.aaline(screen, color_line, (wp_rect.centerx, wp_rect.centery), rod_point)
		for fish in fishes:
			fish.draw(screen)
		if paused:
			draw_pause_window()
	else:
		if state == FISH_CAUGHT:
			tied_fish.caught()
			for fish in fishes:
				fish.draw(screen)
		draw_ingame_window()

	pygame.time.delay(33)
	pygame.display.flip()

pygame.quit()
