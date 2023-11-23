
import redis,json

def GetKeyLocationFromRedis(planId,deviceName,KeyValue):
    pool = redis.ConnectionPool(host='10.119.96.35',port=6379,password='',db=4)  
    r = redis.Redis(connection_pool=pool)
    key = planId + ":" + deviceName + ":" + str(KeyValue).lower()
    data = r.get(key)
    if data == None:
        key = planId + ":" + deviceName + ":" + str(KeyValue).upper()
        data = r.get(key)
    if data !=None:
        return json.loads(data)
    return None

if __name__=="__main__":
    PlanId = "TestSmartArmRobot"
    testMachine_deviceName = "LAPTOP-T7SDIEJE"
    center_Key = "j"
    press_moveCoords_key = [0,0,0]
    center_press_moveCoords_key = [1,1,1]
    keyName = "Q"
    print(GetKeyLocationFromRedis(PlanId,testMachine_deviceName,center_Key))
    print(GetKeyLocationFromRedis(PlanId,testMachine_deviceName,keyName))
