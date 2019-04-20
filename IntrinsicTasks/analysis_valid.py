import subprocess
import os,sys
import matplotlib.pyplot as plt
max = 0
Task1 = []
Task2 = []
Task3 = []
Task4 = []
for i in range(1,int(sys.argv[2])+1):
  filename= "Task"+str(i)+"_"+sys.argv[1]+"/logs" 
  grep = subprocess.Popen(
    ["grep", "Validation accuracy" ,filename],
    stdout=subprocess.PIPE,
  )

  awk = subprocess.Popen(
    ["awk" ,"-F" ,"Validation accuracy: ", "{print $2}"],
    stdin=grep.stdout,
    stdout=subprocess.PIPE,
  )

  for line in awk.stdout:
      if(i==1):
#          print(float(line.decode('utf-8').replace('\n','')))
          Task1.append(float(line.decode('utf-8').replace('\n','')))
      if(i==2):
          Task2.append(float(line.decode('utf-8').replace('\n','')))
      if(i==3):
          Task3.append(float(line.decode('utf-8').replace('\n','')))
      if(i==4):
          Task4.append(float(line.decode('utf-8').replace('\n','')))

  grep = subprocess.Popen(
    ["grep", "Validation accuracy" ,filename],
    stdout=subprocess.PIPE,
  )

  awk = subprocess.Popen(
    ["awk" ,"-F" ,"Validation accuracy: ", "{print $2}"],
    stdin=grep.stdout,
    stdout=subprocess.PIPE,
  )

  wc = subprocess.Popen(
    ["wc", "-l"],
    stdin = awk.stdout,
    stdout=subprocess.PIPE,
  )

  for line in wc.stdout:
      if(int(line.decode('utf-8').strip())> max):
          max = int(line.decode('utf-8').strip())
      print(line.decode('utf-8').strip())

print("Max",max)
print("Task1",len(Task1))
#print(Task1)
l = Task1[len(Task1)-1]
while(len(Task1) < max):
    Task1.append(l)
if(int(sys.argv[2])>1):
  l = Task2[len(Task2)-1]
  while(len(Task2) < max):
    Task2.append(l)
if(int(sys.argv[2])>2):
  l = Task3[len(Task3)-1]
  while(len(Task3) < max):
    Task3.append(l)
if(int(sys.argv[2])>3):
  l = Task4[len(Task4)-1]
  while(len(Task4) < max):
    Task4.append(l)

x = list(range(1, max+1))
plt.plot([100*i for i in x], Task1, label="Simple Relabeling", marker=".", color='y')
if(int(sys.argv[2])>1):
  plt.plot([100*i for i in x], Task2, label="Complex Relabeling", marker=".", color='r')
if(int(sys.argv[2])>2):
  plt.plot([100*i for i in x], Task3, label="Reordering", marker=".", color='g')
if(int(sys.argv[2])>3):
  plt.plot([100*i for i in x], Task4, label="Deletion", marker=".", color='b')
plt.xlabel('Steps sampled every 100 steps')
plt.ylabel('Validation Accuracy')
plt.tight_layout()
plt.legend()
plt.savefig('figs/'+sys.argv[1]+'_validation.png')
