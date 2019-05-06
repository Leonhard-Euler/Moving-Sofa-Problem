#coding:utf-8
import matplotlib # pip3 install matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches

plt.rcParams["animation.html"] = "jshtml"
plt.rcParams['savefig.pad_inches'] = 0

class VisualHelper:
    def __init__(self, simulator, frames):
        self.animation_duration = 6000  # ms
        self.__simulator = simulator
        self.__corridors = simulator.poly_path + simulator.poly_path[::-1]
        self.__reinit__()
        self.__frames = frames
        self.__index_mult = int(len(self.__corridors) / frames)
        Writer = animation.writers['ffmpeg']
        # Writer = animation.FFMpegWriter(fps=20, metadata=dict(artist='Me'), bitrate=1800)
        self.writer = Writer(fps=30,metadata=dict(artist='Me'),bitrate=18000)

    def __reinit__(self):
        self.__current_x = []
        self.__current_y = []

    def plot(self, polygon):
        x, y = polygon.exterior.xy
        fig, axs = plt.subplots()
        axs.set_aspect(1.0)
        axs.plot(x, y,alpha=1,color='#000000')

    def __difference(self, difference, ax, color):
        x, y = difference.exterior.xy
        ax.fill(x, y,alpha=1,fc=color)

    def __differences(self, A, B, ax, color):
        differences = A.difference(B)
        if differences.geom_type == 'Polygon':
            self.__difference(differences, ax, color)
        else:
            for diff in list(differences):
                self.__difference(diff, ax, color)

    def compare(self, A, B, nameA='A', nameB='B'):
        x, y = A.exterior.xy
        fig, axs = plt.subplots()
        axs.set_aspect(1.0)
        a = axs.plot(x, y,alpha=1,color='black',linewidth=0.7)

        x, y = B.exterior.xy
        b = axs.fill(x, y,alpha=0.15,fc='black',ec='black')

        self.__differences(A, B, axs, 'red')
        self.__differences(B, A, axs, 'blue')

        red = mpatches.Patch(color='red', label='{} only'.format(nameA))
        grey = mpatches.Patch(color='black', alpha=0.15, label='both')
        blue = mpatches.Patch(color='blue', label='{} only'.format(nameB))
        axs.legend(handles=[grey, red, blue], bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand",borderaxespad=0.)
        fig.savefig('{}vs{}.pdf'.format(nameA,nameB), format = 'pdf', dpi = 2000, bbox_inches = 'tight', transparent = False, pad_inches = 0.05)

    def plot_path(self, couch_name=None, num_corridors=60, offset_x=0.75, offset_y=0.5):
        skip_num = int(len(self.__corridors) / num_corridors)
        fig, ax = plt.subplots()
        for idx, corridor in enumerate(self.__corridors):
            if idx % skip_num != 0:  # too much noise if we use every corridor, especially with large N
                continue
            x, y = corridor.exterior.xy
            ax.set_aspect(1.0)
            ax.plot(x, y,color='k',linewidth=0.3)

        self.__plot_couch(ax)
        self.__set_bounds(ax, offset_x, offset_y)

        if couch_name is not None:
            plt.title('({}) Area: {}; N={}'.format(couch_name,self.__simulator.area,self.__simulator.N), loc = 'center')
            fig.savefig('{}.pdf'.format(couch_name), format = 'pdf', dpi = 1200, bbox_inches = 'tight', transparent = False, pad_inches = 0.05)

    def plot_path_demo(self, upto_frame, offset_x=0.75, offset_y=0.5):  # for writeup purpose only
        fig, ax = plt.subplots()
        self.__set_bounds(ax, offset_x, offset_y)
        for idx, corridor in enumerate(self.__corridors):
            if idx % int(len(self.__corridors) / 100) != 0:
                continue
            if idx / 2 > upto_frame:
                break

            x, y = corridor.exterior.xy
            ax.set_aspect(1.0)
            ax.plot(x, y,color='k',linewidth=0.3)
        fig.savefig('couch_demo_{}.pdf'.format(upto_frame), format = 'pdf',
                    dpi = 2000,
                    bbox_inches = 'tight',
                    transparent = False,
                    pad_inches = 0.05)

    def __get_minmax(self, corridors, minmax, coord):  # min max, pointer to min/max, coord 0 - x, 1 - y
        return minmax([minmax(c.vertices["INNER_CENTER"][coord],
                              c.vertices["OUTER_CENTER"][coord]) for c in corridors])

    def __get_bounds(self, offset_x, offset_y):
        corridors = self.__simulator.path.corridors
        x_min = self.__get_minmax(corridors, min, 0)
        x_max = self.__get_minmax(corridors, max, 0)
        y_min = self.__get_minmax(corridors, min, 1)
        y_max = self.__get_minmax(corridors, max, 1)
        return np.array([x_min - offset_x, x_max + offset_x, y_min - 0.15, y_max + offset_y])

    def __set_bounds(self, ax, offset_x, offset_y):
        bounds = self.__get_bounds(offset_x, offset_y)
        ax.set_xlim(bounds[0], bounds[1])
        ax.set_ylim(bounds[2], bounds[3])

    def __update_coords(self, index):
        x, y = self.__corridors[index].exterior.xy
        self.__current_x = self.__current_x + x.tolist()
        self.__current_y = self.__current_y + y.tolist()

    def __animate(self, i, trail):
        if not trail:
            self.__reinit__()
        self.__update_coords(index=i * self.__index_mult)
        self.__anim_corridors.set_data(self.__current_x, self.__current_y)

    def __plot_couch(self, ax, fill=False):
        x, y = self.__simulator.couch.exterior.xy
        ax.plot(x, y, alpha=1,color='#000000')

        if fill:
            ax.fill(x, y,alpha=0.15,fc='grey')

    def animate(self, couch_name=None, trail=False, offset_x=0.75, offset_y=0.5):
        self.__reinit__()
        self.__fig, self.ax = plt.subplots()
        self.ax.set_aspect(1.0)
        self.__set_bounds(self.ax, offset_x, offset_y)
        self.__anim_corridors, = self.ax.plot([], [],color='k',linewidth=0.3 if trail else 1)

        self.__plot_couch(self.ax, fill=(not trail))

        if couch_name is not None:
            plt.title('({}) Area: {}; N={}'.format(couch_name, self.__simulator.area,self.__simulator.N), loc = 'center')
            return matplotlib.animation.FuncAnimation(self.__fig,
                                                      self.__animate,
                                                      frames=self.__frames,
                                                      interval=self.animation_duration / self.__frames,
                                                      fargs=[trail])
