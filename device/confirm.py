#!/usr/bin/python
"""
Run a confirmation screen in a separate process.
"""

import multiprocessing
import sys
import os
import time
import inspect

import pygame
from pygame.locals import *
from evdev import InputDevice, list_devices


class ConfirmScreenController(object):
    def __init__(self, fullscreen=False):
        self.started = False
        self.comm = None
        self.fullscreen = fullscreen

    def start(self):
        """Launch the confirm screen."""
        assert not self.started
        self.started = True

        comm1, comm2 = multiprocessing.Pipe()
        self.comm = comm1
        self.csp = ConfirmScreenProcess(comm2, fullscreen=self.fullscreen)
        self.csp.start()

    def set_prompt(self, text):
        pass

    def __getattr__(self, key):
        """
        Forward calls to the screen proces.
        Return values are lost.
        """
        # Make sure it's a declared method on the process
        try:
            method = getattr(ConfirmScreenProcess, key)
            if not inspect.ismethod(method):
                raise AttributeError(key)
        except AttributeError as e:
            raise AttributeError("'{}' has no attribute '{}'".format(self.__class__.__name__, key))

        def wrapped_rpc(*args, **kwargs):
            self.comm.send({
                "method": key,
                "args": args,
                "kwargs": kwargs,
            })
        return wrapped_rpc


class ConfirmScreenProcess(multiprocessing.Process):
    """
    Confirm screen process.
    
    Runs in a separate process.
    Don't call methods on this directly after it has forked.
    Instead communicate through comm to issue call requests.
    """
    def __init__(self, comm, fullscreen=False):
        multiprocessing.Process.__init__(self)
        self.fullscreen = fullscreen
        self.running = False
        self.comm = comm

    def shutdown(self):
        self.running = False

    def _check_message(self):
        if self.comm.poll():
            call = self.comm.recv()
            method = getattr(self, call["method"])
            method(*call["args"], **call["kwargs"])

    def run(self):
        self.running = True

        devices = map(InputDevice, list_devices())
        eventX=""
        for dev in devices:
            if dev.name == "ADS7846 Touchscreen":
                eventX = dev.fn
        print eventX

        os.environ["DISPLAY"] = ":0"
        os.environ["SDL_FBDEV"] = "/dev/fb0"
        os.environ["SDL_MOUSEDRV"] = "TSLIB"
        os.environ["SDL_MOUSEDEV"] = eventX

        pygame.init()

        # set up the window
        flags = 0
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        screen = pygame.display.set_mode((320, 240), flags, 32)
        pygame.display.set_caption('Drawing')

        # set up the colors
        BLACK = (  0,   0,   0)
        WHITE = (255, 255, 255)
        RED   = (255,   0,   0)
        GREEN = (  0, 255,   0)
        BLUE  = (  0,   0, 255)
        CYAN  = (  0, 255, 255)
        MAGENTA=(255,   0, 255)
        YELLOW =(255, 255,   0)
        SOOTHBLUE = (0, 56, 87)

        # Fill background
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill(SOOTHBLUE)

        # Display some text
        font = pygame.font.Font(None, 36)
        text = font.render("Locked", 1, WHITE)
        textpos = text.get_rect(centerx=background.get_width()/2, centery=background.get_height()/2)
        background.blit(text, textpos)

        screen.blit(background, (0, 0))
        pygame.display.flip()

        running = True
        # run the game loop
        while running:
            self._check_message()
            if not self.running:
                return
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    running = False  
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print("Pos: %sx%s\n" % pygame.mouse.get_pos())
                    if textpos.collidepoint(pygame.mouse.get_pos()):
                        pygame.quit()
                        sys.exit()
                        running = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    running = False
            pygame.display.update()


def is_rpi():
    """Test if this code is running on a raspberry pi."""
    try:
        import RPi
        return True
    except ImportError:
        return False

if __name__ == "__main__":
    fullscreen = is_rpi()
    csc = ConfirmScreenController(fullscreen=True)
    csc.start()
    time.sleep(3)
    csc.shutdown()
