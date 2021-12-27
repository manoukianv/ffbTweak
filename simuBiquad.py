"""
This demo demonstrates how to draw a dynamic mpl (matplotlib)
plot in a wxPython application.
It allows "live" plotting as well as manual zooming to specific
regions.
Both X and Y axes allow "auto" or "manual" settings. For Y, auto
mode sets the scaling of the graph to see all the data points.
For X, auto mode makes the graph "follow" the data. Set it X min
to manual 0 to always see the whole data from the beginning.
Note: press Enter in the 'manual' text box to make a new value
affect the plot.
Vincent Manoukian
License: GPL3
"""
import os
import random
import wx

# The code was updated to work with Python 3.8 and wxPython v4

# The recommended way to use wx with mpl is with the WXAgg
# backend.
#
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab


class DataGen(object):
    """ A silly class that generates pseudo-random data for
        display in the plot.
    """
    def __init__(self, init=50):
        self.data = self.init = init
        self.a0 = 0
        self.a1 = 0
        self.a2 = 0
        self.b1 = 0
        self.b2 = 0
        self.z1 = 0
        self.z2 = 0
        self.x1 = 0
        self.x2 = 0

    def reset_series(self):
        self.samples = [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] * 10
        self.filtered_samples = list(map(self._compute_sample,self.samples))
        print(self.filtered_samples)
        self.timing = np.arange(0.0, len(self.samples), 1)

    def setUpCoefficient(self, a0, a1, a2, b1, b2):
        self.a0 = a0
        self.a1 = a1
        self.a2 = a2
        self.b1 = b1
        self.b2 = b2

    def _compute_sample(self,i):
        out = i * self.a0 + self.z1
        self.z1 = i * self.a1 + self.z2 - self.b1 * out
        self.z2 = i * self.a2 - self.b2 * out
        return out


class ControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a
        manual mode with an associated value.
    """
    def __init__(self, parent, ID, label):
        wx.Panel.__init__(self, parent, ID)
        self.a0 = 0.013806011447721036
        self.a1 = 0.02761202289544207
        self.a2 = 0.013806011447721036
        self.b1 = -1.0730986973124192
        self.b2 = 0.12832274310330333

        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        
        #self.radio_auto = wx.RadioButton(self, -1, label="Auto", style=wx.RB_GROUP)
        #self.radio_manual = wx.RadioButton(self, -1, label="Manual")
        self.manual_text0 = wx.TextCtrl(self, -1,
            size=(70,-1),
            value=str(self.a0),
            style=wx.TE_PROCESS_ENTER)
            
        self.manual_text1 = wx.TextCtrl(self, -1,
            size=(70,-1),
            value=str(self.a1),
            style=wx.TE_PROCESS_ENTER)

        self.manual_text2 = wx.TextCtrl(self, -1,
            size=(70,-1),
            value=str(self.a2),
            style=wx.TE_PROCESS_ENTER)

        self.manual_text3 = wx.TextCtrl(self, -1,
            size=(70,-1),
            value=str(self.b1),
            style=wx.TE_PROCESS_ENTER)

        self.manual_text4 = wx.TextCtrl(self, -1,
            size=(70,-1),
            value=str(self.b2),
            style=wx.TE_PROCESS_ENTER)

        #self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT, self.on_text_enter_a0, self.manual_text0)
        self.Bind(wx.EVT_TEXT, self.on_text_enter_a1, self.manual_text1)
        self.Bind(wx.EVT_TEXT, self.on_text_enter_a2, self.manual_text2)
        self.Bind(wx.EVT_TEXT, self.on_text_enter_b1, self.manual_text3)
        self.Bind(wx.EVT_TEXT, self.on_text_enter_b2, self.manual_text4)
        

        #manual_box = wx.BoxSizer(wx.HORIZONTAL)
        #manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        #manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)

        #sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(self.manual_text0, 0, wx.ALL, 10)
        sizer.Add(self.manual_text1, 0, wx.ALL, 10)
        sizer.Add(self.manual_text2, 0, wx.ALL, 10)
        sizer.Add(self.manual_text3, 0, wx.ALL, 10)
        sizer.Add(self.manual_text4, 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def on_text_enter_a0(self, event):
        self.a0 = self.manual_text0.GetValue()

    def on_text_enter_a1(self, event):
        self.a1 = self.manual_text1.GetValue()

    def on_text_enter_a2(self, event):
        self.a2 = self.manual_text2.GetValue()

    def on_text_enter_b1(self, event):
        self.b1 = self.manual_text3.GetValue()

    def on_text_enter_b2(self, event):
        self.b2 = self.manual_text4.GetValue()  

    def value_a0(self):
        return self.a0

    def value_a1(self):
        return self.a1
    
    def value_a2(self):
        return self.a2

    def value_b1(self):
        return self.b1

    def value_b2(self):
        return self.b2


class GraphFrame(wx.Frame):
    """ The main frame of the application
    """
    title = 'Demo: dynamic matplotlib graph'

    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)

        self.datagen = DataGen()

        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()

    def create_menu(self):
        self.menubar = wx.MenuBar()

        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        self.xmin_control = ControlBox(self.panel, -1, "A1 / A2 / B1 / B2")

        self.compute_button = wx.Button(self.panel, -1, "Compute")
        self.Bind(wx.EVT_BUTTON, self.on_compute_button, self.compute_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_compute_button, self.compute_button)

        #self.cb_grid = wx.CheckBox(self.panel, -1,
        #    "Show Grid",
        #    style=wx.ALIGN_RIGHT)
        #self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        #self.cb_grid.SetValue(True)

        #self.cb_xlab = wx.CheckBox(self.panel, -1,
        #    "Show X labels",
        #    style=wx.ALIGN_RIGHT)
        #self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)
        #self.cb_xlab.SetValue(True)
        self.axes.grid(True, color='gray')

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.compute_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox1.AddSpacer(20)
        #self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox1.AddSpacer(10)
        #self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        #self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        #self.hbox2.AddSpacer(24)
        #self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        #self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((10.0, 4.0), dpi=self.dpi)

        self.axes = self.fig.add_subplot(1,1,1)
        self.axes.set_facecolor('black')
        self.axes.set_title('Filter response', size=12)
        
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        # plot the data as a line series, and save the reference
        # to the plotted line series
        #
        self.plot_data = self.axes.plot([], linewidth=1, color=(0, 1, 1),)[0]
        self.plot_data2 = self.axes.plot([], linewidth=1, color=(0.8, 0, 0),)[0]

    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
        #if self.xmax_control.is_auto():
        #    xmax = len(self.data) if len(self.data) > 50 else 50
        #else:
        #    xmax = int(self.xmax_control.manual_value())

        #if self.xmin_control.is_auto():
        #    xmin = xmax - 50
        #else:


        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        #
        # note that it's easy to change this scheme to the
        # minimal/maximal value in the current display, and not
        # the whole data set.
        #
        #if self.ymin_control.is_auto():
        #    ymin = round(min(self.data), 0) - 1
        #else:
        #    ymin = int(self.ymin_control.manual_value())

        #if self.ymax_control.is_auto():
        #    ymax = round(max(self.data), 0) + 1
        #else:
        #    ymax = int(self.ymax_control.manual_value())

        #self.axes.set_xbound(lower=xmin, upper=xmax)
        #self.axes.set_ybound(lower=ymin, upper=ymax)

        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
        #if self.cb_grid.IsChecked():
        #    self.axes.grid(True, color='gray')
        #else:
        #    self.axes.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly
        # iterate, and setp already handles this.
        #
        #pylab.setp(self.axes.get_xticklabels(),
        #    visible=self.cb_xlab.IsChecked())

        #self.plot_data.set_xdata(np.arange(len(self.data)))
        #self.plot_data.set_ydata(np.array(self.data))

        xmin = round(min(self.datagen.timing), 0) + 1
        xmax = round(max(self.datagen.timing), 0) - 1
        ymin = round(min(self.datagen.samples), 0) - 0.2
        ymax = round(max(self.datagen.samples), 0) * 1.1
        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)

        self.plot_data.set_xdata(self.datagen.timing)
        self.plot_data.set_ydata(self.datagen.filtered_samples)
        self.plot_data2.set_xdata(self.datagen.timing)
        self.plot_data2.set_ydata(self.datagen.samples)
        self.canvas.draw()

    def on_compute_button(self, event):
        #todo implement the filter computing here on sample
        a0 = float(self.xmin_control.value_a0())
        a1 = float(self.xmin_control.value_a1())
        a2 = float(self.xmin_control.value_a2())
        b1 = float(self.xmin_control.value_b1())
        b2 = float(self.xmin_control.value_b2())
        self.datagen.setUpCoefficient(a0, a1, a2, b1, b2)
        self.datagen.reset_series()
        self.draw_plot()
        print("a0:" + str(a0) + " a1:" + str(a1) + " a2:" + str(a2) + " b1:" + str(b1) + " b2:" + str(b2))

    def on_update_compute_button(self, event):
        #update the input label here if required
        i=1

    def on_cb_grid(self, event):
        self.draw_plot()

    def on_cb_xlab(self, event):
        self.draw_plot()

    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"

        dlg = wx.FileDialog(
            self,
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)

    def on_exit(self, event):
        self.Destroy()

    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER,
            self.on_flash_status_off,
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)

    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')


if __name__ == '__main__':
    app = wx.App()
    app.frame = GraphFrame()
    app.frame.Show()
    app.MainLoop()