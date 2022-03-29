# Trucking-Analysis
This project is an analysis of a trucking network with the goal of determining actual savings by experimenting with various routing algorithms and strategies for moving vehicles throughout the network. The two major strategies examined here are establishing ideal routes from point A to point B while aiming for the lowest cost, length, and time possible. The second idea I tested is that many trucking companies route based on taking the same route to a destination as they did back, regardless of the present weight of the vehicles. What I did was an analysis of overall savings by going one route empty and returning by another route. This program's final product is a summary pdf that lists the characteristics utilised and the associated outcomes.



How do we go about resolving these issues? I've chosen to create a simulation that represents the actual world with realistic road attribute frequency distributions. The roads were represented as a graph data structure, with nodes representing intersections and edges representing individual roads. Every road has five characteristics: length, speed, weight restriction, travel time, and travel cost.



To figure out the optimum way to route trucks, I ran a simulation of cargo travelling from every intersection to every other intersection three times. The first time, we look for the cheapest way to the destination and record the total cost, time, and distance travelled, we repeat these steps for quickest time and shortest route . Under the hood, the Dijkstras least cost method is used to find these best routes. After conducting this study, it appears evident that all trucking businesses should be routing for the lowest overall cost. Many people believe that the shortest route is always the best, however with the price of gasoline significantly higher, longer routes end up winning with less fuel consumption.



The second part of the analysis looks at what is the ideal approach to send an vehicle to a location to pick up cargo and return it to where you started. This is not a simple problem since every road has weight constraints that decide whether a truck can cross over it or not. When the truck is empty, these restrictions are rarely an issue, but once loaded, they severely limit the roads you may travel on. Many trucking firms will select a single route to a site that can hold the loaded weight and dispatch the truck there and back using that route; however,here I look at taking the best way empty first, then the best way loaded back . To calculate the savings, I take the original network and remove all roads that are under the truck's loaded weight. Next, I use the Dijkstras algorithm to find the best cost route over the entire network plus the stripped down network and compare it to going over the stripped down network both ways.

![alt text](https://github.com/Dhubbs/Trucking-Analysis/blob/main/Report.pdf)
