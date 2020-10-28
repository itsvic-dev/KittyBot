from . import config


def addToBlacklist(userID: int) -> None:
    if config.get("blacklist", "blacklisted") is None:
        config.set("blacklist", "blacklisted", [userID])
    else:
        arr = config.get("blacklist", "blacklisted")
        if userID not in arr:
            arr.append(userID)
        config.set("blacklist", "blacklisted", arr)


def removeFromBlacklist(userID: int) -> None:
    if config.get("blacklist", "blacklisted") is None:
        return
    else:
        arr = config.get("blacklist", "blacklisted")
        if userID in arr:
            arr.remove(userID)
        config.set("blacklist", "blacklisted", arr)


def isInBlacklist(userID: int) -> bool:
    if config.get("blacklist", "blacklisted") is None:
        return False
    else:
        arr = config.get("blacklist", "blacklisted")
        return userID in arr
