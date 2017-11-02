/*
	*	Author : Nitin Jamadagni
	*	USAGE : node script.js </full/path/to/flow.json/in/node-red/format> <port_number>  OR  forever start script.js </full/path/to/flow.json/in/node-red/format> <port_number>
	* 	Precursors : have environment variable NODE_MODULES_ROOT set to /node/installation/lib/node_modules
*/

// USAGE : 
if (process.argv.length != 4){
	console.log("usage format should be : \n  node script.js </full/path/to/flow.json/in/node-red/format> <port_number> \n     or \n  forever start script.js </full/path/to/flow.json/in/node-red/format> <port_number>");
	process.exit();
}

// imports
var NODEROOT = process.env.NODE_MODULES_ROOT;
var embeddedStart = require(NODEROOT + '/node-red-embedded-start');
var fs = require('fs');
var random = require(NODEROOT + '/randomstring');
var RED = require(NODEROOT + '/node-red');
var http = require('http');
var express = require(NODEROOT + '/express');
console.log("imported all items!");


// utility functions
// TODO : manage urls and ports dynamically
// TODO : manage directory and paths dynamically
var changeFormat = function(filename) {
	var content = fs.readFileSync(filename);
	content = JSON.parse(content);
	var returnContent = {};
	var newId = random.generate(8) + "." + random.generate(6);
	var metainfo = content[0];
	returnContent.type = metainfo.type;
	returnContent.id = newId;
	returnContent.label = metainfo.label;
	returnContent.config = [];
	returnContent.disabled = [];
	returnContent.info = '';
	returnContent.nodes = content.slice(1,content.length);

	return returnContent;
}

// server setup
var taskFilename = process.argv[2];
var serverPort = parseInt(process.argv[3]); 
var app = express();
var setApp = app.use("/",express.static("public"));
var server = http.createServer(app);
var settings = {httpAdminRoot:"/red",httpNodeRoot: "/api",userDir:"/home/nitin/DR/node-red/", functionGlobalContext: {}};
var init = RED.init(server,settings);
console.log("init RED");
app.use(settings.httpAdminRoot,RED.httpAdmin);
app.use(settings.httpNodeRoot,RED.httpNode);
server.listen(serverPort);

// start the nodered module
RED.start().then(embeddedStart(RED)).then((result) => {
		
		console.log("started node-red!");
		
		// create flow on you machine, rename it to a something.json, that will be your flow
		var flow = changeFormat(taskFilename);

		//var exampleflow = {"id":"d74e90a2.c5d7c","type":"tab","label":"mytrialflow","configs":[],"disabled":false,"info":"","nodes":[{"id":"4e300716.3a8018","type":"inject","z":"d74e90a2.c5d7c","name":"","topic":"","payload":"","payloadType":"date","repeat":"","crontab":"","once":false,"x":212,"y":147,"wires":[["77bb27cd.294788"]]},{"id":"77bb27cd.294788","type":"debug","z":"d74e90a2.c5d7c","name":"","active":true,"console":"false","complete":"false","x":529,"y":171,"wires":[]}]};
		console.log("created a flow");




		var addFlow = RED.nodes.addFlow(flow);
		console.log("addFlow");




		var allflows = RED.nodes.getFlows();
		console.log("allflows got");
		console.log(allflows);

	}).catch((err)=>{
		console.log("something went wrong")
	});



//visit ip:8000/red to load the editor pallete




