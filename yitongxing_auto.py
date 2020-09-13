import datetime
import codecs
import requests
import os
import json
import time
import random
from pyquery import PyQuery as pq
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

cache = []

baseUrl = "https://game.adjuz.net/v2/"
headers = {
    # "authority": "game.adjuz.net",
    #        "method": "POST",
    #        "path": "/V2/User/Api/GetLoginTask",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    # "User-Agent": "10101;2.1.6beta;Android;7.0;AL1512-mido-build-20191107001218;xiaomi;Redmi Note 4X;1080*1920;null;MOBILE;",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
    "origin": "https://static.game.adjuz.net",
    "referer": "https://static.game.adjuz.net/game/gamecenter/YTX/index.html?v=1512141284",
    "version": "v2",
    "Authorization": "APPCODE 0904e961aaef4609a4191018396cc90f"}

session = requests.Session()
session.headers.update(headers)

videoTime = 5
interTime = 3


def base_param(imei, uid):
    return "?device=android&imei={i}&source=L1001&uid={u}&version=2.1.6&version_code=216".format(i=imei, u=uid)


def setparam(key, value):
    dat = {}
    dat[key] = value
    return dat


def register(list):
    for i in list:
        dat = setparam("imei", str(i))

        rep = session.post(baseUrl + "api/user/register?device=android&source=L1001&version=2.1.6&version_code=216",
                           data=dat)
        print("请求响应 用户注册:" + rep.text)
        assert rep.status_code == 200
        time.sleep(interTime)


# 成语金币翻倍
def phraseDouble(imei, uid):
    rep = session.post(baseUrl + "api/Answer/double" + base_param(imei, uid), data={})
    print("请求响应 成语或刮刮卡金币翻倍:" + rep.text)
    assert rep.status_code == 200
    time.sleep(interTime)


# 新人紅包
def newbieRed(imei, uid):
    rep = session.post(baseUrl + "api/user/loginGIve" + base_param(imei, uid), data={})
    print("请求响应 检查是否新用户:" + rep.text)
    assert rep.status_code == 200
    if json.loads(rep.text)["data"]["status"] == 1:
        # 有新人紅包可領
        time.sleep(interTime)
        rep = session.post(baseUrl + "api/user/getLoginGive" + base_param(imei, uid), data={})
        print("请求响应 新人紅包:" + rep.text)


# 幸运转盘
def luckDraw(imei, uid):
    for i in range(60):
        rep = session.get(baseUrl + "api/Turntable/luckDraw?imei={i}".format(i=imei))
        print("请求响应 幸运转盘:" + rep.text)
        assert rep.status_code == 200
        if json.loads(rep.text)["code"] != 200:
            break
        type = json.loads(rep.text)["data"]["prize_data"]["type"]
        isDouble = json.loads(rep.text)["data"]["is_double"] == 1
        if type == 1:
            # 红包
            rep = session.get(baseUrl + "api/Turntable/get?imei={i}".format(i=imei))
            print("请求响应 幸运转盘之红包:" + rep.text)
        elif type == 2:
            # 宝箱
            rep = session.get(baseUrl + "api/Turntable/get?imei={i}".format(i=imei))
            print("请求响应 幸运转盘之宝箱:" + rep.text)
        else:
            # 金币
            if isDouble:
                rep = session.get(baseUrl + "api/Turntable/newDouble?imei={i}".format(i=imei))
                print("请求响应 幸运转盘之金币翻倍:" + rep.text)
        # 开宝箱
        if json.loads(rep.text)["data"]["success_numbers"] == 5:
            rep = session.get(baseUrl + "api/Turntable/open?imei={i}&numbers={num}".format(i=imei, num=5))
            print("请求响应 幸运转盘 开宝箱成功:" + rep.text)
        if json.loads(rep.text)["data"]["success_numbers"] == 30:
            rep = session.get(baseUrl + "api/Turntable/open?imei={i}&numbers={num}".format(i=imei, num=30))
            print("请求响应 幸运转盘 开宝箱成功:" + rep.text)
        if json.loads(rep.text)["data"]["success_numbers"] == 60:
            rep = session.get(baseUrl + "api/Turntable/open?imei={i}&numbers={num}".format(i=imei, num=60))
            print("请求响应 幸运转盘 开宝箱成功:" + rep.text)
        time.sleep(30)


# 碎片激励视频
def fragmentVideo(imei, uid):
    time.sleep(videoTime)
    rep = session.get(
        "http://api.fragment.zouluzhuan.com/api/fragment/luckDraw?project_id=67394728&uid={u}&is_watch=1".format(u=uid))
    print("请求响应 碎片视频后抽奖:" + rep.text)
    data = json.loads(rep.text)["data"]
    if data["is_watch"] == 1:
        fragmentVideo(imei, uid)
    elif data["is_double"] == 1:
        # 可翻倍
        time.sleep(interTime)
        rep = session.get(
            "http://api.fragment.zouluzhuan.com/api/fragment/double?project_id=67394728&uid={u}".format(u=uid))
        print("请求响应 碎片翻倍:" + rep.text)


# 碎片
def fragment(imei, uid):
    for i in range(20):
        time.sleep(interTime)
        rep = session.get(
            "http://api.fragment.zouluzhuan.com/api/fragment/luckDraw?project_id=67394728&uid={u}".format(u=uid))
        print("请求响应 碎片:" + rep.text)
        assert rep.status_code == 200
        if json.loads(rep.text)["code"] == 2001:
            # 次数用完 获取次数
            time.sleep(videoTime)
            rep = session.get(
                "http://api.fragment.zouluzhuan.com/api/fragment/addLuckDraw?project_id=67394728&uid={u}".format(
                    u=uid))
            print("请求响应 碎片 获取次数:" + rep.text)
            fragment(imei, uid)
        elif json.loads(rep.text)["code"] == 2009:
            # 今日次数用完
            break
        elif json.loads(rep.text)["code"] == 200:
            data = json.loads(rep.text)["data"]

            if data["is_watch"] == 1:
                # 需要看激励视频
                time.sleep(videoTime)
                rep = session.get(
                    "http://api.fragment.zouluzhuan.com/api/fragment/luckDraw?project_id=67394728&uid={u}&is_watch=1".format(
                        u=uid))
                print("请求响应 碎片视频后抽奖:" + rep.text)
                if json.loads(rep.text)["code"] == 202:
                    # 抽奖次数用完
                    break
                elif json.loads(rep.text)["data"]["is_watch"] == 1:
                    fragmentVideo(imei, uid)
            elif data["is_double"] == 1:
                # 可翻倍
                time.sleep(interTime)
                rep = session.get(
                    "http://api.fragment.zouluzhuan.com/api/fragment/double?project_id=67394728&uid={u}".format(u=uid))
                print("请求响应 碎片翻倍:" + rep.text)
            if data["success_numbers"] == 5:
                # 开宝箱
                rep = session.get(
                    "http://api.fragment.zouluzhuan.com/api/fragment/open?project_id=67394728&uid={u}&numbers=5".format(
                        u=uid))
                print("请求响应 碎片5开宝箱:" + rep.text)
            if data["success_numbers"] == 10:
                # 开宝箱
                rep = session.get(
                    "http://api.fragment.zouluzhuan.com/api/fragment/open?project_id=67394728&uid={u}&numbers=10".format(
                        u=uid))
                print("请求响应 碎片10开宝箱:" + rep.text)


# 下一道题或者下一轮
def checkout(action, imei, uid):
    dat = setparam("action", action)
    print("请求参数 成语题目切换:" + str(dat))
    rep = session.post(baseUrl + "api/Answer/checkAnswer" + base_param(imei, uid), data=dat)
    print("请求响应 成语题目切换:" + rep.text)
    assert rep.status_code == 200
    time.sleep(videoTime)

    phraseDouble(imei, uid)
    return json.loads(rep.text)


# 日常奖励收割
def getReward(imei, uid):
    rep = session.post(baseUrl + "api/user/dailyAndLimit" + base_param(imei, uid), data={})
    print("请求响应 日常奖励收割:" + rep.text)
    assert rep.status_code == 200
    red = json.loads(rep.text)
    for item in red["data"]:
        for sub in item["data"]:
            if sub["action"] == "next_dat":
                mip = session.post(baseUrl + "api/user/getNextDay" + base_param(imei, uid), data={})
                print("次日登陆奖励成功:" + mip.text)
            elif sub["action"] == "user_red":
                mip = session.post(baseUrl + "api/user/userRed" + base_param(imei, uid), data={})
                print("用户大礼包奖励成功:" + mip.text)
            elif sub["action"] == "coin_1000":
                mip = session.post(baseUrl + "api/user/getCoin1000" + base_param(imei, uid), data={})
                print("累积1000奖励成功:" + mip.text)
            elif sub["action"] == "user_daily":
                mip = session.post(baseUrl + "api/user/getUserDailyTasks" + base_param(imei, uid), data={})
                print("随机任务奖励成功:" + mip.text)

    time.sleep(interTime)


# 视频奖励 暂时没有限制次数
def videoCoin(imei, uid):
    for i in range(20):
        rep = session.post(baseUrl + "api/user/videoCoin" + base_param(imei, uid), data={})
        print("请求响应 视频奖励:" + str(i) + rep.text)
        if json.loads(rep.text)["code"] != 200:
            break
        time.sleep(videoTime)
        doubleCoin("videoCoin", imei, uid)


# 刮刮卡
def scrach(imei, uid):
    session.post(baseUrl + "api/card/preDepositCard" + base_param(imei, uid), data={})
    rep = session.post(baseUrl + "api/card/index" + base_param(imei, uid), data={})
    print("请求响应 刮刮卡数据:" + rep.text)
    inD = json.loads(rep.text)
    if inD["data"]["surplus_numbers"] > 0:
        # 主卡开奖
        card = session.post(baseUrl + "api/card/openCard" + base_param(imei, uid), data={})
        # 附属卡开奖
        time.sleep(interTime)
        rep = session.post(baseUrl + "api/card/viceOpenCard" + base_param(imei, uid), data={})
        print("请求响应 开奖成功:" + rep.text)
        assert rep.status_code == 200
        if json.loads(card.text)["data"]["surprise_data"]["surprise_status"] == 0:
            # 可翻倍
            phraseDouble(imei, uid)
        time.sleep(videoTime)
        scrach(imei, uid)


# 成语踩中随机金币 每轮一次
def phraseRedGet(imei, uid):
    rep = session.post(baseUrl + "api/red/get" + base_param(imei, uid), data={})
    print("请求响应 成语踩中随机金币:" + rep.text)
    assert rep.status_code == 200
    time.sleep(videoTime)


# 领取俸禄
def getsalary(imei, uid):
    rep = session.post(baseUrl + "api/Answer/salary" + base_param(imei, uid), data={})
    print("请求响应 俸禄列表:" + rep.text)
    salist = json.loads(rep.text)
    list = salist["data"]["salary"]
    for item in list:
        print(item["status"])
        if item["status"] == 1:
            # 可领取
            dat = setparam("checkpoint", str(item["type"]))
            rep = session.post(baseUrl + "api/Answer/getsalary" + base_param(imei, uid), data=dat)
            print("领取俸禄成功:" + rep.text)
            phraseDouble(imei, uid)
            time.sleep(videoTime)


# 补充体力
def getEnerge(imei, uid):
    for i in range(5):
        rep = session.post(baseUrl + "api/Answer/getEnergy" + base_param(imei, uid), data={})
        print("请求响应 补充体力:" + rep.text)
        assert rep.status_code == 200
        time.sleep(videoTime)


# 开始答题
def startAnswer(imei, uid):
    time.sleep(interTime)
    for i in range(1, 11):
        print("第" + str(i) + "题")
        checkout("1", imei, uid)
        time.sleep(interTime)
        if i == 9:
            phraseRedGet(imei, uid)
    # 进入下一轮
    resD = checkout("2", imei, uid)
    if resD["data"]["title"]["status"] == "1":
        print("猜中红包")
        # 猜中红包 奖励翻倍
        phraseDouble(imei, uid)
        time.sleep(videoTime)
    getPhraseList(imei, uid)


# 成语列表数据
def getPhraseList(imei, uid):
    getsalary(imei, uid)
    rep = session.post(baseUrl + "api/answer/BreakThrough" + base_param(imei, uid), data={})
    print("请求响应 成语列表:" + rep.text)
    assert rep.status_code == 200
    listD = json.loads(rep.text)
    print("还差" + listD["data"]["checkpoint"]["again"] + "轮 可升级为" + listD["data"]["checkpoint"]["title"])
    if listD["data"]["surplus_energy"] <= 0:
        # 补充体力
        getEnerge(imei, uid)
        startAnswer(imei, uid)
    else:
        startAnswer(imei, uid)


# 成语部分
def phrase(imei, uid):
    getPhraseList(imei, uid)


def signRed(imei, uid):
    # 签到信息
    rep = session.post(baseUrl + "api/user/signCoin" + base_param(imei, uid), data={})
    repdic = json.loads(rep.text)
    print(repdic["data"]["cd_time"])
    assert rep.status_code == 200
    if repdic["data"]["cd_time"] <= 0:
        time.sleep(interTime)
        # 开红包
        rep = session.post(baseUrl + "api/user/openRed" + base_param(imei, uid), data={})
        print(rep.text)
        assert rep.status_code == 200


# 兑换步数
def exchangeStep(imei, uid):
    steps = random.randint(20001, 25000)
    dat = setparam("step", str(steps))
    print("请求参数 步数兑换:" + str(dat))
    rep = session.post(baseUrl + "api/member/exchangedCoin" + base_param(imei, uid), data=dat)
    print("请求响应 步数兑换:" + rep.text)
    assert rep.status_code == 200
    time.sleep(videoTime)
    doubleCoin("exchangedCoin", imei, uid)


# 金币翻倍
def doubleCoin(source, imei, uid):
    dat = setparam("action", source)
    print("请求参数 金币翻倍:" + str(dat))
    rep = session.post(baseUrl + "api/member/double" + base_param(imei, uid), data=dat)
    print("请求响应 金币翻倍:" + rep.text)
    time.sleep(videoTime)


# 随机金币 50次
def randomCoin(imei, uid):
    for i in range(0, 50):
        print("随机金币:" + str(i))
        coin = random.randint(60, 80)
        dat = setparam("coin", str(coin))
        print("请求参数 随机金币:" + str(dat))
        rep = session.post(baseUrl + "api/member/randCoin" + base_param(imei, uid), data=dat)
        print("请求响应 随机金币:" + rep.text)
        resD = json.loads(rep.text)
        assert rep.status_code == 200
        if resD["code"] != 200:
            break
        time.sleep(videoTime)
        # ==========金币翻倍===============
        doubleCoin("randCoin", imei, uid)
        time.sleep(videoTime)


def gamecenter():
    rep = session.get("https://static.game.adjuz.net/game/gamecenter/YTX/index.html?v=1512141284")
    print("请求响应 百度上报:" + rep.text)


# 获取登陆任务
def EncryptUser():
    dat = setparam("appId", "116")
    dat["uid"] = "340f24a3-b0ca-4ecb-a86f-82ed9f38617b"
    rep = session.post(baseUrl + "User/Api/EncryptUser", data=dat)
    print("请求响应 用户加密:" + rep.text)


# 获取登陆任务
def login(imei, uid):
    dat = setparam("appId", uid)
    # dat["telephone"] = "18630620063"
    dat["telephone"] = "13683166167"
    dat["validCode"] = "154673"
    dat["uid"] = "5a412f6d-666b-4cb4-ae2c-dc20dc82daee"
    dat["t"] = str(round(time.time() * 1000))
    print("请求参数 登陆:" + str(dat))
    rep = session.post(baseUrl + "User/Api/Login", data=dat)
    print("请求响应 登陆:" + rep.text + str(rep.status_code))


# 获取登陆任务
def VerifyGame(imei, uid):
    dat = setparam("clientId", uid)
    dat["gameId"] = 1004
    dat["gameType"] = 1
    dat["gameAccountId"] = "340f24a3-b0ca-4ecb-a86f-82ed9f38617b"
    dat["t"] = str(round(time.time() * 1000))
    rep = session.post(baseUrl + "Api/VerifyGame", data=dat)
    print("请求响应 游戏验证:" + rep.text)


# 获取登陆任务
def get_user_info(imei, uid):
    # dat = setparam("appId", uid)
    # rep = session.post(baseUrl + "Api/GetAll", data=dat)
    # print("请求响应 获取所有信息:" + rep.text)
    dat = setparam("appId", uid)
    dat["userId"] = imei
    dat["t"] = str(round(time.time() * 1000))
    print("请求数据 账户信息:" + str(dat))
    rep = session.post(baseUrl + "User/Api/GetUserByAccount", data=dat)
    print("请求响应 账户信息:" + rep.text)


# 获取登陆任务
def get_login_task(imei, uid):
    dat = setparam("appId", uid)
    dat["accountId"] = imei
    rep = session.post(baseUrl + "User/Api/GetLoginTask", data=dat)
    print("请求响应 登陆任务:" + rep.text)
    assert rep.status_code == 200


# 登陆翻倍奖励
def login_reward(imei, uid):
    dat = setparam("appId", uid)
    dat["accountId"] = imei
    dat["Multiple"] = 2
    # 签到翻倍
    dat["TaskId"] = -1
    dat["Task_Type"] = 7

    # 新人翻倍
    # dat["TaskId"] = 7
    # dat["Task_Type"] = 6

    rep = session.post(baseUrl + "Api/RewardUserTask", data=dat)
    print("请求响应 每日登陆翻倍:" + rep.text)
    assert rep.status_code == 200


# 获取签到信息
def get_sign_info(imei, uid):
    dat = setparam("appId", uid)
    dat["userId"] = imei
    dat["t"] = str(round(time.time() * 1000))
    rep = session.post(baseUrl + "User/Api/GetSignDays", data=dat)
    print("请求响应 获取签到信息:" + rep.text)
    assert rep.status_code == 200


# 签到
def sign(imei, uid):
    dat = setparam("appId", uid)
    dat["userId"] = imei
    dat["t"] = str(round(time.time() * 1000))
    print("请求参数 签到:" + str(dat))
    rep = session.post(baseUrl + "User/Api/Sign", data=dat)
    print("请求响应 签到:" + rep.text)
    assert rep.status_code == 200


# 兑换奖励
def Recharge(imei, uid):
    dat = setparam("appId", uid)
    dat["AccountId"] = imei
    dat["RewardId"] = 9
    dat["t"] = str(round(time.time() * 1000))
    print("请求参数 兑换金币:" + str(dat))
    rep = session.post(baseUrl + "User/Api/Recharge", data=dat)
    print("请求响应 兑换金币:" + rep.text)
    assert rep.status_code == 200


# AppId:117 对应iphone6

# 117:16553 18630620063
# 116:1999 18630620063

# 117: 8748 13683166167
# 116:16499 13683166167

# 117: 16536 15201418063
# 116:16508 15201418063

#{unionid=o-ybuskEaK4HgNgdKD4RNEvSyKcE, screen_name=十二越, city=, accessToken=37_5CT-_L0fI7zUBHwHWZtHTaIDvhg0Dvf_ZlFGIdNeBMWGePHXmoHxuJR625DyOFt4b_q2WpyVwBIPXM7cA7O09uKaWlImDxIYjiNTQb7GLEs, refreshToken=37_L5TAQ7zCrIe2syZmv7WCodO9z1DrBV-Zss0e20gl8CaXrDV6FyR9AIbOqoM-Ki17SJId8EBfcK4QNO4lsk6-_OXNcUmvxb93bxmUPeap5EA, gender=男, province=, openid=onTt2jrjT2sgzU6uxSCkUR3aGZZ4, profile_image_url=https://thirdwx.qlogo.cn/mmopen/vi_32/u8g8UoUaBZQCNHKsvS6actOjRRYicVRibuhf4UAFDbiaGvyApwr0B4ibaDEibjsLGJoGgbSzcnLBoE4mjxvXZ8Nb4Pw/132, country=, access_token=37_5CT-_L0fI7zUBHwHWZtHTaIDvhg0Dvf_ZlFGIdNeBMWGePHXmoHxuJR625DyOFt4b_q2WpyVwBIPXM7cA7O09uKaWlImDxIYjiNTQb7GLEs, iconurl=https://thirdwx.qlogo.cn/mmopen/vi_32/u8g8UoUaBZQCNHKsvS6actOjRRYicVRibuhf4UAFDbiaGvyApwr0B4ibaDEibjsLGJoGgbSzcnLBoE4mjxvXZ8Nb4Pw/132, name=十二越, uid=o-ybuskEaK4HgNgdKD4RNEvSyKcE, expiration=1599966431883, language=zh_CN, expires_in=1599966431883}
# 117: 16536 15201418063
# 116:16508 15201418063
lists = {
    "116": ["1999", "16499", "16508","16580"],
    # "117": ["8748"]
    "117": ["16553", "8748", "16536"]
}
count = 1


def startJob(uid, imei):
    get_user_info(imei, uid)
    get_login_task(imei, uid)
    login_reward(imei, uid)
    get_sign_info(imei, uid)
    sign(imei, uid)
    Recharge(imei, uid)

    # login(imei, uid)

    # randomCoin(imei, uid)
    # luckDraw(imei, uid)
    # fragment(imei, uid)
    # phrase(imei, uid)

    # scrach(imei, uid)
    # signRed(imei, uid)
    # videoCoin(imei, uid)

    # exchangeStep(imei,uid)
    # getReward(imei,uid)
    # register(["865876038083844", "965876038083844"])


# 第一步 领取红包

def threadFunc(userid, a):
    return startJob(a, userid)


def job(appkey, userIdlist):
    for userId in userIdlist:
        # ["1999","16499","16508"]
        times = []
        for i in range(count):
            times.append(userId)
        results = pool.map(partial(threadFunc, a=appkey), times)


# %%
# imeis = sorted(users) # sorted 排序的同时还对key去重
pool = ThreadPool(count)
if __name__ == '__main__':
    appKeyList = sorted(lists)
    for appkey in appKeyList:
        job(appkey, lists[appkey])
