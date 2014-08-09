"""
Created on 22-04-2013

@author: citan
"""

import pygame
from pimonitor.cu.PMCUParameter import PMCUParameter


class PMSingleWindow(object):
    """
    classdocs
    """

    def __init__(self, parameter):
        self._fg_color = pygame.Color(230, 166, 0)
        self._fg_color_dim = pygame.Color(200, 140, 0)
        self._bg_color = pygame.Color(0, 0, 0)
        self._parameters = [parameter]
        self._packets = None

        self._x_offset = 0
        self._sum_value = 0.0
        self._readings = 0

    def set_surface(self, surface):
        if surface is None:
            return

        parameter = self._parameters[0]

        self._surface = surface
        self._width = self._surface.get_width()
        self._height = self._surface.get_height()

        self._title_font_size = int(self._surface.get_height() / 12)
        self._value_font_size = int(self._surface.get_height() / 1.8)
        self._unit_font_size = int(self._surface.get_height() / 4)

        self._title_font = pygame.font.SysFont(pygame.font.get_default_font(), self._title_font_size)
        self._value_font = pygame.font.SysFont(pygame.font.get_default_font(), self._value_font_size)
        self._unit_font = pygame.font.SysFont(pygame.font.get_default_font(), self._unit_font_size)

        self._font_aa = 1

        self._title_lbl = self._title_font.render(parameter.get_name(), self._font_aa, self._fg_color)

        self._unit_lbl = self._unit_font.render(parameter.get_default_unit(), self._font_aa, self._fg_color_dim)
        self._end_x_offset = self._width - self._unit_lbl.get_width() - 10

    def render(self):
        value = "??"
        parameter = self._parameters[0]
        if self._packets is not None:
            if parameter.get_cu_type() == PMCUParameter.CU_TYPE_CALCULATED_PARAMETER():
                value = parameter.get_calculated_value(self._packets)
            else:
                value = parameter.get_value(self._packets[0])

        try:
            self._sum_value += float(value)
            self._readings += 1
        except:
            pass

        value_lbl_width = self._value_font.render(value, self._font_aa, self._fg_color).get_width()
        self._x_offset = (self._width - value_lbl_width) / 2
        value_lbl = self._value_font.render(value, self._font_aa, self._fg_color)

        avg_value_lbl = None
        if self._readings != 0:
            avg_value_lbl = self._unit_font.render("%.2f" % (self._sum_value / self._readings), self._font_aa, self._fg_color_dim)
            self._surface.blit(avg_value_lbl, (self._x_offset + value_lbl_width/2, 10 + self._title_lbl.get_height() + value_lbl.get_height()))

        self._surface.blit(self._title_lbl, (2, 2))
        self._surface.blit(value_lbl, (self._x_offset, 10 + self._title_font_size))
        if avg_value_lbl == None:
            self._surface.blit(self._unit_lbl, (self._end_x_offset, 10 + self._title_lbl.get_height() + value_lbl.get_height()))
        else:
            self._surface.blit(self._unit_lbl, (self._end_x_offset, 10 + self._title_lbl.get_height() + value_lbl.get_height() + avg_value_lbl.get_height()))


    def set_packets(self, packets):
        self._packets = packets

    def get_parameters(self):
        return self._parameters
