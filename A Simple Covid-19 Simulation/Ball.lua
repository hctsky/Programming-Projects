--[[

ball.lua
A Simple Covid-19 Simulation
Created by : Huang ChenTing
Date: March 2022

]]--


Ball = Class {}


Status = {
   ["NORMAL"] = 1,
   ["INFECTED"] = 2,
   ["RECOVERED"] = 3,
   ["VACCINATED"] = 4,
   ["DEAD"] = 5,
}

Mindset = {
   ["NORMAL"] = 1,
   ["CAUTIOUS"] = 2,
   ["LOCKDOWN"] = 3,
}

-- ball init
function Ball:init(x, y, radius, id)

	-- position
	self.px = x
	self.py = y
	
	-- velocity
	self.vx = math.random(2) == 1 and 100 or -100
	self.vy = math.random(-100, 100)	
	
	-- acceleration optional
	self.ax = 0
	self.ay = 0
	
	self.ox = 0
	self.oy = 0
	
	self.radius = radius
	self.mass = radius
	self.state = Status.NORMAL

	self.sickTime = 50
	self.vaccinated = false
	
	self.simTimeRemaining = 0
	self.id = id

end



-- ball collides with another ball
function Ball:collides(ball)

	if ball.id == self.id then
		return false
	end
	
	if ball.state == Status.DEAD then
		return false
	end
	
	-- find distance between 2 balls
	dist2 = (self.px - ball.px) * (self.px - ball.px) + (self.py - ball.py) * (self.py - ball.py)
	
	-- check squared distance
	if dist2 <= (self.radius + ball.radius) * (self.radius + ball.radius) then
		return true	
	end
	
	return false
end



-- resolve collision dynamically
function Ball:collision_response(ball)


	dist = math.sqrt((self.px - ball.px) * (self.px - ball.px) + (self.py - ball.py) * (self.py - ball.py))
	
	nx = (self.px - ball.px) / dist
	ny = (self.py - ball.py) / dist

	tx = -ny
	ty = nx
	
	dpTan1 = self.vx * tx + self.vy * ty
	dpTan2 = ball.vx * tx + ball.vy * ty
	
	dpNorm1 = self.vx * nx + self.vy * ny 
	dpNorm2 = ball.vx * nx + ball.vy * ny	

	-- conservation of momentum 1d
	m1 = (dpNorm1 * (self.mass - ball.mass) + 2 * ball.mass * dpNorm2 ) / (self.mass + ball.mass)
	m2 = (dpNorm2 * (ball.mass - self.mass) + 2 * self.mass * dpNorm1 ) / (self.mass + ball.mass)	


	self.vx = tx * dpTan1 + nx * m1
	self.vy = ty * dpTan1 + ny * m1
	
	ball.vx = tx * dpTan2 + nx * m2
	ball.vy = ty * dpTan2 + ny * m2
	
	
	-- if self is infected
	if self.state == Status.INFECTED and ball.state ~= Status.INFECTED then
	
		if ball.vaccinated then
			if math.random(26) == 1 then
				ball.state = Status.INFECTED
			end		
		else
			if math.random(13) == 1 then
				ball.state = Status.INFECTED
			end
		end
	end
	
	if self.state ~= Status.INFECTED and ball.state == Status.INFECTED then
	
		if self.vaccinated then
			if math.random(26) == 1 then
				self.state = Status.INFECTED
			end		
		else
			if math.random(13) < 1 then
				self.state = Status.INFECTED
			end
		end
	end	
end


-- update ball position
function Ball:update(dt, mindset)

	-- basically dun do anything anymore if dead
	if self.state == Status.DEAD then
		return true
	end


	if mindset == Mindset.LOCKDOWN then
	
		if math.random(10) <= 3 then
			self.ax = -self.vx * 0.8
			self.ay = -self.vy * 0.8
					
			self.vx = self.vx + self.ax * dt
			self.vy = self.vy + self.ay * dt				
		end
	end

	self.px = self.px + self.vx * dt
	self.py = self.py + self.vy * dt
	
	-- static collisions here
	if self.px < -self.radius then
		self.px = VIRTUAL_WIDTH + self.radius
	elseif self.px > VIRTUAL_WIDTH + self.radius then
		self.px = -self.radius
	end
	
	if self.py < -self.radius then
		self.py = VIRTUAL_HEIGHT + self.radius
	elseif self.py > VIRTUAL_HEIGHT + self.radius then
		self.py = -self.radius
	end
	
	if self.vx * self.vx + self.vy * self.vy < 0.01 then
		self.vx = 0
		self.vy = 0
	end
end

function Ball:update_status(dt)
	if self.state == Status.NORMAL then
		
	elseif self.state == Status.INFECTED then
		self.sickTime = self.sickTime - dt
		
		-- recover faster if vaccinated
		if self.vaccinated then
			self.sickTime = self.sickTime - dt
		end

		if self.sickTime <= 0 then
			-- vaccinated, less chance of dying
			if self.vaccinated then
				if math.random(1000) == 1 then
					self.state = Status.DEAD
				else
					self.state = Status.RECOVERED
					self.vaccinated = true
					self.sickTime = 50
				end			
			else	-- unvaccinated, higher chance
				if math.random(100) == 2 then
					--dead
					self.state = Status.DEAD
				else
					self.state = Status.RECOVERED
					self.vaccinated = true
					self.sickTime = 50
				end									
			end
		
		end
		
	--elseif self.state == Status.RECOVERED then
	--elseif self.state == Status.VACCINATED then
		
	elseif self.state == Status.DEAD then
		self.vx = 0
		self.vy = 0
		
	end
end


-- draw ball, different colours depend on different statuses
function Ball:render()

	if self.state == Status.NORMAL then
		love.graphics.setColor(0, 1, 0, 1)
	elseif self.state == Status.INFECTED then
		love.graphics.setColor(1, 0, 0, 1)
	elseif self.state == Status.RECOVERED then
		love.graphics.setColor(0.1, 0.5, 0.1, 1)		
	elseif self.state == Status.VACCINATED then
		love.graphics.setColor(0, 0, 1, 1)
	elseif self.state == Status.DEAD then
		love.graphics.setColor(0.1, 0.1, 0.1, 1)
	end

	love.graphics.circle('fill', self.px, self.py, self.radius, 15)
end


-- ball status change
function Ball:status_change()

	if self.state == Status.NORMAL then
		self.state = Status.INFECTED
	elseif self.state == Status.INFECTED then
		self.state = Status.RECOVERED
	elseif self.state == Status.RECOVERED then
		self.state = Status.VACCINATED		
	elseif self.state == Status.VACCINATED then
		self.state = Status.DEAD
	elseif self.state == Status.DEAD then
		self.state = Status.NORMAL
	end
end