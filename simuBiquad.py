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
from numpy.core.shape_base import stack
import wx
import math

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

class Biquad():
    def __init__(self, biquadType, fc, q, peakGainDB):
        self.a0 = 0
        self.a1 = 0
        self.a2 = 0
        self.b1 = 0
        self.b2 = 0
        self.setBiquad(biquadType, fc, q, peakGainDB)

    def setBiquad(self, biquadType, fc, q, peakGainDB) :
        self.Fc = np.clip(fc, 0, 0.5)
        self.type = biquadType
        self.Q = q
        self.Fc = fc
        self.peakGain = peakGainDB
        self.calcBiquad()

    def calcBiquad(self):
        norm = 0
        V = pow(10, math.fabs(self.peakGain) / 20.0)
        K = math.tan(math.pi * self.Fc)
        if self.type == 0:  #lowpass
            norm = 1 / (1 + K / self.Q + K * K)
            self.a0 = K * K * norm
            self.a1 = 2 * self.a0
            self.a2 = self.a0
            self.b1 = 2 * (K * K - 1) * norm
            self.b2 = (1 - K / self.Q + K * K) * norm

        elif self.type == 1: #highpass:
            norm = 1 / (1 + K / self.Q + K * K)
            self.a0 = 1 * norm
            self.a1 = -2 * self.a0
            self.a2 = self.a0
            self.b1 = 2 * (K * K - 1) * norm
            self.b2 = (1 - K / self.Q + K * K) * norm

        elif self.type == 2: #bandpass:
            norm = 1 / (1 + K / self.Q + K * K)
            self.a0 = K / self.Q * norm
            self.a1 = 0
            self.a2 = -self.a0
            self.b1 = 2 * (K * K - 1) * norm
            self.b2 = (1 - K / self.Q + K * K) * norm

        elif self.type == 3: #notch:
            norm = 1 / (1 + K / self.Q + K * K)
            self.a0 = (1 + K * K) * norm
            self.a1 = 2 * (K * K - 1) * norm
            self.a2 = self.a0
            self.b1 = self.a1
            self.b2 = (1 - K / self.Q + K * K) * norm

        elif self.type == 4: #peak:
            if (self.peakGain >= 0):    # boost
                norm = 1 / (1 + 1/self.Q * K + K * K)
                self.a0 = (1 + V/self.Q * K + K * K) * norm
                self.a1 = 2 * (K * K - 1) * norm
                self.a2 = (1 - V/self.Q * K + K * K) * norm
                self.b1 = self.a1
                self.b2 = (1 - 1/self.Q * K + K * K) * norm
            else:   # cut
                norm = 1 / (1 + V/self.Q * K + K * K)
                self.a0 = (1 + 1/self.Q * K + K * K) * norm
                self.a1 = 2 * (K * K - 1) * norm
                self.a2 = (1 - 1/self.Q * K + K * K) * norm
                self.b1 = self.a1
                self.b2 = (1 - V/self.Q * K + K * K) * norm
        elif self.type == 5: #lowshelf:
            if (self.peakGain >= 0):   # boost
                norm = 1 / (1 + math.sqrt(2) * K + K * K)
                self.a0 = (1 + math.sqrt(2*V) * K + V * K * K) * norm
                self.a1 = 2 * (V * K * K - 1) * norm
                self.a2 = (1 - math.sqrt(2*V) * K + V * K * K) * norm
                self.b1 = 2 * (K * K - 1) * norm
                self.b2 = (1 - math.sqrt(2) * K + K * K) * norm
            else:    # cut
                norm = 1 / (1 + math.sqrt(2*V) * K + V * K * K)
                self.a0 = (1 + math.sqrt(2) * K + K * K) * norm
                self.a1 = 2 * (K * K - 1) * norm
                self.a2 = (1 - math.sqrt(2) * K + K * K) * norm
                self.b1 = 2 * (V * K * K - 1) * norm
                self.b2 = (1 - math.sqrt(2*V) * K + V * K * K) * norm
        elif self.type == 6: #highshelf:
            if (self.peakGain >= 0):   # boost
                norm = 1 / (1 + math.sqrt(2) * K + K * K)
                self.a0 = (V + math.sqrt(2*V) * K + K * K) * norm
                self.a1 = 2 * (K * K - V) * norm
                self.a2 = (V - math.sqrt(2*V) * K + K * K) * norm
                self.b1 = 2 * (K * K - 1) * norm
                self.b2 = (1 - math.sqrt(2) * K + K * K) * norm
            else:    # cut
                norm = 1 / (V + math.sqrt(2*V) * K + K * K)
                self.a0 = (1 + math.sqrt(2) * K + K * K) * norm
                self.a1 = 2 * (K * K - 1) * norm
                self.a2 = (1 - math.sqrt(2) * K + K * K) * norm
                self.b1 = 2 * (K * K - V) * norm
                self.b2 = (V - math.sqrt(2*V) * K + K * K) * norm

class DataGen(object):
    """ A silly class that generates pseudo-random data for
        display in the plot.
    """
    def __init__(self, init=50):
        self.data = self.init = init
        self.z1 = 0
        self.z2 = 0
        self.x1 = 0
        self.x2 = 0

    def reset_series(self, selection):
        if selection == 0:
            #Min value
            samples1 = [0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0] * 5
            samples2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] * 2
            self.samples = samples1 + samples2
            self.timing = np.arange(0.0, len(self.samples), 1)
        elif selection == 1:
            #Max value
            samples1 = [32768] * 140
            samples2 = [0] * 140
            self.samples = samples1 + samples2
            self.timing = np.arange(0.0, len(self.samples), 1)
        elif selection == 2:
            #Sin
            timing1 = np.arange(0.0, 150, 1)
            samples1 = np.sin(timing1 / 10)
            samples2 = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] * 6)
            timing2 = np.arange(len(samples1), len(samples1)+len(samples2), 1)
            self.samples = np.concatenate((samples1, samples2))
            self.timing = np.concatenate((timing1, timing2))
        elif selection == 3:
            self.samples = np.random.randint(1,100,500)
            self.timing = np.arange(0.0, len(self.samples), 1)


        self.average = []
        self.filtered_samples = list(map(self._compute_sample,self.samples))
        for i in range( len(self.samples) ) :
            sum = 0
            nb = 0
            for j in range ( max(0,i-9) , i) :
                sum += self.samples[j]
                nb = nb + 1
            if nb == 0:
                self.average.append( 0 )
            else:
                self.average.append( sum / nb )
        
        print (self.filtered_samples)

    def setUpCoefficient(self, a0, a1, a2, b1, b2):
        self.a0 = a0
        self.a1 = a1
        self.a2 = a2
        self.b1 = b1
        self.b2 = b2
        self.z1 = 0
        self.z2 = 0
        self.x1 = 0
        self.x2 = 0

    def _compute_sample(self,i):
        out = i * self.a0 + self.z1
        self.z1 = i * self.a1 + self.z2 - self.b1 * out
        self.z2 = i * self.a2 - self.b2 * out
        return out

    def _compute_avg(self,i):
        self.avg_sum += i


class ControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a
        manual mode with an associated value.
    """
    def __init__(self, parent, ID, label):
        wx.Panel.__init__(self, parent, ID)
        self.type = 0
        self.sample = 1000
        self.fc = 20
        self.Q = 1
        self.gain = -30

        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        
        #self.radio_auto = wx.RadioButton(self, -1, label="Auto", style=wx.RB_GROUP)
        #self.radio_manual = wx.RadioButton(self, -1, label="Manual")
        type = ['lowpass', 'highpass', 'bandpass', 'notch', 'peak', 'lowshelf', 'highshelf'] 
        self.typeeffect = wx.ComboBox(self, -1,
            size=(70,-1),
            choices = type,
            style=wx.TE_PROCESS_ENTER)        
            
        self.manual_text1 = wx.TextCtrl(self, -1,
            size=(70,-1),
            value=str(self.sample),
            style=wx.TE_PROCESS_ENTER)

        self.manual_text2 = wx.TextCtrl(self, -1,
            size=(70,-1),
            value=str(self.fc),
            style=wx.TE_PROCESS_ENTER)

        self.manual_text3 = wx.TextCtrl(self, -1,
            size=(70,-1),
            value=str(self.Q),
            style=wx.TE_PROCESS_ENTER)

        self.manual_text4 = wx.TextCtrl(self, -1,
            size=(70,-1),
            value=str(self.gain),
            style=wx.TE_PROCESS_ENTER)

        self.Bind(wx.EVT_COMBOBOX, self.on_text_enter_type, self.typeeffect)
        self.Bind(wx.EVT_TEXT, self.on_text_enter_sample, self.manual_text1)
        self.Bind(wx.EVT_TEXT, self.on_text_enter_fc, self.manual_text2)
        self.Bind(wx.EVT_TEXT, self.on_text_enter_Q, self.manual_text3)
        self.Bind(wx.EVT_TEXT, self.on_text_enter_gain, self.manual_text4)

        sizer.Add(wx.StaticText(self,-1,"Type"), 0, wx.ALIGN_CENTER, 5)
        sizer.Add(self.typeeffect, 0, wx.ALIGN_CENTER, 5)
        sizer.Add(wx.StaticText(self,-1,"Freq. sample"), 0, wx.ALIGN_CENTER, 5)
        sizer.Add(self.manual_text1, 0, wx.ALIGN_CENTER, 5)
        sizer.Add(wx.StaticText(self,-1,"Fc"), 0, wx.ALIGN_CENTER, 5)
        sizer.Add(self.manual_text2, 0, wx.ALIGN_CENTER, 5)
        sizer.Add(wx.StaticText(self,-1,"Q"), 0, wx.ALIGN_CENTER, 5)
        sizer.Add(self.manual_text3, 0, wx.ALIGN_CENTER, 5)
        sizer.Add(wx.StaticText(self,-1,"gain"), 0, wx.ALIGN_CENTER, 5)
        sizer.Add(self.manual_text4, 0, wx.ALIGN_CENTER, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def on_text_enter_type(self, event):
        self.type = self.typeeffect.GetSelection()

    def on_text_enter_sample(self, event):
        self.sample = self.manual_text1.GetValue()

    def on_text_enter_fc(self, event):
        self.fc = self.manual_text2.GetValue()

    def on_text_enter_Q(self, event):
        self.Q = self.manual_text3.GetValue()

    def on_text_enter_gain(self, event):
        self.gain = self.manual_text4.GetValue()  

    def value_type(self):
        return self.type

    def value_sample(self):
        return self.sample
    
    def value_fc(self):
        return self.fc

    def value_Q(self):
        return self.Q

    def value_gain(self):
        return self.gain


class GraphFrame(wx.Frame):
    """ The main frame of the application
    """
    title = 'Biquad Filter Response Simulator'

    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        self.datagen = DataGen()
        self.filter = Biquad(0, 20.0 / 1000.0, 1, 0)

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


        self.xmin_control = ControlBox(self.panel, -1, "Biquad Setting")
        
        samples_name = ['min', 'max', 'sin', 'random'] 
        self.typesample = wx.ComboBox(self.panel, -1,
            size=(70,-1),
            choices = samples_name,
            style=wx.TE_PROCESS_ENTER)   


        self.compute_button = wx.Button(self.panel, -1, "Compute")
        self.Bind(wx.EVT_BUTTON, self.on_compute_button, self.compute_button)

        self.axes.grid(True, color='gray')

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add( self.typesample, border =10, flag=wx.ALL)
        self.hbox1.Add(self.compute_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=10, flag=wx.ALL)

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
        self.plot_data3 = self.axes.plot([], linewidth=1, color=(0.8, 0.8, 0),)[0]

    def draw_plot(self):
        """ Redraws the plot
        """
        xmin = round(min(self.datagen.timing), 0) - 1
        xmax = round(max(self.datagen.timing), 0) + 1
        ymin = round(min(self.datagen.samples), 0) - 0.2
        ymax = round(max(self.datagen.samples), 0) * 1.1
        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)

        self.plot_data2.set_xdata(self.datagen.timing)
        self.plot_data2.set_ydata(self.datagen.samples)
        self.plot_data.set_xdata(self.datagen.timing)
        self.plot_data.set_ydata(self.datagen.filtered_samples)
        self.plot_data3.set_xdata(self.datagen.timing)
        self.plot_data3.set_ydata(self.datagen.average)
        self.canvas.draw()

    def on_compute_button(self, event):
        #todo implement the filter computing here on sample
        type = float(self.xmin_control.value_type())
        sample = float(self.xmin_control.value_sample())
        fc = float(self.xmin_control.value_fc())
        Q = float(self.xmin_control.value_Q())
        gain = float(self.xmin_control.value_gain())

        self.filter.setBiquad(type, fc / sample, Q, gain)

        self.datagen.setUpCoefficient(self.filter.a0, self.filter.a1, self.filter.a2, self.filter.b1, self.filter.b2)
        selection = self.typesample.GetSelection()
        self.datagen.reset_series(selection)
        self.draw_plot()
        print("a0:" + str(self.filter.a0) + " a1:" + str(self.filter.a1) + " a2:" + str(self.filter.a2) + 
            " b1:" + str(self.filter.b1) + " b2:" + str(self.filter.b2))

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