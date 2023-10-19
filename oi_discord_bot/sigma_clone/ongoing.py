"""
Apex Sigma: The Database Giant Discord Bot.
Copyright (C) 2019  Lucia's Cipher

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

ongoing_storage = {}


class Ongoing(object):
    @staticmethod
    def get_ongoing(key):
        """
        :type key: str
        :rtype: list
        """
        return ongoing_storage.get(key) or []

    @staticmethod
    def set_ongoing(key, identifier):
        """
        :type key: str
        :type identifier: str or int
        """
        ongoing_list = Ongoing.get_ongoing(key) or []
        ongoing_list.append(identifier)
        ongoing_storage.update({key: ongoing_list})

    @staticmethod
    def del_ongoing(key, identifier):
        """
        :type key: str
        :type identifier: str or int
        """
        ongoing_list = Ongoing.get_ongoing(key)
        if identifier in ongoing_list:
            ongoing_list.remove(identifier)
        ongoing_storage.update({key: ongoing_list})

    @staticmethod
    def is_ongoing(key, identifier):
        """
        :type key: str
        :type identifier: str or int
        :rtype: bool
        """
        return identifier in Ongoing.get_ongoing(key)

    @staticmethod
    def reset_ongoing(identifier):
        """
        :type identifier: str or int
        :rtype: bool
        """
        for key in ongoing_storage:
            ongoing_list = Ongoing.get_ongoing(key)
            if identifier in ongoing_list:
                ongoing_list.remove(identifier)
            ongoing_storage.update({key: ongoing_list})
