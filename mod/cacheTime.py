"""
    Author: Ayzalme
    Github: Tooya12
"""
from rich import print
from glob import glob

if (__name__ == "__main__"):
    import zalsTime as zt

else:
    from mod import zalsTime as zt

zalTime = zt.zalsTime()
cacheName = ".cache"

def makeCacheFile(increase):
    increaseTime = zalTime.timeIncrease(incMinute=increase, encode=True)

    with open(cacheName, "w") as file:
        file.write(increaseTime)
        file.close()

def isCacheExpired():
    thereCache = glob(cacheName)

    if (thereCache):
        with open(cacheName) as file:
            increaseTime = file.read()
            file.close()

        defaultTime = zalTime.timeNow(encode=True)
        compare = zalTime.timeCompare(increaseTime, defaultTime, decode=True)

        if (not compare):
            print("[bold yellow]Cache yang tersedia sudah expired!\n")

            """
                Jika increaseTime < defaultTime
            """
            return True

        """
            Jika increaseTime > defaultTime
        """
        return False

    else:
        print("[bold red]Cache file hilang!\n")
        return True
