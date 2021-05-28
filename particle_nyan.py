import pygame, sys, random	
import os

class ParticlePrinciple:
	def __init__(self):
		self.particles = []

	def emit(self):
		if self.particles:
			self.delete_particles()
			for particle in self.particles:
				particle[0][1] += particle[2][0]
				particle[0][0] += particle[2][1]
				particle[1] -= 0.2
				pygame.draw.circle(screen,pygame.Color('White'),particle[0], int(particle[1]))

	def add_particles(self):
		pos_x = pygame.mouse.get_pos()[0]
		pos_y = pygame.mouse.get_pos()[1] 
		radius = 10
		direction_x = random.randint(-3,3)
		direction_y = random.randint(-3,3)
		particle_circle = [[pos_x,pos_y],radius,[direction_x,direction_y]]
		self.particles.append(particle_circle)

	def delete_particles(self):
		particle_copy = [particle for particle in self.particles if particle[1] > 0]
		self.particles = particle_copy

class ParticleNyan:
	def __init__(self):
		self.particles = []
		self.size = 12

	def emit(self):
		if self.particles:
			self.delete_particles()
			for particle in self.particles:
				particle[0].x -= 1
				pygame.draw.rect(screen,particle[1],particle[0])

		self.draw_nyancat()

	def add_particles(self,offset,color):
		pos_x = 200
		pos_y = 300 + offset
		particle_rect = pygame.Rect(int(pos_x - self.size/2),int(pos_y - self.size/2),self.size,self.size)
		self.particles.append((particle_rect,color))

	def delete_particles(self):
		particle_copy = [particle for particle in self.particles if particle[0].x > 0]
		self.particles = particle_copy

	def draw_nyancat(self):
		nyan_rect = nyan_surface.get_rect(center = (200, 300))
		screen.blit(nyan_surface,nyan_rect)

pygame.init()
screen = pygame.display.set_mode((500,500))
clock = pygame.time.Clock()

particle1 = ParticlePrinciple()

nyan_surface = pygame.image.load('nyan_cat.png').convert_alpha()
particle2 = ParticleNyan()

PARTICLE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(PARTICLE_EVENT,40)

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == PARTICLE_EVENT:
			particle2.add_particles(-30,pygame.Color("Red"))
			particle2.add_particles(-18,pygame.Color("Orange"))
			particle2.add_particles(-6,pygame.Color("Yellow"))
			particle2.add_particles(6,pygame.Color("Green"))
			particle2.add_particles(18,pygame.Color("Blue"))
			particle2.add_particles(30,pygame.Color("Purple"))

	screen.fill((30,30,30))
	particle2.emit()
	pygame.display.update()
	clock.tick(120)