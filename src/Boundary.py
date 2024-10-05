import math

class Boundary:
	def __init__(self, start, end):
		self.start = start
		self.end = end
		self.dx = 0
		self.dy = 0
		self.length = 0
		self.length2 = 0
		self.horizontal = False
		self.angle = 0.0

		self.update()

		# Extend lines a bit
		add_len = 0.001 / self.length

		self.end[0] += self.dx * add_len
		self.end[1] += self.dy * add_len

		self.start[0] -= self.dx * add_len
		self.start[1] -= self.dy * add_len

		self.update()

		self.horizontal = (abs(self.end[0] - self.start[0]) > abs(self.end[1] - self.start[1]))

		self.angle = math.atan2(self.end[1] - self.start[1], self.end[0] - self.start[0])

	def update(self):
		self.dx = self.end[0] - self.start[0]
		self.dy = self.end[1] - self.start[1]

		self.length2 = self.dy ** 2 + self.dx ** 2
		self.length = math.sqrt(self.length2)

	def intersects(self, p):
		# t = dot(Ap, AB) / AB_squared
		# t = dot(start.p, start.end) / length(end-start)^2

		pdx = p[0] - self.start[0]
		pdy = p[1] - self.start[1]

		t = (pdx * self.dx + pdy * self.dy) / self.length2

		return 0 <= t <= 1

	def get_side(self, p):
		pdx = p[0] - self.start[0]
		pdy = p[1] - self.start[1]

		return math.copysign(1, pdy * self.dx - pdx * self.dy)

	def is_near(self, p):
		pdx = p[0] - self.start[0]
		pdy = p[1] - self.start[1]

		return math.sqrt(abs(pdy * self.dx - pdx * self.dy)) < 0.005  # 5 mm
