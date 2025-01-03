import pygame as pg
import threading as thrd
import time
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser

class Object():
    def __init__(self, x, y, w, h, m, d, mi, d_c, b_c, s):
        self.id = len(app.objects)
        self.x, self.y = x, y
        self.width, self.height = w, h #cm
        self.aera = self.width*self.height*10**-4 #cm^2
        self.color = (0, 255, 0)
        self.shape = s
        self.mass = m #Kg
        self.density = d #g/L
        self.micro = mi #dry friction
        self.f_x, self.f_y = [], [] #N
        self.v = (0, 0) #cm/s
        self.a = (0, 0) #cm/s^2
        self.f = (0, 0) #N
        self.t = 1/app.FPS #s
        self.drag_coeff = d_c
        self.bounce_coeff = b_c
        self.k_energy = 0 #J
        self.p_energy = 0 #J
        self.energy = self.k_energy+self.p_energy #J
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)
        self.height = self.width if self.shape == 'circle' else self.height
        
    def collision(self):
        for i in app.objects:
            if i.id != self.id:
                if self.shape == 'rect':
                    if i.shape == 'rect':
                        if self.rect.colliderect(i.rect):
                            if abs((i.x+i.width/2)-(self.x+self.width/2)) > abs((i.y+i.height/2)-(self.y+self.height/2)):
                                if self.x<i.x:
                                    self.x = i.x-self.width-1
                                else:
                                    self.x = i.x+i.width+1
                                self.v = (self.v[0]*-self.bounce_coeff, self.v[1])
                            else:
                                if self.y<i.y:
                                    if not self.y+self.height >= app.HEIGHT:
                                        self.y = i.y+-i.height-1
                                self.v = (self.v[0], self.v[1]*-self.bounce_coeff)
                    if i.shape == 'circle':
                        if self.rect.colliderect(i.rect):
                            for j in (self.x, self.x+self.width/2, self.x+self.width):
                                for k in (self.y, self.y+self.height/2, self.y+self.height):
                                    if np.hypot(abs(j-(i.x+i.width/2)), abs(k-(i.y+i.width/2))) < i.width/2:
                                        if abs((i.x+i.width/2)-(self.x+self.width/2)) > abs((i.y+i.width/2)-(self.y+self.height/2)):
                                            if self.x<i.x:
                                                self.x = i.x-self.width-1
                                            else:
                                                self.x = i.x+i.width+1
                                            self.v = (self.v[0]*-self.bounce_coeff, self.v[1])
                                        else:
                                            if self.y<i.y:
                                                if not self.y+self.height >= app.HEIGHT:
                                                    self.y = i.y+-i.width-1
                                            self.v = (self.v[0], self.v[1]*-self.bounce_coeff)
                                
                if self.shape == 'circle':
                    if i.shape == 'rect':
                        if self.rect.colliderect(i.rect):
                            for j in (i.x, i.x+i.width/2, i.x+i.width):
                                for k in (i.y, i.y+i.height/2, i.y+i.height):
                                    if np.hypot(abs(j-(self.x+self.width/2)), abs(k-(self.y+self.width/2))) < self.width/2:
                                        if abs((i.x+i.width/2)-(self.x+self.width/2)) > abs((i.y+i.height/2)-(self.y+self.width/2)):
                                            if self.x<i.x:
                                                self.x = i.x-self.width-1
                                            else:
                                                self.x = i.x+i.width+1
                                            self.v = (self.v[0]*-self.bounce_coeff, self.v[1])
                                        else:
                                            if self.y<i.y:
                                                if not self.y+self.width >= app.HEIGHT:
                                                    self.y = i.y+-i.height-1
                                            self.v = (self.v[0], self.v[1]*-self.bounce_coeff)
                    if i.shape == 'circle':
                        if np.hypot(abs((i.x+i.width/2)-(self.x+self.width/2)), abs((i.y+i.width/2)-(self.y+self.width/2))) < self.width/2+i.width/2:
                            if abs((i.x+i.width/2)-(self.x+self.width/2)) > abs((i.y+i.height/2)-(self.y+self.width/2)):
                                if self.x<i.x:
                                    self.x = i.x-self.width-1
                                else:
                                    self.x = i.x+i.width+1
                                self.v = (self.v[0]*-self.bounce_coeff, self.v[1])
                            else:
                                if self.y<i.y:
                                    if not self.y+self.width >= app.HEIGHT:
                                        self.y = i.y+-i.height-1
                                self.v = (self.v[0], self.v[1]*-self.bounce_coeff)
                                
    def update(self):
        self.t = 1/app.FPS
        self.f_y.append(self.mass*app.g) #weight force
        self.f_x.append(self.micro*self.f[1]*-float(np.sign(self.v[0]))*(self.y+self.height>app.HEIGHT)) #static friction force
        self.f_y.append(0.5*app.air_density*-self.v[1]*self.drag_coeff)
        self.f_x.append(0.5*app.air_density*-self.v[0]*self.drag_coeff)
        
        self.f = (sum(self.f_x), sum(self.f_y))
        self.a = (self.f[0]/self.mass, self.f[1]/self.mass)
        self.a = (self.a[0], self.a[1])
        self.v = (self.v[0]+self.a[0]*self.t, self.v[1]+self.a[1]*self.t)
        
        if app.collision:
            self.collision()
            
        if self.y+self.height>app.HEIGHT:
            if self.f[1]>0: self.v = (self.v[0], round(-self.v[1]*self.bounce_coeff, 1))
            self.y = app.HEIGHT-self.height
        if self.x < 0:
            if self.f[0]<0: self.v = (round(-self.v[0]*self.bounce_coeff, 1), self.v[1])
            self.x = 0
        if self.x+self.width>app.WIDTH:
            if self.f[0]>0: self.v = (round(-self.v[0]*self.bounce_coeff, 1), self.v[1])
            self.x = app.WIDTH-self.width
            
        self.k_energy = 0.5*self.mass*(self.v[0]**2+self.v[1]**2)
        self.p_energy = self.mass*app.g*(app.HEIGHT-self.y-self.height)
        self.energy = self.k_energy+self.p_energy
            
        self.x += self.v[0]
        self.y += self.v[1]

        self.f_x, self.f_y = [], []
        
    def draw(self):
        if self.shape == 'rect':
            self.rect = pg.draw.rect(app.screen, self.color, pg.Rect(self.x, self.y, self.width, self.height))
        elif self.shape == 'circle':
            self.rect = pg.draw.circle(app.screen, self.color, (self.x+self.width/2, self.y+self.width/2), self.width/2)
        if app.show_forces:
            pg.draw.line(app.screen, (0, 0, 255), (self.x+self.width/2, self.y+self.height/2), (self.x+self.f[0]+self.width/2, self.y+self.height/2), 5)
            pg.draw.line(app.screen, (255, 0, 0), (self.x+self.width/2, self.y+self.height/2), (self.x+self.width/2, self.y+self.f[1]+self.height/2), 5)


class Window():
    def __init__(self):
        pass
        
    def param_apply(self):
        try: app.air_density = float(self.air_density.get())
        except: pass
        try: app.g = float(self.g.get())
        except: pass
        try: app.FPS = int(self.FPS.get())
        except: pass
        try: app.collision = int(self.coll.get())
        except: pass
        try: app.tkinter_inspect_rate = int(self.rate_0.get())
        except: pass
        try: app.background_color = self.bckgrnd_color
        except: pass
        self.root.destroy()
        
    def background_color_changer(self):
        try: 
            self.bckgrnd_color = colorchooser.askcolor(title='Choose the new background color')
            self.bckgrnd_color = self.bckgrnd_color[0]
        except: pass
    
    def param(self):
        self.root = tk.Tk()
        self.root.title('Modify parameter')
        
        self.air_density = tk.StringVar(value=str(app.air_density))
        self.g = tk.StringVar(value=str(app.g))
        self.FPS = tk.StringVar(value=str(app.FPS))
        self.coll = tk.BooleanVar(value=app.collision)
        self.rate_0 = tk.StringVar(value=app.tkinter_inspect_rate)
        self.bckgrnd_color = app.background_color
        
        tk.Label(self.root, text=' Air density : ').grid(row=0)
        tk.Label(self.root, text=' Gravity Acceleration : ').grid(row=1)
        tk.Label(self.root, text=' Image per sec. : ').grid(row=2)
        tk.Label(self.root, text=' Collisions : ').grid(row=3)
        tk.Label(self.root, text=' Refresh rate of the object inspector : ').grid(row=4)
        tk.Label(self.root, text=' Background color : ').grid(row=5)
        
        self.b0 = tk.Entry(self.root, textvariable=self.air_density).grid(row=0, column=1)
        self.b1 = tk.Entry(self.root, textvariable=self.g).grid(row=1, column=1)
        self.b2 = tk.Entry(self.root, textvariable=self.FPS).grid(row=2, column=1)
        self.b3 = tk.Checkbutton(self.root, variable=self.coll).grid(row=3, column=1)
        self.b4 = tk.Entry(self.root, textvariable=self.rate_0).grid(row=4, column=1)
        self.b5 = tk.Button(self.root, text=' change color ', command=self.background_color_changer).grid(row=5, column=1)
        
        tk.Label(self.root, text=' (Kg/m^3) Default: 1.29 ').grid(row=0, column=2)
        tk.Label(self.root, text=' (m/s^2) Default: 9.81 ').grid(row=1, column=2)
        tk.Label(self.root, text=' (Hz) Default: 60 ').grid(row=2, column=2)
        tk.Label(self.root, text=' () Default: Yes ').grid(row=3, column=2)
        tk.Label(self.root, text=' (ms) Default: 200 ').grid(row=4, column=2)
        tk.Label(self.root, text=' (RGB) Default: (135, 205, 235) ').grid(row=5, column=2)
        
        tk.Button(self.root, text=' Apply ', command=self.param_apply).grid()
        tk.Button(self.root, text=' Cancel ', command=self.root.destroy).grid()
        
        self.root.mainloop()
        
    def create_obj_0(self):
        try: self.width = int(self.w.get())
        except: self.width = 100
        try: self.height = int(self.h.get())
        except: self.height = 100
        try: self.mass = float(self.m.get())
        except: self.mass = 1.5
        try: self.density = float(self.d.get())
        except: self.density = 1500
        try: self.micro = float(self.mi.get())
        except: self.micro = 1
        try: self.drag_coeff = float(self.d_c.get())
        except: self.drag_coeff = 1.05
        try: self.drag_coeff = float(self.b_c.get())
        except: self.bounce_coeff = 0.10
        try: self.shape = str(self.e7.get()) if str(self.e7.get()) != '' else 'rect'
        except: self.shape = 'rect'
    
        app.objects.append(Object(self.x, self.y, self.width, self.height, self.mass, self.density, self.micro, self.drag_coeff, self.bounce_coeff, self.shape))
        self.root.destroy()
        
    def custom_preset(self):
        for widget in self.frame_0.winfo_children():
            widget.destroy()
        self.w, self.h, self.m, self.d, self.mi, self.d_c, self.b_c, self.s = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
        
        tk.Label(self.root, text=' Width : ').grid(row=0, column=0)
        tk.Label(self.root, text=' Height : ').grid(row=1, column=0)
        tk.Label(self.root, text=' Mass : ').grid(row=2, column=0)
        tk.Label(self.root, text=' Density : ').grid(row=3, column=0)
        tk.Label(self.root, text=' Friction coeff. : ').grid(row=4, column=0)
        tk.Label(self.root, text=' Dragg coeff. : ').grid(row=5, column=0)
        tk.Label(self.root, text=' Bounce coeff. : ').grid(row=6, column=0)
        tk.Label(self.root, text=' Shape : ').grid(row=7, column=0)
        
        self.e0 = tk.Entry(self.root, textvariable=self.w).grid(row=0, column=1)
        self.e1 = tk.Entry(self.root, textvariable=self.h).grid(row=1, column=1)
        self.e2 = tk.Entry(self.root, textvariable=self.m).grid(row=2, column=1)
        self.e3 = tk.Entry(self.root, textvariable=self.d).grid(row=3, column=1)
        self.e4 = tk.Entry(self.root, textvariable=self.mi).grid(row=4, column=1)
        self.e5 = tk.Entry(self.root, textvariable=self.d_c).grid(row=5, column=1)
        self.e6 = tk.Entry(self.root, textvariable=self.b_c).grid(row=6, column=1)
        self.e7 = ttk.Combobox(self.root, state='readonly', values=['rect', 'circle'], textvariable=self.s)
        self.e7.grid(row=7, column=1)
        
        tk.Label(self.root, text=' (cm) Default: 100 ').grid(row=0, column=2)
        tk.Label(self.root, text=' (cm) Default: 100 ').grid(row=1, column=2)
        tk.Label(self.root, text=' (Kg) Default: 1.50 ').grid(row=2, column=2)
        tk.Label(self.root, text=' (g/L) Default: 1500 ').grid(row=3, column=2)
        tk.Label(self.root, text=' () Default: 1.00 ').grid(row=4, column=2)
        tk.Label(self.root, text=' () Default: 1.05 ').grid(row=5, column=2)
        tk.Label(self.root, text=' () Default: 0.10 ').grid(row=6, column=2)
        tk.Label(self.root, text=' () Default: rect ').grid(row=7, column=2)
        
        tk.Button(self.root, text=' Create ', command=self.create_obj_0).grid(row=8, column=1)
        
        
    def update_get_info(self):
        index = self.index
        self.l0.configure(text=' Index : '+str(index)+' on '+str(len(app.objects)))
        self.l1.configure(text=' Width : '+str(app.objects[index].width)+' cm ')
        self.l2.configure(text=' Height : '+str(app.objects[index].height)+' cm ')
        self.l3.configure(text=' Aera : '+str(app.objects[index].aera)+' cm^2 ')
        self.l4.configure(text=' Shape : '+str(app.objects[index].shape))
        self.l5.configure(text=' Color : '+str(app.objects[index].color)+' RGB ')
        self.l6.configure(text=' Mass : '+str(app.objects[index].mass)+' Kg ')
        self.l7.configure(text=' Density : '+str(app.objects[index].density)+' g/L ')
        self.l8.configure(text=' Friction coeff. : '+str(app.objects[index].micro))
        self.l9.configure(text=' Forces : '+str(app.objects[index].f)+' N ')
        self.l10.configure(text=' Acceleration : '+str(app.objects[index].a)+' m/s^2 ')
        self.l11.configure(text=' Speed : '+str(app.objects[index].v)+' m/s ')
        self.l12.configure(text=' Drag coeff. : '+str(app.objects[index].drag_coeff))
        self.l13.configure(text=' Bounce coeff. : '+str(app.objects[index].bounce_coeff))
        self.l14.configure(text=' Position : '+str((app.objects[index].x, app.objects[index].y))+' cm ')
        self.l15.configure(text=' Kinetic Energy : '+str(app.objects[index].k_energy)+' J ')
        self.l16.configure(text=' Potential Energy : '+str(app.objects[index].p_energy)+' J ')
        self.l17.configure(text=' Total Energy : '+str(app.objects[index].energy)+' J ')
        
        self.root.after(app.tkinter_inspect_rate, self.update_get_info)
        
    def get_info(self, index):
        self.root = tk.Tk()
        self.root.title(' Object informations ')
        
        self.index = index
        
        self.l0 = tk.Label(self.root, text='')
        self.l1 = tk.Label(self.root, text='')
        self.l2 = tk.Label(self.root, text='')
        self.l3 = tk.Label(self.root, text='')
        self.l4 = tk.Label(self.root, text='')
        self.l5 = tk.Label(self.root, text='')
        self.l6 = tk.Label(self.root, text='')
        self.l7 = tk.Label(self.root, text='')
        self.l8 = tk.Label(self.root, text='')
        self.l9 = tk.Label(self.root, text='')
        self.l10 = tk.Label(self.root, text='')
        self.l11 = tk.Label(self.root, text='')
        self.l12 = tk.Label(self.root, text='')
        self.l13 = tk.Label(self.root, text='')
        self.l14 = tk.Label(self.root, text='')
        self.l15 = tk.Label(self.root, text='')
        self.l16 = tk.Label(self.root, text='')
        self.l17 = tk.Label(self.root, text='')
        
        self.l0.grid(row=0)
        self.l1.grid(row=1)
        self.l2.grid(row=2)
        self.l3.grid(row=3)
        self.l4.grid(row=4)
        self.l5.grid(row=5)
        self.l6.grid(row=6)
        self.l7.grid(row=7)
        self.l8.grid(row=8)
        self.l9.grid(row=9)
        self.l10.grid(row=10)
        self.l11.grid(row=11)
        self.l12.grid(row=12)
        self.l13.grid(row=13)
        self.l14.grid(row=14)
        self.l15.grid(row=15)
        self.l16.grid(row=16)
        self.l17.grid(row=17)
        
        self.update_get_info()
        
        self.root.mainloop()
        
    def create_obj_1(self):
        try: self.w = int(self.a2.get())
        except: self.w = 100
        try: self.h = int(self.a3.get())
        except: self.h = 100
        try: self.s = self.a0.get() if self.a0.get() != '' else 'rect'
        except: self.s = 'rect'
        self.d = [600, 900, 2400, 7800][['wood', 'ice', 'stone', 'iron'].index(self.a1.get())]
        self.m = self.d*self.w*(10**-2)*self.h*(10**-2)*10**-3
        self.b_c = [0.4, 0.05, 0.2, 0.2][['wood', 'ice', 'stone', 'iron'].index(self.a1.get())]
        self.f_c = 0.1
        self.d_c = [1.05, 0.47][['rect', 'circle'].index(self.s)]
        
        app.objects.append(Object(self.x, self.y, self.w, self.h, self.m, self.d, self.f_c, self.d_c, self.b_c, self.s))
        
        self.root.destroy()
    
    def create_menu(self, x, y):
        self.x, self.y = x, y
        self.root = tk.Tk()
        self.root.title('Create an object')
        
        self.frame_0 = tk.Frame(self.root, width=100, height=100)
        self.frame_0.grid(row=0, column=0)
        
        tk.Label(self.frame_0, text=' Shape : ').grid(row=0, column=0)
        tk.Label(self.frame_0, text=' Material : ').grid(row=1, column=0)
        tk.Label(self.frame_0, text=' Width : ').grid(row=2, column=0)
        tk.Label(self.frame_0, text=' Height : ').grid(row=3, column=0)
        
        self.a0 = ttk.Combobox(self.frame_0, state='readonly', values=['rect', 'circle'])
        self.a1 = ttk.Combobox(self.frame_0, state='readonly', values=['wood', 'ice', 'stone', 'iron']) # 0.1, 0.1, 0.1, 0.1 for friction(flemme)
        self.a2 = tk.Entry(self.frame_0)                                                                # 0.4, 0.05, 0.20, 0.2 for restitution
        self.a3 = tk.Entry(self.frame_0)
        self.a0.grid(row=0, column=1)
        self.a1.grid(row=1, column=1)
        self.a2.grid(row=2, column=1)
        self.a3.grid(row=3, column=1)
        
        tk.Label(self.frame_0, text=' Default : rectangle ').grid(row=0, column=2)
        tk.Label(self.frame_0, text=' Default : None ').grid(row=1, column=2)
        tk.Label(self.frame_0, text=' Default : 100 cm').grid(row=2, column=2)
        tk.Label(self.frame_0, text=' Default : 100 cm').grid(row=3, column=2)
        
        tk.Button(self.frame_0, text=' Cancel ', command=self.root.destroy).grid(row=4, column=0)
        tk.Button(self.frame_0, text=' Create ', command=self.create_obj_1).grid(row=4, column=1)
        tk.Button(self.frame_0, text=' Custom ', command=self.custom_preset).grid(row=4, column=2)
        
        self.root.mainloop()
        
class App():
    def __init__(self):
        self.RES = self.WIDTH, self.HEIGHT = 1600, 900
        pg.init()
        pg.font.init()
        self.FPS = 60
        self.time_scale = (1, 1)
        self.g = 9.81
        self.objects = []
        self.mouse_pos = (0, 0)
        self.font = pg.font.SysFont('Corbel', 26)
        self.font_18 = pg.font.SysFont('Corbel', 18)
        self.menu_buttons = [[' Create Object ', self.font, (20, 40), (255, 0, 0)],
                        [' Show Forces ', self.font, (40+168, 40), (50, 200, 50)],
                        [' Start Trajectory Analysis ', self.font, (60+168+141, 40), (100, 100, 255)],
                        [' Modify Simulation Parameters ', self.font, (80+309+257, 40), (255, 220, 35)],
                        [' Show information object ', self.font, (100+566+325, 40), (160, 40, 240)]
                        ]
        self.threads = []
        self.drag_index = -1
        self.keys = 0
        self.allow_dragging = True
        self.mouse_pos = (0, 0)
        self.click = False
        self.show_forces = True
        self.trajectory = False
        self.air_density = 1.29
        self.collision = True
        self.tkinter_inspect_rate = 200
        self.background_color = (135, 205, 235)
        self.l_panel = [False]
        self.l_p_offset = -200
        self.i = 0
        self.tool = None
        self.buttons_0 = [[' Drag object ', self.font_18, (255, 0, 0)]]
        
    def render(self):
        for i in self.objects:
            if self.time_scale[1]: i.update()
            i.draw()
            
    def button(self, index):
        if index == 0:
            time.sleep(0.1)
            running = True
            while running:
                x, y = pg.mouse.get_pos()
                for event in pg.event.get():
                    if event.type == pg.MOUSEBUTTONDOWN: 
                        running = False
            self.Window.create_menu(x, y)
        if index == 1:
            self.show_forces = False if self.show_forces else True
            time.sleep(0.1)
        if index == 2:
            if self.trajectory:
                with open('trajectory_data.txt', 'w') as f: pass
                with open('trajectory_data.txt', 'w') as f:
                    f.write(str(self.traj_points))
                self.trajectory = False 
                self.menu_buttons[3][0] = ' Start Trajectory Analysis '
            else:
                self.trajectory = True
                self.menu_buttons[3][0] = ' Stop Trajectory Analysis '
                self.traj_points = [[] for i in self.objects]
            time.sleep(0.1)
        if index == 3:
            time.sleep(0.1)
            self.Window.param() 
        if index == 4:
            time.sleep(0.1)
            running = True
            while running:
                x, y = pg.mouse.get_pos()
                for event in pg.event.get():
                    if event.type == pg.MOUSEBUTTONDOWN: 
                        running = False
            for i, j in enumerate(self.objects):
                if j.rect.collidepoint(x, y):
                    self.threads.append(thrd.Thread(target=self.Window.get_info, args=(i, )))
                    self.threads[len(self.threads)-1].start()
                    return
    
    def calc_traj(self):
        for i in range(len(self.traj_points)):
            self.traj_points[i].append((self.objects[i].x+self.objects[i].width/2, self.objects[i].y+self.objects[i].height/2))
        for i in range(len(self.traj_points)):
            for j in self.traj_points[i]:
                pg.draw.circle(self.screen, (255, 255, 255), j, 1)
            
    def UI(self):
        pg.font.init()
        for i, j in enumerate(self.menu_buttons):
            text = j[1].render(j[0], True, j[3])
            rect = text.get_rect(midleft=j[2])
            if rect.collidepoint(self.mouse_pos) and self.click:
                self.button(i)
            if self.allow_dragging == False and i == 1:
                pg.draw.line(self.screen, j[3], rect.bottomleft, rect.topright)
            if self.show_forces == False and i == 2:
                pg.draw.line(self.screen, j[3], rect.bottomleft, rect.topright)
            pg.draw.rect(self.screen, j[3], rect, 1, 3)
            self.screen.blit(text, rect)
           
        if self.l_panel[0] != None:
            pg.draw.rect(self.screen, (100, 100, 100), pg.Rect(0+self.l_p_offset, self.HEIGHT/2-100, 200, 200), border_top_right_radius=10, border_bottom_right_radius=10)
            pg.draw.rect(self.screen, (50, 50, 50), pg.Rect(200+self.l_p_offset, self.HEIGHT/2-50, 50, 100), border_top_right_radius=5, border_bottom_right_radius=5)    
        if self.l_panel[0] == True:
            pg.draw.polygon(self.screen, (0, 0, 0), [(245, self.HEIGHT/2-45), (205, self.HEIGHT/2), (245, self.HEIGHT/2+45)])
            if pg.Rect(200+self.l_p_offset, self.HEIGHT/2-50, 50, 100).collidepoint(self.mouse_pos) and self.click:
                self.l_panel[0] = None 
                self.i = 0
        elif self.l_panel[0] == False:
            pg.draw.polygon(self.screen, (0, 0, 0), [(5, self.HEIGHT/2-45), (45, self.HEIGHT/2), (5, self.HEIGHT/2+45)])
            if pg.Rect(200+self.l_p_offset, self.HEIGHT/2-50, 50, 100).collidepoint(self.mouse_pos) and self.click:
                self.l_panel[0] = None
                self.i = -200
        else:
            if self.l_p_offset == -200:
                if self.i < 0:
                    pg.draw.rect(self.screen, (100, 100, 100), pg.Rect(0+self.i, self.HEIGHT/2-100, 200, 200), border_top_right_radius=10, border_bottom_right_radius=10)
                    pg.draw.rect(self.screen, (50, 50, 50), pg.Rect(200+self.i, self.HEIGHT/2-50, 50, 100), border_top_right_radius=5, border_bottom_right_radius=5)
                    pg.draw.polygon(self.screen, (0, 0, 0), [(45+self.i, self.HEIGHT/2-45), (5+self.i, self.HEIGHT/2), (45+self.i, self.HEIGHT/2+45)])
                    self.i += 200/0.2/1/self.FPS #200 truc parce qu'on veut 0.2s d'anim 
                else:
                    self.l_p_offset = 0
                    self.l_panel[0] = True
            else:
                if self.i > -200:
                    pg.draw.rect(self.screen, (100, 100, 100), pg.Rect(0+self.i, self.HEIGHT/2-100, 200, 200), border_top_right_radius=10, border_bottom_right_radius=10)
                    pg.draw.rect(self.screen, (50, 50, 50), pg.Rect(200+self.i, self.HEIGHT/2-50, 50, 100), border_top_right_radius=5, border_bottom_right_radius=5)
                    pg.draw.polygon(self.screen, (0, 0, 0), [(45+self.i, self.HEIGHT/2-45), (5+self.i, self.HEIGHT/2), (45+self.i, self.HEIGHT/2+45)])
                    self.i -= 200/0.3/1/self.FPS
                else:
                    self.l_p_offset = -200
                    self.l_panel[0] = False
            
        if self.l_panel[0]:
            width_sum = 5
            height_sum = self.HEIGHT/2-100+18/2+5
            for i, j in enumerate(self.buttons_0):
                text = j[1].render(j[0], True, j[2])
                if width_sum+text.get_rect().width > 200: height_sum += text.get_rect().height+5
                rect = text.get_rect(midleft=(width_sum, height_sum))
                width_sum += rect.width+5
                pg.draw.rect(self.screen, j[2], rect, 1, 2)
                self.screen.blit(text, rect)

            
    def dragging(self, index):
        self.drag_index = index
        while self.click:
            pos_0 = (self.objects[index].x+self.objects[index].width/2, self.objects[index].y+self.objects[index].height/2)
            pg.draw.line(self.screen, (50, 50, 50), pos_0, self.mouse_pos)
            pg.draw.line(self.screen, (50, 50, 50), pos_0, (self.mouse_pos[0], pos_0[1]))
            pg.draw.line(self.screen, (50, 50, 50), pos_0, (pos_0[0], self.mouse_pos[1]))
            text0 = self.font.render(str(round(-pos_0[0]+self.mouse_pos[0], 1))+ '  N', True, (200, 200, 200), (0, 0, 0))
            text1 = self.font.render(str(round(-pos_0[1]+self.mouse_pos[1], 1))+ '  N', True, (200, 200, 200), (0, 0, 0))
            self.screen.blit(text0, text0.get_rect(center=((pos_0[0]+self.mouse_pos[0])/2, pos_0[1])))
            self.screen.blit(text1, text1.get_rect(center=(pos_0[0], (pos_0[1]+self.mouse_pos[1])/2)))
                             
        self.objects[index].f_x.append(-pos_0[0]+self.mouse_pos[0])
        self.objects[index].f_y.append(-pos_0[1]+self.mouse_pos[1])
        self.drag_index = -1
        
    def drag(self):
        if self.click:
            for i, j in enumerate(self.objects):
                if j.rect.collidepoint(self.mouse_pos) and i!=self.drag_index:
                    self.threads.append(thrd.Thread(target=self.dragging, args=(i, )))
                    self.threads[len(self.threads)-1].start()
                    return None
    def __run__(self):
        self.screen = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()
        self.Window = Window()

        self.running = True
        while self.running:
            self.mouse_pos = pg.mouse.get_pos()
            self.keys = pg.key.get_pressed()
            self.screen.fill(self.background_color)
            pg.draw.rect(self.screen, (50, 50, 50), pg.Rect(0, 0, self.WIDTH, 80))
            
            if self.keys[pg.K_SPACE]:
                self.time_scale = (self.time_scale[0], 0) if self.time_scale[1] else (self.time_scale[0], 1)
                time.sleep(0.2)
                
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    pg.quit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.click = True
                if event.type == pg.MOUSEBUTTONUP:
                    self.click = False
            
            self.UI()
            self.render()
            if self.trajectory: self.calc_traj()
            if self.time_scale[1] != 0:
                if self.allow_dragging:
                    self.drag()
        
            pg.display.set_caption(' Py-Physics Simulator  |  ' + str(round(self.clock.get_fps(), 1)))
            pg.display.flip()
            self.clock.tick(self.FPS)
            
            
if __name__ == '__main__':
    app = App()
    app.__run__()