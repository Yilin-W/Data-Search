import subprocess
import sys
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("configfile")
parser.add_argument("--with-js=true", dest="feature", action="store_true")
parser.add_argument("--with-js=false", dest="feature", action="store_false")
parser.set_defaults(feature=True)
parser.add_argument("--prefix=", dest="project_prefix", action="store", type=str, default='')
args = parser.parse_args()

print(args.configfile)

itemNums = dict()   
AppPaths_to_ProjPath= dict()
itemNum = 0

with open(args.configfile) as file:
    for line in file:
        mavenSet = dict() 
        itemNum = ""      
        (firstPart, secondPart) = line.split("=")
        if not any(i.isdigit() for i in firstPart):
            continue 
        itemNum = itemNum.join([str(n) for n in list(firstPart[-3:]) if n.isdigit()]) 
        if not secondPart.strip() and "AppPath" in firstPart:  
            projPath_val = oldSet["ProjectFolderPath" + firstPart[7:]].strip("\n") 
            if projPath_val not in AppPaths_to_ProjPath: 
                AppPaths = [os.path.join(projPath_val + "/target" , file) \
                for file in os.listdir(projPath_val + "/target") \
                if file.endswith(".jar") or file.endswith(".war") \
                and not file.endswith("javadoc.jar") and not file.endswith("sources.jar")] 
                AppPaths_to_ProjPath[projPath_val] = AppPaths 
            secondPart = AppPaths_to_ProjPath[projPath_val].pop() + secondPart
        mavenSet[firstPart] = secondPart
        oldSet = itemNums.get(itemNum, dict())
        oldSet.update(mavenSet)
        itemNums[itemNum] = oldSet
        itemNum = int(itemNum)


if(bool(AppPaths_to_ProjPath)):
    for pj, ap in AppPaths_to_ProjPath.items():
        for i in ap:
            AddPath = dict()
            index_ele = 0
            Str_Count = str(itemNum+1)
            Str_Chop = i.replace(pj + "/target/", "")
            AddPath["ProjectFolderPath" + Str_Count] = pj
            AddPath["AppPath" + Str_Count] = i
            for elem in Str_Chop:
                if elem.isdigit(): 
                    index_ele = Str_Chop.index(elem)
                    break
            if index_ele > 0:
                AddPath["altName" + Str_Count] = Str_Chop[:index_ele-1]
            else:
                AddPath["altName" + Str_Count] = Str_Chop
            if ".jar" or ".zip" or ".war" in i:
                AddPath["projType" + Str_Count] = "maven"
            itemNums[Str_Count] = AddPath        
            itemNum += 1


cmdLines = []
m = -0.5
JSscan = args.feature
if args.project_prefix:
    prefix = args.project_prefix + "_"
else:
    prefix = args.project_prefix


for item in itemNums:
    if itemNums[item]["projType" + item].strip("\n") == "js" and (not JSscan):
        continue 
    if(m >= 2):
        m = -0.5
    if(m < 2):
        cmdLines.append(
            "sleep " +
            str(m+0.5) +
            "; " +
            "java" +
            " -jar /opt/whitesource/wss-unified-agent.jar" +
            " -c /opt/whitesource/config/wss-unified-agent.config.prioritize-Java" +
            " -appPath " + itemNums[item]["AppPath" + item].strip("\n") +
            " -d " + itemNums[item]["ProjectFolderPath" + item].strip("\n") +
            " -project " + prefix + itemNums[item]["altName" + item].strip("\n")
        )
        m += 0.5

n = 0
m = len(cmdLines)-1
while n <= m:
    if n+5 <= m:
        processes = [subprocess.Popen(cmd, shell=True) for cmd in cmdLines[n:n+5]]
        for p in processes: p.wait()
        n += 5
    else:
        processes = [subprocess.Popen(cmd, shell=True) for cmd in cmdLines[n:m+1]]
        for p in processes: p.wait()
        break
