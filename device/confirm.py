#!/usr/bin/python
"""
Run a confirmation screen in a separate process.
"""

import multiprocessing
import sys
import os
import time
import inspect
import colorsys

try:
    import pygame
    from pygame.locals import *
    from evdev import InputDevice, list_devices
except ImportError:
    print "Warning: Pygame and similar imports ignored."


class ConfirmScreenController(object):
    """
    Handle for the confirmation screen.

    Methods can be called on this class from the main thread.
    
    Unrecognized methods will be safely proxied to the graphics thread.
    """
    def __init__(self, fullscreen=False):
        self.started = False
        self.comm = None
        # Only fullscreen if running on a pi.
        self.fullscreen = is_rpi()

    def start(self):
        """Launch the confirm screen."""
        assert not self.started
        self.started = True

        comm1, comm2 = multiprocessing.Pipe()
        self.comm = comm1
        self.csp = ConfirmScreenProcess(comm2, fullscreen=self.fullscreen)
        self.csp.start()

    def yn_prompt(self, text):
        """Present a yes no prompt and get the result.
        Blocks until a response is clicked.

        Args:
            text: Prompt to use.
        Returns:
            Boolean of the user's response.
        """
        self.set_prompt(text)
        return self.comm.recv()

    def __getattr__(self, key):
        """
        Forward calls to the screen proces.
        Return values are lost.
        This was a bad idea. Very confusing.
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

        self.p_prompt_on = False
        self.p_prompt_text = "no prompt text"

    def set_prompt(self, text):
        self.p_prompt_on = True
        self.p_prompt_text = text

    def prompt_response(self, whether):
        self.p_prompt_on = False
        self.p_prompt_text = "no prompt text"
        self.comm.send(whether)

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
        if is_rpi():
            pygame.mouse.set_visible(False)

        # set up the window
        flags = 0
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        self.screen = pygame.display.set_mode((480, 320), flags, 32)
        pygame.display.set_caption('Drawing')

        # set up the colors
        BLACK = self.map_color( (  0,   0,   0) )
        WHITE = self.map_color( (255, 255, 255) )
        RED   = self.map_color( (255,   0,   0) )
        GREEN = self.map_color( (  0, 255,   0) )
        BLUE  = self.map_color( (  0,   0, 255) )
        CYAN  = self.map_color( (  0, 255, 255) )
        MAGENTA = self.map_color( (255,   0, 255) )
        YELLOW = self.map_color( (255, 255,   0) )
        SOOTHBLUE = self.map_color( (0, 56, 87) )

        # run the game loop
        while self.running:

            ###### frame draw
            # Fill background
            background = pygame.Surface(self.screen.get_size())
            background = background.convert()
            background.fill(SOOTHBLUE)

            font = pygame.font.Font(None, 48)

            if self.p_prompt_on:
                # for index, line in enumerate(split_every(self.p_prompt_text, 30)):
                VERT_SPACE = 40
                for index, line in enumerate(self.p_prompt_text.split("\n")):
                    prompttext = font.render(line, 1, WHITE)
                    prompttextpos = prompttext.get_rect(centerx=background.get_width()/2,
                                                        centery=background.get_height()/2 - 80 + VERT_SPACE*index)
                    background.blit(prompttext, prompttextpos)

                yestext = font.render("Allow", 1, WHITE)
                yestextpos = yestext.get_rect(centerx=background.get_width()/2 - 60,
                                              centery=background.get_height()/2 + 80)
                background.blit(yestext, yestextpos)

                notext = font.render("Deny", 1, WHITE)
                notextpos = notext.get_rect(centerx=background.get_width()/2 + 60,
                                            centery=background.get_height()/2 + 80)
                background.blit(notext, notextpos)
            else:
                # Display some text
                text = font.render("Locked", 1, WHITE)
                textpos = text.get_rect(centerx=background.get_width()/2,
                                        centery=background.get_height()/2)
                background.blit(text, textpos)

            self.screen.blit(background, (0, 0))
            pygame.display.flip()
            ###### end frame draw

            self._check_message()
            if not self.running:
                return
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    self.running = False  
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print("touch pos: %sx%s\n" % pygame.mouse.get_pos())
                    if self.p_prompt_on:
                        if notextpos.collidepoint(pygame.mouse.get_pos()):
                            self.prompt_response(False)
                        elif yestextpos.collidepoint(pygame.mouse.get_pos()):
                            self.prompt_response(True)
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.running = False
            pygame.display.update()

    def map_color(self, color):
        """Map a color. Our raspberry pi display shows negative."""
        if not is_rpi():
            return color
        else:
            (r,g,b) = color
            return (255 - r, 255 - g, 255 - b)


class DummyConfirmScreenController(object):
    def yn_prompt(self, text):
        return True

    def shutdown(self):
        pass


def is_rpi():
    """Test if this code is running on a raspberry pi."""
    try:
        import RPi
        return True
    except ImportError:
        return False

def split_every(text, n):
    return [text[i:i+n] for i in range(0, len(text), n)]

if __name__ == "__main__":
    fullscreen = is_rpi()
    csc = ConfirmScreenController()
    csc.start()
    time.sleep(3)
    csc.shutdown()
