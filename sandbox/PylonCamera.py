'''
Minimal Kivy program to demo PylonCamera Class
'''

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, NumericProperty

# Video Related
from kivy.graphics.texture import Texture
import cv2
from pypylon import pylon



class PylonCamera(Image):
    record = ObjectProperty(None)
    record = False

    def __init__(self, **kwargs):
        super(PylonCamera,self).__init__(**kwargs)
        self.camera = False;
        self.play = True;
        self.connect()
        self.start()


    def connect(self):
        try:
            # Create an instant camera object with the camera device found first.
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            self.camera.Open()
            self.camera.Width.SetValue(self.camera.Width.Max)
            self.camera.Height.SetValue(self.camera.Height.Max)
            self.camera.GainAuto.SetValue('Off')
            self.camera.ExposureAuto.SetValue('Off')
            # Grabbing Continusely (video) with minimal delay
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            print("LumaViewPro compatible camera or scope is now connected.")
            print("Error: PylonCamera.connect()")

        except:
            if self.camera == False:
                print("It looks like a LumaViewPro compatible camera or scope is not connected.")
                print("Error: PylonCamera.connect() exception")
            self.camera = False

    def start(self):
        self.fps = 10
        self.frame_event = Clock.schedule_interval(self.update, 1.0 / self.fps)

    def stop(self):
        if self.frame_event:
            Clock.unschedule(self.frame_event)

    def update(self, dt):
        if self.camera == False:
            self.connect()
            if self.camera == False:
                self.source = "./data/camera to USB.png"
                return
        try:
            if self.camera.IsGrabbing():
                grabResult = self.camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)

                if grabResult.GrabSucceeded():
                    image = grabResult.GetArray()
                    image = cv2.flip(image, 1)
                    self.array = image
                    image_texture = Texture.create(size=(image.shape[1],image.shape[0]), colorfmt='luminance')
                    image_texture.blit_buffer(image.flatten(), colorfmt='luminance', bufferfmt='ubyte')                    # display image from the texture
                    self.texture = image_texture

                self.lastGrab = pylon.PylonImage()
                self.lastGrab.AttachGrabResultBuffer(grabResult)

                if self.record == True:
                    self.capture(append = 'ms')

                grabResult.Release()

        except:
            if self.camera == False:
                print("A LumaViewPro compatible camera or scope was disconnected.")
                print("Error: PylonCamera.update() exception")
            self.camera = False

    def capture(self, save_folder = './capture/', file_root = 'live_', append = 'ms'):
        if self.camera == False:
            print("A LumaViewPro compatible camera or scope is not connected.")
            print("Error: PylonCamera.capture() self.camera == False")
            return

        if append == 'time':
            append = time.strftime("%Y%m%d_%H%M%S")
        elif append == 'ms':
            append = str(int(round(time.time() * 1000)))
        else:
            append =''

        filename = save_folder + '/' + file_root + append + '.tiff'
        try:
            self.lastGrab.Save(pylon.ImageFileFormat_Tiff, filename)
        except:
            print("Error: Save folder does not exist.")

    def frame_size(self, w, h):
        if self.camera == False:
            print("A LumaViewPro compatible camera or scope is not connected.")
            print("Error: PylonCamera.frame_size() self.camera == False")
            return

        width = int(min(int(w), self.camera.Width.Max)/2)*2
        height = int(min(int(h), self.camera.Height.Max)/2)*2
        offset_x = int((self.camera.Width.Max-width)/4)*2
        offset_y = int((self.camera.Height.Max-height)/4)*2

        self.camera.StopGrabbing()
        self.camera.Width.SetValue(width)
        self.camera.Height.SetValue(height)
        self.camera.OffsetX.SetValue(offset_x)
        self.camera.OffsetY.SetValue(offset_y)
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    def gain(self, gain):
        if self.camera == False:
            print("A LumaViewPro compatible camera or scope is not connected.")
            print("Error: PylonCamera.gain() self.camera == False")
            return

        self.camera.StopGrabbing()
        self.camera.Gain.SetValue(gain)
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    def exposure_t(self, t):
        if self.camera == False:
            print("A LumaViewPro compatible camera or scope is not connected.")
            print("Error: PylonCamera.exposure_t() self.camera == False")
            return

        self.camera.StopGrabbing()
        self.camera.ExposureTime.SetValue(t*1000) # (t*1000) in microseconds; therefore t  in milliseconds
        # # DEBUG:
        # print(camera.ExposureTime.Min)
        # print(camera.ExposureTime.Max)
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)


# -------------------------------------------------------------------------
# RUN LUMAVIEWPRO APP
# -------------------------------------------------------------------------
class Main(BoxLayout):
    pass

class PylonCameraApp(App):
    def build(self):
        return Main()

PylonCameraApp().run()
