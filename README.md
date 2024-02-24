Project 3 - BGP Router

Three classes:
Router
The router is our main class, this is where the code is run, where messages are handled and most of level 1 to 5 tests' code happens.
Here is a basic procedure of how a every message is handled:
1. the code goes through the run function where it is decoded and handle_message is called
2. the code goes through handle_message, which directs the message to the respective function based on the message "type"
3. the code is then processed in the function which is specialized to deal with that type of message

Table
This class is a helper table to represent the forwarding table for the router.
Each table has a list of Networks mapped to a string(src) so that the program can be more organized than a List, which I had earlier. The table makes it easier to find information, modify it carefully, and debug the code. 
The table class is also where most of my aggregation code is.

Network
This class is a helper to represent each network in a table.
Each network is initialized with the attributes expected and shown in the instructions.
I have my best route calculations here which i use for the data function.
The definition of lt and eq made it much easier to get the best route. I could just call sort() in the data fuction, and it fixed several bugs that I had with my previous messy approach

The class also contains serialization methods that make the response to the "dump" message easy.
The definition of a lt dunder method makes sorting the networks easy so the best network can be found by the router without the router having to worry about the implementation details of the network itself adding a layer of abstraction.

Challenges we faced
Level 2 tests. We were stuck on this step for a while, and I went to office hours for a while to get the right logic to make this work. we actually spent most of the project trying to get the level 2 tests to run, and luckily after adding a table and network class and helper method lt it finally worked. We wrote the code for other functions to while we were stuck on level 2 tests, so I feel that this part was by far the most difficult to break through.

Aggregation and Disaggregation. This part was rather difficult as well, especially since it demanded a lot of researching and coding. We did it step by step, making the overview in aggregate and eventually the helper methods to aggregate network, netmask.

We dealt with these challenges with a ton of print statements, which used to be almost every step of the way during the height of level 2 test and aggregation debugging. We still have a lot of comments and some prints left over from this process.

The Table and Network classes helped make the code much cleaner than it was when we tried to stuff everything in one router class

Testing:
We tested using the config files given in the starter code using the khoury linux terminal.

