"""
    Author: Ayzalme
    Github: Tooya12
"""
import pdb
import re
import httpx
import sys
import subprocess
import time
import json
from bs4 import BeautifulSoup as bsSoup
from glob import glob
from time import sleep
from rich.console import Console
from rich.table import Table
from rich.text import Text
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from mod import cacheTime

class getBmkgWebsite():

  def __init__(self):
    self.cacheName = ".cache-html"
    self.nameConfig = "configCuaca.json"
    self.cmd = ["help", "ganti-provinsi", "version", "daftar-daerah", "daftar-provinsi", "ganti-daerah"]
    self.cmdQuit = ["exit", "quit"]
    self.promptStr = ">>> "
    self.console = Console()
    self.configCuaca = glob(self.nameConfig)

    """ Default untuk daerah DKI Jakarta """
    self.url = "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?kab=Jakarta&Prov=DKI_Jakarta&AreaID=501195"
    self.urlProvinsi = "https://www.bmkg.go.id/cuaca/"
    self.urlDaerah = "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg"

    """ Set user-agent """
    self.headers = {"user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"}

  def requestBmkg(self):
    self.console.print("[yellow]Mengambil data website...\n")

    try:
      self.request = httpx.get(self.url, headers=self.headers)
      self.response = self.request.raise_for_status()

    except httpx.RequestError as err:
      self.console.print(f"[bold red]Error untuk terhubung ke {err.request.url}.")
      sys.exit(1)

    except httpx.HTTPStatusError as err:
      self.console.print(f"[bold red]Error response {err.response.status_code} ketika terhubung ke {err.request.url}.")
      sys.exit(1)

    self.beautiful = str(bsSoup(self.request.text, "html.parser"))

    with open(self.cacheName, "w") as file:
      file.write(self.beautiful)
      file.close()

    self.console.print("[green]Berhasil mengambil data website.\n")

  def parserDataHTML(self):
    self.console.print("[yellow]Menyusun data HTML...\n")

    with open(self.cacheName) as file:
      self.beautiful = bsSoup(file, "html.parser")
      file.close()

    self.pageMain = self.beautiful.find("div", class_="container content")
    self.pageTitle = self.pageMain.find("h2").get_text()
    self.pageTitleSecond = self.pageMain.find("h4").get_text()
    self.pageTabPanel = self.beautiful.find_all("ul", class_="nav nav-tabs")
    self.pageDaerah = self.beautiful.find("div", class_="col-sm-12 no-padding")
    self.pageTitleDaerah = self.pageDaerah.find("option")
    self.pageContentDaerah = self.pageDaerah.find_all("optgroup")
    self.pageValueDaerah = self.pageDaerah.find_all("option")[1:]
    self.pageProvinsi = self.beautiful.find("div", class_="list-cuaca-provinsi md-margin-bottom-10")
    self.pageMainProvinsi = self.pageProvinsi.find_all("a")

    """ Extract Content """
    self.pageTabPanelText = None
    self.pageFinalTitle = self.pageTitle + " - " + self.pageTitleSecond
    self.pageCuacaKota = {}
    self.contentDaerah = {}
    self.valueDaerah = []
    self.contentProvinsi = {}
    self.checkPoint = 0
    self.titlePoint = 1

    for tabPanel in self.pageTabPanel:
      self.pageTabPanelText = tabPanel.get_text().rsplit("\n")
      length = len(self.pageTabPanelText) - 1
      self.pageTabPanelText = self.pageTabPanelText[1:length]

    self.lengthTabPanel = len(self.pageTabPanelText)

    for itter in self.pageMainProvinsi:
      text = itter.get_text()
      href = itter.get("href")

      self.contentProvinsi.update({text: href})

    for itter in self.pageValueDaerah: self.valueDaerah.append(itter.get("value"))

    for itter in self.pageContentDaerah:
      label = itter.get("label")

      if (label):
          self.contentDaerah.update({f"Title-{self.titlePoint}": label})
          self.titlePoint += 1

      splitText = itter.get_text().rsplit("\n")
      splitText = [split for split in splitText if split != ""]

      for adding in splitText:
        self.contentDaerah.update({adding: self.valueDaerah[self.checkPoint]})
        self.checkPoint += 1

    def getCuacaKota(tabPanel):
      trueResult = []
      removeChar = "\xa0"
      clearSomeText = ["Cuaca", "Saat", "Ini", "Kelembapan", "Udara:", "Kec.", "Angin:", "Arah", "Angin", "dari:"]
      pageCuaca = self.pageMain.find("h2", class_="kota").parent

      """ Remove \n """
      result = pageCuaca.get_text().rsplit("\n")

      """ Remove empty str """
      result = [comp for comp in result if comp != ""]

      """ Remove \xa0 """
      for itter in result:
        if (removeChar in itter):
            index = itter.index(removeChar)
            itter = itter[:index] + " " + itter[index + 1:]

        trueResult.append(itter)

      """ Clear beberapa Text """
      trueResult = " ".join(trueResult).rsplit(" ")

      for itterOne in clearSomeText:
        for itterTwo in trueResult:
          if (itterOne == itterTwo):
              trueResult.remove(itterOne)

      indexKm = trueResult.index("km/jam")

      if (indexKm == 5):
          trueResult = [" ".join(trueResult[:1]), trueResult[1], " ".join(trueResult[2:4]), " ".join(trueResult[4:6]), " ".join(trueResult[6:])]

      elif (indexKm == 6):
            trueResult = [" ".join(trueResult[:2]), trueResult[2], " ".join(trueResult[3:5]), " ".join(trueResult[5:7]), " ".join(trueResult[7:])]

      else:
          trueResult = [" ".join(trueResult[:2]), trueResult[2], " ".join(trueResult[3:5]), " ".join(trueResult[5:7]), trueResult[7]]

      dict = {"MainPage": trueResult}
      self.pageCuacaKota.update(dict)

      """ Pastikan trueResult dalam keadaan fresh """
      trueResult = []

      for panel in range(1, tabPanel + 1):
        pageCuaca = self.pageMain.find("div", id=f"TabPaneCuaca{panel}")

        """ Remove \n """
        result = pageCuaca.get_text().rsplit("\n")

        """ Remove empty str """
        result = [comp for comp in result if comp != ""]

        """ Remove \xa0 """
        newList = None

        for itter in result:
          if (removeChar in itter):
              index = itter.index(removeChar)
              itter = itter[:index] + " " + itter[index + 1:]

          if ("jam" in itter):
              index = itter.index("jam") + 3
              itter = itter[:index] + " " + itter[index:]
              newList = itter.rsplit(" ")
              newList = [" ".join(newList[:2]), " ".join(newList[2:len(newList) - 1])]

          if (newList):
              trueResult.append(newList[0])
              trueResult.append(newList[1])
              newList = None

          else:
              trueResult.append(itter)


        dict = {f"Panel-{panel}": trueResult}
        self.pageCuacaKota.update(dict)

        """ Pastikan trueResult dalam keadaan fresh """
        trueResult = []

    """ Get data cuaca """
    getCuacaKota(self.lengthTabPanel)

    self.console.print("[green]Berhasil menyusun data HTML...\n")

  def showingResult(self):

    self.console.print("\n[green]Initialisasi...\n")

    if (not self.configCuaca):
        #self.requestBmkg()
        self.parserDataHTML()

    """ Table Content """
    def makeTable(cuaca, tab, main, panel):
      repeat = int(len(cuaca[f"Panel-{panel}"]) / 6)
      currentPosition = 0

      if (main):
          text = Text("Cuaca Saat Ini", justify="center")

          table = Table(title=f"Prakiraan Cuaca BMKG\n{self.pageFinalTitle}\nTanggal {tab[panel - 1]} 2024", expand=True, title_justify="center", title_style="dodger_blue1", style="blue")
          table.add_column(text, justify="full", no_wrap=True)
          table.add_row(f"Cuaca            : {cuaca["MainPage"][0]}")
          table.add_row(f"Suhu             : {cuaca["MainPage"][1]}")
          table.add_row(f"Kelembapan Udara : {cuaca["MainPage"][2]}")
          table.add_row(f"Kecepatan Angin  : {cuaca["MainPage"][3]}")
          table.add_row(f"Arah Angin       : {cuaca["MainPage"][4]}")

          self.console.print(table)

      for loop in range(repeat):
        text = Text(f"{cuaca[f"Panel-{panel}"][currentPosition]}", justify="center")

        table = Table(expand=True, style="blue")
        table.add_column(text, justify="full", no_wrap=True)
        currentPosition += 1
        table.add_row(f"Cuaca            : {cuaca[f"Panel-{panel}"][currentPosition]}")
        currentPosition += 1
        table.add_row(f"Suhu             : {cuaca[f"Panel-{panel}"][currentPosition]}")
        currentPosition += 1
        table.add_row(f"Kelembapan Udara : {cuaca[f"Panel-{panel}"][currentPosition]}")
        currentPosition += 1
        table.add_row(f"Kecepatan Angin  : {cuaca[f"Panel-{panel}"][currentPosition]}")
        currentPosition += 1
        table.add_row(f"Arah Angin       : {cuaca[f"Panel-{panel}"][currentPosition]}")
        currentPosition += 1

        self.console.print(table)

    def daftarDaerah():
      self.checkPoint = 1
      word = []
      grid = Table.grid(expand=True)
      grid.add_column()

      for itter in self.contentDaerah.keys():
        if ("Title" in itter):
            grid.add_row(f"\n{self.contentDaerah[itter]}")
            continue

        grid.add_row(f"  {self.checkPoint}. {itter}")
        word.append(itter)
        self.checkPoint += 1

      self.console.print(grid, "")
      daerahCompleter = WordCompleter(word, ignore_case=True, sentence=True)

      return word, daerahCompleter

    def daftarProvinsi():
      self.checkPoint = 1
      word = []
      grid = Table.grid(expand=True)
      grid.add_column()

      for itter in self.contentProvinsi.keys():
        grid.add_row("", f"{self.checkPoint}. {itter}")
        word.append(itter)
        self.checkPoint += 1

      self.console.print("", grid, "")
      provinsiCompleter = WordCompleter(word, ignore_case=True, sentence=True)

      return word, provinsiCompleter

    def pilihProvinsi(changePrompt=False):
        word, provinsiCompleter = daftarProvinsi()
        number = len(self.contentProvinsi)
        quitLoop = False

        if (changePrompt):
            self.promptStr = ("ganti-provinsi >>> ")

        while True:

          userInput = prompt(self.promptStr, completer=provinsiCompleter, complete_while_typing=True)

          if (userInput in self.cmdQuit):
              if (changePrompt):
                  self.promptStr = ">>> "

              break

          for itter in word:
            key = itter.lower()

            if (userInput.lower() == key):
                self.url = self.urlProvinsi + self.contentProvinsi[itter]
                self.console.print(f"Anda memilih provinsi {itter}\n")
                #self.requestBmkg()
                self.parserDataHTML()

                if (changePrompt):
                    self.promptStr = ">>> "

                quitLoop = True
                break

          if (quitLoop):
              break

          userNumber = [num for num in userInput if num.isdigit()]
          if (userNumber):
              userNumber = int("".join(userNumber))

              if (userNumber > 0 and userNumber <= number):
                  self.url = self.urlProvinsi + self.contentProvinsi[word[userNumber - 1]]
                  self.console.print(f"Anda memilih provinsi {word[userNumber - 1]}\n")
                  #self.requestBmkg()
                  self.parserDataHTML()

                  if (changePrompt):
                      self.promptStr = ">>> "

                  break

              else:
                  self.console.print(f"Mohon masukan angka antara 1 - {number}")

          else:
              self.console.print("Mohon pilih dengan angka atau ketik nama provinsi dengan benar!")

    def pilihDaerah(changePrompt=False):
        word, daerahCompleter = daftarDaerah()
        number = len(word)
        quitLoop = False

        if (changePrompt):
            self.promptStr = "ganti-daerah >>> "

        while True:

          userInput = prompt(self.promptStr, completer=daerahCompleter, complete_while_typing=True)

          if (userInput in self.cmdQuit):
              if (changePrompt):
                  self.promptStr = ">>> "

              break

          for itter in word:
            key = itter.lower()

            if (userInput.lower() == key):
                self.url = self.urlDaerah + self.contentDaerah[itter]
                self.console.print(f"Anda memilih daerah {itter}\n")
                #self.requestBmkg()
                self.parserDataHTML()

                if (changePrompt):
                    self.promptStr = ">>> "

                quitLoop = True
                break

          if (quitLoop):
              break

          userNumber = [num for num in userInput if num.isdigit()]
          if (userNumber):
              userNumber = int("".join(userNumber))

              if (userNumber > 0 and userNumber <= number):
                  self.url = self.urlDaerah + self.contentDaerah[word[userNumber - 1]]
                  self.console.print(f"Anda memilih daerah {word[userNumber - 1]}\n")
                  #self.requestBmkg()
                  self.parserDataHTML()

                  if (changePrompt):
                      self.promptStr = ">>> "

                  break

              else:
                  self.console.print(f"Mohon masukan angka antara 1 - {number}")

          else:
              self.console.print("Mohon pilih dengan angka atau ketik nama provinsi dengan benar!")

    if (self.configCuaca):
        with open(self.nameConfig) as file:
            self.jsonDump = json.loads(file.read())
            self.url = self.jsonDump["url"]
            file.close()

        """
            Check apakah cache sudah expired jika sudah
            request data baru, jika cache hilang buat
            cache baru
        """
        expired = False #cacheTime.isCacheExpired()

        if (expired):
            #self.requestBmkg()
            self.parserDataHTML()

            """ Buat cache yang expired setiap 10 menit """
            makeCache = cacheTime.makeCacheFile(10)

        else:
            self.parserDataHTML()

    else:
        self.console.rule()
        self.console.print("[bold green]Prakiraan Cuaca BMKG v1.0 by Ayzalme\n", justify="center")
        self.console.print("[green]Silahkan Pilih Provinsi anda...\n", justify="center")
        self.console.rule()
        sleep(2)

        """ Memilih Provinsi """
        pilihProvinsi()

        self.console.rule()
        self.console.print("[green]Silahkan pilih Daerah anda...\n", justify="center")
        self.console.rule()
        time.sleep(2)

        """ Memilih Daerah """
        pilihDaerah()

        """ Simpan config """
        with open(self.nameConfig, "w") as file:
            self.jsonConfig = json.dumps({"url": self.url})
            file.write(self.jsonConfig)
            file.close()

    """ Call Table """
    makeTable(self.pageCuacaKota, self.pageTabPanelText, True, 1)

    while True:
      userInput = prompt(self.promptStr)
      self.isCmd = userInput in self.cmd

      if (userInput in self.cmdQuit):
          break

      if (self.isCmd):
          if (userInput == "help"):
              self.console.print("\nList Command yang tersedia :\n")

              grid = Table.grid(padding=(0,2), expand=True)
              grid.add_column()
              grid.add_row("help", "Untuk menampilkan pesan ini.\n")
              grid.add_row("version", "Untuk menampilkan versi dan author script ini.\n")
              grid.add_row("ganti-provinsi", "Untuk mengganti provinsi.\n")
              grid.add_row("ganti-daerah", "Untuk mengganti daerah.\n")
              grid.add_row("daftar-daerah", "Untuk menampilkan daftar daerah yang ada di provinsi saat ini.\n")
              grid.add_row("daftar-provinsi", "Untuk menampilkan daftar provinsi.\n")

              self.console.print(grid)

          elif (userInput == "version"):
                self.console.print("Prakiraan Cuaca BMKG v1.0 by Ayzalme")

          elif (userInput == "ganti-provinsi"):
                pilihProvinsi(changePrompt=True)
                makeTable(self.pageCuacaKota, self.pageTabPanelText, True, 1)

          elif (userInput == "ganti-daerah"):
                pilihDaerah(changePrompt=True)
                makeTable(self.pageCuacaKota, self.pageTabPanelText, True, 1)

          elif (userInput == "daftar-daerah"):
                self.console.print("\nDaftar daerah yang tersedia di provinsi ini :")

                daftarDaerah()

          elif (userInput == "daftar-provinsi"):
                self.console.print("\nDaftar provinsi :")

                daftarProvinsi()

      else:
          self.console.print(f"'{userInput}' Command tidak tersedia, ketik 'help' untuk menampilkan command yang tersedia")

""" Lets The Show Begins! """
objectStartUp = getBmkgWebsite()
objectStartUp.showingResult()
