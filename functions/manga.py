import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from urllib import request, error
from bs4 import BeautifulSoup as bs
from PyQt6.QtCore import QThread, pyqtSignal


class DownloadThread(QThread):
  progress = pyqtSignal(int)

  def __init__(self, main_config, image_list, download_path):
    super().__init__()

    self.main_config = main_config
    self.image_list = image_list
    self.download_path = download_path
    self.title = self.main_config['General']['title']

    if os.path.exists(self.download_path):
      return
    else:
      os.makedirs(self.download_path)

  def run(self):
    image_list_length = len(self.image_list)
    max_workers = int(self.main_config['Dowload']['max_workers'])

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
      def download_image(image_url):
        ext = image_url.split('.')[-1]

        image_name = os.path.basename(image_url).split('.')[0]
        image_name = f'{image_name.zfill(len(str(image_list_length)))}.{ext}'
        image_path = os.path.join(self.download_path, image_name)

        request.urlretrieve(image_url, image_path)

        time.sleep(int(self.main_config['Dowload']['delay']))

      for index, _ in enumerate(executor.map(download_image, self.image_list)):
        self.progress.emit(index + 1)

class Manga:

  def __init__(self, main_config, window, enabled_button):
    self.main_config = main_config
    self.window = window
    self.enabled_button = enabled_button
    self.title = self.main_config['General']['title']
    self.download_folder = None
    self.download_path = None
    self.mange_id = None
    self.origin = None
    self.soup = None

    self.headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
    }

  def get_cover(self):
    cover_element = self.soup.find(id='cover')
    cover_tag = cover_element.find('img')

    return cover_tag['data-src']

  def get_title(self):
    title_element = self.soup.find('h2', class_='title')
    title_element = title_element.find_all('span')

    return ''.join(span.get_text() for span in title_element)

  def init(self, mange_id):
    self.mange_id = mange_id
    self.origin = f'https://nhentai.net/g/{self.mange_id}'

  def init_error(self):
    self.mange_id = '371601'
    self.origin = f'https://nhentai.net/g/{self.mange_id}'

  def check(self):
    self.window.setWindowTitle(f'{self.main_config['General']['title']} | 接続準備中...')
    self.enabled_button(False)

    req = request.Request(url=self.origin, headers=self.headers)

    try:
      response = request.urlopen(req)
      self.soup = bs(response.read().decode('utf-8'), 'html.parser')

      return True
    except error.HTTPError:
      self.init_error()
      self.check()

      return False

  def download(self, download_path, save_pdf_state):
    self.enabled_button(False)

    thumbnailContainer = self.soup.find(id='thumbnail-container')

    self.download_folder = re.sub(r'[<>|\|*|"|\/|\|:|?]', ' ', self.get_title())
    self.download_path = os.path.join(download_path, self.download_folder)

    if thumbnailContainer:
      image_list = []
      image_element = thumbnailContainer.find_all('img', class_='lazyload')

      for image in image_element:
        image_url = image['data-src']
        ext = image_url.split('.')[-1]

        image_url = image_url.replace(f't.{ext}', f'.{ext}')
        image_url = image_url.replace('https://t', 'https://i')

        image_list.append(image_url)

      self.download_thread = DownloadThread(self.main_config, image_list, self.download_path)
      self.download_thread.started.connect(lambda: on_download_started())
      self.download_thread.finished.connect(lambda: on_download_finished())
      self.download_thread.start()

    def save_as_pdf():
      name = re.sub(r'[<>|\|*|"|\/|\|:|?]', ' ', self.get_title())
      pdf_path = os.path.join(self.download_path, f'{name}.pdf')
      print(pdf_path)

    def on_download_started():
      self.window.setWindowTitle(f'{self.title} | ダウンロード中...')
      self.enabled_button(False)

    def on_download_finished():
      self.window.setWindowTitle(f'{self.title} | ダウンロード完了')

      if (save_pdf_state):
        save_as_pdf()

      self.enabled_button(True)