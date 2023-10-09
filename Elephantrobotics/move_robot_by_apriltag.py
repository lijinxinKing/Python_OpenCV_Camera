#Move Robot By April Tag
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GetCameraData import Get_AprilTag_36h11

tag_id = 5
def MoveRobotByAprilTag(tagId):
    tagId = tag_id
    center = Get_AprilTag_36h11.GetAprilTag36h11(tagId)
    print(center)
    
MoveRobotByAprilTag(5)