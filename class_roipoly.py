"""
Draw polygon regions of interest (ROIs) in matplotlib images,
similar to Matlab's roipoly function.
https://github.com/jdoepfert/roipoly.py
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import image as mpimg
from matplotlib.path import Path as MplPath
from matplotlib.widgets import Button
from matplotlib.figure import Figure


class RoiPoly:

    def __init__(self, fig=None, ax=None, color='b',
                 show_fig=True, close_fig=True):
        """
        fig: matplotlib figure
            Figure on which to create the ROI
        ax: matplotlib axes
            Axes on which to draw the ROI
        color: str
           Color of the ROI
        roicolor: str
            deprecated, use `color` instead
        show_fig: bool
            Display the figure upon initializing a RoiPoly object
        close_fig: bool
            Close the figure after finishing ROI drawing
        """

        self.start_point = []
        self.end_point = []
        self.previous_point = []
        self.x = []
        self.y = []
        self.line = None
        self.completed = False  # Has ROI drawing completed?
        self.color = color
        self.fig = fig
        self.ax = ax
        self.close_figure = close_fig

        # Mouse event callbacks
        self.__cid1 = self.fig.canvas.mpl_connect('motion_notify_event', self.__motion_notify_callback)
        self.__cid2 = self.fig.canvas.mpl_connect('button_press_event', self.__button_press_callback)

        if show_fig:
            self.show_figure()

    @staticmethod
    def show_figure():
        if sys.flags.interactive:
            plt.show(block=False)
        else:
            plt.show(block=True)

    def get_mask(self, current_image):
        if self.completed:
            ny = np.shape(current_image)[0]
            nx = np.shape(current_image)[1]
            poly_verts = ([(self.x[0], self.y[0])] + list(zip(reversed(self.x), reversed(self.y))))
            x, y = np.meshgrid(np.arange(nx), np.arange(ny))
            x, y = x.flatten(), y.flatten()
            points = np.vstack((x, y)).T

            roi_path = MplPath(poly_verts)
            grid = roi_path.contains_points(points).reshape((ny, nx))
            return (grid)

    def display_roi(self, **linekwargs):
        line = plt.Line2D(self.x + [self.x[0]], self.y + [self.y[0]],
                          color=self.color, **linekwargs)
        ax = plt.gca()
        ax.add_line(line)
        plt.draw()

    def get_mean_and_std(self, current_image):
        mask = self.get_mask(current_image)
        mean = np.mean(np.extract(mask, current_image))
        std = np.std(np.extract(mask, current_image))
        return mean, std

    def display_mean(self, current_image, **textkwargs):
        mean, std = self.get_mean_and_std(current_image)
        string = "%.3f +- %.3f" % (mean, std)
        plt.text(self.x[0], self.y[0],
                 string, color=self.color,
                 bbox=dict(facecolor='w', alpha=0.6), **textkwargs)

    def __motion_notify_callback(self, event):
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            if ((event.button is None or event.button == 1) and self.line is not None):
                # Move line around
                x_data = [self.previous_point[0], x]
                y_data = [self.previous_point[1], y]
                #print("draw line x: {} y: {}".format(x_data, y_data))
                self.line.set_data(x_data, y_data)
                self.fig.canvas.draw()

    def __button_press_callback(self, event):
        #print('pressed callback')
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            ax = event.inaxes
            if event.button == 1 and not event.dblclick:
                print("Received single left mouse button click")
                if self.line is None:  # If there is no line, create a line
                    self.line = plt.Line2D([x, x], [y, y], marker='.', color=self.color)
                    self.start_point = [x, y]
                    self.previous_point = self.start_point
                    self.x = [x]
                    self.y = [y]

                    ax.add_line(self.line)
                    self.fig.canvas.draw()
                else:  # If there is a line, create a segment
                    x_data = [self.previous_point[0], x]
                    y_data = [self.previous_point[1], y]
                    print("draw line x: {} y: {}".format(x_data, y_data))
                    self.line = plt.Line2D(x_data, y_data, marker='.', color=self.color)
                    self.previous_point = [x, y]
                    self.x.append(x)
                    self.y.append(y)

                    event.inaxes.add_line(self.line)
                    self.fig.canvas.draw()

            elif (((event.button == 1 and event.dblclick) or (event.button == 3 and not event.dblclick)) and self.line is not None):
                # Close the loop and disconnect
                print("Closing shape")
                self.fig.canvas.mpl_disconnect(self.__cid1)
                self.fig.canvas.mpl_disconnect(self.__cid2)

                self.line.set_data([self.previous_point[0], self.start_point[0]], [self.previous_point[1], self.start_point[1]])
                ax.add_line(self.line)
                self.fig.canvas.draw()
                self.line = None
                self.completed = True



def main(img):

    img = plt.imread(img)
    fig, ax = plt.subplots()
    plt.tight_layout()
    plt.title('Left click: new line segment - Right click: close region')
    ax.axis('off')
    plt.ioff()

    def cancel_callback(event):
        plt.close()
        global ok
        ok = False
    def clear_callback(event):
        plt.sca(ax)
        plt.cla()
        ax.axis('off')
        ax.imshow(img, cmap=plt.cm.gray, interpolation = 'kaiser')
        global roi
        roi = RoiPoly(fig=fig, ax=ax, color='r', show_fig=False)
        global ok
    def done_callback(event):
        plt.close()
        global ok
        if roi.completed: ok = True
        else: ok = False

    axButton1 = plt.axes([0.05, 0.03, 0.3, 0.04])
    button1 = Button(axButton1, 'Cancel', color='0.95', hovercolor='#636363')
    button1.on_clicked(cancel_callback)
    axButton2 = plt.axes([0.36, 0.03, 0.3, 0.04])
    button2 = Button(axButton2, 'Clear', color='0.95', hovercolor='#636363')
    button2.on_clicked(clear_callback)
    axButton3 = plt.axes([0.67, 0.03, 0.3, 0.04])
    button3 = Button(axButton3, 'Done', color='0.95', hovercolor='#636363')
    button3.on_clicked(done_callback)
    ax.imshow(img, cmap=plt.cm.gray, interpolation = 'kaiser')
    roi = RoiPoly(fig=fig, ax=ax, color='r', show_fig=False)
    plt.show()

    try:
        if ok:
            #plt.imshow(roi.get_mask(img))
            #plt.show()
            mpimg.imsave("selection.png", roi.get_mask(img), cmap=plt.cm.gray)
    except:
        print('Not ok')



if __name__=='__main__':
    if os.path.exists('tmp.png'):
        main('tmp.png')
        os.remove("tmp.png")
    else:
        main('template.png')
