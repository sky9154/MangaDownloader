import os
from urllib.request import urlopen
from PyQt6.QtWidgets import QHBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QFont


class CoverImage(QLabel):

  def __init__(self, main_config):
    super().__init__()

    self.main_config = main_config
    self.cover_label = self
    self.cover_data = None

  def init_ui(self):
    images_path = self.main_config['Paths']['images']
    cover_path = os.path.join(images_path, 'cover.png')

    with open(cover_path, 'rb') as cover:
      self.cover_data = cover.read()

    cover = QPixmap()
    cover.loadFromData(self.cover_data)

    self.cover_label.setPixmap(cover)
    self.cover_label.setScaledContents(True)
    self.cover_label.setFixedSize(240, 345)

    cover_image = QHBoxLayout()
    cover_image.addStretch(1)
    cover_image.addWidget(self.cover_label)
    cover_image.addStretch(1)

    return cover_image

  def set_cover(self, cover_url):
    cover_data = urlopen(cover_url).read()

    cover_image = QPixmap()
    cover_image.loadFromData(cover_data)

    self.cover_label.setPixmap(cover_image)

  def reset_cover(self):
    cover = QPixmap()
    cover.loadFromData(self.cover_data)

    self.cover_label.setPixmap(cover)

class InfoLabel(QLabel):

  def __init__(self, value):
    super().__init__()

    self.value = value

  def init_ui(self):
    self.setText(f'{self.value}：')
    self.setFixedHeight(40)
    self.setFont(QFont(self.font().family(), 10))

    return self