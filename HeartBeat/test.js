const axios = require("axios");
const node = "192.168.2.228:62428"



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
(async () => {
    console.log(await get_node_status(node))
})()
