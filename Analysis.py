import networkx as nx
import random
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas

#nodes = intersections
#edges = roads
#GVW = Gross vechicle weight meaning max truck load on a road


#characteristics of the road network speeds pulled from averages over last 2 weeks
Speed = [104,85,70,53,36,32,20]
SpeedFrequency = [0.11,0.1,0.2,0.24,0.159,0.09,0.085]

#Gross Vehicle Weight repersenrs the weight of the vehicle in tons on a road
GVW = [43.5,49.5,55.5,62.5,100]
GVWFrequency = [0.412,0.003,0.008,0.046,0.53]

DrivingRate = 74.72
FuelMultiplier = 0.4329
FuelBase = 12.27
FuelPrice = 1.42

#number of roads in the network
#calculation is exponential so be careful with this
Roads = 1000

#takes a list of nodes in a given path
#returns the total cost of the path
def PathCost(graph,path,weight):
    total = 0
    for i in range(len(path)-1):
        #sums all weights from node to next node    
        total += graph[path[i]][path[i+1]][weight]
    return total

#calculate the total length of the network
def TotalLength(G):
    #total length of the network
    total = 0
    for u,v,a in G.edges(data=True):
        total += a['Length']
    return total

#calculate the total number of nodes in the network
def TotalNodes(G):
    return len(G.nodes)

#adds text to the final report
def Write(Report,x,y,Write,bold=False,fontsize=10):
    if bold:
        Report.setFont("Helvetica-Bold",fontsize)
    else:
        Report.setFont("Helvetica", fontsize)
    Report.drawString(x,y,Write)


Network = nx.Graph()
#generate a network with nodes numbered 0 to # of Roads
Network.add_nodes_from([i for i in range(Roads)])

#generate network
#iterates through all nodes and randomly adds edges as long as the total conennections is less than 3, and the edge is not a self loop
#this is because a intersection can never have more than 4 connections (in most cases)
#cap the bottom 5 and top 5 to not get out of range error
for i in range(5,Roads-5):    
    start,end = random.randint(-5,5) + i, random.randint(-5,5) + i
    if start == end or Network.degree[start]>=3 or Network.degree[end]>=3: continue
    
    #pulled from known average distances and divided by 1000 to turn into kilometers
    Length = random.randint(200,16000)/1000
    RoadSpeed = random.choices(Speed,SpeedFrequency)[0]
    RoadGVW = random.choices(GVW,GVWFrequency)[0]
    Time = Length/RoadSpeed
    #standard calulation used for determining full trip cost
    #math works on a per road basis as well giving the total cost to traverse including drivers cost + fuel cost
    Cost = DrivingRate*Time + ((FuelMultiplier*RoadSpeed)+FuelBase)*Time*FuelPrice
    
    #adds the new road to the network along with all of its attributes
    Network.add_edge(
        start,
        end,
        Length=Length,
        Speed=RoadSpeed,
        GVW=RoadGVW,
        Time = Time,
        Cost = Cost,
    )

#removes all nodes with no connections
#could be expanded to remove all disconnected graphs
for i in range(Roads):
    if Network.degree[i]<1:
        Network.remove_node(i)


#sends trucks from every intersection to every other intersection with routing based on different factors
#Wrote it expanded to be easy to read
#what is the cost,length,time optimizing by cost,length,time
def OptimalRoutes(Network,Report,y):
    Cost = [0,0,0]
    Length = [0,0,0]
    Time = [0,0,0]

    count = 0
    for i in range(Roads):
        for j in range(Roads):
            if i == j: continue
            try:
                #find the shortest path then total cost length and time for that path
                CPath = nx.shortest_path(Network,i,j,weight='Cost')
                Cost[0] += PathCost(Network,CPath,weight='Cost')
                Cost[1] += PathCost(Network,CPath,weight='Length')
                Cost[2] += PathCost(Network,CPath,weight='Time')
                
                LPath = nx.shortest_path(Network,i,j,weight='Length')
                Length[0] += PathCost(Network,LPath,weight='Cost')
                Length[1] += PathCost(Network,LPath,weight='Length')
                Length[2] += PathCost(Network,LPath,weight='Time')

                TPath = nx.shortest_path(Network,i,j,weight='Time')
                Time[0] += PathCost(Network,TPath,weight='Cost')
                Time[1] += PathCost(Network,TPath,weight='Length')
                Time[2] += PathCost(Network,TPath,weight='Time')

                count += 1
            except:
                #expected to have quite a few excepts as not all nodes are connected
                pass
    #add results to final report
    Write(Report,40,y, "simulated 1 way loads : "+str(count))
    Write(Report,40,y-20,"Cost of Cost vs Time = " + str("{:.1f}".format(100-(Cost[0]/Time[0])*100)) + " % savings",bold=True)
    Write(Report,40,y-40,"optimized                    Cost         Length         Time")
    #all numbers formatted to 1 decimal place for alignment on report
    Write(Report,40,y-60,"Cost Optimized     = $" + str("{:.1f}".format(Cost[0])) + " , " + str("{:.1f}".format(Cost[1])) + "km, " + str("{:.1f}".format(Cost[2]))+"hrs")
    Write(Report,40,y-80,"Length Optimized = $" + str("{:.1f}".format(Length[0])) + " , " + str("{:.1f}".format(Length[1])) + "km, " + str("{:.1f}".format(Length[2]))+ "hrs")
    Write(Report,40,y-100,"Time Optimized    = $" + str("{:.1f}".format(Time[0])) + " , " + str("{:.1f}".format(Time[1])) + "km, " + str("{:.1f}".format(Time[2]))+"hrs")
    Write(Report,350,y-40,"Best Average Trip Length = " + str("{:.1f}".format(Length[1]/count)) + "km")
    Write(Report,350,y-60,"Best Average Trip Time = " + str("{:.1f}".format(Time[2]/count)) + "hrs")
    Write(Report,350,y-80,"Best Average Trip Cost = $" + str("{:.1f}".format(Cost[0]/count)))



#determines the total Costs savings of finding a route for when a truck is empty and a different route for when it is loaded
#compares that vs always going in and out assuming that a truck is loaded
def OneWay(truckW,Network,Report,y):
    #makes a copy of the network with only roads where GVW > truckW
    removed = Network.copy()
    remove = []
    #makes a list of all edges with gvw < truck weight
    for start,end,a in Network.edges(data=True):
        if Network.edges[start,end]['GVW']<truckW:
            remove.append((start,end))
    #removes all elements in remove list
    removed.remove_edges_from(remove)
    

    #loops through intersection to every intersection and sums the cost to go there and back taking different routes
    countloaded = 0
    totalCostloaded = 0
    totalCostunloaded = 0 
    for i in range(Roads):
        for j in range(Roads):
            try:
                #drive truck loaded with reduced network
                totalCostloaded += PathCost(removed,nx.shortest_path(removed, j, i, weight='Cost'),'Cost')
                #drop load and drive back empty with full network
                totalCostunloaded += PathCost(Network,nx.shortest_path(Network, j, i, weight='Cost'),'Cost')
                countloaded += 1
            except:
                #again there is expected to be some routes that are impossible
                #especially with the reduced network size many "no path found"s are expected
                pass
    #total savings calculated as total cost to take empty and loaded vs always going loaded route
    savings = 100-(totalCostloaded+totalCostunloaded)/(totalCostloaded*2)*100

    #adds data to final report
    Write(Report,40,y,"Tested truck size = "+str(truckW))
    Write(Report,170,y,"Total # of trips for 1 way routing ="+str(countloaded))
    Write(Report,350,y,"One way route Total Cost Savings = "  + str("{:.3f}".format(savings)) + " %",bold=True)


#generate images for report
def GraphBarChart(x,y,xlabel,ylabel,FileName):
    plt.figure(figsize=(8,6))
    plt.bar(x,y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(FileName)
    plt.close()

GraphBarChart(Speed,SpeedFrequency,"Speed (km/h)","Fraction of roads","Speed.png")
GraphBarChart(GVW,GVWFrequency,"GVW (t)","Fraction of roads","GVW.png")

#generates and saves an image of the network 
pos = nx.spring_layout(Network,weight='Length')
nx.draw(Network, pos=pos, with_labels = True)
plt.savefig("net.png")


Report = canvas.Canvas("Report.pdf")
Write(Report,40,580,"One way routing")
Write(Report,40,560,"Calculated as (total cost going in and out the same way)/(total cost going in and out different ways)")
OneWay(49.5,Network,Report,540)
OneWay(55.5,Network,Report,520)
OneWay(62.5,Network,Report,500)


Write(Report,40,740, "Single way routing Weights")
OptimalRoutes(Network,Report,720)


Write(Report,10,800,"Road Network Simulation",bold=True,fontsize=24)
Write(Report,350,740,"Road network details")
Write(Report,350,720,"Total length of network = "+str("{:.1f}".format(TotalLength(Network)))+"km")
Write(Report,350,700,"Total number of nodes = "+str(TotalNodes(Network)))
#other details are written in OptimalRoutes around average trip details

#images generated and saved above
Report.drawImage("GVW.png",10,290,width=250,height=200)
Report.drawImage("Speed.png",280,290,width=250,height=200)

#fuel and sav come are excel charts that were generated from repeated runs to graph average results
Report.drawImage("net.png",350,10,width=280,height=280)
Report.drawImage("fuel.png",40,30,width=150,height=200)
Report.drawImage("sav.png",200,30,width=150,height=200)
Report.showPage()
Report.save()
