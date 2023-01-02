const axios = require("axios");
// have a ref to the NodeManager , and run in the same pod , so we can use localhost to connect our self(NodeManager)
const NodeManager = "localhost:8000";



// Make a request for a user with a given ID

async function notice_dead_node(NODE) {
  const payload = {
    "sus_node": NODE,
  };
  try {
    const res = await axios.post(`http://${NodeManager}/check-node`, payload);
    // console.log(res);
    return res.status;
  } catch (error) {
    console.log("notice_dead_node complains: ");
    return undefined;
  }
}

async function get_node_status(NODE) {
  try {
    const res = await axios.get(`http://${NODE}/alive`);
    // console.log(res);
    return 200;
  } catch (error) {
    console.log("get_node_status complains: ");
    return undefined;
  }
}

async function get_all_nodes() {
  try {
    const res = await axios.get(`http://${NodeManager}/get-nodes`);
    return res.data["nodes"];
  } catch (error) {
    console.log("get_all_nodes complains: May be our NodeManager is not working... ");
    return undefined;
  }
}

setInterval(async () => {
  console.log("\n-------\n")
  const nodes = await get_all_nodes();
  // check the nodes is get ok without error
  //   console.log(nodes)
  if (!Array.isArray(nodes) || nodes.length === 0) {
    // not successfully retrieve all nodes or not available node
    console.log("Not available nodes yet..");
    return;
  }

  nodes.forEach(async (node) => {
    if (!Array.isArray(nodes) || nodes.length === 0) {
      // not successfully retrieve all nodes or not available node
      console.log("Not available nodes yet..");
      return;
    }

    let node_status = await get_node_status(node);
    if (node_status === 200) {
      console.log(`${node} alive`);
      return;
    }

    // NOTE: since the async function is too hard for our javascript code , so we might delegate to live check to the NodeManager
    if (node_status === undefined) {
      console.log("NodeManager:", node, "seems to be dead_node")
      notice_dead_node(node)
    }
    

  });
}, 5500);


 
