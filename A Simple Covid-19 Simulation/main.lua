--[[

main.lua
A Simple Covid-19 Simulation
Created by : Huang ChenTing
Date: March 2022

]]--

push = require 'push'
Class = require 'class'
require 'Ball'

-- Global Constants
WINDOW_WIDTH = 1728
WINDOW_HEIGHT = 972

VIRTUAL_WIDTH = 864
VIRTUAL_HEIGHT = 486

MAX_BALLS = 200


-- Global variables
pause = false
vaccination_mode = false
accumulated_time = 0

global_mindset = Mindset.NORMAL

-- 8 for 80%
vaccination_rate = 8


-- variables for population status count
total_count = MAX_BALLS
normal_count = 0
vaccinated_count = 0
infected_count = 0
recovered_count = 0
dead_count = 0



-- love load function for initialization
function love.load()

	-- init
	pause = false
	vaccination_mode = false
	global_mindset = Mindset.NORMAL
	accumulated_time = 0
	math.randomseed(os.time())
	love.graphics.setDefaultFilter('nearest', 'nearest')
	love.window.setTitle("Covid-19 Simulation using Love Lua")
	smallFont = love.graphics.newFont('font.TTF', 8)
	scoreFont = love.graphics.newFont('font.TTF', 32)
	victoryFont = love.graphics.newFont('font.TTF', 16)

	-- ball list to keep track of balls
	ball_list = {}
		
	-- create balls randomly throughout screen
	for i = 1, MAX_BALLS do
		ball = Ball(math.random(0, VIRTUAL_WIDTH- 2), math.random(0, VIRTUAL_HEIGHT - 2), 5)
		ball.id = i
		table.insert(ball_list, ball)
	end
	
	gameState = 'start'
	
	push:setupScreen(VIRTUAL_WIDTH, VIRTUAL_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT, {
		fullscreen = false,
		vsync = true,
		resizable = true	
	})	
	
end

-- for resizing screen
function love.resize(w, h)
	push:resize(w, h)
end


-- to check keyboard presses
function love.keypressed(key)
	if key == 'escape' then
		love.event.quit()		
	end	
	
	if key == 'r' then
		love.load()
	end

	if key == 'c' then
		caution_mode()
	end

	if key == 'v' then
		vaccination_mode = not vaccination_mode
		
		if vaccination_mode then
			vaccine_mode()
		end
	end

	-- space to pause and unpause
	if key == 'space' then
		pause = not pause
		if pause then
			for i = 1, MAX_BALLS do
				ball_list[i].vx = 0
				ball_list[i].vy = 0				
			end		
		else
			for i = 1, MAX_BALLS do
				ball_list[i].vx = math.random(-100, 100)	
				ball_list[i].vy = math.random(-100, 100)				
			end				
		end
		
		
	end
	
	
end



-- to check mouse buttons
function love.mousereleased(x, y, button)

	mx = love.mouse.getX() * VIRTUAL_WIDTH / WINDOW_WIDTH
	my = love.mouse.getY() * VIRTUAL_HEIGHT / WINDOW_HEIGHT

    if button == 1 then
		for i = 1, MAX_BALLS do
			if point_in_circle(ball_list[i].px, ball_list[i].py, ball_list[i].radius, mx, my) then
				ball_list[i]:status_change()
			
			end	
		end
    end
end



-- love update function for updating game loop
function love.update(dt)

	-- reset for display to work correctly
	normal_count = 0
	vaccinated_count = 0
	infected_count = 0
	recovered_count = 0
	dead_count = 0	
			
	accumulated_time = accumulated_time + love.timer.getDelta()
		
	nSimUpdates = 4
	nMaxSimSteps = 15
	simElapsedTime = dt / nSimUpdates
		
	-- dynamic collisions 
	for k = 0, nSimUpdates do
		for l= 0, nMaxSimSteps do
			for i = 1, MAX_BALLS do
				ball_list[i]:update(simElapsedTime/nMaxSimSteps, global_mindset)
								
				for j = 1, MAX_BALLS do
					if ball_list[i]:collides(ball_list[j]) then
						ball_list[i]:collision_response(ball_list[j])
						separateBalls(ball_list[i], ball_list[j])			
					end
				end		
			end				
		end
	end	
	
	update_numbers(dt)
	
end




-- love update function for drawing objects
function love.draw()
    
	push:apply('start')

	-- draw different background colour depending on mindset
	if global_mindset == Mindset.NORMAL then
		love.graphics.clear(40  / 255, 45 / 255, 52/ 255, 1)
	elseif global_mindset == Mindset.CAUTIOUS then
		love.graphics.clear(100  / 255, 100 / 255, 25/ 255, 1)
	elseif global_mindset == Mindset.LOCKDOWN then
		love.graphics.clear(90  / 255, 40 / 255, 50/ 255, 1)
	end	
	
	for i = 1, MAX_BALLS do
		ball_list[i]:render()
	end
		
	love.graphics.setColor(1, 1, 1, 1)
	
	-- printing of UI
	displayFPS()		
	love.graphics.setFont(victoryFont)
	
	
	-- only one state for this game
	if gameState == 'start' then
		love.graphics.printf("Covid-19 Sim", 1, 12, VIRTUAL_WIDTH, 'left')
		love.graphics.printf(love.timer.getDelta(), 1, 24, VIRTUAL_WIDTH, 'left')
		love.graphics.printf("Elapsed Time: ".. tostring(math.floor(accumulated_time)), 1, 36, VIRTUAL_WIDTH, 'left')
		
		if global_mindset == Mindset.NORMAL then
			love.graphics.printf("Normal Situation", 1, 50, VIRTUAL_WIDTH, 'left')
		elseif global_mindset == Mindset.CAUTIOUS then
			love.graphics.printf("Social Distancing", 1, 50, VIRTUAL_WIDTH, 'left')
		elseif global_mindset == Mindset.LOCKDOWN then
			love.graphics.printf("Lockdown Mode", 1, 50, VIRTUAL_WIDTH, 'left')
		end
				
		love.graphics.printf("Total: " .. tostring(total_count), 1, 72, VIRTUAL_WIDTH, 'left')
		love.graphics.printf("Normal: " .. tostring(normal_count), 1, 92, VIRTUAL_WIDTH, 'left')
		love.graphics.printf("Infected: " .. tostring(infected_count), 1, 112, VIRTUAL_WIDTH, 'left')
		love.graphics.printf("Recovered: " .. tostring(recovered_count), 1, 132, VIRTUAL_WIDTH, 'left')
		love.graphics.printf("Vaccinated: " .. tostring(vaccinated_count), 1, 152, VIRTUAL_WIDTH, 'left')
		love.graphics.printf("Dead: " .. tostring(dead_count), 1, 172, VIRTUAL_WIDTH, 'left')
		
	end
		
	push:apply('end')
	
end



-- for debugging
function displayFPS()
	love.graphics.setColor(0, 1, 0, 1) -- green rgba
	love.graphics.setFont(smallFont)
	love.graphics.print('FPS: ' .. tostring(love.timer.getFPS()), 1, 1)
		
	love.graphics.setColor(1, 1, 1, 1)
end




-- for static collisions
function separateBalls(b1, b2)

	dist = math.sqrt((b1.px - b2.px) * (b1.px - b2.px) + (b1.py - b2.py) * (b1.py - b2.py))
	
	overlap = 0.5 * (dist - b1.radius - b2.radius)
	
	b1.px = b1.px - overlap * (b1.px - b2.px) / dist
	b1.py = b1.py - overlap * (b1.py - b2.py) / dist
	
	b2.px = b2.px + overlap * (b1.px - b2.px) / dist
	b2.py = b2.py + overlap * (b1.py - b2.py) / dist

end




-- for checking if mouse click is on a ball or not
function point_in_circle(cx, cy, cradius, px, py)

	if (cx - px) * (cx - px) + (cy - py) * (cy - py) < cradius * cradius then
		return true
	else
		return false
	end
end

-- caution mode to check mindset of population, balls behave differently depending on mindset
function caution_mode()
	if global_mindset == Mindset.NORMAL then
		global_mindset = Mindset.CAUTIOUS
	elseif global_mindset == Mindset.CAUTIOUS then
		global_mindset = Mindset.LOCKDOWN
	elseif global_mindset == Mindset.LOCKDOWN then
		global_mindset = Mindset.NORMAL
	end
			
	if global_mindset == Mindset.NORMAL then
		for i = 1, MAX_BALLS do
			ball_list[i].vx = math.random(-100, 100)	
			ball_list[i].vy = math.random(-100, 100)				
		end			
	elseif global_mindset == Mindset.CAUTIOUS then
		for i = 1, MAX_BALLS do
			if math.random(10) <= 8 then
				ball_list[i].vx = math.random(-30, 30)	
				ball_list[i].vy = math.random(-30, 30)				
			end
		end			
	elseif global_mindset == Mindset.LOCKDOWN then
		for i = 1, MAX_BALLS do
			if math.random(10) <= 5 then
				ball_list[i].vx = 0
				ball_list[i].vy = 0			
			end
		end		
	end
end

-- vaccine mode to vaccinate 80% of the population
function vaccine_mode()
	for i = 1, MAX_BALLS do
		if math.random(10) <= vaccination_rate then
			ball_list[i].vaccinated = true
			ball_list[i].state = Status.VACCINATED
		end
	end	
end

-- update population ball status numbers
function update_numbers(dt)
	
	for i = 1, MAX_BALLS do
		
		ball_list[i]:update_status(dt)
		if ball_list[i].state == Status.NORMAL then
			normal_count = normal_count + 1
		elseif ball_list[i].state == Status.INFECTED then
			infected_count = infected_count + 1
		elseif ball_list[i].state == Status.RECOVERED then
			recovered_count = recovered_count + 1
		elseif ball_list[i].state == Status.VACCINATED then
			vaccinated_count = vaccinated_count + 1
		elseif ball_list[i].state == Status.DEAD then
			dead_count = dead_count + 1
		end	
	end
end