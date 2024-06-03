#!/usr/bin/env python3

import os
import time
import logging
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, Table
from reportlab.graphics import shapes
from reportlab.lib import colors
from reportlab.lib.units import mm, inch

# Get the path to the demos directory.
base_path = os.path.dirname(__file__)
font_path = os.path.expanduser('~/Library/Fonts')

# Add some fonts.
# Google Fonts: https://fonts.google.com/noto/specimen/Noto+Sans
registerFont(TTFont('Noto Sans', os.path.join(font_path, 'NotoSans-Regular.ttf')))
registerFont(TTFont('Noto Sans Bold', os.path.join(font_path, 'NotoSans-Bold.ttf')))

styles = getSampleStyleSheet()

class Note:
    def __init__(self, string, font_name, width, height, marginsTBLR=None):
        self.string = string
        self.font_name = font_name
        self.pageWidth = width*mm
        self.pageHeight = height*mm
        self.marginsTBLR = marginsTBLR if marginsTBLR else [8, 8, 8, 8]

        self.file_name = '/tmp/printNote_temp.pdf'

        print(f'Page size: {self.pageWidth/inch:.3f} in x {self.pageHeight/inch:.3f} in')
        print(f'Body size: {self.bodyWidth()/inch:.3f} in x {self.bodyHeight()/inch:.3f} in')

        self.createPage()

    def marginTop(self):
        return self.marginsTBLR[0]*mm

    def marginBottom(self):
        return self.marginsTBLR[1]*mm

    def marginLeft(self):
        return self.marginsTBLR[2]*mm

    def marginRight(self):
        return self.marginsTBLR[3]*mm

    def marginTB(self):
        return self.marginTop() + self.marginBottom()

    def marginLR(self):
        return self.marginLeft() +self.marginRight()

    def bodyWidth(self):
        return self.pageWidth - self.marginLR()

    def bodyHeight(self):
        return self.pageHeight - self.marginTB()


    def wrapText(self, text, font_size, base_para_style):
        para_style = ParagraphStyle('myStyle',
                               fontName=self.font_name,
                               fontSize=font_size,
                               leading=font_size*1.1,
                               alignment=1,
                               splitLongWords=0,
                               parent=base_para_style)
        
        self.paragraph = Paragraph(text, style=para_style)
        
        width, height = self.paragraph.wrapOn(self.canvas, self.bodyWidth(), self.bodyHeight())
        width = self.paragraph.minWidth()

        return width, height

    def scaleFontSize(self, text, base_para_style):
        font_size = 9
        width = 0
        height = 0
        margin = 5
        while font_size < 200:
            font_size += 1
            width, height = self.wrapText(text, font_size, base_para_style)
            logging.info(f'Font size: {font_size} -> Width: {width}, Height: {height}')
            if height >= self.bodyHeight() or width >= self.bodyWidth():
                break

        if height > self.bodyHeight() or width > self.bodyWidth():
            font_size -= 1
            width, height = self.wrapText(text, font_size, base_para_style)

        print(f'Font size: {font_size} pt -> Width: {width/inch:.3f} in, Height: {height/inch:.3f} in')

        self.paragraph.drawOn(self.canvas, self.marginLeft(), self.marginBottom() + (self.bodyHeight()-height)/2)

    def createPage(self):
        self.canvas = canvas.Canvas(self.file_name)
        self.canvas.setPageSize( (self.pageWidth, self.pageHeight) )
        base_para_style = styles['Normal']
        self.scaleFontSize(self.string, base_para_style)

        self.canvas.showPage()
        self.canvas.save()


class NemonicNote(Note):
    PAGE_SIZE = {'note': (80, 80),
                 'label1': (76, 110),
                 'label2': (76, 110),
                 'label3': (76, 110),
                 'label4': (76, 110),
                 'label0.5': (76, 110)
                }

    PAGE_SIZE_ACTUAL = {'note': (80, 80),
                        'label1': (76, 25),
                        'label2': (76, 51),
                        'label3': (76, 76),
                        'label4': (76, 102),
                        'label0.5': (51, 13)
                       }

    STICKY_LPR_ORIENTATION = {'up': '-o orientation-requested=5',
                              'down': '-o orientation-requested=4',
                              'left': '-o orientation-requested=6',
                              'right': '-o orientation-requested=3'
                             }


    def __init__(self, string, font_name, media):
        self.media = media

        width, height = self.PAGE_SIZE[self.media]

        # Set top/bottom margins because for some reason the page height for labels needs to be
        # bigger than the actual page
        marginsTBLR = None
        if self.media.startswith('label'):
            heightActual = self.PAGE_SIZE_ACTUAL[media][1]
            marginOffset = (height - heightActual) / 2
            marginsTBLR = [marginOffset + 4, marginOffset + 4, 8, 8]
        super().__init__(string, font_name, width, height, marginsTBLR)

    def display(self):
        os.system(f'open {self.file_name}')

    def print(self, printer, stickyOrientation):
        if self.media.startswith('label'):
            stickyOrientation = 'right'
        os.system(f'lpr {self.STICKY_LPR_ORIENTATION[stickyOrientation]} -P {printer} {self.file_name}')


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_string')
    parser.add_argument('--checklist', '-c', action='store_true', help='Convert a comma-separated list to a checklist')
    parser.add_argument('--font', '-f', default='Noto Sans Bold')
    parser.add_argument('--printer', '-p', default='nemonic_MIP_201', help='Printer name')
    parser.add_argument('--media', '-m', default='note', choices=NemonicNote.PAGE_SIZE.keys())
    parser.add_argument('--sticky_edge', '-s', default='up', choices=NemonicNote.STICKY_LPR_ORIENTATION.keys(), help='Location of the sticky edge')
    parser.add_argument('--dryrun', '-d', action='store_true')
    args = parser.parse_args()

    start_time = time.time()

    if args.checklist:
        tokens = args.input_string.split(',')
        tokens = [f'\N{BALLOT BOX} {t}' for t in tokens]
        args.input_string = '\n'.join(tokens)

    print(args.input_string)

    note = NemonicNote(args.input_string, args.font, args.media)

    print(f'\nProcessing time: {time.time()-start_time:.3f} s')

    if args.dryrun:
        note.display()
    else:    
        note.print(args.printer, args.sticky_edge)
