"""
Created on 22-04-2013

@author: citan
"""

import pygame
from pimonitor.cu.PMCUParameter import PMCUParameter


class PMWindow(object):
    """
    classdocs
    """

    def __init__(self, parameters):
        self._fg_color = pygame.Color(200, 140, 0)
        self._bg_color = pygame.Color(0, 0, 0)
        self._dict = dict()

        self._parameters = parameters
        self._packets = None

        self._reading_no = 0
        self._sum_fuel_consumption = 0.0

    def set_surface(self, surface):

        if surface is None:
            return

        self._surface = surface
        self._width = self._surface.get_width()
        self._height = self._surface.get_height()

        self._title_font_size = int(self._surface.get_height() / 16)
        self._value_font_size = int(self._surface.get_height() / 3.4)
        self._title_font = pygame.font.SysFont(pygame.font.get_default_font(), self._title_font_size)
        self._value_font = pygame.font.SysFont(pygame.font.get_default_font(), self._value_font_size)

        self._font_aa = 1

        self._value_lbl_width = self._value_font.render("999", self._font_aa, self._fg_color).get_width()

    def render(self):

        if self._packets is None:
            return


        first_row_height = self._title_font_size + self._value_font_size + 10
        second_row_height = first_row_height + self._title_font_size + self._value_font_size + 20
        pygame.draw.line(self._surface, self._fg_color, (0, first_row_height + 10),
                         (self._width, first_row_height + 10))

        parameter_number = 0
        for parameter in self._parameters:

            if parameter.get_cu_type() == PMCUParameter.CU_TYPE_CALCULATED_PARAMETER():
                value = parameter.get_calculated_value(self._packets[len(self._parameters)-1:])
                self._reading_no += 1
                self._sum_fuel_consumption += float(value)
            else:
                value = parameter.get_value(self._packets[parameter_number])


            title = parameter.get_name()  # + " (" + param.get_default_unit() + ")"

            first_row_ids = ["E114", "P104", "P122"]
            if parameter.get_id() in first_row_ids:
                index = first_row_ids.index(parameter.get_id())
                x_offset = (self._width / len(first_row_ids)) * index + 2

                titlelbl = self._title_font.render(title, self._font_aa, self._fg_color)
                valuelbl = self._value_font.render(value, self._font_aa, self._fg_color)
                self._surface.blit(titlelbl, (x_offset + 4, 10))
                self._surface.blit(valuelbl, (x_offset + 4, 10 + self._title_font_size))

                pygame.draw.line(self._surface, self._fg_color, (x_offset, 0), (x_offset, first_row_height))

            second_row_ids = ["P203"]

            if parameter.get_id() in second_row_ids:
                index = second_row_ids.index(parameter.get_id())
                x_offset = (self._width / len(second_row_ids)) * index + 2

                titlelbl = self._title_font.render(title, self._font_aa, self._fg_color)
                valuelbl = self._value_font.render(value, self._font_aa, self._fg_color)
                self._surface.blit(titlelbl, (x_offset + 4, first_row_height + 20))
                self._surface.blit(valuelbl, (x_offset + 4, first_row_height + 20 + self._title_font_size))

                pygame.draw.line(self._surface, self._fg_color, (x_offset, first_row_height + 20),
                                 (x_offset, second_row_height))

                index = 1
                x_offset = (self._width / 2) * index + 2

                titlelbl = self._title_font.render("Average Fuel Cons. l/100km", self._font_aa, self._fg_color)
                valuelbl = self._value_font.render(str(self._sum_fuel_consumption/self._reading_no), self._font_aa, self._fg_color)
                self._surface.blit(titlelbl, (x_offset + 4, first_row_height + 20))
                self._surface.blit(valuelbl, (x_offset + 4, first_row_height + 20 + self._title_font_size))

                pygame.draw.line(self._surface, self._fg_color, (x_offset, first_row_height + 20),
                                 (x_offset, second_row_height))

            parameter_number += 1

    def get_parameters(self):
        return self._parameters[:-1] + self._parameters[-1].get_dependencies()

    def set_packets(self, packets):
        self._packets = packets
