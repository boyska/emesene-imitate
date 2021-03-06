# -*- coding: utf-8 -*-
'''A plug-in that "imitates" someone. It will copy nick, message, picture
from that person and auto-update it. Not so useful, but very funny! ;-)
'''

VERSION = '0.2'
import os
#import sys
import time
#import socket

#import emesenelib.common

import Plugin
import status

class MainClass( Plugin.Plugin ):
    '''Main plugin class'''
    def __init__(self, controller, msn):
        '''constructor'''
        Plugin.Plugin.__init__( self, controller, msn )
        self.description = _('Copy nick, PM, image and status from someone and autoupdates')
        self.authors = { 'BoySka' : 'boyska gmail com' }
        self.website = 'http://emesene.org'
        self.displayName = _('Imitate')
        self.name = 'Imitate'


        self.controller = controller
        self.msn = msn

        self.user = None #user we are imitating
        self.saved_status = {}

        self.cb_ids = {} #callback ids

    #Plugin methods

    def start( self ):
        '''start the plugin'''
        #self._set_nick("prova")
        self.controller.Slash.register('imitate', self.slash_imitate,
            _('Imitates someone'))

        self.cb_ids['nick-changed'] = self.connect(
                'nick-changed', self.on_nick_changed)
        self.cb_ids['message-changed'] = self.connect(
                'personal-message-changed', self.on_message_changed)
        self.cb_ids['picture-changed'] = self.connect(
                'display-picture-changed', self.on_picture_changed)
        
        self.enabled = True

    def stop( self ):
        '''stop the plugin'''
        self.controller.Slash.unregister('imitate')
        self.disconnect(self.cb_ids['nick-changed'])
        self.disconnect(self.cb_ids['message-changed'])
        self.disconnect(self.cb_ids['picture-changed'])
        self.enabled = False
    
    def check( self ):
        '''check if the plugin can be enabled'''
        return ( True, 'Ok' )

    #Callbacks
    def slash_imitate(self, slash_action):
        '''callback used when /imitate is used'''
        if not self.user:
            self._save_status()


        if slash_action.params == 'stop':
            self.user = None
            self._revert_status()
            return

        if not slash_action.params:
            user = slash_action.conversation.getMembers()[0]
        else:
            user = slash_action.params

        self.user = user

        self._imitate_nick(user)
        self._imitate_message(user)
        self._imitate_status(user)
        self._imitate_picture(user)

    def on_nick_changed(self, msn, user, nick):
        '''callback used when someone changes his nick'''
        if user and user == self.user:
            self._set_nick(nick)

    def on_message_changed(self, msn, user, message):
        '''callback used when someone changes his message'''
        if user and user == self.user:
            time.sleep(1)
            self._set_message(message)

    def on_picture_changed(self,  msn, user, creator, email):
        '''callback used when someone changes his picture'''
        if user and user == self.user:
            time.sleep(1)
            self._imitate_picture(email)


    #Internals
    def _save_status(self):
        '''saves user nick, message and picture in self.saved_status'''
        saved = self.saved_status
        saved['nick'] = self.controller.contacts.get_nick()
        saved['message'] = self.controller.contacts.get_message()
        saved['picture'] = self.controller.avatar.getImagePath()
        #saved['status'] = status.STATUS_TO_MSN[self.controller.contacts.get_status()]
        saved['status'] = self.controller.contacts.get_status() or 'NLN'

    def _revert_status(self):
        '''set nick, message and picture to the ones 
        saved in self.saved_status'''
        saved = self.saved_status
        self._set_nick(saved['nick'])
        self._set_message(saved['message'])
        #self._set_picture(os.path.join(
        #    self.controller.config.getAvatarsCachePath(),
        #    saved['picture']))
        self._set_picture(saved['picture'])
        self._set_status(saved['status'])


    def _imitate_nick(self, user):
        '''imitates the nick of user'''
        nick = self.controller.contacts.get_nick(user)
        self._set_nick(nick)
    
    def _imitate_message(self, user):
        '''imitates the message of user'''
        contact = self.msn.contactManager.getContact(user)
        message = contact.personalMessage
 
        self._set_message(message)

    def _imitate_status(self, user):
        '''imitates the status of user'''
        contact = self.msn.contactManager.getContact(user)
        stat = contact.status
 
        self._set_status(stat)

    def _imitate_picture(self, user):
        '''imitates the message of user'''
        contact = self.msn.contactManager.getContact(user)
        picture = contact.displayPicturePath
        if picture:
            picture_path = os.path.join(
                    self.controller.config.getCachePath(), picture)
            self._set_picture(picture_path)

    def _set_message(self, message):
        '''set our message to message'''
        self.controller.contacts.set_message(message)

    def _set_status(self, status):
        '''set our status to status'''
        self.controller.contacts.set_status(status)

    def _set_picture(self, picture_path):
        '''set our picture to picture_path'''
        self.controller.changeAvatar(picture_path)

    def _set_nick(self, nick):
        '''set our nick to nick'''
        self.controller.contacts.set_nick(nick)

