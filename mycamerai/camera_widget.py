__all__ = "CameraOpenCV"

import os

import cv2
import numpy as np

from kivy.app import App
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.logger import Logger
from kivy_garden.xcamera import XCamera
from kivy.core.window import Window


class CameraOpenCV(XCamera):
    faces = []
    faces_detection_active = True
    directory = "/storage/emulated/0/DCIM/"

    def on_camera_ready(self):
        Logger.debug("on_camera_ready %s " % str(self.center))
        if self._camera is not None:
            self._camera.bind(on_texture=self._on_texture)

    def _on_texture(self, instance):
        # TODO : find a better check for this
        if App.get_running_app().manager.current == "Capture":
            height, width = self.texture.height, self.texture.width
            img = np.frombuffer(self.texture.pixels, np.uint8)
            img = img.reshape(height, width, 4)
            img = np.flipud(img)
            factor = Window.height / self.resolution[1]
            img = cv2.resize(img, None, fx=factor, fy=factor)
            if self.faces_detection_active:
                # Logger.debug("avant detection visage")
                detected_faces = App.get_running_app().face_detector.detect_faces(img)
                for c in self.faces:
                    self.canvas.remove(c)
                self.faces = []
                for (x, y, w, h) in detected_faces:
                    Logger.debug("visage détécté %s, %s => %s %s" % (x, y, w, h))
                    with self.canvas:
                        Color(1, 0, 0, 0.8, mode="rgba")
                        # TODO: remove this magic numbers
                        r = Rectangle(size=(h, w), pos=(x + 200, y + 75))
                        self.faces.append(r)

    def picture_taken(self, obj, filename):
        Logger.debug("_on_picture_taken %s => %s" % (obj, filename))
        App.get_running_app().manager.switch_to("Editor")
        App.get_running_app().manager.current_screen.source = os.path.join(self.directory, filename)

    def switch_face_detection(self, *args):
        self.faces_detection_active = not self.faces_detection_active
        Logger.debug("switch_face_detection %s" % self.faces_detection_active)
        args[0].text_color = (1, 1, 0, 1) if self.faces_detection_active else (0, 0, 1, 1)
