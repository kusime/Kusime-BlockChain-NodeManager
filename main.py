import time
import requests
from flask import Flask, jsonify, request
# cors fix
from flask_cors import CORS

from Ku_Crypto.Ku_RSA import Ku_RSA

# TODO: check node alive
# TODO: when node is dead , remove from the list

app = Flask(__name__)
CORS(app)

# Rule : ["localhost:8080"]
managed_nodes = set()
# Rule: ["localhost:8080" : "Node RSA publickey"]
managed_nodes_pub = {}  # mini KMS


@app.route('/alive', methods=["GET", "POST"])
def alive():
    if request.method == 'GET':
        return "alive", 200
    post = request.get_json()
    print("Body=>", post)
    return jsonify(post), 200


@app.route('/register-node', methods=['POST'])
def register_node():
    # Rule {ip,port}
    node_info = request.get_json()
    ip = node_info["ip"]
    port = node_info["port"]
    node_rsa_pub = node_info["node_rsa_pub"]
    node_id = f"{ip}:{port}"
    # register node address
    managed_nodes.add(node_id)
    # register node rsa pool
    managed_nodes_pub[node_id] = node_rsa_pub
    api_return = {
        "message": f"{managed_nodes} registration successfully"
    }
    print(managed_nodes_pub)
    return jsonify(api_return), 200


# SECTION - RSA pool management
@app.route('/get-node-pub', methods=['POST'])
def get_node_pub():
    """ 
    Rule: {"query_node":"localhost:4000"} => {"pub_key":"sisiaowiecmoas"}
        Security check : check both the query_node and target_node is all in the same node network
    """
    query_info = request.get_json()
    query_node = query_info["query_node"]

    if query_node not in managed_nodes:
        api_return = {
            "message": "your node is not managed by this NodeManager , retrieve dropped",
        }
        return jsonify(api_return), 403
    api_return = {
        "pub_key": managed_nodes_pub[query_node]
    }
    return jsonify(api_return), 200


# SECTION - RSA pool management


@app.route('/get-nodes', methods=['GET'])
def get_node():
    """
        get all managed node
    """
    api_return = {
        "message": "nodes get successfully",
        "nodes": list(managed_nodes)
    }
    return jsonify(api_return), 200


@app.route('/get-pubs', methods=['GET'])
def get_pubs():
    """
        get all managed node's rsa
    """
    return jsonify(managed_nodes_pub), 200


# determined where the heartbeats saying is true
@app.route('/death', methods=['POST'])
def death():
    # Rule: we should validate the death signature to prevent fake death
    # {
    #   "death_node_id": "",
    #   "signature": "" <-- the signature of self "death_node_id"
    # }
    death_info = request.get_json()
    death_node_id = death_info["death_node_id"]
    signature = death_info["signature"]
    if death_node_id not in managed_nodes:
        api_return = {
            "message": "your node is not managed by this NodeManager , request dropped",
        }
        print("Your node is not managed by this NodeManager")
        return jsonify(api_return), 403
    death_node_pub = managed_nodes_pub[death_node_id]

    if not Ku_RSA._validate_object(death_node_pub, signature, death_node_id):
        api_return = {
            "message": "Validation failed , refuse to death this node",
        }
        print("RSA check Failed...")
        return jsonify(api_return), 403
    print("Validation passed, now deleting this node from NodeManager")
    # Rule: removing the death node
    print(
        f"LOG : check sus   node {death_node_id} dead, removing rsa_pub and node")
    managed_nodes.discard(death_node_id)
    # Remove rsa_pub from managed key pool
    try:
        del managed_nodes_pub[death_node_id]
    except KeyError:
        print(
            f"The key {death_node_id}'s key already removed from the RSA pool.")

    api_return = {
        "message": f"this node is removed ",
        "nodes": list(managed_nodes)
    }
    return jsonify(api_return), 200


@app.route('/check-node', methods=['POST'])
def check_node():
    # Rule {"sus_node": "ip:port",
    # "|fast_death":True/False|}
    check_info = request.get_json()
    sus_node = check_info['sus_node']
    fast_death = check_info.get("fast_death", False)
    print(fast_death)
    if not fast_death:
        MAX_RETRIES = 5
    else:
        print("ALERT : receive fast_death signal , now start restrict mode")
        MAX_RETRIES = 2
    for retry in range(MAX_RETRIES):
        try:
            # register the node
            response = requests.get(
                f'http://{sus_node}/alive', timeout=1)
            if response.status_code == 200:
                api_return = {
                    "message": f"this node is alive",
                    "nodes": list(managed_nodes)
                }
                print(f"LOG : check sus   node {sus_node} alive, kept")
                managed_nodes.add(sus_node)
                return jsonify(api_return), 200

        except:
            # catch exceptions raised by requests library
            print(f"{sus_node} => Request failed {retry+1}/{MAX_RETRIES}")
            # retry the request after a short delay
            time.sleep(1)

    else:
        # if we exit the loop without a break, node alive check failed
        api_return = {
            "message": f"this node is dead",
            "nodes": list(managed_nodes)
        }
        print(
            f"LOG : check sus   node {sus_node} dead, removing rsa_pub and node")
        managed_nodes.discard(sus_node)
        # Remove rsa_pub from managed key pool
        try:
            del managed_nodes_pub[sus_node]
        except KeyError:
            print(
                f"The key {sus_node}'s key already removed from the RSA pool.")
        return jsonify(api_return), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
