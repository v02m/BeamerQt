"""
Beamer QT
Copyright (C) 2024  Jorge Guerrero - acroper@gmail.com

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


import sys
import os



from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, QObject

from core.beamerSlide import *
from gui.contentwidget import *
from gui.Slide import *

import xml.etree.ElementTree as ET


## This need to define a content widget list



class FrameWidget(QtWidgets.QWidget):
    
    BlockSelected = pyqtSignal()
    
    def __init__(self):
        
        super(FrameWidget, self).__init__()
        
        uic.loadUi('gui/FrameWidget.ui', self)
        
        self.CurrentLayout = "layout_standard"
        
        self.FrameXML = ET.Element('Frame', id='frame_0', visible='True')
        
        self.TitleVisibility = True
        
        self.Columns = [ [], [] ]
        
        self.Blocks = []
        
        self.BlocksCache = []
        
        self.SelectedBlock = None
        
        self.Slide = None
        
        self.BeamerSlide = None
        
        self.title_text.setTabChangesFocus(True)
        
        self.refresh_Layout()
        
        
                      
        # self.show()
        
    
    def selectBlock(self):
        for block in self.Blocks:
            block.unSelected()
        
        block = self.sender()
        block.setSelected()
        
        self.SelectedBlock = block
        
        self.BlockSelected.emit()
        
    
    
    def config_title(self, visibility):
        
        self.TitleVisibility = visibility
        if visibility:
            self.frame.show()
        else:
            self.frame.hide()
            
    
    def config_Layout(self, layoutname):
        
        if layoutname != self.CurrentLayout:
            # Perform the changes
            self.CurrentLayout = layoutname
            print(self.CurrentLayout)
            self.refresh_Layout()
            
            
            
    def refresh_rows(self):
        k = 1
        for block in self.Blocks:
            block.ColumnNumber = -1
            self.ElementsGrid.addWidget(block, k , 1)
            k = k+1
            block.show()
    
    def refresh_columns(self):
        for column in range(2):
            k = 1
            for block in self.Columns[column]:
                block.ColumnNumber = k
                self.ElementsGrid.addWidget(block, k , column+1)
                k = k+1
                block.show()
        
    
    def setMinBlocks(self, C):
        for N in range(  len(self.Blocks), C  ):
            nWidget = ContentWidget()
            nWidget.setContentName("Block # " + str(N+1))
            
            nWidget.Selected.connect(self.selectBlock)
            
            self.Blocks.append(nWidget)
            
            
            
        
    
    def refresh_Layout(self):
        # Reconstructs the layout
        
        # Clear the layout
        
        for i in reversed(range(self.ElementsGrid.count())):
            tmpwidget = self.ElementsGrid.itemAt(i)
            self.ElementsGrid.removeItem(tmpwidget)
            tmpwidget.widget().hide()
        
        
        if self.CurrentLayout == "Custom": 
            self.refresh_columns()
        
        
        if self.CurrentLayout == "layout_2rows": 
            # Needs at least 2 Blocks
            self.setMinBlocks(2)
            self.refresh_rows()
  
        if self.CurrentLayout == "layout_standard":
            # Needs at least 1 Block
            self.setMinBlocks(1)
            self.refresh_rows()
                
                
        if self.CurrentLayout == "layout_2cols":
            # Needs at least 2 Blocks
            self.setMinBlocks(2)
                
            # Needs at least 1 element per column
            if len(self.Columns[0]) == 0:
                self.Columns[0].append(self.Blocks[0])
                self.Columns[1].append(self.Blocks[1])
                
            if len(self.Columns[1]) == 0:
                self.Columns[1].append(self.Blocks[-1])
            
            self.refresh_columns()
            
        if self.CurrentLayout == "layout_1col2rows":
            self.setMinBlocks(3)
            
            if len(self.Columns[0]) == 0:
                self.Columns[0].append(self.Blocks[0])
                self.Columns[1].append(self.Blocks[1])
                self.Columns[1].append(self.Blocks[2])
            
            
            
            if len(self.Columns[1]) < 2:
                # redistribute
                self.Columns[0].clear()
                self.Columns[1].clear()
                self.Columns[0].append(self.Blocks[0])
                
                for k in range(1,len(self.Blocks)):
                    self.Columns[1].append(self.Blocks[k])
                
            self.refresh_columns()


        if self.CurrentLayout == "layout_2rows1col":
            self.setMinBlocks(3)
            
            if len(self.Columns[0]) == 0:
                self.Columns[0].append(self.Blocks[0])
                self.Columns[0].append(self.Blocks[1])
                self.Columns[1].append(self.Blocks[2])
            
            
            
            if len(self.Columns[0]) < 2:
                # redistribute
                self.Columns[0].clear()
                self.Columns[1].clear()
                
                for k in range(0,len(self.Blocks)-1):
                    self.Columns[0].append(self.Blocks[k])
                
                self.Columns[1].append(self.Blocks[-1])
                
                
                
            self.refresh_columns()            
            
        if self.CurrentLayout == "layout_4blocks":
            
            print("configuring layout_4blocks ...")
            self.setMinBlocks(4)
            
            if len(self.Columns[0]) == 0:
                self.Columns[0].append(self.Blocks[0])
                self.Columns[0].append(self.Blocks[1])
                self.Columns[1].append(self.Blocks[2])
                self.Columns[1].append(self.Blocks[3])
            
            
            
            if len(self.Columns[0]) < 2 or len(self.Columns[1]) < 2:
                # redistribute
                self.Columns[0].clear()
                self.Columns[1].clear()
                self.Columns[0].append(self.Blocks[0])
                self.Columns[0].append(self.Blocks[1])
                
                for k in range(2,len(self.Blocks)):
                    self.Columns[1].append(self.Blocks[k])
                
            self.refresh_columns()
            
        self.SaveSlide()
            
    
    def MoveLeft(self):
        print("Moving left")
        if self.SelectedBlock != None:
            if self.SelectedBlock in self.Columns[1]:
                self.Columns[1].remove(self.SelectedBlock)
                self.Columns[0].append(self.SelectedBlock)
                
                self.CurrentLayout = "Custom"
                
                self.refresh_columns()
            
            
        
        
        
    def MoveRight(self):
        print("Moving right")
        if self.SelectedBlock != None:
            if self.SelectedBlock in self.Columns[0]:
                self.Columns[0].remove(self.SelectedBlock)
                self.Columns[1].append(self.SelectedBlock)
                
                self.CurrentLayout = "Custom"
                
                self.refresh_columns()
    
    def MoveUp(self):
        print("Moving Up")
        if self.SelectedBlock != None:
            if self.SelectedBlock in self.Columns[0]:
                index = self.Columns[0].index(self.SelectedBlock)
                if index > 0:
                    self.Columns[0].remove(self.SelectedBlock)
                    self.Columns[0].insert(index-1, self.SelectedBlock)
                    
            if self.SelectedBlock in self.Columns[1]:
                index = self.Columns[1].index(self.SelectedBlock)
                if index > 0:
                    self.Columns[1].remove(self.SelectedBlock)
                    self.Columns[1].insert(index-1, self.SelectedBlock)
                
                
            self.refresh_columns()

        
    def MoveDown(self):
        print("Moving Down")
        if self.SelectedBlock != None:
            if self.SelectedBlock in self.Columns[0]:
                index = self.Columns[0].index(self.SelectedBlock)
                if index < len(self.Columns[0])-1:
                    self.Columns[0].remove(self.SelectedBlock)
                    self.Columns[0].insert(index+1, self.SelectedBlock)
                    
            if self.SelectedBlock in self.Columns[1]:
                index = self.Columns[1].index(self.SelectedBlock)
                if index < len(self.Columns[1])-1:
                    self.Columns[1].remove(self.SelectedBlock)
                    self.Columns[1].insert(index+1, self.SelectedBlock)
                
                
            self.refresh_columns()
            
            
    def SaveSlide(self):
        # Transfer the data to the slide object
        # if self.Slide != None:
        #     pixmap = QPixmap(self.size())
        #     self.render(pixmap)
        #     self.Slide.setPreview(pixmap)
            
        #     ### Update the XML content
            
        #     FrameXML = ET.Element('Frame', id='frame_0')
        #     TitleBar = ET.SubElement(FrameXML, 'TitleBar')
        #     Titlebar_Visible = ET.SubElement(TitleBar, 'Visible')
        #     Titlebar_Visible.text = str(self.TitleVisibility)
        #     TitleBar.text = self.title_text.toPlainText()
            
        #     SubTitleBar = ET.SubElement(FrameXML, 'TitleBar')
        #     SubTitleBar.text = self.subtitle_text.text()
            
        #     FrameLayout = ET.SubElement(FrameXML, 'FrameLayout')
        #     FrameLayout.text = self.CurrentLayout
            
            
        #     for block in self.Blocks:
        #         BlockElem = block.GetXMLContent()
        #         FrameXML.append(BlockElem)

        #     self.Slide.FrameXML = FrameXML

            
        if self.BeamerSlide != None:
            
            self.BeamerSlide.CurrentLayout = self.CurrentLayout
            
            pixmap = QPixmap(self.size())
            self.render(pixmap)
            self.BeamerSlide.setPreview(pixmap)
            
            self.BeamerSlide.Title = self.title_text.toPlainText()
            self.BeamerSlide.Subtitle = self.subtitle_text.text()
            
            
            ## Go through the columns and replicate their structure
            ## Re do this directly in the main functions requires additional code
            ## due to actions (selected, for instance, when move it).
            self.BeamerSlide.Columns[0].clear()
            self.BeamerSlide.Columns[1].clear()
            self.BeamerSlide.Blocks.clear()
            
            for block in self.Columns[0]:
                block.ColumnNumber = 0
                block.UpdateBlock()
                self.BeamerSlide.Columns[0].append(block.Block)
                self.BeamerSlide.Blocks.append( block.Block )
                
            for block in self.Columns[1]:
                block.ColumnNumber = 1
                block.UpdateBlock()
                self.BeamerSlide.Columns[1].append(block.Block)
                self.BeamerSlide.Blocks.append( block.Block )            
                
                

            
            
            
    def ReadSlide (self, slide):
        self.SaveSlide()
        
        ### 
        
        ### Extract the parameters from the slide
        self.title_text.setPlainText(slide.Title)
        self.subtitle_text.setText(slide.Subtitle)
        
        self.CurrentLayout = slide.CurrentLayout
        
        self.BeamerSlide = slide
        
        N = 0
        
        self.Blocks.clear()
        
        self.Columns[0].clear()
        self.Columns[1].clear()
        
        
        for k in range(2):
        
            for block in self.BeamerSlide.Columns[k]:
                nWidget = ContentWidget()
                nWidget.setContentName("Block # " + str(N+1))
                nWidget.Selected.connect(self.selectBlock)
                self.Blocks.append(nWidget)
                
                nWidget.ReadBlock(block)
                
                self.Columns[k].append(nWidget)
                # nWidget.ReadXMLContent(block)
                
                N=N+1
            
        
        
        
        # for block in self.BeamerSlide.Blocks:
        #     nWidget = ContentWidget()
        #     nWidget.setContentName("Block # " + str(N+1))
        #     nWidget.Selected.connect(self.selectBlock)
        #     self.Blocks.append(nWidget)
            
        #     nWidget.ReadBlock(block)
        #     # nWidget.ReadXMLContent(block)
            
        #     N=N+1
            
        self.refresh_Layout()
        
        
        
    
    def ReadSlideOld(self, slide):
        self.SaveSlide()
        
        if self.Slide != slide:
            self.Slide = slide
            # Restoring the slide
            
            try:
                FrameXML = self.Slide.FrameXML
                
                # Title bar properties
                
                TitleBar = FrameXML.findall('TitleBar')[0]
                   
                Titlebar_Visible = TitleBar.findall('Visible')[0]

                self.title_text.setPlainText( TitleBar.text )
                
                                
                if Titlebar_Visible.text == 'False':
                    self.config_title(False)
                else:
                    self.config_title(True)
                    
                
                # Frame layout

                self.CurrentLayout = FrameXML.findall('FrameLayout')[0].text
                
                
                # Search for blocks
                
                nblocks = FrameXML.findall('Block')
                
                if len(nblocks) > 0:
                    self.Blocks.clear()
                
                N = 0
                for block in nblocks:
                    nWidget = ContentWidget()
                    nWidget.setContentName("Block # " + str(N+1))
                    nWidget.Selected.connect(self.selectBlock)
                    self.Blocks.append(nWidget)
                    nWidget.ReadXMLContent(block)
                    
                    N=N+1
                    
                self.refresh_Layout()
                    
            except Exception as error:
                print(error)
                print("Cannot read slide")
                None
            
            
            
            
        
        
        
            
            

                
                
                    
                
                
                
                
            
        
    
    
    
        
            
            
        
            
            
            
            
            

