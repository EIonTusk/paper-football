import arcade
import numpy as np

class GameView(arcade.View):
    
    def __init__(self) -> None:
        # width, height, distance of lines
        self.x = 630
        self.y = 930
        self.mul = 30

        # setting up the menu
        menu_view.setup()

        super().__init__()

    def setup(self):
        # keeps track of seen and unseen points
        self.array = np.full((self.x//self.mul, self.y//self.mul), -1, dtype=int)
        self.array_size_x, self.array_size_y = self.array.shape

        self.currentplayer = 0

        # pass counter
        self.counter = 3
        
        # goal x values
        self.goal = [9, 10, 11]

        # initializing
        self.motion_x = 0
        self.motion_y = 0
        self.array_x = self.array_size_x//2
        self.array_y = self.array_size_y//2

        # creating the goalposts in the grid
        for y in [0,1,self.array_size_y-2, self.array_size_y-1]:
            for x in range(self.array_x-2,self.array_x+3,4):
                if y == 0:
                    self.array[x][y] = 0
                else:
                    self.array[x][y] = 1

        # setting start as used point
        self.array[self.array_x][self.array_y] = 0

        # penalty multiplikator
        self.penmul = 6 * self.mul

        # initializing
        self.penalty = False
        self.finished = False

        # seting start ball coordinates
        self.ball_x = self.x//2
        self.ball_y = self.y//2
        self.ball_array_x = self.array_x
        self.ball_array_y = self.array_y

        # set player colors
        self.playercolor = (arcade.color.BALL_BLUE, arcade.color.BITTER_LIME)

        # keeping track of passes
        # for drawing
        self.pass_list = []
        # for detecting crossings
        self.connectors_dict = {i: [] for i in range(self.array_size_x*self.array_size_y)}

        # creating texts
        self.penalty_vis = arcade.Text("PENALTY!", 30, 30, arcade.color.BLACK, 24)
        self.finish = arcade.Text(f"The Winner is: ", self.x//2, self.y//2 +60, arcade.color.BLACK, 45, anchor_x="center")

        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()

        # grid
        for x in range(15, self.x+1, 30):
            arcade.draw_line(x, 0, x, max(self.x,self.y), arcade.color.BATTLESHIP_GREY, 2)

        for y in range(15, self.y+1, 30):
            arcade.draw_line(0, y, max(self.x,self.y), y, arcade.color.BATTLESHIP_GREY, 2)

        # goals
        arcade.draw_line(self.x//2-(2*self.mul), 15, self.x//2-2*self.mul, self.mul+15, arcade.color.BLACK, 4)
        arcade.draw_line(self.x//2+2*self.mul, 15, self.x//2+2*self.mul, self.mul+15, arcade.color.BLACK, 4)
        arcade.draw_line(self.x//2-2*self.mul, 15, self.x//2+2*self.mul, 15, arcade.color.BLACK, 4)
        arcade.draw_circle_filled(self.x//2-(2*self.mul), 15, 4, self.playercolor[0])
        arcade.draw_circle_filled(self.x//2+(2*self.mul), 15, 4, self.playercolor[0])

        arcade.draw_line(self.x//2-2*self.mul, self.y-15, self.x//2-2*self.mul, self.y-self.mul-15, arcade.color.BLACK, 4)
        arcade.draw_line(self.x//2+2*self.mul, self.y-15, self.x//2+2*self.mul, self.y-self.mul-15, arcade.color.BLACK, 4)
        arcade.draw_line(self.x//2-2*self.mul, self.y-15, self.x//2+2*self.mul, self.y-15, arcade.color.BLACK, 4)
        arcade.draw_circle_filled(self.x//2-(2*self.mul), self.y-15, 4, self.playercolor[1])
        arcade.draw_circle_filled(self.x//2+(2*self.mul), self.y-15, 4, self.playercolor[1])

        # center line
        arcade.draw_line(0, self.y//2, self.x, self.y//2, arcade.color.BLACK, 4)
        arcade.draw_circle_outline(self.x//2, self.y//2, self.mul, arcade.color.BLACK, 4)

        # current player
        arcade.draw_rectangle_filled(self.x-30, self.y-30, 15, 15, self.playercolor[self.currentplayer])
        arcade.draw_rectangle_outline(self.x-30, self.y-30, 15, 15, arcade.color.BLACK)

        # create past passes
        px = self.x//2
        py = self.y//2

        for pas in self.pass_list:
            arcade.draw_line(px, py, pas[0], pas[1], self.playercolor[pas[2]], 3)
            px, py, _ = pas


        # breate ball
        arcade.draw_circle_filled(self.ball_x, self.ball_y, 5, arcade.color.WHITE)
        arcade.draw_circle_outline(self.ball_x, self.ball_y, 5, arcade.color.BLACK, 1)

        # create mousepoint
        arcade.draw_circle_filled(self.motion_x, self.motion_y, 3, arcade.color.BLACK)

        # stop if finished
        if self.finished:
            self.finish.draw()
            self.finish_col.draw()

        # Penalty Text
        if self.penalty: self.penalty_vis.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        # updating coordinates for the mousepoint
        fak = 0.5
        if self.penalty: fak = 3
        mulx = 0
        if x < self.ball_x - fak*self.mul: mulx = -1
        elif x > self.ball_x + fak*self.mul: mulx = 1
        muly = 0
        if y < self.ball_y - fak*self.mul: muly = -1
        elif y > self.ball_y + fak*self.mul: muly = 1

        if self.penalty:
            self.motion_x = self.ball_x + mulx * self.penmul
            self.motion_y = self.ball_y + muly * self.penmul
            self.array_x = self.ball_array_x + 6*mulx
            self.array_y = self.ball_array_y + 6*muly
        else:
            self.motion_x = self.ball_x + mulx * self.mul
            self.motion_y = self.ball_y + muly * self.mul
            self.array_x = self.ball_array_x + mulx
            self.array_y = self.ball_array_y + muly
    

    def on_mouse_press(self, x, y, button, modifiers):
        if self.finished: return
        
        # undo last pass
        if button == 4:
            old_x, old_y, _ = self.pass_list[-2]
            del self.pass_list[-1]

            # calculate array_positions
            old_array_x = (old_x-15)//self.mul
            old_array_y = (old_y-15)//self.mul

            # get offset
            dx = self.ball_array_x - old_array_x
            dy = self.ball_array_y - old_array_y

            # detects if last pass was penalty
            if abs(self.ball_array_x-old_array_x) > 1 or abs(self.ball_array_y-old_array_y) > 1:
                dx //= -6
                dy //= -6

                # resets connectors
                for i in range(1,7):
                    self.connectors_dict[(self.ball_array_x + (i-1)*dx)*self.array_size_y+(self.ball_array_y + (i-1)*dy)].remove((self.ball_array_x + i*dx)*self.array_size_y+(self.ball_array_y + i*dy))
                    self.connectors_dict[(self.ball_array_x + i*dx)*self.array_size_y+(self.ball_array_y + i*dy)].remove((self.ball_array_x + (i-1)*dx)*self.array_size_y+(self.ball_array_y + (i-1)*dy))
                    
                    #resets grid
                    self.array[self.ball_array_x + i*dx][self.ball_array_y + i*dy] = -1
                self.penalty = True
            
            # no penalty before

            # resets connectors
            self.connectors_dict[self.ball_array_x*self.array_size_y+self.ball_array_y].remove(old_array_x*self.array_size_y+old_array_y)
            self.connectors_dict[old_array_x*self.array_size_y+old_array_y].remove(self.ball_array_x*self.array_size_y+self.ball_array_y)

            # resets grid
            self.array[self.ball_array_x][self.ball_array_y] = -1

            # reset passcounter
            if self.counter == 3:
                self.currentplayer = (self.currentplayer+1)%2
                self.counter = 1
            else: self.counter += 1

            # reset coordinates
            self.ball_array_x = old_array_x
            self.ball_array_y = old_array_y

            self.ball_x = old_x
            self.ball_y = old_y

            self.array_x = old_array_x
            self.array_y = old_array_y

            return

        # calculating offset
        dx = self.array_x - self.ball_array_x
        dy = self.array_y - self.ball_array_y

        # detects already taken points (ignores if penalty)
        if self.array[self.array_x][self.array_y] >= 0 and not self.penalty: return

        # avoids passing the ball to the same spot while having a penalty
        if dx == 0 and dy == 0: return

        # detects crossing a former pass
        if abs(dx + dy) != 1 and self.ball_array_x*self.array_size_y+self.array_y in self.connectors_dict[self.array_x*self.array_size_y+self.ball_array_y]: return

        # checks if in goal
        if self.array_x in self.goal:
            if self.array_y == 0:
                self.finished = True
                self.finish_col = arcade.create_rectangle(self.x//2, self.y//2, 60, 60, self.playercolor[1])
            elif self.array_y == self.array.shape[1]-1:
                self.finish_col = arcade.create_rectangle(self.x//2, self.y//2, 60, 60, self.playercolor[0])
                self.finished = True
        
        # updates ball position
        self.ball_x = self.motion_x
        self.ball_y = self.motion_y

        # marks point as taken
        self.array[self.array_x][self.array_y] = self.currentplayer

        # adding the pass to the list for drawing
        self.pass_list.append((self.ball_x, self.ball_y, self.currentplayer))
        
        # adding the pass to the dict for detecting crossing lines
        self.connectors_dict[self.ball_array_x*self.array_size_y+self.ball_array_y].append(self.array_x*self.array_size_y+self.array_y)
        self.connectors_dict[self.array_x*self.array_size_y+self.array_y].append(self.ball_array_x*self.array_size_y+self.ball_array_y)        

        if self.penalty: 
            dx //= 6
            dy //= 6
            
            # adds all passes to dict and marks as points as taken
            for i in range(1,7):
                self.connectors_dict[(self.ball_array_x + (i-1)*dx)*self.array_size_y+(self.ball_array_y + (i-1)*dy)].append((self.ball_array_x + i*dx)*self.array_size_y+(self.ball_array_y + i*dy))
                self.connectors_dict[(self.ball_array_x + i*dx)*self.array_size_y+(self.ball_array_y + i*dy)].append((self.ball_array_x + (i-1)*dx)*self.array_size_y+(self.ball_array_y + (i-1)*dy))
                self.array[self.ball_array_x + i*dx][self.ball_array_y + i*dy] = self.currentplayer

            # resets
            self.counter = 1
            self.penalty = False

        # sets counter / switches player
        if self.counter == 1:
            self.counter = 3
            self.currentplayer = (self.currentplayer+1)%2
        else: self.counter -= 1

        # updating
        self.ball_array_x = self.array_x
        self.ball_array_y = self.array_y

        # checking if 3 passes are possible
        if self.counter == 3 and not self.penalty_detection(self.ball_array_x, self.ball_array_y):
            self.currentplayer = (self.currentplayer+1)%2
            self.penalty = True

        # more enjoyable mouseindicator movement 
        self.on_mouse_motion(x,y,0,0)

    def on_key_press(self, key, modifiers):
        # checks for pressing "m"
        if key == 109:
            window.show_view(menu_view)

    def penalty_detection(self, ci, cj, depth = 0):
        # detects penalty by dfs
        if depth == 3: return True
        for i in range(-1,2):
            if ci+i < 0 or ci+i > self.array_size_x-1: continue
            for j in range(-1,2):
                if cj+j < 0 or cj+j > self.array_size_y-1: continue
                if i == 0 and j == 0: continue
                if self.array[ci+i][cj+j] >= 0: continue
                if abs(i + j) != 1 and ci*self.array_size_y+cj+j in self.connectors_dict[(ci+i)*self.array_size_y+cj]: continue
                self.array[ci+i][cj+j] = 0
                if self.penalty_detection(ci+i, cj+j, depth+1):
                    self.array[ci+i][cj+j] = -1
                    return True
                self.array[ci+i][cj+j] = -1
        return False


class MenuView(arcade.View):
    def setup(self):
        # creates texts
        self.menu_text = arcade.Text("Menu", WIDTH//2, HEIGHT-120, arcade.color.WHITE, 60, anchor_x="center", anchor_y="center")
        self.resume_text = arcade.Text("Back to the game", WIDTH//2, HEIGHT-240, arcade.color.BLACK, 15, anchor_x="center", anchor_y="center")
        self.reset_text = arcade.Text("Reset the game", WIDTH//2, HEIGHT-330, arcade.color.BLACK, 15, anchor_x="center", anchor_y="center")
        self.exit_text = arcade.Text("Exit", WIDTH//2, 60, arcade.color.BLACK, 15, anchor_x="center", anchor_y="center")

        # creates gif
        self.logo = arcade.load_animated_gif("media/ronaldinho.gif")
        self.logo.center_x = WIDTH//2
        self.logo.center_y = 330
        self.logo.scale = 1.4

    def on_show_view(self):
        # sets bg
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)
    
    def on_draw(self):
        self.clear()

        # buttons
        w, h = 270, 60
        arcade.draw_rectangle_filled(WIDTH//2, HEIGHT-240, w, h, arcade.color.WHITE)
        arcade.draw_rectangle_filled(WIDTH//2, HEIGHT-330, w, h, arcade.color.WHITE)
        arcade.draw_rectangle_filled(WIDTH//2, 60, 120, h, arcade.color.AMARANTH)

        # drawing texts
        self.menu_text.draw()
        self.reset_text.draw()
        self.resume_text.draw()
        self.exit_text.draw()

        # drawing and updating gif
        self.logo.draw()
        self.logo.update_animation()

    def on_mouse_press(self, x, y, key, modifiers):
        # checks which button is pressed
        if x > WIDTH//2+135 or x < WIDTH//2-135: return
        if y >= HEIGHT-270 and y <= HEIGHT-210:
            # resume game
            arcade.set_background_color(arcade.color.WHITE)
            window.show_view(game_view)
            return
        if y >= HEIGHT-360 and y <= HEIGHT-300:
            # reset game
            game_view.setup()
            window.show_view(game_view)
            return
        if x <= WIDTH//2+60 and x >= WIDTH//2-60 and y >= 30 and y <= 90:
            # exit
            arcade.close_window()


class InstructionView(arcade.View):
    def setup(self):
        # creating texts
        self.heading = arcade.Text("Controls:", WIDTH//2, HEIGHT//2+60, arcade.color.WHITE, 30, anchor_x="center", anchor_y="center")
        self.text1 = arcade.Text("Left click: passing the ball", WIDTH//2, HEIGHT//2, arcade.color.WHITE, 12, anchor_x="center", anchor_y="center")
        self.text2 = arcade.Text("Right click: undo the last pass", WIDTH//2, HEIGHT//2-30, arcade.color.WHITE, 12, anchor_x="center", anchor_y="center")
        self.text3 = arcade.Text("Pressing m: opening the menu", WIDTH//2, HEIGHT//2-60, arcade.color.WHITE, 12, anchor_x="center", anchor_y="center")

        self.continue_text = arcade.Text("Press any key to continue...", WIDTH//2, 120, arcade.color.WHITE, 15, anchor_x="center", anchor_y="center")

    def on_show_view(self):
        # setting bg
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

    def on_draw(self):
        self.clear()

        # drawing texts
        self.heading.draw()
        self.text1.draw()
        self.text2.draw()
        self.text3.draw()
        self.continue_text.draw()

    def on_mouse_press(self, _x, _y, _key, _modifier):
        # checking for any mouse press then opening the game
        game_view.setup()
        window.show_view(game_view)

    def on_key_press(self, _key, _modifiers):
        # checking for any key press then opening the game
        game_view.setup()
        window.show_view(game_view)

# declaring standard size
WIDTH = 630
HEIGHT = 930

if __name__ == "__main__":
    # creating window
    window = arcade.Window(WIDTH, HEIGHT, "Paper Football")

    # creating views
    instruction_view = InstructionView()
    menu_view = MenuView()
    game_view = GameView()
    
    # setting up instruction view
    instruction_view.setup()
    window.show_view(instruction_view)

    # start arcade module
    arcade.run() 
